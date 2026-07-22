"""Unit tests for Stage 26: Experiment Mode."""
import pytest
from sandbox.experiment import ExperimentConfig, run_experiment, run_gravity_sweep_experiment


def test_experiment_repeatability():
    """Verify running identical experiment config twice produces 100% deterministic identical metrics."""
    config = ExperimentConfig(
        experiment_name="Repeatability Check",
        robot_spec_path="robots/presets/lightweight_fighter.json",
        gravity=(0.0, -9.8),
        duration_steps=100,
    )

    report1 = run_experiment(config)
    report2 = run_experiment(config)

    assert report1.distance_traveled == pytest.approx(report2.distance_traveled)
    assert report1.max_height_reached == pytest.approx(report2.max_height_reached)
    assert report1.energy_consumed == pytest.approx(report2.energy_consumed)


def test_experiment_gravity_sweep_physical_sensitivity():
    """Verify gravity sweep produces genuinely different, physically sensible results."""
    reports = run_gravity_sweep_experiment(
        "robots/presets/lightweight_fighter.json", multipliers=[0.5, 1.0, 2.5]
    )

    assert len(reports) == 3
    # Higher gravity restricts max height reached
    height_low_g = reports[0].max_height_reached
    height_high_g = reports[2].max_height_reached

    assert height_low_g > height_high_g


def test_experiment_report_summary_text_format():
    """Verify ExperimentReport.summary_text formats output matching concept doc standard."""
    config = ExperimentConfig(
        experiment_name="High Gravity Test",
        robot_spec_path="robots/presets/lightweight_fighter.json",
        gravity=(0.0, -24.5),
        duration_steps=50,
    )

    report = run_experiment(config)
    summary = report.summary_text()

    assert "Experiment: High Gravity Test" in summary
    assert "Robot: Lightweight Fighter" in summary
    assert "Environment: Gravity = 2.5x" in summary
    assert "Result: Distance:" in summary
    assert "Energy Consumed:" in summary
