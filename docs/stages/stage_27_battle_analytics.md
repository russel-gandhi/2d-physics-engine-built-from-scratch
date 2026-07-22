# Stage 27 — Battle Analytics

**Phase 7. Depends on:** Stage 23 (needs real replay data to analyze).

## Goal

Post-battle reports from real match data — matching the concept doc's "Battle Report" example.

## What to build

`analytics/battle_report.py`
- `generate_report(replay_file) -> BattleReport`: reads a `replay/recorder.py` log and computes real statistics: winner, damage dealt (as a % of opponent's total durability), movement efficiency (e.g. distance covered per unit of energy or per unit of motor effort — define this concretely and consistently, document the formula in the code), successful attack count (weapon-contact damage events above the stage 17 threshold), and one or more simple rule-based "weakness" flags derived from the log — e.g. "slow recovery" if time-to-return-to-upright after a knockdown exceeds a defined threshold, "low mobility" if average speed falls below a threshold relative to the robot's preset. Document each rule plainly in the code so it's clear these are simple heuristics over real data, not a claimed diagnostic system.

## Definition of Done

- [ ] Running this against a replay from an actual stage 19-24 match produces a report with real numbers that match what you can independently verify by watching the replay (spot check at least the winner and one damage figure)
- [ ] Weakness flags only appear when their defined threshold condition is actually met in the log — verify by constructing (or finding) one match where a flag should fire and one where it clearly shouldn't, and confirming both cases behave correctly
- [ ] Report format is readable as plain text or simple structured output, similar in spirit to the concept doc's example
