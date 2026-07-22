# Project Context — Read This First

> Load this file at the start of every agent session. It is the single source of truth for what this project is. If anything in a stage file seems to contradict this document, this document wins — stop and flag it instead of guessing.

## What

A 2D physics engine, built from scratch (no Box2D, pymunk, or other physics library — only `numpy` for the math), that simulates rigid bodies, collisions, and articulated joints. On top of that physics core sit two separate "brains":

- **A) RL Walker** — one articulated creature (a small number of rigid segments connected by motorized joints) trained with PPO (via `stable-baselines3`) to locomote.
- **B) Evolutionary Sandbox** — a population of creatures controlled by small neural networks, evolved over generations with a genetic algorithm (selection, crossover, mutation) — no gradient-based training involved in this half.

Both systems run on the **same physics core** and the **same creature representation**, so the finished codebase reads as one coherent simulation platform with two different "brains" plugged into it — not two unrelated demos glued together at the end.

## Why

- **Primary:** a portfolio/resume project demonstrating both systems-level engineering (writing a physics engine, not importing one) and applied ML (RL + evolutionary computation) in a single project.
- **Secondary:** the builder wants to genuinely understand every part of the code afterward — able to explain it in an interview — not just end up with a working demo they can't walk through.
- This is a side project running alongside other hackathon work. It does not need to scale beyond a single machine, a single user, or beyond the 7-day build window.

## Who

- **Builder / primary user:** a first-year Data Science & AI undergraduate, comfortable with ML/hackathon work, newer to physics simulation and lower-level systems code.
- **Audience for the finished result:** resume readers, interviewers, hackathon/portfolio viewers — people who may ask "walk me through how this works." Clarity of code and of the explanations (physics core, RL vs. GA) matters as much as the demo itself.
- **The coding agent (you):** working mostly autonomously per stage, likely on a lightweight/free model. This document set exists specifically to give you complete context up front and avoid back-and-forth clarification burning time and tokens.

## When

- Total build window: **7 days**, 2 stages per day (see `04_IMPLEMENTATION_PLAN.md` for the exact table).
- Order matters and is dependency-driven: physics core → collision → joints → world/rendering → creature format → RL environment → RL training → evolutionary layer → integration/polish. Do not start RL or evolution work before the physics core it depends on is verified working — a bug in the physics core will silently corrupt everything built on top of it.

## Where

- **Runs locally** on the builder's machine — no deployment, no server, no cloud training. Target is a laptop/desktop CPU; do not assume a GPU is available (PPO on this small a policy network is fine on CPU).
- **Language/stack:** Python 3.10+. The physics simulation core (integration, collision, joints) is hand-built — no physics engine libraries (Box2D, pymunk, etc.) standing in for it, since building that is the actual point of the project. Beyond that, library choice is open: `numpy` is the natural default for the physics math, `pygame` for rendering, `gymnasium` for the RL environment API, `stable-baselines3` for PPO, `matplotlib` for plots — but swap in `torch`, `scipy`, or anything else where it's a better fit (e.g. the evolutionary NN controller in stage 11 can use numpy or torch). The only real constraint: you understand what every library call is doing well enough to explain it in an interview — don't reach for one as a black box you can't defend.
- **Repo layout:** see `01_ARCHITECTURE.md`.

## Non-goals (explicitly out of scope for the 7-day build)

- 3D physics
- Networked/multiplayer anything
- A GUI level editor
- Hand-rolled PPO (using `stable-baselines3` is intentional — the resume value here is building the *environment and physics*, not re-deriving a well-known RL algorithm badly in a week)
- Photorealistic rendering — `pygame` primitives (lines, polygons, circles) are enough
- Mobile/web builds

If a stage seems to be drifting toward any of the above, stop and flag it rather than continuing.
