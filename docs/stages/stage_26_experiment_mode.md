# Stage 26 — Experiment Mode

**Phase 6. Depends on:** Stage 25.

## Goal

Structured, repeatable experiments with a real report — matching the concept doc's example format exactly.

## What to build

`sandbox/experiment.py`
- `run_experiment(config: ExperimentConfig) -> ExperimentReport`: `config` specifies a robot preset and environment parameters (e.g. `gravity_multiplier`), runs a real simulation for a fixed duration or until some end condition, and returns a report with real computed values — e.g. distance traveled, energy used (if the energy system from stage 15 is wired up), time survived.
- Report format should match the concept doc's example style:
  ```
  Experiment: High Gravity Test
  Robot: SpiderBot
  Environment: Gravity = 2.5x
  Result: Distance: 20m, Energy Usage: 65%
  ```
  with the actual numbers coming from the actual run, not placeholders.
- A small set of preset experiments (e.g. a gravity sweep, a terrain-type sweep) that can be run and compared.

## Definition of Done

- [ ] Running the same experiment config twice with the same robot preset produces consistent results (small variation is fine if there's any randomness in the controller; wildly different results each time suggests a bug, e.g. state leaking between runs)
- [ ] Running the same experiment with two different `gravity_multiplier` values produces genuinely different, physically sensible results (higher gravity → shorter distance / different energy usage) — computed, not assumed
- [ ] Report values trace back to real logged simulation data, not estimated/interpolated numbers
