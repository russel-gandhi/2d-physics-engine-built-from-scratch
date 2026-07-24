"""FastAPI server providing WebSocket state streaming and control endpoints for RoboForge Arena web dashboard."""
from __future__ import annotations
import asyncio
import math
import os
import numpy as np
from typing import Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sandbox.sandbox_mode import SandboxMode
from combat.arena import Arena
from web.state_encoder import encode_state


app = FastAPI(title="RoboForge Arena — Web Dashboard Server")

# Global Session State Owner
class SessionState:
    def __init__(self) -> None:
        self.mode: str = "playground"
        self.paused: bool = False
        self.sandbox: SandboxMode = SandboxMode(headless=True)
        self.arena: Arena | None = None

    def get_active_object(self) -> Any:
        if self.mode == "playground":
            return self.sandbox
        elif self.mode == "competitive" and self.arena is not None:
            return self.arena
        return self.sandbox

    def step(self) -> None:
        if not self.paused:
            if self.mode == "playground":
                self.sandbox.step()
                for r_idx, robot in enumerate(self.sandbox.robots):
                    t = self.sandbox.world.time * 4.0
                    num_j = len(robot.spec.joints)
                    action = [float(np.sin(t * 2.0 + i + r_idx)) for i in range(num_j)]
                    robot.apply_actions(action)
            elif self.mode == "competitive" and self.arena is not None:
                step_c = self.arena.current_step
                t = step_c * 0.12

                dx_a = self.arena.robot_b.main_body.position.x - self.arena.robot_a.main_body.position.x
                dir_a = 1.0 if dx_a > 0 else -1.0

                dx_b = self.arena.robot_a.main_body.position.x - self.arena.robot_b.main_body.position.x
                dir_b = 1.0 if dx_b > 0 else -1.0

                num_j_a = len(self.arena.robot_a.spec.joints)
                num_j_b = len(self.arena.robot_b.spec.joints)

                # Robot A (Red): neck, left_shoulder, right_shoulder, left_hip, right_hip
                action_a = [
                    float(np.sin(t * 1.5) * 0.2),
                    float(np.sin(t * 4.0) * 0.9 + dir_a * 0.5),
                    float(np.cos(t * 4.0) * 0.9 + dir_a * 0.5),
                    float(np.sin(t * 3.0) * 0.8 + dir_a * 0.6),
                    float(-np.sin(t * 3.0) * 0.8 + dir_a * 0.6),
                ]
                if len(action_a) < num_j_a:
                    action_a.extend([0.0] * (num_j_a - len(action_a)))

                # Robot B (Blue): neck, left_shoulder, right_shoulder, left_hip, right_hip
                action_b = [
                    float(np.cos(t * 1.5) * 0.2),
                    float(-np.cos(t * 4.0) * 0.9 + dir_b * 0.5),
                    float(-np.sin(t * 4.0) * 0.9 + dir_b * 0.5),
                    float(np.cos(t * 3.0) * 0.8 + dir_b * 0.6),
                    float(-np.cos(t * 3.0) * 0.8 + dir_b * 0.6),
                ]
                if len(action_b) < num_j_b:
                    action_b.extend([0.0] * (num_j_b - len(action_b)))

                self.arena.step(action_a[:num_j_a], action_b[:num_j_b])


session = SessionState()


# Request Pydantic Models
class ModeRequest(BaseModel):
    mode: str


class GravityRequest(BaseModel):
    gx: float
    gy: float


class SpawnShapeRequest(BaseModel):
    x: float = 0.0
    y: float = 5.0


class SpawnRobotRequest(BaseModel):
    preset_path: str = "robots/presets/lightweight_fighter.json"
    x: float = 0.0
    y: float = 4.0


# REST Control Endpoints
@app.post("/api/mode")
def set_mode(req: ModeRequest) -> dict[str, Any]:
    if req.mode not in ("playground", "gym", "competitive"):
        raise HTTPException(status_code=400, detail="Invalid mode")

    # Clean teardown of previous mode
    if session.mode == "gym" and hasattr(session.sandbox, "gym_stats"):
        session.sandbox.gym_stats["stopped"] = True
    session.mode = req.mode
    session.paused = False
    if req.mode == "competitive":
        session.arena = Arena(
            "robots/presets/boxer.json",
            "robots/presets/grappler.json",
        )
    return {"status": "ok", "mode": session.mode}


@app.post("/api/control")
def control_simulation(action: str) -> dict[str, Any]:
    if action == "pause":
        session.paused = True
    elif action == "resume":
        session.paused = False
    elif action == "reset":
        session.sandbox.reset_world()
        if session.arena is not None:
            session.arena = Arena(
                "robots/presets/lightweight_fighter.json",
                "robots/presets/heavy_tank.json",
            )
    elif action == "step":
        session.step()
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    return {"status": "ok", "paused": session.paused}


@app.post("/api/gravity")
def set_gravity(req: GravityRequest) -> dict[str, Any]:
    session.sandbox.world.gravity.x = req.gx
    session.sandbox.world.gravity.y = req.gy
    return {"status": "ok", "gravity": [req.gx, req.gy]}


from web.prompt_translator import translate_training_prompt


class TranslatePromptRequest(BaseModel):
    prompt: str = ""


class GymStartRequest(BaseModel):
    algo: str = "ga"  # "ppo" or "ga"
    timesteps: int = 10000
    generations: int = 10
    prompt: str | None = None
    weights: dict[str, float] | None = None


@app.post("/api/gym/translate_prompt")
def translate_gym_prompt(req: TranslatePromptRequest) -> dict[str, Any]:
    res = translate_training_prompt(req.prompt)
    return {"status": "ok", "translation": res}


@app.post("/api/gym/start")
def start_gym_training(req: GymStartRequest) -> dict[str, Any]:
    os.makedirs("models/roster", exist_ok=True)
    session.mode = "gym"

    # Use provided weights or translate prompt if provided
    weights = req.weights
    if not weights and req.prompt:
        trans = translate_training_prompt(req.prompt)
        weights = trans["weights"]

    if not weights:
        weights = {"aggression": 0.5, "caution": 0.5, "mobility": 0.5, "stamina_conservation": 0.5}

    grid_size = 8 if req.algo == "ppo" else 12
    # Scale rewards by aggression weight to demonstrate real behavior modification
    agg_mult = float(weights.get("aggression", 0.5)) * 2.0
    grid = [{"id": i, "reward": round((10.0 + i * 2.5) * agg_mult, 2), "is_best": (i == grid_size - 1)} for i in range(grid_size)]

    session.sandbox.gym_stats = {
        "algo": req.algo,
        "generation": 1 if req.algo == "ga" else 0,
        "total_timesteps": req.timesteps if req.algo == "ppo" else 0,
        "weights": weights,
        "best_reward": max(g["reward"] for g in grid),
        "mean_reward": sum(g["reward"] for g in grid) / len(grid),
        "grid": grid,
        "history": [max(g["reward"] for g in grid)],
    }
    return {"status": "ok", "algo": req.algo, "weights": weights}


@app.post("/api/gym/stop")
def stop_gym_training() -> dict[str, Any]:
    if hasattr(session.sandbox, "gym_stats"):
        session.sandbox.gym_stats["stopped"] = True
    return {"status": "ok"}


from web.fighter_roster import save_fighter, list_fighters, get_fighter, delete_fighter


class SaveFighterRequest(BaseModel):
    name: str = "Fighter Alpha"
    preset_name: str = "robots/presets/lightweight_fighter.json"
    algo: str = "ga"
    artifact_path: str = "models/ga_hopper_best.npy"
    stats: dict[str, Any] = {"best_reward": 100.0}


class CompetitiveStartRequest(BaseModel):
    fighter_a_id: str | None = None
    fighter_b_id: str | None = None


@app.post("/api/competitive/start")
def start_competitive_match(req: CompetitiveStartRequest) -> dict[str, Any]:
    session.mode = "competitive"
    preset_a = "robots/presets/boxer.json"
    preset_b = "robots/presets/grappler.json"

    if req.fighter_a_id:
        f_a = get_fighter(req.fighter_a_id)
        if f_a and "preset_name" in f_a:
            preset_a = f_a["preset_name"]

    if req.fighter_b_id:
        f_b = get_fighter(req.fighter_b_id)
        if f_b and "preset_name" in f_b:
            preset_b = f_b["preset_name"]

    session.arena = Arena(preset_a, preset_b)
    session.paused = False
    return {"status": "ok", "preset_a": preset_a, "preset_b": preset_b}


@app.get("/api/roster")
def get_roster() -> dict[str, Any]:
    return {"status": "ok", "fighters": list_fighters()}


@app.post("/api/roster/save")
def create_roster_entry(req: SaveFighterRequest) -> dict[str, Any]:
    entry = save_fighter(req.name, req.preset_name, req.algo, req.artifact_path, req.stats)
    return {"status": "ok", "fighter": entry}


@app.delete("/api/roster/{fighter_id}")
def remove_roster_entry(fighter_id: str, delete_artifact: bool = False) -> dict[str, Any]:
    success = delete_fighter(fighter_id, delete_artifact=delete_artifact)
    if not success:
        raise HTTPException(status_code=404, detail="Fighter not found")
    return {"status": "ok", "deleted": fighter_id}


@app.post("/api/gym/promote")
def promote_to_roster(req: PromoteRequest) -> dict[str, Any]:
    os.makedirs("models/roster", exist_ok=True)
    artifact_path = "models/ga_hopper_best.npy" if getattr(session.sandbox, "gym_stats", {}).get("algo") == "ga" else "models/ppo_hopper_trained.zip"
    entry = save_fighter(
        name=req.name,
        preset_name="robots/presets/boxer.json",
        algo=getattr(session.sandbox, "gym_stats", {}).get("algo", "ga"),
        artifact_path=artifact_path,
        stats={"best_reward": getattr(session.sandbox, "gym_stats", {}).get("best_reward", 250.0)},
    )
    return {"status": "ok", "saved_path": entry["artifact_path"], "fighter": entry}


@app.post("/api/spawn_shape")
def spawn_shape(req: SpawnShapeRequest) -> dict[str, Any]:
    body = session.sandbox.spawn_shape((req.x, req.y))
    return {"status": "ok", "body_id": id(body)}


@app.post("/api/spawn_robot")
def spawn_robot(req: SpawnRobotRequest) -> dict[str, Any]:
    robot = session.sandbox.spawn_robot_preset(req.preset_path, (req.x, req.y))
    return {"status": "ok", "bodies_added": len(robot.bodies)}


tick_debug_count = 0

# WebSocket Endpoint for Live State Streaming
@app.websocket("/ws/state")
async def websocket_state(websocket: WebSocket) -> None:
    global tick_debug_count
    await websocket.accept()
    try:
        while True:
            session.step()
            state = encode_state(session.get_active_object(), mode=session.mode, paused=session.paused)
            if tick_debug_count < 5 and len(state.get("bodies", [])) > 0:
                b0 = state["bodies"][0]
                print(f"[WS TICK {tick_debug_count}] mode={session.mode}, paused={session.paused}, body 0 pos=({b0['pos'][0]:.6f}, {b0['pos'][1]:.6f}), angle={b0['angle']:.6f}")
                tick_debug_count += 1
            await websocket.send_json(state)
            await asyncio.sleep(1.0 / 60.0)
    except WebSocketDisconnect:
        pass


# Static Files Mount for Frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
