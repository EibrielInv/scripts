bl_info = {
    "name": "eCrowd",
    "author": "Eibriel",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "View3D -> Tool Panel -> Animation",
    "description": "One click crowd generator",
    "warning": "",
    "wiki_url": "",
    "category": "Eibriel"}

# Detectar armatures
# Detectar Mallas
# Multiplicar personajes
# Multiplicar animación

import random
import json
import bpy
import os

from bpy.props import StringProperty


class ECROWD_setPlaceCharacter(bpy.types.Operator):
    """Set as eCrowd place character"""
    bl_idname = "ecrowd.setplacecharacter"
    bl_label = "eCrowd set place character"

    def execute(self, context):
        C = bpy.context
        D = bpy.data
        for object in C.selected_objects:
            if object.type == "EMPTY":
                object["ecrowd_place"] = 1
                object["ecrowd_place_character"] = C.window_manager.ecrowd_charactertype
        return {'FINISHED'}


class ECROWD_cleananims(bpy.types.Operator):
    """Clear users on animations unrelated to eCrowd"""
    bl_idname = "ecrowd.cleananims"
    bl_label = "eCrowd animation cleanup"

    def execute(self, context):
        D = bpy.data

        for animation in D.actions:
            if not animation.name.startswith('ecrowd'):
                animation.user_clear()

        return {'FINISHED'}


class ECROWD_deplace(bpy.types.Operator):
    """Delete characters previously placed by eCrowd"""
    bl_idname = "ecrowd.deplace"
    bl_label = "Deplace eCrowd agents"

    def execute(self, context):
        C = bpy.context
        D = bpy.data

        for obj in C.scene.objects:
            obj.select = False

        # Cleanup
        for obj in C.scene.objects:
            if obj.get("ecrowd_placed_duplicated") == 1 or obj.get("ecrowd_placed") is not None:
                obj.select = True
                bpy.ops.object.delete()
        #
        return {'FINISHED'}



class ECROWD_place(bpy.types.Operator):
    """Generate and place eCrowd agents"""
    bl_idname = "ecrowd.place"
    bl_label = "Place eCrowd agents"


    def deselect_all(self):
        C = bpy.context
        for object in C.scene.objects:
            object.select = False


    def load_script(self):
        C = bpy.context
        D = bpy.data
        # Load script
        script_text = ""
        for script_line in bpy.data.texts["ecrowd_script"].lines:
            if script_text == "":
                script_text = script_line.body
            else:
                script_text = "{}\n{}".format(script_text, script_line.body)
        try:
            script_json = json.loads(script_text)
        except json.decoder.JSONDecodeError as e:
            strerror, = e.args
            self.report({'ERROR'}, "Script error: {}".format(strerror))
            return {'CANCELLED'}, None
        return {}, script_json


    def get_characters_filepaths(self, script_json):
        # Get characters filepaths
        characters_abspath = bpy.path.abspath(script_json["characters_path"])
        if not os.path.isdir(characters_abspath):
            self.report({'ERROR'}, "Characters Path does not exists: {}".format(characters_abspath))
            return {'CANCELLED'}, None
        characters_lib_abspath = {}
        for character in script_json["characters"]:
            characters_lib_abspath[character] = {}
            for char_name in script_json["characters"][character]:
                #for char_path in script_json["characters"][character]["blend_files"]:
                char_path = script_json["characters"][character][char_name]["blend_file"]
                character_abspath = os.path.join(characters_abspath, char_path)
                if not os.path.exists(character_abspath):
                    self.report({'ERROR'}, "Character Path does not exist: {}".format(character_abspath))
                    return {'CANCELLED'}, None
                #characters_lib_abspath[character].append(character_abspath)
                characters_lib_abspath[character][char_name] = character_abspath
        return {}, characters_lib_abspath


    def get_placers(self):
        C = bpy.context
        D = bpy.data
        #Get Placers
        placers = {}
        for object in C.scene.objects:
            if object.get("ecrowd_place") == 1:
                place_type = object.get("ecrowd_place_character")
                if placers.get(place_type) is None:
                    placers[place_type] = []
                placers[place_type].append((object.location, object.rotation_euler, object.name))
        return {}, placers


    def load_library(self, character_abspath, character):
        C = bpy.context
        D = bpy.data
        # Load Library
        print ("Load {}".format(character_abspath))
        obj_to_link = []
        with D.libraries.load(character_abspath, link=True) as (data_from, data_to):
            for obj in data_from.objects:
                obj_name = str(obj)
                if obj.startswith("ecrowd_") :
                    data_to.objects.append(obj)
                    obj_to_link.append(obj_name)
            for act in data_from.actions:
                act_name = str(act)
                if act.startswith("ecrowd_") :
                    data_to.actions.append(act)
                    #obj_to_link.append(obj_name)

        #Deselect all
        self.deselect_all()

        sorted_obj = [None, None]
        for obj_name in obj_to_link:
            if D.objects[obj_name].type == "MESH":
                sorted_obj[1] = obj_name
            elif D.objects[obj_name].type == "ARMATURE":
                sorted_obj[0] = obj_name

        for obj_name in sorted_obj:
            # Colocar objetos en las escenas
            obj_linked = C.scene.objects.link(D.objects[obj_name]).object
            C.scene.update()
            obj_linked.select = True
        bpy.ops.object.make_local(type='SELECT_OBJECT')

        for obj in C.selected_objects:
            # Rename
            obj_new_name = "ecrowd_placed_{}".format(obj.name[7:])
            obj.name = obj_new_name
            obj["ecrowd_placed"] = character

            # TODO How to know that the Armature
            # is first on C.selected_objects list?
            if obj.type == "MESH":
                obj.modifiers["Armature"].object = None
                C.scene.update()
                obj.modifiers["Armature"].object = arm_new
            else:
                arm_new = obj


    def execute(self, context):
        C = bpy.context
        D = bpy.data

        print ("\nECROWD_place")

        print ("Load Script")
        status, script_json = self.load_script()
        if status != {}:
            return status
        #print (script_json)

        print ("Get Characters Filepaths")
        status, characters_lib_abspath = self.get_characters_filepaths(script_json)
        if status != {}:
            return status
        #print (characters_lib_abspath)

        print ("Get Placers")
        status, placers = self.get_placers()
        if status != {}:
            return status
        print (placers)

        print ("Load Characters Libraries")
        for place_type in placers:
            if place_type in characters_lib_abspath:
                for cc in characters_lib_abspath[place_type]:
                    self.load_library(characters_lib_abspath[place_type][cc], cc)

        print ("Move to Placers")
        for place_type in placers:
            for placer in placers[place_type]:
                newlocation, newrotation, name = placer
                random.seed(abs(hash(name)))
                character = random.choice(list(script_json["characters"][place_type].keys()))
                action = random.choice(script_json["characters"][place_type][character]["actions"])[0]
                print ("Placer: {}, Character: {}".format(name, character))
                self.deselect_all()
                #Select linked characters
                for obj in C.scene.objects:
                    if obj.get("ecrowd_placed_duplicated") is not None:
                        continue
                    if obj.get("ecrowd_placed") == character:
                        obj.select = True
                #Duplicate
                bpy.ops.object.duplicate(linked=True)
                # Mark as duplicated
                for obj in C.selected_objects:
                    obj["ecrowd_placed_duplicated"] = 1
                armature = C.selected_objects[0]
                mesh = C.selected_objects[1]
                #armature.location = newlocation
                #armature.rotation_euler = newrotation
                armature.animation_data.action = D.actions[action]
                armature.parent = C.scene.objects[name]

                # Randomize Material
                bpy.ops.object.make_single_user(material=True)
                for material_slot in mesh.material_slots:
                    if not material_slot.material.use_nodes:
                        continue
                    for node in material_slot.material.node_tree.nodes:
                        if node.name.startswith("ecrowd_random"):
                            node.outputs[0].default_value = random.random()

                min_frame = None
                max_frame = None
                anim_data = []
                for fcurve in armature.animation_data.action.fcurves:
                    anim_data.append([])
                    for keyframe_point in fcurve.keyframe_points:
                        if min_frame is None or keyframe_point.co[0] < min_frame:
                            min_frame = keyframe_point.co[0]
                        if max_frame is None or keyframe_point.co[0] > max_frame:
                            max_frame = keyframe_point.co[0]
                        # Save data
                        anim_data[-1].append([keyframe_point.co[0], keyframe_point.co[1]])
                # Single user animation
                bpy.ops.object.make_single_user(animation=True)
                # Move animation
                random.seed()
                random_shift = C.scene.frame_start - random.randint(0,max_frame-min_frame) - 1
                for fcurve in armature.animation_data.action.fcurves:
                    for keyframe_point in fcurve.keyframe_points:
                        keyframe_point.co[0] += random_shift
                    fcurve.update()

                last_frame = max_frame + random_shift
                first_frame = min_frame + random_shift

                #Cycle animation
                loop_n = 0
                while last_frame+((last_frame-first_frame)*loop_n) < C.scene.frame_end+(last_frame-first_frame):
                    for fcurve in armature.animation_data.action.fcurves:
                        keyframes_to_insert = []
                        for keyframe_point in fcurve.keyframe_points:
                            if keyframe_point.co[0] > last_frame:
                                continue
                            new_keyframe = keyframe_point.co[0]+((last_frame-first_frame)*loop_n)
                            if new_keyframe > C.scene.frame_end+1:
                                continue
                            keyframes_to_insert.append([new_keyframe, keyframe_point.co[1]])
                        for kf in keyframes_to_insert:
                            fcurve.keyframe_points.insert(kf[0], kf[1], options={'REPLACE', 'FAST'})
                        fcurve.update()
                    loop_n += 1

                # Remove frames outside range
                for fcurve in armature.animation_data.action.fcurves:
                    # What keyframes are immediately outside range?
                    keyframe_first_start = None
                    keyframe_first_end = None
                    for keyframe_point in fcurve.keyframe_points:
                        if keyframe_point.co[0] < C.scene.frame_start:
                            if keyframe_first_start is None or keyframe_point.co[0] > keyframe_first_start:
                                keyframe_first_start = keyframe_point.co[0]
                        if C.scene.frame_end < keyframe_point.co[0]:
                            if keyframe_first_end is None or keyframe_point.co[0] < keyframe_first_end:
                                keyframe_first_end = keyframe_point.co[0]

                    #keyframes_to_remove = []
                    removing = True
                    while removing:
                        removing = False
                        for keyframe_point in fcurve.keyframe_points:
                            if keyframe_first_end == keyframe_point.co[0] or keyframe_first_start == keyframe_point.co[0]:
                                continue
                            if keyframe_point.co[0] > C.scene.frame_end + 1 or keyframe_point.co[0] < C.scene.frame_start - 1:
                                print ("Removing ", keyframe_point.co[0])
                                fcurve.keyframe_points.remove(keyframe_point, fast=False)
                                removing = True
                                break

        #Cleanup
        for obj in C.scene.objects:
            obj.select = False
        for obj in C.scene.objects:
            if obj.get("ecrowd_placed") is not None and obj.get("ecrowd_placed_duplicated") is None:
                obj.select = True
                bpy.ops.object.delete()

        return {'FINISHED'}


class eCrowdPanel(bpy.types.Panel):
    bl_idname = "ecrowd"
    bl_label = "eCrowd"
    bl_category = "Animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=0)
        col.label( text= "eCrowd" )
        col.operator(operator="ecrowd.deplace", text="Deplace", icon="TRIA_RIGHT")
        col.operator(operator="ecrowd.place", text="Place", icon="TRIA_RIGHT")
        col.separator()
        col.operator(operator="ecrowd.setplacecharacter", text="Set Character", icon="TRIA_RIGHT")
        col.prop(context.window_manager, "ecrowd_charactertype")


class ECROWD_super_cleanup(bpy.types.Operator):
    """Cleanup keyframes """
    bl_idname = "ecrowd.supercleanup"
    bl_label = "Place eCrowd agents"

    def execute(self, context):
        bpy.ops.action.clean(channels=False, threshold=0.01)


class eCrowdPanelDopesheet(bpy.types.Panel):
    bl_idname = "ecrowd_dopesheet"
    bl_label = "eCrowd"
    #bl_category = "Animation"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=0)
        col.label( text= "eCrowd" )
        op = col.operator(operator="action.clean", text="Super Clean", icon="TRIA_RIGHT")
        op.channels=False
        op.threshold=0.005 #0.001
        #
        op = col.operator(operator="action.clean", text="Mega Clean", icon="TRIA_RIGHT")
        op.channels=False
        op.threshold=0.01 #0.001
        #
        op = col.operator(operator="action.clean", text="Archi Clean", icon="TRIA_RIGHT")
        op.channels=False
        op.threshold=0.02 #0.001

def register():
    # Register properties
    bpy.utils.register_class(eCrowdPanel)
    bpy.utils.register_class(eCrowdPanelDopesheet)
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.ecrowd_charactertype = StringProperty(name="Character Type", default="", options={'HIDDEN', 'SKIP_SAVE'})

def unregister():
    # Unregister properties
    bpy.utils.unregister_class(eCrowdPanel)
    bpy.utils.unregister_class(eCrowdPanelDopesheet)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
