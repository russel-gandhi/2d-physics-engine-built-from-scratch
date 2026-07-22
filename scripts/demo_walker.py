"""Demo runner executing trained PPO RL locomotion policy in Pygame renderer."""
from __future__ import annotations
import argparse
import os
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from stable_baselines3 import PPO
from rl.env import CreatureEnv
from render.renderer import Renderer


def run_ppo_demo(
    model_path: str = "models/ppo_hopper_trained.zip",
    max_steps: int = 600,
    headless: bool = True,
) -> float:
    """Load trained PPO checkpoint and run live/headless simulation rollout."""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"PPO checkpoint not found at '{model_path}'. Train model first.")

    print(f"Loading PPO policy from '{model_path}'...")
    model = PPO.load(model_path)

    env = CreatureEnv(max_episode_steps=max_steps)
    obs, info = env.reset()
    assert env.world is not None

    renderer = Renderer(width=800, height=400, headless=headless)

    total_reward = 0.0
    step_count = 0
    done = False

    while not done and step_count < max_steps:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        step_count += 1
        done = terminated or truncated

        renderer.render(env.world)

    renderer.close()
    env.close()

    print(f"PPO Demo finished: {step_count} steps, Total Reward: {total_reward:.2f}")
    return total_reward


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run PPO Trained Walker Demo")
    parser.add_argument("--model-path", type=str, default="models/ppo_hopper_trained.zip")
    parser.add_argument("--gui", action="store_true", help="Run with Pygame GUI window")
    args = parser.parse_args()

    run_ppo_demo(model_path=args.model_path, headless=not args.gui)
