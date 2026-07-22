"""Match recording module serializing 1v1 arena physics trajectories and combat events."""
from __future__ import annotations
import json
import os
from typing import Any
from combat.arena import Arena


class MatchRecorder:
    """Records per-frame robot body transforms, health status, and combat events."""

    def __init__(self) -> None:
        """Initialize frame buffer and metadata for a match recording."""
        self.frames: list[dict[str, Any]] = []
        self.metadata: dict[str, Any] = {}

    def start_match(self, robot_a_name: str, robot_b_name: str) -> None:
        """Initialize match metadata header."""
        self.frames = []
        self.metadata = {
            "robot_a": robot_a_name,
            "robot_b": robot_b_name,
            "total_frames": 0,
            "winner": None,
            "win_reason": None,
        }

    def record_step(self, arena: Arena, damage_events: list[dict[str, Any]] | None = None) -> None:
        """Capture body positions, angles, velocities, health, and damage events for current step."""
        def extract_robot_state(robot) -> dict[str, Any]:
            bodies_state = {}
            for name, body in robot.bodies.items():
                bodies_state[name] = {
                    "pos": [float(body.position.x), float(body.position.y)],
                    "angle": float(body.angle),
                    "vel": [float(body.velocity.x), float(body.velocity.y)],
                    "ang_vel": float(body.angular_velocity),
                }
            return {
                "segment_health": {k: float(v) for k, v in robot.segment_health.items()},
                "total_durability": float(robot.total_durability),
                "bodies": bodies_state,
            }

        frame_data = {
            "step": int(arena.current_step),
            "robot_a": extract_robot_state(arena.robot_a),
            "robot_b": extract_robot_state(arena.robot_b),
            "damage_events": damage_events if damage_events is not None else [],
        }

        self.frames.append(frame_data)
        self.metadata["total_frames"] = len(self.frames)

    def end_match(self, winner: str | None, win_reason: str) -> None:
        """Finalize match winner metadata."""
        self.metadata["winner"] = winner
        self.metadata["win_reason"] = win_reason

    def save(self, filepath: str) -> None:
        """Save recording payload to JSON file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        payload = {
            "metadata": self.metadata,
            "frames": self.frames,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> dict[str, Any]:
        """Load match replay recording from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
