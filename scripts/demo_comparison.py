"""Side-by-side comparison runner evaluating PPO Reinforcement Learning vs Genetic Algorithm Evolution."""
from __future__ import annotations
import argparse
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import PPO

from evolution.population import Population
from rl.env import CreatureEnv


def run_comparison(
    ppo_model_path: str = "models/ppo_hopper_trained.zip",
    ga_genome_path: str = "models/ga_hopper_best.npy",
    plot_path: str = "scripts/rl_vs_ga_comparison.png",
    num_episodes: int = 10,
) -> dict:
    """Evaluate and compare PPO policy vs GA controller across multiple episodes."""
    if not os.path.exists(ppo_model_path):
        raise FileNotFoundError(f"PPO model not found at {ppo_model_path}")
    if not os.path.exists(ga_genome_path):
        raise FileNotFoundError(f"GA genome not found at {ga_genome_path}")

    print("Evaluating PPO RL Policy...")
    ppo_model = PPO.load(ppo_model_path)
    ppo_returns = []
    ppo_steps = []

    for _ in range(num_episodes):
        env = CreatureEnv(max_episode_steps=500)
        obs, _ = env.reset()
        ep_ret = 0.0
        steps = 0
        done = False
        while not done:
            action, _ = ppo_model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(action)
            ep_ret += reward
            steps += 1
            done = terminated or truncated
        ppo_returns.append(ep_ret)
        ppo_steps.append(steps)
        env.close()

    print("Evaluating Evolved GA Controller...")
    genome = np.load(ga_genome_path)
    pop = Population(size=1, hidden_dim=16)
    ga_controller = pop.create_controller(genome)
    ga_returns = []
    ga_steps = []

    for _ in range(num_episodes):
        env = CreatureEnv(max_episode_steps=500)
        obs, _ = env.reset()
        ep_ret = 0.0
        steps = 0
        done = False
        while not done:
            action = ga_controller.act(obs)
            obs, reward, terminated, truncated, _ = env.step(action)
            ep_ret += reward
            steps += 1
            done = terminated or truncated
        ga_returns.append(ep_ret)
        ga_steps.append(steps)
        env.close()

    # Plot Comparison Bar Chart
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    categories = ["PPO (RL)", "GA (Evolution)"]
    means = [np.mean(ppo_returns), np.mean(ga_returns)]
    stds = [np.std(ppo_returns), np.std(ga_returns)]

    axes[0].bar(categories, means, yerr=stds, capsize=8, color=["#1f77b4", "#ff7f0e"], alpha=0.85)
    axes[0].set_title("Average Return Comparison")
    axes[0].set_ylabel("Episode Return")
    axes[0].grid(True, alpha=0.3)

    step_means = [np.mean(ppo_steps), np.mean(ga_steps)]
    step_stds = [np.std(ppo_steps), np.std(ga_steps)]
    axes[1].bar(categories, step_means, yerr=step_stds, capsize=8, color=["#2ca02c", "#d62728"], alpha=0.85)
    axes[1].set_title("Average Episode Duration")
    axes[1].set_ylabel("Steps Before Termination")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"Comparison plot saved to {plot_path}")

    summary = {
        "ppo_mean_return": float(np.mean(ppo_returns)),
        "ppo_mean_steps": float(np.mean(ppo_steps)),
        "ga_mean_return": float(np.mean(ga_returns)),
        "ga_mean_steps": float(np.mean(ga_steps)),
        "plot_path": plot_path,
    }

    print("--- RL vs GA Locomotion Benchmark ---")
    print(f"PPO (RL)   Mean Return: {summary['ppo_mean_return']:.2f} | Mean Steps: {summary['ppo_mean_steps']:.1f}")
    print(f"GA (Evol)  Mean Return: {summary['ga_mean_return']:.2f} | Mean Steps: {summary['ga_mean_steps']:.1f}")

    return summary


if __name__ == "__main__":
    run_comparison()
