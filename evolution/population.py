"""Population structure and individual fitness evaluation for Evolutionary Algorithm."""
from __future__ import annotations
import numpy as np
from creatures.morphology import CreatureSpec
from rl.env import CreatureEnv
from evolution.nn_controller import NNController


class Population:
    """Manages a population of Neural Network genomes and handles fitness evaluation."""

    def __init__(
        self,
        size: int,
        creature_spec: CreatureSpec | str | None = None,
        hidden_dim: int = 16,
    ) -> None:
        """Initialize population of random individual genomes matching creature morphology."""
        self.size = size
        self.hidden_dim = hidden_dim

        # Determine dimensions from sample environment
        sample_env = CreatureEnv(spec=creature_spec)
        self.creature_spec = sample_env.creature_spec
        self.obs_dim = sample_env.observation_space.shape[0]
        self.num_actions = sample_env.action_space.shape[0]
        sample_env.close()

        # Dummy controller to get genome length
        dummy_ctrl = NNController(self.obs_dim, self.num_actions, hidden_dim)
        self.genome_length = dummy_ctrl.total_weights

        # Initialize random genomes (normal distribution std=0.5)
        self.genomes = [
            np.random.randn(self.genome_length).astype(np.float32) * 0.5
            for _ in range(size)
        ]

    def create_controller(self, genome: np.ndarray) -> NNController:
        """Instantiate NNController initialized with given genome parameters."""
        controller = NNController(self.obs_dim, self.num_actions, self.hidden_dim)
        controller.set_genome(genome)
        return controller

    def evaluate(self, genome: np.ndarray, max_steps: int = 500) -> float:
        """Evaluate an individual genome in a fresh physics environment and return total fitness."""
        env = CreatureEnv(spec=self.creature_spec, max_episode_steps=max_steps)
        controller = self.create_controller(genome)

        obs, info = env.reset()
        total_fitness = 0.0
        done = False

        while not done:
            action = controller.act(obs)
            obs, reward, terminated, truncated, info = env.step(action)
            total_fitness += reward
            done = terminated or truncated

        env.close()
        return float(total_fitness)
