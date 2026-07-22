# Stage 12 — Genetic Algorithm Loop

**Day 6, second half. Depends on:** Stage 11.

## Goal

The actual evolutionary learning loop — this is the second centerpiece result of the project.

## What to build

`evolution/ga.py`
- `select(population, fitnesses, n) -> list[genome]` — tournament selection (see glossary) is a good default: simple, no extra hyperparameters beyond tournament size.
- `crossover(parent_a, parent_b) -> child_genome` — uniform crossover.
- `mutate(genome, rate, strength) -> genome` — add Gaussian noise to a `rate` fraction of weights, scaled by `strength`.
- `run_generations(population, num_generations) -> history`: for each generation — evaluate all genomes' fitness (this is where most of the compute time goes; if too slow, reduce population size or episode length before cutting corners elsewhere), log best/mean fitness, select + crossover + mutate to produce the next generation's genomes, keep at least 1 elite (the best genome carried over unchanged) so fitness can't regress.

`scripts/plot_evolution.py` — plot best-fitness and mean-fitness per generation from the real logged `history`.

## Definition of Done

- [ ] A real run (budget generations/population size against remaining time — start smaller to confirm the loop works, then scale up if time allows) shows best-fitness trending upward across generations (again, noise is normal; a completely flat line across many generations suggests a bug — e.g. mutation too weak/strong, or elitism not actually preserving the best genome — not something to smooth over in the plot)
- [ ] The best genome from the final generation, replayed through the renderer, visibly performs better than a random genome from generation 0 — this is the real qualitative proof evolution did something; watch it yourself before considering the stage done
- [ ] Fitness/generation data plotted comes from the actual `history` log, not illustrative/placeholder numbers
