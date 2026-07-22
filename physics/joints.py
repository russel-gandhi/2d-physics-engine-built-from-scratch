"""Joints and physical constraint solvers."""
from __future__ import annotations
from physics.vec2 import Vec2
from physics.body import RigidBody


class Joint:
    """Base class for physical joint constraints."""

    def solve(self, dt: float) -> None:
        """Solve joint constraint for timestep dt."""
        raise NotImplementedError


class DistanceJoint(Joint):
    """Joint maintaining a fixed distance between two anchor points on two rigid bodies."""

    def __init__(
        self,
        body_a: RigidBody,
        anchor_a: Vec2 | tuple | list,
        body_b: RigidBody,
        anchor_b: Vec2 | tuple | list,
        rest_length: float | None = None,
    ) -> None:
        """Initialize DistanceJoint between body_a and body_b at specified local anchor points."""
        self.body_a: RigidBody = body_a
        self.anchor_a: Vec2 = anchor_a if isinstance(anchor_a, Vec2) else Vec2(anchor_a)
        self.body_b: RigidBody = body_b
        self.anchor_b: Vec2 = anchor_b if isinstance(anchor_b, Vec2) else Vec2(anchor_b)

        p_a = self.body_a.position + self.anchor_a.rotate(self.body_a.angle)
        p_b = self.body_b.position + self.anchor_b.rotate(self.body_b.angle)

        if rest_length is None:
            self.rest_length: float = (p_b - p_a).length()
        else:
            self.rest_length = float(rest_length)

    def solve(self, dt: float) -> None:
        """Solve distance constraint via impulse correction."""
        p_a = self.body_a.position + self.anchor_a.rotate(self.body_a.angle)
        p_b = self.body_b.position + self.anchor_b.rotate(self.body_b.angle)

        d = p_b - p_a
        dist = d.length()

        if dist > 1e-12:
            axis = d * (1.0 / dist)
        else:
            axis = Vec2(1.0, 0.0)

        r_a = p_a - self.body_a.position
        r_b = p_b - self.body_b.position

        v_a = self.body_a.velocity + Vec2(-self.body_a.angular_velocity * r_a.y, self.body_a.angular_velocity * r_a.x)
        v_b = self.body_b.velocity + Vec2(-self.body_b.angular_velocity * r_b.y, self.body_b.angular_velocity * r_b.x)

        v_rel = v_b - v_a
        rel_v = v_rel.dot(axis)
        pos_error = dist - self.rest_length

        r_a_cross_axis = r_a.cross(axis)
        r_b_cross_axis = r_b.cross(axis)

        denom = (
            self.body_a.inv_mass
            + self.body_b.inv_mass
            + (r_a_cross_axis ** 2) * self.body_a.inv_moment_of_inertia
            + (r_b_cross_axis ** 2) * self.body_b.inv_moment_of_inertia
        )

        if denom < 1e-12:
            return

        bias = (0.2 / dt) * pos_error
        j = -(rel_v + bias) / denom
        impulse = axis * j

        if not self.body_a.is_static:
            self.body_a.velocity = self.body_a.velocity - impulse * self.body_a.inv_mass
            self.body_a.angular_velocity -= r_a.cross(impulse) * self.body_a.inv_moment_of_inertia

        if not self.body_b.is_static:
            self.body_b.velocity = self.body_b.velocity + impulse * self.body_b.inv_mass
            self.body_b.angular_velocity += r_b.cross(impulse) * self.body_b.inv_moment_of_inertia


class RevoluteJoint(Joint):
    """Hinge joint pinning two anchor points together on two rigid bodies."""

    def __init__(
        self,
        body_a: RigidBody,
        anchor_a: Vec2 | tuple | list,
        body_b: RigidBody,
        anchor_b: Vec2 | tuple | list,
        motor_torque: float = 0.0,
    ) -> None:
        """Initialize RevoluteJoint with optional motor torque."""
        self.body_a: RigidBody = body_a
        self.anchor_a: Vec2 = anchor_a if isinstance(anchor_a, Vec2) else Vec2(anchor_a)
        self.body_b: RigidBody = body_b
        self.anchor_b: Vec2 = anchor_b if isinstance(anchor_b, Vec2) else Vec2(anchor_b)
        self.motor_torque: float = float(motor_torque)

    def apply_motor(self) -> None:
        """Apply motor torque as equal and opposite torques to connected bodies."""
        if self.motor_torque != 0.0:
            if not self.body_a.is_static:
                self.body_a.apply_torque(-self.motor_torque)
            if not self.body_b.is_static:
                self.body_b.apply_torque(self.motor_torque)

    def solve(self, dt: float) -> None:
        """Solve 2D point constraint keeping anchor points together."""
        for axis in (Vec2(1.0, 0.0), Vec2(0.0, 1.0)):
            p_a = self.body_a.position + self.anchor_a.rotate(self.body_a.angle)
            p_b = self.body_b.position + self.anchor_b.rotate(self.body_b.angle)
            pos_error = p_b - p_a

            r_a = p_a - self.body_a.position
            r_b = p_b - self.body_b.position

            v_a = self.body_a.velocity + Vec2(-self.body_a.angular_velocity * r_a.y, self.body_a.angular_velocity * r_a.x)
            v_b = self.body_b.velocity + Vec2(-self.body_b.angular_velocity * r_b.y, self.body_b.angular_velocity * r_b.x)
            v_rel = v_b - v_a

            rel_v = v_rel.dot(axis)
            err = pos_error.dot(axis)

            r_a_cross = r_a.cross(axis)
            r_b_cross = r_b.cross(axis)

            denom = (
                self.body_a.inv_mass
                + self.body_b.inv_mass
                + (r_a_cross ** 2) * self.body_a.inv_moment_of_inertia
                + (r_b_cross ** 2) * self.body_b.inv_moment_of_inertia
            )

            if denom > 1e-12:
                bias = (0.5 / dt) * err
                j = -(rel_v + bias) / denom
                impulse = axis * j

                if not self.body_a.is_static:
                    self.body_a.velocity = self.body_a.velocity - impulse * self.body_a.inv_mass
                    self.body_a.angular_velocity -= r_a.cross(impulse) * self.body_a.inv_moment_of_inertia

                if not self.body_b.is_static:
                    self.body_b.velocity = self.body_b.velocity + impulse * self.body_b.inv_mass
                    self.body_b.angular_velocity += r_b.cross(impulse) * self.body_b.inv_moment_of_inertia

        # Positional correction to eliminate drift
        p_a = self.body_a.position + self.anchor_a.rotate(self.body_a.angle)
        p_b = self.body_b.position + self.anchor_b.rotate(self.body_b.angle)
        pos_err = p_b - p_a
        inv_mass_sum = self.body_a.inv_mass + self.body_b.inv_mass
        if inv_mass_sum > 1e-12:
            corr = pos_err * 0.05
            if not self.body_a.is_static:
                self.body_a.position += corr * (self.body_a.inv_mass / inv_mass_sum)
            if not self.body_b.is_static:
                self.body_b.position -= corr * (self.body_b.inv_mass / inv_mass_sum)
