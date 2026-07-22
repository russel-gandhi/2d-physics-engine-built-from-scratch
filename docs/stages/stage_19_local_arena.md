# Stage 19 — Local 1v1 Arena

**Phase 3. Depends on:** Stage 18.

## Goal

Put two robots in the same simulation with real win/loss conditions — the first fully playable (if not yet intelligent) combat match.

## What to build

`combat/arena.py`
- `Arena(robot_a_spec, robot_b_spec)`: builds both robots into one `World` at opposite starting positions.
- `step(action_a, action_b)`: applies each robot's motor torques from its action, steps the shared `World` once, checks win conditions.
- Win conditions: a robot's `Chassis` component reaching 0 durability ends the match (the other robot wins); optionally a time limit, with the higher-total-remaining-durability robot winning on timeout.
- For now, actions can come from anywhere — manual/scripted for testing, since Phase 4 is what adds real intelligence. Don't couple `Arena` tightly to any one controller type; it just needs `(action_a, action_b) -> (obs_a, obs_b, done, info)` roughly, matching the shape `combat_env.py` will wrap in stage 20.

## Definition of Done

- [ ] Two robots placed in an `Arena`, driven by simple scripted/manual actions (e.g. move-forward-and-swing), run a full match through the renderer and it ends correctly on a chassis-destroyed condition
- [ ] Timeout win condition tested explicitly (run a match where neither chassis is destroyed before the time limit, confirm the higher-durability robot is declared the winner based on real logged durability values)
- [ ] No part of the match loop short-circuits to a scripted outcome — the winner is always determined by the actual simulated state at the end
