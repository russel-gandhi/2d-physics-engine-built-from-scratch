"""Self-Play Reinforcement Learning (PPO) training script for Robot Combat."""
from __future__ import annotations
import argparse
import glob
import os
import random
import sys
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pygame

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy

from combat.combat_env import CombatEnv
from render.renderer import Renderer


class PolicyPoolOpponent:
    """Opponent policy callback sampling from saved self-play checkpoint pool."""

    def __init__(self, checkpoint_dir: str) -> None:
        self.checkpoint_dir = checkpoint_dir
        self.current_model: PPO | None = None
        self.reload_opponent()

    def reload_opponent(self, expected_obs_dim: int | None = None) -> None:
        """Sample random checkpoint from pool or use heuristic if pool empty."""
        checkpoints = glob.glob(os.path.join(self.checkpoint_dir, "*.zip"))
        if checkpoints:
            chosen = random.choice(checkpoints)
            try:
                model = PPO.load(chosen)
                # Validate obs shape matches current env — skip stale checkpoints
                if expected_obs_dim is not None:
                    loaded_obs_dim = model.observation_space.shape[0]
                    if loaded_obs_dim != expected_obs_dim:
                        self.current_model = None
                        return
                self.current_model = model
                return
            except Exception:
                pass
        self.current_model = None

    def __call__(self, obs_b: np.ndarray) -> np.ndarray:
        """Predict action for opponent B."""
        if self.current_model is not None:
            action, _ = self.current_model.predict(obs_b, deterministic=True)
            return action
        # Heuristic default: swing all joints forward
        n = max(1, len(obs_b) // 4)  # rough estimate of num actions
        return np.ones(n, dtype=np.float32)


def train_combat_rl(
    total_timesteps: int = 100000,
    model_save_path: str = "models/combat_ppo_policy.zip",
    plot_path: str = "scripts/combat_rl_winrate.png",
    gif_path: str = "scripts/combat_rl_match.gif",
    verbose: int = 1,
) -> PPO:
    """Train Combat PPO agent using self-play opponent sampling and plot progress."""
    checkpoint_dir = "models/checkpoints_combat"
    log_dir = "logs/combat_ppo_monitor"

    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)

    pool_opponent = PolicyPoolOpponent(checkpoint_dir)
    raw_env = CombatEnv(opponent_policy=pool_opponent, max_episode_steps=500)
    monitored_env = Monitor(raw_env, log_dir)

    model = PPO(
        policy="MlpPolicy",
        env=monitored_env,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=verbose,
    )

    print(f"Starting Self-Play Combat PPO training for {total_timesteps} timesteps...")
    steps_per_iter = 20000
    trained_steps = 0

    while trained_steps < total_timesteps:
        chunk = min(steps_per_iter, total_timesteps - trained_steps)
        model.learn(total_timesteps=chunk, reset_num_timesteps=False)
    if os.path.exists(model_save_path) and total_timesteps == 0:
        print(f"Loading existing combat model from {model_save_path}...")
        model = PPO.load(model_save_path, env=monitored_env)
    else:
        print(f"Starting Self-Play Combat PPO training for {total_timesteps} timesteps...")
        steps_per_iter = 20000
        trained_steps = 0

        while trained_steps < total_timesteps:
            chunk = min(steps_per_iter, total_timesteps - trained_steps)
            model.learn(total_timesteps=chunk, reset_num_timesteps=False)
            trained_steps += chunk

            # Save checkpoint to self-play pool
            ckpt_path = os.path.join(checkpoint_dir, f"combat_ppo_{trained_steps}.zip")
            model.save(ckpt_path)
            pool_opponent.reload_opponent(expected_obs_dim=raw_env.observation_space.shape[0])
            print(f"  Completed {trained_steps}/{total_timesteps} timesteps. Checkpoint saved to pool.")

        model.save(model_save_path)
        print(f"Final Combat PPO model saved to {model_save_path}")

    # Plot Reward Curve
    try:
        x, y = ts2xy(load_results(log_dir), "timesteps")
        if len(x) > 0:
            plt.figure(figsize=(9, 5))
            plt.plot(x, y, label="Combat Reward", color="purple", alpha=0.3)
            if len(y) >= 10:
                window_size = min(20, len(y))
                y_smooth = np.convolve(y, np.ones(window_size) / window_size, mode="valid")
                x_smooth = x[window_size - 1:]
                plt.plot(x_smooth, y_smooth, label="Smoothed Reward (Moving Avg)", color="darkred", linewidth=2)

            plt.title("Self-Play Combat RL Training Reward Curve")
            plt.xlabel("Timesteps")
            plt.ylabel("Episode Combat Return")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()
            print(f"Combat RL reward curve saved to {plot_path}")
    except Exception as e:
        print(f"Warning: Could not plot combat reward curve: {e}")

    # Record GIF match rollout
    print("Recording combat match GIF animation...")
    eval_env = CombatEnv(max_episode_steps=300)
    obs_a, _ = eval_env.reset()
    obs_b = eval_env.current_obs_b

    renderer = Renderer(width=800, height=400, headless=True)
    frames = []

    done = False
    step_count = 0

    while not done and step_count < 300:
        action_a, _ = model.predict(obs_a, deterministic=True)
        # Opponent B driven by heuristic / pool policy
        action_b = pool_opponent(obs_b) if pool_opponent.current_model is not None else np.array([1.0], dtype=np.float32)

        obs_a, obs_b, rew_a, rew_b, done, info = eval_env.step_two_agents(action_a, action_b)
        step_count += 1

        renderer.render(eval_env.arena.world)
        rgb_bytes = pygame.image.tostring(renderer.screen, "RGB")
        frame_img = Image.frombytes("RGB", (800, 400), rgb_bytes)
        frames.append(frame_img)

    renderer.close()

    if frames:
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=33,
            loop=0,
        )
        print(f"Combat match GIF saved to {gif_path}")

    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Self-Play Combat RL Policy")
    parser.add_argument("--timesteps", type=int, default=50000, help="Total timesteps to train")
    args = parser.parse_args()

    train_combat_rl(total_timesteps=args.timesteps)
