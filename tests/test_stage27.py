"""Unit tests for Stage 27: Battle Analytics."""
import pytest
from combat.arena import Arena
from replay.recorder import MatchRecorder
from analytics.battle_report import generate_battle_report


def test_generate_battle_report_from_replay(tmp_path):
    """Verify generate_battle_report computes real metrics and formats summary from replay recording."""
    recorder = MatchRecorder()
    recorder.start_match("Lightweight Fighter", "Heavy Tank")

    arena = Arena(
        "robots/presets/lightweight_fighter.json",
        "robots/presets/heavy_tank.json",
        max_steps=10,
    )

    for _ in range(10):
        arena.step([0.0], [0.0])
        recorder.record_step(arena, damage_events=[])

    recorder.end_match(arena.winner, arena.win_reason)

    save_file = str(tmp_path / "replay_analytics.json")
    recorder.save(save_file)

    report = generate_battle_report(save_file)

    assert report.robot_a_name == "Lightweight Fighter"
    assert report.robot_b_name == "Heavy Tank"
    assert isinstance(report.damage_pct_a, float)
    assert isinstance(report.distance_covered_a, float)

    summary = report.summary_text()
    assert "=== BATTLE ANALYTICS REPORT ===" in summary
    assert "Robot A (Lightweight Fighter):" in summary
    assert "Distance Covered:" in summary


def test_weakness_heuristics_detection():
    """Verify weakness flags trigger when low mobility or high chassis damage thresholds are met."""
    # Stationary replay frame data
    stationary_frames = [
        {
            "step": 0,
            "robot_a": {
                "total_durability": 300.0,
                "bodies": {"torso": {"pos": [0.0, 1.0], "angle": 0.0}},
            },
            "robot_b": {
                "total_durability": 300.0,
                "bodies": {"torso": {"pos": [4.0, 1.0], "angle": 0.0}},
            },
        },
        {
            "step": 1,
            "robot_a": {
                "total_durability": 50.0,  # Dropped below 30% -> vulnerable_chassis
                "bodies": {"torso": {"pos": [0.0, 1.0], "angle": 0.0}},  # Zero movement -> low_mobility
            },
            "robot_b": {
                "total_durability": 300.0,
                "bodies": {"torso": {"pos": [4.0, 1.0], "angle": 0.0}},
            },
        },
    ]

    replay_payload = {
        "metadata": {
            "robot_a": "Robot A",
            "robot_b": "Robot B",
            "winner": "robot_b",
            "win_reason": "chassis_destruction",
        },
        "frames": stationary_frames,
    }

    report = generate_battle_report(replay_payload)

    assert "low_mobility" in report.weaknesses_a
    assert "vulnerable_chassis" in report.weaknesses_a
