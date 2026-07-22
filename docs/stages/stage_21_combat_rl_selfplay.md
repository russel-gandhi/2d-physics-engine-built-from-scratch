# Stage 21 — Combat RL & Self-Play

**Phase 4. Depends on:** Stage 20.

## Goal

Train a robot to fight — the RL half of "Intelligent Combat Systems," running entirely locally.

## What to build

- Start simpler than full self-play: train a PPO policy in `CombatEnv` against a **fixed scripted or heuristic opponent** first (e.g. an opponent that always advances and swings) — this is a smaller, more debuggable problem than self-play from scratch, and reuses the exact same `rl/train_ppo.py` pattern from stage 09/10.
- Once that works and shows real learning (reward/win-rate improving), extend to **self-play**: maintain a small pool of saved policy checkpoints (start with just the current policy vs. its own most recent checkpoint), sample an opponent from the pool each training episode so the policy doesn't overfit to one static opponent (see glossary).
- Reward shaping for combat: something like `damage_dealt - damage_taken + small_survival_bonus`, tuned based on what actually happens in training (same iterative approach as stage 10) — watch for exploits (e.g. running away scoring better than fighting) and adjust if they show up.

## Definition of Done

- [ ] Fixed-opponent training run shows a real upward trend in win rate / reward against that specific opponent (logged, not asserted)
- [ ] Self-play run (even a short one) shows the policy improving against a sampled-from-pool opponent, not just against whichever single opponent it started with
- [ ] A recorded clip of a trained policy fighting shows genuine combat behavior (approaching, attempting to land hits, reacting to damage) — imperfect is fine, faked is not
