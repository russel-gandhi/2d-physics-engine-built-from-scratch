# Stage 13 — Integration & Demo Capture

**Day 7, first half. Depends on:** Stage 10, Stage 12.

## Goal

Bring both learning systems into one coherent, demoable artifact — this is what gets shown in the resume/portfolio, so it should read as one project, not two separate scripts.

## What to build

`scripts/demo_walker.py` — loads a trained PPO checkpoint, runs it live in the renderer.
`scripts/demo_evolution.py` — loads the best evolved genome, runs it live in the renderer, alongside (or followed by) the fitness-over-generations plot.
- If time allows: a single script/menu that can run either "brain" (PPO policy or evolved `NNController`) on the same creature, back to back, so the parallel is visually obvious — this is the payoff of having built `NNController.act()` with the same signature shape the RL policy uses.
- Screen-record (or use pygame's own frame-dump, or `ffmpeg` on the rendered window) short clips of: the RL walker, the best evolved agent, and (optional but nice) the fitness curve animating.

## Definition of Done

- [ ] Both demo scripts run standalone and produce a live-rendered result from real saved artifacts (a PPO checkpoint file, a saved best-genome array) — not from re-running training live during the demo
- [ ] At least one recorded clip of each ("RL walker" and "evolved agent") saved to disk
- [ ] Nothing in the demo path silently falls back to a scripted/canned animation if loading a checkpoint fails — a missing/broken checkpoint should error clearly, not substitute fake footage
