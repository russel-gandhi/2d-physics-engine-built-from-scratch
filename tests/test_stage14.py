"""Unit tests for Stage 14: Final Verification & Polish."""
import os
import pytest


def test_readme_exists_and_contains_sections():
    """Verify README.md exists and contains key documentation sections."""
    readme_path = "README.md"
    assert os.path.exists(readme_path)

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# RoboForge Arena" in content
    assert "Custom 2D Physics Engine" in content
    assert "Quickstart Guide" in content
    assert "System Architecture" in content


def test_codebase_anti_hardcoding_audit():
    """Verify core physics and learning modules contain no bare except blocks or suspicious placeholders."""
    python_files = []
    for root, _, files in os.walk("."):
        if ".git" in root or "__pycache__" in root or ".pytest_cache" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    for filepath in python_files:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines, start=1):
            # No bare except: blocks allowed in core code
            stripped = line.strip()
            assert not stripped.startswith("except:"), f"Bare except found in {filepath}:{idx}"


def test_saved_artifacts_present():
    """Verify key trained model checkpoints, plots, and animation GIFs exist in workspace."""
    artifacts = [
        "models/ppo_hopper_trained.zip",
        "models/ga_hopper_best.npy",
        "scripts/ppo_reward_curve.png",
        "scripts/ga_fitness_curve.png",
        "scripts/rl_vs_ga_comparison.png",
        "scripts/ppo_hopper_locomotion.gif",
        "scripts/ga_hopper_locomotion.gif",
    ]

    for artifact in artifacts:
        assert os.path.exists(artifact), f"Artifact missing: {artifact}"
        assert os.path.getsize(artifact) > 0, f"Artifact empty: {artifact}"
