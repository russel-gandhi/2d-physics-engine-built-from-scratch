"""Robot spec data model extending creature morphology with physical components and durability tracking."""
from __future__ import annotations
import json
from typing import Any
from physics.vec2 import Vec2
from physics.world import World
from creatures.morphology import CreatureSpec, Creature, build_creature
from robots.components import ComponentSpec, ComponentType


class RobotSpec(CreatureSpec):
    """Robot specification extending CreatureSpec with modular physical components."""

    def __init__(
        self,
        name: str,
        segments: list[Any],
        joints: list[Any],
        components: dict[str, list[ComponentSpec]] | None = None,
    ) -> None:
        super().__init__(name, segments, joints)
        self.components = components if components is not None else {}

    @property
    def total_mass(self) -> float:
        """Calculate total robot mass by summing base segment masses and all component masses."""
        base_mass = sum(seg.mass for seg in self.segments)
        comp_mass = sum(
            comp.mass
            for comp_list in self.components.values()
            for comp in comp_list
        )
        return float(base_mass + comp_mass)

    @property
    def total_durability(self) -> float:
        """Calculate total max durability (HP) across all installed components."""
        return float(sum(
            comp.durability
            for comp_list in self.components.values()
            for comp in comp_list
        ))

    @property
    def total_energy_capacity(self) -> float:
        """Calculate total energy pool capacity from installed energy system components."""
        capacity = 0.0
        for comp_list in self.components.values():
            for comp in comp_list:
                if comp.component_type == ComponentType.ENERGY_SYSTEM:
                    capacity += float(comp.properties.get("capacity", 100.0))
        return capacity if capacity > 0 else 100.0

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["components"] = {
            seg_id: [c.to_dict() for c in comp_list]
            for seg_id, comp_list in self.components.items()
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RobotSpec:
        creature_spec = super().from_dict(data)
        comp_data = data.get("components", {})
        components = {
            seg_id: [ComponentSpec.from_dict(c) for c in c_list]
            for seg_id, c_list in comp_data.items()
        }
        return cls(
            name=creature_spec.name,
            segments=creature_spec.segments,
            joints=creature_spec.joints,
            components=components,
        )

    @classmethod
    def from_json(cls, filepath: str) -> RobotSpec:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class Robot(Creature):
    """Runtime Robot instance extending Creature with health/durability pools and energy management."""

    def __init__(self, spec: RobotSpec, creature: Creature) -> None:
        self.robot_spec = spec
        # Copy underlying physics body references
        self.main_body = creature.main_body
        self.bodies = creature.bodies
        self.joints = creature.joints

        # Initialize durability (health) per segment
        self.segment_health: dict[str, float] = {}
        for seg_id, comp_list in spec.components.items():
            self.segment_health[seg_id] = sum(c.durability for c in comp_list)

        # Initialize energy pool
        self.max_energy = spec.total_energy_capacity
        self.current_energy = self.max_energy

    @property
    def is_chassis_destroyed(self) -> bool:
        """Check if main torso chassis health has reached zero."""
        main_id = self.robot_spec.segments[0].name
        return self.segment_health.get(main_id, 100.0) <= 0.0

    def apply_damage(self, segment_id: str, damage_amount: float) -> None:
        """Apply damage to a specific robot segment."""
        if segment_id in self.segment_health:
            self.segment_health[segment_id] = max(0.0, self.segment_health[segment_id] - damage_amount)

    def consume_energy(self, amount: float) -> bool:
        """Attempt to consume energy. Returns True if sufficient energy was available."""
        if self.current_energy >= amount:
            self.current_energy -= amount
            return True
        return False


def build_robot(
    spec: RobotSpec, world: World, base_position: Vec2 | tuple[float, float] = (0.0, 2.0)
) -> Robot:
    """Build Robot physics bodies and attach component properties."""
    # Apply total calculated component masses to segment specifications for physics integration
    modified_spec = RobotSpec(
        name=spec.name,
        segments=[seg for seg in spec.segments],
        joints=[j for j in spec.joints],
        components=spec.components,
    )

    # Adjust segment masses to include component masses
    for seg in modified_spec.segments:
        comp_mass = sum(c.mass for c in spec.components.get(seg.name, []))
        seg.mass = float(seg.mass + comp_mass)

    creature = build_creature(modified_spec, world, base_position=base_position)
    return Robot(spec, creature)
