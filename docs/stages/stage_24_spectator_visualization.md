# Stage 24 — Spectator Visualization Polish

**Phase 5. Depends on:** Stage 23.

## Goal

Make matches (live or replayed) actually watchable and legible — this is what turns "a physics sim with numbers" into something demo-worthy for a resume/portfolio.

## What to build

`render/renderer.py` (extend)
- Health/durability bars per robot (and optionally per major component), drawn above or beside each robot, updated from real current durability values
- Damage event flashes/overlays (a brief visual indicator when a component takes a hit, sized or colored by damage amount)
- Slow-motion trigger on significant events (e.g. auto-slow-motion for a few frames when a chassis-ending hit lands) — this can be built into `replay/player.py`'s playback controls rather than the live renderer, whichever is simpler given what's already built
- Optional debug overlay toggle (already exists from stage 05) extended to show contact points/impulse magnitudes live, useful for verifying stage 17-18's damage system is behaving as expected while building

## Definition of Done

- [ ] Health bars visibly and correctly track real durability values through a full match (verify by comparing the displayed value to the logged value at a few points)
- [ ] Damage overlays appear only on real logged damage events, not on every contact regardless of whether damage was actually dealt (below-threshold contacts per stage 17 should not trigger a damage flash)
- [ ] A recorded clip of a full match with this polish applied looks like something you'd actually want to show someone — this is a subjective check, but worth doing before moving on
