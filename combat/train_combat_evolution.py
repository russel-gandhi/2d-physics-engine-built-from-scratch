"""Evolutionary tournament training script for Robot Combat using round-robin population matches."""
from __future__ import annotations
import argparse
import os
import random
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import pygame

from combat.combat_env import CombatEnv
from evolution.nn_controller import NNController
from evolution.population import Population
from evolution.ga import tournament_selection, crossover, mutate
from render.renderer import Renderer


def evaluate_combat_population(
    population: Population,
    num_matches_per_individual: int = 3,
    max_steps: int = 300,
    spec_a_path: str | None = None,
    spec_b_path: str | None = None,
) -> np.ndarray:
    """Evaluate population fitness via round-robin combat matches in CombatEnv."""
    pop_size = len(population.genomes)
    fitnesses = np.zeros(pop_size, dtype=np.float32)

    env = CombatEnv(
        robot_a_spec=spec_a_path,
        robot_b_spec=spec_b_path,
        max_episode_steps=max_steps,
    )

    sample_obs_a, _ = env.reset()
    sample_obs_b = env.current_obs_b

    obs_dim_a = env.observation_space.shape[0]
    num_actions_a = env.action_space.shape[0]

    obs_dim_b = len(sample_obs_b)
    num_actions_b = env.action_space_b.shape[0]

    ctrl_a = NNController(obs_dim=obs_dim_a, num_actions=num_actions_a)
    ctrl_b = NNController(obs_dim=obs_dim_b, num_actions=num_actions_b)

    for i in range(pop_size):
        # Sample opponent indices (excluding self)
        possible_opponents = [j for j in range(pop_size) if j != i]
        opponents = random.sample(
            possible_opponents, min(num_matches_per_individual, len(possible_opponents))
        )

        match_scores = []
        ctrl_a.set_genome(population.genomes[i])

        for opp_idx in opponents:
            ctrl_b.set_genome(population.genomes[opp_idx])

            obs_a, _ = env.reset()
            obs_b = env.current_obs_b

            done = False
            total_rew_a = 0.0

            while not done:
                act_a = ctrl_a.act(obs_a)
                act_b = ctrl_b.act(obs_b)

                obs_a, obs_b, rew_a, rew_b, done, info = env.step_two_agents(act_a, act_b)
                total_rew_a += rew_a

            match_scores.append(total_rew_a)

        fitnesses[i] = float(np.mean(match_scores))

    return fitnesses


def train_combat_evolution(
    generations: int = 15,
    pop_size: int = 12,
    model_save_path: str = "models/combat_ga_best.npy",
    plot_path: str = "scripts/combat_ga_fitness_curve.png",
    gif_path: str = "scripts/combat_ga_match.gif",
) -> tuple[np.ndarray, float]:
    """Run evolutionary combat training over multiple generations."""
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)

    dummy_env = CombatEnv()
    obs_dim = dummy_env.observation_space.shape[0]
    num_actions = dummy_env.action_space.shape[0]

    population = Population(size=pop_size, obs_dim=obs_dim, num_actions=num_actions)

    best_fitness_history = []
    mean_fitness_history = []

    gen0_best_genome: np.ndarray | None = None

    for gen in range(generations):
        fitnesses = evaluate_combat_population(population)
        best_idx = int(np.argmax(fitnesses))
        best_fit = float(fitnesses[best_idx])
        mean_fit = float(np.mean(fitnesses))

        best_fitness_history.append(best_fit)
        mean_fitness_history.append(mean_fit)

        if gen == 0:
            gen0_best_genome = population.genomes[best_idx].copy()

        print(f"Gen {gen:02d} | Best Combat Fitness: {best_fit:7.2f} | Mean: {mean_fit:7.2f}")

        # Selection, Crossover, Mutation & Elitism
        new_genomes = []
        # Elitism: top 2 preserved
        sorted_indices = np.argsort(fitnesses)[::-1]
        new_genomes.append(population.genomes[sorted_indices[0]].copy())
        new_genomes.append(population.genomes[sorted_indices[1]].copy())

        while len(new_genomes) < pop_size:
            parents = tournament_selection(
                population.genomes, fitnesses, num_select=2, tournament_size=3
            )
            child = crossover(parents[0], parents[1])
            child = mutate(child, mutation_rate=0.05, mutation_strength=0.1)
            new_genomes.append(child)

        population.genomes = new_genomes

    # Final evaluation of best genome
    final_fitnesses = evaluate_combat_population(population)
    best_final_idx = int(np.argmax(final_fitnesses))
    best_final_genome = population.genomes[best_final_idx].copy()

    np.save(model_save_path, best_final_genome)
    print(f"Saved best combat evolved genome to {model_save_path}")

    # Plot fitness curve
    plt.figure(figsize=(9, 5))
    plt.plot(best_fitness_history, label="Best Combat Fitness", color="green", marker="o")
    plt.plot(mean_fitness_history, label="Mean Combat Fitness", color="blue", linestyle="--")
    plt.title("Evolutionary Combat Fitness Across Generations")
    plt.xlabel("Generation")
    plt.ylabel("Combat Fitness")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()
    print(f"Evolution combat fitness curve saved to {plot_path}")

    # Head-to-Head Verification: Gen Final Best vs Gen 0 Best
    if gen0_best_genome is not None:
        print("Running verification match: Gen Final Best vs Gen 0 Best...")
        env = CombatEnv(max_episode_steps=300)
        ctrl_final = NNController(obs_dim=obs_dim, num_actions=num_actions)
        ctrl_gen0 = NNController(obs_dim=obs_dim, num_actions=num_actions)
        ctrl_final.set_genome(best_final_genome)
        ctrl_gen0.set_genome(gen0_best_genome)

        wins_final = 0
        for _ in range(5):
            obs_a, _ = env.reset()
            obs_b = env.current_obs_b
            done = False
            while not done:
                act_a = ctrl_final.act(obs_a)
                act_b = ctrl_gen0.act(obs_b)
                obs_a, obs_b, _, _, done, info = env.step_two_agents(act_a, act_b)
            if info.get("winner") == "robot_a":
                wins_final += 1

        print(f"Head-to-Head Win Rate for Evolved Gen Final vs Gen 0: {wins_final}/5 matches ({wins_final*20}%)")

    # Record match GIF
    renderer = Renderer(width=800, height=400, headless=True)
    env = CombatEnv(max_episode_steps=300)
    ctrl_a = NNController(obs_dim=obs_dim, num_actions=num_actions)
    ctrl_b = NNController(obs_dim=obs_dim, num_actions=num_actions)
    ctrl_a.set_genome(best_final_genome)
    ctrl_b.set_genome(gen0_best_genome if gen0_best_genome is not None else best_final_genome)

    obs_a, _ = env.reset()
    obs_b = env.current_obs_b

    frames = []
    done = False
    step_count = 0

    while not done and step_count < 300:
        act_a = ctrl_a.act(obs_a)
        act_b = ctrl_b.act(obs_b)
        obs_a, obs_b, _, _, done, info = env.step_two_agents(act_a, act_b)
        step_count += 1

        renderer.render(env.arena.world)
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
        print(f"Combat GA match GIF saved to {gif_path}")

    return best_final_genome, best_fitness_history[-1]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Evolutionary Combat Population")
    parser.add_argument("--generations", type=int, default=10, help="Generations")
    parser.add_argument("--pop-size", type=int, default=10, help="Population size")
    args = parser.parse_args()

    train_combat_evolution(generations=args.generations, pop_size=args.pop_size)
