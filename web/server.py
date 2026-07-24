"""FastAPI server providing WebSocket state streaming and control endpoints for RoboForge Arena web dashboard."""
from __future__ import annotations
import asyncio
import math
import os
import threading
import time
import random
import numpy as np
from typing import Any
from concurrent.futures import ProcessPoolExecutor
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sandbox.sandbox_mode import SandboxMode
from combat.arena import Arena
from web.state_encoder import encode_state
from combat.combat_env import CombatEnv
from evolution.nn_controller import NNController
from evolution.ga import tournament_selection, crossover, mutate
from web.fighter_roster import save_fighter, list_fighters, get_fighter, delete_fighter
from web.prompt_translator import translate_training_prompt


app = FastAPI(title="RoboForge Arena — Web Dashboard Server")


def _evaluate_single_combat_match(
    args: tuple[np.ndarray, np.ndarray, str, str, dict[str, float], int]
) -> float:
    """Evaluate one combat match between two genomes independently in a worker process."""
    genome_a, genome_b, robot_a_spec, robot_b_spec, weights, max_steps = args
    env = CombatEnv(
        robot_a_spec=robot_a_spec,
        robot_b_spec=robot_b_spec,
        max_episode_steps=max_steps,
    )
    obs_a, _ = env.reset()
    obs_b = env.current_obs_b

    obs_dim_a = env.observation_space.shape[0]
    num_actions_a = env.action_space.shape[0]
    obs_dim_b = len(env.current_obs_b)
    num_actions_b = env.action_space_b.shape[0]

    ctrl_a = NNController(obs_dim=obs_dim_a, num_actions=num_actions_a, hidden_dim=16)
    ctrl_b = NNController(obs_dim=obs_dim_b, num_actions=num_actions_b, hidden_dim=16)

    ctrl_a.set_genome(genome_a)
    ctrl_b.set_genome(genome_b)

    aggression = float(weights.get("aggression", 0.5))
    caution = float(weights.get("caution", 0.5))
    mobility = float(weights.get("mobility", 0.5))

    total_reward = 0.0
    done = False

    while not done:
        action_a = ctrl_a.act(obs_a)
        action_b = ctrl_b.act(obs_b)
        obs_a, obs_b, rew_a, rew_b, done, info = env.step_two_agents(action_a, action_b)

        shaped_reward = (
            rew_a * (1.0 + aggression)
            + info.get("distance_closed", 0.0) * mobility
            - info.get("damage_received", 0.0) * caution
        )
        total_reward += shaped_reward

    env.close()
    return float(total_reward)


# Global Session State Owner
class SessionState:
    def __init__(self) -> None:
        self.mode: str = "playground"
        self.paused: bool = False
        self.sandbox: SandboxMode = SandboxMode(headless=True)
        self.arena: Arena | None = None
        self.ctrl_a: Any = None
        self.ctrl_b: Any = None

    def get_active_object(self) -> Any:
        if self.mode == "playground":
            return self.sandbox
        elif self.mode == "competitive" and self.arena is not None:
            return self.arena
        return self.sandbox

    def load_controllers_for_competitive(
        self, fighter_a_id: str | None = None, fighter_b_id: str | None = None
    ) -> None:
        if self.arena is None:
            return
        self.ctrl_a = self._load_single_controller(fighter_a_id, is_robot_a=True)
        self.ctrl_b = self._load_single_controller(fighter_b_id, is_robot_a=False)

    def _load_single_controller(self, fighter_id: str | None, is_robot_a: bool) -> Any:
        if self.arena is None:
            return None
        robot = self.arena.robot_a if is_robot_a else self.arena.robot_b
        opponent = self.arena.robot_b if is_robot_a else self.arena.robot_a
        obs = self.arena.get_observation(robot, opponent)
        obs_dim = obs.shape[0]
        num_actions = len(robot.spec.joints)

        ctrl = NNController(obs_dim=obs_dim, num_actions=num_actions, hidden_dim=16)

        fighter_entry = get_fighter(fighter_id) if fighter_id else None
        artifact_path = fighter_entry.get("artifact_path") if fighter_entry else None

        if not artifact_path or not os.path.exists(artifact_path):
            if os.path.exists("models/combat_ga_best.npy"):
                artifact_path = "models/combat_ga_best.npy"

        if artifact_path and os.path.exists(artifact_path):
            if artifact_path.endswith(".npy"):
                try:
                    genome = np.load(artifact_path)
                    if genome.size == ctrl.total_weights:
                        ctrl.set_genome(genome)
                except Exception:
                    pass
                return ctrl
            elif artifact_path.endswith(".zip"):
                try:
                    from stable_baselines3 import PPO
                    ppo_model = PPO.load(artifact_path)

                    class PPOWrapper:
                        def __init__(self, model: Any):
                            self.model = model

                        def act(self, observation: np.ndarray) -> np.ndarray:
                            action, _ = self.model.predict(observation, deterministic=True)
                            return action

                    return PPOWrapper(ppo_model)
                except Exception:
                    pass

        return ctrl

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
                obs_a = self.arena.get_observation(self.arena.robot_a, self.arena.robot_b)
                obs_b = self.arena.get_observation(self.arena.robot_b, self.arena.robot_a)

                if self.ctrl_a is None:
                    self.ctrl_a = self._load_single_controller(None, is_robot_a=True)
                if self.ctrl_b is None:
                    self.ctrl_b = self._load_single_controller(None, is_robot_a=False)

                num_j_a = len(self.arena.robot_a.spec.joints)
                num_j_b = len(self.arena.robot_b.spec.joints)

                action_a = self.ctrl_a.act(obs_a)
                action_b = self.ctrl_b.act(obs_b)

                self.arena.step(action_a[:num_j_a], action_b[:num_j_b])


session = SessionState()


def _simulation_loop() -> None:
    """Background thread stepping physics simulation independently from the WebSocket loop."""
    while True:
        try:
            if not session.paused:
                session.step()
        except Exception:
            pass
        time.sleep(1.0 / 60.0)


_sim_thread = threading.Thread(target=_simulation_loop, daemon=True)
_sim_thread.start()


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
        session.paused = True  # Pause during teardown transition
    else:
        session.paused = False

    session.mode = req.mode
    if req.mode == "competitive":
        session.arena = Arena(
            "robots/presets/boxer.json",
            "robots/presets/grappler.json",
        )
        session.load_controllers_for_competitive()
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
            session.load_controllers_for_competitive()
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


def _run_combat_gym_training(
    sandbox: Any,
    weights: dict[str, float],
    generations: int,
    pop_size: int,
    max_steps_per_match: int,
) -> None:
    """Background thread running real 1v1 CombatEnv GA evolution with parallel process evaluation."""
    try:
        robot_a_spec = "robots/presets/boxer.json"
        robot_b_spec = "robots/presets/grappler.json"

        aggression = float(weights.get("aggression", 0.5))
        caution = float(weights.get("caution", 0.5))
        mobility = float(weights.get("mobility", 0.5))

        # Initialize CombatEnv once to get observation/action dimensions
        env = CombatEnv(
            robot_a_spec=robot_a_spec,
            robot_b_spec=robot_b_spec,
            max_episode_steps=max_steps_per_match,
        )
        obs_a, _ = env.reset()
        obs_dim_a = env.observation_space.shape[0]
        num_actions_a = env.action_space.shape[0]
        env.close()

        # Initialize random population of NNController genome vectors
        dummy = NNController(obs_dim=obs_dim_a, num_actions=num_actions_a, hidden_dim=16)
        genome_len = dummy.total_weights
        genomes = [np.random.randn(genome_len).astype(np.float32) * 0.5 for _ in range(pop_size)]

        fitness_history: list[float] = []
        max_workers = min(pop_size, os.cpu_count() or 4)

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for gen_idx in range(generations):
                if sandbox.gym_stats.get("stopped"):
                    break

                task_args = []
                for i in range(pop_size):
                    opp_idx = random.choice([j for j in range(pop_size) if j != i])
                    task_args.append((
                        genomes[i],
                        genomes[opp_idx],
                        robot_a_spec,
                        robot_b_spec,
                        weights,
                        max_steps_per_match,
                    ))

                futures = [executor.submit(_evaluate_single_combat_match, arg) for arg in task_args]
                fitnesses = [f.result() for f in futures]

                best_fitness = float(max(fitnesses))
                mean_fitness = float(np.mean(fitnesses))
                best_idx = int(np.argmax(fitnesses))
                fitness_history.append(best_fitness)

                grid = [
                    {"id": i, "reward": round(fitnesses[i], 2), "is_best": (i == best_idx)}
                    for i in range(pop_size)
                ]

                sandbox.gym_stats.update({
                    "generation": gen_idx + 1,
                    "best_reward": round(best_fitness, 2),
                    "mean_reward": round(mean_fitness, 2),
                    "grid": grid,
                    "history": list(fitness_history),
                })

                # GA reproduction
                elite = [genomes[best_idx].copy()]
                parents = tournament_selection(genomes, fitnesses, num_select=pop_size - 1, tournament_size=3)
                new_genomes = elite[:]
                for k in range(0, len(parents) - 1, 2):
                    child = crossover(parents[k], parents[k + 1])
                    child = mutate(child, mutation_rate=0.08, mutation_strength=0.15)
                    new_genomes.append(child)
                while len(new_genomes) < pop_size:
                    new_genomes.append(mutate(genomes[best_idx].copy(), mutation_rate=0.1, mutation_strength=0.2))
                genomes = new_genomes[:pop_size]

        os.makedirs("models", exist_ok=True)
        best_genome = genomes[int(np.argmax(fitnesses))]
        np.save("models/combat_ga_best.npy", best_genome)
        sandbox.gym_stats["training_complete"] = True

    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        os.makedirs("logs", exist_ok=True)
        with open("logs/gym_training_error.log", "a", encoding="utf-8") as f:
            f.write(f"=== Gym Training Crash ===\n{tb_str}\n\n")
        if hasattr(sandbox, "gym_stats"):
            sandbox.gym_stats["error"] = str(e)
            sandbox.gym_stats["traceback"] = tb_str
            sandbox.gym_stats["stopped"] = True


@app.post("/api/gym/start")
def start_gym_training(req: GymStartRequest) -> dict[str, Any]:
    os.makedirs("models/roster", exist_ok=True)
    session.mode = "gym"

    # Translate prompt to combat reward weights
    weights = req.weights
    if not weights and req.prompt:
        trans = translate_training_prompt(req.prompt)
        weights = trans["weights"]
    if not weights:
        weights = {"aggression": 0.5, "caution": 0.5, "mobility": 0.5, "stamina_conservation": 0.5}

    pop_size = 6
    generations = max(1, req.generations)
    max_steps = 150  # Faster matches = faster first-generation feedback

    session.sandbox.gym_stats = {
        "algo": "ga_combat",
        "generation": 0,
        "weights": weights,
        "best_reward": 0.0,
        "mean_reward": 0.0,
        "grid": [{"id": i, "reward": 0.0, "is_best": False} for i in range(pop_size)],
        "history": [],
        "stopped": False,
        "training_complete": False,
    }

    t = threading.Thread(
        target=_run_combat_gym_training,
        args=(session.sandbox, weights, generations, pop_size, max_steps),
        daemon=True,
    )
    t.start()

    return {"status": "ok", "algo": "ga_combat", "generations": generations, "pop_size": pop_size, "weights": weights}


@app.post("/api/gym/stop")
def stop_gym_training() -> dict[str, Any]:
    if hasattr(session.sandbox, "gym_stats"):
        session.sandbox.gym_stats["stopped"] = True
    return {"status": "ok"}


class GymPromoteRequest(BaseModel):
    name: str = "Champion"


@app.post("/api/gym/promote")
def promote_gym_champion(req: GymPromoteRequest) -> dict[str, Any]:
    """Save the best evolved genome as a named roster entry under models/roster/."""
    os.makedirs("models/roster", exist_ok=True)

    stats = {}
    if hasattr(session.sandbox, "gym_stats"):
        stats = {
            "algo": session.sandbox.gym_stats.get("algo", "ga_combat"),
            "best_reward": session.sandbox.gym_stats.get("best_reward", 0.0),
            "mean_reward": session.sandbox.gym_stats.get("mean_reward", 0.0),
            "generation": session.sandbox.gym_stats.get("generation", 0),
        }

    artifact_path = "models/combat_ga_best.npy"
    entry = save_fighter(
        name=req.name,
        preset_name="robots/presets/boxer.json",
        algo="ga",
        artifact_path=artifact_path,
        stats=stats,
    )

    return {"status": "ok", "saved_path": entry["artifact_path"], "fighter": entry}


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
    session.load_controllers_for_competitive(req.fighter_a_id, req.fighter_b_id)
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
