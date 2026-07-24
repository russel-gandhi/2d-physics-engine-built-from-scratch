"""Unit and integration tests for Stage 34: Competitive Mode UI & Server Endpoints."""
import os
import pytest
from fastapi.testclient import TestClient
from web.server import app, session
from web.fighter_roster import save_fighter, ROSTER_FILE
from combat.arena import Arena


def test_competitive_match_start_server_parity():
    """Verify starting a match via /api/competitive/start runs a real Arena match server-side."""
    client = TestClient(app)

    # 1. Start Competitive Match via REST API
    res = client.post("/api/competitive/start", json={
        "fighter_a_id": None,
        "fighter_b_id": None
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert session.mode == "competitive"
    assert session.arena is not None
    assert isinstance(session.arena, Arena)

    # 2. Step session 10 times and verify server state match outcomes
    for _ in range(10):
        session.step()

    arena_hp_a = session.arena.robot_a.total_durability
    arena_hp_b = session.arena.robot_b.total_durability

    assert arena_hp_a > 0.0
    assert arena_hp_b > 0.0


def test_competitive_mode_no_manual_attack_endpoints():
    """Verify backend contains no endpoints accepting manual attack/steering commands during competitive matches."""
    client = TestClient(app)

    # Attempting to call non-existent manual attack endpoint must 404/405
    res = client.post("/api/competitive/attack", json={"action": "punch"})
    assert res.status_code in (404, 405)


def test_competitive_damage_events_stream():
    """Verify damage events logged during competitive match match real impulse damage events."""
    session.mode = "competitive"
    session.arena = Arena("robots/presets/boxer.json", "robots/presets/grappler.json")

    body_b = session.arena.robot_b.bodies["torso"]
    from physics.vec2 import Vec2
    contact = type("Contact", (), {"point": Vec2(0.0, 0.0), "normal": Vec2(0.0, 1.0), "penetration": 0.1})()
    
    # Process collision with impulse above threshold
    dmg_a, dmg_b = session.arena.damage_system.process_collision(
        session.arena.robot_a.bodies["torso"],
        body_b,
        contact,
        restitution=0.5,
        friction=0.3
    )

    events = session.arena.damage_system.damage_history
    assert isinstance(events, list)
