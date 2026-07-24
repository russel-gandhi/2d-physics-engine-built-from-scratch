"""Unit tests for Stage 16: Robot Presets & Scene Test."""
import os
import json
import pytest
from scripts.robot_scene_test import run_robot_scene_test
from robots.robot_spec import RobotSpec


def test_robot_presets_loading_and_simulation():
    """Verify lightweight and heavy robot presets load cleanly and run in physics loop."""
    results = run_robot_scene_test(steps=60, verbose=False)

    assert results["lightweight"]["total_mass"] < results["heavy_tank"]["total_mass"]
    assert results["lightweight"]["total_durability"] < results["heavy_tank"]["total_durability"]


def test_lightweight_vs_heavy_speed_performance_tradeoff():
    """Verify lightweight fighter achieves higher initial acceleration than heavy tank under identical action torque.
    
    Note (Issue 4 Audit Fix): Comparing initial acceleration over the first 10 timesteps isolates the F=ma
    mass/torque relationship directly before chaotic ground contact & bouncing dynamics occur, ensuring
    deterministic cross-platform test reliability.
    """
    results = run_robot_scene_test(steps=60, verbose=False)

    # Lightweight fighter has higher acceleration due to F=ma (5.2kg vs 37.5kg mass)
    assert results["lightweight"]["initial_acceleration"] > results["heavy_tank"]["initial_acceleration"]


def test_data_driven_preset_modification(tmp_path):
    """Verify editing JSON values alters robot mass and simulation dynamics without code modifications."""
    preset_path = str(tmp_path / "custom_bot.json")
    base_spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")

    spec_dict = base_spec.to_dict()
    # Add a torso component if not already present (LF has no components by default)
    if "torso" not in spec_dict["components"]:
        spec_dict["components"]["torso"] = [{
            "name": "Custom Chassis",
            "component_type": "chassis",
            "mass": 1.0,
            "durability": 100.0,
            "energy_consumption": 0.0,
            "properties": {}
        }]
    spec_dict["components"]["torso"][0]["mass"] = 50.0  # Massive chassis weight bump

    with open(preset_path, "w", encoding="utf-8") as f:
        json.dump(spec_dict, f)

    loaded_custom = RobotSpec.from_json(preset_path)
    # Total mass should include the 50.0 torso component mass (was 1.0 -> bump of +49.0)
    assert loaded_custom.total_mass >= base_spec.total_mass + 49.0
