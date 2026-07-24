"""
Verification test: Real 1v1 CombatEnv training.
Runs 2 generations of 4-candidate GA combat evaluation and prints real fitness values.
Exits with non-zero status if fitness stays exactly 0 (indicating physics never ran).
"""
import sys
import random
import numpy as np
from combat.combat_env import CombatEnv
from evolution.nn_controller import NNController
from evolution.ga import tournament_selection, crossover, mutate

GENERATIONS = 2
POP_SIZE = 4
MAX_STEPS = 100

robot_a = "robots/presets/boxer.json"
robot_b = "robots/presets/grappler.json"

print("[STEP 1] Creating CombatEnv with real robots...")
env = CombatEnv(robot_a_spec=robot_a, robot_b_spec=robot_b, max_episode_steps=MAX_STEPS, frame_skip=4)
obs_a, _ = env.reset()
obs_dim_a = env.observation_space.shape[0]
num_actions_a = env.action_space.shape[0]
obs_dim_b = len(env.current_obs_b)
num_actions_b = env.action_space_b.shape[0]

print(f"  obs_dim_a={obs_dim_a}, num_actions_a={num_actions_a}")
print(f"  obs_dim_b={obs_dim_b}, num_actions_b={num_actions_b}")

dummy = NNController(obs_dim_a, num_actions_a, 16)
genome_len = dummy.total_weights
print(f"  genome_length={genome_len}")

genomes = [np.random.randn(genome_len).astype(np.float32) * 0.5 for _ in range(POP_SIZE)]
ctrl_a = NNController(obs_dim_a, num_actions_a, 16)
ctrl_b = NNController(obs_dim_b, num_actions_b, 16)

print(f"\n[STEP 2] Running {GENERATIONS} generations x {POP_SIZE} candidates in REAL 1v1 physics...")

all_gen_fitnesses = []
for gen_idx in range(GENERATIONS):
    fitnesses = []
    for i, genome in enumerate(genomes):
        ctrl_a.set_genome(genome)
        opp_idx = random.choice([j for j in range(POP_SIZE) if j != i])
        ctrl_b.set_genome(genomes[opp_idx])

        obs_a, _ = env.reset()
        obs_b = env.current_obs_b
        total_reward = 0.0
        done = False
        steps = 0

        while not done:
            action_a = ctrl_a.act(obs_a)
            action_b = ctrl_b.act(obs_b)
            obs_a, obs_b, rew_a, rew_b, done, info = env.step_two_agents(action_a, action_b)
            total_reward += rew_a
            steps += 1

        fitnesses.append(float(total_reward))
        print(f"  Gen {gen_idx+1} | Candidate {i}: reward={total_reward:.4f}, steps={steps}, winner={info.get('winner','?')}")

    best = max(fitnesses)
    mean = sum(fitnesses) / len(fitnesses)
    all_gen_fitnesses.append(best)
    print(f"  --> Gen {gen_idx+1} BEST={best:.4f} MEAN={mean:.4f}")

    # GA evolution
    elite = [genomes[int(np.argmax(fitnesses))].copy()]
    parents = tournament_selection(genomes, fitnesses, num_select=POP_SIZE - 1, tournament_size=2)
    new_genomes = elite[:]
    for k in range(0, len(parents) - 1, 2):
        child = crossover(parents[k], parents[k+1])
        child = mutate(child, 0.08, 0.15)
        new_genomes.append(child)
    while len(new_genomes) < POP_SIZE:
        new_genomes.append(mutate(genomes[0].copy(), 0.1, 0.2))
    genomes = new_genomes[:POP_SIZE]

env.close()

print("\n[STEP 3] Result summary:")
print(f"  Fitness per generation: {[round(f, 4) for f in all_gen_fitnesses]}")

# Check that at least something happened (nonzero rewards)
all_nonzero = any(abs(f) > 1e-6 for f in all_gen_fitnesses)
if all_nonzero:
    print("  PASS: Real physics ran — fitness values are nonzero.")
    sys.exit(0)
else:
    print("  FAIL: All fitness values are zero — physics may not be running!")
    sys.exit(1)
