"""Gymnasium environment wrapping 1v1 Local Arena for single-agent and multi-agent combat training."""
from __future__ import annotations
import os
from typing import Any, Callable
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from combat.arena import Arena
from robots.robot_spec import RobotSpec


class CombatEnv(gym.Env):
    """Gymnasium environment wrapping 1v1 Combat Arena.
    
    Supports single-agent training (agent A vs fixed opponent policy) and
    two-policy stepping (agent A vs agent B) for self-play RL & GA evaluation.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(
        self,
        robot_a_spec: RobotSpec | str | None = None,
        robot_b_spec: RobotSpec | str | None = None,
        opponent_policy: Callable[[np.ndarray], np.ndarray] | None = None,
        max_episode_steps: int = 1000,
        frame_skip: int = 4,
    ) -> None:
        """Initialize CombatEnv with robot specs and optional opponent policy callback."""
        super().__init__()

        if robot_a_spec is None:
            robot_a_spec = os.path.join("robots", "presets", "lightweight_fighter.json")
        if robot_b_spec is None:
            robot_b_spec = os.path.join("robots", "presets", "heavy_tank.json")

        if isinstance(robot_a_spec, str):
            self.spec_a = RobotSpec.from_json(robot_a_spec)
        else:
            self.spec_a = robot_a_spec

        if isinstance(robot_b_spec, str):
            self.spec_b = RobotSpec.from_json(robot_b_spec)
        else:
            self.spec_b = robot_b_spec

        self.opponent_policy = opponent_policy
        self.max_episode_steps = max_episode_steps
        self.frame_skip = frame_skip

        # Action space for Robot A
        num_actions_a = sum(1 for j in self.spec_a.joints if j.joint_type == "revolute")
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(num_actions_a,), dtype=np.float32
        )

        # Action space for Robot B
        num_actions_b = sum(1 for j in self.spec_b.joints if j.joint_type == "revolute")
        self.action_space_b = spaces.Box(
            low=-1.0, high=1.0, shape=(num_actions_b,), dtype=np.float32
        )

        # Observation space: 11 relative combat features + 2 * num_joints
        obs_dim_a = 11 + 2 * len(self.spec_a.joints)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim_a,), dtype=np.float32
        )

        self.arena: Arena | None = None
        self.current_obs_a: np.ndarray | None = None
        self.current_obs_b: np.ndarray | None = None

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Reset combat environment and 1v1 arena."""
        super().reset(seed=seed)

        self.arena = Arena(
            robot_a_spec=self.spec_a,
            robot_b_spec=self.spec_b,
            max_steps=self.max_episode_steps,
            frame_skip=self.frame_skip,
        )

        self.current_obs_a = self.arena.get_observation(self.arena.robot_a, self.arena.robot_b)
        self.current_obs_b = self.arena.get_observation(self.arena.robot_b, self.arena.robot_a)

        return self.current_obs_a, {}

    def step(
        self, action: np.ndarray | list[float]
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """Single-agent RL step: agent A action provided, opponent B driven by opponent_policy."""
        assert self.arena is not None and self.current_obs_b is not None

        if self.opponent_policy is not None:
            action_b = self.opponent_policy(self.current_obs_b)
        else:
            action_b = self.action_space_b.sample()

        obs_a, obs_b, rew_a, rew_b, done, info = self.arena.step(action, action_b)
        self.current_obs_a = obs_a
        self.current_obs_b = obs_b

        truncated = bool(self.arena.current_step >= self.max_episode_steps)
        terminated = done and not truncated

        return obs_a, float(rew_a), terminated, truncated, info

    def step_two_agents(
        self, action_a: np.ndarray | list[float], action_b: np.ndarray | list[float]
    ) -> tuple[np.ndarray, np.ndarray, float, float, bool, dict[str, Any]]:
        """Two-agent simultaneous step: returns obs_a, obs_b, rew_a, rew_b, done, info."""
        assert self.arena is not None

        obs_a, obs_b, rew_a, rew_b, done, info = self.arena.step(action_a, action_b)
        self.current_obs_a = obs_a
        self.current_obs_b = obs_b

        return obs_a, obs_b, float(rew_a), float(rew_b), done, info
