"""Shapes and bounding boxes for physics collision detection."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from physics.vec2 import Vec2
from physics.body import RigidBody


@dataclass
class AABB:
    """Axis-Aligned Bounding Box."""
    min: Vec2
    max: Vec2

    def overlaps(self, other: AABB) -> bool:
        """Check if this AABB overlaps with another AABB."""
        if self.max.x < other.min.x or self.min.x > other.max.x:
            return False
        if self.max.y < other.min.y or self.min.y > other.max.y:
            return False
        return True


class Shape:
    """Base class for collision shapes."""
    def get_aabb(self, body: RigidBody) -> AABB:
        """Return world-space AABB for body."""
        raise NotImplementedError


class Circle(Shape):
    """Circle shape defined by radius."""

    def __init__(self, radius: float) -> None:
        """Initialize Circle with radius."""
        if radius <= 0:
            raise ValueError(f"Radius must be positive, got {radius}")
        self.radius: float = float(radius)

    def get_aabb(self, body: RigidBody) -> AABB:
        """Return world-space AABB for circle shape."""
        r = self.radius
        min_pt = Vec2(body.position.x - r, body.position.y - r)
        max_pt = Vec2(body.position.x + r, body.position.y + r)
        return AABB(min_pt, max_pt)


class Polygon(Shape):
    """Convex polygon shape defined by local vertices in CCW order."""

    def __init__(self, vertices: list[Vec2] | list[tuple[float, float]]) -> None:
        """Initialize Polygon with local space vertices."""
        if len(vertices) < 3:
            raise ValueError("Polygon must have at least 3 vertices")
        self.vertices: list[Vec2] = [v if isinstance(v, Vec2) else Vec2(v) for v in vertices]

    def get_world_vertices(self, body: RigidBody) -> list[Vec2]:
        """Transform local vertices to world coordinates using body's position and angle."""
        return [v.rotate(body.angle) + body.position for v in self.vertices]

    def get_aabb(self, body: RigidBody) -> AABB:
        """Return world-space AABB for polygon shape."""
        world_verts = self.get_world_vertices(body)
        xs = [v.x for v in world_verts]
        ys = [v.y for v in world_verts]
        return AABB(Vec2(min(xs), min(ys)), Vec2(max(xs), max(ys)))
