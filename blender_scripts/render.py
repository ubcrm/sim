import bpy
import os
import bmesh
import random
import json
import sys
import time
import math
from mathutils.bvhtree import BVHTree
from typing import List

from pathfinder import simulate_motion, initialise_pathfinder

output_path = os.path.join(os.getcwd(), 'renders')
if not os.path.isdir(output_path):
    os.makedirs(output_path)

render_flag = sys.argv[-1]

render_configs = {
    # The rotation units are in radians, the blender UI will display them in degrees
    'cameras': [
        {
            'location': (-2.19561, -1.05119, 3.34377),
            'rotation': (0.976892, 0.0568127, -0.976659)
        },
        {
            'location': (10.2974, 5.5376, 3.31218),
            'rotation': (0.976892, 0.0568127, 2.15071)
        }
    ],
    'camera_focal_length': 23,
    'spawn_blocks': [
        {
            'block_name': 'A',
            'x_range': (1.7, 2.9),
            'y_range': (3.0, 3.8)
        },
        {
            'block_name': 'B',
            'x_range': (5.2, 5.8),
            'y_range': (3.0, 3.8)
        },
        {
            'block_name': 'C',
            'x_range': (7.4, 7.4),
            'y_range': (1.7, 3.5)
        },
        {
            'block_name': 'D',
            'x_range': (5.3, 6.3),
            'y_range': (0.6, 1.5)
        },
        {
            'block_name': 'E',
            'x_range': (2.4, 2.9),
            'y_range': (0.7, 1.5)
        },
        {
            'block_name': 'F',
            'x_range': (0.76, 0.76),
            'y_range': (1, 2.5)
        }
    ],
    'num_of_simulations': 1,
    'frames_per_simulation': 250,
    'GPU_configs': {
        'device': 'GPU',
        'samples': 2,
        'tile_size': 256,
        'max_bounces': 2,
        'adaptive_sampling': True,
        'enable_caustics': False
    }
}


def render():
    """
    Runs the simulation and outputs render frames and object coordinates
    """
    if str(render_flag) != 'render':
        return
    start_time = time.time()
    scene = bpy.data.scenes[0]
    cameras = []
    outpost_a_location = render_configs['cameras'][0]['location']
    outpost_a_rotation = render_configs['cameras'][0]['rotation']
    cameras.append(initialise_camera(outpost_a_location, outpost_a_rotation))

    outpost_b_location = render_configs['cameras'][1]['location']
    outpost_b_rotation = render_configs['cameras'][1]['rotation']
    # cameras.append(initialise_camera(outpost_b_location, outpost_b_rotation))

    # The custom robot objects should created and placed inside the scene
    # and then their object names placed inside this array
    robot_names = ['r1_base', 'r2_base', 'r3_base', 'r4_base']
    batch_render(scene, robot_names, cameras)
    print(f'Render finished in {time.time() - start_time}!')


def initialise_camera(coordinates, rotation):
    """
    Returns a wide-angle camera object with given coordinates and rotation that is set to the scene
    Helper for render()
    """
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=coordinates,
                              rotation=rotation, scale=[1, 1, 1])
    bpy.context.object.data.lens = render_configs['camera_focal_length']
    bpy.data.scenes[0].camera = bpy.context.object
    return bpy.context.object


def batch_render(scene, robot_names, camera_objects):
    """
    Sets up the render configurations, simulation configurations and then performs
    individual rendering and label saving
    Helper for render()
    """

    num_of_simulations = render_configs['num_of_simulations']
    camera_frames = render_configs['frames_per_simulation']
    labels = []

    # Cycles render engine parameters for optimal quality and performance
    bpy.context.scene.cycles.device = render_configs['GPU_configs']['device']
    bpy.context.scene.cycles.samples = render_configs['GPU_configs']['samples']
    bpy.context.scene.render.tile_x = render_configs['GPU_configs']['tile_size']
    bpy.context.scene.render.tile_y = render_configs['GPU_configs']['tile_size']
    bpy.context.scene.cycles.max_bounces = render_configs['GPU_configs']['max_bounces']

    for i in range(0, num_of_simulations):
        spawn_robots(robot_names, render_configs['spawn_blocks'])
        simulation_labels = render_helper(scene, robot_names, camera_objects, camera_frames, simulation_number=str(i))
        labels.append(simulation_labels)

    save_labels_to_file(labels)


def setup_animation_paths(mesh_objects):
    scene = bpy.data.scenes[0]
    x_transitions = [-0.5, 0.5]
    y_transitions = [-0.25, 0.25]

    for frame in range(0, 100, 50):
        scene.frame_set(frame)
        for robot in mesh_objects:
            mesh = scene.objects[robot]
            if frame == 0:
                mesh.keyframe_insert(data_path='location')
            else:
                mesh.location.x = (mesh.location.x + x_transitions[random.randint(0, 1)])
                mesh.location.y = (mesh.location.y + y_transitions[random.randint(0, 1)])
                mesh.keyframe_insert(data_path='location')


def spawn_robots(robot_objects, spawn_blocks: List[dict]):
    """
    Randomly spawns the given robots in the given blocks
    Helper for batch_render()
    """
    random.shuffle(spawn_blocks)
    scene = bpy.data.scenes[0]
    for index, robot in enumerate(robot_objects):
        robot_mesh = scene.objects[robot]
        spawn_block = spawn_blocks[index]
        robot_mesh.location.x = random.uniform(spawn_block['x_range'][0], spawn_block['x_range'][1])
        robot_mesh.location.y = random.uniform(spawn_block['y_range'][0], spawn_block['y_range'][1])
        robot_mesh.location.z = 0.03

    layer = bpy.context.view_layer
    layer.update()

    print("Robots successfully spawned")


def robot_intersects(robot_object: str, block_list: List[str]):
    """
    Returns true if given robot_object overlaps with any block mesh, false otherwise

    Helper function for spawn_robots()

    :param robot_object: name of the object to check for mesh overlap
    :type robot_object: str
    :param block_list: string list of all the block obstacles in the environment
    :type block_list: List[str]
    """

    scene = bpy.data.scenes[0]

    # Create a copy of the object for matrix transformation
    copy_mesh = bmesh.new()
    copy_mesh.from_mesh(scene.objects[robot_object].data)
    copy_mesh.transform(scene.objects[robot_object].matrix_world)
    robot_bvtree = BVHTree.FromBMesh(copy_mesh)
    # Check if spawned robot overlaps with existing meshes
    for block in block_list:
        comparison_mesh = bmesh.new()
        comparison_mesh.from_mesh(scene.objects[block].data)
        comparison_mesh.transform(scene.objects[block].matrix_world)
        comparison_bvtree = BVHTree.FromBMesh(comparison_mesh)
        intersections = comparison_bvtree.overlap(robot_bvtree)
        if len(intersections) > 0:
            print(f'{block} intersects with {robot_object} at {len(intersections)} points, respawning...')
            return True
    return False


def render_helper(scene, robot_names, camera_objects, camera_frames, simulation_number='render'):
    """
    Sets render configuration, renders the scene and returns a the individual simulation data in a dict
    """

    # This stores information about each robot, and its coordinates per frame
    sim_no = f'simulation_number{simulation_number}'
    simulation_log = {
        sim_no: {
            f'{robot_names[0]}': {},
            f'{robot_names[1]}': {},
            f'{robot_names[2]}': {},
            f'{robot_names[3]}': {}
        }
    }

    pathfinder_configs, obstacle_list, other_robots_map = initialise_pathfinder(robot_names)

    # Rendering
    # https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
    for frame in range(0, camera_frames):
        # Changes keyframe to allow passage of time
        scene.frame_set(frame)
        simulate_motion(robot_names, pathfinder_configs, obstacle_list, other_robots_map, frame)
        for index, camera in enumerate(camera_objects):
            filename = f'Simulation{simulation_number}-frame{str(frame)}-camera{index}.png'
            camera_path = os.path.join(output_path, f'camera{index + 1}')
            bpy.context.scene.render.filepath = os.path.join(camera_path, filename)
            bpy.data.scenes[0].camera = camera
            # Temporary code to reduce testing runtime, default render resolution is 1080p
            scene.render.resolution_x = 960
            scene.render.resolution_y = 540
            bpy.ops.render.render(write_still=True)

        # Get the placement coordinates of each robot
        for index, robot in enumerate(robot_names):
            mesh = bpy.context.scene.objects[robot]
            position = {
                "x": mesh.location.x,
                "y": mesh.location.y,
                "z": mesh.location.z
            }
            simulation_log[sim_no][robot][f'frame_{frame}'] = position

    return simulation_log


def save_labels_to_file(labels):
    """
    Saves the coordinates of the robot objects to a json for each individual frame to a labels.json
    File is overwritten if it already exists
    Helper for render_helper()
    """
    with open(os.path.join(output_path, 'labels.json'), 'w+') as f:
        json.dump(labels, f, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    # For testing
    render()
