import bpy
import os
import numpy as np
from random import random

FIELD_X = 8.08 #length  
FIELD_Y = 4.48 #width
BASE_TEXTURE_PATH = os.path.join(os.getcwd(), "assets/base_v1.png")

class BlenderEnv():
    # constants

    def __init__(self):
        self.clear_env()
        
        # Make collections
        self.field_collection = bpy.data.collections.new('field')
        self.lights_collection = bpy.data.collections.new('lights')
        
        # Add collections to scene
        bpy.context.scene.collection.children.link(self.field_collection)
        bpy.context.scene.collection.children.link(self.lights_collection)

        # Setup environment
        self.make_base()
        self.make_lights('POINT', 10, 75, 60)
        # self.make_lights('SPOT', 10, 150, 60)

    def make_base(self):
        '''base of field'''
        # make mesh
        vertices = [(0, 0, 0), (FIELD_X, 0, 0), (FIELD_X, FIELD_Y, 0), (0, FIELD_Y, 0)]
        edges = [[0, 1], [1, 2], [2, 3], [3, 0]]
        faces = [(0,1,2,3)]
        base_mesh = bpy.data.meshes.new('base_mesh')
        base_mesh.from_pydata(vertices, edges, faces)
        base_mesh.update()
        # mesh creation
        base_mesh.uv_layers.new(name='base_uv')
        # make object from mesh
        base_obj = bpy.data.objects.new('base_obj', base_mesh)
        # add object to scene collection
        self.field_collection.objects.link(base_obj)

        #create texture on plane for image
        base_mat = bpy.data.materials.new(name="base_mat")
        base_mat.use_nodes = True
        bsdf = base_mat.node_tree.nodes["Principled BSDF"]
        texImage = base_mat.node_tree.nodes.new('ShaderNodeTexImage')
        texImage.image = bpy.data.images.load(BASE_TEXTURE_PATH)
        base_mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

        # ob = bpy.data.objects['new_object']
        base_obj.data.materials.append(base_mat)

    def make_lights(self, type_of_light, number_of_lights, base_power, power_variance, color_min=0, color_max=1):
        '''Generate randomly placed lights around the base'''

        # Get size of field to generate range of positions
        base_loc = np.array(self.field_collection.objects['base_obj'].location)
        base_dim = np.array(self.field_collection.objects['base_obj'].dimensions)

        for _ in range(number_of_lights):
            # Create light datablock, set attributes
            light_data = bpy.data.lights.new(name="light", type=type_of_light)
            
            # Calculate random power value
            light_data.energy = random() * power_variance + base_power
            # Generate random color
            light_data.color = tuple(np.random.uniform(color_min, color_max,3))
            # Set blend value for spot lights
            # if type_of_light == "SPOT":
                # light_data.blend = 
            
            # Make new light object
            light_object = bpy.data.objects.new(name="light", object_data=light_data)

            # Set random location near arena
            xy_coord = np.random.randint(-base_dim[0]/2,base_dim[0]/2,size=2)
            z_coord = np.random.randint(3,6,size=1)
            light_object.location = tuple(base_loc + base_dim/2 + np.concatenate((xy_coord,z_coord)))

            #add to collections
            self.lights_collection.objects.link(light_object)

    def clear_env(self):
        '''Function to clean environment'''
        data_blocks= [
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
if __name__ == '__main__':
    blender_env = BlenderEnv()