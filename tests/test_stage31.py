"""Unit and integration tests for Stage 31: Gym Mode UI."""
import os
import time
from fastapi.testclient import TestClient
from web.server import app, session


def test_gym_training_start_and_population_grid():
    """Verify starting Gym training initializes population grid stats and best badge highlighting."""
    client = TestClient(app)

    # 1. Start GA Combat Training
    res_ga = client.post("/api/gym/start", json={"algo": "ga", "generations": 1})
    assert res_ga.status_code == 200

    assert "gym_stats" in dir(session.sandbox)
    # algo is now "ga_combat" since it runs real CombatEnv
    assert session.sandbox.gym_stats["algo"] == "ga_combat"

    grid = session.sandbox.gym_stats["grid"]
    assert len(grid) == 8  # Real GA population size is 8

    # All initial rewards start at 0.0 (real training hasn't finished yet)
    assert all(isinstance(g["reward"], (int, float)) for g in grid)
    assert all(not g["is_best"] for g in grid)  # none highlighted until gen 1 completes

    # 2. Start again (resets training state)
    res_ga2 = client.post("/api/gym/start", json={"algo": "ppo", "timesteps": 20000, "generations": 1})
    assert res_ga2.status_code == 200
    assert session.sandbox.gym_stats["algo"] == "ga_combat"  # always ga_combat (real training)
    assert len(session.sandbox.gym_stats["grid"]) == 8


def test_gym_promote_to_roster():
    """Verify promote to roster saves a real file under models/roster/."""
    client = TestClient(app)

    res = client.post("/api/gym/promote", json={"name": "Test Champion"})
    assert res.status_code == 200

    saved_path = res.json()["saved_path"]
    assert os.path.exists(saved_path)
    assert "test_champion.json" in saved_path
