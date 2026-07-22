"""Interactive Sandbox mode enabling real-time physics scene manipulation, gravity toggling, and robot spawning."""
from __future__ import annotations
import random
from typing import Any
import pygame

from physics.vec2 import Vec2
from physics.shapes import Polygon, Circle
from physics.body import RigidBody
from physics.world import World
from robots.robot_spec import RobotSpec, build_robot
from render.renderer import Renderer


class SandboxMode:
    """Free-play interactive laboratory for spawning physics shapes and testing robot dynamics."""

    def __init__(self, headless: bool = False) -> None:
        """Initialize empty Sandbox World and interactive environment."""
        self.headless = headless
        self.gravity_modes = [(0.0, -9.8), (0.0, 0.0), (0.0, -25.0), (0.0, 9.8)]
        self.gravity_idx = 0

        self.terrain_modes = ["flat", "sloped", "empty"]
        self.terrain_idx = 0

        self.paused = False
        self.renderer: Renderer | None = None
        if not self.headless:
            self.renderer = Renderer(width=800, height=400, title="RoboForge Arena — Sandbox Mode")

        self.world: World = World(gravity=self.gravity_modes[0])
        self.setup_terrain()

    def setup_terrain(self) -> None:
        """Construct terrain ground in current World according to terrain_mode."""
        mode = self.terrain_modes[self.terrain_idx]

        if mode == "flat":
            ground_shape = Polygon([
                Vec2(-30.0, -0.5),
                Vec2(30.0, -0.5),
                Vec2(30.0, 0.5),
                Vec2(-30.0, 0.5),
            ])
            ground = RigidBody(position=(0.0, 0.5), mass=0.0, shape=ground_shape)
            self.world.add_body(ground)
        elif mode == "sloped":
            slope_shape = Polygon([
                Vec2(-30.0, -2.0),
                Vec2(30.0, 4.0),
                Vec2(30.0, -3.0),
                Vec2(-30.0, -3.0),
            ])
            slope = RigidBody(position=(0.0, 0.0), mass=0.0, shape=slope_shape)
            self.world.add_body(slope)

    def reset_world(self) -> None:
        """Clear all bodies and rebuild world."""
        self.world = World(gravity=self.gravity_modes[self.gravity_idx])
        self.setup_terrain()

    def toggle_gravity(self) -> Vec2:
        """Cycle gravity setting and mutate world.gravity live."""
        self.gravity_idx = (self.gravity_idx + 1) % len(self.gravity_modes)
        new_g = self.gravity_modes[self.gravity_idx]
        self.world.gravity = Vec2(new_g[0], new_g[1])
        return self.world.gravity

    def toggle_terrain(self) -> str:
        """Cycle terrain setting and rebuild world."""
        self.terrain_idx = (self.terrain_idx + 1) % len(self.terrain_modes)
        self.reset_world()
        return self.terrain_modes[self.terrain_idx]

    def spawn_shape(self, position: tuple[float, float] = (0.0, 5.0)) -> RigidBody:
        """Spawn dynamic box shape into World at specified position."""
        box_shape = Polygon([
            Vec2(-0.5, -0.5),
            Vec2(0.5, -0.5),
            Vec2(0.5, 0.5),
            Vec2(-0.5, 0.5),
        ])
        body = RigidBody(position=position, mass=2.0, shape=box_shape)
        self.world.add_body(body)
        return body

    def spawn_robot_preset(
        self, spec_path: str = "robots/presets/lightweight_fighter.json", position: tuple[float, float] = (0.0, 4.0)
    ) -> Any:
        """Spawn robot preset into World."""
        spec = RobotSpec.from_json(spec_path)
        robot = build_robot(spec, self.world, base_position=position)
        return robot

    def step(self) -> None:
        """Advance physics simulation by 1 step if not paused."""
        if not self.paused:
            self.world.step(1.0 / 60.0)

        if not self.headless and self.renderer is not None:
            self.renderer.render(self.world)

    def run_interactive_loop(self, max_steps: int | None = None) -> None:
        """Run interactive event loop listening to keyboard bindings."""
        clock = pygame.time.Clock()
        step_count = 0

        while True:
            if max_steps is not None and step_count >= max_steps:
                break

            if not self.headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.paused = not self.paused
                        elif event.key == pygame.K_g:
                            self.toggle_gravity()
                        elif event.key == pygame.K_t:
                            self.toggle_terrain()
                        elif event.key == pygame.K_s:
                            self.spawn_shape((random.uniform(-4, 4), 6.0))
                        elif event.key == pygame.K_r:
                            self.spawn_robot_preset("robots/presets/lightweight_fighter.json", (random.uniform(-3, 3), 4.0))
                        elif event.key == pygame.K_c:
                            self.reset_world()

            self.step()
            step_count += 1

            if not self.headless:
                clock.tick(60)

        if self.renderer is not None:
            self.renderer.close()
