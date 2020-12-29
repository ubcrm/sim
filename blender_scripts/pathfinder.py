import math
import bpy
import bmesh
import random
import time
from typing import List
from mathutils.bvhtree import BVHTree

MAX_SPEED = 0.03300
MIN_SPEED = 0.00800
SPEED_DELTA = 0.00132

MAX_SCAN = 0.7
MIN_SCAN = 0.38
SCAN_INCREMENT_DELTA = 0.0040
SCAN_DECREMENT_DELTA = 0.0100
SCAN_DISC_VERTICES = 16

ROTATION_DELTA = ((math.pi * 2.7) / 180)
# Bearings are measured in radians, clockwise from the positive y-axis


def initialise_pathfinder(robot_names: List[str]):
    pathfinder_configs = {}
    other_robots_map = {}
    for robot in robot_names:
        pathfinder_configs[f'{robot}'] = {
            'translation_speed': MAX_SPEED,
            'scan_radius': MAX_SCAN,
            'is_turning': False,
            'rotation_direction': 0,    # 0 means turn clockwise, 1 means turn anti-clockwise
            'bearing': math.pi/2        # Initialised to face up
        }
        other_robot_list = robot_names.copy()
        other_robot_list.remove(robot)
        other_robots_map[robot] = other_robot_list

    obstacle_list = [f'block_B{i}_obj' for i in range(1, 10)]
    obstacle_list.append('wall_obj')

    return pathfinder_configs, obstacle_list, other_robots_map


def object_from_data(data, name, scene):
    """ Initialises the object to the given scene. Helper function for make_disc()"""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(data['verts'], data['edges'], data['faces'])
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    mesh.update(calc_edges=True)
    mesh.validate(verbose=True)
    return obj


def make_ring(segments, radius, x, y, z):
    """ Create the vertex ring for a disc. Helper function for make_disc() """
    vertices = []
    for i in range(segments):
        angle = (math.pi * 2) * i / segments
        vertices.append((x + (radius * math.cos(angle)),
                         y + (radius * math.sin(angle)),
                         z))
    return vertices


def make_disc(name, segments, radius, x, y, z):
    """
    Create a disc

    :param name: Name of the object
    :param segments: Number of segments in the disc
    :param radius: Radius of the disc
    :param x: X-coordinate of the disc
    :param y: Y-coordinate of the disc
    :param z: Z-coordinate of the disc
    """
    data = {
        'verts': make_ring(segments, radius, x, y, z),
        'edges': [],
        'faces': [[i for i in range(segments)]]
    }

    scene = bpy.context.scene
    return object_from_data(data, name, scene)


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


def has_obstacles_in_path(robot: bpy.types.Object, obstacle_list: List[str], config: dict, other_robots: List[str]):
    """
    Checks if there any obstacles in the robot's scanning range using a disc spawned underneath the robot
    """
    scene = bpy.data.scenes[0]

    make_disc('scan_disc', SCAN_DISC_VERTICES, config['scan_radius'],
              robot.location.x, robot.location.y, robot.location.z - 0.01)
    scan_disc = scene.objects['scan_disc']

    # Modify obstacle list to include non-self robots
    obstacles = obstacle_list.copy()
    obstacles.extend(other_robots)

    disc_mesh = bmesh.new()
    disc_mesh.from_mesh(scan_disc.data)
    disc_mesh.transform(scan_disc.matrix_world)
    scan_disc_bvtree = BVHTree.FromBMesh(disc_mesh)

    for obstacle in obstacle_list:
        obstacle_mesh = bmesh.new()
        obstacle_mesh.from_mesh(scene.objects[obstacle].data)
        obstacle_mesh.transform(scene.objects[obstacle].matrix_world)
        obstacle_bvtree = BVHTree.FromBMesh(obstacle_mesh)
        intersections = scan_disc_bvtree.overlap(obstacle_bvtree)
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

    robot.rotation_euler.z = config['bearing'] - math.pi/2
    print(f'{robot.name} has turned to {robot.rotation_euler.z} by {config["bearing"]}')
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
    # start_time = time.time()
    robot_mesh.location.x += (config['translation_speed'] * math.cos(config['bearing']))
    robot_mesh.location.y += (config['translation_speed'] * math.sin(config['bearing']))

    layer = bpy.context.view_layer
    layer.update()

    # print(f'{time.time() - start_time} taken to move robot')


def simulate_motion(robot_names, pathfinder_configs, obstacle_list, other_robots_map, frame):
    scene = bpy.data.scenes[0]
    for robot_name in robot_names:
        robot_mesh = scene.objects[robot_name]
        robot_config = pathfinder_configs[robot_name]
        # start_time = time.time()
        if has_obstacles_in_path(robot_mesh, obstacle_list, robot_config, other_robots_map[robot_name]):
            # print(f'{time.time() - start_time} taken to find obstacles for {robot_name}')
            print(f'{robot_name} found an obstacle at frame-{frame}, slow down and turn!')
            slow_down_and_turn(robot_mesh, robot_config)
        else:
            # print(f'{time.time() - start_time} taken to mark the way clear for {robot_name}')
            print(f'{robot_name} found no obstacles at frame-{frame}, keep moving...')
            continue_moving(robot_config)

        move_robot(robot_mesh, robot_config)
