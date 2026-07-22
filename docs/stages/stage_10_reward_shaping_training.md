# Stage 10 — Reward Shaping & Real Training Run

**Day 5, second half. Depends on:** Stage 09.

## Goal

Get an actual, visible "the creature learned to move" result — the centerpiece result of the RL half of the project.

## What to build

- Iterate on the reward function from stage 07 based on what stage 09's short run showed. Common fixes if the creature isn't learning anything useful:
  - Reward too sparse → add a small per-step shaping term (e.g. forward velocity) instead of only rewarding at episode end
  - Creature learns a "cheat" (e.g. falling forward repeatedly for one-time distance credit) → penalize falling / reward staying upright, or end the episode with zero/negative reward on fall
  - Torque too cheap → add a control-effort penalty term so it doesn't thrash uselessly
- Run a real training session with a meaningfully larger `total_timesteps` than stage 09's smoke test (budget this against whatever time you have left in the day — a few hundred thousand to a low millions of timesteps is a reasonable range for a small environment like this on CPU, but let actual wall-clock time on your machine decide, don't assume a number).
- Record: the reward curve over training (from the real tensorboard/logged data), and a short video/gif of the trained policy running in the environment (use the renderer from stage 05, driven by `model.predict` instead of a random/manual action).

## Definition of Done

- [ ] Reward curve trends upward over the course of training (some noise is expected and fine — RL is noisy; a flat or declining curve means something needs more iteration, not that it should be presented as-is)
- [ ] Recorded video/gif shows the creature actually attempting locomotion (even an imperfect hop/shuffle counts — it does not need to look like a natural gait) — this must be a real screen/frame capture of the live rendered policy, not staged
- [ ] Both the reward curve and the video are saved to disk for use in stage 13/14 and for the resume/portfolio writeup
