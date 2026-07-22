"""Unit tests for Stage 19: Local 1v1 Arena."""
import pytest
from combat.arena import Arena
from robots.robot_spec import RobotSpec


def test_arena_initialization_and_observation_shapes():
    """Verify 1v1 Arena initializes both robots in world and returns valid observation vectors."""
    preset_light = "robots/presets/lightweight_fighter.json"
    preset_heavy = "robots/presets/heavy_tank.json"

    arena = Arena(preset_light, preset_heavy, max_steps=100)

    assert len(arena.world.bodies) >= 5  # Ground + 2 bodies per robot
    assert arena.robot_a.total_durability > 0
    assert arena.robot_b.total_durability > 0

    obs_a = arena.get_observation(arena.robot_a, arena.robot_b)
    obs_b = arena.get_observation(arena.robot_b, arena.robot_a)

    assert obs_a.ndim == 1
    assert obs_b.ndim == 1
    assert obs_a.shape == obs_b.shape


def test_arena_chassis_destruction_win_condition():
    """Verify match terminates with robot_a declared winner when robot_b torso health drops to 0."""
    arena = Arena(
        "robots/presets/lightweight_fighter.json",
        "robots/presets/heavy_tank.json",
        max_steps=100,
    )

    # Manually destroy robot_b torso chassis
    arena.robot_b.segment_health["torso"] = 0.0

    obs_a, obs_b, rew_a, rew_b, done, info = arena.step([0.0], [0.0])

    assert done is True
    assert info["winner"] == "robot_a"
    assert info["reason"] == "chassis_destruction"
    assert rew_a > 0.0


def test_arena_out_of_bounds_win_condition():
    """Verify ring out past arena boundary declares opponent winner."""
    arena = Arena(
        "robots/presets/lightweight_fighter.json",
        "robots/presets/heavy_tank.json",
        max_steps=100,
    )

    # Teleport robot_b far below ground plane (ring out)
    arena.robot_b.main_body.position.y = -10.0

    obs_a, obs_b, rew_a, rew_b, done, info = arena.step([0.0], [0.0])

    assert done is True
    assert info["winner"] == "robot_a"
    assert info["reason"] == "out_of_bounds"


def test_arena_timeout_higher_durability_win_condition():
    """Verify match reaching max_steps declares winner based on higher remaining durability."""
    arena = Arena(
        "robots/presets/lightweight_fighter.json",
        "robots/presets/lightweight_fighter.json",
        max_steps=5,
    )

    # Deal partial damage to robot_b torso
    arena.robot_b.apply_damage("torso", 50.0)

    done = False
    info = {}
    for _ in range(5):
        _, _, _, _, done, info = arena.step([0.0], [0.0])

    assert done is True
    assert info["winner"] == "robot_a"
    assert info["reason"] == "timeout"
    assert info["durability_a"] > info["durability_b"]
