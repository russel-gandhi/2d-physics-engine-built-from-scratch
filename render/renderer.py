"""Pygame renderer for visualization of bodies, joints, and debug overlays."""
from __future__ import annotations
import math
import os
import pygame
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.shapes import Circle, Polygon
from physics.joints import DistanceJoint, RevoluteJoint
from physics.world import World


class Renderer:
    """Renders 2D physics world onto a pygame display."""

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        scale: float = 50.0,
        camera_offset: Vec2 | tuple = (400, 500),
        caption: str = "RoboForge Arena — Physics Simulation",
        headless: bool = False,
    ) -> None:
        """Initialize renderer window, coordinate transformations, and display surface."""
        self.width = width
        self.height = height
        self.scale = scale
        self.camera_offset = Vec2(camera_offset)
        self.caption = caption
        self.headless = headless

        if self.headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"

        pygame.init()
        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

    def world_to_screen(self, pos: Vec2 | tuple) -> tuple[int, int]:
        """Convert world-space position (meters, +y up) to screen coordinates (pixels, +y down)."""
        p = pos if isinstance(pos, Vec2) else Vec2(pos)
        sx = int(self.camera_offset.x + p.x * self.scale)
        sy = int(self.camera_offset.y - p.y * self.scale)
        return (sx, sy)

    def screen_to_world(self, screen_pos: tuple[int, int]) -> Vec2:
        """Convert screen position (pixels) to world position (meters)."""
        wx = (screen_pos[0] - self.camera_offset.x) / self.scale
        wy = (self.camera_offset.y - screen_pos[1]) / self.scale
        return Vec2(wx, wy)

    def render(self, world: World, debug: bool = True) -> None:
        """Render the physics world. Only reads physics state, never mutates it."""
        self.screen.fill((25, 25, 30))  # Dark background

        # 1. Draw Bodies
        for body in world.bodies:
            color = (120, 120, 130) if body.is_static else (80, 180, 240)
            outline_color = (200, 200, 220)

            if isinstance(body.shape, Circle):
                center_screen = self.world_to_screen(body.position)
                radius_px = int(body.shape.radius * self.scale)
                pygame.draw.circle(self.screen, color, center_screen, radius_px)
                pygame.draw.circle(self.screen, outline_color, center_screen, radius_px, 2)

                # Draw angle indicator line
                line_end_world = body.position + Vec2(body.shape.radius, 0.0).rotate(body.angle)
                line_end_screen = self.world_to_screen(line_end_world)
                pygame.draw.line(self.screen, (255, 255, 255), center_screen, line_end_screen, 2)

            elif isinstance(body.shape, Polygon):
                world_verts = body.shape.get_world_vertices(body)
                screen_verts = [self.world_to_screen(v) for v in world_verts]
                if len(screen_verts) >= 3:
                    pygame.draw.polygon(self.screen, color, screen_verts)
                    pygame.draw.polygon(self.screen, outline_color, screen_verts, 2)

        # 2. Draw Joints
        for joint in world.joints:
            p_a = joint.body_a.position + joint.anchor_a.rotate(joint.body_a.angle)
            p_b = joint.body_b.position + joint.anchor_b.rotate(joint.body_b.angle)
            s_a = self.world_to_screen(p_a)
            s_b = self.world_to_screen(p_b)

            if isinstance(joint, DistanceJoint):
                pygame.draw.line(self.screen, (255, 200, 50), s_a, s_b, 3)
            elif isinstance(joint, RevoluteJoint):
                pygame.draw.line(self.screen, (240, 100, 100), s_a, s_b, 2)
                pygame.draw.circle(self.screen, (255, 255, 255), s_a, 5)

        # 3. Draw Debug Overlay (Contacts & Velocity Vectors)
        if debug:
            for contact in world.last_contacts:
                cp_screen = self.world_to_screen(contact.point)
                pygame.draw.circle(self.screen, (255, 50, 50), cp_screen, 4)
                # Draw contact normal vector
                n_end_world = contact.point + contact.normal * 0.4
                n_end_screen = self.world_to_screen(n_end_world)
                pygame.draw.line(self.screen, (255, 100, 100), cp_screen, n_end_screen, 2)

            for body in world.bodies:
                if not body.is_static and body.velocity.length_sq() > 1e-4:
                    start_s = self.world_to_screen(body.position)
                    end_s = self.world_to_screen(body.position + body.velocity * 0.2)
                    pygame.draw.line(self.screen, (50, 255, 100), start_s, end_s, 2)

        pygame.display.flip()

    def close(self) -> None:
        """Close renderer and quit pygame."""
        pygame.quit()
