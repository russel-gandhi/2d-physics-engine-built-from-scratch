"""Unit tests for Stage 09: PPO Integration."""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import pytest
from stable_baselines3 import PPO
from rl.env import CreatureEnv
from rl.train_ppo import train_ppo


def test_ppo_training_pipeline_and_model_saving(tmp_path):
    """Verify running PPO training loop completes, saves model file, and checkpoint exists."""
    save_file = str(tmp_path / "ppo_test_model.zip")
    tb_dir = str(tmp_path / "tb_logs")

    # Run short 1024 timestep training
    trained_model = train_ppo(
        total_timesteps=1024,
        save_path=save_file,
        tensorboard_log=tb_dir,
        checkpoint_freq=500,
        verbose=0,
    )

    # 1. Verify model file was written to disk
    assert os.path.exists(save_file)
    assert os.path.getsize(save_file) > 0


def test_ppo_model_loading_and_inference(tmp_path):
    """Verify saved PPO model can be reloaded and drives environment actions."""
    save_file = str(tmp_path / "ppo_test_model.zip")
    tb_dir = str(tmp_path / "tb_logs")

    train_ppo(
        total_timesteps=1024,
        save_path=save_file,
        tensorboard_log=tb_dir,
        verbose=0,
    )

    # Load model from disk
    loaded_model = PPO.load(save_file)
    env = CreatureEnv(max_episode_steps=100)

    obs, info = env.reset()
    ep_reward = 0.0
    steps = 0
    done = False

    while not done:
        action, _states = loaded_model.predict(obs, deterministic=True)
        assert action.shape == env.action_space.shape
        assert (action >= -1.0).all() and (action <= 1.0).all()

        obs, reward, terminated, truncated, info = env.step(action)
        ep_reward += reward
        steps += 1
        done = terminated or truncated

    assert steps > 0
    env.close()
