"""Interactive physics simulation test scene using fixed-timestep physics loop and pygame rendering."""
import math
import sys
import time
import pygame
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.shapes import Circle, Polygon
from physics.joints import DistanceJoint, RevoluteJoint
from physics.world import World
from render.renderer import Renderer


def create_demo_world() -> World:
    """Build a demo physics world with ground, bouncing shapes, and joint constraints."""
    world = World(gravity=(0.0, -9.8), substeps=8, restitution=0.4, friction=0.3)

    # Static ground
    ground_poly = Polygon([
        Vec2(-10.0, -0.5),
        Vec2(10.0, -0.5),
        Vec2(10.0, 0.5),
        Vec2(-10.0, 0.5),
    ])
    ground = RigidBody(position=(0.0, 0.5), mass=0.0, shape=ground_poly)
    world.add_body(ground)

    # Dynamic Bouncing Circle
    circle = RigidBody(position=(-2.0, 6.0), mass=1.0, shape=Circle(0.6))
    world.add_body(circle)

    # Dynamic Bouncing Box
    box_poly = Polygon([
        Vec2(-0.5, -0.5),
        Vec2(0.5, -0.5),
        Vec2(0.5, 0.5),
        Vec2(-0.5, 0.5),
    ])
    box = RigidBody(position=(2.0, 7.0), angle=0.4, mass=1.5, moment_of_inertia=0.5, shape=box_poly)
    world.add_body(box)

    # Pendulum attached to static pin
    pin = RigidBody(position=(0.0, 8.0), mass=0.0)
    pendulum_bob = RigidBody(position=(1.5, 8.0), mass=1.0, moment_of_inertia=0.1, shape=Circle(0.4))
    joint = RevoluteJoint(pin, (0, 0), pendulum_bob, (-1.5, 0))
    world.add_body(pin)
    world.add_body(pendulum_bob)
    world.add_joint(joint)

    return world


def run(max_frames: int | None = None, headless: bool = False, sleep_delay: float = 0.0) -> None:
    """Run physics simulation with fixed timestep accumulator."""
    world = create_demo_world()
    renderer = Renderer(width=800, height=600, scale=50.0, camera_offset=(400, 450), headless=headless)

    dt_sim = 1.0 / 60.0
    accumulator = 0.0
    last_time = time.perf_counter()
    frame_count = 0

    running = True
    while running:
        current_time = time.perf_counter()
        frame_time = min(current_time - last_time, 0.25)  # Cap max frame time to prevent spiral of death
        last_time = current_time

        accumulator += frame_time

        # Process Pygame Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Fixed timestep physics updates
        while accumulator >= dt_sim:
            world.step(dt_sim)
            accumulator -= dt_sim

        # Optional artificial render sleep to verify fixed-timestep independence
        if sleep_delay > 0.0:
            time.sleep(sleep_delay)

        # Render frame
        renderer.render(world, debug=True)
        frame_count += 1

        if max_frames is not None and frame_count >= max_frames:
            running = False

    renderer.close()


if __name__ == "__main__":
    headless_flag = "--headless" in sys.argv
    run(max_frames=300 if headless_flag else None, headless=headless_flag)
