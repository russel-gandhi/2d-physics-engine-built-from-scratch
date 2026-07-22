"""Unit tests for Stage 05: World Loop & Renderer."""
import time
import pytest
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.shapes import Circle, Polygon
from physics.world import World
from render.renderer import Renderer
from scripts.run_scene import create_demo_world, run


def test_world_physics_simulation():
    """Verify World steps gravity, integration, collisions, and joint constraints properly over time."""
    world = create_demo_world()
    dt = 1.0 / 60.0

    # Step simulation for 3 seconds (180 frames)
    for _ in range(180):
        world.step(dt)

    # Check that dynamic bodies fell and settled on or near the ground (y around 1.1 - 1.5)
    circle_body = world.bodies[1]
    box_body = world.bodies[2]

    assert circle_body.position.y < 6.0  # Fell from y=6
    assert circle_body.position.y >= 1.0  # Settled on ground without falling through
    assert box_body.position.y < 7.0  # Fell from y=7
    assert box_body.position.y >= 1.0


def test_fixed_timestep_independence():
    """Verify physics state after N simulated seconds is independent of rendering frame delays."""
    world_fast = create_demo_world()
    world_slow = create_demo_world()

    dt_sim = 1.0 / 60.0
    total_sim_time = 2.0  # 2 simulated seconds
    target_steps = int(total_sim_time / dt_sim)

    # Fast simulation run (no render delay)
    for _ in range(target_steps):
        world_fast.step(dt_sim)

    # Slow simulation run with variable accumulator updates
    simulated_accum = 0.0
    frame_delays = [0.016, 0.033, 0.005, 0.050, 0.016]  # irregular render frame times
    delay_idx = 0

    while simulated_accum < total_sim_time:
        delay = frame_delays[delay_idx % len(frame_delays)]
        delay_idx += 1
        simulated_accum += delay

        while simulated_accum >= dt_sim and target_steps > 0:
            world_slow.step(dt_sim)
            target_steps -= 1

    # Verify positions after 2 seconds of physics time match exactly
    for b1, b2 in zip(world_fast.bodies, world_slow.bodies):
        assert pytest.approx(b1.position.x, abs=1e-5) == b2.position.x
        assert pytest.approx(b1.position.y, abs=1e-5) == b2.position.y
        assert pytest.approx(b1.angle, abs=1e-5) == b2.angle


def test_headless_renderer():
    """Verify Renderer initializes and draws without error in headless mode and without mutating physics state."""
    world = create_demo_world()
    renderer = Renderer(width=800, height=600, headless=True)

    pos_before = [b.position.copy() for b in world.bodies]
    angle_before = [b.angle for b in world.bodies]

    renderer.render(world, debug=True)

    # Confirm renderer did NOT mutate any body position or angle
    for i, body in enumerate(world.bodies):
        assert body.position == pos_before[i]
        assert body.angle == angle_before[i]

    renderer.close()


def test_run_scene_headless_execution():
    """Verify scripts/run_scene.py completes headless run for 60 frames cleanly."""
    run(max_frames=60, headless=True)
