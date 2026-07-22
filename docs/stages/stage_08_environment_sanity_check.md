# Stage 08 — Environment Sanity Check

**Day 4, second half. Depends on:** Stage 07.

## Goal

Catch environment bugs *before* spending day 5's time budget on RL training that silently learns nothing because of a broken reward or observation.

## What to build

`scripts/sanity_check_env.py`
- Run several hundred/thousand steps with a **random** policy (`env.action_space.sample()`), logging: reward per step (should vary, not be constant or always identical), episode lengths (should vary — if every single episode is exactly 1 step, or always exactly hits `truncated` at max length with `terminated` never firing, something is likely wrong), and observation ranges (should stay within `observation_space` bounds, no NaN/inf).
- Also run a **fixed, deliberately-bad** action (e.g. all zeros — motors off) and confirm reward/behavior differs sensibly from random actions (a completely still creature should behave differently than a randomly-flailing one).
- Plot reward-per-episode across ~50 random-policy episodes with `matplotlib` — it won't show learning (there's no learning yet), but it should show a real, noisy, non-constant distribution.

## Definition of Done

- [ ] Sanity check script runs and produces the plot described above, saved to disk
- [ ] `terminated` fires on at least some fraction of random-policy episodes (confirms the fall-detection condition is reachable, not miscalibrated to never/always trigger)
- [ ] No NaN/inf ever appears in observations or rewards across the whole sanity run — if it does, this is a stage-07 bug to fix now, before stage 09, not something to patch around later with clipping that hides the underlying issue
