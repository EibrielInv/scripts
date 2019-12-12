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

import bpy
import mathutils
import math

bl_info = {
    "name": "eSnap",
    "author": "Eibriel, Pullusb",
    "version": (0, 2),
    "blender": (2, 81, 0),
    "location": "View3D > Snap (Shift+S)",
    "description": "Snap location, rotation and scale",
    "warning": "",
    "wiki_url": "https://www.patreon.com/posts/esnap-addon-32057418",
    "tracker_url": "https://www.patreon.com/posts/esnap-addon-32056627",
    "category": "Eibriel"}


class EIBRIEL_OT_Snap(bpy.types.Operator):
    """Snap selected object or bone to active object or bone"""
    bl_idname = "esnap.snap"
    bl_label = "eSnap"
    bl_options = {"REGISTER", "UNDO"}

    invert : bpy.props.BoolProperty(name="Invert", default=False)

    @classmethod
    def poll(cls, context):
        epoll = True

        if len(context.selected_objects) == 1 and context.selected_objects[0].type == "ARMATURE":
            pass
        elif len(context.selected_objects) != 2:
            epoll = False

        if len(context.selected_objects) == 1 and (context.selected_objects[0].type != "ARMATURE" or (context.selected_objects[0].type == "ARMATURE" and context.selected_objects[0].mode != "POSE")):
            epoll = False

        for ob in context.selected_objects:
            if ob.mode not in ['OBJECT', 'POSE']:
                epoll = False

        return epoll

    def execute(self, context):
        scn = context.scene

        # OBJECT > OBJECT
        # ARMATURE A BONE > OBJECT
        # OBJECT > ARMATURE A
        # ARMATURE A BONE > ARMATURE B BONE
        # ARMATURE A BONE A > ARMATURE A BONE B

        for ob in context.selected_objects:
            if ob.mode not in ['OBJECT', 'POSE']:
                self.report({'ERROR'}, "Only Object or Pose mode supported")
                return {'CANCELLED'}

        if len(context.selected_objects) == 1 and context.selected_objects[0].type == "ARMATURE":
            pass
        elif len(context.selected_objects) != 2:
            self.report({'ERROR'}, "Exactly 2 objets selected are needed")
            return {'CANCELLED'}

        object_a = context.active_object
        object_b = object_a
        for ao in context.selected_objects:
            if ao != object_a:
                object_b = ao
                break

        if self.invert:
            tmp = object_a
            object_a = object_b
            object_b = tmp

        bone_to = None
        object_to = object_a
        if object_to.type == 'ARMATURE' and object_to.mode == 'POSE':
            bone_to = object_to.pose.bones[object_to.data.bones.active.name]

        bone_from = None
        if len(context.selected_objects) > 1:
            object_from = object_b
            if object_from.type == 'ARMATURE' and object_from.mode == 'POSE':
                bone_from = object_from.pose.bones[object_from.data.bones.active.name]
        elif object_to.type == 'ARMATURE':
            object_from = object_to

            for b in object_from.data.bones:
                if b.select_get() and b.name != bone_to.name:
                    bone_from = object_from.pose.bones[b.name]
                    break
        else:
            self.report({'ERROR'}, "Exactly 2 bones selected are needed")
            return {'CANCELLED'}

        if object_b == object_a and self.invert:
            tmp = bone_from
            bone_from = bone_to
            bone_to = tmp

        if bone_to is not None:
            matrix_to = object_to.matrix_world @ bone_to.matrix
        else:
            matrix_to = object_to.matrix_world

        if bone_from is not None:
            bone_from.matrix = object_from.matrix_world.inverted() @ matrix_to
        else:
            object_from.matrix_world = matrix_to

        return {'FINISHED'}


def button_esnap(self, context):
    self.layout.separator()
    self.layout.operator("esnap.snap")


def pie_button_esnap(self, context):
    layout = self.layout
    pie = layout.menu_pie()
    pie.operator("esnap.snap", text="eSnap", icon='CURSOR')

addon_keymaps = []


def register():
    # TODO
    # Pie menus only support up to 8 elements
    bpy.types.VIEW3D_MT_snap_pie.append(pie_button_esnap)
    bpy.types.VIEW3D_MT_snap.append(button_esnap)
    bpy.utils.register_class(EIBRIEL_OT_Snap)

    # handle the keymap
    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new(EIBRIEL_OT_Snap.bl_idname, 'S', 'PRESS', ctrl=True, oskey=True)
    kmi.properties.invert = False
    addon_keymaps.append((km, kmi))

    km = wm.keyconfigs.addon.keymaps.new(name='Pose', space_type='EMPTY')
    kmi = km.keymap_items.new(EIBRIEL_OT_Snap.bl_idname, 'S', 'PRESS', ctrl=True, oskey=True)
    kmi.properties.invert = False
    addon_keymaps.append((km, kmi))


def unregister():
    # TODO
    # Pie menus only support up to 8 elements
    bpy.types.VIEW3D_MT_snap_pie.remove(pie_button_esnap)
    bpy.types.VIEW3D_MT_snap.remove(button_esnap)
    bpy.utils.unregister_class(EIBRIEL_OT_Snap)

    # handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
