import sys
import bpy
import os

dirname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirname)

from myrobot import AIRobot

import numpy as np
import sys
from random import random
from random import randint
from random import uniform
from math import radians, sqrt
from math import pi as PI

blender_path = os.path.join(os.getcwd(), 'blender_scripts')
if not blender_path in sys.path:
    sys.path.append(blender_path)

from render import render

FIELD_X = 8.08  # length
FIELD_Y = 4.48  # width
BASE_TEXTURE_PATH = os.path.join(os.getcwd(), "assets/base_v1.png")
MARKER_TEXTURE_PATH = os.path.join(os.getcwd(), "assets/vision_markers/")

WALL_WIDTH = 0.410
WALL_HEIGHT = 0.50
WALL_COLOR = (44 / 255, 44 / 255, 44 / 255, 1)  # #2C2C2C hex color
BLOCK_COLOR = (139 / 255, 139 / 255, 139 / 255, 1)  # #8B8B8B hex color


class BlenderEnv():
    # constants

    def __init__(self):
        self.clear_env()

        # Make collections
        self.field_collection = bpy.data.collections.new('field')
        self.lights_collection = bpy.data.collections.new('lights')
        self.blocks_collection = bpy.data.collections.new('blocks')
        self.robots_collection = bpy.data.collections.new('robots')
        
        # Add collections to scene
        bpy.context.scene.collection.children.link(self.field_collection)
        bpy.context.scene.collection.children.link(self.lights_collection)
        bpy.context.scene.collection.children.link(self.blocks_collection)
        bpy.context.scene.collection.children.link(self.robots_collection)

        # Setup environment
        self.make_base()
        self.make_wall()
        self.make_blocks()

        # self.make_lights('POINT', 10, 75, 60)
        # self.make_lights('POINT', 10, 75, 60, light_color=(1,1,1))
        # self.make_lights('SPOT', 10, 150, 60)
        self.make_lights('SPOT', 15, 150, 60, light_color=(1, 1, 1))

        self.robots = {}
        self.robots['r1'] = AIRobot('r1', self.robots_collection, 'blue')
        self.robots['r2'] = AIRobot('r2', self.robots_collection, 'blue')
        self.robots['r3'] = AIRobot('r3', self.robots_collection, 'red')
        self.robots['r4'] = AIRobot('r4', self.robots_collection, 'red')
        
        #random spawning and rotation, for demo only
        for robot in self.robots.values():
            robot_box = 0.2
            x = uniform(robot_box, FIELD_X-robot_box)
            y = uniform(robot_box, FIELD_Y-robot_box)
            theta = uniform(0, 2*PI)
            theta_yaw = uniform(-PI/2, PI/2)
            theta_pitch = uniform(-PI/6, PI/6)

            robot.base_obj.location = (x, y, 0)
            robot.base_obj.delta_rotation_euler = (0, 0, 0)
            robot.barrel_obj.delta_rotation_euler = (theta_pitch, 0, 0)
            robot.yaw_obj.delta_rotation_euler = (0, 0, theta_yaw)


    def make_base(self):
        '''base of field'''
        # make mesh
        vertices = [(0, 0, 0), (FIELD_X, 0, 0), (FIELD_X, FIELD_Y, 0), (0, FIELD_Y, 0)]
        edges = [[0, 1], [1, 2], [2, 3], [3, 0]]
        faces = [(0, 1, 2, 3)]
        base_mesh = bpy.data.meshes.new('base_mesh')
        base_mesh.from_pydata(vertices, edges, faces)
        base_mesh.update()
        # mesh creation
        base_mesh.uv_layers.new(name='base_uv')
        # make object from mesh
        base_obj = bpy.data.objects.new('base_obj', base_mesh)
        # add object to scene collection
        self.field_collection.objects.link(base_obj)

        # create texture on plane for image
        base_mat = bpy.data.materials.new(name="base_mat")
        base_mat.use_nodes = True
        bsdf = base_mat.node_tree.nodes["Principled BSDF"]
        texImage = base_mat.node_tree.nodes.new('ShaderNodeTexImage')
        texImage.image = bpy.data.images.load(BASE_TEXTURE_PATH)
        base_mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

        # ob = bpy.data.objects['new_object']
        base_obj.data.materials.append(base_mat)

    def make_wall(self):
        '''base of field'''
        # make mesh
        w = WALL_WIDTH
        h = WALL_HEIGHT
        vertices = [
            # inside clockwise, bottom
            (0, 0, 0), (0, FIELD_Y, 0), (FIELD_X, FIELD_Y, 0), (FIELD_X, 0, 0),
            # outside clockwise, bottom
            (-w, -w, 0), (-w, FIELD_Y + w, 0), (FIELD_X + w, FIELD_Y + w, 0), (FIELD_X + w, -w, 0),
            # inside clockwise, top
            (0, 0, h), (0, FIELD_Y, h), (FIELD_X, FIELD_Y, h), (FIELD_X, 0, h),
            # outside clockwise, top
            (-w, -w, h), (-w, FIELD_Y + w, h), (FIELD_X + w, FIELD_Y + w, h), (FIELD_X + w, -w, h),
        ]
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7],

            [8, 9], [9, 10], [10, 11], [11, 8],
            [12, 13], [13, 14], [14, 15], [15, 12],
            [8, 12], [9, 13], [10, 14], [11, 15],

            [0, 8], [1, 9], [2, 10], [3, 11], [4, 12], [5, 13], [6, 14], [7, 15],
        ]
        faces = [
            (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
            (8, 9, 13, 12), (9, 10, 14, 13), (10, 11, 15, 14), (11, 8, 12, 15),
            (0, 1, 9, 8), (1, 2, 10, 9), (2, 3, 11, 10), (3, 0, 8, 11),
            (4, 5, 13, 12), (5, 6, 14, 13), (6, 7, 15, 14), (7, 4, 12, 15),
        ]
        # (0,1,2,3,4,5,6,7)]
        wall_mesh = bpy.data.meshes.new('wall_mesh')
        wall_mesh.from_pydata(vertices, edges, faces)
        wall_mesh.update()
        # mesh creation
        wall_mesh.uv_layers.new(name='wall_uv')
        # make object from mesh
        wall_obj = bpy.data.objects.new('wall_obj', wall_mesh)
        # add to collection
        # add object to scene collection
        self.field_collection.objects.link(wall_obj)

        # create texture on plane for image
        wall_mat = bpy.data.materials.new(name="wall_mat")
        wall_mat.use_nodes = True
        bsdf = wall_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = WALL_COLOR
        # texImage = wall_mat.node_tree.nodes.new('ShaderNodeTexImage')

        wall_obj.data.materials.append(wall_mat)

    def make_blocks(self):
        ''' Makes all blocks '''
        # block name, size, location and rotation maps
        block_sizes = {
            'S6': {'x': 1, 'y': 0.2, 'z': 0.4, },
            'S2': {'x': 0.8, 'y': 0.2, 'z': 0.4, },
            'S1': {'x': 0.25, 'y': 0.25, 'z': 0.4, },
        }

        all_blocks = {
            'B1': {'size': block_sizes['S6'],
                   'location': {'x': 0, 'y': 3.280},
                   'rot': 0, },
            'B2': {'size': block_sizes['S2'],
                   'location': {'x': 1.5, 'y': 2.140},
                   'rot': 0, },
            'B3': {'size': block_sizes['S6'],
                   'location': {'x': 1.5 + 0.2, 'y': 0},
                   'rot': radians(90), },
            'B4': {'size': block_sizes['S6'],
                   'location': {'x': 3.54, 'y': 4.48 - 0.935 - 0.2},
                   'rot': radians(0), },
            'B5': {'size': block_sizes['S1'],
                   'location': {'x': 4.04 - (0.25 / sqrt(2)), 'y': 2.240},
                   'rot': radians(-45), },
            'B6': {'size': block_sizes['S6'],
                   'location': {'x': 3.54, 'y': 0.935},
                   'rot': 0, },
            'B7': {'size': block_sizes['S6'],
                   'location': {'x': 8.08 - 1.5 - 0.2, 'y': 4.480},
                   'rot': radians(-90), },
            'B8': {'size': block_sizes['S2'],
                   'location': {'x': 8.08 - 1.5 - 0.8, 'y': 2.140},
                   'rot': 0, },
            'B9': {'size': block_sizes['S6'],
                   'location': {'x': 8.08, 'y': 4.480 - 3.280},
                   'rot': radians(180), },
        }

        def generate_block_mesh(size, block_id):
            'x, y, z are length width and height of block'
            x = size['x']
            y = size['y']
            z = size['z']
            vertices = [
                (0, 0, 0), (0, y, 0), (x, y, 0), (x, 0, 0),
                (0, 0, z), (0, y, z), (x, y, z), (x, 0, z), ]
            edges = [
                [0, 1], [1, 2], [2, 3], [3, 0],
                [4, 5], [5, 6], [6, 7], [7, 4],
                [0, 4], [1, 5], [2, 6], [3, 7]]
            faces = [
                (4, 5, 1, 0), (5, 6, 2, 1), (6, 7, 3, 2), (7, 4, 0, 3),
                (3, 2, 1, 0), (7, 6, 5, 4), ]
            block_mesh = bpy.data.meshes.new('block_{}_mesh'.format(block_id))
            block_mesh.from_pydata(vertices, edges, faces)
            block_mesh.update()
            # mesh creation
            block_mesh.uv_layers.new(name='block_{}_uv'.format(block_id))
            # make object from mesh
            block_obj = bpy.data.objects.new('block_{}_obj'.format(block_id), block_mesh)
            # add object to scene collection
            self.blocks_collection.objects.link(block_obj)
            return block_obj

        self.blocks = {}
        for block in all_blocks:
            self.blocks[block] = generate_block_mesh(all_blocks[block]['size'], block)
            self.blocks[block].delta_location[0] = all_blocks[block]['location']['x']
            self.blocks[block].delta_location[1] = all_blocks[block]['location']['y']
            self.blocks[block].delta_rotation_euler[2] = all_blocks[block]['rot']

        # create texture on plane for image
        block_mat = bpy.data.materials.new(name="block_mat")
        block_mat.use_nodes = True
        bsdf = block_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = BLOCK_COLOR

        # ob = bpy.data.objects['new_object']
        for block_id in self.blocks:
            self.blocks[block_id].data.materials.append(block_mat)

        def get_mat(index):

            # Add random image as texture from image markers
            image_filename = '00' + str(randint(1, 44)).zfill(2) + '.jpg'
            img = bpy.data.images.load(filepath=MARKER_TEXTURE_PATH + image_filename)

            mat = bpy.data.materials.get("mat-" + str(index))
            if mat is None:
                mat = bpy.data.materials.new(name="mat-" + str(index))

            mat.use_nodes = True

            list_of_nodes = mat.node_tree.nodes.keys()
            if "Image Texture" in list_of_nodes:
                old_node = mat.node_tree.nodes["Image Texture"]
                mat.node_tree.nodes.remove(old_node)

            node_tree = bpy.data.materials["mat-" + str(index)].node_tree
            bsdf = mat.node_tree.nodes["Principled BSDF"]
            texture_node = node_tree.nodes.new('ShaderNodeTexImage')

            texture_node.image = img

            mat.node_tree.links.new(bsdf.inputs['Base Color'], texture_node.outputs['Color'])

            return mat

        def generate_marker_plane(index, marker_info):

            name, attributes = marker_info
            vms = 0.15 #vision_marker_size

            m = bpy.data.meshes.new('mesh_' + name)
            d = bpy.data.objects.new('obj_' + name, m)

            verts = [(-vms/2, -vms/2, 0), (-vms/2, vms/2, 0), (vms/2, vms/2, 0), (vms/2, -vms/2, 0)]
            faces = [(0, 1, 2, 3)]
            m.from_pydata(verts, [], faces)
            m.update(calc_edges=True)
            m.uv_layers.new(name='marker_{}_uv'.format(name))

            self.blocks_collection.objects.link(d)
            d.parent = self.blocks['B' + name[1]]
            
            mat = get_mat(index)
            d.delta_location = attributes['location']
            d.delta_rotation_euler = attributes['rotation']
            if d.data.materials:
                d.data.materials[0] = mat
            else:
                d.data.materials.append(mat)
            mod = d.modifiers.new(name + '_mod', 'SOLIDIFY')
            mod.thickness = -0.0005
            mod.offset = 1

        all_markers = {
            'E1-1': {'location': (0.5, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E1-2': {'location': (1.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E1-3': {'location': (0.5, 0.2, 0.2), 'rotation': (radians(-90), radians(180), 0)},

            'E2-1': {'location': (0.4, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E2-2': {'location': (0.8, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E2-3': {'location': (0.4, 0.2, 0.2), 'rotation': (radians(-90), radians(180), 0)},
            'E2-4': {'location': (0.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(90))},
            'E2-5': {'location': (0.4, 0.1, 0.4), 'rotation': (radians(180), radians(180), radians(180))},

            'E3-1': {'location': (0.5, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E3-2': {'location': (1.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E3-3': {'location': (0.5, 0.2, 0.2), 'rotation': (radians(-90), radians(180), 0)},

            'E4-1': {'location': (0.5, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E4-2': {'location': (1.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E4-3': {'location': (0.5, 0.2, 0.2), 'rotation': (radians(-90), radians(180), 0)},
            'E4-4': {'location': (0.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(90))},
            'E4-5': {'location': (0.5, 0.1, 0.4), 'rotation': (radians(180), radians(180), radians(180))},

            'E5-2': {'location': (0.125, 0.25, 0.2), 'rotation': (radians(-90), radians(180), 0)},
            'E5-3': {'location': (0.25, 0.125, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E5-4': {'location': (0.0, 0.125, 0.2), 'rotation': (radians(-90), radians(180), radians(90))},
            'E5-1': {'location': (0.125, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E5-5': {'location': (0.125, 0.125, 0.4), 'rotation': (radians(180), radians(180), radians(180))},

            'E6-1': {'location': (0.5, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E6-2': {'location': (1.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E6-3': {'location': (0.5, 0.2, 0.2), 'rotation': (radians(-90), radians(180), 0)},
            'E6-4': {'location': (0.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(90))},
            'E6-5': {'location': (0.5, 0.1, 0.4), 'rotation': (radians(180), radians(180), radians(180))},

            'E7-1': {'location': (0.5, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E7-2': {'location': (1.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E7-3': {'location': (0.5, 0.2, 0.2), 'rotation': (radians(-90), radians(180), 0)},

            'E8-1': {'location': (0.4, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E8-2': {'location': (0.8, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E8-3': {'location': (0.4, 0.2, 0.2), 'rotation': (radians(-90), radians(180), 0)},
            'E8-4': {'location': (0.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(90))},
            'E8-5': {'location': (0.4, 0.1, 0.4), 'rotation': (radians(180), radians(180), radians(180))},

            'E9-1': {'location': (0.5, 0.0, 0.2), 'rotation': (radians(-90), radians(180), radians(180))},
            'E9-2': {'location': (1.0, 0.1, 0.2), 'rotation': (radians(-90), radians(180), radians(270))},
            'E9-3': {'location': (0.5, 0.2, 0.2), 'rotation': (radians(-90), radians(180), 0)},
        }

        for i, marker in enumerate(all_markers.items()):
            generate_marker_plane(i, marker)

        # add vision markings here!
        # use children relative locations for blocks
        # ie set parent of plane to be a block, then set the delta_location and delta_rotation_euler to desired location

    def make_lights(self, type_of_light, number_of_lights, base_power, power_variance,
                    light_color='random', color_min=0, color_max=1):
        '''Generate randomly placed lights around the base'''

        # Get size of field to generate range of positions
        base_loc = np.array(self.field_collection.objects['base_obj'].location)
        base_dim = np.array(self.field_collection.objects['base_obj'].dimensions)

        for _ in range(number_of_lights):
            # Create light datablock, set attributes
            light_data = bpy.data.lights.new(name="light", type=type_of_light)

            # Set spot light properties
            if type_of_light == 'SPOT':
                light_data.spot_blend = 0.1
                light_data.spot_size = 1.5

            # Calculate random power value
            light_data.energy = random() * power_variance + base_power

            # Choose light color
            if light_color == 'random':
                light_data.color = tuple(np.random.uniform(color_min, color_max, 3))
            else:
                light_data.color = light_color

            # Make new light object
            light_object = bpy.data.objects.new(name="light", object_data=light_data)

            # Set random location near arena
            x_coord = np.random.randint(-base_dim[0] / 1.5, base_dim[0] / 1.5)
            y_coord = np.random.randint(-base_dim[1] / 1.5, base_dim[1] / 1.5)
            z_coord = np.random.randint(3, 6, size=1)
            light_object.location = tuple(base_loc + base_dim / 2 + (x_coord, y_coord, z_coord))

            # add to collections
            self.lights_collection.objects.link(light_object)

    def clear_env(self):
        '''Function to clean environment'''
        data_blocks = [
            bpy.data.meshes,
            bpy.data.materials,
            bpy.data.textures,
            bpy.data.images,
            bpy.data.brushes,
            bpy.data.cameras,
            bpy.data.lights,
            bpy.data.linestyles,
            bpy.data.palettes,
            bpy.data.actions,
            bpy.data.collections,
            bpy.data.grease_pencils,
            bpy.data.texts,
            # bpy.data.scenes
            bpy.data.worlds]
        for block_list in data_blocks:
            for block in block_list:
                block_list.remove(block)


# blender_env = BlenderEnv()
# print(type(__name__))
if __name__ == '__main__' or __name__ == '<run_path>':
    blender_env = BlenderEnv()
    render()
