# Stage 22 — Combat Evolution

**Phase 4. Depends on:** Stage 20.

## Goal

The evolutionary half of "Intelligent Combat Systems" — a population of fighters evolved via round-robin competition rather than a solo distance/survival metric.

## What to build

`evolution/ga.py` (extend) or a new combat evaluation function using the same `select`/`crossover`/`mutate` machinery from stage 12:
- `evaluate_combat_fitness(population) -> fitnesses`: for each generation, have each genome fight a handful of others sampled from the same population (round-robin, not necessarily every pair if population size makes that too slow — see glossary), using `CombatEnv` with both sides driven by `NNController`. Fitness combines win rate, damage dealt, and (optionally) movement efficiency/survival time, matching the concept doc's stated fitness factors.
- Keep elitism from stage 12 (best genome carried over unchanged) so the population doesn't regress.

## Definition of Done

- [ ] A real run shows best/mean fitness trending upward across generations (noise expected, flat-forever is a bug to investigate)
- [ ] The best genome from the final generation, fought against a genome from generation 0, wins more often than not across a handful of real matches — this is the qualitative proof evolution produced better fighters; watch/log actual match outcomes to confirm
- [ ] Fitness data plotted comes from real logged match outcomes, not illustrative numbers
