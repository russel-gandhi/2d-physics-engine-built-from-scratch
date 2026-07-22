# Domain Glossary — Physics, RL, and Evolutionary Computation

Reference this when implementing a stage that uses a term below. Keep implementations consistent with these definitions rather than improvising alternatives.

## Physics

**Semi-implicit (symplectic) Euler integration** — update velocity first using the current force, then update position using the *new* velocity:
```
v_new = v + (F / m) * dt
x_new = x + v_new * dt
```
More stable than explicit Euler (which uses the old velocity for both updates) at the same `dt`, and simple enough to hand-derive — use this, not RK4, unless a stage says otherwise.

**AABB (Axis-Aligned Bounding Box)** — the smallest rectangle, aligned to the x/y axes, that fully contains a shape. Used for cheap broad-phase collision checks before running expensive exact tests.

**SAT (Separating Axis Theorem)** — two convex shapes are *not* colliding if there exists any axis along which their projections don't overlap. For polygon-polygon collision, test the axes perpendicular to each polygon's edges; if every axis shows a gap, no collision. If none do, the axis with the smallest overlap gives the collision normal and penetration depth.

**Impulse-based collision resolution** — instead of solving forces continuously through a collision, apply an instantaneous velocity change (impulse `J`) at the moment of contact:
```
J = -(1 + e) * relative_velocity_along_normal / (1/m_a + 1/m_b)
```
where `e` is the coefficient of restitution (0 = perfectly inelastic, 1 = perfectly elastic). Apply `+J*normal/m_a` and `-J*normal/m_b` to each body's velocity.

**Joint / constraint** — a rule restricting relative motion between two bodies (e.g. "these two points must stay the same distance apart" for a `DistanceJoint`, or "these two bodies rotate around a shared point" for a `RevoluteJoint`/hinge). Solved iteratively (a few passes per timestep) rather than exactly, which is standard practice in real-time physics engines.

## Reinforcement Learning

**Environment / Agent / Episode** — the environment (`CreatureEnv`) presents an observation, the agent picks an action, the environment returns a reward and the next observation; this repeats until the episode ends (`terminated` — e.g. creature fell over — or `truncated` — e.g. time limit hit).

**Observation space / Action space** — the shape and bounds of what the agent sees and can do. For a creature: observation is typically joint angles, joint angular velocities, body orientation, maybe contact flags; action is typically a torque or target angle per motorized joint, bounded to `[-1, 1]` and scaled to real torque units inside the environment.

**Reward shaping** — designing the reward function so maximizing it actually produces the behavior you want. For locomotion, a common minimal reward is roughly `forward_velocity - small_penalty_for_torque_used - penalty_for_falling`. Too sparse (only reward at episode end) and PPO struggles to learn; too shaped (rewarding very specific poses) and you get unnatural, overfit gaits. Start minimal, only add penalty terms if a specific bad behavior shows up.

**PPO (Proximal Policy Optimization)** — a policy-gradient RL algorithm that improves the policy in small, clipped steps to avoid destructively large updates. Treated as a library call here (`stable_baselines3.PPO`) — understand its inputs (environment, policy network size, hyperparameters like `learning_rate`, `n_steps`, `gamma`) well enough to tune them, but do not reimplement the algorithm itself.

## Evolutionary Computation

**Genome** — here, the flattened weights (and biases) of a small MLP, represented as a 1D numpy array so it can be mutated/crossed-over like any other vector.

**Fitness function** — what's being maximized by evolution — for this project, typically the same kind of signal as the RL reward (distance traveled / time upright), but evaluated as a single scalar per full episode rather than a per-step reward.

**Selection** — choosing which genomes reproduce into the next generation, biased toward higher fitness (e.g. tournament selection: randomly sample a few genomes, keep the fittest).

**Crossover** — combining two parent genomes into a child (e.g. uniform crossover: each weight has a 50% chance of coming from either parent).

**Mutation** — randomly perturbing a genome's weights (e.g. add small Gaussian noise to a random subset of weights) to maintain diversity and enable exploration crossover alone can't reach.

**Generation loop** — evaluate fitness for the whole population → select parents → produce the next generation via crossover + mutation → repeat. Track best/average fitness per generation for the progress plot.
