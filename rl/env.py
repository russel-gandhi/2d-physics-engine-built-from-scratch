"""Gymnasium environment wrapping custom 2D physics world and creature for reinforcement learning."""
from __future__ import annotations
import os
from typing import Any
import numpy as np
import gymnasium as gym
from gymnasium import spaces

from physics.vec2 import Vec2
from physics.shapes import Polygon
from physics.body import RigidBody
from physics.world import World
from creatures.morphology import CreatureSpec, Creature, build_creature


class CreatureEnv(gym.Env):
    """Gymnasium environment wrapping a creature in the 2D physics world.

    Observation Space (1D float32 numpy array):
        0: torso height (y position)
        1: torso velocity x
        2: torso velocity y
        3: torso angle (radians)
        4: torso angular velocity (rad/s)
        5..5+N-1: relative joint angle for each motorized joint
        5+N..5+2N-1: relative joint angular velocity for each motorized joint
        5+2N..5+3N-1: ground contact flag for each motorized joint child segment (1.0 if contact, 0.0 if not)

    Action Space:
        Box(-1.0, 1.0, shape=(num_motorized_joints,)) representing normalized motor torques.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(
        self,
        spec: CreatureSpec | str | None = None,
        render_mode: str | None = None,
        max_episode_steps: int = 1000,
        frame_skip: int = 4,
    ) -> None:
        """Initialize CreatureEnv with morphology spec and Gymnasium action/observation spaces."""
        super().__init__()

        if spec is None:
            preset_path = os.path.join("creatures", "presets", "hopper.json")
            self.spec = CreatureSpec.from_json(preset_path)
        elif isinstance(spec, str):
            self.spec = CreatureSpec.from_json(spec)
        else:
            self.spec = spec

        self.render_mode = render_mode
        self.max_episode_steps = max_episode_steps
        self.frame_skip = frame_skip

        # Determine number of motorized joints
        self.num_joints = len(self.spec.joints)
        num_actions = sum(1 for j in self.spec.joints if j.joint_type == "revolute")

        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(num_actions,), dtype=np.float32
        )

        # Observation dimension: 5 (torso state) + 3 * num_joints
        obs_dim = 5 + 3 * self.num_joints
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )

        self.world: World | None = None
        self.creature: Creature | None = None
        self.current_step = 0

    def _get_obs(self) -> np.ndarray:
        """Construct and return current observation vector from creature state."""
        assert self.creature is not None
        torso = self.creature.main_body

        obs_list = [
            float(torso.position.y),
            float(torso.velocity.x),
            float(torso.velocity.y),
            float(torso.angle),
            float(torso.angular_velocity),
        ]

        # Joint relative angles and angular velocities
        for j_spec in self.spec.joints:
            parent = self.creature.bodies[j_spec.parent_segment]
            child = self.creature.bodies[j_spec.child_segment]
            rel_angle = float(child.angle - parent.angle)
            rel_ang_vel = float(child.angular_velocity - parent.angular_velocity)
            obs_list.append(rel_angle)
            obs_list.append(rel_ang_vel)

        # Ground contact flags per joint segment
        assert self.world is not None
        contact_bodies = set()
        for contact in self.world.last_contacts:
            if contact.body_a is not None:
                contact_bodies.add(contact.body_a)
            if contact.body_b is not None:
                contact_bodies.add(contact.body_b)

        for j_spec in self.spec.joints:
            child = self.creature.bodies[j_spec.child_segment]
            in_contact = 1.0 if child in contact_bodies else 0.0
            obs_list.append(in_contact)

        return np.array(obs_list, dtype=np.float32)

    def reset(
        self, seed: int | None = None, options: dict[str, Any] | None = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Reset environment to initial state."""
        super().reset(seed=seed)

        self.world = World(gravity=(0.0, -9.8), substeps=8, restitution=0.2, friction=0.4)

        # Static ground
        ground_shape = Polygon([
            Vec2(-100.0, -0.5),
            Vec2(100.0, -0.5),
            Vec2(100.0, 0.5),
            Vec2(-100.0, 0.5),
        ])
        ground = RigidBody(position=(0.0, 0.5), mass=0.0, shape=ground_shape)
        self.world.add_body(ground)

        # Build creature
        self.creature = build_creature(self.spec, self.world, base_position=(0.0, 2.0))
        self.current_step = 0

        # Run 1 initial step to populate contacts
        self.world.step(1.0 / 60.0)

        obs = self._get_obs()
        return obs, {}

    def step(
        self, action: np.ndarray | list[float]
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """Advance simulation by 1 RL step (frame_skip physics substeps)."""
        assert self.creature is not None and self.world is not None

        act_array = np.asarray(action, dtype=np.float32)
        self.creature.apply_actions(act_array)

        dt = 1.0 / 60.0
        for _ in range(self.frame_skip):
            self.world.step(dt)

        obs = self._get_obs()
        torso = self.creature.main_body

        # Reward: forward velocity minus small control cost
        forward_vel = float(torso.velocity.x)
        ctrl_cost = 0.001 * float(np.sum(np.square(act_array)))
        reward = forward_vel - ctrl_cost

        # Termination criteria: fell over or height dropped too low
        terminated = bool(torso.position.y < 0.7 or abs(torso.angle) > 1.2)

        self.current_step += 1
        truncated = bool(self.current_step >= self.max_episode_steps)

        info = {
            "forward_velocity": forward_vel,
            "torso_height": float(torso.position.y),
        }

        return obs, reward, terminated, truncated, info
