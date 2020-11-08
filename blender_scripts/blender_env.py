import bpy
import os

FIELD_X = 8.08 #length  
FIELD_Y = 4.48 #width
BASE_TEXTURE_PATH = os.path.join(os.getcwd(), "assets/base_v1.png")

WALL_WIDTH = 0.410
WALL_HEIGHT = 0.50
WALL_COLOR = (44/255, 44/255, 44/255, 1) # #2C2C2C hex color

class BlenderEnv():
    # constants

    def __init__(self):
        self.clear_env()
        
        #make field collection
        self.field_collection = bpy.data.collections.new('field')
        bpy.context.scene.collection.children.link(self.field_collection)


        #setup environment
        self.make_base()
        self.make_wall()


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
        # add to collection
        # bpy.context.scene.collection.children.link(self.field_collection)
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


    def make_wall(self):
        '''base of field'''
        # make mesh
        w = WALL_WIDTH
        h = WALL_HEIGHT
        vertices = [
            #inside clockwise, bottom
            (0, 0, 0), (0, FIELD_Y, 0), (FIELD_X, FIELD_Y, 0), (FIELD_X, 0, 0),
            #outside clockwise, bottom
            (-w, -w, 0), (-w, FIELD_Y+w, 0), (FIELD_X+w, FIELD_Y+w, 0), (FIELD_X+w, -w, 0),
            #inside clockwise, top
            (0, 0, h), (0, FIELD_Y, h), (FIELD_X, FIELD_Y, h), (FIELD_X, 0, h),
            #outside clockwise, top
            (-w, -w, h), (-w, FIELD_Y+w, h), (FIELD_X+w, FIELD_Y+w, h), (FIELD_X+w, -w, h),
            ]
        edges = [
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7],
            
            [8, 9], [9, 10], [10, 11], [11, 8],
            [12, 13], [13, 14], [14, 15], [15, 12],
            [8, 12], [9, 13], [10, 14], [11, 15],

            [0,8], [1,9], [2, 10], [3, 11], [4, 12], [5,13], [6,14], [7,15],
            ]
        faces = [ 
            (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7),
            (8,9,13,12), (9,10,14,13), (10,11,15,14), (11,8,12,15),
            (0,1,9,8), (1,2,10,9), (2,3,11,10), (3,0,8,11),
            (4,5,13,12), (5,6,14,13), (6,7,15,14), (7,4,12,15),
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

        #create texture on plane for image
        wall_mat = bpy.data.materials.new(name="wall_mat")
        wall_mat.use_nodes = True
        bsdf = wall_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = WALL_COLOR
        texImage = wall_mat.node_tree.nodes.new('ShaderNodeTexImage')
        # texImage.image = bpy.data.images.load(BASE_TEXTURE_PATH)
        # wall_mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

        # ob = bpy.data.objects['new_object']
        wall_obj.data.materials.append(wall_mat)


    def add_cube(self, size, location):


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
# print(type(__name__))
if __name__ == '__main__' or __name__ == '<run_path>':
    blender_env = BlenderEnv()