"""Impulse-based collision resolution with restitution, Coulomb friction, and positional correction."""
from __future__ import annotations
import math
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.collision import Contact


def resolve_collision(
    a: RigidBody,
    b: RigidBody,
    contact: Contact,
    restitution: float = 0.2,
    friction: float = 0.3,
) -> None:
    """Resolve collision between body a and body b using impulse response."""
    if a.is_static and b.is_static:
        return

    normal = contact.normal
    p = contact.point

    r_a = p - a.position
    r_b = p - b.position

    # Velocity of contact points
    v_a = a.velocity + Vec2(-a.angular_velocity * r_a.y, a.angular_velocity * r_a.x)
    v_b = b.velocity + Vec2(-b.angular_velocity * r_b.y, b.angular_velocity * r_b.x)

    v_rel = v_b - v_a
    rel_vel_n = v_rel.dot(normal)

    # Do not resolve if moving apart
    if rel_vel_n > 0:
        return

    r_a_cross_n = r_a.cross(normal)
    r_b_cross_n = r_b.cross(normal)

    denom_n = (
        a.inv_mass
        + b.inv_mass
        + (r_a_cross_n ** 2) * a.inv_moment_of_inertia
        + (r_b_cross_n ** 2) * b.inv_moment_of_inertia
    )

    if denom_n < 1e-12:
        return

    j_n = -(1.0 + restitution) * rel_vel_n / denom_n
    impulse_n = normal * j_n

    # Apply normal impulse
    if not a.is_static:
        a.velocity = a.velocity - impulse_n * a.inv_mass
        a.angular_velocity -= r_a.cross(impulse_n) * a.inv_moment_of_inertia

    if not b.is_static:
        b.velocity = b.velocity + impulse_n * b.inv_mass
        b.angular_velocity += r_b.cross(impulse_n) * b.inv_moment_of_inertia

    # Re-evaluate relative velocity for friction after normal impulse
    v_a = a.velocity + Vec2(-a.angular_velocity * r_a.y, a.angular_velocity * r_a.x)
    v_b = b.velocity + Vec2(-b.angular_velocity * r_b.y, b.angular_velocity * r_b.x)
    v_rel = v_b - v_a

    tangent_vec = v_rel - normal * v_rel.dot(normal)
    tangent_len_sq = tangent_vec.length_sq()

    if tangent_len_sq > 1e-12:
        tangent = tangent_vec.normalize()
        rel_vel_t = v_rel.dot(tangent)

        r_a_cross_t = r_a.cross(tangent)
        r_b_cross_t = r_b.cross(tangent)

        denom_t = (
            a.inv_mass
            + b.inv_mass
            + (r_a_cross_t ** 2) * a.inv_moment_of_inertia
            + (r_b_cross_t ** 2) * b.inv_moment_of_inertia
        )

        if denom_t > 1e-12:
            j_t = -rel_vel_t / denom_t
            # Coulomb friction clamping
            max_j_t = friction * j_n
            j_t = max(-max_j_t, min(max_j_t, j_t))
            impulse_t = tangent * j_t

            if not a.is_static:
                a.velocity = a.velocity - impulse_t * a.inv_mass
                a.angular_velocity -= r_a.cross(impulse_t) * a.inv_moment_of_inertia

            if not b.is_static:
                b.velocity = b.velocity + impulse_t * b.inv_mass
                b.angular_velocity += r_b.cross(impulse_t) * b.inv_moment_of_inertia

    # Positional correction to prevent sinking/penetration accumulation
    slop = 0.01
    percent = 0.4
    inv_mass_sum = a.inv_mass + b.inv_mass
    if inv_mass_sum > 1e-12:
        correction_mag = max(contact.penetration - slop, 0.0) / inv_mass_sum * percent
        correction = normal * correction_mag

        if not a.is_static:
            a.position = a.position - correction * a.inv_mass
        if not b.is_static:
            b.position = b.position + correction * b.inv_mass


def resolve_contacts(
    contacts: list[Contact],
    restitution: float = 0.2,
    friction: float = 0.3,
) -> None:
    """Resolve a list of contact constraints."""
    for contact in contacts:
        if contact.body_a is not None and contact.body_b is not None:
            resolve_collision(
                contact.body_a,
                contact.body_b,
                contact,
                restitution=restitution,
                friction=friction,
            )
