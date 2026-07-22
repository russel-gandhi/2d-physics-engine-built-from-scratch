# Stage 23 — Replay System

**Phase 5. Depends on:** Stage 19 (a real arena/match loop to record).

## Goal

Record real matches and play them back — the foundation for both spectator mode and analytics (stage 27).

## What to build

`replay/recorder.py`
- `MatchRecorder`: hooks into `combat/arena.py`'s `step()` (or wraps it), logging per-step: both robots' body positions/angles, damage events (which component, how much, from what impulse), and the eventual match result. Write to a simple format (JSON lines is fine — no need for a custom binary format).

`replay/player.py`
- Reads a recorded match file and drives the Phase 1 renderer frame-by-frame from the logged data, with playback controls: pause, scrub to a specific step, slow-motion (render multiple real frames per logged step, interpolating position/angle between them if you want smoothness — linear interpolation between consecutive logged states is enough, don't over-engineer this).

## Definition of Done

- [ ] Recording a real match (from stage 19/20's arena, even with simple scripted actions) produces a replay file
- [ ] Playing that file back through `replay/player.py` visually matches what happened in the live match (same collisions, same damage events, same outcome) — confirm by comparing a live run and its replay side by side once
- [ ] Slow-motion playback doesn't change the underlying data, only how it's rendered — the replay file itself is the single source of truth
