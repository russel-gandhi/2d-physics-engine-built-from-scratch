"""Persistent fighter roster manager storing trained PPO/GA fighters and stats."""
from __future__ import annotations
import json
import os
import uuid
from typing import Any


ROSTER_FILE = "models/roster/roster.json"


def _load_roster_data() -> list[dict[str, Any]]:
    os.makedirs(os.path.dirname(ROSTER_FILE), exist_ok=True)
    if not os.path.exists(ROSTER_FILE):
        return []
    try:
        with open(ROSTER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_roster_data(data: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(ROSTER_FILE), exist_ok=True)
    with open(ROSTER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_fighter(
    name: str,
    preset_name: str,
    algo: str,
    artifact_path: str,
    stats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Save a trained fighter entry to persistent roster file."""
    roster = _load_roster_data()
    fighter_id = str(uuid.uuid4())[:8]

    entry = {
        "id": fighter_id,
        "name": name,
        "preset_name": preset_name,
        "algo": algo,
        "artifact_path": artifact_path,
        "stats": stats or {"best_reward": 0.0, "trained_amount": 0},
    }

    roster.append(entry)
    _save_roster_data(roster)
    return entry


def list_fighters() -> list[dict[str, Any]]:
    """List all saved fighters from persistent roster."""
    return _load_roster_data()


def get_fighter(fighter_id: str) -> dict[str, Any] | None:
    """Get a single fighter entry by ID."""
    roster = _load_roster_data()
    for f in roster:
        if f.get("id") == fighter_id or f.get("name") == fighter_id:
            return f
    return None


def delete_fighter(fighter_id: str, delete_artifact: bool = False) -> bool:
    """Delete a fighter entry from roster file."""
    roster = _load_roster_data()
    target_idx = None

    for idx, f in enumerate(roster):
        if f.get("id") == fighter_id or f.get("name") == fighter_id:
            target_idx = idx
            break

    if target_idx is None:
        return False

    entry = roster.pop(target_idx)
    _save_roster_data(roster)

    if delete_artifact and "artifact_path" in entry:
        artifact_path = entry["artifact_path"]
        if os.path.exists(artifact_path):
            try:
                os.remove(artifact_path)
            except OSError:
                pass

    return True
