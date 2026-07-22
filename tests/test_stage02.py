"""Unit tests for Stage 02: Shapes and Collision Detection."""
import math
import pytest
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.shapes import Circle, Polygon, AABB
from physics import collision
from physics.collision import (
    circle_vs_circle,
    polygon_vs_polygon,
    circle_vs_polygon,
    find_contacts,
    reset_collision_stats,
)


def test_circles_overlapping():
    """Verify two overlapping circles detect contact with exact penetration depth."""
    # Circle A at (0, 0) r=1.0, Circle B at (1.5, 0) r=1.0
    # Center dist = 1.5, total_r = 2.0, penetration = 2.0 - 1.5 = 0.5
    body_a = RigidBody(position=(0.0, 0.0), shape=Circle(1.0))
    body_b = RigidBody(position=(1.5, 0.0), shape=Circle(1.0))

    contact = circle_vs_circle(body_a, body_b)
    assert contact is not None
    assert pytest.approx(contact.penetration) == 0.5
    assert pytest.approx(contact.normal.x) == 1.0
    assert pytest.approx(contact.normal.y) == 0.0


def test_circles_separated():
    """Verify two separated circles return None."""
    body_a = RigidBody(position=(0.0, 0.0), shape=Circle(1.0))
    body_b = RigidBody(position=(5.0, 0.0), shape=Circle(1.0))

    contact = circle_vs_circle(body_a, body_b)
    assert contact is None


def test_axis_aligned_overlapping_squares():
    """Verify two overlapping axis-aligned unit squares produce correct normal and penetration depth."""
    # Box A: center (0, 0), size 2x2 [-1, 1]x[-1, 1]
    # Box B: center (1.8, 0), size 2x2 [0.8, 2.8]x[-1, 1]
    # Overlap along x = 1.0 - 0.8 = 0.2
    poly_shape = Polygon([Vec2(-1, -1), Vec2(1, -1), Vec2(1, 1), Vec2(-1, 1)])
    body_a = RigidBody(position=(0.0, 0.0), shape=poly_shape)
    body_b = RigidBody(position=(1.8, 0.0), shape=poly_shape)

    contact = polygon_vs_polygon(body_a, body_b)
    assert contact is not None
    assert pytest.approx(contact.penetration) == 0.2
    assert pytest.approx(contact.normal.x) == 1.0
    assert pytest.approx(contact.normal.y) == 0.0


def test_separated_polygons_at_angle():
    """Verify two separated rotated polygons return None (testing non-axis-aligned SAT axes)."""
    # Create two triangles rotated 45 degrees, placed far enough apart along their rotated axis
    tri = Polygon([Vec2(0, 1), Vec2(-1, -1), Vec2(1, -1)])
    body_a = RigidBody(position=(0.0, 0.0), angle=math.pi / 4, shape=tri)
    body_b = RigidBody(position=(3.0, 3.0), angle=math.pi / 4, shape=tri)

    contact = polygon_vs_polygon(body_a, body_b)
    assert contact is None


def test_broad_phase_filtering():
    """Verify find_contacts only runs narrow phase on AABB-overlapping body pairs."""
    reset_collision_stats()

    # Create 5 circles: 2 overlapping, 3 far away
    bodies = [
        RigidBody(position=(0.0, 0.0), shape=Circle(1.0)),   # Body 0
        RigidBody(position=(1.5, 0.0), shape=Circle(1.0)),   # Body 1 (overlaps with 0)
        RigidBody(position=(10.0, 0.0), shape=Circle(1.0)),  # Body 2
        RigidBody(position=(20.0, 0.0), shape=Circle(1.0)),  # Body 3
        RigidBody(position=(30.0, 0.0), shape=Circle(1.0)),  # Body 4
    ]

    contacts = find_contacts(bodies)
    assert len(contacts) == 1

    # Total body pairs for 5 bodies = 5 * 4 / 2 = 10 broad phase checks
    assert collision.broad_phase_checks == 10
    # Narrow phase should ONLY be called for the 1 pair whose AABBs overlap (Body 0 & Body 1)
    assert collision.narrow_phase_checks == 1
