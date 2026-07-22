# Stage 05 — World Loop & Renderer

**Day 3, first half. Depends on:** Stage 03, Stage 04.

## Goal

Tie physics into a real fixed-timestep simulation loop, and see it — this is the first stage that's actually visible.

## What to build

`physics/world.py`
- `World`: owns `bodies: list[RigidBody]`, `joints: list[Joint]`, `gravity: Vec2` (default `(0, -9.8)`).
- `add_body`, `add_joint`, `step(dt: float)`:
  1. Apply gravity as a force to every dynamic body
  2. `body.integrate(dt)` for every body
  3. `contacts = find_contacts(bodies)`
  4. `resolve_collision(...)` for each contact
  5. `joint.solve(dt)` for every joint (do a few solver iterations, e.g. 4-8, per step — standard for stability with iterative constraint solvers)
- Use a **fixed timestep** (e.g. `dt = 1/60`) regardless of real frame rate — accumulate real elapsed time and step the world in fixed increments (standard game-loop pattern) so physics behavior doesn't change with rendering speed.

`render/renderer.py`
- pygame window, world-to-screen coordinate transform (physics uses meters/SI-ish units with +y up; screen space is pixels with +y down — handle this conversion in one place)
- Draw circles/polygons per body, draw joints as lines between anchor points, optional debug overlay toggle (velocity vectors, contact points from the last step)

`scripts/` — a small `run_scene.py` that builds a `World`, adds a ground (static body) and a few dynamic shapes, and runs the render loop.

## Definition of Done

- [ ] Run `run_scene.py` — a window opens, shapes fall under gravity, collide with the ground and each other, and settle (or bounce, depending on restitution) visibly correctly
- [ ] Fixed timestep confirmed: simulation speed looks the same whether or not you throttle/artificially slow the render loop (test by adding a `time.sleep` in the render-only part and confirming physics doesn't speed up/slow down)
- [ ] No physics computation happens inside the renderer — the renderer only reads final positions/angles, it never mutates them
