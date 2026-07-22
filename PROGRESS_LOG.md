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

### Stage 01 — Vector Math & Rigid Body Core — 2026-07-20

- What was built: `Vec2` 2D vector class (`physics/vec2.py`) with complete vector math operations (add, sub, scalar multiply, dot, 2D cross, length, normalize, rotate) and `RigidBody` class (`physics/body.py`) supporting force/torque accumulation and semi-implicit Euler integration for dynamic and static bodies.
- Key design decision (and why): Wrapped a numpy 1D float64 array of shape (2,) inside `Vec2` to combine vectorized numpy performance with explicit 2D properties (`.x`, `.y`), operator overloading, and 2D-specific scalar cross products.
- Verification run (paste the actual command + result, not a description):
```
pytest tests/test_stage01.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D-Physics-rendering-engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 6 items

tests/test_stage01.py::test_vec2_basic_math PASSED                       [ 16%]
tests/test_stage01.py::test_vec2_dot_cross_length_normalize_rotate PASSED [ 33%]
tests/test_stage01.py::test_constant_velocity PASSED                     [ 50%]
tests/test_stage01.py::test_projectile_motion_semi_implicit PASSED       [ 66%]
tests/test_stage01.py::test_off_center_force_and_torque PASSED           [ 83%]
tests/test_stage01.py::test_static_body_does_not_move PASSED             [100%]

============================== 6 passed in 1.50s ==============================
```
- Anything that's a known rough edge / would do differently with more time: `Vec2` handles implicit conversions for tuple/list/array inputs for user convenience, but keeping all internal operations strictly typed to `Vec2` keeps physics operations fast and clean.

