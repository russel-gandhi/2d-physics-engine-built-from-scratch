# Stage 25 — Sandbox Mode

**Phase 6. Depends on:** Stage 16 (needs robots to spawn, not combat).

## Goal

A free-play space to experiment with the physics/robots directly — "a virtual robotics laboratory," per the concept doc.

## What to build

`sandbox/sandbox_mode.py`
- An interactive scene (extend stage 05's render loop) with live controls (keyboard bindings are enough — no need for a GUI framework): spawn a shape or a robot preset at the cursor/a fixed point, adjust `world.gravity` live, swap the ground/terrain shape, pause/resume/reset the scene.
- Keep this a thin layer over `World` and existing render code — sandbox mode shouldn't need new physics logic, just new ways to poke the existing `World` interactively.

## Definition of Done

- [ ] Running sandbox mode, you can spawn at least one shape and one robot preset live, and see gravity changes take effect immediately on already-spawned bodies (not just newly spawned ones — gravity is applied every step in `World.step`, so this should just work if `world.gravity` is genuinely mutated, not copied at spawn time)
- [ ] Reset control genuinely rebuilds the world from empty, not just visually clearing the screen while stale bodies still exist in memory
