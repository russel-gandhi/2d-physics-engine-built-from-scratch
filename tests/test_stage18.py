"""Unit tests for Stage 18: Weapon System & Damage Scaling."""
import pytest
from physics.world import World
from physics.vec2 import Vec2
from robots.components import CHASSIS_CORE
from robots.robot_spec import RobotSpec, build_robot
from combat.weapons import (
    Weapon,
    WeaponType,
    SPINNER_WEAPON,
    get_segment_weapon_multiplier,
    apply_weapon_impulse_damage,
)
from combat.damage import apply_impulse_damage


def test_weapon_component_damage_multiplier_scaling():
    """Verify weapon components increase impulse damage by exact documented damage multiplier."""
    base_spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")

    # Robot without weapon
    unarmed_spec = RobotSpec(
        name="UnarmedBot",
        segments=base_spec.segments,
        joints=base_spec.joints,
        components={"torso": [CHASSIS_CORE]},
    )

    # Robot with Spinner Weapon (multiplier = 3.0)
    armed_spec = RobotSpec(
        name="ArmedBot",
        segments=base_spec.segments,
        joints=base_spec.joints,
        components={"torso": [CHASSIS_CORE, SPINNER_WEAPON]},
    )

    world = World()
    unarmed_bot = build_robot(unarmed_spec, world)
    armed_bot = build_robot(armed_spec, world)

    assert get_segment_weapon_multiplier(unarmed_bot, "torso") == 1.0
    assert get_segment_weapon_multiplier(armed_bot, "torso") == 3.0

    target1 = build_robot(unarmed_spec, world)
    target2 = build_robot(unarmed_spec, world)

    impulse = 30.0
    threshold = 10.0
    # Excess impulse = 20.0

    # Unarmed impact damage (1.0x)
    dmg_unarmed = apply_weapon_impulse_damage(
        unarmed_bot, "torso", target1, "torso", impulse_magnitude=impulse, threshold=threshold
    )
    assert dmg_unarmed == pytest.approx(20.0)

    # Armed weapon impact damage (3.0x)
    dmg_armed = apply_weapon_impulse_damage(
        armed_bot, "torso", target2, "torso", impulse_magnitude=impulse, threshold=threshold
    )
    assert dmg_armed == pytest.approx(60.0)

    # Armed case deals exactly 3x damage
    assert dmg_armed / dmg_unarmed == pytest.approx(3.0)


def test_weapon_limb_swing_simulation_damage():
    """Verify swinging a motorized weapon limb into a target robot deals higher damage than a non-weapon limb."""
    base_spec = RobotSpec.from_json("robots/presets/lightweight_fighter.json")

    unarmed_spec = RobotSpec(
        name="UnarmedSwinger",
        segments=base_spec.segments,
        joints=base_spec.joints,
        components={"leg": [CHASSIS_CORE]},
    )

    weapon_spec = RobotSpec(
        name="WeaponSwinger",
        segments=base_spec.segments,
        joints=base_spec.joints,
        components={"leg": [CHASSIS_CORE, Weapon("Blade", WeaponType.SPINNER, damage_multiplier=2.5)]},
    )

    w1 = World()
    swinger_unarmed = build_robot(unarmed_spec, w1, base_position=(-0.3, 2.0))
    target1 = build_robot(unarmed_spec, w1, base_position=(0.3, 2.0))

    # Swing leg at high torque
    swinger_unarmed.apply_actions([1.0] * len(swinger_unarmed.motorized_joints))

    w2 = World()
    swinger_armed = build_robot(weapon_spec, w2, base_position=(-0.3, 2.0))
    target2 = build_robot(unarmed_spec, w2, base_position=(0.3, 2.0))

    swinger_armed.apply_actions([1.0] * len(swinger_armed.motorized_joints))

    impulse = 40.0
    threshold = 10.0

    dmg1 = apply_weapon_impulse_damage(swinger_unarmed, "leg", target1, "torso", impulse, threshold)
    dmg2 = apply_weapon_impulse_damage(swinger_armed, "leg", target2, "torso", impulse, threshold)

    assert dmg2 > dmg1
    assert dmg2 == pytest.approx(dmg1 * 2.5)
