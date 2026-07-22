# Stage 18 — Weapons

**Phase 3. Depends on:** Stage 17.

## Goal

Give robots a way to deal damage on purpose, still derived from real physics rather than a scripted hit.

## What to build

`combat/weapons.py`
- A `Weapon` component (e.g. a striker limb) that carries a `damage_multiplier` applied on top of stage 17's impulse-derived damage formula when the *weapon's* body is the one making contact (vs. a passive collision between two non-weapon components, which still deals some damage per stage 17, just without the multiplier).
- Keep weapons to melee/contact-based for this build (a striking limb, e.g. driven by a motorized joint with high torque) — a full projectile system (spawning/tracking separate projectile bodies, collision against them) is a real feature but adds meaningful scope; note it as a stretch addition only if earlier phases finish with time to spare, and if added, it should reuse the same physics/collision/damage pipeline rather than a separate hit-detection system.

## Definition of Done

- [ ] Unit test: identical impulse magnitude, weapon component vs. non-weapon component making contact — weapon case deals more damage, by the documented multiplier, computed from the same underlying formula
- [ ] Manual/visual check: a robot with a weapon limb, driven to swing into an opponent, visibly deals more damage than the same swing would from a non-weapon limb — confirm by comparing logged damage numbers from two actual runs, not by assumption
