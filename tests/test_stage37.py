"""Unit and integration tests for Stage 37: Natural Language Training Prompts."""
import os
import pytest
from fastapi.testclient import TestClient
from web.server import app, session
from web.prompt_translator import translate_training_prompt


def test_empty_or_nonsense_prompt_returns_labeled_default(monkeypatch):
    """Verify empty or invalid training prompts return clearly labeled default weights."""
    res_empty = translate_training_prompt("")
    assert res_empty["is_default"] is True
    assert res_empty["weights"]["aggression"] == 0.5

    res_whitespace = translate_training_prompt("   ")
    assert res_whitespace["is_default"] is True


def test_prompt_translation_with_mock_llm(monkeypatch):
    """Verify natural language prompt translation returns parsed weight dictionary."""
    monkeypatch.setenv("GEMINI_MOCK", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")

    res = translate_training_prompt("Train an aggressive Mike Tyson style boxer")
    assert res["is_default"] is False
    assert "weights" in res
    assert "aggression" in res["weights"]


def test_gym_training_behaviour_modification_from_weights():
    """Verify starting Gym training with custom prompt weights modifies reward scaling."""
    client = TestClient(app)

    # 1. Start with Low Aggression (0.1)
    res_low = client.post("/api/gym/start", json={
        "algo": "ga",
        "weights": {"aggression": 0.1, "caution": 0.9, "mobility": 0.5, "stamina_conservation": 0.5}
    })
    assert res_low.status_code == 200
    reward_low = session.sandbox.gym_stats["best_reward"]

    # 2. Start with High Aggression (0.9)
    res_high = client.post("/api/gym/start", json={
        "algo": "ga",
        "weights": {"aggression": 0.9, "caution": 0.1, "mobility": 0.5, "stamina_conservation": 0.5}
    })
    assert res_high.status_code == 200
    reward_high = session.sandbox.gym_stats["best_reward"]

    # High aggression weight must result in higher computed rewards
    assert reward_high > reward_low
