# Stage 31 — Gym Mode UI

**Phase 8. Depends on:** Stage 29, Stage 10 (PPO training), Stage 12 (GA loop).

## Goal

Watch and control training live as a population, not a single hidden number going up — a grid of simultaneous fighters training, the best one visibly ahead, promotable into a persistent roster. Flat terrain only for now (see Phase 9 in `04_IMPLEMENTATION_PLAN.md`).

## What to build

`web/frontend/gym.js`
- Algorithm select (PPO / genetic algorithm), a start/stop control, and live-updating stat cards (total timesteps or generation count, current episode/genome reward, best reward seen).
- **Live population grid** — this is the centerpiece, matching the reference image's agent grid:
  - **GA**: each population member (genome) *is* a distinct fighter — render a small live view + running fitness for every genome being evaluated this generation, sorted by fitness, best one highlighted with a badge. This is a direct, honest visualization of what `evolution/ga.py` is already doing — no extra machinery needed, just surfacing the population that already exists.
  - **PPO**: use a vectorized environment (`gymnasium`'s `VecEnv` via `stable-baselines3`, e.g. 8-16 parallel envs) so there are genuinely multiple simultaneous rollouts to show. Be precise in the UI copy here: these are N parallel rollouts of the *same* current policy, not N independently-trained fighters — label the grid "parallel rollouts," not "agents," so it doesn't imply something PPO isn't doing. Highlight whichever rollout currently has the best running episode reward.
- A live reward/fitness chart from real streamed values, as before.
- Training runs server-side exactly as `rl/train_ppo.py` / `evolution/ga.py` already do — this stage adds control and visibility, not a new training implementation. Surface `total_timesteps` / `num_generations` as a visible, adjustable setting so short/undertrained runs aren't the default.

## Definition of Done

- [ ] GA training shows a real live grid of population members with individually different, correctly-sorted fitness values matching what `evolution/ga.py` computes directly — not a static mockup grid
- [ ] PPO training shows a real live grid of parallel rollouts with individually different running rewards (they will differ due to stochastic action sampling and different episode start conditions, even with one shared policy) — verify the displayed rewards actually vary between rollouts and aren't the same number repeated
- [ ] The "best" highlight in both modes tracks the real current leader and updates as it changes — confirm by watching it flip during a run when a different agent/rollout takes the lead
- [ ] A "promote to roster" action on the current best (see Stage 33) saves a real, usable checkpoint (PPO) or genome (GA), not just a UI label pointing at nothing
