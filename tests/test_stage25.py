"""Unit tests for Stage 25: Sandbox Mode."""
import pytest
from physics.vec2 import Vec2
from sandbox.sandbox_mode import SandboxMode


def test_sandbox_mode_gravity_and_terrain_toggling():
    """Verify live gravity mutation and terrain resetting in SandboxMode."""
    sandbox = SandboxMode(headless=True)
    initial_g = Vec2(sandbox.world.gravity.x, sandbox.world.gravity.y)

    new_g = sandbox.toggle_gravity()
    assert sandbox.world.gravity == new_g
    assert (sandbox.world.gravity.x, sandbox.world.gravity.y) != (initial_g.x, initial_g.y)

    initial_terrain = sandbox.terrain_modes[sandbox.terrain_idx]
    next_terrain = sandbox.toggle_terrain()
    assert next_terrain != initial_terrain


def test_sandbox_mode_spawning_shapes_and_robots():
    """Verify spawning dynamic shapes and robot presets into SandboxMode world."""
    sandbox = SandboxMode(headless=True)
    initial_body_count = len(sandbox.world.bodies)

    shape_body = sandbox.spawn_shape((0.0, 5.0))
    assert len(sandbox.world.bodies) == initial_body_count + 1
    assert shape_body in sandbox.world.bodies

    robot = sandbox.spawn_robot_preset("robots/presets/lightweight_fighter.json", (0.0, 4.0))
    assert len(sandbox.world.bodies) > initial_body_count + 1
    assert len(robot.bodies) >= 2


def test_sandbox_mode_world_reset():
    """Verify reset_world completely clears dynamic spawned bodies and rebuilds terrain."""
    sandbox = SandboxMode(headless=True)

    sandbox.spawn_shape((1.0, 5.0))
    sandbox.spawn_robot_preset("robots/presets/lightweight_fighter.json", (-2.0, 4.0))

    assert len(sandbox.world.bodies) > 2

    sandbox.reset_world()
    # Reset restores only terrain ground body (1 body)
    assert len(sandbox.world.bodies) == 1
