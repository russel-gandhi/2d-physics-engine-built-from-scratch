# Stage 02 — Shapes & Collision Detection

**Day 1, second half. Depends on:** Stage 01.

## Goal

Give bodies a shape, and detect when two shapes overlap — detection only, no resolution yet (that's stage 03).

## What to build

`physics/shapes.py`
- `Circle(radius: float)` and `Polygon(vertices: list[Vec2])` (vertices in local space, counter-clockwise winding). Both attach to a `RigidBody` (add a `shape` field to `RigidBody`, or a `shape` param to its constructor).
- Each shape exposes `get_aabb(body: RigidBody) -> AABB` (world-space bounding box given the body's current position/angle) and `get_world_vertices(body) -> list[Vec2]` for polygons.

`physics/collision.py`
- `AABB` dataclass (`min: Vec2`, `max: Vec2`) + `aabb_overlap(a: AABB, b: AABB) -> bool` — broad phase.
- Narrow-phase, returning `Contact | None` (dataclass: `point: Vec2`, `normal: Vec2`, `penetration: float`):
  - `circle_vs_circle(a, b) -> Contact | None`
  - `circle_vs_polygon(circle, poly) -> Contact | None`
  - `polygon_vs_polygon(a, b) -> Contact | None` — implement via SAT (see glossary): project both shapes onto each candidate axis, if any axis shows separation return `None`, otherwise return the contact using the minimum-overlap axis as the normal.
- `find_contacts(bodies: list[RigidBody]) -> list[Contact]` — for every pair, AABB-check first (skip the pair if no overlap), only run narrow-phase on pairs that pass.

## Definition of Done

- [ ] Unit test: two circles with distance between centers less than the sum of radii → contact returned with correct penetration depth (check against a hand-computed value)
- [ ] Unit test: two circles far apart → `None`
- [ ] Unit test: two axis-aligned overlapping squares (simple case, easy to hand-verify) → correct normal (should point along one of the two obvious axes) and penetration
- [ ] Unit test: two separated polygons at an angle (not axis-aligned) → `None` — this specifically tests that SAT checks edge-normal axes, not just x/y
- [ ] `find_contacts` on a list of 5+ bodies only calls narrow-phase on AABB-overlapping pairs (add a call counter or log to confirm, then remove/quiet it once verified)
