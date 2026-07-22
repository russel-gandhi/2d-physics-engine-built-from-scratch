"""RoboForge Arena — Main Entry Point Launcher."""
from __future__ import annotations
import sys
import os


def print_menu():
    print("=" * 60)
    print("      ROBOFORGE ARENA — 2D PHYSICS ENGINE & COMBAT SIM     ")
    print("=" * 60)
    print("Select a mode to run:")
    print("  [1] Interactive Sandbox Mode (Live controls: S=spawn shape, R=spawn robot, G=gravity, T=terrain)")
    print("  [2] Replay System & Spectator Player (Play recorded matches)")
    print("  [3] PPO Locomotion Walker Demo")
    print("  [4] Evolutionary Locomotion Walker Demo")
    print("  [5] RL vs GA Locomotion Benchmark Comparison")
    print("  [6] Self-Play Combat RL Training (Generates winrate plot & match GIF)")
    print("  [7] Evolutionary Combat Tournament (Generates fitness curve & match GIF)")
    print("  [8] Run Gravity Sweep Experiment & Generate Lab Report")
    print("  [9] Physics Engine Baseline Scene Test")
    print("  [0] Exit")
    print("-" * 60)


def main():
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print_menu()
        choice = input("Enter choice (0-9): ").strip()

    if choice == "1":
        print("\nStarting Interactive Sandbox Mode (Close Pygame window to exit)...")
        from sandbox.sandbox_mode import SandboxMode
        sb = SandboxMode(headless=False)
        sb.run_interactive_loop()
    elif choice == "2":
        print("\nStarting Replay Player...")
        import subprocess
        subprocess.run([sys.executable, "-m", "replay.player"])
    elif choice == "3":
        print("\nRunning PPO Locomotion Walker Demo...")
        import subprocess
        subprocess.run([sys.executable, "-m", "scripts.demo_walker"])
    elif choice == "4":
        print("\nRunning Evolutionary Locomotion Walker Demo...")
        import subprocess
        subprocess.run([sys.executable, "-m", "scripts.demo_evolution"])
    elif choice == "5":
        print("\nRunning RL vs GA Locomotion Comparison Benchmark...")
        import subprocess
        subprocess.run([sys.executable, "-m", "scripts.demo_comparison"])
    elif choice == "6":
        print("\nStarting Self-Play Combat RL Training...")
        import subprocess
        subprocess.run([sys.executable, "-m", "combat.train_combat_rl"])
    elif choice == "7":
        print("\nStarting Evolutionary Combat Tournament...")
        import subprocess
        subprocess.run([sys.executable, "-m", "combat.train_combat_evolution"])
    elif choice == "8":
        print("\nRunning Gravity Sweep Experiment Series...\n")
        from sandbox.experiment import run_gravity_sweep_experiment
        reports = run_gravity_sweep_experiment("robots/presets/lightweight_fighter.json", multipliers=[0.5, 1.0, 2.5])
        for r in reports:
            print(r.summary_text())
            print("-" * 40)
    elif choice == "9":
        print("\nRunning Baseline Physics Engine Scene...")
        import subprocess
        subprocess.run([sys.executable, "-m", "scripts.run_scene"])
    elif choice == "0":
        print("Exiting RoboForge Arena.")
    else:
        print(f"Invalid choice: {choice}")


if __name__ == "__main__":
    main()
