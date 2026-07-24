# Stage 35 — UI Integration Polish

**Phase 8. Depends on:** Stage 30, Stage 31, Stage 33, Stage 34.

## Goal

Make the three modes feel like one app, and audit the UI layer against the same rules the rest of the project follows.

## What to build / do

- Cross-mode navigation: switching modes cleanly tears down the previous mode's session server-side (stop training, end a match) rather than leaving orphaned background simulations running.
- Wire Stage 27's battle analytics and Stage 23's replay player fully into Competitive mode's post-match screen (if not already complete from Stage 34).
- **UI-layer anti-hardcoding audit**, extending Stage 14's audit to the new code: check `web/` for any endpoint or frontend code that returns canned/example data instead of real streamed state, any silently-caught WebSocket errors that would hide a disconnected or failed backend, and any loading/placeholder UI that could be mistaken for real data if the backend hasn't actually started yet (a clear "not running" state is fine; a fake-looking default chart is not).
- Basic error/empty states: what the UI shows before any mode has been started, and if the WebSocket disconnects mid-session — these should be honest ("disconnected", "no training running") rather than silently frozen on stale data.

## Definition of Done

- [ ] Switching from Gym to Competitive mid-training stops the training run server-side (verify no orphaned process/thread keeps consuming CPU after the switch)
- [ ] The UI-layer audit finds and fixes (or confirms the absence of) any of the anti-patterns listed above — document what was checked and found in `PROGRESS_LOG.md`, same as prior audits
- [ ] Manually disconnecting the backend (e.g. stopping the server) while the UI is open results in a visible "disconnected" state in the browser, not a frozen display of the last good frame with no indication anything is wrong
