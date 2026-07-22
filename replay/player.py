"""Replay player module loading recorded match trajectories and rendering playback with controls."""
from __future__ import annotations
import time
from typing import Any
import pygame

from physics.vec2 import Vec2
from physics.shapes import Polygon
from physics.body import RigidBody
from physics.world import World
from render.renderer import Renderer
from replay.recorder import MatchRecorder


class ReplayPlayer:
    """Renders playback of recorded match JSON trajectories with scrub and speed controls."""

    def __init__(self, replay_data_or_path: dict[str, Any] | str, headless: bool = False) -> None:
        """Initialize replay player with replay recording payload."""
        if isinstance(replay_data_or_path, str):
            self.data = MatchRecorder.load(replay_data_or_path)
        else:
            self.data = replay_data_or_path

        self.metadata = self.data["metadata"]
        self.frames = self.data["frames"]
        self.headless = headless

        self.current_frame_idx = 0
        self.total_frames = len(self.frames)
        self.playback_speed = 1.0
        self.paused = False

        self.renderer: Renderer | None = None
        if not self.headless:
            self.renderer = Renderer(width=800, height=400, title="Robot Combat Replay Player")

    def get_frame(self, frame_idx: int) -> dict[str, Any]:
        """Return recording frame dict at specified index."""
        idx = max(0, min(frame_idx, self.total_frames - 1))
        return self.frames[idx]

    def build_world_for_frame(self, frame_idx: int) -> World:
        """Reconstruct physics bodies in World at recorded positions and angles for rendering."""
        frame = self.get_frame(frame_idx)
        world = World(gravity=(0.0, -9.8))

        # Ground plane
        ground_shape = Polygon([
            Vec2(-30.0, -0.5),
            Vec2(30.0, -0.5),
            Vec2(30.0, 0.5),
            Vec2(-30.0, 0.5),
        ])
        ground = RigidBody(position=(0.0, 0.5), mass=0.0, shape=ground_shape)
        world.add_body(ground)

        for robot_key in ("robot_a", "robot_b"):
            r_data = frame[robot_key]
            for seg_name, b_state in r_data["bodies"].items():
                pos = Vec2(b_state["pos"][0], b_state["pos"][1])
                angle = b_state["angle"]
                # Create visual representation box
                shape = Polygon([
                    Vec2(-0.4, -0.2),
                    Vec2(0.4, -0.2),
                    Vec2(0.4, 0.2),
                    Vec2(-0.4, 0.2),
                ])
                body = RigidBody(position=pos, mass=1.0, shape=shape)
                body.angle = angle
                world.add_body(body)

        return world

    def render_frame(self, frame_idx: int) -> None:
        """Render single replay frame."""
        world = self.build_world_for_frame(frame_idx)
        if self.renderer is not None:
            self.renderer.render(world)

    def play(self, max_render_frames: int | None = None) -> None:
        """Play match recording loop with interactive Pygame input controls."""
        clock = pygame.time.Clock()
        rendered_count = 0

        while self.current_frame_idx < self.total_frames:
            if max_render_frames is not None and rendered_count >= max_render_frames:
                break

            if not self.headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.paused = not self.paused
                        elif event.key == pygame.K_RIGHT:
                            self.current_frame_idx = min(self.total_frames - 1, self.current_frame_idx + 5)
                        elif event.key == pygame.K_LEFT:
                            self.current_frame_idx = max(0, self.current_frame_idx - 5)
                        elif event.key == pygame.K_1:
                            self.playback_speed = 0.5
                        elif event.key == pygame.K_2:
                            self.playback_speed = 1.0
                        elif event.key == pygame.K_3:
                            self.playback_speed = 2.0

            self.render_frame(self.current_frame_idx)
            rendered_count += 1

            if not self.paused:
                self.current_frame_idx += 1

            if not self.headless:
                clock.tick(int(60 * self.playback_speed))

        if self.renderer is not None:
            self.renderer.close()
