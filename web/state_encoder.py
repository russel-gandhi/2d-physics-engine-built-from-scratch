"""State encoder module converting physics objects (World, SandboxMode, Arena) into JSON-serializable dictionaries."""
from __future__ import annotations
from typing import Any
from physics.world import World
from physics.shapes import Circle, Polygon
from physics.joints import DistanceJoint, RevoluteJoint
from sandbox.sandbox_mode import SandboxMode
from combat.arena import Arena
from combat.combat_env import CombatEnv


def encode_state(obj: Any, mode: str = "playground", paused: bool = False) -> dict[str, Any]:
    """Serialize physics World, SandboxMode, or Arena state into JSON-serializable dictionary."""
    if obj is None:
        return {
            "mode": mode,
            "paused": paused,
            "bodies": [],
            "joints": [],
            "gravity": [0.0, -9.8],
        }

    world: World | None = None
    arena: Arena | None = None

    if isinstance(obj, SandboxMode):
        world = obj.world
        paused = obj.paused
    elif isinstance(obj, Arena):
        arena = obj
        world = obj.world
    elif isinstance(obj, CombatEnv):
        arena = obj.arena
        world = obj.arena.world
    elif isinstance(obj, World):
        world = obj

    bodies_encoded = []
    joints_encoded = []
    gravity = [0.0, -9.8]

    if world is not None:
        gravity = [float(world.gravity.x), float(world.gravity.y)]

        for body_id, body in enumerate(world.bodies):
            b_dict: dict[str, Any] = {
                "id": body_id,
                "pos": [float(body.position.x), float(body.position.y)],
                "angle": float(body.angle),
                "is_static": bool(body.is_static),
            }

            if isinstance(body.shape, Circle):
                b_dict["shape_type"] = "circle"
                b_dict["radius"] = float(body.shape.radius)
            elif isinstance(body.shape, Polygon):
                b_dict["shape_type"] = "polygon"
                b_dict["vertices"] = [[float(v.x), float(v.y)] for v in body.shape.vertices]
            else:
                b_dict["shape_type"] = "unknown"

            bodies_encoded.append(b_dict)

        for joint in world.joints:
            p_a = joint.body_a.position + joint.anchor_a.rotate(joint.body_a.angle)
            p_b = joint.body_b.position + joint.anchor_b.rotate(joint.body_b.angle)

            j_type = "distance" if isinstance(joint, DistanceJoint) else "revolute"
            joints_encoded.append({
                "type": j_type,
                "anchor_a": [float(p_a.x), float(p_a.y)],
                "anchor_b": [float(p_b.x), float(p_b.y)],
            })

    result: dict[str, Any] = {
        "mode": mode,
        "paused": paused,
        "gravity": gravity,
        "bodies": bodies_encoded,
        "joints": joints_encoded,
    }

    if hasattr(obj, "gym_stats") and obj.gym_stats:
        result["gym"] = obj.gym_stats

    if arena is not None:
        result["combat"] = {
            "robot_a_hp": float(arena.robot_a.total_durability),
            "max_durability_a": float(arena.robot_a.total_durability),  # Initial or current
            "robot_b_hp": float(arena.robot_b.total_durability),
            "max_durability_b": float(arena.robot_b.total_durability),
            "winner": arena.winner,
            "win_reason": arena.win_reason,
            "commentary": getattr(arena, "commentary", "Both fighters maneuver for spatial position in the arena!"),
        }

    return result
