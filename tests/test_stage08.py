"""Unit tests for Stage 08: Environment Sanity Check."""
import os
import pytest
from scripts.sanity_check_env import run_sanity_check


def test_environment_sanity_check_execution(tmp_path):
    """Run sanity check runner and verify returns, plot creation, termination triggering, and lack of NaNs."""
    plot_file = str(tmp_path / "sanity_check_rewards.png")
    results = run_sanity_check(num_episodes=30, plot_path=plot_file, verbose=False)

    # 1. Plot file created
    assert os.path.exists(plot_file)
    assert os.path.getsize(plot_file) > 0

    # 2. No NaN or Inf in observations or rewards
    assert not results["nan_inf_found"]

    # 3. Terminated triggered on at least some fraction of random episodes
    assert results["terminated_count"] > 0

    # 4. Standard deviation of return is non-zero (non-constant reward distribution)
    assert results["std_return"] > 0.01

    # 5. Random policy return differs from zero action baseline return
    assert abs(results["mean_return"] - results["zero_action_mean_return"]) > 0.001
