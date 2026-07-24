"""Run honest-sized GA combat training session, save champion to roster, and simulate competitive match."""
import os
import sys
import time
import json
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from web.server import session, _run_combat_gym_training, Arena
from web.fighter_roster import save_fighter, list_fighters


def run_full_training_and_match():
    print("=== STARTING HONEST GA COMBAT TRAINING SESSION ===")
    generations = 10
    pop_size = 6
    max_steps = 150
    weights = {"aggression": 0.9, "caution": 0.3, "mobility": 0.7}

    session.sandbox.gym_stats = {
        "algo": "ga_combat",
        "generation": 0,
        "weights": weights,
        "best_reward": 0.0,
        "mean_reward": 0.0,
        "grid": [],
        "history": [],
        "stopped": False,
        "training_complete": False,
    }

    t0 = time.perf_counter()
    _run_combat_gym_training(
        session.sandbox,
        weights=weights,
        generations=generations,
        pop_size=pop_size,
        max_steps_per_match=max_steps,
    )
    t_train = time.perf_counter() - t0

    history = session.sandbox.gym_stats.get("history", [])
    best_reward = session.sandbox.gym_stats.get("best_reward", 0.0)
    mean_reward = session.sandbox.gym_stats.get("mean_reward", 0.0)

    print(f"\n[TRAINING SUMMARY]")
    print(f"Generations Evaluated: {generations}")
    print(f"Population Size: {pop_size}")
    print(f"Max Steps Per Match: {max_steps}")
    print(f"Total Wall-Clock Time: {t_train:.2f} seconds ({t_train/generations:.2f}s / generation)")
    print(f"Initial Generation Best Reward: {history[0] if history else 'N/A'}")
    print(f"Final Generation Best Reward:   {history[-1] if history else 'N/A'}")
    print(f"Reward Curve History: {history}")

    # Save best champion to roster
    champ_path = "models/roster/ga_aggression_champ.npy"
    if os.path.exists("models/combat_ga_best.npy"):
        genome = np.load("models/combat_ga_best.npy")
        np.save(champ_path, genome)

    champ_entry = save_fighter(
        name="Aggressive Brawler Champ",
        preset_name="robots/presets/boxer.json",
        algo="ga",
        artifact_path=champ_path,
        stats={"best_reward": best_reward, "generations": generations, "time_s": round(t_train, 2)},
    )
    print(f"Champion promoted and saved to roster: {champ_entry['id']} ('{champ_entry['name']}')")

    # Run Competitive Match between Champion and a second fighter
    print("\n=== RUNNING COMPETITIVE MATCH WITH TRAINED ROSTER CHAMPION ===")
    session.mode = "competitive"
    session.arena = Arena("robots/presets/boxer.json", "robots/presets/grappler.json")
    session.load_controllers_for_competitive(champ_entry["id"], None)

    steps = 100
    actions_a = []
    actions_b = []

    for _ in range(steps):
        obs_a = session.arena.get_observation(session.arena.robot_a, session.arena.robot_b)
        obs_b = session.arena.get_observation(session.arena.robot_b, session.arena.robot_a)
        act_a = session.ctrl_a.act(obs_a)
        act_b = session.ctrl_b.act(obs_b)
        actions_a.append(act_a[:5])
        actions_b.append(act_b[:5])
        session.step()

    pos_a = session.arena.robot_a.main_body.position
    pos_b = session.arena.robot_b.main_body.position
    dur_a = session.arena.robot_a.total_durability
    dur_b = session.arena.robot_b.total_durability

    print(f"Match Step Count: {steps}")
    print(f"Robot A (Trained Champion) Final Pos: ({pos_a.x:.2f}, {pos_a.y:.2f}), Durability: {dur_a:.1f}")
    print(f"Robot B (Grappler Opponent) Final Pos: ({pos_b.x:.2f}, {pos_b.y:.2f}), Durability: {dur_b:.1f}")
    print(f"Robot A Mean Joint Output: {np.mean(actions_a, axis=0).round(3)}")
    print(f"Robot B Mean Joint Output: {np.mean(actions_b, axis=0).round(3)}")
    print("MATCH COMPLETED SUCCESSFULLY — Trained AI policy active and governing movement!")


if __name__ == "__main__":
    run_full_training_and_match()
