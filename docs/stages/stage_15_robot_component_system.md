# Stage 15 — Robot Component System

**Phase 2. Depends on:** Stage 06 (creature morphology format).

## Goal

Turn the generic creature format into a robot-building system with real physical tradeoffs — this is what lets "Lightweight Fighter" and "Heavy Tank Fighter" be genuinely different robots, not just reskins.

## What to build

`robots/components.py`
- Component type definitions, each with physical properties consistent with what `creatures/morphology.py` already uses (mass, size) plus combat-relevant ones added here: `durability` (max HP), `energy_consumption` (drains an energy pool when active — see below), `movement_constraint` (e.g. a wheel component only allows rolling motion, not arbitrary rotation — keep this simple; a documented limitation is fine if full constraint enforcement gets complex).
- Component categories, mirroring the concept doc: `Chassis` (the core body — robot "dies" when this reaches 0 durability), `Armor` (extra durability layered on another component, adds mass), `Limb` (a segment + revolute joint, as creatures already support), `Wheel` (a limb variant biased toward rolling), `Sensor` (no physical footprint — just widens the observation space in Phase 4), `Motor` (a revolute joint's torque capacity), `Weapon` (see stage 18), `EnergySystem` (defines the robot's total energy pool and regen rate).

`robots/robot_spec.py`
- `RobotSpec` extending `CreatureSpec` — same segments/joints structure, plus a `components: dict[segment_id, Component]` mapping.
- `build_robot(spec: RobotSpec, world: World, base_position: Vec2) -> Robot` — mirrors `build_creature`, and additionally tracks per-component durability and the robot's current energy level on the returned `Robot` object.

## Definition of Done

- [ ] A robot built from `RobotSpec` behaves identically to a plain creature at the physics level (same integration/collision/joint behavior) — components add data, they don't change the physics
- [ ] Unit test: a robot with an `Armor` component on a segment has measurably higher mass than the same segment without it, and this changes its simulated behavior (e.g. falls with more momentum) — confirmed by an actual simulation run, not just checking the stored mass value
- [ ] Unit test: total robot mass/durability/energy is computed by summing its components, not set as a separate hardcoded field that could drift out of sync with the components list
