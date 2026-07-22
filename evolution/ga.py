"""Genetic Algorithm engine with tournament selection, uniform crossover, Gaussian mutation, and elitism."""
from __future__ import annotations
import numpy as np
from evolution.population import Population


def tournament_selection(
    genomes: list[np.ndarray],
    fitnesses: list[float],
    num_select: int,
    tournament_size: int = 3,
) -> list[np.ndarray]:
    """Select parent genomes via tournament selection."""
    pop_size = len(genomes)
    selected = []

    for _ in range(num_select):
        indices = np.random.choice(pop_size, size=min(tournament_size, pop_size), replace=False)
        best_idx = max(indices, key=lambda idx: fitnesses[idx])
        selected.append(genomes[best_idx].copy())

    return selected


def crossover(parent_a: np.ndarray, parent_b: np.ndarray) -> np.ndarray:
    """Perform uniform crossover between two parent genomes."""
    mask = np.random.rand(len(parent_a)) < 0.5
    child = np.where(mask, parent_a, parent_b)
    return child.astype(np.float32)


def mutate(
    genome: np.ndarray, mutation_rate: float = 0.05, mutation_strength: float = 0.1
) -> np.ndarray:
    """Apply Gaussian noise mutation to a fraction of genes in the genome."""
    mutated = genome.copy()
    mask = np.random.rand(len(genome)) < mutation_rate
    noise = np.random.randn(len(genome)).astype(np.float32) * mutation_strength
    mutated[mask] += noise[mask]
    return mutated


class GeneticAlgorithm:
    """Manages generation advancement and evolutionary optimization loop."""

    def __init__(
        self,
        population: Population,
        elitism: int = 1,
        mutation_rate: float = 0.05,
        mutation_strength: float = 0.1,
        tournament_size: int = 3,
    ) -> None:
        """Initialize Genetic Algorithm with hyperparameters."""
        self.population = population
        self.elitism = max(1, elitism)
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.tournament_size = tournament_size
        self.generation = 0

    def step_generation(self, max_steps_per_eval: int = 400) -> dict:
        """Evaluate population fitness and produce next generation via selection, crossover, and mutation."""
        # 1. Evaluate current generation fitnesses
        fitnesses = [
            self.population.evaluate(g, max_steps=max_steps_per_eval)
            for g in self.population.genomes
        ]

        best_idx = int(np.argmax(fitnesses))
        best_fitness = float(fitnesses[best_idx])
        mean_fitness = float(np.mean(fitnesses))
        best_genome = self.population.genomes[best_idx].copy()

        stats = {
            "generation": self.generation,
            "best_fitness": best_fitness,
            "mean_fitness": mean_fitness,
            "best_genome": best_genome,
        }

        # 2. Elitism: preserve top N genomes
        sorted_indices = np.argsort(fitnesses)[::-1]
        next_genomes = [self.population.genomes[idx].copy() for idx in sorted_indices[: self.elitism]]

        # 3. Fill remaining population via selection + crossover + mutation
        num_children_needed = self.population.size - self.elitism
        parents = tournament_selection(
            self.population.genomes,
            fitnesses,
            num_select=num_children_needed * 2,
            tournament_size=self.tournament_size,
        )

        for i in range(num_children_needed):
            p_a = parents[i * 2]
            p_b = parents[i * 2 + 1]
            child = crossover(p_a, p_b)
            child_mutated = mutate(
                child,
                mutation_rate=self.mutation_rate,
                mutation_strength=self.mutation_strength,
            )
            next_genomes.append(child_mutated)

        self.population.genomes = next_genomes
        self.generation += 1

        return stats

    def run_evolution(
        self, num_generations: int = 25, max_steps_per_eval: int = 400, verbose: bool = True
    ) -> list[dict]:
        """Run evolutionary loop across multiple generations and return history stats."""
        history = []

        for gen in range(num_generations):
            stats = self.step_generation(max_steps_per_eval=max_steps_per_eval)
            history.append(stats)

            if verbose:
                print(
                    f"Generation {stats['generation']:02d} | "
                    f"Best Fitness: {stats['best_fitness']:6.2f} | "
                    f"Mean Fitness: {stats['mean_fitness']:6.2f}"
                )

        return history
