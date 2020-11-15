import bpy, os
import random
import json
import sys

"""
Add scripts folder to Blender's Python interpreter and reload all scripts.
http://web.purplefrog.com/~thoth/blender/python-cookbook/import-python.html
"""
blender_path = os.path.dirname(bpy.data.filepath)
if not blender_path in sys.path:
    sys.path.append(blender_path)


def render():
    """
    Runs the simulation and outputs render frames and object coordinates
    """

    scene = bpy.data.scenes['Scene']
    cameras = []
    outpost_a_location = (-2.19561, -1.05119, 3.34377)
    outpost_a_rotation = (0.976892, 0.0568127, -0.976659)
    cameras.append(initialise_camera(outpost_a_location, outpost_a_rotation))

    outpost_b_location = (10.1851, 5.63574, 3.34377)
    outpost_b_rotation = (0.976892, 0.0568127, 2.15071)
    cameras.append(initialise_camera(outpost_b_location, outpost_b_rotation))

    # TODO: Make custom robot object and insert it here instead of cube
    # The custom robot objects should created and placed inside the scene
    # and then their mesh names placed inside this array
    mesh_objects = None  # Create the 4 robot cubes through blender
    batch_render(scene, mesh_objects, cameras)


def initialise_camera(coordinates, rotation):
    """
    Returns a wide-angle camera object with given coordinates and rotation that is set to the scene
    """
    outpost_coordinate = coordinates
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=outpost_coordinate, rotation=rotation,
                              scale=(1, 1, 1))
    bpy.context.object.data.lens = 23
    bpy.data.scenes['Scene'].camera = bpy.context.object
    return bpy.context.object


def batch_render(scene, mesh_objects, camera_objects):
    """
    Sets up the render configurations, simulation configurations and then performs individual rendering
    and label saving
    """

    """ Environment Configurations 
    camera_frames = Number of frames for each individual simulation
    num_of_simulations = Number of simulations to run
    spawn_range = 3D range for the spawning of objects
    """
    camera_frames = 10
    num_of_simulations = 3
    spawn_range = [
        (0, 8),
        (0, 4),
        (0.2, 1.2)
    ]
    labels = []

    # Cycles render engine parameters for optimal quality and performance
    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.scene.cycles.samples = 4
    bpy.context.scene.render.tile_x = 256
    bpy.context.scene.render.tile_y = 256
    bpy.context.scene.cycles.max_bounces = 4

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
        # TODO: Ensure spawned objects do not clip the existing walls
        robot.location.x = random.uniform(spawn_range[0][0], spawn_range[0][1])
        robot.location.y = random.uniform(spawn_range[1][0], spawn_range[1][1])
        robot.location.z = random.uniform(spawn_range[2][0], spawn_range[2][1])

    print("spawn_objects runs 1/2")


def render_helper(scene, mesh_objects, camera_objects, camera_frames, file_prefix="render"):
    """
    Sets render configuration, renders the scene and returns a list of label data
    """

    # This stores the coordinates of the robots
    labels = []

    # Rendering
    # https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
    for i in range(0, camera_frames + 1):
        # Changes keyframe to allow passage of time
        scene.frame_set(i)

        # bpy.data.scenes[0].render.use_multiview = True
        # bpy.data.scenes[0].render.views_format = 'MULTIVIEW'
        for index, camera in enumerate(camera_objects):
            filename = 'Simulation{}-frame{}-camera{}.png'.format(str(file_prefix), str(i), index)
            bpy.context.scene.render.filepath = os.path.join(bpy.path.abspath("//renders/"), filename)
            bpy.data.scenes['Scene'].camera = camera
            bpy.ops.render.render(write_still=True)

        label_entry = {
            'image': filename,
            'meshes': {}
        }

        # Get the placement coordinates of each robot
        for robot in mesh_objects:
            label_entry['meshes'][robot.name] = {
                'x': robot.location.x,
                'y': robot.location.y,
                'z': robot.location.z
            }

        labels.append(label_entry)
    print("render runs 2/2")
    return labels


def save_labels_to_file(labels):
    """
    Saves the coordinates of the robot objects to a json for each individual frame
    """
    with open(bpy.path.abspath("\\renders\\labels.json"), 'w+') as f:
        json.dump(labels, f, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    # For testing
    render()
