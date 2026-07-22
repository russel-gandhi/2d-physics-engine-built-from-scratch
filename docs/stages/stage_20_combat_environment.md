# Stage 20 — Combat Environment

**Phase 4. Depends on:** Stage 19.

## Goal

Wrap the local arena in the standard RL interface, extended for two agents, so both RL training (stage 21) and evolutionary evaluation (stage 22) can drive it the same way.

## What to build

`combat/combat_env.py`
- `CombatEnv(gymnasium.Env)`, built on `combat/arena.py` the way `rl/env.py`'s `CreatureEnv` was built on a single-robot `World`.
- `observation_space`: everything `CreatureEnv` already exposes for "self" (joint angles/velocities, torso state) plus opponent-relative state — opponent position/velocity relative to self, opponent's current total durability fraction, self's current total durability fraction, self's energy level if using the energy system from stage 15.
- `action_space`: same shape as `CreatureEnv`'s, per robot.
- Support both single-agent use (one side is a fixed/scripted opponent — needed to bootstrap training in stage 21 before self-play is viable) and two-policy use (both sides driven by a controller — needed for self-play and for stage 22's round-robin evaluation).

## Definition of Done

- [ ] `CombatEnv` against a fixed scripted opponent runs full episodes without crashing, reward/observations are real computed values (spot-check a handful of steps)
- [ ] `CombatEnv` with both sides driven by (even untrained, random) `NNController`/policy instances runs correctly — confirms the two-agent path works structurally before stage 21/22 add real learning
- [ ] Episode termination correctly reflects `arena.py`'s win conditions from stage 19 (chassis destroyed / timeout), not a separate duplicated condition that could drift out of sync
