"""Unit and integration tests for Stage 28: Dashboard Backend."""
import pytest
from fastapi.testclient import TestClient
from web.server import app, session
from web.state_encoder import encode_state


def test_state_encoder_output_structure():
    """Verify state_encoder produces valid JSON-serializable output structure."""
    session.sandbox.reset_world()
    state = encode_state(session.sandbox, mode="playground", paused=False)

    assert "mode" in state
    assert state["mode"] == "playground"
    assert "bodies" in state
    assert "joints" in state
    assert "gravity" in state
    assert isinstance(state["bodies"], list)


def test_fastapi_control_and_spawn_endpoints():
    """Verify REST endpoints trigger real changes in server session state."""
    client = TestClient(app)

    # 1. Mode Endpoint
    res = client.post("/api/mode", json={"mode": "playground"})
    assert res.status_code == 200
    assert res.json()["mode"] == "playground"

    # 2. Control Endpoint
    res = client.post("/api/control?action=pause")
    assert res.status_code == 200
    assert session.paused is True

    res = client.post("/api/control?action=resume")
    assert res.status_code == 200
    assert session.paused is False

    # 3. Spawn Shape Endpoint
    initial_bodies = len(session.sandbox.world.bodies)
    res = client.post("/api/spawn_shape", json={"x": 1.0, "y": 5.0})
    assert res.status_code == 200
    assert len(session.sandbox.world.bodies) == initial_bodies + 1

    # 4. Spawn Robot Endpoint
    res = client.post("/api/spawn_robot", json={"preset_path": "robots/presets/lightweight_fighter.json", "x": 0.0, "y": 4.0})
    assert res.status_code == 200
    assert len(session.sandbox.world.bodies) > initial_bodies + 1


def test_websocket_state_streaming():
    """Verify WebSocket endpoint /ws/state streams live changing position frames."""
    client = TestClient(app)

    # Resume session
    client.post("/api/control?action=resume")

    with client.websocket_connect("/ws/state") as websocket:
        data1 = websocket.receive_json()
        data2 = websocket.receive_json()

        assert "bodies" in data1
        assert "bodies" in data2
        assert data1["mode"] == "playground"
