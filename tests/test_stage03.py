"""Unit tests for Stage 03: Collision Resolution."""
import math
import pytest
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.shapes import Circle, Polygon
from physics.collision import circle_vs_circle, circle_vs_polygon, Contact
from physics.resolver import resolve_collision, resolve_contacts


def test_elastic_bounce_height():
    """Verify ball dropped on static ground with restitution=1.0 bounces back close to original height."""
    # Ball radius 0.5, mass 1.0, starting at height 5.0
    initial_y = 5.0
    ball = RigidBody(position=(0.0, initial_y), velocity=(0.0, 0.0), mass=1.0, shape=Circle(0.5))
    ground = RigidBody(position=(0.0, 0.0), mass=0.0, shape=Polygon([Vec2(-10, -0.5), Vec2(10, -0.5), Vec2(10, 0.5), Vec2(-10, 0.5)]))

    g = 9.8
    dt = 0.001
    bounced = False
    max_height_after_bounce = 0.0

    for _ in range(3000):
        ball.apply_force(Vec2(0.0, -g * ball.mass))
        ball.integrate(dt)

        contact = circle_vs_polygon(ball, ground)
        if contact is not None:
            resolve_collision(ball, ground, contact, restitution=1.0, friction=0.0)
            bounced = True

        if bounced and ball.velocity.y < 0.0 and max_height_after_bounce == 0.0:
            max_height_after_bounce = ball.position.y

    assert bounced
    # Check return height is close to initial_y = 5.0 (allowing discrete time step error)
    assert pytest.approx(max_height_after_bounce, rel=0.05) == initial_y


def test_inelastic_collision():
    """Verify restitution=0.0 stops bouncing and ball settles on ground."""
    ball = RigidBody(position=(0.0, 2.0), velocity=(0.0, 0.0), mass=1.0, shape=Circle(0.5))
    ground = RigidBody(position=(0.0, 0.0), mass=0.0, shape=Polygon([Vec2(-10, -0.5), Vec2(10, -0.5), Vec2(10, 0.5), Vec2(-10, 0.5)]))

    g = 9.8
    dt = 0.01

    for _ in range(500):
        ball.apply_force(Vec2(0.0, -g * ball.mass))
        ball.integrate(dt)

        contact = circle_vs_polygon(ball, ground)
        if contact is not None:
            resolve_collision(ball, ground, contact, restitution=0.0, friction=0.5)

    # Ball radius = 0.5, ground top edge = 0.5. Ball center should settle near y = 1.0
    assert pytest.approx(ball.position.y, abs=0.05) == 1.0
    assert abs(ball.velocity.y) < 0.1


def test_momentum_conservation_elastic():
    """Verify total momentum before and after elastic collision of two dynamic bodies is conserved."""
    # Body A moving right at (2, 0), Body B stationary at rest
    body_a = RigidBody(position=(0.0, 0.0), velocity=(2.0, 0.0), mass=1.0, shape=Circle(0.5))
    body_b = RigidBody(position=(0.9, 0.0), velocity=(0.0, 0.0), mass=2.0, shape=Circle(0.5))

    p_before = body_a.velocity * body_a.mass + body_b.velocity * body_b.mass

    contact = circle_vs_circle(body_a, body_b)
    assert contact is not None

    resolve_collision(body_a, body_b, contact, restitution=1.0, friction=0.0)

    p_after = body_a.velocity * body_a.mass + body_b.velocity * body_b.mass

    assert pytest.approx(p_after.x, abs=1e-5) == p_before.x
    assert pytest.approx(p_after.y, abs=1e-5) == p_before.y


def test_ball_drop_settle_simulation():
    """Simulate ball drop over 300 steps and print/verify trajectory stability."""
    ball = RigidBody(position=(0.0, 3.0), velocity=(0.0, 0.0), mass=1.0, shape=Circle(0.5))
    ground = RigidBody(position=(0.0, 0.0), mass=0.0, shape=Polygon([Vec2(-10, -0.5), Vec2(10, -0.5), Vec2(10, 0.5), Vec2(-10, 0.5)]))

    g = 9.8
    dt = 0.01

    positions = []
    for _ in range(300):
        ball.apply_force(Vec2(0.0, -g * ball.mass))
        ball.integrate(dt)

        contact = circle_vs_polygon(ball, ground)
        if contact is not None:
            resolve_collision(ball, ground, contact, restitution=0.2, friction=0.4)

        positions.append(ball.position.y)

    # Verify ball settled without penetrating ground (ground surface y=0.5, radius=0.5 -> center=1.0)
    final_y = positions[-1]
    assert final_y >= 0.95  # Did not sink into ground
    assert abs(positions[-1] - positions[-10]) < 0.02  # Settled, no huge jitter
