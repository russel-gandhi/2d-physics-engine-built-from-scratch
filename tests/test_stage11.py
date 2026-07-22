"""Unit tests for Stage 11: NN Controller & Population."""
import numpy as np
import pytest
from evolution.nn_controller import NNController
from evolution.population import Population


def test_nn_controller_forward_pass_and_bounds():
    """Verify NNController outputs valid action within [-1.0, 1.0] matching action shape."""
    obs_dim = 11
    num_actions = 2
    controller = NNController(obs_dim, num_actions, hidden_dim=16)

    random_obs = np.random.randn(obs_dim).astype(np.float32)
    action = controller.act(random_obs)

    assert isinstance(action, np.ndarray)
    assert action.shape == (num_actions,)
    assert (action >= -1.0).all() and (action <= 1.0).all()


def test_genome_roundtrip_serialization():
    """Verify get_genome -> set_genome round-trip is lossless."""
    controller = NNController(obs_dim=8, num_actions=3, hidden_dim=12)
    original_genome = controller.get_genome().copy()

    # Mutate genome
    new_genome = np.random.randn(len(original_genome)).astype(np.float32)
    controller.set_genome(new_genome)

    retrieved_genome = controller.get_genome()
    np.testing.assert_allclose(retrieved_genome, new_genome, rtol=1e-6, atol=1e-6)


def test_population_evaluation_fitness_variance():
    """Verify evaluating different random genomes produces different fitness values."""
    pop = Population(size=5, hidden_dim=16)
    fitnesses = [pop.evaluate(genome, max_steps=100) for genome in pop.genomes]

    assert len(fitnesses) == 5
    assert len(set(fitnesses)) > 1  # Not all identical
    assert all(isinstance(f, float) for f in fitnesses)
