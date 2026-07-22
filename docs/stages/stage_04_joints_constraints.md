# Stage 04 — Joints & Constraints

**Day 2, second half. Depends on:** Stage 01 (does not need collision — joints connect bodies directly).

## Goal

Let two bodies be connected — this is the difference between "objects in a scene" and "a walker with limbs," and every creature in this project depends on it.

## What to build

`physics/joints.py`
- `Joint` base concept: something with a `solve(dt: float) -> None` method, called once (or a few iterations) per `World.step`.
- `DistanceJoint(body_a, anchor_a: Vec2, body_b, anchor_b: Vec2, rest_length: float)` — keeps the world-space distance between the two anchor points equal to `rest_length`. Solve via a velocity-level correction: compute the relative velocity along the joint axis and apply an impulse to cancel any component that would change the distance (same style as collision resolution, but along the joint axis instead of a collision normal, and it corrects in both directions rather than only when separating).
- `RevoluteJoint(body_a, anchor_a: Vec2, body_b, anchor_b: Vec2)` — pins the two anchor points together (a hinge) — this is what connects creature limb segments. Implement as a 2D point constraint: both bodies' world-space anchor points must coincide; solve via an impulse similar to `DistanceJoint` but constraining both x and y (two scalar constraints, or one 2D constraint solved directly).
- Add `motor_torque: float` (settable, default 0) to `RevoluteJoint` — applied as equal-and-opposite torque to both connected bodies each step, before the constraint solve. This is what an RL action or NN controller will drive later.

## Definition of Done

- [ ] Unit test: `DistanceJoint` between two dynamic bodies — after simulating a few steps under gravity, the distance between anchor points stays within a small tolerance of `rest_length` (it will drift slightly with iterative solving — that's expected; it should not diverge)
- [ ] Unit test: `RevoluteJoint` between a static body and a dynamic body (a simple pendulum) — the dynamic body's anchor point stays at the pin location while the body swings; period of small-angle oscillation roughly matches the pendulum formula `T ≈ 2π√(L/g)` as a sanity check
- [ ] Unit test: setting `motor_torque` on a `RevoluteJoint` between two free bodies causes them to rotate relative to each other in the expected direction
- [ ] Manual/visual check (print or plot positions over time): a 2-segment chain hanging from a fixed point swings and settles without flying apart or the joint visibly stretching
