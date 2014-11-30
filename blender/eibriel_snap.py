# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "eSnap",
    "author": "Eibriel",
    "version": (0,1),
    "blender": (2, 72, 0),
    "location": "View3D > Specials",
    "description": "Snap location, rotation and scale",
    "warning": "",
    "wiki_url": "https://github.com/Eibriel/scripts/wiki",
    "tracker_url": "https://github.com/Eibriel/scripts/issues",
    "category": "Eibriel"}

import bpy, mathutils, math


class eibrielSnap (bpy.types.Operator):
    """Snap selected object or bone to active object or bone"""
    bl_idname = "esnap.snap"
    bl_label = "eSnap"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        for ob in context.selected_objects:
            print ("%s %s %s" % (ob.name, ob.type, ob.mode) )
        epoll = True
        
        if len(context.selected_objects)==1 and context.selected_objects[0].type=="ARMATURE":
            pass
        elif len(context.selected_objects) != 2:
            epoll = False
        
        if len(context.selected_objects)==1 and (context.selected_objects[0].type!="ARMATURE" or (context.selected_objects[0].type=="ARMATURE" and context.selected_objects[0].mode!="POSE")):
            epoll = False
        
        for ob in context.selected_objects:
            if not ob.mode in ['OBJECT', 'POSE']:
                epoll = False
                
        return epoll
        
    def execute(self,context):
        scn = context.scene
        
        #OBJECT > OBJECT
        #ARMATURE A BONE > OBJECT
        #OBJECT > ARMATURE A
        #ARMATURE A BONE > ARMATURE B BONE
        #ARMATURE A BONE A > ARMATURE A BONE B
        
        for ob in context.selected_objects:
            if not ob.mode in ['OBJECT', 'POSE']:
                self.report( {'ERROR'}, "Only Object or Pose mode supported" )
                return {'CANCELLED'}
        
        if len(context.selected_objects)==1 and context.selected_objects[0].type=="ARMATURE":
            pass
        elif len(context.selected_objects) != 2:
            self.report( {'ERROR'}, "Exactly 2 objets selected are needed" )
            return {'CANCELLED'}
        
        bone_to = None
        object_to = context.active_object
        if object_to.type == 'ARMATURE' and object_to.mode == 'POSE':
            bone_to = object_to.pose.bones[ object_to.data.bones.active.name ]
        
        bone_from = None
        if len(context.selected_objects) > 1:
            for ao in context.selected_objects:
                if ao != object_to:
                    object_from = ao
                    break
            if object_from.type == 'ARMATURE' and object_from.mode == 'POSE':
                bone_from = object_from.pose.bones[ object_from.data.bones.active.name ]
        elif object_to.type == 'ARMATURE':
            object_from = object_to
            
            for b in object_from.data.bones:
                if b.select and b.name != bone_to.name:
                    bone_from = object_from.pose.bones[ b.name ]
                    break     
        else:
            self.report( {'ERROR'}, "Exactly 2 bones selected are needed" )
            return {'CANCELLED'}
        
        if bone_to != None:
            matrix_to = object_to.matrix_world * bone_to.matrix
        else:
            matrix_to = object_to.matrix_world
        
        
        if bone_from != None:
            bone_from.matrix = object_from.matrix_world.inverted() * matrix_to
        else:
            object_from.matrix_world = matrix_to

        return {'FINISHED'}

def button_esnap(self, context):
    self.layout.operator("esnap.snap")

def register():
    bpy.types.VIEW3D_MT_object_specials.append(button_esnap)
    bpy.types.VIEW3D_MT_armature_specials.append(button_esnap)
    bpy.types.VIEW3D_MT_pose_specials.append(button_esnap)
    bpy.utils.register_module(__name__)
    

def unregister():
    bpy.types.VIEW3D_MT_object_specials.remove(button_esnap)
    bpy.types.VIEW3D_MT_armature_specials.remove(button_esnap)
    bpy.types.VIEW3D_MT_pose_specials.remove(button_esnap)
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
