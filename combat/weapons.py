"""Weapon component and combat damage scaling system."""
from __future__ import annotations
from enum import Enum
from typing import Any
from robots.components import ComponentSpec, ComponentType
from robots.robot_spec import Robot
from combat.damage import DamageSystem, apply_impulse_damage


class WeaponType(Enum):
    SPINNER = "spinner"
    HAMMER = "hammer"
    FLIPPER = "flipper"
    RAM = "ram"


class Weapon(ComponentSpec):
    """Weapon component specifying damage multiplier and physical attack properties."""

    def __init__(
        self,
        name: str,
        weapon_type: WeaponType,
        damage_multiplier: float = 2.5,
        mass: float = 1.0,
        durability: float = 120.0,
        energy_consumption: float = 2.0,
        properties: dict[str, Any] | None = None,
    ) -> None:
        props = properties if properties is not None else {}
        props["weapon_type"] = weapon_type.value
        props["damage_multiplier"] = damage_multiplier

        super().__init__(
            name=name,
            component_type=ComponentType.WEAPON,
            mass=mass,
            durability=durability,
            energy_consumption=energy_consumption,
            properties=props,
        )
        self.weapon_type = weapon_type
        self.damage_multiplier = damage_multiplier


def get_segment_weapon_multiplier(robot: Robot, segment_name: str) -> float:
    """Check if segment contains an active weapon component and return its damage multiplier."""
    mult = 1.0
    for comp in robot.robot_spec.components.get(segment_name, []):
        if comp.component_type == ComponentType.WEAPON:
            weapon_mult = float(comp.properties.get("damage_multiplier", 2.5))
            if weapon_mult > mult:
                mult = weapon_mult
    return mult


def apply_weapon_impulse_damage(
    striking_robot: Robot,
    striking_segment: str,
    target_robot: Robot,
    target_segment: str,
    impulse_magnitude: float,
    threshold: float = 10.0,
    base_scale: float = 1.0,
) -> float:
    """Calculate and apply physics impulse damage with weapon damage multiplier."""
    multiplier = get_segment_weapon_multiplier(striking_robot, striking_segment)
    scaled_scale = base_scale * multiplier
    return apply_impulse_damage(
        target_robot,
        target_segment,
        impulse_magnitude=impulse_magnitude,
        threshold=threshold,
        scale=scaled_scale,
    )


# Standard Preset Weapon Components
SPINNER_WEAPON = Weapon("High RPM Rotary Blade", WeaponType.SPINNER, damage_multiplier=3.0, mass=1.5, durability=150.0)
HAMMER_WEAPON = Weapon("Pneumatic Crusher Hammer", WeaponType.HAMMER, damage_multiplier=2.5, mass=2.0, durability=180.0)
FLIPPER_WEAPON = Weapon("Hydraulic Flipper Wedge", WeaponType.FLIPPER, damage_multiplier=1.8, mass=1.2, durability=200.0)
RAM_WEAPON = Weapon("Hardened Steel Bumper Ram", WeaponType.RAM, damage_multiplier=2.0, mass=1.8, durability=250.0)
