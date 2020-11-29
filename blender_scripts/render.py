import bpy
import os
import bmesh
import random
import json
import sys
import time
from mathutils.bvhtree import BVHTree

output_path = os.path.join(os.getcwd(), 'renders')
if not os.path.isdir(output_path):
    os.makedirs(output_path)

render_flag = sys.argv[-1]

render_configs = {
    'cameras': [
        {
            'location': (-2.19561, -1.05119, 3.34377),
            'rotation': (0.976892, 0.0568127, -0.976659)
        },
        {
            'location': (10.1851, 5.63574, 3.34377),
            'rotation': (0.976892, 0.0568127, 2.15071)
        }
    ],
    'camera_focal_length': 23,
    'robot_spawn_range': [
        (0, 8),
        (0, 4),
        (0.2, 1.2)
    ],
    'num_of_simulations': 3,
    'frames_per_simulation': 3,
    'GPU_configs': {
        'device': 'GPU',
        'samples': 4,
        'tile_size': 256,
        'max_bounces': 4
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
    cameras.append(initialise_camera(outpost_b_location, outpost_b_rotation))

    # TODO: Make custom robot object and insert it here instead of cube
    # The custom robot objects should created and placed inside the scene
    # and then their mesh names placed inside this array
    mesh_objects = ['r1_base', 'r2_base', 'r3_base', 'r4_base']  # Create the 4 robot cubes through blender
    batch_render(scene, mesh_objects, cameras)
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


def batch_render(scene, mesh_objects, camera_objects):
    """
    Sets up the render configurations, simulation configurations and then performs
    individual rendering and label saving
    Helper for render()
    """

    num_of_simulations = render_configs['num_of_simulations']
    camera_frames = render_configs['frames_per_simulation']
    spawn_range = [
        render_configs['robot_spawn_range'][0],
        render_configs['robot_spawn_range'][1],
        render_configs['robot_spawn_range'][2]
    ]
    labels = []

    # Cycles render engine parameters for optimal quality and performance
    bpy.context.scene.cycles.device = render_configs['GPU_configs']['device']
    bpy.context.scene.cycles.samples = render_configs['GPU_configs']['samples']
    bpy.context.scene.render.tile_x = render_configs['GPU_configs']['tile_size']
    bpy.context.scene.render.tile_y = render_configs['GPU_configs']['tile_size']
    bpy.context.scene.cycles.max_bounces = render_configs['GPU_configs']['max_bounces']

    for i in range(0, num_of_simulations):
        spawn_robots(mesh_objects, spawn_range)
        scene_labels = render_helper(scene, mesh_objects, camera_objects, camera_frames, file_prefix=str(i))
        labels += scene_labels

    save_labels_to_file(labels)


def spawn_robots(mesh_objects, spawn_range):
    """
    Randomly spawns the given robots in the given range
    """

    for robot in mesh_objects:
        never_ran = True
        robot_list = []
        while never_ran or robot_intersects(robot.name):
            robot.location.x = random.uniform(spawn_range[0][0], spawn_range[0][1])
            robot.location.y = random.uniform(spawn_range[1][0], spawn_range[1][1])
            robot.location.z = random.uniform(spawn_range[2][0], spawn_range[2][1])
            never_ran = False

        robot_list.append(robot)

    print("Robots randomly spawned")


def robot_intersects(robot_object: str):
    """
    Returns true if given object overlaps with any existing mesh, false otherwise

    Helper function for spawn_robots()

    :param robot_object: name of the object to check for mesh overlap
    :type robot_object: str
    """

    intersections = []
    scene = bpy.data.scenes[0]

    # Create a copy of the object for matrix transformation
    copy_mesh = bmesh.new()
    copy_mesh.from_mesh(scene.objects[robot_object].data)
    copy_mesh.transform(scene.objects[robot_object].matrix_world)
    robot_bvtree = BVHTree.FromBMesh(copy_mesh)

    # Check if spawned robot overlaps with existing mesh
    for mesh in bpy.data.meshes:
        comparison_mesh = bmesh.new()
        comparison_mesh.from_mesh(scene.objects[mesh].data)
        comparison_mesh.transform(scene.objects[mesh].matrix_world)
        comparison_bvtree = BVHTree.FromBMesh(comparison_mesh)
        intersections.append(comparison_bvtree.overlap(robot_bvtree))
        if intersections:
            return True

    return False


def render_helper(scene, robot_meshes, camera_objects, camera_frames, file_prefix="render"):
    """
    Sets render configuration, renders the scene and returns a list of label data
    """

    # This stores information about each robot, and its coordinates per frame
    labels = []
    for robot in robot_meshes:
        labels.append({
            'robot_name': str(robot.name),
            'robot_coordinates': []
        })

    # Rendering
    # https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
    for frame in range(0, camera_frames):
        # Changes keyframe to allow passage of time
        scene.frame_set(frame)
        for index, camera in enumerate(camera_objects):
            filename = 'Simulation{}-frame{}-camera{}.png'.format(str(file_prefix), str(frame), index)
            camera_path = os.path.join(output_path, f'camera{index + 1}')
            bpy.context.scene.render.filepath = os.path.join(camera_path, filename)
            bpy.data.scenes[0].camera = camera
            bpy.ops.render.render(write_still=True)

        # Get the placement coordinates of each robot
        for index, robot in enumerate(robot_meshes):
            coordinate_entry = {
                'frame': frame,
                'x': robot.location.x,
                'y': robot.location.y,
                'z': robot.location.z
            }
            labels[index]['robot_coordinates'].append(coordinate_entry)

    return labels


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
