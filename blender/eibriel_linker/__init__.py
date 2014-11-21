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

#.pc2 export code based on io_export_pc2.py by Florian Meyer (tstscr)

bl_info = {
    "name": "eLinker",
    "author": "Eibriel",
    "version": (0,1),
    "blender": (2, 72, 0),
    "location": "View3D > Tools > Relations",
    "description": "Tools for film production.",
    "warning": "",
    "wiki_url": "https://github.com/Eibriel/scripts/wiki",
    "tracker_url": "https://github.com/Eibriel/scripts/issues",
    "category": "Eibriel"}

import bpy
from bpy.types import AddonPreferences 
from bpy.props import *

import os, json
from os import path

import mathutils, math, struct

libitems = []

class eLibraryGroups(bpy.types.PropertyGroup):
    name = StringProperty(name="Name", default="", options={'HIDDEN', 'SKIP_SAVE'})


class eLibraryLibs(bpy.types.PropertyGroup):
    name = StringProperty(name="Name", default="", options={'HIDDEN', 'SKIP_SAVE'})


def refreshLibrariesCallback(self, context):
        bpy.ops.elinker.refresh_libraries()
    
        
class eLibraryProperties(bpy.types.PropertyGroup):
    folderpath = StringProperty(name="Library folder", default="", subtype='DIR_PATH', options={'HIDDEN', 'SKIP_SAVE'}, update=refreshLibrariesCallback)
    name = StringProperty(name="Name", default="", options={'HIDDEN', 'SKIP_SAVE'})
    project = StringProperty(name="Project", default="main", options={'HIDDEN', 'SKIP_SAVE'})
    lodsuffixes = StringProperty(name="LOD suffixes", default="", options={'HIDDEN', 'SKIP_SAVE'})
    
        
class eLinkerPreferences(AddonPreferences):
    bl_idname = __name__
    
    elibrary_collection = CollectionProperty(type=eLibraryProperties, options={'HIDDEN', 'SKIP_SAVE'})
        
    def draw(self, context):  
        """if len(self.elibrary_collection) == 0:
            pie_set = self.elibrary_collection
            pie_item = pie_set.add()
            pie_item.folderpath = "test/test"
            pie_item.name = "test"
            context.window_manager.elibrary_collection_index = 0"""
          
        layout = self.layout
        
        row = layout.row()
        col = row.column()
        col.template_list("UI_UL_list", "ui_lib_list_prop", self, "elibrary_collection", context.window_manager, "elibrary_collection_index", rows=5)
        col = row.column(align=True)
        col.operator("elinker.add_library", icon="ZOOMIN", text="")
        col.operator("elinker.remove_library", icon="ZOOMOUT", text="")
        
        #col = row.column(align=True)
        #col.operator("object.vertex_group_add", icon='ZOOMIN', text="")
        #col.operator("object.vertex_group_remove", icon='ZOOMOUT', text="").all = False
        
        
        
        if len(self.elibrary_collection) > 0:
            col = self.elibrary_collection[ context.window_manager.elibrary_collection_index ]
            layout.label(text="Lib %s:" % col.name)
            layout.prop(col, "name")
            layout.prop(col, "folderpath")
            layout.prop(col, "lodsuffixes")
        
        layout.separator()
        
        row = layout.row(align=1)
        row.operator("elinker.save_preferences", icon="FILE_FOLDER")
        row.operator("elinker.load_preferences", icon="FILE_TICK")


class eLinkerPanelLibrary(bpy.types.Panel):
    bl_idname = "elinker"
    bl_label = "eLinker"
    bl_category = "Relations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    
    def draw(self, context):
        active_obj = context.active_object

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        wm = context.window_manager
        layout = self.layout
        
        col = layout.column()
        col.operator("elinker.refresh_libraries", icon="FILE_REFRESH", text="")
        col.template_list("UI_UL_list", "ui_lib_list", addon_prefs, "elibrary_collection", wm, "elibrary_collection_index", rows=len(addon_prefs.elibrary_collection), type="DEFAULT")

        row = col.row(align=1)
        coll = row.column()
        if not len( wm.elib_libs ) > 0:
            coll.enabled = False
        coll.operator("elinker.load_library", icon="LINK_BLEND")
        coll.template_list("UI_UL_list", "ui_library_list", wm, "elib_libs", wm, "elib_libs_index", rows=5)

        colb = row.column()
        if not len( wm.elib_groups ) > 0:
            colb.enabled = False
        colb.operator("elinker.link_group", icon="GROUP")
        colb.template_list("UI_UL_list", "ui_group_list", wm, "elib_groups", wm, "elib_groups_index", rows=5)
        

class eLinkerPanelLinks(bpy.types.Panel):
    bl_idname = "elinker_options"
    bl_label = "eLinker Options"
    bl_category = "Relations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        active_obj = context.active_object
        wm = context.window_manager
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        elib_collection = addon_prefs.elibrary_collection
        #print ( len (elib_collection) )
        #print (wm.elibrary_collection_index+1)
        if len (elib_collection) < wm.elibrary_collection_index+1:
            wm.elibrary_collection_index = 0
        #elib = None
        #if len(elib_collection) > 0:
        #    elib = elib_collection[ wm.elibrary_collection_index ]
        
        layout = self.layout
        
        col = layout.column(align=0)
        
        if not active_obj:
            col.label( text= "No active object" )
            return
        
        col.label( text= "Name: %s" % active_obj.name )
        #col.label( text= active_obj.name )
        
        etype = active_obj.get('elinker_type')
        egroup = active_obj.get('elinker_group')
        
        if etype:
            col.label( text= "Type: %s" % etype )
        #col.label( text= etype )
        
        if egroup:
        
            suffarray = []
            
            elib = None
            for el in elib_collection:
                #te = elib_collection[el]
                if el.name == etype:
                    elib = el
            
            if elib and elib.lodsuffixes != "":
                suffarray = elib.lodsuffixes.split(";")
            
            for suff in suffarray:
                if egroup.endswith(suff):
                    col.label( text= "LOD suffix: %s" % suff )
                    #col.label( text= suff )
            
            for suff in suffarray:
                oprops = col.operator(operator="elinker.change_group", text="Change to %s" % suff, icon="TRIA_RIGHT")
                oprops.suffix = suff
            

            layout.separator()
            col = layout.column(align=0)
            
            col.prop(context.scene, "elinker_cachepath")
            col.operator("elinker.gen_cache", icon="MOD_MESHDEFORM")
        
        layout.separator()
        col = layout.column(align=0)
        row = col.row(align=1)
        row.operator("elinker.meshcache2shapekeys", icon="KEYINGSET")
        row.operator("elinker.clearanimshapeskey", icon="KEY_DEHLT")
        

class changeGroup (bpy.types.Operator):
    bl_idname = "elinker.change_group"
    bl_label = "Change Group"
    
    suffix = StringProperty(name="Suffix", description="Group suffix", default="")
    
    def execute(self,context):
        print (self.suffix)
        
        wm = context.window_manager
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        elib_collection = addon_prefs.elibrary_collection
        elib = elib_collection[ wm.elibrary_collection_index ]
        
        obj = context.active_object
        egroup = obj.dupli_group

        grtemp = ''
        
        if not obj.get('elinker_type'):
            self.report( {'ERROR'}, "The object was linked without eLinker" )
            return {'CANCELLED'}
        
        if obj.type == 'ARMATURE':
            obj = context.scene.objects[ obj['elinker_parent'] ]
        
        if not obj.get('elinker_file'):
            self.report( {'ERROR'}, "Error obtaining File Path" )
            return {'CANCELLED'}
            
        if egroup == None or obj['elinker_type'] == None:
            self.report( {'ERROR'}, "Active object is not a Dupli Group" )
            return {'CANCELLED'}
        
        if egroup.name.endswith(self.suffix):
            self.report( {'WARNING'}, "Already %s" % self.suffix )
            return {'CANCELLED'}
                
        
        libfile = obj['elinker_file']
        libfile = libfile.replace('\\','/')
        libfile = os.path.abspath(os.path.normpath(bpy.path.abspath(libfile)))
        #print (libfile)
        
        if not os.path.exists(libfile):
            self.report( {'ERROR'}, "File do not exist: \"%s\"" % libfile)
            return {'CANCELLED'}
        
        #print ("libfile: %s" % libfile)
        suffarray = []
        if elib.lodsuffixes != "":
            suffarray = elib.lodsuffixes.split(";")
        
        grtemp = None
        for suff in suffarray:
            if egroup.name.endswith(suff):
                endpos = -(len(suff))
                grtemp = "%s%s" % (egroup.name[:endpos], self.suffix)
                print (suff)
        
        if not grtemp:
            self.report( {'ERROR'}, "Actual suffix not recognized")
            return {'CANCELLED'}
        
        with bpy.data.libraries.load(libfile, link=True) as (data_from, data_to):
                for grr in data_from.groups:
                    if grr == grtemp :
                        data_to.groups.append(grr)
        try:
            bpy.data.groups[grtemp]
        except:
            self.report( {'ERROR'}, "Group do not exist: \"%s\"" % grtemp)
            return {'CANCELLED'}
        
        oldgr = obj.dupli_group
        obj.dupli_group = bpy.data.groups[ grtemp ]
        obj["elinker_group"] = grtemp
        
        """if context.scene.elinker_cleangroup:
            try:
                oldgr.user_clear()
                bpy.data.groups.remove(oldgr)
            except:
                pass"""
                
        return {'FINISHED'}     

class savePref (bpy.types.Operator):
    bl_idname = "elinker.save_preferences"
    bl_label = "Save Preferences"
    
    def execute(self,context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        wm = context.window_manager
        userpath = bpy.utils.resource_path(type="USER")
        
        libraries = {}
        for elib in addon_prefs.elibrary_collection:
            libraries[elib.name] = {'name':elib.name, 'folderpath':elib.folderpath, 'project':elib.project, 'lodsuffixes':elib.lodsuffixes}
        print (libraries)
        
        jdata = {'libraries':libraries}
        
        jtext = json.dumps( jdata )

        jpath = path.join(userpath, 'elinker.conf')

        jfile = None
        try:
            jfile = open(jpath, 'w')
        except:
            pass

        if jfile:
            jfile.write( jtext )
            jfile.close()
        
        return {'FINISHED'}

class loadPref (bpy.types.Operator):
    bl_idname = "elinker.load_preferences"
    bl_label = "Load Preferences"
    
    def execute(self,context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        wm = context.window_manager
        userpath = bpy.utils.resource_path(type="USER")
        jpath = path.join(userpath, 'elinker.conf')
        
        try:
            jfile = open(jpath, 'r')
        except:
            #print ("BL: Error reading %s" % path)
            self.report( {'ERROR'}, "Error reading: \"%s\"" % (jpath) )
            return {'CANCELLED'}

        jtext = jfile.read()
        jfile.close()

        try:
            jdata = json.loads( jtext )
        except:
            print ("BL: Error parsing %s" % path)
            return
        
        if len(jdata['libraries'])<1:
            return {'FINISHED'}
        
        addon_prefs.elibrary_collection.clear()
        
        for jlib in jdata['libraries']:
            jjlib = jdata['libraries'][jlib]
            elib_collection = addon_prefs.elibrary_collection
            elib_item = elib_collection.add()
            elib_item.folderpath = jjlib['folderpath']
            elib_item.lodsuffixes = jjlib['lodsuffixes']
            elib_item.name = jjlib['name']
        
        return {'FINISHED'}


class addLibrary (bpy.types.Operator):
    bl_idname = "elinker.add_library"
    bl_label = "Add Library"
    
    def execute(self,context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        
        elib_collection = addon_prefs.elibrary_collection
        elib_item = elib_collection.add()
        elib_item.folderpath = ""
        elib_item.name = "Library Name"
        context.window_manager.elibrary_collection_index = len(addon_prefs.elibrary_collection)-1
        
        return {'FINISHED'}



class removeLibrary (bpy.types.Operator):
    bl_idname = "elinker.remove_library"
    bl_label = "Remove Library"
    
    def execute(self,context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        wm = context.window_manager
        
        elib_collection = addon_prefs.elibrary_collection
        elib_collection.remove(wm.elibrary_collection_index)
        wm.elibrary_collection_index = len(addon_prefs.elibrary_collection)-1
        
        return {'FINISHED'}
        
        
class refreshLibrary (bpy.types.Operator):
    bl_idname = "elinker.refresh_libraries"
    bl_label = "Refresh Libraries"
    
    def execute(self,context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        wm = context.window_manager
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        elib_collection = addon_prefs.elibrary_collection
        
        print ("Refreshing")
        
        wm.elib_libs.clear()
        wm.elib_libs_index = 0
        wm.elib_groups.clear()
        wm.elib_groups_index = 0
        
        if len(elib_collection) ==0:
            self.report( {'WARNING'}, "No library configured" )
            return {'CANCELLED'}
        
        elib = elib_collection[ wm.elibrary_collection_index ]
        
        elib_collection = addon_prefs.elibrary_collection
        #for elib in elib_collection:
        
        assetlist = None
        try:
            assetlist = os.listdir(elib.folderpath)
        except:
            pass
        if assetlist != None:
            assetlist.sort()
            for filename in assetlist:
                if filename.endswith('.blend'):
                    pie_set = wm.elib_libs
                    pie_item = pie_set.add()
                    pie_item.name = filename
        
        return {'FINISHED'}

class loadLibraries (bpy.types.Operator):
    bl_idname = "elinker.load_library"
    bl_label = "Load Blend"
    #bl_options = {"REGISTER", "UNDO"}
    def execute(self,context):
        #scnsettings = context.scene.movietools
        scn = context.scene
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        wm = context.window_manager
        elib_collection = addon_prefs.elibrary_collection
        elib = elib_collection[ wm.elibrary_collection_index ]
        
        suffarray = []
        if elib.lodsuffixes != "":
            suffarray = elib.lodsuffixes.split(";")
        
        print (suffarray)
        
        wm.elib_groups_index = 0
        
        lfile = wm.elib_libs[ wm.elib_libs_index ].name
        lpath = elib.folderpath
        with bpy.data.libraries.load(path.join(lpath, lfile)) as (data_from, data_to):
            wm.elib_groups.clear()
            data_from.groups.sort()
            persg_set = wm.elib_groups
            for group in data_from.groups:
                if len(suffarray)>0:
                    for suff in suffarray:
                        if group.endswith(suff):
                            persg_item = persg_set.add()
                            persg_item.name = group
                else:
                    persg_item = persg_set.add()
                    persg_item.name = group
            #for ind, perg in enumerate(persg_set):
            #    wm.elib_groups_index = ind
        return {'FINISHED'}


class linkGroup (bpy.types.Operator):
    bl_idname = "elinker.link_group"
    bl_label = "Link Group"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self,context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        wm = context.window_manager
        elib_collection = addon_prefs.elibrary_collection
    
        if context.mode != 'OBJECT':
            self.report( {'ERROR'}, "The context must be Object Mode" )
            return {'CANCELLED'}
        
        gr = wm.elib_groups[ wm.elib_groups_index ].name
        lfile = wm.elib_libs[ wm.elib_libs_index ].name
        lpath = elib_collection[ wm.elibrary_collection_index ].folderpath
        libfile = path.join(lpath, lfile)
        elib = elib_collection[ wm.elibrary_collection_index ]
        elibname = elib.name
        
        #print (libfile)
        #libfile = bpy.path.relpath( libfile )
        #print (libfile)
        
        with bpy.data.libraries.load(libfile, link=True) as (data_from, data_to):
            for grr in data_from.groups:
                if grr == gr:
                    data_to.groups.append(grr)
        
        #bpy.ops.object.group_instance_add(name=gr[:-6].lower(), group=gr, view_align=False, location=(0, 0, 0), rotation=(0, 0, 0))
        #empty = bpy.context.object

        """if gr[-7:] == '_LAYOUT':
            tmpname = gr
        elif gr[-8:] == '_PROXY_2':
            tmpname = gr[:-8]
        elif gr[-6:] == '_PROXY':
            tmpname = gr[:-6]
        elif libfile[-13:] == '_layout.blend':
            tmpname
        elif libfile[-18:] == '_layout_anim.blend':
            tmpname
        else:
            tmpname = gr"""
        
        suffarray = []
        if elib.lodsuffixes != "":
            suffarray = elib.lodsuffixes.split(";")
            
        tmpname = gr
        el = None
        
        for suff in suffarray:
            if tmpname.endswith(suff):
                tmpname = tmpname[:len(suff)+1]
        
        """#layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        layers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        #Search empty layer:
        for lobj in context.scene.objects:
            try:
                lobj['elinker_type']
            except:
                continue
            if lobj['elinker_type'] != 'PERSONAJE':
                continue
            for k, l in enumerate(lobj.layers):
                if l:
                    try:
                        layers[ k ] += 1
                    except:
                        layers[ k ] = 1
        el = 0
        maxp = 1
        #l = 0
        #for k, l in enumerate(layers):
        while 1:
            l = layers[el]
            print ("%s - %s - %s" % (l, el, maxp))
            if l<maxp:
                break
            el = el + 1
            if el>3:
                maxp += 1
                el = 0
            
        
        layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        layers[el] = True"""
        
        empty = bpy.data.objects.new(tmpname.lower(), None)
        context.scene.objects.link( empty )
        context.scene.objects.active = empty
        #empty.layers = layers

        empty.location[0] = 0
        empty.location[1] = 0
        empty.location[2] = 0
        empty.rotation_euler[0] = 0
        empty.rotation_euler[1] = 0
        empty.rotation_euler[2] = 0
                
        empty.dupli_type = 'GROUP'
        empty.dupli_group = bpy.data.groups[gr]
        
        empty["elinker_type"] = elibname
        empty["elinker_file"] = libfile
        empty["elinker_group"] = gr
        
        empty.lock_location[0] = True
        empty.lock_location[1] = True
        empty.lock_location[2] = True
        empty.lock_rotation[0] = True
        empty.lock_rotation[1] = True
        empty.lock_rotation[2] = True
        empty.lock_scale[0] = True
        empty.lock_scale[1] = True
        empty.lock_scale[2] = True
        
        for ob in empty.dupli_group.objects:
            #print (ob.name[-4:])
            #if ob.name[-8:] == "_blenrig" or ob.name[-15:] == "_blenrig_layout":
            if ob.type=="ARMATURE":
                #ob.proxy_make(object='DEFAULT')
                bpy.ops.object.proxy_make(object=ob.name)
                
                rig = bpy.context.object
                rig.name = "%s_blenrig" % tmpname.lower()
                
                bpy.context.object.lock_location[0] = True
                bpy.context.object.lock_location[1] = True
                bpy.context.object.lock_location[2] = True
                bpy.context.object.lock_rotation[0] = True
                bpy.context.object.lock_rotation[1] = True
                bpy.context.object.lock_rotation[2] = True
                bpy.context.object.lock_scale[0] = True
                bpy.context.object.lock_scale[1] = True
                bpy.context.object.lock_scale[2] = True
                
                layers = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
                
                if el:
                    if el<=10:
                        layers[el+10] = True
                else:
                    layers= empty.layers
                    
                rig.layers = layers
                
                rig.show_x_ray = True
                rig["elinker_type"] = "%s_rig" % (elibname)
                rig["elinker_children"] = empty.name
                empty["elinker_rig"] = rig.name
                
                actname = rig.name
                """if addon_prefs.role == 'layout':
                    actname = "lay_%s" % rig.name
                elif addon_prefs.role == 'animacion': 
                    actname = "anim_%s" % rig.name"""
                act = bpy.data.actions.new(actname)
                rig.animation_data_create()
                rig.animation_data.action = act
                
                #Vuelve a seleccionar el empty para poder traer mas rigs
                context.scene.objects.active = empty
        return {'FINISHED'}

##---------------------------GEN CACHE------------------
class genCache (bpy.types.Operator):
    bl_idname = "elinker.gen_cache"
    bl_label = "Build Cache"

    filename_ext = ".pc2"

    def execute(self,context):
        scn = context.scene
        props = self.properties
        
        if scn.elinker_cachepath == "":
            return {'CANCELLED'}
        
        mat_x90 = mathutils.Matrix.Rotation(-math.pi/2, 4, 'X')
        gr = context.active_object
        sc = context.scene
        start = sc.frame_start-2
        end = sc.frame_end+1
        sampling = 1
        apply_modifiers = True
        
        objnames = []
        count = 0
        objects = {}

        abspath = bpy.path.abspath(scn.elinker_cachepath)
        filepath = path.join(abspath, context.active_object.name)
        
        if not gr:
            self.report( {'ERROR'}, "No active object" )
            return {'CANCELLED'}
        
        if not gr.dupli_group:
            self.report( {'ERROR'}, "The object is not a Dupli Group" )
            return {'CANCELLED'}
        
        for ob in gr.dupli_group.objects:
            if ( ob.hide_render == True):
                continue
            if ( not ob.type in {'MESH'} ):
                continue
                
            usemask = False
            usemirror = False
            
            for modd in ob.modifiers:
                if modd.type == 'SUBSURF':
                    modd.show_render = False
            for modd in ob.modifiers:
                if modd.type == 'MASK':
                    modd.show_render = False
                    usemask = True
                    self.report( {'WARNING'}, "Mask modifier on Object \"%s\", unexpected results" % ob.name )
            for modd in ob.modifiers:
                if modd.type == 'MIRROR':
                    #modd.show_render = False
                    usemirror = True
                    self.report( {'WARNING'}, "Mirror modifier on object: \"%s\", unexpected results" % ob.name )
            
            if ob.location.x != 0 or ob.location.y != 0 or ob.location.z != 0:
                self.report( {'WARNING'}, "Location is not 0,0,0 on object: \"%s\", unexpected results" % ob.name )
            
            if ob.rotation_euler.x != 0 or ob.rotation_euler.y != 0 or ob.rotation_euler.z != 0:
                self.report( {'WARNING'}, "Rotation Euler is not 0,0,0 on object: \"%s\", unexpected results" % ob.name )
            
            if ob.rotation_quaternion.x != 0 or ob.rotation_quaternion.y != 0 or ob.rotation_quaternion.z != 0 or ob.rotation_quaternion.w != 0:
                self.report( {'WARNING'}, "Rotation Quaternion is not 0,0,0,0 on object: \"%s\", unexpected results" % ob.name )
            
            if ob.scale.x != 0 or ob.scale.y != 0 or ob.scale.z != 0:
                self.report( {'WARNING'}, "Scale is not 0,0,0 on object: \"%s\", unexpected results" % ob.name )
                

            objnames.append (ob.name)
                
            objects[ob.name] = {}
            objects[ob.name]['object'] = ob
                    
            count = count + 1
            #print ("CACHE: Generating test mesh '%s' objeto '%d' de '%d'" % (ob.name, count, len(gr.dupli_group.objects))) #DEBUG
            me = ob.to_mesh(sc, apply_modifiers, 'RENDER')
            vertCount = len(me.vertices)
            objects[ob.name]['vertCount'] = vertCount
            sampletimes = self.getSampling(start, end, sampling)
            sampleCount = len(sampletimes)
            
            # Create the header
            headerFormat='<12siiffi'
            headerStr = struct.pack(headerFormat, b'POINTCACHE2\0',
                                    1, vertCount, start, sampling, sampleCount)
            
            tail = "%s_%s.ps2" % (filepath, ob.name)
            filepath_temp = path.join(scn.elinker_cachepath, tail)
            print ("CACHE: Writting to '%s'" % filepath_temp)
            if not path.exists(scn.elinker_cachepath):
                try:
                    makedirs(scn.elinker_cachepath)
                except:
                    pass

            objects[ob.name]['filepath'] = filepath_temp
            
            try:
                f = open(filepath_temp, "wb")
            except:
                #print('CACHEERROR: No se puede escribir el archivo "%s".' % (filepath_temp))
                self.report( {'ERROR'}, "Can not open file: \"%s\"" % (filepath_temp) )
                return {'CANCELLED'}
            f.write(headerStr)
            #f.close()
            
            for frame in sampletimes:
                filen = 0
                count = 0.
                obinfo = objects[ob.name]
                    
                sc.frame_set(frame)
                per = float(frame-start)/float(end-start)
                perb = (count / len(objects))*0.01
                per += perb
                per = int(per * 100)
                cindx = 0
                try:
                    cindx = context.scene.cache_index
                except:
                    pass
                #print ("FRAME: %s PROGRESS: %s%% ACTIVITY: %s" % (cindx, per, ob.name))
                me = ob.to_mesh(sc, apply_modifiers, 'RENDER')
                
                if len(me.vertices) != obinfo['vertCount']:
                    try:
                        remove(obinfo['filepath'])
                    except:
                        empty = open(obinfo['filepath'], 'w')
                        empty.write('DUMMIFILE - export failed\n')
                        empty.close()
                    #print('CACHEERROR: Export failed. Vertexcount of Object is not constant')
                    self.report( {'ERROR'}, "Export failed. Vertexcount of Object is not constant" )
                    return {'CANCELLED'}
                
                me.transform(ob.matrix_world)
                
                try:
                    f = open(obinfo['filepath'], "ab")
                except:
                    #print('CACHEERROR: No se puede escribir el archivo "%s".' % (obinfo['filepath']))
                    self.report( {'ERROR'}, "Can not open file: \"%s\"" % (obinfo['filepath']) )
                    return {'CANCELLED'}
                
                for v in me.vertices:
                    thisVertex = struct.pack('<fff', float(v.co[0]),
                                                     float(v.co[1]),
                                                     float(v.co[2]))
                    f.write(thisVertex)

                bpy.data.meshes.remove(me)
                del me
                count += 1.

            f.flush()
            f.close()
                
            if 0:
                newob = bpy.data.objects.new( ob.name, ob.data )
            else:
                newme = bpy.data.meshes.new_from_object( sc, ob, False, 'RENDER' )
                if newme.shape_keys != None :
                    knam = newme.shape_keys.name
                    #newme.shape_keys.user_clear()
                    #bpy.data.shape_keys[ knam ].user_clear()
                    for k in bpy.data.shape_keys[ knam ].key_blocks.keys():
                        skey = bpy.data.shape_keys[ knam ].key_blocks[ k ]
                        #print ("Muteando %s" % skey.name)
                        skey.mute = True
                        #skey.user_clear()
                        
                newob = bpy.data.objects.new( ob.name, newme )
                
            
            #if usemirror:
            #    mod = newob.modifiers.new('Mirror', 'MIRROR')
                
                
            sc.objects.link(newob)	
            mod = newob.modifiers.new('eLinker Mesh Cache', 'MESH_CACHE')
            mod.cache_format = 'PC2'
            mod.filepath = filepath_temp
            mod.frame_start = start
             
            if usemask:
                mod = newob.modifiers.new('Mask', 'MASK')
            
            mod = newob.modifiers.new('Subsurf', 'SUBSURF')
            
            #del newme
            del newob
            del mod
                
        return {'FINISHED'}
        
    def getSampling(self, start, end, sampling):
        samples = [start + x * sampling
                   for x in range(int((end - start) / sampling) + 1)]
        return samples

class cache2shapekeys (bpy.types.Operator):
    """Bake Mesh Cache to ShapeKeys"""
    bl_idname = "elinker.meshcache2shapekeys"
    bl_label = "Shape Key sequence"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self,context):
        C = context
        obj = context.active_object

        if not context.active_object or context.active_object.type!="MESH":
            self.report( {'ERROR'}, "No active object" )
            return {'CANCELLED'}

        modcachename = "eLinker Mesh Cache"

        try:
            obj.modifiers[ modcachename ]
        except:
            self.report( {'ERROR'}, "The object must have a Mesh Cache modifier" )
            return {'CANCELLED'}

        obj.modifiers[ modcachename ].show_viewport = False
        obj.modifiers[ modcachename ].show_render = False
        fil = obj.modifiers[ modcachename ].filepath

        obj.use_shape_key_edit_mode = True

        for n in range (bpy.context.scene.frame_start-2,bpy.context.scene.frame_end+1+1):
            bpy.context.scene.frame_current = n
            nam = "CacheAnim_%s" % n
            
            ks = None
            try:
                ks = obj.data.shape_keys.key_blocks[ nam ]
            except:
                pass
            
            if ks:
                kind = None
                for kkb, kb in enumerate(obj.data.shape_keys.key_blocks):
                    if kb == ks:
                        kind = kkb
                        break
                        
                obj.active_shape_key_index = kind
                bpy.ops.object.shape_key_remove(all=False)
            
            C.active_object.modifiers.new(name=nam, type="MESH_CACHE")
            obj.modifiers[nam].filepath = fil
            obj.modifiers[nam].cache_format = 'PC2'
            obj.modifiers[nam].frame_start = bpy.context.scene.frame_start-2

            override = C.copy()
            override['modifier'] = obj.modifiers[ nam ]
            bpy.ops.object.modifier_apply(override, apply_as='SHAPE', modifier=nam)
            obj.data.shape_keys.key_blocks[ nam ].value = 1
            

            if not obj.data.shape_keys.animation_data:
                obj.data.shape_keys.animation_data_create()

            if not obj.data.shape_keys.animation_data.action:
                act = bpy.data.actions.new("%s_animkeys" % obj.name)
                obj.data.shape_keys.animation_data_create()
                obj.data.shape_keys.animation_data.action = act

            datapath = 'key_blocks["%s"].value' % nam

            try:
                obj.data.shape_keys.animation_data.action.fcurves.new(data_path= datapath)
            except:
                for curv in obj.data.shape_keys.animation_data.action.fcurves:
                    if curv.data_path == datapath:
                        obj.data.shape_keys.animation_data.action.fcurves.remove(fcurve = curv)
                        
                obj.data.shape_keys.animation_data.action.fcurves.new(data_path= datapath)
                pass

            for curv in obj.data.shape_keys.animation_data.action.fcurves:
                if curv.data_path == datapath:
                    curv.keyframe_points.insert( n-1, 0, options={'NEEDED','FAST'}) #PREV
                    curv.keyframe_points.insert( n, 1, options={'NEEDED','FAST'}) #ACTUAL
                    curv.keyframe_points.insert( n+1, 0, options={'NEEDED','FAST'}) #SIG

        return {'FINISHED'}


class clearanimkeyshapes (bpy.types.Operator):
    """Delete Mesh Cache bake from Shapekeys"""
    bl_idname = "elinker.clearanimshapeskey"
    bl_label = "Clear Shape Keys"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self,context):
        C = context
        obj = context.active_object
        
        modcachename = "eLinker Mesh Cache"
        
        try:
            obj.modifiers[ modcachename ]
        except:
            self.report( {'ERROR'}, "The object must have a Mesh Cache modifier" )
            return {'CANCELLED'}
        
        obj.modifiers[ modcachename ].show_viewport = True
        obj.modifiers[ modcachename ].show_render = True
        obj.modifiers[ modcachename ].deform_mode = 'INTEGRATE'
        
        for tmpn in range(0, len(obj.data.shape_keys.key_blocks) ):
            kind = None
            for kkb, kb in enumerate(obj.data.shape_keys.key_blocks):
                if kb.name[:10] == "CacheAnim_":
                    kind = kkb
                    break
            if kind:
                obj.active_shape_key_index = kind
                bpy.ops.object.shape_key_remove(all=False)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(eLinkerPanelLibrary)
    bpy.utils.register_class(eLinkerPanelLinks)
    bpy.utils.register_module(__name__)

    bpy.types.WindowManager.elibrary_collection_index = IntProperty(options={'HIDDEN', 'SKIP_SAVE'}, update=refreshLibrariesCallback)
    
    bpy.types.WindowManager.elib_libs = CollectionProperty(type=eLibraryLibs, options={'HIDDEN', 'SKIP_SAVE'})
    bpy.types.WindowManager.elib_libs_index = IntProperty(options={'HIDDEN', 'SKIP_SAVE'})
    
    bpy.types.WindowManager.elib_groups = CollectionProperty(type=eLibraryGroups, options={'HIDDEN', 'SKIP_SAVE'})
    bpy.types.WindowManager.elib_groups_index = IntProperty(options={'HIDDEN', 'SKIP_SAVE'})
    
    bpy.types.Scene.elinker_cachepath = StringProperty(name="Cache Path", default="", subtype='DIR_PATH', options={'HIDDEN', 'SKIP_SAVE'})
    

def unregister():
    bpy.utils.unregister_class(eLinkerPanelLibrary)
    bpy.utils.unregister_class(eLinkerPanelLinks)
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
