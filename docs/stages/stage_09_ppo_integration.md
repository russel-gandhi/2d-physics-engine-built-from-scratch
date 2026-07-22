# Stage 09 — PPO Integration

**Day 5, first half. Depends on:** Stage 08 (sanity-checked environment).

## Goal

Wire the verified environment into `stable-baselines3` and get a real (if not yet good) training run end-to-end.

## What to build

`rl/train_ppo.py`
- Instantiate `CreatureEnv` (wrap with `gymnasium`'s vectorized env if time allows, for faster training — optional, not required for a working v1)
- `model = PPO("MlpPolicy", env, verbose=1, tensorboard_log=...)` with a small policy network (this is a simple environment — default SB3 MLP sizes are more than enough)
- `model.learn(total_timesteps=...)` — pick an initial budget you can afford time-wise (e.g. something small enough to finish in minutes, to confirm the pipeline works, before committing to a longer run in stage 10)
- Checkpointing: save the model periodically (`model.save(...)`) so a long run isn't lost, and so stage 10/13 can load a specific checkpoint to compare progress
- Logging: SB3's built-in tensorboard logging is enough — don't build a custom logger

## Definition of Done

- [ ] A short training run (small `total_timesteps`, just to prove the pipeline) completes without crashing and produces a saved model file
- [ ] Loading the saved model and running it in the environment (`model.predict(obs)`) produces actions and a real episode — confirms it runs, not that training converged yet (that's stage 10's job)
- [ ] Tensorboard log (or equivalent logged reward values) shows real numbers pulled from actual training, not placeholder/example values
