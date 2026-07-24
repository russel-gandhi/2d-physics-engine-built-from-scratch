"""Unit and integration tests for Stage 33: Fighter Roster & Selection."""
import os
import pytest
from fastapi.testclient import TestClient
from web.server import app
from web.fighter_roster import save_fighter, list_fighters, delete_fighter, ROSTER_FILE


def test_roster_save_list_delete_persistence():
    """Verify roster CRUD operations, file persistence across restarts, and artifact protection on delete."""
    # Reset Roster File for Test
    if os.path.exists(ROSTER_FILE):
        os.remove(ROSTER_FILE)

    # 1. Save Fighter Entry
    entry = save_fighter(
        name="Champion Striker",
        preset_name="robots/presets/boxer.json",
        algo="ga",
        artifact_path="models/ga_hopper_best.npy",
        stats={"best_reward": 450.0, "generations": 20},
    )

    assert entry["name"] == "Champion Striker"
    assert entry["stats"]["best_reward"] == 450.0

    # 2. Verify Roster Persistence (Simulating Server Restart by re-reading)
    fighters = list_fighters()
    assert len(fighters) == 1
    assert fighters[0]["id"] == entry["id"]

    # 3. Delete Roster Entry (Verify Artifact is NOT deleted)
    artifact_existed_before = os.path.exists("models/ga_hopper_best.npy")
    success = delete_fighter(entry["id"], delete_artifact=False)
    assert success is True
    assert len(list_fighters()) == 0

    if artifact_existed_before:
        assert os.path.exists("models/ga_hopper_best.npy")


def test_roster_fastapi_endpoints():
    """Verify REST endpoints for roster listing, saving, and deletion."""
    client = TestClient(app)

    # 1. Save via REST API
    res = client.post("/api/roster/save", json={
        "name": "Rest Fighter",
        "preset_name": "robots/presets/grappler.json",
        "algo": "ppo",
        "artifact_path": "models/ppo_hopper_trained.zip",
        "stats": {"best_reward": 320.0}
    })
    assert res.status_code == 200
    fighter_id = res.json()["fighter"]["id"]

    # 2. Get Roster via REST API
    res_list = client.get("/api/roster")
    assert res_list.status_code == 200
    assert len(res_list.json()["fighters"]) >= 1

    # 3. Delete via REST API
    res_del = client.delete(f"/api/roster/{fighter_id}")
    assert res_del.status_code == 200
    assert res_del.json()["deleted"] == fighter_id
