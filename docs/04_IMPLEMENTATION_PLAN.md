# Implementation Plan — Stage Index

Work through stages in order within each phase — phases are also mostly sequential (Phase 2 needs Phase 1's creature format, Phase 3 needs Phase 2's robots, etc.). Load exactly one `stages/stage_NN_*.md` file at a time; don't pull the others into context.

No fixed calendar deadline — see `00_PROJECT_CONTEXT.md`. Phase 1's original "Day N" labels are a pace baseline from when this was a smaller-scoped sandbox project; Phases 2-7 aren't assigned to specific days but are sized the same way — each stage is roughly half a day to a day of focused, independently-verifiable work.

## Phase 1 — Physics & Locomotion Foundation

The physics engine plus a generic articulated creature trained to move, via RL and via evolution. Everything else in this project is built on top of this phase.

| # | Stage file | Builds | Depends on |
|---|-----------|--------|-------------|
| 01 | `stage_01_vector_math_rigidbody.md` | Vec2 math, RigidBody, integrator | — |
| 02 | `stage_02_shapes_collision_detection.md` | Shapes, AABB broad-phase, SAT narrow-phase | 01 |
| 03 | `stage_03_collision_resolution.md` | Impulse-based resolver (restitution, friction) | 02 |
| 04 | `stage_04_joints_constraints.md` | DistanceJoint, RevoluteJoint solver | 01 |
| 05 | `stage_05_world_loop_renderer.md` | World (fixed-timestep loop), pygame renderer | 03, 04 |
| 06 | `stage_06_creature_format_scene_test.md` | Creature morphology format + manual test scene | 05 |
| 07 | `stage_07_gym_environment_wrapper.md` | Gymnasium `CreatureEnv` | 06 |
| 08 | `stage_08_environment_sanity_check.md` | Random-policy sanity run | 07 |
| 09 | `stage_09_ppo_integration.md` | SB3 PPO training script, logging, checkpointing | 08 |
| 10 | `stage_10_reward_shaping_training.md` | Tuned reward, real training run, visible walking | 09 |
| 11 | `stage_11_nn_controller_population.md` | NNController, genome (de)serialization, Population | 06 |
| 12 | `stage_12_genetic_algorithm_loop.md` | GA loop (selection/crossover/mutation), fitness plot | 11 |
| 13 | `stage_13_integration_demo_capture.md` | Shared demo script, recorded clips | 10, 12 |
| 14 | `stage_14_final_verification_polish.md` | Anti-hardcoding audit, README polish, diagram | 13 |

## Phase 2 — Robot Component System

Robots as specialized creatures assembled from components with real physical tradeoffs.

| # | Stage file | Builds | Depends on |
|---|-----------|--------|-------------|
| 15 | `stage_15_robot_component_system.md` | Component types, `RobotSpec`, robot builder | 06 |
| 16 | `stage_16_robot_presets_scene_test.md` | Lightweight Fighter + Heavy Tank presets, manual test verifying real tradeoffs | 15 |

## Phase 3 — Combat Mechanics

Physics-driven damage, weapons, and a local 1v1 arena.

| # | Stage file | Builds | Depends on |
|---|-----------|--------|-------------|
| 17 | `stage_17_damage_durability.md` | Durability tracking, impulse-derived damage, component breaking | 16 |
| 18 | `stage_18_weapons.md` | Weapon components, contact-based damage multiplier | 17 |
| 19 | `stage_19_local_arena.md` | Local 1v1 arena, match loop, win conditions | 18 |

## Phase 4 — Combat Intelligence

RL and evolutionary training extended to combat, entirely local (self-play — no networking, see glossary).

| # | Stage file | Builds | Depends on |
|---|-----------|--------|-------------|
| 20 | `stage_20_combat_environment.md` | `CombatEnv`, opponent-relative observations | 19 |
| 21 | `stage_21_combat_rl_selfplay.md` | Self-play PPO training loop | 20 |
| 22 | `stage_22_combat_evolution.md` | Round-robin evolutionary combat fitness | 20 |

## Phase 5 — Local Battle Experience

Replay and spectator polish for the local matches Phase 3-4 produce.

| # | Stage file | Builds | Depends on |
|---|-----------|--------|-------------|
| 23 | `stage_23_replay_system.md` | Match recorder + playback (scrub, slow-motion) | 19 |
| 24 | `stage_24_spectator_visualization.md` | Health bars, damage overlays, slow-motion on big hits | 23 |

## Phase 6 — Sandbox & Experiment Modes

| # | Stage file | Builds | Depends on |
|---|-----------|--------|-------------|
| 25 | `stage_25_sandbox_mode.md` | Free-play scene control (spawn, gravity, terrain) | 16 |
| 26 | `stage_26_experiment_mode.md` | Structured experiment runner + report | 25 |

## Phase 7 — Robot Analytics

| # | Stage file | Builds | Depends on |
|---|-----------|--------|-------------|
| 27 | `stage_27_battle_analytics.md` | Post-battle report from real replay data | 23 |

## Phase 8 — UI Dashboard

A local web dashboard over the existing simulation — Playground, Gym, and Competitive modes. Flat terrain only; see Phase 9.

| # | Stage file | Builds | Depends on |
|---|-----------|--------|-------------|
| 28 | `stage_28_dashboard_backend.md` | FastAPI + WebSocket server, state streaming, control endpoints | 06, 19 |
| 29 | `stage_29_frontend_shell_renderer.md` | Mode shell, WebSocket client, canvas renderer for articulated bodies | 28 |
| 30 | `stage_30_playground_ui.md` | Playground mode — spawn, gravity, terrain reset | 29, 25 |
| 31 | `stage_31_gym_ui.md` | Gym mode — live population grid (GA genomes / PPO parallel rollouts), promote-to-roster | 29, 10, 12 |
| 32 | `stage_32_fighter_archetype_presets.md` | Named fighter presets (Boxer, Grappler, etc.) on the existing component system | 16 |
| 33 | `stage_33_fighter_roster_selection.md` | Persistent roster of trained fighters, fed by Gym, read by Competitive | 31, 32 |
| 34 | `stage_34_competitive_ui.md` | Competitive mode — pick fighters from the roster, live viewport, autonomous policies only | 29, 33, 20 |
| 35 | `stage_35_ui_integration_polish.md` | Replay/battle-report hookup, cross-mode nav, anti-hardcoding audit for the UI layer | 30, 31, 34 |
| 36 | `stage_36_llm_integration_foundation.md` | Shared Gemini API client, safe key handling, structured-output validation | 28 |
| 37 | `stage_37_natural_language_training_prompts.md` | Text-box training prompts → real, inspectable reward/fitness config | 36, 31, 10, 12 |
| 38 | `stage_38_live_match_commentary.md` | Async, throttled, clearly-labeled live match commentary | 36, 34, 20 |

## Phase 9 — Terrain Variety (planned next, not yet staged)

Hills, gaps, and stairs for Gym mode. Deliberately sequenced after Phase 8 per an explicit decision — needs real physics work (varied terrain geometry, spawn logic that works across terrain types) before it gets stage files. Don't start this from a UI stage's momentum; it gets its own stage docs when picked up.

## Not staged — see `05_FUTURE_VISION.md`

Real networked multiplayer, matchmaking, ranked ladders, cross-machine tournaments, robot marketplace, community rankings.

## Status tracking

Mark stages done only after actually running that stage's verification — not because code was generated for it.

## If you need to prioritize

The resume-critical core is Phase 1 + Phase 2 + Phase 3 + at least one of Phase 4's two tracks (RL or evolution — doesn't need both to be a complete story). Phases 5-7 are genuinely valuable polish but are safe to trim first if time runs short — a working local combat match between trained fighters is a complete, defensible project even without replay/sandbox/analytics.
