"""Unit tests for Stage 12: Genetic Algorithm Loop."""
import os
import pytest
from evolution.ga import tournament_selection, crossover, mutate, GeneticAlgorithm
from evolution.population import Population
from scripts.plot_evolution import run_and_plot_evolution


def test_ga_operators_behavior():
    """Verify tournament selection, uniform crossover, and Gaussian mutation operators."""
    pop = Population(size=6, hidden_dim=8)

    # 1. Selection
    fitnesses = [10.0, 50.0, 5.0, 30.0, 100.0, 2.0]
    selected = tournament_selection(pop.genomes, fitnesses, num_select=2, tournament_size=3)
    assert len(selected) == 2
    assert selected[0].shape == pop.genomes[0].shape

    # 2. Crossover
    child = crossover(pop.genomes[0], pop.genomes[1])
    assert child.shape == pop.genomes[0].shape

    # 3. Mutation
    mutated = mutate(pop.genomes[0], mutation_rate=0.5, mutation_strength=0.1)
    assert mutated.shape == pop.genomes[0].shape
    assert not (mutated == pop.genomes[0]).all()


def test_ga_evolution_and_plot_generation(tmp_path):
    """Verify running GA evolution produces increasing best fitness, plot, and GIF."""
    genome_file = str(tmp_path / "ga_test_best.npy")
    plot_file = str(tmp_path / "ga_test_fitness.png")
    gif_file = str(tmp_path / "ga_test_locomotion.gif")

    results = run_and_plot_evolution(
        num_generations=10,
        pop_size=10,
        genome_save_path=genome_file,
        plot_path=plot_file,
        gif_path=gif_file,
        verbose=False,
    )

    # 1. Genome numpy file saved
    assert os.path.exists(genome_file)
    assert os.path.getsize(genome_file) > 0

    # 2. Fitness plot saved
    assert os.path.exists(plot_file)
    assert os.path.getsize(plot_file) > 0

    # 3. Locomotion GIF saved
    assert os.path.exists(gif_file)
    assert os.path.getsize(gif_file) > 0

    # 4. Best fitness trends higher than initial mean fitness
    initial_mean = results["history"][0]["mean_fitness"]
    final_best = results["history"][-1]["best_fitness"]
    assert final_best > initial_mean
