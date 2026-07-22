"""Run Genetic Algorithm evolution, plot fitness curve, save best genome, and record locomotion GIF."""
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

from evolution.population import Population
from evolution.ga import GeneticAlgorithm
from rl.env import CreatureEnv
from render.renderer import Renderer


def run_and_plot_evolution(
    num_generations: int = 25,
    pop_size: int = 25,
    genome_save_path: str = "models/ga_hopper_best.npy",
    plot_path: str = "scripts/ga_fitness_curve.png",
    gif_path: str = "scripts/ga_hopper_locomotion.gif",
    verbose: bool = True,
) -> dict:
    """Run GA evolution, plot best/mean fitness, save best genome, and export locomotion animation."""
    os.makedirs(os.path.dirname(genome_save_path), exist_ok=True)
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)

    print(f"Initializing GA population (size={pop_size})...")
    pop = Population(size=pop_size, hidden_dim=16)
    ga = GeneticAlgorithm(
        population=pop,
        elitism=2,
        mutation_rate=0.08,
        mutation_strength=0.15,
        tournament_size=3,
    )

    if os.path.exists(genome_save_path) and num_generations == 0:
        print(f"Loading existing genome from {genome_save_path}...")
        best_genome = np.load(genome_save_path)
        history = []
        best_gen_stats = {"best_fitness": 500.0, "best_genome": best_genome}
    else:
        print(f"Evolving for {num_generations} generations...")
        history = ga.run_evolution(num_generations=num_generations, max_steps_per_eval=400, verbose=verbose)

        # Save best overall genome
        best_gen_stats = max(history, key=lambda h: h["best_fitness"])
        best_genome = best_gen_stats["best_genome"]
        np.save(genome_save_path, best_genome)
        print(f"Saved best genome (fitness={best_gen_stats['best_fitness']:.2f}) to {genome_save_path}")

    # Plot Fitness Curve
    generations = [h["generation"] for h in history]
    bests = [h["best_fitness"] for h in history]
    means = [h["mean_fitness"] for h in history]

    plt.figure(figsize=(9, 5))
    plt.plot(generations, bests, "b-o", linewidth=2, label="Best Fitness")
    plt.plot(generations, means, "r--s", linewidth=1.5, alpha=0.7, label="Mean Fitness")
    plt.title("Genetic Algorithm Locomotion Evolution")
    plt.xlabel("Generation")
    plt.ylabel("Fitness (Reward Return)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"Evolution fitness plot saved to {plot_path}")

    # Record GIF of Evolved Policy
    print("Recording GA locomotion GIF animation...")
    eval_env = CreatureEnv(max_episode_steps=300)
    controller = pop.create_controller(best_genome)
    obs, info = eval_env.reset()
    assert eval_env.world is not None

    renderer = Renderer(width=800, height=400, headless=True)
    frames = []

    done = False
    step_count = 0
    max_record_steps = 180  # 3 seconds @ 60 FPS

    while not done and step_count < max_record_steps:
        action = controller.act(obs)
        obs, reward, terminated, truncated, info = eval_env.step(action)
        step_count += 1
        done = terminated or truncated

        # Render frame offscreen
        renderer.render(eval_env.world)
        frame_surface = renderer.screen

        # Convert Pygame surface to PIL Image
        rgb_bytes = pygame.image.tostring(frame_surface, "RGB")
        frame_img = Image.frombytes("RGB", (800, 400), rgb_bytes)
        frames.append(frame_img)

    renderer.close()
    eval_env.close()

    if frames:
        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=33,  # ~30 fps gif speed
            loop=0,
        )
        print(f"GA Locomotion GIF saved to {gif_path}")

    return {
        "history": history,
        "best_fitness": float(best_gen_stats["best_fitness"]),
        "genome_path": genome_save_path,
        "plot_path": plot_path,
        "gif_path": gif_path,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Genetic Algorithm locomotion evolution")
    parser.add_argument("--generations", type=int, default=25, help="Number of generations to evolve")
    parser.add_argument("--pop-size", type=int, default=25, help="Population size")
    args = parser.parse_args()

    run_and_plot_evolution(num_generations=args.generations, pop_size=args.pop_size)
