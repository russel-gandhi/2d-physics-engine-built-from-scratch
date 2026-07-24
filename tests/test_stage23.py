"""Unit tests for Stage 23: Replay System."""
import os
import pytest
from combat.arena import Arena
from replay.recorder import MatchRecorder
from replay.player import ReplayPlayer


def test_match_recorder_saves_and_loads_replay(tmp_path):
    """Verify MatchRecorder captures match steps, serializes to JSON file, and reloads payload."""
    recorder = MatchRecorder()
    recorder.start_match("Lightweight Fighter", "Heavy Tank")

    arena = Arena(
        "robots/presets/lightweight_fighter.json",
        "robots/presets/heavy_tank.json",
        max_steps=20,
    )

    na = len(arena.robot_a.motorized_joints)
    nb = len(arena.robot_b.motorized_joints)
    for _ in range(10):
        arena.step([0.0] * na, [0.0] * nb)
        recorder.record_step(arena, damage_events=[])

    recorder.end_match(arena.winner, arena.win_reason)

    save_file = str(tmp_path / "test_match.json")
    recorder.save(save_file)

    assert os.path.exists(save_file)

    loaded_data = MatchRecorder.load(save_file)
    assert loaded_data["metadata"]["robot_a"] == "Lightweight Fighter"
    assert loaded_data["metadata"]["total_frames"] == 10
    assert len(loaded_data["frames"]) == 10


def test_replay_player_reconstructs_and_renders(tmp_path):
    """Verify ReplayPlayer loads replay payload, builds reconstructed world frames, and steps playback."""
    recorder = MatchRecorder()
    recorder.start_match("Lightweight Fighter", "Heavy Tank")

    arena = Arena(
        "robots/presets/lightweight_fighter.json",
        "robots/presets/heavy_tank.json",
        max_steps=5,
    )

    na = len(arena.robot_a.motorized_joints)
    nb = len(arena.robot_b.motorized_joints)
    for _ in range(5):
        arena.step([0.0] * na, [0.0] * nb)
        recorder.record_step(arena, damage_events=[])

    recorder.end_match(arena.winner, arena.win_reason)

    save_file = str(tmp_path / "replay_test.json")
    recorder.save(save_file)

    player = ReplayPlayer(save_file, headless=True)
    assert player.total_frames == 5

    world = player.build_world_for_frame(2)
    assert len(world.bodies) >= 3

    # Step playback in headless mode
    player.play(max_render_frames=3)
    assert player.current_frame_idx == 3
