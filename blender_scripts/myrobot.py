import bpy
import os

class AIRobot():

    FBX_PATH = 'assets/robot_mesh_split_v1.fbx'

    def __init__(self, name, super_collection, color):
        ''' robot class '''
        old_objs = set(bpy.context.scene.objects)
        bpy.ops.import_scene.fbx(filepath=self.FBX_PATH)
        new_objs = set(bpy.context.scene.objects)
        objs = new_objs - old_objs

        self.robot_collection = bpy.data.collections.new(name+'_collection')

        self.base_obj = None
        self.barrel_obj = None
        self.yaw_obj = None
        self.name = name
        self.all_objs = []
        for obj in objs:
            obj.name = name + '_' + obj.name
            self.all_objs.append(obj)
            if 'base' in obj.name:
                self.base_obj = obj
            if 'body_a' in obj.name:
                self.barrel_obj = obj
            if 'body_b' in obj.name:
                self.yaw_obj = obj

        #recusrively move objects to collection
        def tranverse_tree(t):
            yield t
            for c in t.children:
                yield from tranverse_tree(c)
        
        current_collection = self.base_obj.users_collection[0]
        for c in tranverse_tree(self.base_obj):
            current_collection.objects.unlink(c)
            self.robot_collection.objects.link(c) 
        if color=='blue':
            self.color_panels(color=(0/255, 0/255,255/255, 1))
        elif color == 'red':
            self.color_panels(color=(255/255, 0/255, 0/255, 1))
        self.color_robot()
        self.make_camera()
        
        bpy.ops.object.select_all(action='DESELECT')
        super_collection.children.link(self.robot_collection)

    def make_camera(self):
        #make camera
        cam_data = bpy.data.cameras.new(name=self.name + '_camera')
        cam_obj = bpy.data.objects.new(self.name + '_camera', cam_data)
        cam_obj.parent = self.barrel_obj 
        self.robot_collection.objects.link(cam_obj)
        cam_obj.rotation_euler = [-3.14/2, 3.14, 0]
        cam_obj.delta_location = [-0.026, -0.2, 0.03]

    def color_panels(self, color=(255/255, 0/255, 0/255, 1), strength=4.0):
        '''only can call once, need to remove old materials for multiple add'''
        #create texture on plane for image
        panel_mat = bpy.data.materials.new(name=self.name + '_panel_light_mat')
        panel_mat.use_nodes = True
        out = panel_mat.node_tree.nodes["Material Output"]
        em = panel_mat.node_tree.nodes.new(type="ShaderNodeEmission")

        panel_mat.node_tree.links.new(out.inputs['Surface'], em.outputs['Emission'])
        em.inputs['Color'].default_value = color
        em.inputs['Strength'].default_value = strength

        for obj in self.all_objs:
            if any(x in obj.name for x in ['AM', 'LI']):
                obj.data.materials.append(panel_mat)
    
    def color_robot(self, color=(44/255, 44/255, 44/255, 1)):
        '''only can call once, right now, need to remove old materials for multiple add'''
        robot_mat = bpy.data.materials.new(name=self.name + '_robot_mat')
        robot_mat.use_nodes = True
        bsdf = robot_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs['Base Color'].default_value = color
        for obj in self.all_objs:
            if any(x in obj.name for x in ['base', 'body']):
                obj.data.materials.append(robot_mat)

    def get_collection(self):
        return self.robot_collection

if __name__ == '__main__' or __name__ == '<run_path>':
    coll1 = bpy.data.collections.new('test_coll')
    bpy.context.scene.collection.children.link(coll1)
    a = AIRobot('r1', coll1)    
