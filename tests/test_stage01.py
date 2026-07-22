"""Unit tests for Stage 01: Vec2 math and RigidBody integration."""
import math
import pytest
import numpy as np
from physics.vec2 import Vec2
from physics.body import RigidBody


def test_vec2_basic_math():
    """Test Vec2 addition, subtraction, scalar multiplication, and division."""
    v1 = Vec2(3.0, 4.0)
    v2 = Vec2(1.0, 2.0)

    v_add = v1 + v2
    assert v_add == Vec2(4.0, 6.0)

    v_sub = v1 - v2
    assert v_sub == Vec2(2.0, 2.0)

    v_mul = v1 * 2.0
    assert v_mul == Vec2(6.0, 8.0)
    assert 2.0 * v1 == Vec2(6.0, 8.0)

    v_div = v1 / 2.0
    assert v_div == Vec2(1.5, 2.0)

    assert -v1 == Vec2(-3.0, -4.0)


def test_vec2_dot_cross_length_normalize_rotate():
    """Test Vec2 dot product, 2D cross product, length, normalize, and rotate."""
    v1 = Vec2(1.0, 0.0)
    v2 = Vec2(0.0, 1.0)

    assert v1.dot(v2) == 0.0
    assert v1.dot(v1) == 1.0

    assert v1.cross(v2) == 1.0
    assert v2.cross(v1) == -1.0

    v3 = Vec2(3.0, 4.0)
    assert v3.length() == 5.0
    assert v3.length_sq() == 25.0

    v3_norm = v3.normalize()
    assert pytest.approx(v3_norm.length()) == 1.0
    assert pytest.approx(v3_norm.x) == 0.6
    assert pytest.approx(v3_norm.y) == 0.8

    v1_rot = v1.rotate(math.pi / 2)
    assert pytest.approx(v1_rot.x, abs=1e-7) == 0.0
    assert pytest.approx(v1_rot.y, abs=1e-7) == 1.0


def test_constant_velocity():
    """Verify a body with mass 1, no forces, initial vel (1, 0) moves to (10, 0) after 10 steps of dt=1.0."""
    body = RigidBody(position=(0.0, 0.0), velocity=(1.0, 0.0), mass=1.0)
    dt = 1.0
    for _ in range(10):
        body.integrate(dt)
    assert body.position == Vec2(10.0, 0.0)


def test_projectile_motion_semi_implicit():
    """Verify body under constant gravity matches analytical projectile formula y = y0 - 0.5*g*t^2 within tolerance."""
    body = RigidBody(position=(0.0, 0.0), velocity=(0.0, 0.0), mass=1.0)
    g = 9.8
    dt = 0.001
    total_steps = 1000

    for _ in range(total_steps):
        body.apply_force(Vec2(0.0, -g * body.mass))
        body.integrate(dt)

    t = total_steps * dt
    analytical_y = -0.5 * g * (t ** 2)
    assert pytest.approx(body.position.y, rel=1e-3) == analytical_y


def test_off_center_force_and_torque():
    """Verify off-center apply_force produces torque, and pure torque rotates without translation."""
    body1 = RigidBody(position=(0.0, 0.0), mass=1.0, moment_of_inertia=1.0)
    body1.apply_force(Vec2(1.0, 0.0), point=Vec2(0.0, 1.0))
    assert body1.torque_accum == -1.0
    assert body1.force_accum == Vec2(1.0, 0.0)

    body2 = RigidBody(position=(5.0, 5.0), mass=1.0, moment_of_inertia=2.0)
    body2.apply_torque(4.0)
    body2.integrate(dt=0.5)

    assert pytest.approx(body2.angular_velocity) == 1.0
    assert pytest.approx(body2.angle) == 0.5
    assert body2.position == Vec2(5.0, 5.0)
    assert body2.velocity == Vec2(0.0, 0.0)


def test_static_body_does_not_move():
    """Verify static body (mass=0) does not move under any applied force or torque."""
    body = RigidBody(position=(2.0, 3.0), velocity=(0.0, 0.0), mass=0.0)
    assert body.is_static

    body.apply_force(Vec2(100.0, -500.0), point=Vec2(10.0, 10.0))
    body.apply_torque(50.0)
    body.integrate(dt=1.0)

    assert body.position == Vec2(2.0, 3.0)
    assert body.velocity == Vec2(0.0, 0.0)
    assert body.angle == 0.0
    assert body.angular_velocity == 0.0
