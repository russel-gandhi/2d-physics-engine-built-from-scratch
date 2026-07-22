"""Train PPO locomotion policy, plot training reward curve, and record Pygame GIF animation of trained gait."""
from __future__ import annotations
import argparse
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pygame

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.results_plotter import load_results, ts2xy
from rl.env import CreatureEnv
from render.renderer import Renderer


def train_and_record_ppo(
    total_timesteps: int = 200000,
    model_save_path: str = "models/ppo_hopper_trained.zip",
    plot_path: str = "scripts/ppo_reward_curve.png",
    gif_path: str = "scripts/ppo_hopper_locomotion.gif",
    num_eval_episodes: int = 5,
    verbose: int = 1,
) -> PPO:
    """Train PPO policy, plot reward curve, and record GIF of best evaluation episode."""
    log_dir = "logs/ppo_monitor"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)

    # Wrap environment with Monitor to record episode statistics
    raw_env = CreatureEnv(max_episode_steps=500)
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
        ent_coef=0.0,
        verbose=verbose,
    )

    if os.path.exists(model_save_path) and total_timesteps == 0:
        print(f"Loading existing model from {model_save_path}...")
        model = PPO.load(model_save_path, env=monitored_env)
    else:
        print(f"Starting PPO training for {total_timesteps} timesteps...")
        model.learn(total_timesteps=total_timesteps)
        model.save(model_save_path)
        print(f"Model saved to {model_save_path}")

    # Plot Reward Curve
    try:
        x, y = ts2xy(load_results(log_dir), "timesteps")
        if len(x) > 0:
            plt.figure(figsize=(9, 5))
            plt.plot(x, y, label="Episode Reward", color="blue", alpha=0.3)

            if len(y) >= 10:
                window_size = min(20, len(y))
                y_smooth = np.convolve(y, np.ones(window_size) / window_size, mode="valid")
                x_smooth = x[window_size - 1:]
                plt.plot(x_smooth, y_smooth, label="Smoothed Reward (Moving Avg)", color="red", linewidth=2)

            plt.title("PPO Locomotion Training Reward Curve")
            plt.xlabel("Timesteps")
            plt.ylabel("Episode Return")
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()
            print(f"Reward curve plot saved to {plot_path}")

            # Report final reward statistics
            final_returns = y[-20:] if len(y) >= 20 else y
            print(f"PPO Training Completed. Final 20 episodes reward: Mean={np.mean(final_returns):.2f}, Max={np.max(final_returns):.2f}, Min={np.min(final_returns):.2f}")
    except Exception as e:
        print(f"Warning: Could not plot reward curve: {e}")

    # Evaluate multiple episodes and record the best performing one
    print(f"Evaluating {num_eval_episodes} episodes to select best rollout for GIF recording...")
    best_frames = []
    best_reward = -float("inf")
    best_steps = 0

    max_record_steps = 300  # Up to 5 seconds @ 60 FPS

    for ep in range(num_eval_episodes):
        eval_env = CreatureEnv(max_episode_steps=max_record_steps)
        obs, _ = eval_env.reset()
        assert eval_env.world is not None

        renderer = Renderer(width=800, height=400, headless=True)
        ep_frames = []
        ep_reward = 0.0
        step_count = 0
        done = False

        while not done and step_count < max_record_steps:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = eval_env.step(action)
            ep_reward += reward
            step_count += 1
            done = terminated or truncated

            renderer.render(eval_env.world)
            rgb_bytes = pygame.image.tostring(renderer.screen, "RGB")
            frame_img = Image.frombytes("RGB", (800, 400), rgb_bytes)
            ep_frames.append(frame_img)

        renderer.close()
        eval_env.close()

        print(f"  Eval Episode {ep+1}: {step_count} steps, Total Reward: {ep_reward:.2f}")
        if ep_reward > best_reward:
            best_reward = ep_reward
            best_steps = step_count
            best_frames = ep_frames

    # Check for short episode threshold warning
    if best_steps < 60:
        print(f"WARNING: Best evaluation episode lasted only {best_steps} steps (< 60 frames threshold). Policy may be falling early!")

    if best_frames:
        best_frames[0].save(
            gif_path,
            save_all=True,
            append_images=best_frames[1:],
            duration=33,  # ~30 fps gif speed
            loop=0,
        )
        print(f"Best locomotion GIF ({best_steps} frames, return {best_reward:.2f}) saved to {gif_path}")

    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train PPO Hopper and record locomotion GIF")
    parser.add_argument("--timesteps", type=int, default=200000, help="Timesteps to train")
    args = parser.parse_args()

    train_and_record_ppo(total_timesteps=args.timesteps)
