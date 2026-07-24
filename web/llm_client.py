"""Shared Gemini LLM client module for structured prompts and commentary generation."""
from __future__ import annotations
import json
import os
import urllib.request
import urllib.error
from typing import Any


def load_env() -> None:
    """Load environment variables from .env file if python-dotenv or simple reader is available."""
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip().strip("'\"")


load_env()


class LLMClient:
    """Client for invoking Gemini API for structured JSON extraction and commentary generation."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def _require_api_key(self) -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY environment variable is missing. Set GEMINI_API_KEY in .env file."
            )
        return self.api_key

    def generate_text(self, prompt: str, max_tokens: int = 150) -> str:
        """Call Gemini REST API to generate free text output."""
        key = self._require_api_key()

        # If mock mode is enabled for testing
        if os.environ.get("GEMINI_MOCK") == "1":
            return f"Mock response for prompt: {prompt[:30]}..."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                candidates = res_data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return str(parts[0].get("text", "")).strip()
                return ""
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Gemini API HTTP Error {e.code}: {e.reason}") from e
        except Exception as e:
            raise RuntimeError(f"Gemini API request failed: {e}") from e

    def generate_structured(self, prompt: str, schema_keys: list[str]) -> dict[str, Any]:
        """Call Gemini API and parse JSON output matching expected schema keys."""
        full_prompt = f"{prompt}\nReturn ONLY a valid JSON object with keys: {schema_keys}. Do not include markdown code block syntax."

        # Support Mock mode in unit tests
        if os.environ.get("GEMINI_MOCK") == "1":
            if "FAIL_TEST" in prompt:
                raise ValueError("Structured schema validation failed after retry: missing keys")
            return {k: 1.0 if k in ("target_speed", "target_torso_angle") else 0 for k in schema_keys}

        attempts = 0
        last_err = None

        while attempts < 2:
            attempts += 1
            try:
                raw_text = self.generate_text(full_prompt, max_tokens=256)
                # Clean Markdown backticks if present
                clean_text = raw_text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_text)

                if isinstance(data, dict):
                    # Validate all schema keys exist
                    missing = [k for k in schema_keys if k not in data]
                    if not missing:
                        return data
                    full_prompt += f"\nCRITICAL: Your previous output missed keys: {missing}. Return valid JSON now."
                else:
                    full_prompt += "\nCRITICAL: Output must be a JSON object dictionary, not a list or scalar."
            except Exception as e:
                last_err = e
                full_prompt += "\nCRITICAL: Invalid JSON output. Fix formatting and return clean JSON."

        raise ValueError(f"Structured schema validation failed after 2 attempts: {last_err}")
