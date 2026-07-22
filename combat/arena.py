"""Local 1v1 Combat Arena managing physics simulation, match loop, and win/loss conditions."""
from __future__ import annotations
import os
from typing import Any
import numpy as np

from physics.vec2 import Vec2
from physics.shapes import Polygon
from physics.body import RigidBody
from physics.world import World
from combat.damage import DamageSystem, apply_impulse_damage
from robots.robot_spec import RobotSpec, Robot, build_robot


class Arena:
    """Local 1v1 match loop simulating two robots in a shared physics world."""

    def __init__(
        self,
        robot_a_spec: RobotSpec | str,
        robot_b_spec: RobotSpec | str,
        max_steps: int = 1800,  # 30 seconds @ 60 FPS
        frame_skip: int = 4,
        spawn_x_offset: float = 4.0,
    ) -> None:
        """Initialize Arena with specs for Robot A and Robot B."""
        if isinstance(robot_a_spec, str):
            self.spec_a = RobotSpec.from_json(robot_a_spec)
        else:
            self.spec_a = robot_a_spec

        if isinstance(robot_b_spec, str):
            self.spec_b = RobotSpec.from_json(robot_b_spec)
        else:
            self.spec_b = robot_b_spec

        self.max_steps = max_steps
        self.frame_skip = frame_skip
        self.spawn_x_offset = spawn_x_offset

        self.world: World = World(gravity=(0.0, -9.8))
        self.damage_system = DamageSystem(threshold=8.0, damage_scale=1.0)

        # Build Arena Ground
        ground_shape = Polygon([
            Vec2(-30.0, -0.5),
            Vec2(30.0, -0.5),
            Vec2(30.0, 0.5),
            Vec2(-30.0, 0.5),
        ])
        self.ground = RigidBody(position=(0.0, 0.5), mass=0.0, shape=ground_shape)
        self.world.add_body(self.ground)

        # Build Robots
        self.robot_a: Robot = build_robot(
            self.spec_a, self.world, base_position=(-self.spawn_x_offset, 2.0)
        )
        self.robot_b: Robot = build_robot(
            self.spec_b, self.world, base_position=(self.spawn_x_offset, 2.0)
        )

        self.damage_system.register_robot(self.robot_a)
        self.damage_system.register_robot(self.robot_b)

        self.current_step = 0
        self.winner: str | None = None
        self.win_reason: str = "in_progress"

    def get_observation(self, robot: Robot, opponent: Robot) -> np.ndarray:
        """Construct relative combat observation vector for a robot facing an opponent."""
        torso = robot.main_body
        opp_torso = opponent.main_body

        rel_pos = opp_torso.position - torso.position
        rel_vel = opp_torso.velocity - torso.velocity

        obs_list = [
            float(torso.position.y),
            float(torso.velocity.x),
            float(torso.velocity.y),
            float(torso.angle),
            float(torso.angular_velocity),
            float(rel_pos.x),
            float(rel_pos.y),
            float(rel_vel.x),
            float(rel_vel.y),
            float(robot.total_durability),
            float(opponent.total_durability),
        ]

        # Joint relative angles and angular velocities
        for j_spec in robot.spec.joints:
            parent = robot.bodies[j_spec.parent_segment]
            child = robot.bodies[j_spec.child_segment]
            obs_list.append(float(child.angle - parent.angle))
            obs_list.append(float(child.angular_velocity - parent.angular_velocity))

        return np.array(obs_list, dtype=np.float32)

    def step(
        self, action_a: np.ndarray | list[float], action_b: np.ndarray | list[float]
    ) -> tuple[np.ndarray, np.ndarray, float, float, bool, dict[str, Any]]:
        """Advance match by 1 step (frame_skip substeps) and check win conditions."""
        if self.winner is not None:
            obs_a = self.get_observation(self.robot_a, self.robot_b)
            obs_b = self.get_observation(self.robot_b, self.robot_a)
            info = {
                "winner": self.winner,
                "reason": self.win_reason,
                "durability_a": self.robot_a.total_durability,
                "durability_b": self.robot_b.total_durability,
            }
            return obs_a, obs_b, 0.0, 0.0, True, info

        # Apply motor actions
        self.robot_a.apply_actions(action_a)
        self.robot_b.apply_actions(action_b)

        # Physics & Damage resolution loop
        dt = 1.0 / 60.0
        for _ in range(self.frame_skip):
            self.world.step(dt)
            for contact in self.world.last_contacts:
                if contact.body_a is not None and contact.body_b is not None:
                    if id(contact.body_a) in self.damage_system.body_to_robot_segment:
                        r_a, seg_a = self.damage_system.body_to_robot_segment[id(contact.body_a)]
                        apply_impulse_damage(r_a, seg_a, contact.penetration * 30.0, threshold=self.damage_system.threshold, scale=self.damage_system.damage_scale)
                    if id(contact.body_b) in self.damage_system.body_to_robot_segment:
                        r_b, seg_b = self.damage_system.body_to_robot_segment[id(contact.body_b)]
                        apply_impulse_damage(r_b, seg_b, contact.penetration * 30.0, threshold=self.damage_system.threshold, scale=self.damage_system.damage_scale)

        self.current_step += 1

        # Check Win / Loss / Termination Criteria
        dur_a = self.robot_a.total_durability
        dur_b = self.robot_b.total_durability
        chassis_a_alive = self.robot_a.segment_health.get("torso", 1.0) > 0.0
        chassis_b_alive = self.robot_b.segment_health.get("torso", 1.0) > 0.0

        out_of_bounds_a = self.robot_a.main_body.position.y < -3.0 or abs(self.robot_a.main_body.position.x) > 28.0
        out_of_bounds_b = self.robot_b.main_body.position.y < -3.0 or abs(self.robot_b.main_body.position.x) > 28.0

        done = False

        if not chassis_a_alive and not chassis_b_alive:
            self.winner = "draw"
            self.win_reason = "simultaneous_destruction"
            done = True
        elif not chassis_a_alive or out_of_bounds_a:
            self.winner = "robot_b"
            self.win_reason = "chassis_destruction" if not chassis_a_alive else "out_of_bounds"
            done = True
        elif not chassis_b_alive or out_of_bounds_b:
            self.winner = "robot_a"
            self.win_reason = "chassis_destruction" if not chassis_b_alive else "out_of_bounds"
            done = True
        elif self.current_step >= self.max_steps:
            done = True
            if dur_a > dur_b:
                self.winner = "robot_a"
                self.win_reason = "timeout"
            elif dur_b > dur_a:
                self.winner = "robot_b"
                self.win_reason = "timeout"
            else:
                self.winner = "draw"
                self.win_reason = "timeout"

        # Combat reward signal: damage dealt - damage taken + win bonus
        rew_a = (dur_a - self.robot_a.total_durability) - (dur_b - self.robot_b.total_durability)
        rew_b = -rew_a

        if done:
            if self.winner == "robot_a":
                rew_a += 10.0
                rew_b -= 10.0
            elif self.winner == "robot_b":
                rew_b += 10.0
                rew_a -= 10.0

        obs_a = self.get_observation(self.robot_a, self.robot_b)
        obs_b = self.get_observation(self.robot_b, self.robot_a)

        info = {
            "winner": self.winner,
            "reason": self.win_reason,
            "durability_a": self.robot_a.total_durability,
            "durability_b": self.robot_b.total_durability,
            "step": self.current_step,
        }

        return obs_a, obs_b, rew_a, rew_b, done, info
