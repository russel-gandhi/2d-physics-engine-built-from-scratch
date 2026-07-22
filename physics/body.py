"""Rigid body module for 2D physics engine."""
from __future__ import annotations
from physics.vec2 import Vec2


class RigidBody:
    """Rigid body representation with position, velocity, mass, and integration."""

    def __init__(
        self,
        position: Vec2 | tuple | list | None = None,
        velocity: Vec2 | tuple | list | None = None,
        angle: float = 0.0,
        angular_velocity: float = 0.0,
        mass: float = 1.0,
        moment_of_inertia: float = 1.0,
    ) -> None:
        """Initialize a rigid body with position, velocity, orientation, and mass properties."""
        self.position: Vec2 = Vec2(position) if position is not None else Vec2(0.0, 0.0)
        self.velocity: Vec2 = Vec2(velocity) if velocity is not None else Vec2(0.0, 0.0)
        self.angle: float = float(angle)
        self.angular_velocity: float = float(angular_velocity)
        self.mass: float = float(mass)
        self.moment_of_inertia: float = float(moment_of_inertia)

        if self.mass <= 0.0:
            self.mass = 0.0
            self.inv_mass: float = 0.0
            self.inv_moment_of_inertia: float = 0.0
        else:
            self.inv_mass: float = 1.0 / self.mass
            self.inv_moment_of_inertia: float = 1.0 / self.moment_of_inertia if self.moment_of_inertia > 0.0 else 0.0

        self.force_accum: Vec2 = Vec2(0.0, 0.0)
        self.torque_accum: float = 0.0

    @property
    def is_static(self) -> bool:
        """Return True if the body is static (mass == 0)."""
        return self.inv_mass == 0.0

    def apply_force(
        self,
        force: Vec2 | tuple | list,
        point: Vec2 | tuple | list | None = None,
    ) -> None:
        """Accumulate force applied at world-space point (or center of mass if point is None)."""
        f = force if isinstance(force, Vec2) else Vec2(force)
        self.force_accum = self.force_accum + f
        if point is not None:
            pt = point if isinstance(point, Vec2) else Vec2(point)
            torque = (pt - self.position).cross(f)
            self.torque_accum += torque

    def apply_torque(self, t: float) -> None:
        """Accumulate torque directly."""
        self.torque_accum += float(t)

    def integrate(self, dt: float) -> None:
        """Integrate body state over timestep dt using semi-implicit Euler."""
        if self.is_static:
            self.velocity = Vec2(0.0, 0.0)
            self.angular_velocity = 0.0
            self.force_accum = Vec2(0.0, 0.0)
            self.torque_accum = 0.0
            return

        acceleration = self.force_accum * self.inv_mass
        self.velocity = self.velocity + acceleration * dt

        angular_accel = self.torque_accum * self.inv_moment_of_inertia
        self.angular_velocity += angular_accel * dt

        self.position = self.position + self.velocity * dt
        self.angle += self.angular_velocity * dt

        self.force_accum = Vec2(0.0, 0.0)
        self.torque_accum = 0.0

    def __repr__(self) -> str:
        """Return string representation of rigid body."""
        return f"RigidBody(pos={self.position}, vel={self.velocity}, angle={self.angle:.4f}, mass={self.mass})"
