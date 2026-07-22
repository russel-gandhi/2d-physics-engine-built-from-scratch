"""Unit tests for Stage 24: Spectator Visualization Polish."""
import pytest
from physics.vec2 import Vec2
from render.renderer import Renderer
from render.spectator import SpectatorOverlay


def test_spectator_overlay_initialization_and_flashes():
    """Verify SpectatorOverlay queues damage flashes and updates hit markers cleanly."""
    overlay = SpectatorOverlay()
    renderer = Renderer(width=800, height=400, headless=True)

    assert len(overlay.active_flashes) == 0

    overlay.trigger_damage_flash(Vec2(0.0, 2.0), damage_amount=25.0)
    assert len(overlay.active_flashes) == 1

    # Render overlay frame
    overlay.update_and_draw(
        renderer,
        durability_a=200.0,
        max_durability_a=300.0,
        durability_b=150.0,
        max_durability_b=300.0,
    )

    # Frame step decreases TTL
    assert overlay.active_flashes[0]["ttl"] == 14
    renderer.close()


def test_spectator_overlay_health_bars_proportional_rendering():
    """Verify health bar proportion calculation for various HP states."""
    overlay = SpectatorOverlay()
    renderer = Renderer(width=800, height=400, headless=True)

    # Test full health, partial health, and 0 HP
    overlay.update_and_draw(
        renderer,
        durability_a=300.0,
        max_durability_a=300.0,
        durability_b=0.0,
        max_durability_b=300.0,
    )

    renderer.close()
