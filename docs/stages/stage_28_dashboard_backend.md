# Stage 28 — Dashboard Backend

**Phase 8. Depends on:** Stage 06 (creature format), Stage 19 (arena).

## Goal

A backend that drives the existing simulation modules and streams their real state — it does not reimplement any physics, training, or combat logic.

## What to build

`web/server.py`
- A FastAPI app with a WebSocket endpoint (e.g. `/ws/state`) that streams the current simulation state at a fixed rate (target the render rate from Stage 05, e.g. 30-60 Hz) as JSON.
- Control endpoints (REST is fine): select mode (`playground` / `gym` / `competitive`), start/pause/reset, and mode-specific actions (spawn a shape/robot, start training, start a match) — each of these calls straight into the existing module (`sandbox/sandbox_mode.py`, `rl/train_ppo.py`/`evolution/ga.py`, `combat/arena.py`) rather than reimplementing what they do.
- Keep exactly one simulation "owner" object alive per mode session server-side (a `World`, an `Arena`, a training loop) — the backend's job is to expose it, not duplicate its state.

`web/state_encoder.py`
- `encode_state(world_or_arena) -> dict`: serializes body positions/angles, joint connections (for the renderer to draw limbs), and mode-specific extras (reward/episode info for Gym, durability/hp for Competitive) into a JSON-serializable dict. This is the single place that translates internal physics objects into what the frontend sees — if a new field is ever needed on screen, it's added here, not invented client-side.

## Definition of Done

- [ ] Connecting a WebSocket client (even a simple test script, not the real frontend yet) to `/ws/state` while a scene is running receives a real stream of changing positions — verify by printing a few consecutive messages and confirming the numbers actually move
- [ ] A control endpoint call (e.g. spawn a shape in Playground) has a visible, verifiable effect on the next streamed state — not just a 200 response with no real change
- [ ] No endpoint returns synthetic/example data when the underlying simulation isn't actually running — an empty/not-started state should be represented honestly (e.g. an empty body list), never filled with placeholder values
