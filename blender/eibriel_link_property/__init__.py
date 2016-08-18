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
import mathutils
from bpy.props import PointerProperty
from bpy.props import FloatVectorProperty
from bpy.props import FloatProperty
from bpy.props import IntProperty


class eLinkedAddKeys (bpy.types.Operator):
    """Agrega claves de animación a las propiedades"""
    bl_idname = "elinked.add_keys"
    bl_label = "Add Keyframes"

    def execute(self,context):
        obj = context.active_object

        if obj.type != 'ARMATURE':
            self.report( {'ERROR'}, "El objeto activo debe ser un Armature" )
            return {'CANCELLED'}

        if obj.animation_data.action == None:
            self.report( {'ERROR'}, "El Armature debe tener una acción" )
            return {'CANCELLED'}

        ofc = obj.animation_data.action.fcurves
        scn = context.scene

        keys = {}
        keys['pose.bones["light_main"].location'] = 0
        keys['pose.bones["light_main"].rotation_quaternion'] = 0
        keys['pose.bones["light_main"].scale'] = 0
        #
        keys['pose.bones["light_rim"].location'] = 0
        keys['pose.bones["light_rim"].rotation_quaternion'] = 0
        keys['pose.bones["light_rim"].scale'] = 0
        #
        keys['pose.bones["light_main omni"].location'] = 0
        keys['pose.bones["light_main omni"].rotation_quaternion'] = 0
        keys['pose.bones["light_main omni"].scale'] = 0
        #
        keys['pose.bones["light_secondary"].location'] = 0
        keys['pose.bones["light_secondary"].rotation_quaternion'] = 0
        keys['pose.bones["light_secondary"].scale'] = 0


        keys['eibriel_linkproperty.npr_rim_intensity'] = obj.eibriel_linkproperty.npr_rim_intensity
        keys['eibriel_linkproperty.npr_rim_color'] = obj.eibriel_linkproperty.npr_rim_color

        keys['eibriel_linkproperty.npr_ambient_factor'] = obj.eibriel_linkproperty.npr_ambient_factor
        keys['eibriel_linkproperty.npr_ambient_color'] = obj.eibriel_linkproperty.npr_ambient_color

        keys['eibriel_linkproperty.npr_level_shadow'] = obj.eibriel_linkproperty.npr_level_shadow
        keys['eibriel_linkproperty.npr_level_light'] = obj.eibriel_linkproperty.npr_level_light
        keys['eibriel_linkproperty.npr_shadow_smoothness'] = obj.eibriel_linkproperty.npr_shadow_smoothness
        keys['eibriel_linkproperty.npr_shadow_color_factor'] = obj.eibriel_linkproperty.npr_shadow_color_factor
        keys['eibriel_linkproperty.npr_shadow_color'] = obj.eibriel_linkproperty.npr_shadow_color
        keys['eibriel_linkproperty.npr_light_color'] = obj.eibriel_linkproperty.npr_light_color
        keys['eibriel_linkproperty.npr_secondary_light_color'] = obj.eibriel_linkproperty.npr_secondary_light_color
        keys['eibriel_linkproperty.npr_secondary_light_factor'] = obj.eibriel_linkproperty.npr_secondary_light_factor
        keys['eibriel_linkproperty.npr_tertiary_light_color'] = obj.eibriel_linkproperty.npr_tertiary_light_color
        keys['eibriel_linkproperty.npr_tertiary_light_offset'] = obj.eibriel_linkproperty.npr_tertiary_light_offset

        keys['eibriel_linkproperty.npr_main_point_intensity'] = obj.eibriel_linkproperty.npr_main_point_intensity
        keys['eibriel_linkproperty.npr_main_sun_intensity'] = obj.eibriel_linkproperty.npr_main_sun_intensity
        keys['eibriel_linkproperty.npr_main_samples'] = obj.eibriel_linkproperty.npr_main_samples
        keys['eibriel_linkproperty.npr_main_point_samples'] = obj.eibriel_linkproperty.npr_main_point_samples
        keys['eibriel_linkproperty.npr_main_point_size'] = obj.eibriel_linkproperty.npr_main_point_size

        keys['eibriel_linkproperty.npr_specular_color'] = obj.eibriel_linkproperty.npr_specular_color
        keys['eibriel_linkproperty.npr_specular_factor'] = obj.eibriel_linkproperty.npr_specular_factor

        keys['eibriel_linkproperty.npr_sss_factor'] = obj.eibriel_linkproperty.npr_sss_factor
        keys['eibriel_linkproperty.npr_ao_factor'] = obj.eibriel_linkproperty.npr_ao_factor
        keys['eibriel_linkproperty.npr_mouth_shadow'] = obj.eibriel_linkproperty.npr_mouth_shadow
        keys['eibriel_linkproperty.npr_enable_bump'] = obj.eibriel_linkproperty.npr_enable_bump

        keys['eibriel_linkproperty.npr_eye_specular_normal'] = obj.eibriel_linkproperty.npr_eye_specular_normal
        keys['eibriel_linkproperty.npr_eye_specular_size'] = obj.eibriel_linkproperty.npr_eye_specular_size

        keys['eibriel_linkproperty.npr_iris_specular_normal'] = obj.eibriel_linkproperty.npr_iris_specular_normal
        keys['eibriel_linkproperty.npr_iris_selfillumination'] = obj.eibriel_linkproperty.npr_iris_selfillumination

        keys['eibriel_linkproperty.npr_lens_refraction_color'] = obj.eibriel_linkproperty.npr_lens_refraction_color
        keys['eibriel_linkproperty.npr_lens_refraction_color_factor'] = obj.eibriel_linkproperty.npr_lens_refraction_color_factor
        keys['eibriel_linkproperty.npr_lens_refraction_ior'] = obj.eibriel_linkproperty.npr_lens_refraction_ior

        keys['eibriel_linkproperty.npr_lens_reflection_color'] = obj.eibriel_linkproperty.npr_lens_reflection_color
        keys['eibriel_linkproperty.npr_lens_reflection_color_factor'] = obj.eibriel_linkproperty.npr_lens_reflection_color_factor
        keys['eibriel_linkproperty.npr_lens_reflection_factor'] = obj.eibriel_linkproperty.npr_lens_reflection_factor

        keys['eibriel_linkproperty.npr_hair_selfillumination'] = obj.eibriel_linkproperty.npr_hair_selfillumination
        keys['eibriel_linkproperty.npr_hair_opacity'] = obj.eibriel_linkproperty.npr_hair_opacity
        keys['eibriel_linkproperty.npr_hair_thickness'] = obj.eibriel_linkproperty.npr_hair_thickness

        keys['eibriel_linkproperty.npr_rim_samples'] = obj.eibriel_linkproperty.npr_rim_samples
        keys['eibriel_linkproperty.npr_secondary_samples'] = obj.eibriel_linkproperty.npr_secondary_samples
        keys['eibriel_linkproperty.npr_secondary_size'] = obj.eibriel_linkproperty.npr_secondary_size

        def get_ffc(ind, ai=0):
            ffc = None
            for fc in ofc:
                if ind == fc.data_path and ai == fc.array_index:
                    ffc = fc
            if ffc == None:
                ofc.new ( ind, ai )
                ffc = ofc[len(ofc )-1]
            return ffc

        for ind, k in keys.items():
            tmpind = ind
            if tmpind[:1] != '[':
                tmpind = tmpind
            key_data = eval("obj.{}".format(tmpind))

            if type(key_data) in [mathutils.Color, mathutils.Vector]:
                for ai in range(0,3):
                    ffc = get_ffc(ind, ai)
                    ffc.keyframe_points.insert(frame=scn.frame_current, value = key_data[ai])
            elif type(key_data) in [mathutils.Quaternion]:
                for ai in range(0,4):
                    ffc = get_ffc(ind, ai)
                    ffc.keyframe_points.insert(frame=scn.frame_current, value = key_data[ai])
            else:
                ffc = get_ffc(ind)
                ffc.keyframe_points.insert(frame=scn.frame_current, value = key_data)

        return {'FINISHED'}


class eLinkedPropertiesPanel(bpy.types.Panel):
    bl_idname = "elinkedproperties"
    bl_label = "eLinkedProperties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        #active_obj = context.active_object
        layout = self.layout

        #for obj in bpy.data.objects:
        if context.active_object and "mov_type" in context.active_object:
            obj = context.active_object
            try:
                obj["mov_type"]
            except:
                pass
                #continue
            if obj["mov_type"] in ["PERSONAJE_LIGHTRIG", "INTERACTIVO_LIGHTRIG", "SOURCE_LIGHTRIG"]:
                active_obj = obj

                col = layout.column()

                col.label( text= "# {0} #".format(obj.name) )
                col.separator()
                col.operator("elinked.add_keys", icon="KEY_HLT")
                col.separator()
                col.label( text= "-Despegue-" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_rim_intensity', text="Despegue intensidad")
                col.prop(active_obj.eibriel_linkproperty, 'npr_rim_color', text="Despegue color")
                #col.prop(active_obj.eibriel_linkproperty, 'npr_rim_smoothness', text="Despegue tipo offset")
                col.separator()
                col.label( text= "-Ambiente-" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_ambient_factor', text="Ambiente factor")
                col.prop(active_obj.eibriel_linkproperty, 'npr_ambient_color', text="Ambiente color")
                col.separator()
                col.label( text= "-Luz y Sombra-" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_level_shadow', text="Nivel sombra")
                col.prop(active_obj.eibriel_linkproperty, 'npr_level_light', text="Nivel luz")
                col.prop(active_obj.eibriel_linkproperty, 'npr_shadow_smoothness', text="Sombra suavidad offset")
                col.prop(active_obj.eibriel_linkproperty, 'npr_shadow_color_factor', text="Coloreado sombra, luz factor")
                col.prop(active_obj.eibriel_linkproperty, 'npr_shadow_color', text="Sombra color")
                col.prop(active_obj.eibriel_linkproperty, 'npr_light_color', text="Luz color")
                col.prop(active_obj.eibriel_linkproperty, 'npr_secondary_light_color', text="Luz secundaria color")
                col.prop(active_obj.eibriel_linkproperty, 'npr_secondary_light_factor', text="Luz secundaria factor")
                col.prop(active_obj.eibriel_linkproperty, 'npr_tertiary_light_color', text="Luz sobre Luz color")
                col.prop(active_obj.eibriel_linkproperty, 'npr_tertiary_light_offset', text="Luz sobre Luz offset")
                #col.prop(active_obj.eibriel_linkproperty, 'npr_border_thick', text="Grosor de borde")
                col.label( text= "-Principal-" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_main_point_intensity', text="Intensidad principal punto")
                col.prop(active_obj.eibriel_linkproperty, 'npr_main_sun_intensity', text="Intensidad principal sol")
                col.prop(active_obj.eibriel_linkproperty, 'npr_main_samples', text="Samples luz principal")
                col.prop(active_obj.eibriel_linkproperty, 'npr_main_point_samples', text="Samples luz principal punto")
                col.prop(active_obj.eibriel_linkproperty, 'npr_main_point_size', text="Tamaño luz pincipal punto")
                col.separator()
                col.label( text= "-Especular-" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_specular_color', text="Especular color")
                col.prop(active_obj.eibriel_linkproperty, 'npr_specular_factor', text="Especular factor")
                col.separator()
                col.label( text= "-Extras-" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_sss_factor', text="SSS factor")
                col.prop(active_obj.eibriel_linkproperty, 'npr_ao_factor', text="AO factor")
                col.prop(active_obj.eibriel_linkproperty, 'npr_mouth_shadow', text="Boca sombra")
                col.prop(active_obj.eibriel_linkproperty, 'npr_enable_bump', text="Habilitar Bump")
                col.separator()
                col.label( text= "-Ojos-" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_eye_specular_normal', text="")
                col.prop(active_obj.eibriel_linkproperty, 'npr_eye_specular_size', text="Brillo especular tamaño")
                col.label( text= "Iris:" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_iris_specular_normal', text="")
                col.prop(active_obj.eibriel_linkproperty, 'npr_iris_selfillumination', text="Autoiluminacion iris")
                #col.prop(active_obj.eibriel_linkproperty, 'npr_specular_color')
                col.separator()
                col.label( text= "-Anteojos-" )
                col.prop(active_obj.eibriel_linkproperty, 'npr_lens_refraction_color', text="Color refracción")
                col.prop(active_obj.eibriel_linkproperty, 'npr_lens_refraction_color_factor', text="Color refracción factor")
                col.prop(active_obj.eibriel_linkproperty, 'npr_lens_refraction_ior', text="IOR")
                col.separator()
                col.prop(active_obj.eibriel_linkproperty, 'npr_lens_reflection_color', text="Color reflección")
                col.prop(active_obj.eibriel_linkproperty, 'npr_lens_reflection_color_factor', text="Color reflección factor")
                col.prop(active_obj.eibriel_linkproperty, 'npr_lens_reflection_factor', text="Reflección factor")
                col.separator()
                col.label( text= "-Pelos-" )
                col.separator()
                col.prop(active_obj.eibriel_linkproperty, 'npr_hair_selfillumination', text="Autoiluminación del pelo")
                col.prop(active_obj.eibriel_linkproperty, 'npr_hair_opacity', text="Opacidad del pelo")
                col.prop(active_obj.eibriel_linkproperty, 'npr_hair_thickness', text="Grosor del pelo")
                col.label( text= "-Luces-" )
                col.separator()
                col.prop(active_obj.eibriel_linkproperty, 'npr_rim_samples', text="Samples luz despegue")
                col.prop(active_obj.eibriel_linkproperty, 'npr_secondary_samples', text="Samples luz secundaria")
                col.prop(active_obj.eibriel_linkproperty, 'npr_secondary_size', text="Tamaño luz secundaria")




class eLinkedProperties(bpy.types.PropertyGroup):
    name = "linked_properties"
    npr_rim_intensity = FloatProperty(name="Rim intensity", description="Intensidad del despegue, entre 0 y 1", min=0, max=1)
    npr_rim_color = FloatVectorProperty(name="Rim color", subtype="COLOR", description="Color de la luz de despegue ", min=0, max=1)
    npr_ambient_factor = FloatProperty(name="Ambient factor", description="Intensidad de la luz ambiental, entre 0 y 1", min=0, max=1)
    npr_ambient_color = FloatVectorProperty(name="Ambient color", description="Color de la luz ambiental", subtype="COLOR", min=0, max=1)
    npr_level_shadow = IntProperty(name="Shadow level", description="Nivel en la sombra, entre 0 y 10", min=0, max=20)
    npr_level_light = IntProperty(name="Light level", description="Nivel en la luz, entre 0 y 10", min=0, max=20)
    npr_shadow_color_factor = FloatProperty(name="Shadow color factor", description="Peso del color de sombra sobre la sombra, entre 0 y 1", min=0, max=1)
    npr_shadow_color = FloatVectorProperty(name="Shadow color", description="Color para la zona de sombra", subtype="COLOR", min=0, max=1)
    npr_light_color = FloatVectorProperty(name="Light color", description="Color para la zona de luz", subtype="COLOR", min=0, max=1)

    npr_border_thick = FloatProperty(name="Border thickness", description="Grosor de las lineas de borde (sin uso)", min=0, max=1)
    npr_eye_specular_normal = FloatVectorProperty(name="Eye specular position", description="Posición del brillo especuar en el ojo", default=(0.0, 0.0, 1.0), subtype="DIRECTION", min=0, max=1)
    npr_iris_specular_normal = FloatVectorProperty(name="Iris specular position", description="Posición del brillo especuar en el iris", default=(0.0, 0.0, 1.0), subtype="DIRECTION", min=0, max=1)
    npr_iris_selfillumination = FloatProperty(name="Iris selfillumination", description="Autoiluminacion del Iris", min=0, default=1)
    npr_eye_specular_size = FloatProperty(name="Eye specular size", description="Tamaño del brillo especular del ojo, entre 0 y 1", min=0, max=1)
    #npr_specular_color = FloatVectorProperty(name="Specular color", subtype="COLOR", min=0, max=1)

    npr_shadow_smoothness = FloatProperty(name="Shadow smoothness", description="Offset del valor local, -1 lleva todo a 0, 1 lleva todo a 1, 0 deja todo como está", default=0, min=-1, max=1)
    npr_specular_color = FloatVectorProperty(name="Specular color", description="Color del especular", subtype="COLOR", min=0, max=1)
    npr_specular_factor = FloatProperty(name="Specular factor", description="Factor del brillo especular, entre 0 y 1", min=0, max=1)
    npr_ao_factor = FloatProperty(name="Ambient Occlusion factor", description="Nivel de AO, entre 0 y 1", default=0.5, min=0, max=1)
    npr_sss_factor = FloatProperty(name="SSS factor", description="Nivel de SSS, entre 0 y 1", default=1, min=0, max=1)
    npr_rim_smoothness = FloatProperty(name="Rim smoothness", description="Offset del valor local, -1 lleva todo a 0, 1 lleva todo a 1, 0 deja todo como está", default=0, min=-1, max=1)

    npr_secondary_light_color = FloatVectorProperty(name="Secondary light color", description="Color de la luz secundaria", subtype="COLOR", min=0, max=1)
    npr_secondary_light_factor = FloatProperty(name="Secondary light factor", description="Intensidad de la luz secundaria, entre 0 e infinito", min=0)

    npr_mouth_shadow = FloatProperty(name="Mouth shadow", description="Nivel de oscuridad en el interior de la boca, entre 0 y 1", default=0.5, min=0, max=1)

    npr_tertiary_light_color = FloatVectorProperty(name="Tertiary light color", description="Color de la Luz sobre Luz", subtype="COLOR", min=0, max=1)
    npr_tertiary_light_offset = FloatProperty(name="Tertiary light offset", description="Multiplicador del valor local, entre 0 e infinito", default=0, min=0)
    npr_enable_bump = IntProperty(name="Enable Bump", description="1 activa el Bump, 0 lo desactiva", default=1, min=0, max=1)

    npr_lens_refraction_color = FloatVectorProperty(name="Lens refraction color", description="Color de la refracción cristal de los anteojos", subtype="COLOR", min=0, max=1, default=(0.084062, 0.269913, 0.398288))
    npr_lens_refraction_color_factor = FloatProperty(name="Lens refraction color factor", description="Nivel de mezcla del color de la refracción del cristal, entre 0 y 1", default=0, min=0, max=1)
    npr_lens_refraction_ior = FloatProperty(name="Lens IOR", description="IOR del cristal, entre 0 y 1", default=1.05, min=0)

    npr_lens_reflection_color = FloatVectorProperty(name="Lens reflection color", description="Color de la reflección cristal de los anteojos", subtype="COLOR", min=0, max=1, default=(0.199071, 0.670155, 1.0))
    npr_lens_reflection_color_factor = FloatProperty(name="Lens reflection color factor", description="Nivel de mezcla del color de la reflección del cristal, entre 0 y 1", default=1, min=0, max=1)
    npr_lens_reflection_factor = FloatProperty(name="Lens reflection factor", description="Nivel de reflección", default=1, min=0, max=1)

    npr_rim_samples = IntProperty(name="Rim light samples", description="Cantidad de samples para la luz de despegue", default=12, min=0)
    npr_secondary_samples = IntProperty(name="Secondary light samples", description="Cantidad de samples para la luz secundaria", default=1, min=0)
    npr_secondary_size = FloatProperty(name="Secondary light size", description="Tamaño la luz secundaria, a mayor tamaño mas suave es la sombra", default=0.1, min=0)

    npr_hair_selfillumination = FloatProperty(name="Hair self illumination", description="Autoiluminación de los pelos", default=0.2, min=0, max=1)
    npr_hair_opacity = FloatProperty(name="Hair opacity", description="Opacidad de los pelos", default=1, min=0, max=1)
    npr_hair_thickness = FloatProperty(name="Hair thickness", description="Grosor de los pelos", default=0.5)

    npr_main_samples = IntProperty(name="Main light samples", description="Cantidad de samples para la luz principal", default=12, min=0)

    npr_main_point_intensity = FloatProperty(name="Main point intensity", description="Intensidad de la luz principal punto", default=0, min=0)
    npr_main_sun_intensity = FloatProperty(name="Main sun intensity", description="Intensidad de la luz principal sol", default=1, min=0, max=1)
    npr_main_point_samples = IntProperty(name="Main point samples", description="Cantidad de samples para la luz principal punto", default=1, min=0)
    npr_main_point_size = FloatProperty(name="Main point size", description="Tamaño la luz principal punto, a mayor tamaño mas suave es la sombra", default=0.1, min=0)


def register():
    bpy.utils.register_class(eLinkedPropertiesPanel)
    bpy.utils.register_class(eLinkedProperties)
    bpy.utils.register_class(eLinkedAddKeys)

    bpy.types.Object.eibriel_linkproperty = PointerProperty(type=eLinkedProperties, name="Linked Properties")


def unregister():
    bpy.utils.unregister_class(eLinkedPropertiesPanel)
    bpy.utils.unregister_class(eLinkedProperties)
    bpy.utils.unregister_class(eLinkedAddKeys)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
