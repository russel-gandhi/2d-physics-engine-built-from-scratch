# Stage 30 — Playground Mode UI

**Phase 8. Depends on:** Stage 29, Stage 25 (sandbox mode).

## Goal

A UI over `sandbox/sandbox_mode.py` — free spawning and live world tweaks, exactly what that module already supports, just clickable instead of keybound.

## What to build

`web/frontend/playground.js`
- Controls mirroring `sandbox/sandbox_mode.py`'s existing capabilities: spawn a shape, spawn a robot preset (dropdown of existing presets), a gravity slider, a terrain reset button, pause/resume.
- Each control calls the matching Stage 28 backend endpoint and relies on the next streamed state to reflect the change — don't optimistically draw a change on the client before the backend confirms it, since that risks the UI showing something that didn't actually happen server-side.

## Definition of Done

- [ ] Spawning a shape and a robot preset from the UI produces real new bodies in the next streamed state, matching what a direct call to `sandbox_mode.py` would produce
- [ ] The gravity slider's effect is visible on already-spawned bodies within a second, confirming it's mutating live state and not just affecting future spawns
- [ ] Terrain reset visibly clears the scene and the backend confirms an empty/reset world state, not just a client-side canvas clear
