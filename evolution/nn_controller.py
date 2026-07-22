"""Feedforward Neural Network controller for evolutionary creature locomotion."""
from __future__ import annotations
import numpy as np


class NNController:
    """Multi-Layer Perceptron (MLP) policy for creature articulation control.

    Architecture:
        Input Layer: obs_dim neurons
        Hidden Layer: hidden_dim neurons (ReLU activation)
        Output Layer: num_actions neurons (Tanh activation -> [-1.0, 1.0])
    """

    def __init__(self, obs_dim: int, num_actions: int, hidden_dim: int = 16) -> None:
        """Initialize controller layer shapes and random weights/biases."""
        self.obs_dim = obs_dim
        self.num_actions = num_actions
        self.hidden_dim = hidden_dim

        # Calculate weight matrix sizes
        self.w1_size = obs_dim * hidden_dim
        self.b1_size = hidden_dim
        self.w2_size = hidden_dim * num_actions
        self.b2_size = num_actions

        self.total_weights = self.w1_size + self.b1_size + self.w2_size + self.b2_size

        # Initialize with Xavier/Glorot random weights
        limit1 = np.sqrt(6.0 / (obs_dim + hidden_dim))
        self.W1 = np.random.uniform(-limit1, limit1, (obs_dim, hidden_dim)).astype(np.float32)
        self.b1 = np.zeros((hidden_dim,), dtype=np.float32)

        limit2 = np.sqrt(6.0 / (hidden_dim + num_actions))
        self.W2 = np.random.uniform(-limit2, limit2, (hidden_dim, num_actions)).astype(np.float32)
        self.b2 = np.zeros((num_actions,), dtype=np.float32)

    def act(self, observation: np.ndarray) -> np.ndarray:
        """Compute feedforward pass and return continuous action vector in range [-1.0, 1.0]."""
        obs = np.asarray(observation, dtype=np.float32)
        if obs.ndim == 1:
            obs = obs.reshape(1, -1)

        # Hidden layer: ReLU(obs @ W1 + b1)
        hidden = np.maximum(0.0, obs @ self.W1 + self.b1)

        # Output layer: Tanh(hidden @ W2 + b2)
        output = np.tanh(hidden @ self.W2 + self.b2)
        return output.squeeze(axis=0)

    def get_genome(self) -> np.ndarray:
        """Flatten all weight and bias matrices into a single 1D numpy genome array."""
        return np.concatenate([
            self.W1.ravel(),
            self.b1.ravel(),
            self.W2.ravel(),
            self.b2.ravel(),
        ]).astype(np.float32)

    def set_genome(self, genome: np.ndarray) -> None:
        """Unflatten 1D genome array into weight and bias matrices."""
        g = np.asarray(genome, dtype=np.float32)
        if g.size != self.total_weights:
            raise ValueError(
                f"Genome length mismatch: expected {self.total_weights}, got {g.size}"
            )

        idx = 0
        self.W1 = g[idx : idx + self.w1_size].reshape(self.obs_dim, self.hidden_dim)
        idx += self.w1_size

        self.b1 = g[idx : idx + self.b1_size].reshape(self.hidden_dim)
        idx += self.b1_size

        self.W2 = g[idx : idx + self.w2_size].reshape(self.hidden_dim, self.num_actions)
        idx += self.w2_size

        self.b2 = g[idx : idx + self.b2_size].reshape(self.num_actions)
