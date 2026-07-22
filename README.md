# Physics + RL Creature Sandbox

A from-scratch 2D physics engine used as the simulation substrate for two learning systems:
1. A single articulated creature trained with reinforcement learning (PPO) to walk.
2. A population of neural-network-controlled creatures evolved with a genetic algorithm.

Built in 7 days as a portfolio project demonstrating systems programming (physics simulation) and applied ML (RL + evolutionary computation) in one coherent codebase.

## How to use this repo with an AI coding agent

Read files in this order, and **only** load what's needed for the stage you're working on — don't dump the whole `docs/` folder into context at once. That's the whole point of splitting it this way: small, focused context per session instead of one giant spec the model has to re-parse every time.

1. **Always load first, every session:** `docs/00_PROJECT_CONTEXT.md` and `docs/02_AGENT_RULES.md`
2. **Load once, keep for reference:** `docs/01_ARCHITECTURE.md`
3. **Load when touching physics/RL/GA math specifically:** `docs/03_DOMAIN_GLOSSARY.md`
4. **Load to pick the next unit of work:** `docs/04_IMPLEMENTATION_PLAN.md`
5. **Load exactly one file at a time:** `docs/stages/stage_NN_*.md` — this is the actual spec for what to build right now. Do not load other stage files while working a given stage.

After finishing a stage, append a short entry to `PROGRESS_LOG.md` (template included in that file) before moving to the next stage. This is not optional busywork — it's what lets a human (or a fresh agent session with no memory of earlier work) understand what already exists.

## Quick start

```bash
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Stage status

See `docs/04_IMPLEMENTATION_PLAN.md` for the full 14-stage table across the 7-day build. Mark stages done there only after actually running that stage's verification steps — not because code was generated for it.

## Project structure (target — built incrementally, stage by stage)

```
physics_rl_sandbox/
├── physics/        # vector math, rigid bodies, collision, joints, world loop
├── render/         # pygame rendering
├── creatures/      # data-driven creature morphology format + presets
├── rl/             # gymnasium environment + PPO training
├── evolution/      # NN controller + genetic algorithm
├── scripts/        # demo/sanity-check entry points
└── tests/          # unit tests, one set per physics/rl/evolution module
```

Full detail in `docs/01_ARCHITECTURE.md`.
