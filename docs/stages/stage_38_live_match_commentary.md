# Stage 38 — Live Match Commentary

**Phase 8. Depends on:** Stage 36 (LLM foundation), Stage 34 (Competitive UI), Stage 20 (combat environment).

## Goal

A live "what's likely driving this" readout during matches — genuinely useful and fun to watch, but honestly framed as AI commentary interpreting real telemetry, not the robot's literal internal reasoning (see `02_AGENT_RULES.md` rule 8 — PPO/GA policies have no language-based cognition).

## What to build

`web/server.py` / a background task
- Every few seconds of match time (not every physics step — an LLM call per step would badly lag a real-time match, and would be needlessly expensive), gather real telemetry since the last commentary call: both robots' positions/distance, recent damage events, current durability, recent actions taken. Send this to `llm_client.generate_text(...)` asking for a short (1-2 sentence) caption.
- Run this as a background/async task that does not block the match simulation — the physics and the stream to the frontend continue at full real-time speed regardless of whether a commentary call is in flight. The commentary panel simply updates whenever the next caption arrives, a beat behind the live action, same as real sports commentary lags the live play.
- Throttle sensibly (e.g. one call every 2-3 seconds, or triggered on a significant event like a big damage hit rather than a fixed timer alone) to keep this affordable and not spammy.

`web/frontend/competitive.js` (extend)
- A commentary panel next to the event log, clearly labeled (e.g. a small "AI commentary" tag) so it reads as interpretation, not a claim about the robot's actual thought process.
- If a commentary call fails or times out, show "commentary unavailable" rather than freezing on stale text or fabricating a caption client-side.

## Definition of Done

- [ ] During a real match, the commentary panel updates with real Gemini-generated captions tied to what's actually happening (paste a few real captions alongside the match state that produced them, and confirm they're plausible given that state)
- [ ] The match's actual simulation speed and the data streamed to Stage 29's renderer are unaffected by commentary latency — verify by watching the match run at normal speed even if a commentary call is slow
- [ ] The "AI commentary" label is visibly present in the UI, not something that could be mistaken for the robot's actual decision process
- [ ] Deliberately breaking the API call (bad key, network off) results in a visible "commentary unavailable" state, not a frozen caption or a crash of the match view
