"""Physics World loop managing bodies, joints, collisions, and fixed-timestep integration."""
from __future__ import annotations
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.joints import Joint, RevoluteJoint
from physics.collision import find_contacts, Contact
from physics.resolver import resolve_contacts


class World:
    """Simulation world managing rigid bodies, joints, gravity, and timestep updates."""

    def __init__(
        self,
        gravity: Vec2 | tuple | list = (0.0, -9.8),
        substeps: int = 8,
        restitution: float = 0.2,
        friction: float = 0.3,
    ) -> None:
        """Initialize World with gravity, constraint substeps, and collision parameters."""
        self.bodies: list[RigidBody] = []
        self.joints: list[Joint] = []
        self.gravity: Vec2 = gravity if isinstance(gravity, Vec2) else Vec2(gravity)
        self.substeps: int = int(substeps)
        self.restitution: float = float(restitution)
        self.friction: float = float(friction)
        self.last_contacts: list[Contact] = []
        self.time: float = 0.0
        self.step_count: int = 0

    def add_body(self, body: RigidBody) -> None:
        """Add a rigid body to the world."""
        if body not in self.bodies:
            self.bodies.append(body)

    def add_joint(self, joint: Joint) -> None:
        """Add a joint constraint to the world."""
        if joint not in self.joints:
            self.joints.append(joint)

    def step(self, dt: float) -> None:
        """Advance simulation by fixed timestep dt."""
        self.time += dt
        self.step_count += 1
        # 1. Apply motor torques to RevoluteJoints
        for joint in self.joints:
            if isinstance(joint, RevoluteJoint):
                joint.apply_motor()

        # 2. Apply gravity to dynamic bodies
        for body in self.bodies:
            if not body.is_static:
                body.apply_force(self.gravity * body.mass)

        # 3. Integrate body velocities and positions
        for body in self.bodies:
            body.integrate(dt)

        # 4. Broad and narrow phase collision detection
        self.last_contacts = find_contacts(self.bodies)

        # 5. Resolve collisions
        resolve_contacts(
            self.last_contacts,
            restitution=self.restitution,
            friction=self.friction,
        )

        # 6. Iterative joint solver
        for _ in range(self.substeps):
            for joint in self.joints:
                joint.solve(dt)
