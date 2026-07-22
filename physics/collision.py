"""Collision detection module implementing broad-phase AABB checks and SAT narrow-phase."""
from __future__ import annotations
from dataclasses import dataclass
import math
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.shapes import AABB, Circle, Polygon, Shape


@dataclass
class Contact:
    """Collision contact information."""
    point: Vec2
    normal: Vec2  # Points from body_a to body_b
    penetration: float
    body_a: RigidBody | None = None
    body_b: RigidBody | None = None


def aabb_overlap(a: AABB, b: AABB) -> bool:
    """Broad-phase AABB overlap test."""
    return a.overlaps(b)


def circle_vs_circle(a: RigidBody, b: RigidBody) -> Contact | None:
    """Narrow-phase collision detection between two circles."""
    if not isinstance(a.shape, Circle) or not isinstance(b.shape, Circle):
        raise TypeError("Both bodies must have Circle shapes")

    d = b.position - a.position
    dist_sq = d.length_sq()
    total_r = a.shape.radius + b.shape.radius

    if dist_sq >= total_r * total_r:
        return None

    dist = math.sqrt(dist_sq)
    if dist < 1e-12:
        normal = Vec2(1.0, 0.0)
        penetration = total_r
        point = a.position.copy()
    else:
        normal = d * (1.0 / dist)
        penetration = total_r - dist
        point = a.position + normal * (a.shape.radius - penetration * 0.5)

    return Contact(point=point, normal=normal, penetration=penetration, body_a=a, body_b=b)


def circle_vs_polygon(a: RigidBody, b: RigidBody) -> Contact | None:
    """Narrow-phase collision detection between Circle (body a) and Polygon (body b)."""
    # If a is Polygon and b is Circle, swap them and invert normal
    swapped = False
    if isinstance(a.shape, Polygon) and isinstance(b.shape, Circle):
        a, b = b, a
        swapped = True

    if not isinstance(a.shape, Circle) or not isinstance(b.shape, Polygon):
        raise TypeError("Expected one Circle and one Polygon shape")

    circle = a.shape
    poly = b.shape
    c_pos = a.position
    verts = poly.get_world_vertices(b)
    n_verts = len(verts)

    # Candidate axes: polygon edge normals + axis from circle center to closest vertex
    closest_vert = verts[0]
    min_dist_sq = (verts[0] - c_pos).length_sq()
    for v in verts[1:]:
        d_sq = (v - c_pos).length_sq()
        if d_sq < min_dist_sq:
            min_dist_sq = d_sq
            closest_vert = v

    axes: list[Vec2] = []
    # Polygon edge normals
    for i in range(n_verts):
        v1 = verts[i]
        v2 = verts[(i + 1) % n_verts]
        edge = v2 - v1
        normal = Vec2(-edge.y, edge.x).normalize()
        axes.append(normal)

    # Circle center to closest vertex axis
    axis_c_v = closest_vert - c_pos
    if axis_c_v.length_sq() > 1e-12:
        axes.append(axis_c_v.normalize())

    min_overlap = float("inf")
    best_normal = Vec2(1.0, 0.0)

    for axis in axes:
        # Project polygon
        poly_projs = [v.dot(axis) for v in verts]
        p_min, p_max = min(poly_projs), max(poly_projs)

        # Project circle
        c_proj = c_pos.dot(axis)
        c_min, c_max = c_proj - circle.radius, c_proj + circle.radius

        # Overlap test
        overlap = min(p_max, c_max) - max(p_min, c_min)
        if overlap <= 0:
            return None

        if overlap < min_overlap:
            min_overlap = overlap
            best_normal = axis

    # Orient normal from a to b
    if (b.position - a.position).dot(best_normal) < 0:
        best_normal = -best_normal

    if swapped:
        # Swap back so normal points from original body_a to body_b
        return Contact(
            point=c_pos + best_normal * (circle.radius - min_overlap * 0.5),
            normal=-best_normal,
            penetration=min_overlap,
            body_a=b,
            body_b=a,
        )

    point = c_pos + best_normal * (circle.radius - min_overlap * 0.5)
    return Contact(
        point=point,
        normal=best_normal,
        penetration=min_overlap,
        body_a=a,
        body_b=b,
    )


def polygon_vs_polygon(a: RigidBody, b: RigidBody) -> Contact | None:
    """Narrow-phase collision detection between two Polygons using SAT."""
    if not isinstance(a.shape, Polygon) or not isinstance(b.shape, Polygon):
        raise TypeError("Both bodies must have Polygon shapes")

    verts_a = a.shape.get_world_vertices(a)
    verts_b = b.shape.get_world_vertices(b)

    def get_axes(verts: list[Vec2]) -> list[Vec2]:
        axes = []
        n = len(verts)
        for i in range(n):
            v1 = verts[i]
            v2 = verts[(i + 1) % n]
            edge = v2 - v1
            normal = Vec2(-edge.y, edge.x).normalize()
            axes.append(normal)
        return axes

    axes_a = get_axes(verts_a)
    axes_b = get_axes(verts_b)

    min_overlap = float("inf")
    best_normal = Vec2(1.0, 0.0)

    for axis in axes_a + axes_b:
        projs_a = [v.dot(axis) for v in verts_a]
        projs_b = [v.dot(axis) for v in verts_b]

        min_a, max_a = min(projs_a), max(projs_a)
        min_b, max_b = min(projs_b), max(projs_b)

        overlap = min(max_a, max_b) - max(min_a, min_b)
        if overlap <= 0:
            return None

        if overlap < min_overlap:
            min_overlap = overlap
            best_normal = axis

    # Orient normal from a to b
    if (b.position - a.position).dot(best_normal) < 0:
        best_normal = -best_normal

    # Estimate contact point
    point = (a.position + b.position) * 0.5

    return Contact(
        point=point,
        normal=best_normal,
        penetration=min_overlap,
        body_a=a,
        body_b=b,
    )


# Call statistics tracking for verification
broad_phase_checks = 0
narrow_phase_checks = 0


def reset_collision_stats() -> None:
    """Reset broad and narrow phase call counters."""
    global broad_phase_checks, narrow_phase_checks
    broad_phase_checks = 0
    narrow_phase_checks = 0


def find_contacts(bodies: list[RigidBody]) -> list[Contact]:
    """Find all contacts among a list of rigid bodies using AABB broad-phase and SAT narrow-phase."""
    global broad_phase_checks, narrow_phase_checks
    contacts: list[Contact] = []
    n = len(bodies)

    for i in range(n):
        body_a = bodies[i]
        if body_a.shape is None:
            continue
        aabb_a = body_a.shape.get_aabb(body_a)

        for j in range(i + 1, n):
            body_b = bodies[j]
            if body_b.shape is None:
                continue

            broad_phase_checks += 1
            aabb_b = body_b.shape.get_aabb(body_b)

            # Broad-phase check
            if not aabb_overlap(aabb_a, aabb_b):
                continue

            # Narrow-phase check
            narrow_phase_checks += 1
            contact = None

            if isinstance(body_a.shape, Circle) and isinstance(body_b.shape, Circle):
                contact = circle_vs_circle(body_a, body_b)
            elif isinstance(body_a.shape, Polygon) and isinstance(body_b.shape, Polygon):
                contact = polygon_vs_polygon(body_a, body_b)
            elif isinstance(body_a.shape, Circle) and isinstance(body_b.shape, Polygon):
                contact = circle_vs_polygon(body_a, body_b)
            elif isinstance(body_a.shape, Polygon) and isinstance(body_b.shape, Circle):
                contact = circle_vs_polygon(body_a, body_b)

            if contact is not None:
                contacts.append(contact)

    return contacts
