# Implementation Plan — Stage Index

Work through stages in order — each depends on the ones listed. Load exactly one `stages/stage_NN_*.md` file at a time; don't pull the others into context.

| # | Day | Stage file | Builds | Depends on |
|---|-----|-----------|--------|-------------|
| 01 | 1 | `stage_01_vector_math_rigidbody.md` | Vec2 math, RigidBody, integrator | — |
| 02 | 1 | `stage_02_shapes_collision_detection.md` | Shapes, AABB broad-phase, SAT narrow-phase | 01 |
| 03 | 2 | `stage_03_collision_resolution.md` | Impulse-based resolver (restitution, friction) | 02 |
| 04 | 2 | `stage_04_joints_constraints.md` | DistanceJoint, RevoluteJoint solver | 01 |
| 05 | 3 | `stage_05_world_loop_renderer.md` | World (fixed-timestep loop), pygame renderer | 03, 04 |
| 06 | 3 | `stage_06_creature_format_scene_test.md` | Creature morphology format + manual test scene | 05 |
| 07 | 4 | `stage_07_gym_environment_wrapper.md` | Gymnasium `CreatureEnv` | 06 |
| 08 | 4 | `stage_08_environment_sanity_check.md` | Random-policy sanity run, obs/action/reward verified sane | 07 |
| 09 | 5 | `stage_09_ppo_integration.md` | SB3 PPO training script, logging, checkpointing | 08 |
| 10 | 5 | `stage_10_reward_shaping_training.md` | Tuned reward, real training run, visible walking | 09 |
| 11 | 6 | `stage_11_nn_controller_population.md` | NNController (numpy MLP), genome (de)serialization, Population | 06 |
| 12 | 6 | `stage_12_genetic_algorithm_loop.md` | GA loop (selection/crossover/mutation), fitness plot | 11 |
| 13 | 7 | `stage_13_integration_demo_capture.md` | Shared demo script (RL policy + evolved agents), recorded clips | 10, 12 |
| 14 | 7 | `stage_14_final_verification_polish.md` | Anti-hardcoding audit, README polish, architecture diagram | 13 |

## Status tracking

Copy this table into your own notes or a project board and mark stages done as you verify them — per that stage's Definition of Done. Mark a stage done because you ran its verification and it passed, not because code was generated for it.

## If you're running low on time by day 6-7

Priority order to protect if the schedule slips: **05 → 07 → 09/10 (working RL walker) → 11/12 (working GA loop) → 13 → 14.** A working RL walker on a simple hopper plus *some* evolutionary result is a complete, defensible project even if stage 13's full integration gets trimmed. Do not skip ahead to stage 13/14 polish while an earlier stage is still faking its output — an honest, smaller demo beats a fake, complete-looking one, both ethically and for actually surviving interview questions.
