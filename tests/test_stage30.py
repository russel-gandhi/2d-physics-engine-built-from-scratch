"""Unit and integration tests for Stage 30: Playground Mode UI."""
from fastapi.testclient import TestClient
from web.server import app, session


def test_playground_spawn_shapes_and_robots():
    """Verify Playground control endpoints mutate live server-side simulation world state."""
    client = TestClient(app)

    # 1. Reset world
    client.post("/api/control?action=reset")
    initial_count = len(session.sandbox.world.bodies)

    # 2. Spawn Shape
    res = client.post("/api/spawn_shape", json={"x": 0.0, "y": 5.0})
    assert res.status_code == 200
    assert len(session.sandbox.world.bodies) == initial_count + 1

    # 3. Spawn Robot Presets
    res_robot_a = client.post("/api/spawn_robot", json={"preset_path": "robots/presets/lightweight_fighter.json", "x": -1.0, "y": 4.0})
    assert res_robot_a.status_code == 200

    res_robot_b = client.post("/api/spawn_robot", json={"preset_path": "robots/presets/heavy_tank.json", "x": 1.0, "y": 4.0})
    assert res_robot_b.status_code == 200

    assert len(session.sandbox.world.bodies) > initial_count + 1


def test_playground_gravity_mutation_and_reset():
    """Verify gravity slider endpoint mutates live world gravity and reset clears non-terrain bodies."""
    client = TestClient(app)

    # Mutate Gravity
    res = client.post("/api/gravity", json={"gx": 0.0, "gy": -15.0})
    assert res.status_code == 200
    assert session.sandbox.world.gravity.y == -15.0

    # Reset World
    res_reset = client.post("/api/control?action=reset")
    assert res_reset.status_code == 200
    # World reset leaves only terrain (1 static ground body)
    assert len(session.sandbox.world.bodies) == 1
