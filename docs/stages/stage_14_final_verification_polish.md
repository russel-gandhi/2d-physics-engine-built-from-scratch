# Stage 14 — Final Verification & Polish

**Day 7, second half. Depends on:** Stage 13.

## Goal

Confirm the whole project actually holds up end-to-end, and package it so it's presentable — on GitHub, in an interview, or in a portfolio link.

## What to build / do

**Anti-hardcoding audit** (go through `02_AGENT_RULES.md`'s hard rules against the *entire* codebase, not just the stage you last touched):
- Grep for suspicious patterns: bare `except:` blocks, functions that `return` a constant where a computed value is expected, any leftover `TODO`/stub from earlier stages
- Re-run every stage's unit tests together (`pytest`) — confirm nothing that passed in isolation earlier broke once later stages were added
- Re-run `demo_walker.py` and `demo_evolution.py` from a clean checkout (fresh venv) to confirm there's no hidden dependency on leftover state from development

**README** — top-level project README (already scaffolded — fill it in for a human reader, not an agent): what it is, a gif/screenshot, how to run it, a short "how it works" section pointing at `01_ARCHITECTURE.md` for detail.

**Architecture diagram** — a simple visual (even a hand-drawn-style block diagram) of the module map from `01_ARCHITECTURE.md` — physics core → creature layer → RL / GA branching off it. Good portfolio material on its own.

**Progress log review** — read back through `PROGRESS_LOG.md`; for each stage, make sure you (the human) can actually explain what was built and why, in your own words — this is the point of keeping the log. If any entry doesn't make sense on re-read, that's worth spending remaining time on over any further feature work.

## Definition of Done

- [ ] Fresh-environment run of the full test suite and both demo scripts succeeds
- [ ] README is written for a human, not restating the `docs/` files verbatim
- [ ] You can, without looking at the code, explain: how the physics integrator works, how collision resolution works, the difference between the RL and GA approaches used here, and why PPO was used as a library while the physics/evolution/NN pieces were hand-built
