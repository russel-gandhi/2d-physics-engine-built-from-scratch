# Project Context — Read This First

> Load this file at the start of every agent session. It is the single source of truth for what this project is. If anything in a stage file seems to contradict this document, this document wins — stop and flag it instead of guessing.

## What

**RoboForge Arena** — a robot combat simulation platform built entirely on a custom 2D physics engine. Players design robots from modular components, train combat behavior with reinforcement learning or evolutionary algorithms, then fight locally in a physics-driven arena with no scripted attack animations — combat emerges from physics, robot design, and learned behavior.

The current build has two layers on the same physics core:

- **Foundation (Phase 1):** the hand-built physics engine itself — rigid bodies, collision, joints — plus a generic articulated "creature" that can be trained to locomote via RL (PPO) or evolved via a genetic algorithm. This is the substrate everything else stands on.
- **RoboForge (Phases 2-7):** robots as specialized creatures assembled from components (chassis, armor, limbs, weapons, sensors, energy), combat mechanics (physics-derived damage, no scripted hits), combat-trained fighters (RL self-play + evolutionary tournaments), local 1v1 battles with replay, a sandbox and structured experiment mode, and post-battle analytics reports.
- **UI Dashboard (Phase 8):** a local web dashboard — the simulation core stays exactly as built; a thin backend streams live state over WebSocket to a browser frontend with three modes: **Playground** (free sandbox), **Gym** (train PPO/GA agents, flat terrain for now — terrain variety is Phase 9, sequenced after the UI), and **Competitive** (local 1v1 matches, robots choosing their own strategy from training — never manual/scripted input). Robots render as articulated joint figures (circles at joints, lines for limbs), and fighter presets carry archetype names (e.g. "Boxer", "Grappler") on top of the existing component system from Phase 2 — this is presentation and preset variety, not a new combat mechanic.

**Not in the current build** (see `05_FUTURE_VISION.md`): real networked multiplayer, matchmaking, ranked ladders, tournaments run across machines, a robot marketplace, community rankings. These require server/networking infrastructure that is a different scale of engineering than everything above combined — that doc explains why they're documented separately instead of staged.

## Why

- **Primary:** a portfolio/resume project demonstrating physics simulation, applied ML (RL + evolutionary computation), and game-systems design (component-based creature design, combat mechanics, replay systems) in one coherent codebase.
- **Secondary:** the builder wants to genuinely understand every part of the code — able to explain it in an interview — not just end up with a working demo they can't walk through.
- The scope grew from a smaller physics+RL sandbox into this fuller vision; the build is being done with AI coding-agent assistance, so the plan favors clear, small, verifiable stages over trying to move fast by skipping verification.

## Who

- **Builder / primary user:** a first-year Data Science & AI undergraduate, comfortable with ML/hackathon work, newer to physics simulation and lower-level systems/game-architecture code.
- **Audience for the finished result:** resume readers, interviewers, hackathon/portfolio viewers — people who may ask "walk me through how this works." Clarity of code and of the explanations matters as much as the demo itself.
- **The coding agent (you):** working mostly autonomously per stage, likely on a lightweight/free model. This document set exists to give you complete context up front and avoid back-and-forth burning time and tokens.

## When

- No fixed calendar deadline — the build is paced with AI coding-agent assistance rather than a rigid day count. Phase 1 (stages 01-14) was originally scoped as roughly a week of focused work and is a reasonable pace baseline; Phases 2-7 (stages 15-27) are sized the same way (each stage ≈ half a day to a day of focused, verifiable work) but aren't assigned to specific days.
- **Order matters and is dependency-driven** — see `04_IMPLEMENTATION_PLAN.md`. Do not start combat mechanics before robots exist, don't start combat RL/GA before combat mechanics are verified, don't start replay/analytics before there's a real match loop producing real data to record.

## Where

- **Runs locally** on the builder's machine — no deployment, no server, no cloud training/hosting. Target is a laptop/desktop CPU; do not assume a GPU is available.
- **Language/stack:** Python 3.10+. The physics simulation core is hand-built — no physics engine libraries (Box2D, pymunk, etc.) standing in for it. Beyond that, library choice is open (`numpy`/`torch`, `pygame`, `gymnasium`, `stable-baselines3`, `matplotlib`, plus whatever else genuinely fits) — the only constraint is understanding what every library call does well enough to explain it.
- **Repo layout:** see `01_ARCHITECTURE.md`.

## Non-goals for the current build

- 3D physics
- **Terrain variety (hills, gaps, stairs)** — Gym mode currently trains and displays on flat terrain only. This was deliberately sequenced after the UI (Phase 8) rather than before it, and will become its own phase once picked up — don't quietly add partial terrain support inside a UI stage.
- **Real networked multiplayer, matchmaking, ranked servers, tournaments across machines, a robot marketplace, community rankings** — see `05_FUTURE_VISION.md`. "Local 1v1 battle" (two robots in the same simulation on one machine) is in scope and is *not* the same thing as networked multiplayer — don't build a fake/stubbed networking layer to simulate the appearance of this; build the honest local version instead.
- A full GUI level/robot editor — sandbox and experiment modes (Phase 6) are script/keybinding-driven, not a drag-and-drop UI
- Hand-rolled PPO (using `stable-baselines3` is intentional — see the domain glossary)
- Photorealistic rendering — `pygame` primitives are enough
- Mobile/web builds

If a stage seems to be drifting toward any of the above, stop and flag it rather than continuing.
