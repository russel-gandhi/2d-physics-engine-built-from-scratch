# Architecture

## Module map

```
physics_rl_sandbox/
├── physics/              # Phase 1 — vector math, rigid bodies, collision, joints, world loop
│   ├── vec2.py
│   ├── body.py
│   ├── shapes.py
│   ├── collision.py
│   ├── resolver.py
│   ├── joints.py
│   └── world.py
├── render/                # Phase 1, extended Phase 5 — pygame rendering + combat/spectator overlays
│   └── renderer.py
├── creatures/              # Phase 1 — generic data-driven articulated-body format
│   ├── morphology.py
│   └── presets/
├── rl/                     # Phase 1 locomotion env, extended Phase 4 for combat
│   ├── env.py
│   └── train_ppo.py
├── evolution/               # Phase 1 locomotion GA, extended Phase 4 for combat
│   ├── nn_controller.py
│   ├── population.py
│   └── ga.py
├── robots/                  # Phase 2 — robot component system, built on top of creatures/
│   ├── components.py         # component types: chassis, armor, limb, wheel, sensor, motor, weapon, energy
│   ├── robot_spec.py          # RobotSpec (extends CreatureSpec) + robot builder
│   └── presets/                # lightweight_fighter.json, heavy_tank.json
├── combat/                    # Phase 3-4 — damage, weapons, arena, combat RL environment
│   ├── damage.py                # durability tracking, component breaking, physics-derived damage
│   ├── weapons.py                # weapon components, contact-based damage dealing
│   ├── arena.py                   # local 1v1 arena: two robots in one World, win conditions
│   └── combat_env.py              # CombatEnv (extends CreatureEnv) — two-agent env, self-play support
├── replay/                     # Phase 5 — match recording and playback
│   ├── recorder.py
│   └── player.py
├── sandbox/                     # Phase 6 — free-play and structured experiments
│   ├── sandbox_mode.py
│   └── experiment.py
├── analytics/                    # Phase 7 — post-battle reports
│   └── battle_report.py
├── web/                            # Phase 8 — local dashboard: backend + frontend
│   ├── server.py                     # FastAPI app + WebSocket state streaming, mode/control endpoints
│   ├── state_encoder.py               # World/Arena state -> JSON per tick (positions, angles, hp, rewards)
│   ├── fighter_roster.py               # persistent store of trained fighters (checkpoint/genome + stats)
│   ├── llm_client.py                    # shared Gemini API client — structured config parsing + commentary
│   └── frontend/                       # HTML/CSS/JS — mode shell, canvas renderer, per-mode panels
│       ├── index.html
│       ├── app.js                        # WebSocket client, mode router, canvas draw loop
│       ├── renderer.js                    # shared articulated-body drawing, used by all modes
│       ├── playground.js
│       ├── gym.js                          # includes the live population grid + training prompt box
│       ├── roster.js
│       └── competitive.js                  # includes the AI commentary panel
├── scripts/                       # entry points across all phases
├── tests/                           # unit tests per module — see each stage file for required cases
└── docs/                             # this folder
```

## Data flow

**Phase 1 (unchanged):** `World.step(dt)` is the only place time advances: apply forces → integrate → detect collisions → resolve collisions → solve joints. `rl/env.py` and `evolution/population.py` both drive a `World` + creature without touching physics internals directly.

**Phase 2-3 (robots + combat):**
- `robots/robot_spec.py` builds on `creatures/morphology.py`: a `RobotSpec` is a `CreatureSpec` where segments/joints are tagged with component types (armor, weapon, sensor, etc.) carrying combat-relevant properties (durability, damage multiplier) alongside the physical properties (mass, size) creatures already have.
- `combat/damage.py` hooks into `physics/resolver.py`'s contact resolution: when a contact's impulse magnitude between two robots' components exceeds a threshold, `damage.py` reduces the struck component's durability proportional to that real impulse (weapon components apply a multiplier). No damage is ever assigned outside of an actual computed contact — this is what "combat emerges from physics" means in practice.
- `combat/arena.py` owns one `World` with two robots in it, runs the match loop (get each robot's action from its controller → apply → `world.step()` → check damage/win conditions), and is what both the RL and GA layers, and the replay recorder, plug into.

**Phase 4 (combat intelligence):**
- `combat/combat_env.py` wraps `combat/arena.py` in the same `reset()/step()` shape as `rl/env.py`'s `CreatureEnv`, but the observation now includes the opponent's state (position, velocity, damage) and the environment supports **self-play**: both robots can be driven by policies (the same policy, different snapshots of it, or a fixed heuristic opponent) running in the same local simulation — no networking involved (see glossary).
- `evolution/ga.py`'s fitness function is extended for combat: instead of one robot's solo distance, `Population.evaluate` can run a small local round-robin between genomes and score on damage dealt / survival / victories.

**Phase 5 (replay/spectator):**
- `replay/recorder.py` subscribes to the arena loop and logs body states + damage events per step to a file. `replay/player.py` reads that file back and drives the Phase 1 renderer exactly like a live match would, so playback is a real re-render of real logged data, not a separate animation system.

**Phase 6 (sandbox/experiment):**
- `sandbox/sandbox_mode.py` is a thin interactive layer over `World` (spawn/adjust live). `sandbox/experiment.py` takes a structured config (robot + environment parameters, e.g. a gravity multiplier), runs a real simulation, and emits a report — matching the "Experiment: High Gravity Test" format from the original concept doc, computed from the actual run.

**Phase 7 (analytics):**
- `analytics/battle_report.py` reads a `replay/recorder.py` log after a match and computes real statistics from it (damage %, movement efficiency, successful attack count) — plus simple rule-based weakness flags (e.g. "slow recovery" if time-to-right-itself-after-a-knockdown exceeds a threshold in the log). These flags are derived from logged numbers, not invented.

**Phase 8 (UI dashboard):**
- `web/server.py` doesn't run its own simulation logic — it drives the existing `sandbox/sandbox_mode.py` (Playground), `rl/train_ppo.py` / `evolution/ga.py` (Gym), and `combat/arena.py` / `combat_env.py` (Competitive) exactly as those modules already work, and streams their real state over WebSocket every tick via `web/state_encoder.py`. The browser never computes physics or decides an outcome — it only renders what the backend sends and forwards user actions (spawn, start training, start match) back as requests. In Competitive mode, robot actions come only from a loaded policy (PPO checkpoint or evolved `NNController`) via `combat_env.py` — the UI has no manual attack controls, matching "robots choose their own strategy."
- `web/llm_client.py` is called in exactly two places, both outside the real-time simulation loop: once at the start of a Gym training run (Stage 37, translating a text prompt into real reward/fitness weights that then get used for actual training) and periodically (every few seconds, async, non-blocking) during a Competitive match (Stage 38, generating commentary from real telemetry). The LLM never decides a robot's action — that always comes from the trained policy/genome, matching rule 8 in `02_AGENT_RULES.md`.

## Key interfaces (do not change signatures without updating this file)

- `RigidBody.apply_force(force, point)`, `World.step(dt)`, `CreatureEnv` — unchanged from Phase 1, see stage 01-14 files for exact signatures.
- `RobotSpec` — extends `CreatureSpec`; `build_robot(spec, world, position) -> Robot` mirrors `build_creature`.
- `CombatEnv(gymnasium.Env)` — same `reset()/step()` shape as `CreatureEnv`, two-agent.
- `NNController.act(observation) -> action` — unchanged; combat controllers use the same interface as locomotion controllers.

## Tech stack

| Purpose | Library | Notes |
|---|---|---|
| Physics math | `numpy` (default) | the simulation core itself must be hand-built — no physics engine libraries (pymunk/Box2D) standing in for it |
| Rendering | `pygame` | simple 2D primitives, extended with damage/health overlays in Phase 5 |
| RL env API | `gymnasium` | standard `Env` interface, including `CombatEnv` |
| RL algorithm | `stable-baselines3` (PPO) | do not hand-roll PPO |
| Evolution NN | `numpy` or `torch` | hand-rolled forward pass either way |
| Replay storage | stdlib (`json` or `pickle`) | no new dependency needed — a log of per-step state is enough |
| Plots | `matplotlib` | reward/fitness curves, battle stats |
| UI backend | `FastAPI` + `uvicorn`, WebSocket | streams real simulation state; no physics/decision logic lives here |
| UI frontend | plain HTML/CSS/JS, `<canvas>` | draws robots from streamed joint positions — no separate rendering logic that could drift from the real simulation |
| LLM | Gemini API | text-prompt-to-reward-config (Stage 37) and live match commentary (Stage 38) only — never in the physics/action loop, see `02_AGENT_RULES.md` rule 8 |

Library choice elsewhere is open — add `scipy` or anything else that fits, as long as you understand what it's doing.
