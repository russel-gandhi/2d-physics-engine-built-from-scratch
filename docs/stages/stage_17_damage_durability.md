# Stage 17 — Damage & Durability

**Phase 3. Depends on:** Stage 16.

## Goal

Make combat physics-driven: damage comes from real computed collision impulses, not a scripted "attack" system.

## What to build

`combat/damage.py`
- `apply_impulse_damage(contact: Contact, impulse_magnitude: float, struck_component, threshold: float, scale: float) -> None` — called from the collision resolution step (extend `physics/resolver.py`'s per-contact loop, or hook in via a callback so `physics/` doesn't need to know about combat concepts directly — keep the physics core combat-agnostic, this is important for architecture cleanliness). If `impulse_magnitude > threshold`, reduce `struck_component.durability` by `(impulse_magnitude - threshold) * scale`.
- Component breaking: when a component's durability reaches 0, mark it broken — a broken `Motor`/`Limb` stops responding to `motor_torque` (set it to 0 and ignore further commands), a broken `Chassis` ends the match for that robot (see stage 19).
- Keep the physics core (`physics/`) itself unaware of "damage" — it only produces contacts and impulses; `combat/damage.py` is what interprets those for robots. This keeps the physics engine reusable/testable independent of the combat layer, which is good architecture and a good thing to be able to explain.

## Definition of Done

- [ ] Unit test: a contact with impulse magnitude below `threshold` causes no durability loss
- [ ] Unit test: a contact with impulse magnitude above `threshold` causes durability loss proportional to the excess (not a flat/fixed amount — confirm by testing two different impulse magnitudes and checking the damage scales)
- [ ] Unit test: a component reaching exactly 0 durability is marked broken, and a broken `Motor`'s `motor_torque` has no effect on the simulation afterward (verify by setting it and checking the body's angular velocity doesn't respond)
- [ ] Manual/visual check: two robots collided at high relative velocity (e.g. one thrown or driven hard into the other) show real, different damage amounts depending on impact force — not a fixed "hit = 10 damage" regardless of how hard the impact was
