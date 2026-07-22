"""Unit tests for Stage 15: Robot Component System."""
import pytest
from physics.world import World
from creatures.morphology import CreatureSpec
from robots.components import (
    ComponentSpec,
    ComponentType,
    CHASSIS_CORE,
    ARMOR_PLATE,
    STANDARD_BATTERY,
)
from robots.robot_spec import RobotSpec, build_robot


def test_robot_component_summation_properties():
    """Verify total mass, durability, and energy capacity are dynamically computed from components."""
    creature_spec = CreatureSpec.from_json("creatures/presets/hopper.json")

    components = {
        "torso": [CHASSIS_CORE, ARMOR_PLATE, STANDARD_BATTERY],
        "leg": [ComponentSpec("Motor", ComponentType.MOTOR, mass=0.5, durability=80.0)],
    }

    robot_spec = RobotSpec(
        name="TestBot",
        segments=creature_spec.segments,
        joints=creature_spec.joints,
        components=components,
    )

    expected_base_mass = sum(s.mass for s in creature_spec.segments)
    expected_comp_mass = 2.0 + 1.5 + 0.8 + 0.5  # 4.8 kg
    assert robot_spec.total_mass == pytest.approx(expected_base_mass + expected_comp_mass)

    expected_durability = 300.0 + 150.0 + 100.0 + 80.0  # 630.0 HP
    assert robot_spec.total_durability == pytest.approx(expected_durability)
    assert robot_spec.total_energy_capacity == pytest.approx(500.0)


def test_armor_component_increases_mass_and_alters_dynamics():
    """Verify adding heavy armor increases physical mass and alters gravity drop dynamics in simulation."""
    creature_spec = CreatureSpec.from_json("creatures/presets/hopper.json")

    unarmored_spec = RobotSpec(
        name="LightBot",
        segments=creature_spec.segments,
        joints=creature_spec.joints,
        components={"torso": [CHASSIS_CORE]},
    )

    armored_spec = RobotSpec(
        name="HeavyBot",
        segments=creature_spec.segments,
        joints=creature_spec.joints,
        components={
            "torso": [
                CHASSIS_CORE,
                ComponentSpec("Extra Heavy Plating", ComponentType.ARMOR, mass=10.0, durability=500.0),
            ]
        },
    )

    assert armored_spec.total_mass > unarmored_spec.total_mass

    # Run physics simulation comparisons
    w1 = World(gravity=(0.0, -9.8))
    bot_light = build_robot(unarmored_spec, w1, base_position=(0.0, 10.0))

    w2 = World(gravity=(0.0, -9.8))
    bot_heavy = build_robot(armored_spec, w2, base_position=(0.0, 10.0))

    # Apply identical horizontal force and simulate
    bot_light.main_body.apply_force((50.0, 0.0))
    bot_heavy.main_body.apply_force((50.0, 0.0))

    for _ in range(30):
        w1.step(1.0 / 60.0)
        w2.step(1.0 / 60.0)

    # Heavier robot should have lower horizontal acceleration (a = F / m)
    assert bot_light.main_body.position.x > bot_heavy.main_body.position.x


def test_robot_durability_and_energy_tracking():
    """Verify Robot instance tracks segment health pools and energy consumption."""
    creature_spec = CreatureSpec.from_json("creatures/presets/hopper.json")
    components = {"torso": [CHASSIS_CORE, ARMOR_PLATE]}

    spec = RobotSpec(
        name="TestBot",
        segments=creature_spec.segments,
        joints=creature_spec.joints,
        components=components,
    )

    world = World()
    robot = build_robot(spec, world)

    assert not robot.is_chassis_destroyed
    assert robot.segment_health["torso"] == pytest.approx(450.0)

    robot.apply_damage("torso", 450.0)
    assert robot.is_chassis_destroyed

    assert robot.consume_energy(50.0)
    assert robot.current_energy == pytest.approx(50.0)  # default 100 capacity - 50
