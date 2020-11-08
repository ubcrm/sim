import bpy, os
from math import sin, cos, pi
import random
import numpy as np
import json
import sys

"""
Add scripts folder to Blender's Python interpreter and reload all scripts.
http://web.purplefrog.com/~thoth/blender/python-cookbook/import-python.html
"""
dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
import importlib

def render():
    """
    Runs the simulation and outputs render frames and object coordinates
    """

    scene = bpy.data.scenes['Scene']
    camera_object = initialise_camera()
    # TODO: Make custom robot object and insert it here instead of cube
    # The custom robot objects should created and placed inside the scene
    # and then their mesh names placed inside this array
    mesh_objects = None # Create the 4 robot cubes through blender
    batch_render(scene, camera_object, mesh_objects)

def initialise_camera():
    outpost_coordinate = (-2.19561, -1.05119, 3.34377)
    # TODO: Figure out rotation properly and the units of rotation for camera_add()
    camera_rotation = (41.61, -1.91622, -51)
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=outpost_coordinate, rotation=camera_rotation, scale=(1, 1, 1))
    return bpy.data.objects['Camera']


def batch_render(scene, camera_object, mesh_objects):
    """
    Arguments:

        scene: The scene from bpy.data.scenes

        camera_object: The camera object from bpy.data.objects.camera

        mesh_objects: List of robot objects that need to be randomly placed

    """    

    """ Environment Configurations 
    camera_frames = Number of frames for each individual simulation
    num_of_simulations = Number of simulations to run
    spawn_range = 3D range for the spawning of objects
    """
    camera_frames = 30         
    num_of_simulations = 3             
    spawn_range = [       
        (0, 8),
        (0, 4),
        (0.2, 1.2)
    ]
    labels = []


    for i in range(0, num_of_simulations):
        spawn_objects(scene, mesh_objects, spawn_range)
        scene_labels = render(scene, camera_object, mesh_objects, camera_frames, file_prefix=i)
        labels += scene_labels

    save_labels_to_file(labels)   


def spawn_objects(scene, mesh_objects, spawn_range):
    """
    Randomly spawns the given objects in the given range
    """
    for object in mesh_objects:
        # TODO: Ensure spawned objects do not clip the existing walls
        object.location.x = random.uniform(spawn_range[0][0], spawn_range[0][1])
        object.location.y = random.uniform(spawn_range[1][0], spawn_range[1][1])
        object.location.z = random.uniform(spawn_range[2][0], spawn_range[2][1])

    print("spawn_objects runs 1/2")

def render(scene, camera_object, mesh_objects, camera_frames, file_prefix="render"):
    """
    Renders the scene and returns a list of label data
    """

    # This stores the coordinates of the robots
    labels = []

    # Rendering
    # https://blender.stackexchange.com/questions/1101/blender-rendering-automation-build-script
    for i in range(0, camera_frames + 1):
        filename = 'Simulation{}-frame{}.png'.format(str(file_prefix), str(i))
        bpy.context.scene.render.filepath = os.path.join(bpy.path.abspath("//renders/"), filename)

        # Changes keyframe to allow passage of time
        scene.frame_set(i)

        # Cycles render engine parameters for optimal quality and performance
        bpy.context.scene.cycles.device = 'GPU'
        bpy.context.scene.cycles.samples = 4
        bpy.context.scene.render.tile_x = 256
        bpy.context.scene.render.tile_y = 256
        bpy.context.scene.cycles.max_bounces = 4
        bpy.ops.render.render(write_still=True)

        # scene = bpy.data.scenes['Scene']
        label_entry = {
            'image': filename,
            'meshes': {}
        }

        # Get the placement coordinates of each robot
        for object in mesh_objects:
            label_entry['meshes'][object.name] = {
                'x': object.location.x,
                'y': object.location.y,
                'z': object.location.z
            }
            
        labels.append(label_entry)
    print("render runs 2/2")
    return labels

    
def save_labels_to_file(labels):
    """
    Saves the coordinates of the robot objects to a json for each individual frame
    """
    with open(bpy.path.abspath("//renders/labels.json"), 'w+') as f:
        json.dump(labels, f, sort_keys=True, indent=4, separators=(',', ': ')) 