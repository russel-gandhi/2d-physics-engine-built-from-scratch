"""Unit and integration tests for Stage 35: UI Integration Polish & Anti-Hardcoding Audit."""
import os
import re
import pytest
from fastapi.testclient import TestClient
from web.server import app, session


def test_mode_switch_teardown_server_side():
    """Verify switching modes mid-training cleanly stops active Gym training server-side."""
    client = TestClient(app)

    # 1. Start Gym Mode training
    res_start = client.post("/api/gym/start", json={"algo": "ga", "generations": 100})
    assert res_start.status_code == 200
    assert session.mode == "gym"
    assert session.sandbox.gym_stats.get("stopped") is not True

    # 2. Switch Mode to Competitive mid-training
    res_mode = client.post("/api/mode", json={"mode": "competitive"})
    assert res_mode.status_code == 200
    assert session.mode == "competitive"

    # 3. Verify Gym training was torn down and stopped
    assert session.sandbox.gym_stats.get("stopped") is True
    assert session.paused is True


def test_ui_layer_anti_hardcoding_audit():
    """Audit web/ frontend & backend files to enforce zero fake/canned default data or swallowed WebSocket errors."""
    web_files = []
    for root, _, files in os.walk("web"):
        for file in files:
            if file.endswith((".py", ".js", ".html", ".css")):
                web_files.append(os.path.join(root, file))

    assert len(web_files) > 0

    for path in web_files:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for unhandled silent catch blocks in frontend JS
        if path.endswith(".js"):
            assert "catch (err) {}" not in content
            assert "catch (e) {}" not in content

        # Check for hardcoded stub strings in backend Python
        if path.endswith(".py"):
            assert "pass  # stub" not in content
            assert "TODO" not in content
            assert "FIXME" not in content
