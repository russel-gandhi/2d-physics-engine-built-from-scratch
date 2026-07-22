# Architecture

## Module map

```
physics_rl_sandbox/
├── physics/
│   ├── vec2.py         # Vector2 math (add, sub, dot, cross, normalize, rotate)
│   ├── body.py          # RigidBody: mass, position, velocity, angle, angular velocity, forces/torques
│   ├── shapes.py         # Circle, Polygon (AABB computation lives here too)
│   ├── collision.py      # Broad-phase (AABB) + narrow-phase (SAT / circle tests) -> Contact objects
│   ├── resolver.py       # Impulse-based collision resolution (restitution + friction)
│   ├── joints.py         # DistanceJoint, RevoluteJoint (constraint solver)
│   └── world.py          # World: owns bodies/joints, fixed-timestep step(), gravity
├── render/
│   └── renderer.py       # pygame draw calls for bodies, joints, debug overlays
├── creatures/
│   ├── morphology.py     # Creature definition (segments + joints + motor limits), loader
│   └── presets/           # JSON/py creature definitions (e.g. hopper.json, walker.json)
├── rl/
│   ├── env.py             # Gymnasium Env wrapping World + one creature
│   └── train_ppo.py       # SB3 PPO training entrypoint, checkpointing, logging
├── evolution/
│   ├── nn_controller.py   # Tiny MLP forward pass (numpy only), genome <-> weights (de)serialization
│   ├── population.py      # Population init, fitness evaluation (runs World per genome)
│   └── ga.py               # Selection, crossover, mutation, generation loop
├── scripts/
│   ├── demo_walker.py      # Load a trained RL policy, render it live
│   └── demo_evolution.py   # Run/replay the GA result, render best-of-generation, plot fitness curve
├── tests/
│   └── ...                 # unit tests per physics/rl/evolution module — see each stage file for required cases
└── docs/                    # this folder
```

## Data flow

1. `World.step(dt)` is the only place time advances: apply forces → integrate velocities/positions → detect collisions → resolve collisions → solve joints. Everything else (rendering, RL, GA) calls `World.step()` and reads state after — nothing else mutates physics state directly.
2. `rl/env.py` wraps one `World` + one creature: `reset()` rebuilds the world, `step(action)` applies motor torques from `action`, calls `World.step()`, returns `(observation, reward, terminated, truncated, info)`.
3. `evolution/population.py` runs many short-lived `World` instances (one per genome per generation), each driven by an `NNController` instead of an RL policy — the physics core doesn't know or care which kind of "brain" is driving it.

## Key interfaces (do not change signatures without updating this file)

- `RigidBody.apply_force(force: Vec2, point: Vec2 | None)`, `RigidBody.apply_torque(t: float)`
- `World.step(dt: float) -> None`
- `World.add_body(body: RigidBody) -> None`, `World.add_joint(joint: Joint) -> None`
- `CreatureEnv(gymnasium.Env)` — standard `reset()` / `step()` / `observation_space` / `action_space`
- `NNController.act(observation: np.ndarray) -> np.ndarray` — same input/output shape as what `CreatureEnv` expects from an RL policy, so a trained PPO policy and an evolved `NNController` are interchangeable when driving a creature in `scripts/demo_*.py`

## Tech stack

| Purpose | Library | Notes |
|---|---|---|
| Physics math | `numpy` (default) | the simulation core itself must be hand-built — no physics engine libraries (pymunk/Box2D) standing in for it |
| Rendering | `pygame` | simple 2D primitives only |
| RL env API | `gymnasium` | standard `Env` interface |
| RL algorithm | `stable-baselines3` (PPO) | do not hand-roll PPO — see non-goals in `00_PROJECT_CONTEXT.md` |
| Evolution NN | `numpy` or `torch` | small MLP, hand-rolled forward pass either way (no autograd needed — weights update via the GA, not gradients) |
| Plots | `matplotlib` | reward curves, fitness-over-generations |

Library choice elsewhere is open — add `scipy` or anything else that fits, as long as you understand what it's doing. Pin exact versions in `requirements.txt` once installed in a working environment (`pip freeze`), rather than guessing version numbers here.
