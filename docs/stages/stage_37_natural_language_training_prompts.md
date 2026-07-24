# Stage 37 — Natural Language Training Prompts

**Phase 8. Depends on:** Stage 36 (LLM foundation), Stage 31 (Gym UI), Stage 10 (PPO reward shaping), Stage 12 (GA fitness).

## Goal

A text box where a description like "train like Mike Tyson — aggressive boxer" becomes a real, visible set of reward/fitness weights that training actually optimizes against — not a vibe, an inspectable config.

## What to build

`web/frontend/gym.js` (extend)
- A text input in Gym mode: "Describe how this fighter should train." Submitting it calls a new backend endpoint before training starts.

`web/server.py` (extend)
- Endpoint that sends the description to `llm_client.generate_structured(...)` with a schema covering the real weight terms `rl/env.py` (or `combat/combat_env.py` for combat training) and `evolution/ga.py`'s fitness function already support — e.g. `aggression` (weight on damage dealt / forward engagement), `caution` (weight on avoiding damage / survival), `mobility` (weight on movement efficiency), `stamina_conservation` (weight on control-effort penalty). Do not invent new reward terms the environment doesn't actually compute — the schema must map onto real, already-implemented signals from Stage 10/17/21/22.
- The returned config is shown to the user before training starts (e.g. "Interpreted as: aggression 0.9, mobility 0.4, caution 0.2 — start training?") with the option to adjust values manually before confirming. Only once confirmed does it get passed into the real reward/fitness function as actual weight multipliers.

## Definition of Done

- [ ] Submitting a real description produces a real Gemini-generated config (paste the actual API response), shown to the user, not silently applied without visibility
- [ ] Starting training with that config measurably changes training behavior compared to default weights — e.g. an "aggressive" config should show higher `damage_dealt` in the reward breakdown during training than a "cautious" config, verified from real logged reward-component values, not assumed
- [ ] The user-facing preview accurately reflects the exact weights actually passed into the reward/fitness function — no drift between what's shown and what's used
- [ ] A nonsense or empty description doesn't crash training — it should fall back to a clearly-labeled default config (not a silently different unlabeled one) and say so in the UI
