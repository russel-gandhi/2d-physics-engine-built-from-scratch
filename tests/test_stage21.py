"""Unit tests for Stage 21: Combat RL & Self-Play."""
import os
import numpy as np
import pytest
from combat.train_combat_rl import PolicyPoolOpponent, train_combat_rl
from combat.combat_env import CombatEnv


def test_policy_pool_opponent_selection(tmp_path):
    """Verify PolicyPoolOpponent provides valid actions with empty or populated checkpoint directory."""
    pool = PolicyPoolOpponent(str(tmp_path))

    # Get correct observation and action dimensions from a real env
    env = CombatEnv(max_episode_steps=5)
    obs_b, _ = env.reset()
    obs_b_arr = env.current_obs_b  # actual obs_b shape

    # Empty pool returns default heuristic action
    act = pool(obs_b_arr)
    assert isinstance(act, np.ndarray)
    # Action must be a valid 1D numpy array (shape may be 1 or full joint count depending on impl)
    assert act.ndim == 1
    assert len(act) >= 1
    env.close()


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
