# Stage 06 — Creature Morphology Format & Manual Scene Test

**Day 3, second half. Depends on:** Stage 05.

## Goal

Define a reusable, data-driven format for "a creature" so both the RL environment (stage 07) and the evolutionary population (stage 11) build creatures the same way, from the same files.

## What to build

`creatures/morphology.py`
- A `CreatureSpec` dataclass (or JSON schema) describing: a list of segments (shape, size, mass, initial relative position/angle) and a list of joints connecting them (which two segments, anchor points, motor torque limits).
- `build_creature(spec: CreatureSpec, world: World, base_position: Vec2) -> Creature` — instantiates the bodies and joints described by the spec into a `World` at a given position, and returns a `Creature` object holding references to its own bodies/joints (needed later so the RL/GA layers can read this creature's state and drive its motors without touching unrelated bodies in the world).

`creatures/presets/hopper.json` (or `.py`) — the simplest creature that can plausibly learn to move: e.g. 2 segments (a body + one leg) with 1 motorized revolute joint. Keep this simple — a minimal viable creature is the priority; more complex morphologies are a stretch goal only if days 5-6 finish early.

## Definition of Done

- [ ] `build_creature` loading the hopper preset into a `World`, run through stage 05's render loop with a fixed or randomly-varying `motor_torque` on its joint — you can visually see it flail/hop under the applied torque and gravity, connected correctly (no disconnected limbs, no exploding joints)
- [ ] Creature spec is genuinely data-driven — changing a number in the preset file (e.g. leg length) changes the simulated creature without touching Python code; confirm this by actually editing the file and rerunning
