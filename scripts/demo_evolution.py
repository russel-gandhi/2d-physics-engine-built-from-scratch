"""Demo runner executing best evolved Genetic Algorithm genome in Pygame renderer."""
from __future__ import annotations
import argparse
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
import numpy as np
from evolution.population import Population
from rl.env import CreatureEnv
from render.renderer import Renderer


def run_evolution_demo(
    genome_path: str = "models/ga_hopper_best.npy",
    max_steps: int = 600,
    headless: bool = True,
    loop: bool = False,
) -> float:
    """Load best evolved genome array and run live/headless simulation rollout."""
    if not os.path.exists(genome_path):
        raise FileNotFoundError(f"Evolved genome array not found at '{genome_path}'. Run GA evolution first.")

    print(f"Loading best evolved genome from '{genome_path}'...")
    genome = np.load(genome_path)

    pop = Population(size=1, hidden_dim=16)
    controller = pop.create_controller(genome)

    renderer = Renderer(width=800, height=400, headless=headless)
    clock = pygame.time.Clock() if not headless else None

    running = True
    total_reward = 0.0

    while running:
        env = CreatureEnv(max_episode_steps=max_steps)
        obs, info = env.reset()
        assert env.world is not None

        step_count = 0
        ep_reward = 0.0
        done = False

        while not done and step_count < max_steps:
            if not headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        done = True

            action = controller.act(obs)
            obs, reward, terminated, truncated, info = env.step(action)
            ep_reward += reward
            step_count += 1
            done = terminated or truncated

            renderer.render(env.world)

            if clock is not None:
                clock.tick(60)  # Maintain 60 FPS in GUI mode

        total_reward = ep_reward
        env.close()

        print(f"GA Evolution Demo finished episode: {step_count} steps, Total Reward: {total_reward:.2f}")

        if not loop or not running:
            break

    renderer.close()
    return total_reward


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Evolved GA Controller Demo")
    parser.add_argument("--genome-path", type=str, default="models/ga_hopper_best.npy")
    parser.add_argument("--gui", action="store_true", help="Run with Pygame GUI window")
    parser.add_argument("--loop", action="store_true", help="Loop playback continuously")
    args = parser.parse_args()

    # Default to GUI mode if user runs script directly
    headless_mode = not args.gui if args.gui else False
    run_evolution_demo(genome_path=args.genome_path, headless=headless_mode, loop=args.loop)
