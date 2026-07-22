"""Unit tests for Stage 10: Locomotion Reward Shaping & Real Training Run."""
import os
import pytest
from scripts.train_and_record_ppo import train_and_record_ppo


def test_train_and_record_ppo_pipeline(tmp_path):
    """Verify running PPO training generates trained model, reward plot, and locomotion GIF animation."""
    model_file = str(tmp_path / "ppo_test_trained.zip")
    plot_file = str(tmp_path / "ppo_test_reward_curve.png")
    gif_file = str(tmp_path / "ppo_test_locomotion.gif")

    model = train_and_record_ppo(
        total_timesteps=4096,
        model_save_path=model_file,
        plot_path=plot_file,
        gif_path=gif_file,
        verbose=0,
    )

    # 1. Model saved
    assert os.path.exists(model_file)
    assert os.path.getsize(model_file) > 0

    # 2. Reward plot file created
    assert os.path.exists(plot_file)
    assert os.path.getsize(plot_file) > 0

    # 3. Locomotion GIF file created
    assert os.path.exists(gif_file)
    assert os.path.getsize(gif_file) > 0
