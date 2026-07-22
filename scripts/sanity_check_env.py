"""Environment sanity check running random and zero-action policies to audit rewards, observations, and termination rules."""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import matplotlib.pyplot as plt
import numpy as np
from rl.env import CreatureEnv


def run_sanity_check(
    num_episodes: int = 50,
    plot_path: str = "scripts/sanity_check_rewards.png",
    verbose: bool = True,
) -> dict:
    """Run environment sanity check across multiple random and zero-action episodes."""
    env = CreatureEnv(max_episode_steps=500)

    random_returns = []
    random_lengths = []
    terminated_count = 0
    nan_inf_found = False

    # 1. Evaluate Random Policy
    for ep in range(num_episodes):
        obs, info = env.reset()
        ep_reward = 0.0
        ep_len = 0
        done = False

        while not done:
            if np.isnan(obs).any() or np.isinf(obs).any():
                nan_inf_found = True

            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)

            if np.isnan(reward) or np.isinf(reward):
                nan_inf_found = True

            ep_reward += reward
            ep_len += 1
            done = terminated or truncated

            if terminated:
                terminated_count += 1

        random_returns.append(ep_reward)
        random_lengths.append(ep_len)

    # 2. Evaluate Fixed Zero Action Policy (Motors Off)
    zero_returns = []
    zero_lengths = []
    for _ in range(5):
        obs, info = env.reset()
        ep_reward = 0.0
        ep_len = 0
        done = False
        while not done:
            obs, reward, terminated, truncated, info = env.step([0.0] * env.action_space.shape[0])
            ep_reward += reward
            ep_len += 1
            done = terminated or truncated
        zero_returns.append(ep_reward)
        zero_lengths.append(ep_len)

    if verbose:
        print(f"Sanity Check Completed across {num_episodes} Random Episodes:")
        print(f"  Mean Return: {np.mean(random_returns):.2f} ± {np.std(random_returns):.2f}")
        print(f"  Mean Length: {np.mean(random_lengths):.1f} steps")
        print(f"  Terminated Episodes (Fell): {terminated_count}/{num_episodes}")
        print(f"  Zero-Action Mean Return: {np.mean(zero_returns):.2f}")
        print(f"  NaN/Inf Found: {nan_inf_found}")

    # 3. Plot Return Distribution
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(random_returns, "b-o", alpha=0.7, label="Random Policy")
    plt.axhline(y=np.mean(zero_returns), color="r", linestyle="--", label="Zero Action Mean")
    plt.title("Reward per Episode (Random Policy)")
    plt.xlabel("Episode")
    plt.ylabel("Total Return")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.hist(random_lengths, bins=15, color="green", alpha=0.7, edgecolor="black")
    plt.title("Episode Length Distribution")
    plt.xlabel("Episode Length (Steps)")
    plt.ylabel("Count")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    results = {
        "num_episodes": num_episodes,
        "mean_return": float(np.mean(random_returns)),
        "std_return": float(np.std(random_returns)),
        "mean_length": float(np.mean(random_lengths)),
        "terminated_count": terminated_count,
        "nan_inf_found": nan_inf_found,
        "zero_action_mean_return": float(np.mean(zero_returns)),
        "plot_path": plot_path,
    }

    env.close()
    return results


if __name__ == "__main__":
    run_sanity_check(num_episodes=50, verbose=True)
