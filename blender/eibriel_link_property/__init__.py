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
    "name": "eLinkProperty",
    "author": "Eibriel",
    "version": (0,0),
    "blender": (2, 76, 0),
    "location": "View3D > Tools > Relations",
    "description": "Control Panel to manipulate properties",
    "warning": "",
    "wiki_url": "https://github.com/Eibriel/scripts/wiki",
    "tracker_url": "https://github.com/Eibriel/scripts/issues",
    "category": "Eibriel"}

import bpy
from bpy.props import PointerProperty
from bpy.props import FloatVectorProperty
from bpy.props import FloatProperty
from bpy.props import IntProperty

class eLinkedPropertiesPanel(bpy.types.Panel):
    bl_idname = "elinkedproperties"
    bl_label = "eLinkedProperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        #active_obj = context.active_object
        layout = self.layout

        for obj in bpy.data.objects:
            try:
                obj["mov_type"]
            except:
                continue
            if obj["mov_type"] in ["PERSONAJE_RIG", "SOURCE_RIG"]:
                active_obj = obj

                col = layout.column()

                col.label( text= obj.name )
                col.prop(active_obj.eibriel_linkproperty, 'npr_rim_intensity')
                col.prop(active_obj.eibriel_linkproperty, 'npr_rim_color')
                col.prop(active_obj.eibriel_linkproperty, 'npr_ambient_factor')
                col.prop(active_obj.eibriel_linkproperty, 'npr_ambient_color')
                col.prop(active_obj.eibriel_linkproperty, 'npr_level_shadow')
                col.prop(active_obj.eibriel_linkproperty, 'npr_level_light')
                col.prop(active_obj.eibriel_linkproperty, 'npr_shadow_color_factor')
                col.prop(active_obj.eibriel_linkproperty, 'npr_shadow_color')
                col.prop(active_obj.eibriel_linkproperty, 'npr_light_color')

                col.prop(active_obj.eibriel_linkproperty, 'npr_border_thick')
                col.prop(active_obj.eibriel_linkproperty, 'npr_eye_specular_normal', text="")
                col.prop(active_obj.eibriel_linkproperty, 'npr_eye_specular_size')
                #col.prop(active_obj.eibriel_linkproperty, 'npr_specular_color')


class eLinkedProperties(bpy.types.PropertyGroup):
    name = "linked_properties"
    npr_rim_intensity = FloatProperty(name="Rim intensity", min=0, max=1)
    npr_rim_color = FloatVectorProperty(name="Rim color", subtype="COLOR", min=0, max=1)
    npr_ambient_factor = FloatProperty(name="Ambient factor", min=0, max=1)
    npr_ambient_color = FloatVectorProperty(name="Ambient color", subtype="COLOR", min=0, max=1)
    npr_level_shadow = IntProperty(name="Shadow level", min=0, max=10)
    npr_level_light = IntProperty(name="Light level", min=0, max=10)
    npr_shadow_color_factor = FloatProperty(name="Shadow color factor", min=0, max=1)
    npr_shadow_color = FloatVectorProperty(name="Shadow color", subtype="COLOR", min=0, max=1)
    npr_light_color = FloatVectorProperty(name="Light color", subtype="COLOR", min=0, max=1)

    npr_border_thick = FloatProperty(name="Border thickness", min=0, max=1)
    npr_eye_specular_normal = FloatVectorProperty(name="Eye specular position", default=(0.0, 0.0, 1.0), subtype="DIRECTION", min=0, max=1)
    npr_eye_specular_size = FloatProperty(name="Eye specular size", min=0, max=1)
    #npr_specular_color = FloatVectorProperty(name="Specular color", subtype="COLOR", min=0, max=1)


def register():
    bpy.utils.register_class(eLinkedPropertiesPanel)

    bpy.utils.register_class(eLinkedProperties)

    bpy.types.Object.eibriel_linkproperty = PointerProperty(type=eLinkedProperties, name="Linked Properties")


def unregister():
    bpy.utils.unregister_class(eLinkedPropertiesPanel)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
