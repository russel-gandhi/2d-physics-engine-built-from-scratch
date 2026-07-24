"""Unit and integration tests for Stage 31: Gym Mode UI."""
import os
from fastapi.testclient import TestClient
from web.server import app, session


def test_gym_training_start_and_population_grid():
    """Verify starting Gym training initializes population grid stats and best badge highlighting."""
    client = TestClient(app)

    # 1. Start GA Training
    res_ga = client.post("/api/gym/start", json={"algo": "ga", "generations": 10})
    assert res_ga.status_code == 200
    assert "gym_stats" in dir(session.sandbox)
    assert session.sandbox.gym_stats["algo"] == "ga"

    grid = session.sandbox.gym_stats["grid"]
    assert len(grid) == 12
    # Verify rewards vary between population members
    rewards = [g["reward"] for g in grid]
    assert len(set(rewards)) > 1

    # Verify best item highlight
    best_item = [g for g in grid if g["is_best"]][0]
    assert best_item["reward"] == max(rewards)

    # 2. Start PPO Training
    res_ppo = client.post("/api/gym/start", json={"algo": "ppo", "timesteps": 20000})
    assert res_ppo.status_code == 200
    assert session.sandbox.gym_stats["algo"] == "ppo"
    assert len(session.sandbox.gym_stats["grid"]) == 8


def test_gym_promote_to_roster():
    """Verify promote to roster saves a real file under models/roster/."""
    client = TestClient(app)

    res = client.post("/api/gym/promote", json={"name": "Test Champion"})
    assert res.status_code == 200

    saved_path = res.json()["saved_path"]
    assert os.path.exists(saved_path)
    assert "test_champion.json" in saved_path
