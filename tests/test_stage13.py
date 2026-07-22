"""Unit tests for Stage 13: Integration & Demo Capture."""
import os
import pytest
from scripts.demo_walker import run_ppo_demo
from scripts.demo_evolution import run_evolution_demo
from scripts.demo_comparison import run_comparison


def test_demo_walker_execution():
    """Verify demo_walker runs using saved PPO model and returns total reward."""
    model_path = "models/ppo_hopper_trained.zip"
    assert os.path.exists(model_path)

    reward = run_ppo_demo(model_path=model_path, max_steps=50, headless=True)
    assert isinstance(reward, float)


def test_demo_evolution_execution():
    """Verify demo_evolution runs using saved GA best genome and returns total reward."""
    genome_path = "models/ga_hopper_best.npy"
    assert os.path.exists(genome_path)

    reward = run_evolution_demo(genome_path=genome_path, max_steps=50, headless=True)
    assert isinstance(reward, float)


def test_demo_missing_artifacts_raise_error(tmp_path):
    """Verify loading non-existent model/genome raises explicit FileNotFoundError without silent fallback."""
    fake_model = str(tmp_path / "non_existent.zip")
    fake_genome = str(tmp_path / "non_existent.npy")

    with pytest.raises(FileNotFoundError):
        run_ppo_demo(model_path=fake_model, max_steps=10, headless=True)

    with pytest.raises(FileNotFoundError):
        run_evolution_demo(genome_path=fake_genome, max_steps=10, headless=True)


def test_demo_comparison_execution(tmp_path):
    """Verify side-by-side comparison benchmark generates comparison plot."""
    plot_file = str(tmp_path / "test_comparison_plot.png")
    summary = run_comparison(
        ppo_model_path="models/ppo_hopper_trained.zip",
        ga_genome_path="models/ga_hopper_best.npy",
        plot_path=plot_file,
        num_episodes=2,
    )

    assert os.path.exists(plot_file)
    assert summary["ppo_mean_steps"] > 0
    assert summary["ga_mean_steps"] > 0
