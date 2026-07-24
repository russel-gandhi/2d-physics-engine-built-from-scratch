# RoboForge Arena

A robot combat simulation platform built entirely on a from-scratch 2D physics engine: design robots from modular components, train them to fight with reinforcement learning or evolutionary algorithms, and run local battles where combat emerges from real physics — no scripted attack animations.

Built as a portfolio project demonstrating physics simulation, applied ML (RL + evolutionary computation), and game-systems design in one coherent codebase.

**Scope note:** real networked multiplayer, matchmaking, ranked servers, and a robot marketplace are part of the long-term vision but are *not* part of the current build — see `docs/05_FUTURE_VISION.md` for why. What's here is local: a single machine, two robots in a shared simulation, real physics-driven combat.

## How to use this repo with an AI coding agent

Read files in this order, and **only** load what's needed for the stage you're working on — don't dump the whole `docs/` folder into context at once.

1. **Always load first, every session:** `docs/00_PROJECT_CONTEXT.md` and `docs/02_AGENT_RULES.md`
2. **Load once, keep for reference:** `docs/01_ARCHITECTURE.md`
3. **Load when touching physics/RL/GA/combat math specifically:** `docs/03_DOMAIN_GLOSSARY.md`
4. **Load to pick the next unit of work:** `docs/04_IMPLEMENTATION_PLAN.md`
5. **Load exactly one file at a time:** `docs/stages/stage_NN_*.md` — the actual spec for what to build right now
6. **For anything about multiplayer/marketplace/community features:** `docs/05_FUTURE_VISION.md` — this is direction, not a stage to implement

After finishing a stage, append a short entry to `PROGRESS_LOG.md` before moving to the next stage.

## Quick start

```bash
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Build phases

| Phase | What it covers |
|---|---|
| 1 | Physics engine + a generic creature trained to move (RL + evolution) |
| 2 | Robot component system — chassis/armor/limbs/weapons/sensors/energy with real tradeoffs |
| 3 | Combat mechanics — physics-derived damage, weapons, a local 1v1 arena |
| 4 | Combat intelligence — RL self-play and evolutionary combat fitness |
| 5 | Replay and spectator polish |
| 6 | Sandbox and structured experiment modes |
| 7 | Post-battle analytics |

Full stage-by-stage detail in `docs/04_IMPLEMENTATION_PLAN.md`. Multiplayer/platform features beyond this are in `docs/05_FUTURE_VISION.md`, deliberately not staged.

## Project structure (target — built incrementally, stage by stage)

```
physics_rl_sandbox/
├── physics/        # vector math, rigid bodies, collision, joints, world loop
├── render/         # pygame rendering
├── creatures/      # data-driven articulated-body format
├── rl/             # gymnasium environment + PPO training
├── evolution/      # NN controller + genetic algorithm
├── robots/         # robot component system, built on creatures/
├── combat/         # damage, weapons, local arena, combat RL environment
├── replay/         # match recording and playback
├── sandbox/        # free-play and structured experiments
├── analytics/      # post-battle reports
├── scripts/        # demo/sanity-check entry points
└── tests/          # unit tests, one set per module
```

Full detail in `docs/01_ARCHITECTURE.md`.
