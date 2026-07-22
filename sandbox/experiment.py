"""Structured physics experiment runner and report generator."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np

from physics.vec2 import Vec2
from physics.shapes import Polygon
from physics.body import RigidBody
from physics.world import World
from robots.robot_spec import RobotSpec, build_robot


@dataclass
class ExperimentConfig:
    """Configuration parameters for a physics experiment run."""

    experiment_name: str
    robot_spec_path: str
    gravity: tuple[float, float] = (0.0, -9.8)
    duration_steps: int = 300
    motor_action: list[float] | None = None


@dataclass
class ExperimentReport:
    """Computed metrics and human-readable summary report from an experiment run."""

    experiment_name: str
    robot_name: str
    gravity_setting: tuple[float, float]
    distance_traveled: float
    max_height_reached: float
    energy_consumed: float
    remaining_durability: float

    def summary_text(self) -> str:
        """Format report matching standard laboratory experiment template."""
        g_mult = abs(self.gravity_setting[1]) / 9.8
        lines = [
            f"Experiment: {self.experiment_name}",
            f"Robot: {self.robot_name}",
            f"Environment: Gravity = {g_mult:.1f}x ({self.gravity_setting[0]:.1f}, {self.gravity_setting[1]:.1f} m/s^2)",
            f"Result: Distance: {self.distance_traveled:.2f}m, Energy Consumed: {self.energy_consumed:.1f} J, Remaining HP: {self.remaining_durability:.0f}",
        ]
        return "\n".join(lines)


def run_experiment(config: ExperimentConfig) -> ExperimentReport:
    """Run deterministic physics experiment simulation and compute exact physical metrics."""
    spec = RobotSpec.from_json(config.robot_spec_path)

    world = World(gravity=config.gravity)

    # Add ground
    ground_shape = Polygon([
        Vec2(-50.0, -0.5),
        Vec2(50.0, -0.5),
        Vec2(50.0, 0.5),
        Vec2(-50.0, 0.5),
    ])
    ground = RigidBody(position=(0.0, 0.5), mass=0.0, shape=ground_shape)
    world.add_body(ground)

    robot = build_robot(spec, world, base_position=(0.0, 2.0))

    initial_x = float(robot.main_body.position.x)
    max_y = float(robot.main_body.position.y)

    action = config.motor_action
    if action is None:
        num_motors = sum(1 for j in spec.joints if j.joint_type == "revolute")
        action = [1.0] * num_motors

    initial_energy = robot.current_energy

    for _ in range(config.duration_steps):
        robot.apply_actions(action)
        # Consume energy per motor activation
        robot.consume_energy(0.1 * len(action))
        world.step(1.0 / 60.0)

        max_y = max(max_y, float(robot.main_body.position.y))

    final_x = float(robot.main_body.position.x)
    distance = abs(final_x - initial_x)
    energy_used = float(initial_energy - robot.current_energy)

    return ExperimentReport(
        experiment_name=config.experiment_name,
        robot_name=spec.name,
        gravity_setting=config.gravity,
        distance_traveled=distance,
        max_height_reached=max_y,
        energy_consumed=energy_used,
        remaining_durability=float(robot.total_durability),
    )


def run_gravity_sweep_experiment(
    robot_spec_path: str, multipliers: list[float] = [0.5, 1.0, 2.5]
) -> list[ExperimentReport]:
    """Run gravity sweep experiment series across multiple gravity multipliers."""
    reports = []
    for m in multipliers:
        config = ExperimentConfig(
            experiment_name=f"Gravity Sweep {m}x",
            robot_spec_path=robot_spec_path,
            gravity=(0.0, -9.8 * m),
            duration_steps=200,
        )
        report = run_experiment(config)
        reports.append(report)
    return reports
