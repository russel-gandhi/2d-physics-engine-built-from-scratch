# Stage 16 — Robot Presets & Scene Test

**Phase 2. Depends on:** Stage 15.

## Goal

Prove the component system produces genuinely different robots with real engineering tradeoffs — the "players must balance tradeoffs" part of the concept doc, verified in simulation rather than just asserted in a spec file.

## What to build

`robots/presets/lightweight_fighter.json` (or `.py`) — low mass, minimal armor, higher motor torque-to-mass ratio → should move faster but have low durability.
`robots/presets/heavy_tank.json` — high armor/durability, higher total mass, same or lower motor torque → should move slower but survive more hits.

`scripts/robot_scene_test.py` — load both presets into the same `World` (reuse stage 05's renderer), apply the same test stimulus to each independently (e.g. the same motor torque profile) and observe/log their actual resulting speed. If stage 17 (damage) isn't built yet, just log mass/durability numbers for now and revisit the "how much damage to destroy each" comparison once it is.

## Definition of Done

- [ ] Both presets load and simulate correctly (no exploding joints, no invalid physics)
- [ ] Under an identical motor torque profile, the lightweight fighter demonstrably reaches higher speed than the heavy tank in the same time window — measured from the actual simulation run, not asserted from the spec numbers alone
- [ ] Presets are genuinely data-driven — editing a value in the JSON changes the simulated robot without touching Python code (same test as stage 06, applied to robots now)
