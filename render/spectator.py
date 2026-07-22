"""Spectator visualization module providing HUD health bars, damage flashes, and hit markers."""
from __future__ import annotations
from typing import Any
import pygame
from physics.vec2 import Vec2
from render.renderer import Renderer


class SpectatorOverlay:
    """Renders combat HUD, health bars, damage popups, and slow-motion impact triggers."""

    def __init__(self) -> None:
        """Initialize spectator overlay assets and damage event queues."""
        self.active_flashes: list[dict[str, Any]] = []

    def trigger_damage_flash(self, position: Vec2 | tuple[float, float], damage_amount: float) -> None:
        """Queue a dynamic hit flash marker at collision position proportional to damage."""
        if isinstance(position, tuple):
            pos = Vec2(position[0], position[1])
        else:
            pos = position

        self.active_flashes.append({
            "pos": pos,
            "damage": damage_amount,
            "ttl": 15,  # 15 frames duration
        })

    def update_and_draw(
        self,
        renderer: Renderer,
        durability_a: float,
        max_durability_a: float,
        durability_b: float,
        max_durability_b: float,
        robot_a_name: str = "Robot A",
        robot_b_name: str = "Robot B",
    ) -> None:
        """Draw top HUD health bars and active hit markers onto renderer surface."""
        screen = renderer.screen
        width, height = renderer.width, renderer.height

        # Draw HUD Header Bar Background
        pygame.draw.rect(screen, (30, 30, 40), (0, 0, width, 50))
        pygame.draw.line(screen, (80, 80, 100), (0, 50), (width, 50), 2)

        font = pygame.font.SysFont("Arial", 16, bold=True)

        # Robot A Health Bar (Left, Red)
        frac_a = max(0.0, min(1.0, durability_a / max(1.0, max_durability_a)))
        bar_w = int(width * 0.35)
        pygame.draw.rect(screen, (80, 20, 20), (20, 15, bar_w, 20), border_radius=4)
        pygame.draw.rect(screen, (220, 50, 50), (20, 15, int(bar_w * frac_a), 20), border_radius=4)
        lbl_a = font.render(f"{robot_a_name}: {durability_a:.0f}/{max_durability_a:.0f} HP", True, (255, 255, 255))
        screen.blit(lbl_a, (20, 16))

        # Robot B Health Bar (Right, Blue)
        frac_b = max(0.0, min(1.0, durability_b / max(1.0, max_durability_b)))
        pygame.draw.rect(screen, (20, 50, 80), (width - 20 - bar_w, 15, bar_w, 20), border_radius=4)
        pygame.draw.rect(screen, (50, 150, 240), (width - 20 - bar_w, 15, int(bar_w * frac_b), 20), border_radius=4)
        lbl_b = font.render(f"{robot_b_name}: {durability_b:.0f}/{max_durability_b:.0f} HP", True, (255, 255, 255))
        screen.blit(lbl_b, (width - 20 - bar_w + 10, 16))

        # Render Active Damage Flashes
        surviving_flashes = []
        for flash in self.active_flashes:
            screen_pos = renderer.world_to_screen(flash["pos"])
            alpha_ratio = flash["ttl"] / 15.0
            radius = int((1.0 - alpha_ratio * 0.5) * (10 + flash["damage"] * 0.2))

            # Outer explosion flash circle
            pygame.draw.circle(screen, (255, 200, 50), screen_pos, radius, 2)
            pygame.draw.circle(screen, (255, 100, 0), screen_pos, max(2, radius // 2))

            flash["ttl"] -= 1
            if flash["ttl"] > 0:
                surviving_flashes.append(flash)

        self.active_flashes = surviving_flashes
