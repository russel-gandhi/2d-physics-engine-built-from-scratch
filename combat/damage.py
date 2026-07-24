"""Combat damage & durability module translating physical collision impulses into component damage."""
from __future__ import annotations
from typing import Callable
from physics.collision import Contact
from physics.resolver import resolve_collision
from robots.robot_spec import Robot


def apply_impulse_damage(
    robot: Robot,
    segment_name: str,
    impulse_magnitude: float,
    threshold: float = 10.0,
    scale: float = 1.0,
) -> float:
    """Calculate and apply damage from collision impulse if magnitude exceeds threshold."""
    if impulse_magnitude <= threshold:
        return 0.0

    damage = (impulse_magnitude - threshold) * scale
    robot.apply_damage(segment_name, damage)

    # Check if segment durability depleted -> disable motor joints on broken segment
    if robot.segment_health.get(segment_name, 100.0) <= 0.0:
        disable_segment_motors(robot, segment_name)

    return damage


def disable_segment_motors(robot: Robot, segment_name: str) -> None:
    """Disable motorized revolute joints attached to a broken segment."""
    for j_spec in robot.robot_spec.joints:
        if j_spec.joint_type == "revolute":
            if j_spec.parent_segment == segment_name or j_segment_matches(j_spec, segment_name):
                if j_spec.name in robot.joints:
                    joint = robot.joints[j_spec.name]
                    joint.motor_torque = 0.0
                    j_spec.max_torque = 0.0


def j_segment_matches(j_spec, segment_name: str) -> bool:
    return getattr(j_spec, "child_segment", None) == segment_name


class DamageSystem:
    """Combat listener interpreting physical collision contact impulses without altering core physics engine."""

    def __init__(self, threshold: float = 10.0, damage_scale: float = 1.0) -> None:
        self.threshold = threshold
        self.damage_scale = damage_scale
        self.body_to_robot_segment: dict[int, tuple[Robot, str]] = {}
        self.damage_history: list[dict[str, Any]] = []

    def register_robot(self, robot: Robot) -> None:
        """Register robot body IDs to enable automatic damage tracking upon collision."""
        for seg_name, body in robot.bodies.items():
            self.body_to_robot_segment[id(body)] = (robot, seg_name)

    def process_collision(self, body_a, body_b, contact: Contact, restitution: float = 0.5, friction: float = 0.3) -> tuple[float, float]:
        """Resolve physical collision and extract actual normal impulse magnitude for damage calculation."""
        impulse_mag = resolve_collision(body_a, body_b, contact, restitution=restitution, friction=friction)

        dmg_a = 0.0
        dmg_b = 0.0

        if id(body_a) in self.body_to_robot_segment:
            robot_a, seg_a = self.body_to_robot_segment[id(body_a)]
            dmg_a = apply_impulse_damage(robot_a, seg_a, impulse_mag, threshold=self.threshold, scale=self.damage_scale)
            if dmg_a > 0.0:
                self.damage_history.append({
                    "robot": robot_a.robot_spec.name,
                    "segment_id": seg_a,
                    "damage": dmg_a,
                    "impulse": impulse_mag,
                })

        if id(body_b) in self.body_to_robot_segment:
            robot_b, seg_b = self.body_to_robot_segment[id(body_b)]
            dmg_b = apply_impulse_damage(robot_b, seg_b, impulse_mag, threshold=self.threshold, scale=self.damage_scale)
            if dmg_b > 0.0:
                self.damage_history.append({
                    "robot": robot_b.robot_spec.name,
                    "segment_id": seg_b,
                    "damage": dmg_b,
                    "impulse": impulse_mag,
                })

        return dmg_a, dmg_b
