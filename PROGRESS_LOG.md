# Progress Log

Append one entry per completed stage — this is for you as much as for the agent. Keep entries short (3-6 bullets); the goal is being able to explain the project later, not documenting everything.

## Template (copy for each stage)

### Stage NN — <name> — <date>

- What was built:
- Key design decision (and why):
- Verification run (paste the actual command + result, not a description):
- Anything that's a known rough edge / would do differently with more time:

---

<!-- New entries go below this line, most recent last -->

### Stage 01 — Vector Math & Rigid Body Core — 2026-07-22

- What was built: `Vec2` 2D vector class (`physics/vec2.py`) with complete vector math operations (add, sub, scalar multiply, dot, 2D cross, length, normalize, rotate) and `RigidBody` class (`physics/body.py`) supporting force/torque accumulation and semi-implicit Euler integration for dynamic and static bodies.
- Key design decision (and why): Wrapped a numpy 1D float64 array of shape (2,) inside `Vec2` to combine vectorized numpy performance with explicit 2D properties (`.x`, `.y`), operator overloading, and 2D-specific scalar cross products.
- Verification run (paste the actual command + result, not a description):
```
pytest tests/test_stage01.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D_physics_engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 6 items

tests/test_stage01.py::test_vec2_basic_math PASSED                       [ 16%]
tests/test_stage01.py::test_vec2_dot_cross_length_normalize_rotate PASSED [ 33%]
tests/test_stage01.py::test_constant_velocity PASSED                     [ 50%]
tests/test_stage01.py::test_projectile_motion_semi_implicit PASSED       [ 66%]
tests/test_stage01.py::test_off_center_force_and_torque PASSED           [ 83%]
tests/test_stage01.py::test_static_body_does_not_move PASSED             [100%]

============================== 6 passed in 0.46s ==============================
```
- Anything that's a known rough edge / would do differently with more time: `Vec2` handles implicit conversions for tuple/list/array inputs for user convenience, but keeping all internal operations strictly typed to `Vec2` keeps physics operations fast and clean.

### Stage 02 — Shapes & Collision Detection — 2026-07-22

- What was built: Collision shapes (`Circle`, `Polygon`, `AABB` in `physics/shapes.py`) and broad-phase AABB filtering + narrow-phase SAT collision detection (`physics/collision.py`) returning `Contact` data structures (point, normal, penetration).
- Key design decision (and why): Used Separating Axis Theorem (SAT) for convex polygons and circle-vs-polygon, checking edge normals and circle-to-closest-vertex axes to cleanly handle rotated geometry.
- Verification run (paste the actual command + result, not a description):
```
pytest tests/test_stage02.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D_physics_engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 5 items

tests/test_stage02.py::test_circles_overlapping PASSED                   [ 20%]
tests/test_stage02.py::test_circles_separated PASSED                     [ 40%]
tests/test_stage02.py::test_axis_aligned_overlapping_squares PASSED      [ 60%]
tests/test_stage02.py::test_separated_polygons_at_angle PASSED           [ 80%]
tests/test_stage02.py::test_broad_phase_filtering PASSED                 [100%]

============================== 5 passed in 0.17s ==============================
```
- Anything that's a known rough edge / would do differently with more time: Polygon contact point estimation currently uses body center midpoint for poly-poly, which will be refined with contact manifold generation in collision resolution if multiple contact points are needed for complex stacks.

### Stage 03 — Collision Resolution — 2026-07-22

- What was built: Impulse-based collision solver (`physics/resolver.py`) handling normal restitution impulse, Coulomb friction tangent impulse, angular momentum transfer, and Baumgarte-style positional penetration correction.
- Key design decision (and why): Included rotational inertia cross products in the denominator of normal and tangent impulse calculations so off-center impacts correctly generate body rotation and spin.
- Verification run (paste the actual command + result, not a description):
```
pytest tests/test_stage03.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D_physics_engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 4 items

tests/test_stage03.py::test_elastic_bounce_height PASSED                 [ 25%]
tests/test_stage03.py::test_inelastic_collision PASSED                   [ 50%]
tests/test_stage03.py::test_momentum_conservation_elastic PASSED         [ 75%]
tests/test_stage03.py::test_ball_drop_settle_simulation PASSED           [100%]

============================== 4 passed in 0.66s ==============================
```
- Anything that's a known rough edge / would do differently with more time: Positional correction uses simple 40% penetration push-apart per frame with a 0.01 slop threshold; for dense multi-body stacks, iterative constraint relaxation across multiple sub-steps gives even tighter stacking stability.

### Stage 04 — Joints & Constraints — 2026-07-22

- What was built: Joint constraint solvers (`physics/joints.py` containing `DistanceJoint` and `RevoluteJoint`) with Baumgarte bias stabilization and `motor_torque` support on revolute hinges for driving creature limbs.
- Key design decision (and why): Formulated joint constraint impulses along local anchor world-positions with iterative relaxation per timestep, maintaining exact geometric connections between body segments.
- Verification run (paste the actual command + result, not a description):
```
pytest tests/test_stage04.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D_physics_engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 4 items

tests/test_stage04.py::test_distance_joint_length_preservation PASSED    [ 25%]
tests/test_stage04.py::test_revolute_joint_pendulum_period PASSED        [ 50%]
tests/test_stage04.py::test_revolute_joint_motor_torque PASSED           [ 75%]
tests/test_stage04.py::test_two_segment_chain_stability PASSED           [100%]

============================== 4 passed in 2.12s ==============================
```
- Anything that's a known rough edge / would do differently with more time: Solving 2D revolute joints sequentially per axis works well for low segment counts; for deep kinematic trees, block 2x2 matrix constraint solvers could solve both axes simultaneously.
