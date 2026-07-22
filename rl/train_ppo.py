"""Stable-Baselines3 PPO training pipeline for locomotion policy learning."""
from __future__ import annotations
import argparse
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from rl.env import CreatureEnv


def train_ppo(
    total_timesteps: int = 10000,
    save_path: str = "models/ppo_hopper.zip",
    tensorboard_log: str = "logs/ppo_tb",
    checkpoint_freq: int = 5000,
    verbose: int = 1,
) -> PPO:
    """Train a PPO policy on CreatureEnv and save the model checkpoint."""
    env = CreatureEnv(max_episode_steps=500)

    # Ensure output directories exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    os.makedirs(tensorboard_log, exist_ok=True)

    checkpoint_dir = os.path.join(os.path.dirname(save_path), "checkpoints")
    os.makedirs(checkpoint_dir, exist_ok=True)

    checkpoint_callback = CheckpointCallback(
        save_freq=checkpoint_freq,
        save_path=checkpoint_dir,
        name_prefix="ppo_hopper_ckpt",
    )

    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        n_steps=512,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,
        verbose=verbose,
        tensorboard_log=tensorboard_log,
    )

    model.learn(total_timesteps=total_timesteps, callback=checkpoint_callback)
    model.save(save_path)
    env.close()

    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train PPO Walker Policy")
    parser.add_argument("--timesteps", type=int, default=10000, help="Total timesteps to train")
    parser.add_argument("--save-path", type=str, default="models/ppo_hopper.zip", help="Path to save model")
    args = parser.parse_args()

    train_ppo(total_timesteps=args.timesteps, save_path=args.save_path)
