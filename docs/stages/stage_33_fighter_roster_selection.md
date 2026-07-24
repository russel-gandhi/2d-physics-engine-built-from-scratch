# Stage 33 — Fighter Roster & Selection

**Phase 8. Depends on:** Stage 31 (Gym UI producing trained fighters), Stage 32 (archetype presets).

## Goal

"Keep adding fighters, pick the best one" as a real, persistent feature — every promoted training result becomes a saved, named fighter that stays available across sessions, browsable when setting up a Competitive match.

## What to build

`web/fighter_roster.py`
- A simple persistent store (a JSON file or SQLite — no need for a real database at this scope) of saved fighters. Each entry: a name (auto-suggested from the preset/archetype + a timestamp, editable), which archetype preset it's built on (Stage 32), which algorithm trained it (PPO or GA), a pointer to the real artifact (checkpoint `.zip` path or genome `.npy` path), and real stats captured at save time (best reward/fitness, timesteps or generations trained).
- `save_fighter(...)`, `list_fighters()`, `delete_fighter(id)` — straightforward CRUD over the store.

`web/frontend/roster.js`
- A browsable roster view: cards per saved fighter showing its name, archetype, algorithm, and stats. A "promote" entry point from Stage 31's Gym UI lands here. Fighters can be deleted (with the underlying checkpoint/genome file left alone unless explicitly asked to delete the file too — don't silently destroy training artifacts).
- This is what Stage 34's Competitive mode match setup reads from instead of raw file browsing — picking a fighter for a match means picking a roster entry, not hunting for a `.zip` path.

## Definition of Done

- [ ] Promoting a fighter from a real Gym training run (either algorithm) creates a real roster entry pointing at a real, loadable checkpoint or genome file — verify by loading it back and running it in `combat/combat_env.py`
- [ ] The roster persists across a backend restart (it's reading from the real saved file/DB, not an in-memory list that resets)
- [ ] Roster stats shown (best reward/fitness, training amount) match what was actually logged during that fighter's training run — not re-derived or guessed after the fact
- [ ] Deleting a roster entry removes it from the list without requiring the underlying artifact file to also be deleted — the two are related but separate operations
