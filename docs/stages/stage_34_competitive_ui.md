# Stage 34 — Competitive Mode UI

**Phase 8. Depends on:** Stage 29, Stage 32, Stage 33 (fighter roster), Stage 20 (combat environment).

## Goal

Local 1v1 matches where both robots fight using whatever they learned in Gym mode — never manual or scripted attack input from the UI.

## What to build

`web/frontend/competitive.js`
- Match setup: pick two fighters from Stage 33's roster (or a basic built-in heuristic opponent if nothing has been trained yet, matching Stage 21's bootstrap approach) — selection is by roster entry, not raw checkpoint file path. There is no control here that lets a user directly command an attack or movement during the match — the UI can only start/pause/reset the match and choose which trained brain drives each side.
- Live match view built on Stage 29's renderer: health bars per robot (real durability from the stream), the arena viewport, and a live event log of real damage events as they're streamed (reuse the same event data Stage 23's replay recorder captures).
- Post-match: buttons to view the Stage 27 battle report and to load the match into Stage 23's replay player for scrubbing/slow-motion.

## Definition of Done

- [ ] Starting a match with two selected presets and brains runs a real `combat/arena.py` match server-side and streams real outcomes — confirm the winner and final health values match what running the same matchup directly through `combat/arena.py` would produce
- [ ] Grep/review confirms there is no code path in `competitive.js` or the corresponding backend endpoint that accepts a manual attack/move command during an active match — the only per-match inputs are pre-match setup (preset + brain selection) and playback controls
- [ ] The event log entries shown correspond to real logged damage events from Stage 17's impulse-derived damage system, not synthesized commentary
