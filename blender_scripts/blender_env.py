import bpy
import os

FIELD_X = 8.08 #length  
FIELD_Y = 4.48 #width
BASE_TEXTURE_PATH = os.path.join(os.getcwd(), "assets/base_v1.png")

class BlenderEnv():
    # constants

    def __init__(self):
        self.clear_env()
        
        #make field collection
        self.field_collection = bpy.data.collections.new('field')

        #setup environment
        self.make_base()

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
        bpy.context.scene.collection.children.link(self.field_collection)
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

blender_env = BlenderEnv()
if __name__ == '__main__':
    blender_env = BlenderEnv()