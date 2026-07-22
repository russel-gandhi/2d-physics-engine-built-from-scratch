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

### Stage 05 — World Loop & Renderer — 2026-07-22

- What was built: `World` class (`physics/world.py`) managing fixed-timestep simulation loop (`dt=1/60`), gravity application, integration, collision detection/resolution, and iterative joint constraint solving; Pygame renderer (`render/renderer.py`) with world-to-screen coordinate transforms (+y up to +y down), body/joint drawing, and debug overlays; demo runner (`scripts/run_scene.py`).
- Key design decision (and why): Decoupled rendering from physics simulation using a fixed-timestep accumulator in the main loop so physics fidelity and speed are completely independent of rendering framerate or sleep delays.
- Verification run (paste the actual command + result, not a description):
```
pytest tests/test_stage05.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D_physics_engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 4 items

tests/test_stage05.py::test_world_physics_simulation PASSED              [ 25%]
tests/test_stage05.py::test_fixed_timestep_independence PASSED           [ 50%]
tests/test_stage05.py::test_headless_renderer PASSED                     [ 75%]
tests/test_stage05.py::test_run_scene_headless_execution PASSED          [100%]

======================== 4 passed, 2 warnings in 1.86s ========================
```
- Anything that's a known rough edge / would do differently with more time: Renderer is pure Pygame primitives; adding anti-aliased surface rendering and customizable camera zoom/pan controls will enhance interactive visual exploration during creature training.

### Stage 06 — Creature Morphology Format & Manual Scene Test — 2026-07-22

- What was built: Data-driven morphology spec loader (`CreatureSpec`, `SegmentSpec`, `JointSpec` in `creatures/morphology.py`), `build_creature` builder, `Creature` instance interface with normalized `apply_actions` motor torque mapping, and preset `creatures/presets/hopper.json` (2-segment single-revolute-joint walker).
- Key design decision (and why): Defined a data-driven JSON format for creature morphologies so both the Gymnasium RL environment (Stage 07) and the Evolutionary population (Stage 11) share identical creature creation logic without duplicating code.
- Verification run (paste the actual command + result, not a description):
```
pytest tests/test_stage06.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D_physics_engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 3 items

tests/test_stage06.py::test_build_creature_from_hopper_preset PASSED     [ 33%]
tests/test_stage06.py::test_creature_action_application_and_simulation PASSED [ 66%]
tests/test_stage06.py::test_data_driven_preset_modification PASSED       [100%]

============================== 3 passed in 0.28s ==============================
```
- Anything that's a known rough edge / would do differently with more time: Joint angle limits (min/max angle stops) can be added to JointSpec as an extension when creating multi-limb creatures with anatomical constraints.

### Stage 07 — Gymnasium Environment Wrapper — 2026-07-22

- What was built: `CreatureEnv` class (`rl/env.py`) wrapping standard Gymnasium `Env` interface with continuous Box action space (`[-1.0, 1.0]` normalized torques), Box observation space (torso pose/velocity + relative joint angles/velocities + foot contact flags), frame-skipping, dynamic forward velocity reward, fall termination logic, and max episode step truncation.
- Key design decision (and why): Wrapped physics world stepping into frame_skip (4 physics steps per RL step) to lower the RL decision frequency relative to physics integration frequency, improving policy stability and learning efficiency.
- Verification run (paste the actual command + result, not a description):
```
pytest tests/test_stage07.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D_physics_engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 4 items

tests/test_stage07.py::test_environment_reset_and_observation_shape PASSED [ 25%]
tests/test_stage07.py::test_random_action_multi_episode_loop PASSED      [ 50%]
tests/test_stage07.py::test_dynamic_reward_computation PASSED            [ 75%]
tests/test_stage07.py::test_termination_on_fall PASSED                   [100%]

============================== 4 passed in 1.69s ==============================
```
- Anything that's a known rough edge / would do differently with more time: Standard Gymnasium `env.render()` visual mode can be added as a pass-through to Stage 05's `Renderer` for live episode playback during RL evaluation.

### Stage 08 — Environment Sanity Check — 2026-07-22

- What was built: Environment sanity audit runner (`scripts/sanity_check_env.py`) validating reward distributions, observation bounds (zero NaNs/Infs), episode termination reaching, zero-action baseline comparison, and automated Matplotlib reward distribution plotting (`scripts/sanity_check_rewards.png`).
- Key design decision (and why): Compared random-policy rollouts against a zero-action baseline to ensure non-trivial dynamic signal in rewards and observations before launching policy gradient optimization.
- Verification run (paste the actual command + result, not a description):
```
python -m scripts.sanity_check_env
Sanity Check Completed across 50 Random Episodes:
  Mean Return: -1.11 ± 6.93
  Mean Length: 23.0 steps
  Terminated Episodes (Fell): 50/50
  Zero-Action Mean Return: 22.57
  NaN/Inf Found: False

pytest tests/test_stage08.py -v
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.4.2, pluggy-1.5.0 -- C:\Anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\Kashish Gandhi\Desktop\2D_physics_engine
plugins: asyncio-1.4.0, anyio-4.10.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 1 item

tests/test_stage08.py::test_environment_sanity_check_execution PASSED    [100%]

======================== 1 passed, 2 warnings in 5.92s ========================
```
- Anything that's a known rough edge / would do differently with more time: Zero action policy lets creature stand still / fall gradually (giving positive survival reward), whereas random flailing causes fast tipping (triggering early termination), confirming that locomotion reward shaping in Stage 10 will have a clear learning signal to reward forward progress over falling.
