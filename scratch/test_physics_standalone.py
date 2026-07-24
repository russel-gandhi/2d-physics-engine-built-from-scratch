"""Step 1 Standalone Backend Test: Verify physics world stepping alters robot position and angle under motor torque."""
from physics.world import World
from physics.shapes import Polygon
from physics.vec2 import Vec2
from physics.body import RigidBody
from robots.robot_spec import RobotSpec, build_robot

def run_step_1_test():
    world = World(gravity=(0.0, -9.8))
    # Add ground
    ground_shape = Polygon([Vec2(-30.0, -0.5), Vec2(30.0, -0.5), Vec2(30.0, 0.5), Vec2(-30.0, 0.5)])
    ground = RigidBody(position=(0.0, 0.5), mass=0.0, shape=ground_shape)
    world.add_body(ground)

    spec = RobotSpec.from_json("robots/presets/boxer.json")
    robot = build_robot(spec, world, base_position=(0.0, 4.0))

    pos_before = (robot.main_body.position.x, robot.main_body.position.y)
    angle_before = robot.main_body.angle

    print(f"BEFORE: Main Body Position = ({pos_before[0]:.6f}, {pos_before[1]:.6f}), Angle = {angle_before:.6f}")

    # Set non-zero motor torque on hips/shoulders
    for joint in robot.joints.values():
        if hasattr(joint, 'motor_torque'):
            joint.motor_torque = 50.0

    # Step world 60 times manually
    for step in range(60):
        robot.apply_actions([1.0] * len(robot.joints))
        world.step(1.0 / 60.0)

    pos_after = (robot.main_body.position.x, robot.main_body.position.y)
    angle_after = robot.main_body.angle

    print(f"AFTER 60 STEPS: Main Body Position = ({pos_after[0]:.6f}, {pos_after[1]:.6f}), Angle = {angle_after:.6f}")

    dx = pos_after[0] - pos_before[0]
    dy = pos_after[1] - pos_before[1]
    dangle = angle_after - angle_before
    print(f"DELTA: dx = {dx:.6f}, dy = {dy:.6f}, dangle = {dangle:.6f}")

if __name__ == "__main__":
    run_step_1_test()
