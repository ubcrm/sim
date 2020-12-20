import math
import bpy
import bmesh
import random
from typing import List
from mathutils.bvhtree import BVHTree

MAX_SPEED = 0.03300
MIN_SPEED = 0.00800
SPEED_DELTA = 0.00102

MAX_SCAN = 0.6
MIN_SCAN = 0.4
SCAN_INCREMENT_DELTA = 0.0040
SCAN_DECREMENT_DELTA = 0.0085
SCAN_DISC_VERTICES = 16

ROTATION_DELTA = ((math.pi * 2.7) / 180)
# Bearings are measured in radians, clockwise from the positive y-axis


def initialise_pathfinder(robot_names: List[str]):
    pathfinder_configs = {}
    other_robots_map = {}
    for robot in robot_names:
        pathfinder_configs[f'{robot}'] = {
            'translation_speed': 0.0350,
            'scan_radius': 0.6,
            'is_turning': False,
            'rotation_direction': 0,                # 0 means turn clockwise, 1 means turn anti-clockwise
            'bearing': 0                            # Initialised to face up
        }
        other_robot_list = robot_names.copy()
        other_robot_list.remove(robot)
        other_robots_map[robot] = other_robot_list
        print(robot)
    print(other_robots_map)
    obstacle_list = [f'block_B{i}_obj' for i in range(1, 10)]
    obstacle_list.append('wall_obj')

    return pathfinder_configs, obstacle_list, other_robots_map


def increment_speed(config: dict):
    new_speed = config['translation_speed'] + SPEED_DELTA
    if new_speed > MAX_SPEED:
        config['translation_speed'] = MAX_SPEED
    else:
        config['translation_speed'] = new_speed


def decrement_speed(config: dict):
    new_speed = config['translation_speed'] - SPEED_DELTA
    if new_speed < MIN_SPEED:
        config['translation_speed'] = MIN_SPEED
    else:
        config['translation_speed'] = new_speed


def increment_scan_range(config: dict):
    new_scan = config['scan_radius'] + SCAN_INCREMENT_DELTA
    if new_scan > MAX_SCAN:
        config['scan_radius'] = MAX_SCAN
    else:
        config['scan_radius'] = new_scan


def decrement_scan_range(config: dict):
    new_scan = config['scan_radius'] - SCAN_DECREMENT_DELTA
    if new_scan < MIN_SCAN:
        config['scan_radius'] = MIN_SCAN
    else:
        config['scan_radius'] = new_scan


def has_obstacles_in_path(robot: bpy.types.Object, obstacle_list: List[str], other_robots: List[str]):
    """
    Checks if there any obstacles in the robot's scanning range
    """
    scene = bpy.data.scenes[0]
    # Add scanning disc
    scan_centre = [robot.location.x, robot.location.y, 0.01]
    bpy.ops.mesh.primitive_cylinder_add(vertices=SCAN_DISC_VERTICES, radius=MAX_SCAN,
                                        depth=0.00005, location=scan_centre)
    scan_disc = bpy.context.object
    scan_disc.name = 'scan_disc'

    # Modify obstacle list to include other robots
    obstacle_list.extend(other_robots)

    copy_mesh = bmesh.new()
    copy_mesh.from_mesh(robot.data)
    copy_mesh.transform(robot.matrix_world)
    robot_bvtree = BVHTree.FromBMesh(copy_mesh)

    for obstacle in obstacle_list:
        obstacle_mesh = bmesh.new()
        obstacle_mesh.from_mesh(scene.objects[obstacle].data)
        obstacle_mesh.transform(scene.objects[obstacle].matrix_world)
        obstacle_bvtree = BVHTree.FromBMesh(obstacle_mesh)
        intersections = robot_bvtree.overlap(obstacle_bvtree)
        if len(intersections) > 0:
            bpy.data.objects.remove(scan_disc, do_unlink=True)
            return True

    bpy.data.objects.remove(scan_disc, do_unlink=True)
    return False


def slow_down_and_turn(robot, config: dict):
    """
    Sets the robot to turning mode if not turning, turns it, then reduces speed and scanning range
    """
    if not config['is_turning']:
        config['is_turning'] = True
        config['rotation_direction'] = random.randint(0, 1)

    if config['rotation_direction'] == 0:
        config['bearing'] += ROTATION_DELTA
    else:
        config['bearing'] -= ROTATION_DELTA

    robot.rotation_euler.z = config['bearing']
    decrement_speed(config)
    decrement_scan_range(config)


def continue_moving(config: dict):
    """
    Stops the robot from turning and attempts to increase its speed and scanning range
    """
    config['is_turning'] = False
    increment_speed(config)
    increment_scan_range(config)


def move_robot(robot_mesh: bpy.types.Object, config: dict):
    """
    Changes the robot's location depending on movement config
    Also updates the environment layer
    """
    robot_mesh.location.x += (config['translation_speed'] * math.sin(config['bearing']))
    robot_mesh.location.y += (config['translation_speed'] * math.cos(config['bearing']))

    layer = bpy.context.view_layer
    layer.update()


def simulate_motion(robot_names, pathfinder_configs, obstacle_list, other_robots_map):
    scene = bpy.data.scenes[0]
    for robot_name in robot_names:
        robot_mesh = scene.objects[robot_name]
        config = pathfinder_configs[robot_name]
        if has_obstacles_in_path(robot_mesh, obstacle_list, other_robots_map[robot_name]):
            slow_down_and_turn(robot_mesh, config)
        else:
            continue_moving(config)

        move_robot(robot_mesh, config)
