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
    "name": "V-Ray material (.vrscene)",
    "author": "Eibriel",
    "version": (0, 0),
    "blender": (2, 76, 0),
    "location": "File > Import > V-Ray material (.vrscene)",
    "description": "Import V-Ray materials as Blender materials (.vrscene)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/Eibriel/scripts/issues",
    "category": "Import-Export"}

import os
import re
import bpy
import pprint

from bpy.types import Operator
from bpy.props import StringProperty
from bpy.props import CollectionProperty

from bpy_extras.object_utils import AddObjectHelper
from bpy_extras.object_utils import object_data_add

from bpy_extras.image_utils import load_image

from io_import_vraymaterial.vray_data import vray_data
from io_import_vraymaterial.vray_data import vr_link
from io_import_vraymaterial.vray_data import vr_acolor
from io_import_vraymaterial.vray_data import vr_color


class IMPORT_OT_vray_material(Operator, AddObjectHelper):
    """V-Ray materials to Blender materials"""
    bl_idname = "import_material.vray"
    bl_label = "V-Ray materials to Blender materials"
    bl_options = {'REGISTER', 'UNDO'}

    # -----------
    # File props.
    files = CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory = StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})


    def update_extensions(self, context):
        #space = bpy.context.space_data
        #space.params.filter_glob = ";*.vrscene"
        return


    def draw(self, context):
        pass


    def invoke(self, context, event):
        self.update_extensions(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    # Import
    #cycles_data = {}
    #internal_data = {}
    vray_nodes = {}
    links = []

    def check_val(self, value, types):
        if type(value) in types:
            return value
        else:
            return None


    def get_connections(self, node, mat, vray_chain=[]):
        D = bpy.data

        nodeName = node['_name']

        if nodeName in mat.node_tree.nodes:
            pass
        elif node['_type'] == 'MtlSingleBRDF':
            nodeout_internal = mat.node_tree.nodes.new(type='ShaderNodeOutput')
            nodeout_internal.name = nodeName

        elif node['_type'] == 'BitmapBuffer':
            image = load_image(node['file'])

            # look for texture with importsettings
            fn_full = os.path.normpath(bpy.path.abspath(image.filepath))
            img_texture = None
            for texture in bpy.data.textures:
                if texture.type == 'IMAGE':
                    tex_img = texture.image
                    if (tex_img is not None) and (tex_img.library is None):
                        fn_tex_full = os.path.normpath(bpy.path.abspath(tex_img.filepath))
                        if fn_full == fn_tex_full:
                            #self.set_texture_options(context, texture)
                            img_texture = texture
                            break

            # if no texture is found: create one
            if not img_texture:
                name_compat = bpy.path.display_name_from_filepath(image.filepath)
                img_texture = bpy.data.textures.new(name=name_compat, type='IMAGE')
                img_texture.image = image
                #self.set_texture_options(context, texture)

            #nodeName = node
            nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeTexture')
            nodeoccl.texture = img_texture
            nodeoccl.name = nodeName
            #self.internal_data[node]['_blnode'] = nodeoccl
            #mat.node_tree.links.new(nodeout_internal.inputs[1], nodeoccl.outputs[0])
            #nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
            #nodeoccl.image = image
            #nodes = material.node_tree.nodes
            #img = next((node.image for node in nodes if node.type == 'TEX_IMAGE'))

            for prev_node in reversed(vray_chain):
                prev_node_obj = self.vray_nodes[prev_node[0]]
                input_ = None
                if prev_node_obj['_type'] == 'BRDFBump':
                    break
                elif prev_node_obj['_type'] == 'BRDFVRayMtl':
                    if prev_node[1] == 'diffuse':
                        input_ = 0
                    elif prev_node[1] == 'reflect':
                        input_ = 4
                    if input_ != None:
                        self.links.append( [[nodeName, 1], [prev_node_obj['_name'], input_]] )
                    break
                elif prev_node_obj['_type'] == 'TexLayered':
                    self.links.append( [[nodeName, 1], [prev_node_obj['_name'], 0]] )
                    break
                elif prev_node_obj['_type'] == 'TexAColorOp':
                    if prev_node[1] == 'color_a':
                        input_ = 1
                    elif prev_node[1] == 'color_b':
                        input_ = 2
                    if input_ != None:
                        self.links.append( [[nodeName, 1], [prev_node_obj['_name'], input_]] )
                    break

        elif node['_type'] == 'BRDFVRayMtl':
            nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeExtendedMaterial')
            nodeoccl.name = nodeName
            mat_name = "{0}_material".format(self.mat_name)
            #print (len(mat_name))
            #NTMAsh_v_madera_asientoNBRDFVRayMtlMAsh_v_madera_asiento_materi
            #63
            #NTMAsh_v_madera_asientoNBRDFVRayMtlMAsh_v_madera_asiento
            try:
                D.materials[mat_name]
            except:
                D.materials.new(name=mat_name)

            node_mat = D.materials[mat_name]
            nodeoccl.material = node_mat

            if type(node['diffuse']) == vr_acolor:
                # Color (0)
                nodeoccl.inputs[0].default_value[0] = node['diffuse'].r
                nodeoccl.inputs[0].default_value[1] = node['diffuse'].g
                nodeoccl.inputs[0].default_value[2] = node['diffuse'].b
                nodeoccl.inputs[0].default_value[3] = node['diffuse'].a
            if type(node['opacity']) in [int, float]:
                # Alpha (9)
                nodeoccl.inputs[9].default_value = node['opacity']
            if type(node['reflect']) == vr_acolor:
                # Mirror (4)
                nodeoccl.inputs[4].default_value[0] = node['reflect'].r
                nodeoccl.inputs[4].default_value[1] = node['reflect'].g
                nodeoccl.inputs[4].default_value[2] = node['reflect'].b
                nodeoccl.inputs[4].default_value[3] = node['reflect'].a
                if node['reflect'].r != 0 or node['reflect'].r != 0 or node['reflect'].r != 0:
                    nodeoccl.material.raytrace_mirror.use = True
            if type(node['reflect']) == vr_link:
                nodeoccl.material.raytrace_mirror.use = True
                nodeoccl.material.raytrace_mirror.reflect_factor = 1
            if type(node['self_illumination']) == vr_acolor:
                # Emit (6)
                nodeoccl.inputs[6].default_value = (node['self_illumination'].r+node['self_illumination'].g+node['self_illumination'].b)/3
            if type(node['translucency']) in [int, float]:
                # Translucency (10)
                nodeoccl.inputs[10].default_value = node['translucency']
            #TODO Fix:
            nodeoccl.material.diffuse_intensity = 1

            for prev_node in reversed(vray_chain):
                prev_node_obj = self.vray_nodes[prev_node[0]]
                if prev_node_obj['_type'] == 'MtlSingleBRDF':
                    self.links.append( [[nodeName, 0], [prev_node_obj['_name'], 0]] )
                    break

            #self.internal_data[node]['_blnode'] = nodeoccl
            #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])
        elif node['_type'] == 'TexAColorOp':
            nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeMixRGB')
            nodeoccl.name = nodeName

            if type(node['color_a']) == vr_acolor:
                nodeoccl.inputs[1].default_value[0] = node['color_a'].r
                nodeoccl.inputs[1].default_value[1] = node['color_a'].g
                nodeoccl.inputs[1].default_value[2] = node['color_a'].b
                nodeoccl.inputs[1].default_value[3] = node['color_a'].a
            if type(node['color_b']) == vr_acolor:
                nodeoccl.inputs[1].default_value[0] = node['color_b'].r
                nodeoccl.inputs[1].default_value[1] = node['color_b'].g
                nodeoccl.inputs[1].default_value[2] = node['color_b'].b
                nodeoccl.inputs[1].default_value[3] = node['color_b'].a

            #self.internal_data[node]['_blnode'] = nodeoccl
            #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])
            for prev_node in reversed(vray_chain):
                prev_node_obj = self.vray_nodes[prev_node[0]]
                input_ = None
                if prev_node_obj['_type'] == 'BRDFBump':
                    break
                elif prev_node_obj['_type'] == 'BRDFVRayMtl':
                    if prev_node[1] == 'diffuse':
                        input_ = 0
                    elif prev_node[1] == 'reflect':
                        input_ = 4
                    if input_ != None:
                        self.links.append( [[nodeName, 0], [prev_node_obj['_name'], input_]] )
                    break
                elif prev_node_obj['_type'] == 'TexLayered':
                    self.links.append( [[nodeName, 0], [prev_node_obj['_name'], 0]] )
                    break
                elif prev_node_obj['_type'] == 'TexAColorOp':
                    if prev_node[1] == 'color_a':
                        input_ = 1
                    elif prev_node[1] == 'color_b':
                        input_ = 2
                    if input_ != None:
                        self.links.append( [[nodeName, 0], [prev_node_obj['_name'], input_]] )
                    break
        elif node['_type'] == 'TexAColor':
            nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeRGB')
            nodeoccl.name = nodeName
            if type(node['texture']) == vr_acolor:
                nodeoccl.outputs[0].default_value[0] = node['texture'].r
                nodeoccl.outputs[0].default_value[1] = node['texture'].g
                nodeoccl.outputs[0].default_value[2] = node['texture'].b
                nodeoccl.outputs[0].default_value[3] = node['texture'].a
            #self.internal_data[node]['_blnode'] = nodeoccl
            #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])
            for prev_node in reversed(vray_chain):
                prev_node_obj = self.vray_nodes[prev_node[0]]
                input_ = None
                if prev_node_obj['_type'] == 'BRDFBump':
                    break
                elif prev_node_obj['_type'] == 'BRDFVRayMtl':
                    if prev_node[1] == 'diffuse':
                        input_ = 0
                    elif prev_node[1] == 'reflect':
                        input_ = 4
                    if input_ != None:
                        self.links.append( [[nodeName, 0], [prev_node_obj['_name'], input_]] )
                    break
                elif prev_node_obj['_type'] == 'TexLayered':
                    self.links.append( [[nodeName, 0], [prev_node_obj['_name'], 0]] )
                    break
                elif prev_node_obj['_type'] == 'TexAColorOp':
                    if prev_node[1] == 'color_a':
                        input_ = 1
                    elif prev_node[1] == 'color_b':
                        input_ = 2
                    if input_ != None:
                        self.links.append( [[nodeName, 0], [prev_node_obj['_name'], input_]] )
                    break
        elif node['_type'] == 'TexLayered':
            nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeMixRGB')
            nodeoccl.name = nodeName
            #self.internal_data[node]['_blnode'] = nodeoccl
            #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])
            for prev_node in reversed(vray_chain):
                prev_node_obj = self.vray_nodes[prev_node[0]]
                input_ = None
                if prev_node_obj['_type'] == 'BRDFBump':
                    break
                elif prev_node_obj['_type'] == 'BRDFVRayMtl':
                    if prev_node[1] == 'diffuse':
                        input_ = 0
                    elif prev_node[1] == 'reflect':
                        input_ = 4
                    if input_ != None:
                        self.links.append( [[nodeName, 0], [prev_node_obj['_name'], input_]] )
                    break
                elif prev_node_obj['_type'] == 'TexLayered':
                    self.links.append( [[nodeName, 0], [prev_node_obj['_name'], 0]] )
                    break
                elif prev_node_obj['_type'] == 'TexAColorOp':
                    if prev_node[1] == 'color_a':
                        input_ = 1
                    elif prev_node[1] == 'color_b':
                        input_ = 2
                    if input_ != None:
                        self.links.append( [[nodeName, 0], [prev_node_obj['_name'], input_]] )
                    break
        elif node['_type'] == 'TexDirt':
            nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeMixRGB')
            nodeoccl.name = nodeName
            #self.internal_data[node]['_blnode'] = nodeoccl
            #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])
            for prev_node in reversed(vray_chain):
                prev_node_obj = self.vray_nodes[prev_node[0]]
                input_ = None
                if prev_node_obj['_type'] == 'BRDFBump':
                    break
                elif prev_node_obj['_type'] == 'BRDFVRayMtl':
                    if prev_node[1] == 'diffuse':
                        input_ = 0
                    elif prev_node[1] == 'reflect':
                        input_ = 4
                    if input_ != None:
                        self.links.append( [[nodeName, 0], [prev_node_obj['_name'], input_]] )
                    break
                elif prev_node_obj['_type'] == 'TexLayered':
                    self.links.append( [[nodeName, 0], [prev_node_obj['_name'], 0]] )
                    break
                elif prev_node_obj['_type'] == 'TexAColorOp':
                    if prev_node[1] == 'color_a':
                        input_ = 1
                    elif prev_node[1] == 'color_b':
                        input_ = 2
                    if input_ != None:
                        self.links.append( [[nodeName, 0], [prev_node_obj['_name'], input_]] )
                    break
        elif node['_type'] == 'TexFalloff':
            nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeGeometry')
            nodeoccl.name = nodeName



            #self.internal_data[node]['_blnode'] = nodeoccl
            #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])
            for prev_node in reversed(vray_chain):
                prev_node_obj = self.vray_nodes[prev_node[0]]
                input_ = None
                if prev_node_obj['_type'] == 'BRDFBump':
                    break
                elif prev_node_obj['_type'] == 'BRDFVRayMtl':
                    if prev_node[1] == 'diffuse':
                        input_ = 0
                    elif prev_node[1] == 'reflect':
                        input_ = 4
                    if input_ != None:
                        self.links.append( [[nodeName, 5], [prev_node_obj['_name'], input_]] )
                    break
                elif prev_node_obj['_type'] == 'TexLayered':
                    self.links.append( [[nodeName, 5], [prev_node_obj['_name'], 0]] )
                    break
                elif prev_node_obj['_type'] == 'TexAColorOp':
                    if prev_node[1] == 'color_a':
                        input_ = 1
                    elif prev_node[1] == 'color_b':
                        input_ = 2
                    if input_ != None:
                        self.links.append( [[nodeName, 5], [prev_node_obj['_name'], input_]] )
                    break
        elif node['_type'] == 'UVWGenMayaPlace2dTexture':
            nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeGeometry')
            nodeoccl.name = nodeName
            #self.internal_data[node]['_blnode'] = nodeoccl
            nodeoccl.uv_layer = node['uv_set_name']

            nolink = True
            for prev_node in reversed(vray_chain):
                prev_node_obj = self.vray_nodes[prev_node[0]]
                if prev_node_obj['_type'] == 'BitmapBuffer':
                    self.links.append( [[nodeName, 4], [prev_node_obj['_name'], 0]] )
                    nolink = False
                    break
            if nolink:
                print ("WARNING: Node {0} not linked".format(nodeName))
                pprint.pprint( vray_chain )
            #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])

        #print ("vray_chain")
        #print (vray_chain)
        vray_chain_tmp = list(vray_chain)
        #print ("vray_chain_tmp")
        #print (vray_chain_tmp)

        for prop in node:
            if prop[0] == '_':
                continue

            vray_chain_tmp = list(vray_chain + [[node['_name'], prop]] )

            if type(node[prop]) == list:
                for nname in node[prop]:
                    if nname in self.vray_nodes:
                        self.get_connections( self.vray_nodes[nname], mat, vray_chain_tmp )
            elif type(node[prop]) == vr_link:
                if node[prop].name in self.vray_nodes:
                    #print ("Connection {0} -> {1}".format(node['_name'], node[prop]))
                    self.get_connections( self.vray_nodes[node[prop].name], mat, vray_chain_tmp )


    def execute(self, context):
        print ("Importing")
        C = context
        D = bpy.data

        vrscene_files = []
        for fn in self.files:
            vrscene_files.append( os.path.join(self.directory, fn.name) )

        re_nodes = {}
        for node_type in vray_data.nodes_properties:
            re_nodes[node_type] = {}
            for np in vray_data.nodes_properties[node_type]:
                re_nodes[node_type][np] = re.compile('^.*?{0}\s*=\s*(?P<{0}>\S+?)\s*;'.format(np), re.MULTILINE)

            re_nodes[node_type]['_main'] = re.compile(r'''^\s*{0}\s+(?P<name>\S+?)\s*\{{
            (?P<content>.*?)
            \}}'''.format(node_type), re.MULTILINE|re.DOTALL|re.VERBOSE)

        for vrsf in vrscene_files:
            with open (vrsf, "r") as myfile:
                data=myfile.read()

            output_node = None
            self.vray_nodes = {}
            self.links = []
            for node_type in vray_data.nodes_properties:
                m = re_nodes[node_type]['_main'].finditer(data)
                if m:
                    for match_node in m:
                        node_data = {
                            '_type' : node_type,
                            '_name' : match_node.group('name')
                        }
                        for np in vray_data.nodes_properties[node_type]:
                            if np == '_main':
                                continue
                            match_content = re_nodes[node_type][np].search(match_node.group('content'))
                            if match_content:
                                converted_prop = vray_data.convert_prop(match_content.group(np))
                                node_data[np] = converted_prop
                        self.vray_nodes[ match_node.group('name') ] = node_data
                        if node_type == 'MtlSingleBRDF':
                            output_node_name = match_node.group('name')

            output_node = self.vray_nodes[output_node_name]

            # Create Material

            self.mat_name = os.path.split(vrsf)[1]

            try:
                D.materials[self.mat_name]
            except:
                D.materials.new(name=self.mat_name)

            mat = D.materials[self.mat_name]
            mat.use_nodes = True

            self.get_connections(output_node, mat)

            #mat.node_tree.nodes['Material Output']


            for link in self.links:
                #print (link)
                if link[0][0] not in mat.node_tree.nodes:
                    print ("ERROR: {0} Blender node not found".format(link[0][0]))
                    break
                if link[1][0] not in mat.node_tree.nodes:
                    print ("ERROR: {0} Blender node not found".format(link[1][0]))
                    break
                node_a = mat.node_tree.nodes[link[0][0]]
                node_a_n = link[0][1]
                node_b = mat.node_tree.nodes[link[1][0]]
                node_b_n = link[1][1]
                mat.node_tree.links.new(node_b.inputs[node_b_n], node_a.outputs[node_a_n])

            #pprint.pprint (vray_nodes[output_node])
            #pprint.pprint (vray_nodes)
            #pprint.pprint (self.links)
            #NTMAsh_v_asiento_lotNBRDFVRayMtlMAsh_v_asiento_lot
            #NTMAsh_v_madera_asientoNBRDFVRayMtlMAsh_v_madera_asiento

        return {'FINISHED'}


# Register
def import_vray_mat_button(self, context):
    self.layout.operator(IMPORT_OT_vray_material.bl_idname,
                         text="V-Ray materials (.vrscene)", icon='MATERIAL')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(import_vray_mat_button)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(import_vray_mat_button)


if __name__ == "__main__":
    register()
