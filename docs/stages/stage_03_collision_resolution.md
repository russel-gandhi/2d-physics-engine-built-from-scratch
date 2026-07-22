# Stage 03 — Collision Resolution

**Day 2, first half. Depends on:** Stage 02.

## Goal

Turn detected contacts into actual velocity changes, so bodies bounce/stop instead of passing through each other.

## What to build

`physics/resolver.py`
- `resolve_collision(a: RigidBody, b: RigidBody, contact: Contact, restitution: float, friction: float) -> None`
  - Compute relative velocity along the contact normal.
  - If bodies are already separating (relative velocity along normal > 0), skip — don't add energy to a collision that's already resolving.
  - Compute and apply the normal impulse (see glossary formula), respecting each body's `inv_mass` (so static bodies, `inv_mass=0`, don't move).
  - Apply a basic Coulomb friction impulse tangent to the normal, clamped by `friction * normal_impulse` magnitude.
  - Positional correction: push bodies apart along the normal by a fraction of `contact.penetration` to prevent sinking — a simple percentage correction (e.g. correct 20-80% of penetration per step) is sufficient; don't try to make this perfectly energy-conserving.
- Wire into a per-step call: for every `Contact` from `find_contacts`, call `resolve_collision`.

## Definition of Done

- [ ] Unit test: a ball dropped onto a static ground with `restitution=1.0` (idealized, frictionless, single-bounce test) returns to very close to its original height after one bounce (energy roughly conserved — allow a small numerical tolerance, don't expect exact due to discrete timestep)
- [ ] Unit test: `restitution=0.0` → ball does not bounce, comes to rest on the ground
- [ ] Unit test: two dynamic bodies colliding — total momentum before ≈ total momentum after (within tolerance) for `restitution=1.0`
- [ ] Visual/manual check: run a short scene (can piggyback on stage 05's renderer once it exists — for now, print positions per frame or plot with matplotlib) showing a ball dropping and settling on the ground without jittering forever or sinking through it
- [ ] No special-casing that fakes a "good-looking" bounce independent of the actual computed impulse — the numbers must come from the formula, not be nudged to look right
