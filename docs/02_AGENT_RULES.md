# Agent Rules — Non-Negotiable

These apply to every stage, no exceptions. If a stage file's instructions ever conflict with these rules, these rules win — stop and flag the conflict rather than silently picking one.

## Hard rules (automatic rejection if violated)

1. **No hardcoded or faked results.** Every number shown to the user (a reward curve, a fitness value, a "physics is stable" claim) must come from an actual computation that actually ran. Never write a function that returns a plausible-looking constant instead of computing the real thing, even temporarily "to get the demo working."
2. **No silently-swallowed failures.** Don't wrap code in try/except that hides a crash and prints a fake success message. If something fails, it should fail loudly (raise, log clearly) so it gets fixed, not papered over.
3. **No mocked physics.** Collision, integration, and joint solving must be real — no shortcuts like snapping a body to "look right" instead of resolving the actual collision, no faking a joint by teleporting a body to where it should be.
4. **No pre-recorded "demo" data presented as live output.** If a video/gif is shown as "the trained agent walking," it must be a recording of an actual run of the actual trained policy — not a hand-scripted animation standing in for it.
5. **Every stage ships with a way to verify it's real, and that verification is actually run** before the stage is marked done — see "Definition of Done" below.
6. **No stand-in networking.** Local 1v1 battles (two robots in the same simulation on one machine) are real and in scope. Real networked multiplayer is explicitly out of scope for now (see `05_FUTURE_VISION.md`) — don't build a fake "multiplayer" that's secretly just local play relabeled, and don't build partial networking scaffolding that doesn't actually work end-to-end. If asked to work on multiplayer, stop and check with the user first — it isn't part of the staged plan.

## Definition of Done (apply this checklist at the end of every stage)

- [ ] Code runs without errors on a clean environment (`pip install -r requirements.txt` + run)
- [ ] The stage's specified unit tests / verification steps pass, and you actually ran them (paste the real output — don't describe what it "should" show)
- [ ] No `TODO` / bare `pass` / stub functions left in code paths this stage claims to implement
- [ ] New public functions/classes have a one-line docstring explaining what they do
- [ ] `PROGRESS_LOG.md` has a new entry for this stage (template is in that file)

## Coding conventions

- Python 3.10+, type hints on public function signatures
- One class/concept per file where the architecture doc says so — don't merge modules for convenience
- Prefer small, testable pure functions in the physics core (e.g. `resolve_collision(a, b, contact) -> None` should be independently testable without a full `World`)
- Use `dataclasses` for simple state containers (e.g. `Contact`)
- Keep magic numbers named (`GRAVITY = 9.8`, `DEFAULT_RESTITUTION = 0.2`) — not inline literals scattered through the code

## When something is genuinely hard or ambiguous

If a stage's requirements are ambiguous, or a physics/RL result looks wrong and you can't tell if it's a bug or expected behavior (RL training is often noisy — this is normal, don't "fix" it by faking a smoother curve), stop and flag it clearly instead of guessing silently. State what you tried, what you observed, and what you think the options are. A flagged uncertainty costs a little time; a silently faked result costs the whole point of the project.
