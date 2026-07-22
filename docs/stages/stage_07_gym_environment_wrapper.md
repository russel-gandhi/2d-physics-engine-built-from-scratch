# Stage 07 — Gymnasium Environment Wrapper

**Day 4, first half. Depends on:** Stage 06.

## Goal

Make the creature+world controllable through the standard RL interface so `stable-baselines3` (or any RL library, or a hand-written policy) can drive it without knowing anything about the physics internals.

## What to build

`rl/env.py`
- `CreatureEnv(gymnasium.Env)`:
  - `__init__`: builds a `World`, ground, and one creature from a `CreatureSpec`
  - `observation_space`: `Box` covering joint angles, joint angular velocities, torso angle/angular velocity, torso height, and (if time allows) binary ground-contact flags per foot — document the exact vector layout in a comment, since stage 11's `NNController` needs to match it
  - `action_space`: `Box(-1, 1, shape=(num_motorized_joints,))`
  - `reset() -> (observation, info)`: rebuild the world/creature to its initial pose, return the initial observation
  - `step(action) -> (observation, reward, terminated, truncated, info)`:
    - scale `action` from `[-1, 1]` to real torque range, set each joint's `motor_torque`
    - call `world.step(fixed_dt)` (possibly multiple physics sub-steps per RL step, e.g. 4, so the RL decision frequency is lower than the physics update frequency — standard practice, improves stability)
    - compute `reward` (start simple: forward velocity of the torso, minus a small control-effort penalty — see glossary)
    - `terminated = True` if the creature has fallen (e.g. torso angle or height past a threshold)
    - `truncated = True` if a max episode step count is hit

## Definition of Done

- [ ] `env = CreatureEnv(); obs, info = env.reset()` — `obs` shape matches `observation_space`, no NaNs
- [ ] Stepping with `action = env.action_space.sample()` in a loop runs without crashing for at least a few hundred steps in a row across multiple resets
- [ ] Reward is a real computed float derived from actual torso velocity each step (print/log a handful of steps to confirm it isn't constant/hardcoded)
- [ ] `terminated` actually triggers on a deliberately bad episode (e.g. apply a torque that tips the creature over immediately) — confirm episodes end instead of running forever with the creature lying on the ground
