"""Unit tests for Stage 06: Creature Morphology Format and Builder."""
import json
import os
import pytest
from physics.vec2 import Vec2
from physics.world import World
from creatures.morphology import CreatureSpec, build_creature


def test_build_creature_from_hopper_preset():
    """Verify loading hopper preset JSON and building creature in World."""
    preset_path = os.path.join("creatures", "presets", "hopper.json")
    spec = CreatureSpec.from_json(preset_path)

    assert spec.name == "Hopper"
    assert len(spec.segments) == 2
    assert len(spec.joints) == 1

    world = World()
    creature = build_creature(spec, world, base_position=(0.0, 3.0))

    assert "torso" in creature.bodies
    assert "leg" in creature.bodies
    assert "hip" in creature.joints
    assert len(world.bodies) == 2
    assert len(world.joints) == 1


def test_creature_action_application_and_simulation():
    """Verify applying motor action drives revolute joint torques and moves creature segments."""
    preset_path = os.path.join("creatures", "presets", "hopper.json")
    spec = CreatureSpec.from_json(preset_path)
    world = World(gravity=(0.0, -9.8))
    creature = build_creature(spec, world, base_position=(0.0, 4.0))

    # Apply positive motor action
    creature.apply_actions([1.0])
    hip_joint = creature.joints["hip"]
    assert pytest.approx(hip_joint.motor_torque) == 30.0

    # Step simulation for 60 frames (1 second)
    dt = 1.0 / 60.0
    for _ in range(60):
        # Oscillate motor action
        creature.apply_actions([1.0])
        world.step(dt)

    # Verify segments reacted to motor torque and gravity
    torso = creature.bodies["torso"]
    leg = creature.bodies["leg"]

    # Torso and leg angles should have changed due to motor torque
    assert abs(torso.angular_velocity) > 0.0 or abs(leg.angular_velocity) > 0.0

    # Check anchor connection between torso and leg remains intact
    anchor_torso_world = torso.position + Vec2(0.0, -0.2).rotate(torso.angle)
    anchor_leg_world = leg.position + Vec2(0.0, 0.5).rotate(leg.angle)
    assert pytest.approx((anchor_leg_world - anchor_torso_world).length(), abs=0.10) == 0.0


def test_data_driven_preset_modification(tmp_path):
    """Verify editing numbers in JSON preset directly alters physical morphology without code changes."""
    # Create custom JSON spec with modified leg vertices (longer leg)
    custom_spec_dict = {
        "name": "LongLegHopper",
        "segments": [
            {
                "name": "torso",
                "shape_type": "polygon",
                "vertices": [[-0.5, -0.2], [0.5, -0.2], [0.5, 0.2], [-0.5, 0.2]],
                "mass": 2.0,
                "moment_of_inertia": 0.2,
                "relative_position": [0.0, 2.0],
                "relative_angle": 0.0,
            },
            {
                "name": "leg",
                "shape_type": "polygon",
                "vertices": [[-0.1, -1.5], [0.1, -1.5], [0.1, 1.5], [-0.1, 1.5]],  # 3m long leg vs 1m original
                "mass": 1.5,
                "moment_of_inertia": 0.3,
                "relative_position": [0.0, 0.5],
                "relative_angle": 0.0,
            },
        ],
        "joints": [
            {
                "name": "hip",
                "joint_type": "revolute",
                "parent_segment": "torso",
                "child_segment": "leg",
                "anchor_parent": [0.0, -0.2],
                "anchor_child": [0.0, 1.5],
                "max_torque": 50.0,
            }
        ],
    }

    json_file = tmp_path / "long_hopper.json"
    json_file.write_text(json.dumps(custom_spec_dict), encoding="utf-8")

    spec = CreatureSpec.from_json(str(json_file))
    world = World()
    creature = build_creature(spec, world)

    leg_shape = creature.bodies["leg"].shape
    # Verify leg vertices match custom JSON spec exactly
    assert leg_shape.vertices[0] == Vec2(-0.1, -1.5)
    assert leg_shape.vertices[2] == Vec2(0.1, 1.5)
