"""Unit tests for Stage 22: Combat Evolution."""
import os
import numpy as np
import pytest
from combat.combat_env import CombatEnv
from combat.train_combat_evolution import train_combat_evolution, evaluate_combat_population
from evolution.population import Population


def test_evaluate_combat_population_returns_valid_scores():
    """Verify evaluate_combat_population computes valid float fitness array for population."""
    dummy_env = CombatEnv()
    obs_dim = dummy_env.observation_space.shape[0]
    num_actions = dummy_env.action_space.shape[0]

    pop = Population(size=4, obs_dim=obs_dim, num_actions=num_actions)
    fitnesses = evaluate_combat_population(pop, num_matches_per_individual=2, max_steps=50)

    assert isinstance(fitnesses, np.ndarray)
    assert fitnesses.shape == (4,)
    assert not np.isnan(fitnesses).any()


def test_combat_evolution_pipeline_and_artifacts(tmp_path):
    """Verify combat GA training pipeline executes over multiple generations and saves artifacts."""
    model_path = str(tmp_path / "combat_ga.npy")
    plot_path = str(tmp_path / "combat_ga_curve.png")
    gif_path = str(tmp_path / "combat_ga_match.gif")

    best_genome, final_fit = train_combat_evolution(
        generations=3,
        pop_size=6,
        model_save_path=model_path,
        plot_path=plot_path,
        gif_path=gif_path,
    )

    assert os.path.exists(model_path)
    assert os.path.exists(plot_path)
    assert os.path.exists(gif_path)
    assert best_genome.ndim == 1
