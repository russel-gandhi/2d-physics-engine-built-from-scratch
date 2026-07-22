"""Robot component type definitions and physical property spec model."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ComponentType(Enum):
    CHASSIS = "chassis"
    ARMOR = "armor"
    LIMB = "limb"
    WHEEL = "wheel"
    SENSOR = "sensor"
    MOTOR = "motor"
    WEAPON = "weapon"
    ENERGY_SYSTEM = "energy_system"


@dataclass
class ComponentSpec:
    """Physical specifications and combat parameters for a robot component."""

    name: str
    component_type: ComponentType
    mass: float = 0.5  # kg
    durability: float = 100.0  # max HP
    energy_consumption: float = 0.0  # Watts/step when active
    properties: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "component_type": self.component_type.value,
            "mass": self.mass,
            "durability": self.durability,
            "energy_consumption": self.energy_consumption,
            "properties": self.properties,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ComponentSpec:
        return cls(
            name=data["name"],
            component_type=ComponentType(data["component_type"]),
            mass=float(data.get("mass", 0.5)),
            durability=float(data.get("durability", 100.0)),
            energy_consumption=float(data.get("energy_consumption", 0.0)),
            properties=data.get("properties", {}),
        )


# Standard Preset Components
CHASSIS_CORE = ComponentSpec("Core Chassis", ComponentType.CHASSIS, mass=2.0, durability=300.0)
ARMOR_PLATE = ComponentSpec("Heavy Steel Armor", ComponentType.ARMOR, mass=1.5, durability=150.0)
HIGH_TORQUE_MOTOR = ComponentSpec("High Torque Servo Motor", ComponentType.MOTOR, mass=0.4, durability=80.0, energy_consumption=2.0)
STANDARD_BATTERY = ComponentSpec("LiPo Battery Cell", ComponentType.ENERGY_SYSTEM, mass=0.8, durability=100.0, properties={"capacity": 500.0, "regen_rate": 1.0})
STANDARD_WHEEL = ComponentSpec("Rubber Traction Wheel", ComponentType.WHEEL, mass=0.6, durability=120.0)
PROXIMITY_SENSOR = ComponentSpec("IR Proximity Sensor", ComponentType.SENSOR, mass=0.1, durability=50.0, energy_consumption=0.1)
