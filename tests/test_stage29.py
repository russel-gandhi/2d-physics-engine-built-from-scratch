"""Unit and integration tests for Stage 29: Frontend Shell & Renderer."""
import os
from fastapi.testclient import TestClient
from web.server import app


def test_frontend_static_files_served():
    """Verify index.html and frontend assets are static-mounted and served by FastAPI."""
    client = TestClient(app)

    res = client.get("/")
    assert res.status_code == 200
    assert "ROBOFORGE ARENA" in res.text
    assert "<canvas" in res.text

    res_js = client.get("/renderer.js")
    assert res_js.status_code == 200
    assert "CanvasRenderer" in res_js.text

    res_app = client.get("/app.js")
    assert res_app.status_code == 200
    assert "connectWebSocket" in res_app.text


def test_mode_switching_nav_endpoint():
    """Verify switching modes via API updates server session state."""
    client = TestClient(app)

    for mode in ["playground", "gym", "competitive"]:
        res = client.post("/api/mode", json={"mode": mode})
        assert res.status_code == 200
        assert res.json()["mode"] == mode
