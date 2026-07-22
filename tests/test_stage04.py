"""Unit tests for Stage 04: Joints and Constraints."""
import math
import pytest
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.joints import DistanceJoint, RevoluteJoint


def test_distance_joint_length_preservation():
    """Verify DistanceJoint keeps anchor distance within small tolerance under gravity."""
    body_a = RigidBody(position=(0.0, 5.0), mass=1.0)
    body_b = RigidBody(position=(3.0, 5.0), mass=1.0)

    joint = DistanceJoint(body_a, (0, 0), body_b, (0, 0), rest_length=3.0)
    g = 9.8
    dt = 0.01

    for _ in range(100):
        body_a.apply_force(Vec2(0.0, -g * body_a.mass))
        body_b.apply_force(Vec2(0.0, -g * body_b.mass))

        body_a.integrate(dt)
        body_b.integrate(dt)

        # Solve joint constraint
        for _ in range(5):
            joint.solve(dt)

    dist = (body_b.position - body_a.position).length()
    assert pytest.approx(dist, abs=0.05) == 3.0


def test_revolute_joint_pendulum_period():
    """Verify RevoluteJoint simple pendulum maintains pin location and oscillation period matches formula."""
    # Pin at (0, 0) static body, pendulum bob at length L=2.0
    L = 2.0
    g = 9.8
    expected_period = 2.0 * math.pi * math.sqrt(L / g)  # approx 2.837 s

    theta0 = 0.1  # small initial angle (rad)
    anchor_b = Vec2(0.0, L)
    bob_pos = Vec2(0.0, 0.0) - anchor_b.rotate(theta0)

    pin_body = RigidBody(position=(0.0, 0.0), mass=0.0)
    bob_body = RigidBody(
        position=bob_pos,
        angle=theta0,
        mass=1.0,
        moment_of_inertia=0.001,
    )

    joint = RevoluteJoint(pin_body, (0, 0), bob_body, (0, L))
    dt = 0.002

    # Measure time between zero position crossings along x
    crossings = []
    prev_x = bob_body.position.x
    sim_time = 0.0

    for _ in range(3000):
        bob_body.apply_force(Vec2(0.0, -g * bob_body.mass))
        bob_body.integrate(dt)

        for _ in range(5):
            joint.solve(dt)

        sim_time += dt
        curr_x = bob_body.position.x

        # Crosses x=0 moving from positive to negative or vice versa
        if (prev_x > 0 and curr_x <= 0) or (prev_x < 0 and curr_x >= 0):
            crossings.append(sim_time)
        prev_x = curr_x

    # Verify pin anchor stays pinned
    bob_anchor_world = bob_body.position + anchor_b.rotate(bob_body.angle)
    assert pytest.approx(bob_anchor_world.x, abs=0.05) == 0.0
    assert pytest.approx(bob_anchor_world.y, abs=0.05) == 0.0

    # Time between crossings[0] and crossings[2] is 2 half-periods = 1 full period
    assert len(crossings) >= 3
    measured_period = crossings[2] - crossings[0]
    assert pytest.approx(measured_period, rel=0.10) == expected_period


def test_revolute_joint_motor_torque():
    """Verify setting motor_torque on RevoluteJoint causes relative rotation between free bodies."""
    body_a = RigidBody(position=(0.0, 0.0), mass=1.0, moment_of_inertia=1.0)
    body_b = RigidBody(position=(2.0, 0.0), mass=1.0, moment_of_inertia=1.0)

    joint = RevoluteJoint(body_a, (1.0, 0.0), body_b, (-1.0, 0.0), motor_torque=5.0)

    dt = 0.01
    joint.apply_motor()

    body_a.integrate(dt)
    body_b.integrate(dt)
    joint.solve(dt)

    # Equal and opposite torques cause opposite angular velocities
    assert body_a.angular_velocity < 0.0
    assert body_b.angular_velocity > 0.0
    assert pytest.approx(body_a.angular_velocity, abs=1e-5) == -body_b.angular_velocity


def test_two_segment_chain_stability():
    """Verify a 2-segment chain hanging from fixed pin swings cleanly without flying apart."""
    pin = RigidBody(position=(0.0, 0.0), mass=0.0)
    seg1 = RigidBody(position=(0.0, -1.0), mass=1.0, moment_of_inertia=0.1)
    seg2 = RigidBody(position=(0.0, -3.0), mass=1.0, moment_of_inertia=0.1)

    joint1 = RevoluteJoint(pin, (0, 0), seg1, (0, 1.0))
    joint2 = RevoluteJoint(seg1, (0, -1.0), seg2, (0, 1.0))

    g = 9.8
    dt = 0.005

    for _ in range(500):
        seg1.apply_force(Vec2(0.0, -g * seg1.mass))
        seg2.apply_force(Vec2(0.0, -g * seg2.mass))

        seg1.integrate(dt)
        seg2.integrate(dt)

        for _ in range(10):
            joint1.solve(dt)
            joint2.solve(dt)

    # Check joint 1 anchor alignment
    anchor1 = seg1.position + Vec2(0, 1.0).rotate(seg1.angle)
    assert pytest.approx(anchor1.x, abs=0.05) == 0.0
    assert pytest.approx(anchor1.y, abs=0.05) == 0.0

    # Check joint 2 anchor alignment
    anchor2_a = seg1.position + Vec2(0, -1.0).rotate(seg1.angle)
    anchor2_b = seg2.position + Vec2(0, 1.0).rotate(seg2.angle)
    assert pytest.approx((anchor2_b - anchor2_a).length(), abs=0.05) == 0.0
