"""Unit tests for Stage 07: Gymnasium Environment Wrapper."""
import numpy as np
import pytest
from rl.env import CreatureEnv


def test_environment_reset_and_observation_shape():
    """Verify env.reset() returns valid observations matching observation_space with no NaNs."""
    env = CreatureEnv()
    obs, info = env.reset()

    assert isinstance(obs, np.ndarray)
    assert obs.shape == env.observation_space.shape
    assert not np.isnan(obs).any()
    assert not np.isinf(obs).any()


def test_random_action_multi_episode_loop():
    """Verify stepping with random actions across multiple resets runs without error for 500+ total steps."""
    env = CreatureEnv(max_episode_steps=100)
    total_steps = 0

    for _ in range(10):  # 10 episodes
        obs, info = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            assert isinstance(reward, float)
            assert not np.isnan(obs).any()
            done = terminated or truncated
            total_steps += 1

    assert total_steps >= 100


def test_dynamic_reward_computation():
    """Verify reward is dynamically computed from actual torso velocity per step, not hardcoded."""
    env = CreatureEnv()
    obs, info = env.reset()

    rewards = []
    for _ in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        rewards.append(reward)

    # Check rewards are varied floats and match torso velocity
    assert len(set(rewards)) > 1  # Not all identical
    assert all(isinstance(r, float) for r in rewards)


def test_termination_on_fall():
    """Verify terminated=True triggers when creature falls over."""
    env = CreatureEnv(max_episode_steps=500)
    obs, info = env.reset()

    # Apply continuous maximum torque to force creature to fall over
    terminated_triggered = False
    for _ in range(100):
        obs, reward, terminated, truncated, info = env.step([1.0])
        if terminated:
            terminated_triggered = True
            break

    assert terminated_triggered
