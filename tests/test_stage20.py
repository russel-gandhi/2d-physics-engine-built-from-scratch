"""Unit tests for Stage 20: Combat Environment."""
import numpy as np
import pytest
from combat.combat_env import CombatEnv
from evolution.nn_controller import NNController


def test_combat_env_reset_and_observation_shapes():
    """Verify CombatEnv resets cleanly and returns correct observation and action spaces."""
    env = CombatEnv(max_episode_steps=100)
    obs, info = env.reset()

    assert isinstance(obs, np.ndarray)
    assert not np.isnan(obs).any()
    assert env.observation_space.contains(obs)
    assert env.action_space.shape == (1,)  # Single revolute joint on preset


def test_combat_env_single_agent_against_scripted_opponent():
    """Verify CombatEnv runs full episode with agent A against a fixed scripted opponent policy."""
    # Scripted policy swinging back and forth
    def scripted_policy(obs_b: np.ndarray) -> np.ndarray:
        return np.array([1.0], dtype=np.float32)

    env = CombatEnv(opponent_policy=scripted_policy, max_episode_steps=50)
    obs, info = env.reset()

    total_reward = 0.0
    for _ in range(50):
        action_a = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action_a)
        assert isinstance(reward, float)
        assert not np.isnan(obs).any()
        total_reward += reward
        if terminated or truncated:
            break

    assert info["step"] > 0


def test_combat_env_two_agents_steering():
    """Verify CombatEnv with both sides driven by NNControllers executes cleanly."""
    env = CombatEnv(max_episode_steps=50)
    obs_a, _ = env.reset()

    # Create two random NNControllers
    ctrl_a = NNController(obs_dim=env.observation_space.shape[0], num_actions=1, hidden_dim=16)
    ctrl_b = NNController(obs_dim=env.observation_space.shape[0], num_actions=1, hidden_dim=16)

    obs_b = env.current_obs_b

    for _ in range(50):
        act_a = ctrl_a.act(obs_a)
        act_b = ctrl_b.act(obs_b)

        obs_a, obs_b, rew_a, rew_b, done, info = env.step_two_agents(act_a, act_b)
        assert not np.isnan(obs_a).any()
        assert not np.isnan(obs_b).any()
        if done:
            break

    assert info["winner"] in ("robot_a", "robot_b", "draw")


def test_combat_env_termination_matches_arena():
    """Verify CombatEnv termination directly reflects Arena win conditions."""
    env = CombatEnv(max_episode_steps=5)
    obs, info = env.reset()

    done = False
    for _ in range(5):
        action_a = np.array([0.0], dtype=np.float32)
        obs, reward, terminated, truncated, info = env.step(action_a)
        done = terminated or truncated

    assert done is True
    assert info["winner"] is not None
    assert info["reason"] in ("chassis_destruction", "out_of_bounds", "timeout", "simultaneous_destruction")
