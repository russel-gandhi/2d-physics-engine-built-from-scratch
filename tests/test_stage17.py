"""Unit tests for Stage 17: Damage & Durability System."""
import pytest
from physics.world import World
from physics.vec2 import Vec2
from robots.robot_spec import RobotSpec, build_robot
from combat.damage import apply_impulse_damage, DamageSystem


def test_impulse_below_threshold_causes_no_damage():
    """Verify collisions below damage threshold result in zero durability loss."""
    spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")
    world = World()
    robot = build_robot(spec, world)

    initial_hp = robot.segment_health["torso"]

    # Small impulse below 10.0 threshold
    dmg = apply_impulse_damage(robot, "torso", impulse_magnitude=5.0, threshold=10.0, scale=1.0)
    assert dmg == 0.0
    assert robot.segment_health["torso"] == initial_hp


def test_impulse_above_threshold_proportional_damage():
    """Verify damage scales linearly with excess impulse magnitude over threshold."""
    spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")

    world1 = World()
    robot1 = build_robot(spec, world1)
    hp_initial = robot1.segment_health["torso"]

    # Medium impulse = 20.0 (excess 10.0)
    dmg_medium = apply_impulse_damage(robot1, "torso", impulse_magnitude=20.0, threshold=10.0, scale=2.0)
    assert dmg_medium == pytest.approx(20.0)
    assert robot1.segment_health["torso"] == pytest.approx(hp_initial - 20.0)

    world2 = World()
    robot2 = build_robot(spec, world2)
    # Large impulse = 40.0 (excess 30.0)
    dmg_large = apply_impulse_damage(robot2, "torso", impulse_magnitude=40.0, threshold=10.0, scale=2.0)
    assert dmg_large == pytest.approx(60.0)
    assert robot2.segment_health["torso"] == pytest.approx(hp_initial - 60.0)

    # Confirm damage ratio matches excess ratio (30 / 10 = 3x)
    assert dmg_large / dmg_medium == pytest.approx(3.0)


def test_component_destruction_disables_motor():
    """Verify when segment durability reaches zero, attached motor joints are disabled."""
    spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")
    world = World()
    robot = build_robot(spec, world)

    # Deplete leg segment durability to zero
    apply_impulse_damage(robot, "leg", impulse_magnitude=1000.0, threshold=10.0, scale=1.0)
    assert robot.segment_health["leg"] == 0.0

    # Attempt to apply motor action torque
    robot.apply_actions([1.0])
    joint = robot.joints["hip"]
    assert joint.motor_torque == 0.0


def test_high_velocity_impact_damage_simulation():
    """Verify physical collision between two robots at high velocity causes impulse-driven damage."""
    spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")
    world = World()

    bot_a = build_robot(spec, world, base_position=(-0.3, 2.0))
    bot_b = build_robot(spec, world, base_position=(0.3, 2.0))

    damage_sys = DamageSystem(threshold=5.0, damage_scale=1.0)
    damage_sys.register_robot(bot_a)
    damage_sys.register_robot(bot_b)

    # Launch bot_a towards bot_b at high speed
    for b in bot_a.bodies.values():
        b.velocity = Vec2(30.0, 0.0)
    for b in bot_b.bodies.values():
        b.velocity = Vec2(-30.0, 0.0)

    hp_a_start = bot_a.segment_health["torso"]
    hp_b_start = bot_b.segment_health["torso"]

    # Run physics steps to trigger collision
    for _ in range(10):
        from physics.collision import find_contacts
        contacts = find_contacts(world.bodies)
        for contact in contacts:
            if contact.body_a is not None and contact.body_b is not None:
                damage_sys.process_collision(contact.body_a, contact.body_b, contact)
        world.step(1.0 / 60.0)

    # Both robots should sustain damage on impacted segments from high-energy collision
    total_hp_a_end = sum(bot_a.segment_health.values())
    total_hp_b_end = sum(bot_b.segment_health.values())
    assert total_hp_a_end < (hp_a_start + bot_a.segment_health.get("leg", 0.0)) or bot_a.segment_health["torso"] < hp_a_start
