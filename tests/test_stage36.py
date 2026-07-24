"""Unit and integration tests for Stage 36: LLM Integration Foundation."""
import os
import pytest
from web.llm_client import LLMClient


def test_missing_api_key_raises_clear_error(monkeypatch):
    """Verify missing GEMINI_API_KEY environment variable raises clear ValueError."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    client = LLMClient(api_key=None)

    with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is missing"):
        client.generate_text("Hello world")


def test_structured_generation_retry_path(monkeypatch):
    """Verify structured output parsing retries and raises clear error on failure."""
    monkeypatch.setenv("GEMINI_MOCK", "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")

    client = LLMClient()
    res = client.generate_structured("Translate task", ["target_speed", "target_torso_angle"])
    assert "target_speed" in res
    assert "target_torso_angle" in res

    with pytest.raises(ValueError, match="Structured schema validation failed"):
        client.generate_structured("FAIL_TEST task", ["key1"])


def test_gitignore_contains_env():
    """Verify .gitignore contains .env entry to prevent API key commits."""
    assert os.path.exists(".gitignore")
    with open(".gitignore", "r", encoding="utf-8") as f:
        content = f.read()
    assert ".env" in content
