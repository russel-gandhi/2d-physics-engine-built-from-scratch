"""Unit and integration tests for Stage 32: Fighter Archetype Presets."""
import os
import pytest
from physics.world import World
from robots.robot_spec import RobotSpec, build_robot


def test_archetype_presets_loading_and_simulation():
    """Verify all preset files (including Boxer and Grappler) load and simulate cleanly in World."""
    preset_dir = "robots/presets"
    preset_files = [f for f in os.listdir(preset_dir) if f.endswith(".json")]

    assert len(preset_files) >= 4  # lightweight, heavy, boxer, grappler

    for p_file in preset_files:
        path = os.path.join(preset_dir, p_file)
        spec = RobotSpec.from_json(path)
        world = World(gravity=(0.0, -9.8))
        robot = build_robot(spec, world, base_position=(0.0, 2.0))

        assert len(robot.bodies) > 0
        assert robot.total_mass > 0.0

        # Step physics world for 10 frames
        for _ in range(10):
            robot.apply_actions([0.5] * len(robot.joints))
            world.step(1.0 / 60.0)


def test_archetype_tradeoff_physical_behavior():
    """Verify Boxer and Grappler exhibit empirically distinct acceleration and mass dynamics under identical motor inputs."""
    boxer_spec = RobotSpec.from_json("robots/presets/boxer.json")
    grappler_spec = RobotSpec.from_json("robots/presets/grappler.json")

    # 1. Verify Mass Tradeoffs
    world_b = World(gravity=(0.0, 0.0))
    robot_boxer = build_robot(boxer_spec, world_b, base_position=(0.0, 2.0))

    world_g = World(gravity=(0.0, 0.0))
    robot_grappler = build_robot(grappler_spec, world_g, base_position=(0.0, 2.0))

    assert robot_grappler.total_mass > robot_boxer.total_mass

    # 2. Verify Initial Angular Acceleration Tradeoff (F = ma) under torque
    robot_boxer.apply_actions([1.0] * len(robot_boxer.motorized_joints))
    world_b.step(1.0 / 60.0)

    robot_grappler.apply_actions([1.0] * len(robot_grappler.motorized_joints))
    world_g.step(1.0 / 60.0)

    # Higher torque / lower inertia on Boxer produces higher initial leg angular velocity
    boxer_leg_w = abs(robot_boxer.bodies["left_leg"].angular_velocity)
    grappler_leg_w = abs(robot_grappler.bodies["left_leg"].angular_velocity)

    assert boxer_leg_w > grappler_leg_w


def test_preset_presentation_metadata_data_driven():
    """Verify presentation metadata (display_name, description, color) is present on all preset JSON files."""
    preset_dir = "robots/presets"
    for p_file in os.listdir(preset_dir):
        if p_file.endswith(".json"):
            spec = RobotSpec.from_json(os.path.join(preset_dir, p_file))
            raw_json = spec.to_dict()

            assert "display_name" in raw_json
            assert "description" in raw_json
            assert "color" in raw_json
            assert raw_json["color"].startswith("#")
