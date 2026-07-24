# Stage 32 — Fighter Archetype Presets

**Phase 8. Depends on:** Stage 16 (robot presets).

## Goal

Give the robot preset library fighting-game-style personality — "Boxer", "Grappler", and similar — as flavor and genuine build variety on top of the existing component system from Phase 2, not a new combat mechanic.

## What to build

`robots/presets/`
- Add 2-3 new presets alongside the existing Lightweight Fighter / Heavy Tank, each a real, distinct combination of existing component types — e.g. a "Boxer" preset favoring fast, high-torque arm/weapon limbs with lighter armor (fast strikes, lower durability), a "Grappler" preset favoring stronger limb joints and higher mass for control-heavy play (slower, tankier, better at pushing/throwing via real physics rather than a scripted grab move). Every stat difference must come from real component values (mass, torque, durability) that then produce real different simulated behavior — same rule as Stage 16's tradeoff test.
- Add a small metadata field per preset (display name, one-line flavor description, a UI color tag) that `web/frontend/competitive.js` (Stage 33) reads to label fighters — this is presentation metadata only, it has no effect on physics or combat.

## Definition of Done

- [ ] Each new preset loads and simulates correctly, same as Stage 16's checks
- [ ] Under a comparable test (same style as Stage 16's tradeoff test), the new presets show measurably different real behavior from each other and from the existing two (e.g. Boxer's strikes land with higher impulse per Stage 17's damage system; Grappler resists being pushed more than Boxer does) — computed from an actual run, not asserted from the preset file
- [ ] Preset metadata (name/description/color) is data, not hardcoded into UI logic — adding a fourth archetype preset file should make it appear in the UI without a frontend code change
