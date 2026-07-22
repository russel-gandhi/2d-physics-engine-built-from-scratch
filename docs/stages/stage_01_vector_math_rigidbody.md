# Stage 01 — Vector Math & Rigid Body Core

**Day 1, first half. Depends on:** nothing (first stage).

## Goal

Build the minimal math and state representation every later physics module needs: 2D vectors and a rigid body that can be pushed around by forces.

## What to build

`physics/vec2.py`
- A `Vec2` type (numpy array of shape `(2,)` wrapped in a small class, or plain numpy — pick one and use it consistently everywhere from here on) with: add, subtract, scalar multiply, dot product, cross product (2D cross returns a scalar: `a.x*b.y - a.y*b.x`), length, normalize, and `rotate(angle)`.

`physics/body.py`
- `RigidBody` with: `position: Vec2`, `velocity: Vec2`, `angle: float`, `angular_velocity: float`, `mass: float`, `moment_of_inertia: float`, `force_accum: Vec2`, `torque_accum: float`.
- `apply_force(force: Vec2, point: Vec2 | None = None)` — accumulates force; if `point` is given (world-space), also accumulates the resulting torque (`torque = (point - position).cross(force)`).
- `apply_torque(t: float)` — accumulates torque directly.
- `integrate(dt: float)` — semi-implicit Euler (see `03_DOMAIN_GLOSSARY.md`): update velocity/angular_velocity from accumulated force/torque, then update position/angle from the new velocities, then zero the accumulators.
- Support both dynamic bodies (`mass > 0`, `inv_mass = 1/mass`) and static bodies (`mass = 0` → `inv_mass = 0`, never moved by forces) — static bodies are needed for the ground in stage 05.

## Definition of Done

- [ ] Unit test: a body with mass 1, no forces, initial velocity `(1, 0)` — after `integrate(dt=1.0)` ten times, position is `(10, 0)` (constant-velocity sanity check)
- [ ] Unit test: a body with mass 1 under constant gravity force `(0, -9.8)`, starting at rest — verify position after `integrate` matches the analytical projectile formula `y = y0 - 0.5*g*t^2` within a small numerical tolerance (this catches integrator bugs — do not skip this test)
- [ ] Unit test: `apply_force` at an off-center point produces nonzero torque, and a body with only torque applied (no net force) rotates but does not translate
- [ ] Static body (`mass=0`) does not move under any applied force
- [ ] All tests actually run and pass — paste the pytest output in `PROGRESS_LOG.md`, don't just claim it works
