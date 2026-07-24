"""Unit and integration tests for Stage 38: Live Match Commentary."""
import os
import pytest
from web.commentary import generate_match_commentary
from web.state_encoder import encode_state
from combat.arena import Arena


def test_commentary_generation_with_mock_llm(monkeypatch):
    """Verify commentary generator synthesizes match telemetry into short sports commentary."""
    monkeypatch.setenv("GEMINI_MOCK", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")

    telemetry = {
        "hp_a": 80.0,
        "hp_b": 45.0,
        "distance": 1.2,
        "recent_events": [{"damage": 15.0, "segment_id": "torso"}]
    }

    caption = generate_match_commentary(telemetry)
    assert isinstance(caption, str)
    assert len(caption) > 0
    assert "Commentary unavailable" not in caption


def test_commentary_graceful_error_handling(monkeypatch):
    """Verify broken API key or network failure returns 'Commentary unavailable' without crashing."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MOCK", raising=False)

    telemetry = {"hp_a": 100.0, "hp_b": 100.0}
    caption = generate_match_commentary(telemetry)

    assert caption == "Commentary unavailable"


def test_encoded_state_contains_commentary_field():
    """Verify state encoder serializes commentary field in combat mode output."""
    arena = Arena("robots/presets/boxer.json", "robots/presets/grappler.json")
    arena.commentary = "Red Corner launches a devastating counter punch!"

    state = encode_state(arena, mode="competitive")
    assert "combat" in state
    assert "commentary" in state["combat"]
    assert state["combat"]["commentary"] == "Red Corner launches a devastating counter punch!"
