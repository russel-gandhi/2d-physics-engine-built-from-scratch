# Stage 29 — Frontend Shell & Renderer

**Phase 8. Depends on:** Stage 28.

## Goal

The mode-switching shell and the one canvas renderer every mode reuses — get this right once so Playground/Gym/Competitive don't each reinvent drawing.

## What to build

`web/frontend/index.html` + `web/frontend/app.js`
- A simple layout: a mode nav (Playground / Gym / Competitive) and a main content area that swaps per mode. No framework needed — plain DOM is enough at this scope.
- WebSocket client connecting to `/ws/state`, reconnecting on drop, dispatching incoming state to whichever mode module is currently active.

`web/frontend/renderer.js` (shared by all three mode files)
- `drawBody(ctx, bodyState)`: draws a rigid body from the encoded state — circle for a `Circle` shape, polygon for a `Polygon` shape, using the actual position/angle from the stream (no client-side physics or interpolation guessing beyond simple linear smoothing between ticks if the stream rate is lower than the display rate).
- `drawJoints(ctx, jointStates)`: draws limb connections as lines between the two body anchor points, and a small circle at each joint — this is what gives robots the articulated look (matching the reference screenshot's joint-and-limb style), and it's driven entirely by real joint anchor positions, not a separately-authored skeleton.

## Definition of Done

- [ ] Loading `index.html` while the backend is streaming a Playground scene shows real moving shapes on canvas, matching what's actually happening server-side (spot check against server-side logged positions at a few points)
- [ ] Switching modes in the nav swaps the visible panel without breaking the WebSocket connection
- [ ] A robot with joints (from any existing preset) renders with visible joint circles and limb lines connecting them, not just disconnected body outlines
