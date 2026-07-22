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
    """Verify lightweight fighter achieves higher speed than heavy tank under identical action torque."""
    results = run_robot_scene_test(steps=120, verbose=False)

    # Lightweight fighter has higher acceleration and velocity due to F/m
    assert results["lightweight"]["final_speed"] > results["heavy_tank"]["final_speed"]


def test_data_driven_preset_modification(tmp_path):
    """Verify editing JSON values alters robot mass and simulation dynamics without code modifications."""
    preset_path = str(tmp_path / "custom_bot.json")
    base_spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")

    spec_dict = base_spec.to_dict()
    spec_dict["components"]["torso"][0]["mass"] = 50.0  # Massive chassis weight bump

    with open(preset_path, "w", encoding="utf-8") as f:
        json.dump(spec_dict, f)

    loaded_custom = RobotSpec.from_json(preset_path)
    assert loaded_custom.total_mass == pytest.approx(base_spec.total_mass + 49.0)
