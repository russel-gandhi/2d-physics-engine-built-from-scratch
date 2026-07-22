"""Demo runner executing best evolved Genetic Algorithm genome in Pygame renderer."""
from __future__ import annotations
import argparse
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from evolution.population import Population
from rl.env import CreatureEnv
from render.renderer import Renderer


def run_evolution_demo(
    genome_path: str = "models/ga_hopper_best.npy",
    max_steps: int = 600,
    headless: bool = True,
) -> float:
    """Load best evolved genome array and run live/headless simulation rollout."""
    if not os.path.exists(genome_path):
        raise FileNotFoundError(f"Evolved genome array not found at '{genome_path}'. Run GA evolution first.")

    print(f"Loading best evolved genome from '{genome_path}'...")
    genome = np.load(genome_path)

    pop = Population(size=1, hidden_dim=16)
    controller = pop.create_controller(genome)

    env = CreatureEnv(max_episode_steps=max_steps)
    obs, info = env.reset()
    assert env.world is not None

    renderer = Renderer(width=800, height=400, headless=headless)

    total_reward = 0.0
    step_count = 0
    done = False

    while not done and step_count < max_steps:
        action = controller.act(obs)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        step_count += 1
        done = terminated or truncated

        renderer.render(env.world)

    renderer.close()
    env.close()

    print(f"GA Evolution Demo finished: {step_count} steps, Total Reward: {total_reward:.2f}")
    return total_reward


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Evolved GA Controller Demo")
    parser.add_argument("--genome-path", type=str, default="models/ga_hopper_best.npy")
    parser.add_argument("--gui", action="store_true", help="Run with Pygame GUI window")
    args = parser.parse_args()

    run_evolution_demo(genome_path=args.genome_path, headless=not args.gui)
