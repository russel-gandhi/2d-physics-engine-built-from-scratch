"""Creature morphology specification, JSON loader, and builder for data-driven creature instantiation."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
from typing import Any
import numpy as np
from physics.vec2 import Vec2
from physics.body import RigidBody
from physics.shapes import Circle, Polygon, Shape
from physics.joints import Joint, RevoluteJoint, DistanceJoint
from physics.world import World


@dataclass
class SegmentSpec:
    """Specification for a single rigid body segment of a creature."""
    name: str
    shape_type: str  # "circle" or "polygon"
    mass: float
    moment_of_inertia: float
    relative_position: list[float]  # [x, y] offset relative to base_position
    relative_angle: float = 0.0
    radius: float | None = None
    vertices: list[list[float]] | None = None


@dataclass
class JointSpec:
    """Specification for a joint connecting two creature segments."""
    name: str
    joint_type: str  # "revolute" or "distance"
    parent_segment: str
    child_segment: str
    anchor_parent: list[float]  # [x, y] in parent local space
    anchor_child: list[float]   # [x, y] in child local space
    max_torque: float = 20.0
    rest_length: float | None = None


@dataclass
class CreatureSpec:
    """Data-driven creature morphology specification."""
    name: str
    segments: list[SegmentSpec]
    joints: list[JointSpec]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreatureSpec:
        """Construct CreatureSpec from dictionary representation."""
        name = data.get("name", data.get("display_name", "Robot"))
        segments = [SegmentSpec(**s) for s in data["segments"]]
        joints = [JointSpec(**j) for j in data["joints"]]
        return cls(name=name, segments=segments, joints=joints)

    @classmethod
    def from_json(cls, json_path: str) -> CreatureSpec:
        """Load CreatureSpec from a JSON file path."""
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)


class Creature:
    """Instantiated creature holding references to its physical bodies and joints."""

    def __init__(
        self,
        spec: CreatureSpec,
        bodies: dict[str, RigidBody],
        joints: dict[str, Joint],
        base_position: Vec2,
    ) -> None:
        """Initialize creature instance with references to world bodies and joints."""
        self.spec = spec
        self.bodies = bodies
        self.joints = joints
        self.base_position = base_position
        self.main_body: RigidBody = list(bodies.values())[0]

    @property
    def motorized_joints(self) -> list[tuple[str, RevoluteJoint, float]]:
        """Return list of (joint_name, revolute_joint, max_torque) for motorized joints."""
        motorized = []
        for j_spec in self.spec.joints:
            if j_spec.joint_type == "revolute" and j_spec.name in self.joints:
                joint = self.joints[j_spec.name]
                if isinstance(joint, RevoluteJoint):
                    motorized.append((j_spec.name, joint, j_spec.max_torque))
        return motorized

    def apply_actions(self, actions: list[float] | np.ndarray) -> None:
        """Apply normalized motor torque actions in [-1.0, 1.0] scaled by max_torque."""
        motorized = self.motorized_joints
        if len(actions) != len(motorized):
            raise ValueError(f"Expected {len(motorized)} actions, got {len(actions)}")

        for i, (_, joint, max_torque) in enumerate(motorized):
            clamped_action = float(np.clip(actions[i], -1.0, 1.0))
            joint.motor_torque = clamped_action * max_torque


def build_creature(
    spec: CreatureSpec,
    world: World,
    base_position: Vec2 | tuple | list = (0.0, 3.0),
) -> Creature:
    """Instantiate a creature described by spec into the physics World."""
    base_pos = base_position if isinstance(base_position, Vec2) else Vec2(base_position)
    bodies: dict[str, RigidBody] = {}
    joints: dict[str, Joint] = {}

    # 1. Create bodies
    for seg_spec in spec.segments:
        if seg_spec.shape_type == "circle":
            if seg_spec.radius is None:
                raise ValueError(f"Circle segment {seg_spec.name} missing radius")
            shape: Shape = Circle(radius=seg_spec.radius)
        elif seg_spec.shape_type == "polygon":
            if seg_spec.vertices is None:
                raise ValueError(f"Polygon segment {seg_spec.name} missing vertices")
            verts = [Vec2(v) for v in seg_spec.vertices]
            shape = Polygon(vertices=verts)
        else:
            raise ValueError(f"Unknown shape_type: {seg_spec.shape_type}")

        pos = base_pos + Vec2(seg_spec.relative_position)
        body = RigidBody(
            position=pos,
            angle=seg_spec.relative_angle,
            mass=seg_spec.mass,
            moment_of_inertia=seg_spec.moment_of_inertia,
            shape=shape,
        )
        bodies[seg_spec.name] = body
        world.add_body(body)

    # 2. Create joints
    for j_spec in spec.joints:
        if j_spec.parent_segment not in bodies or j_spec.child_segment not in bodies:
            raise KeyError(f"Joint {j_spec.name} references missing segment(s)")

        body_a = bodies[j_spec.parent_segment]
        body_b = bodies[j_spec.child_segment]

        if j_spec.joint_type == "revolute":
            joint: Joint = RevoluteJoint(
                body_a=body_a,
                anchor_a=Vec2(j_spec.anchor_parent),
                body_b=body_b,
                anchor_b=Vec2(j_spec.anchor_child),
                motor_torque=0.0,
            )
        elif j_spec.joint_type == "distance":
            joint = DistanceJoint(
                body_a=body_a,
                anchor_a=Vec2(j_spec.anchor_parent),
                body_b=body_b,
                anchor_b=Vec2(j_spec.anchor_child),
                rest_length=j_spec.rest_length,
            )
        else:
            raise ValueError(f"Unknown joint_type: {j_spec.joint_type}")

        joints[j_spec.name] = joint
        world.add_joint(joint)

    return Creature(spec=spec, bodies=bodies, joints=joints, base_position=base_pos)
