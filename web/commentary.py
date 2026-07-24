"""Live match commentary generator synthesizing physics telemetry into real-time sports commentary."""
from __future__ import annotations
import os
from typing import Any
from web.llm_client import LLMClient


def generate_match_commentary(telemetry: dict[str, Any], client: LLMClient | None = None) -> str:
    """Generate a short 1-2 sentence sports commentary caption from match telemetry."""
    if os.environ.get("GEMINI_MOCK") == "1":
        return "Red Corner lands a crushing blow to Blue Corner's torso armor!"

    client = client or LLMClient()

    hp_a = telemetry.get("hp_a", 100.0)
    hp_b = telemetry.get("hp_b", 100.0)
    distance = telemetry.get("distance", 5.0)
    recent_events = telemetry.get("recent_events", [])

    prompt = (
        "You are an exciting live sports commentator for RoboForge Arena (robot combat league).\n"
        f"Match State: Distance between fighters: {distance:.1f}m. "
        f"Robot A HP: {hp_a:.1f}, Robot B HP: {hp_b:.1f}. "
        f"Recent hits: {recent_events}.\n"
        "Provide a 1-2 sentence energetic live commentary line. Keep it short, punchy, and grounded in physics."
    )

    try:
        caption = client.generate_text(prompt, max_tokens=80)
        return caption if caption else "Both fighters maneuver for spatial position in the arena!"
    except Exception:
        return "Commentary unavailable"
