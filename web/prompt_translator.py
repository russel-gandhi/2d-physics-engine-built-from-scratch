"""Natural language training prompt translator converting user intent to reward weights."""
from __future__ import annotations
from typing import Any
from web.llm_client import LLMClient


DEFAULT_WEIGHTS = {
    "aggression": 0.5,
    "caution": 0.5,
    "mobility": 0.5,
    "stamina_conservation": 0.5,
}


def translate_training_prompt(prompt: str, client: LLMClient | None = None) -> dict[str, Any]:
    """Translate natural language training strategy prompt into numerical reward weights."""
    if not prompt or not prompt.strip():
        return {"is_default": True, "weights": DEFAULT_WEIGHTS, "message": "Using default balanced weights."}

    client = client or LLMClient()
    schema_keys = ["aggression", "caution", "mobility", "stamina_conservation"]

    instruction = (
        f"You are a combat robot training coach. Analyze this training goal prompt: '{prompt}'.\n"
        f"Output normalized numerical weights between 0.0 and 1.0 for: {schema_keys}."
    )

    try:
        raw_weights = client.generate_structured(instruction, schema_keys)
        weights = {}
        for k in schema_keys:
            val = float(raw_weights.get(k, 0.5))
            weights[k] = max(0.0, min(1.0, val))

        return {"is_default": False, "weights": weights, "prompt": prompt}
    except Exception as e:
        return {
            "is_default": True,
            "weights": DEFAULT_WEIGHTS,
            "message": f"Could not parse prompt strategy ({e}). Using default balanced weights.",
        }
