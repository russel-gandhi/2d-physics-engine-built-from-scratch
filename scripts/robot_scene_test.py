"""Benchmark and scene test script comparing Lightweight Fighter vs Heavy Tank dynamic behavior."""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from physics.world import World
from physics.shapes import Polygon
from physics.body import RigidBody
from physics.vec2 import Vec2
from robots.robot_spec import RobotSpec, build_robot


def run_robot_scene_test(steps: int = 120, verbose: bool = True) -> dict:
    """Simulate Lightweight Fighter and Heavy Tank under identical motor inputs and log performance."""
    light_spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")
    heavy_spec = RobotSpec.from_json("robots/presets/heavy_tank.json")

    # Build physics world
    world = World(gravity=(0.0, -9.8))

    # Ground
    ground_shape = Polygon([Vec2(-50, -0.5), Vec2(50, -0.5), Vec2(50, 0.5), Vec2(-50, 0.5)])
    ground = RigidBody(position=(0.0, 0.5), mass=0.0, shape=ground_shape)
    world.add_body(ground)

    light_bot = build_robot(light_spec, world, base_position=(-5.0, 2.0))
    heavy_bot = build_robot(heavy_spec, world, base_position=(5.0, 2.0))

    dt = 1.0 / 60.0

    for _ in range(steps):
        # Apply identical motor action torque
        light_bot.apply_actions([1.0])
        heavy_bot.apply_actions([1.0])
        world.step(dt)

    light_speed = float(light_bot.main_body.velocity.length())
    heavy_speed = float(heavy_bot.main_body.velocity.length())

    results = {
        "lightweight": {
            "name": light_spec.name,
            "total_mass": light_spec.total_mass,
            "total_durability": light_spec.total_durability,
            "final_speed": light_speed,
        },
        "heavy_tank": {
            "name": heavy_spec.name,
            "total_mass": heavy_spec.total_mass,
            "total_durability": heavy_spec.total_durability,
            "final_speed": heavy_speed,
        },
    }

    if verbose:
        print("=== Robot Preset Physics Performance Comparison ===")
        print(f"Lightweight Fighter: Mass={results['lightweight']['total_mass']:.1f}kg | Durability={results['lightweight']['total_durability']:.0f}HP | Speed={light_speed:.2f}m/s")
        print(f"Heavy Tank Fighter:  Mass={results['heavy_tank']['total_mass']:.1f}kg | Durability={results['heavy_tank']['total_durability']:.0f}HP | Speed={heavy_speed:.2f}m/s")

    return results


if __name__ == "__main__":
    run_robot_scene_test()
