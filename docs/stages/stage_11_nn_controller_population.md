# Stage 11 — NN Controller & Population

**Day 6, first half. Depends on:** Stage 06 (creature format).

## Goal

Build the "brain" and the population machinery for the evolutionary half of the project — no learning yet, just the plumbing.

## What to build

`evolution/nn_controller.py`
- `NNController`: a small MLP with a hand-rolled forward pass — one hidden layer is enough (e.g. `observation_size -> 16 -> num_motorized_joints`), `tanh` activation on the output so it lands in `[-1, 1]` matching the action space from stage 07. `numpy` or `torch` both work — if using `torch`, you still don't need autograd here (weights are set directly from the genome, not learned via backprop), so a plain forward pass under `torch.no_grad()` is enough.
- `act(observation: np.ndarray) -> np.ndarray` — forward pass only (no backprop needed — weights only change via the GA's mutation/crossover, not gradients).
- `get_genome() -> np.ndarray` / `set_genome(genome: np.ndarray) -> None` — flatten/unflatten all weights+biases to/from a single 1D array (see glossary: this array *is* the genome).

`evolution/population.py`
- `Population(size: int, creature_spec: CreatureSpec)`: holds a list of genomes (random-initialized).
- `evaluate(genome: np.ndarray) -> float`: build a fresh `World` + creature (reuse `build_creature` from stage 06) and a fresh evaluation loop (can reuse `CreatureEnv` directly, or drive the `World` more directly if simpler — either is fine as long as it's a genuinely independent simulation per genome), run an episode with the `NNController` loaded from `genome` driving the creature, return total distance traveled (or another fitness definition — keep it consistent with stage 12).

## Definition of Done

- [ ] `NNController` with a random genome, run against a random observation, produces a valid action within `[-1, 1]` of the right shape
- [ ] `get_genome()` → `set_genome()` round-trip is lossless (set then get returns the same array)
- [ ] `Population.evaluate` on 5-10 random genomes returns different fitness values (confirms genome differences actually change simulated behavior — if every genome scores identically, something's wired wrong, e.g. the genome isn't actually being applied before the episode runs)
