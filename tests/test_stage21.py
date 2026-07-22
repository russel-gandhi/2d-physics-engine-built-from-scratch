"""Unit tests for Stage 21: Combat RL & Self-Play."""
import os
import numpy as np
import pytest
from combat.train_combat_rl import PolicyPoolOpponent, train_combat_rl


def test_policy_pool_opponent_selection(tmp_path):
    """Verify PolicyPoolOpponent provides valid actions with empty or populated checkpoint directory."""
    pool = PolicyPoolOpponent(str(tmp_path))
    obs_b = np.zeros(15, dtype=np.float32)

    # Empty pool returns default heuristic action
    act = pool(obs_b)
    assert isinstance(act, np.ndarray)
    assert act.shape == (1,)
    assert act[0] == 1.0


def test_combat_rl_training_pipeline_and_artifacts(tmp_path):
    """Verify self-play combat RL training pipeline runs and saves model, reward plot, and match GIF."""
    model_path = str(tmp_path / "combat_ppo.zip")
    plot_path = str(tmp_path / "combat_reward.png")
    gif_path = str(tmp_path / "combat_match.gif")

    model = train_combat_rl(
        total_timesteps=4000,
        model_save_path=model_path,
        plot_path=plot_path,
        gif_path=gif_path,
        verbose=0,
    )

    assert os.path.exists(model_path)
    assert os.path.exists(plot_path)
    assert os.path.exists(gif_path)
    assert os.path.getsize(model_path) > 0
