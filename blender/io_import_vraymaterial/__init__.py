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

class vr_link(str):
    pass

class vr_acolor:
    def __init__(self, r, g, b, a):
        self.r=r
        self.g=g
        self.b=b
        self.a=a

    def __repr__(self):
        return "vr_acolor({0}, {1}, {2}, {3})".format(self.r, self.g, self.b, self.a)

class vr_color:
    def __init__(self, r, g, b):
        self.r=r
        self.g=g
        self.b=b

    def __repr__(self):
        return "vr_color({0}, {1}, {2})".format(self.r, self.g, self.b)

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
    cycles_data = {}
    internal_data = {}
    vray_nodes = {}

    def check_val(self, value, types):
        if type(value) in types:
            return value
        else:
            return None

    def get_connections(self, node_, vray_chain=[]):
        #print (vray_chain)
        if node_['_type'] == 'MtlSingleBRDF':
            #print ("Shader single")
            #shader_data['output']['mix'] = False
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'output',
                '_parent_node': None,
                '_parent_output': None,
                'color#0': None,
                'alpha#1': None
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'output',
                '_parent_node': None,
                '_parent_output': None,
                'surface#0': None,
                'volume#1': None,
                'displacement#2': None
            }
        elif node_['_type'] == 'BRDFBump':
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'reroute',
                '_parent_node': None,
                '_parent_output': None,
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'bump',
                '_parent_node': None,
                '_parent_output': None,

            }
        elif node_['_type'] == 'BRDFVRayMtl':
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'extended_material',
                '_parent_node': vray_chain[-1],
                '_parent_output': '',
                'emit#6': self.check_val(node_['self_illumination'], [vr_acolor]),
                'color#6': self.check_val(node_['diffuse'], [vr_acolor]),
                'alpha#9': self.check_val(node_['opacity'], [int, float, vr_acolor]),
                'reflectivity#8': self.check_val(node_['reflect'], [int, float, vr_acolor]),
            }
        elif node_['_type'] == 'TexOutput':
            #print ("{0}:{1} -> Is using a Texture".format(vray_node, vray_input))
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'reroute',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'reroute',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
            }
        elif node_['_type'] == 'TexBitmap':
            #print ("{0}:{1} -> Is using a Bitmap Texture".format(vray_node, vray_input))
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'reroute',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'reroute',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
            }
        elif node_['_type'] == 'BitmapBuffer':
            #print ("{0}:{1} -> Bitmap: {2}".format(vray_node, vray_input, node_['file']))
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'image_texture',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'image': self.check_val(node_['file'], [str]),
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'image_texture',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'image': self.check_val(node_['file'], [str]),
            }
        elif node_['_type'] == 'TexLayered':
            #print ("{0}:{1} -> Is mixing Textures: {2}".format(vray_node, vray_input, node_['textures']))
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'mix_rgb',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'factor#0': 0.5,
                'color1#1': None,
                'color2#2': None,
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'mix_rgb',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'factor#0': 0.5,
                'color1#1': None,
                'color2#2': None,
            }
        elif node_['_type'] == 'TexAColor':
            #print ("{0}:{1} -> A solid color".format(vray_node, vray_input))
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'rgb',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'color#0': self.check_val(node_['texture'], [vr_acolor]),
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'rgb',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'color#0': self.check_val(node_['texture'], [vr_acolor]),
            }
        elif node_['_type'] == 'TexAColorOp':
            #print ("{0}:{1} -> Is mixing Colors or Textures".format(vray_node, vray_input))
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'mix_rgb',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'factor#0': 0.5,
                'color1#1': self.check_val(node_['color_a'], [vr_acolor]),
                'color2#2': self.check_val(node_['color_b'], [vr_acolor]),
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'mix_rgb',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'factor#0': 0.5,
                'color1#1': self.check_val(node_['color_a'], [vr_acolor]),
                'color2#2': self.check_val(node_['color_b'], [vr_acolor]),
            }
        elif node_['_type'] == 'TexFalloff':
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'geometry',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'layer_weight',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
            }
        elif node_['_type'] == 'UVWGenMayaPlace2dTexture':
            self.internal_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'geometry',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'uv_map': node_['uv_set_name'],
            }
            self.cycles_data[node_['_name']] = {
                '_name': node_['_name'],
                '_type': 'uv_map',
                '_parent_node': vray_chain[-1],
                '_parent_output': None,
                'uv_map': node_['uv_set_name'],
            }

        for prop in node_:
            if prop[0] == '_':
                continue

            #if node_['_type'] in ['BRDFVRayMtl', 'BRDFBump']:
            vray_chain.append(node_['_name'])

            if type(node_[prop]) == list:
                for nname in node_[prop]:
                    if nname in self.vray_nodes:
                        self.get_connections( self.vray_nodes[nname], vray_chain )
            elif type(node_[prop]) == vr_link:
                if node_[prop] in self.vray_nodes:
                    #print ("Connection {0} -> {1}".format(node_['_name'], node_[prop]))
                    self.get_connections( self.vray_nodes[node_[prop]], vray_chain )

    def execute(self, context):
        print ("Importing")

        vrscene_files = []
        for fn in self.files:
            vrscene_files.append( os.path.join(self.directory, fn.name) )

        nodes_properties = {}
        nodes_properties['MtlSingleBRDF'] = {
            'brdf': '',
            'allow_negative_colors': '',
            'double_sided': '',
            'filter': '',
        }

        nodes_properties['BRDFBump'] = {
            'base_brdf': '',
            'bump_delta_scale': '',
            'bump_shadows': '',
            'bump_tex_color': '',
            'bump_tex_float': '',
            'bump_tex_mult': '',
            'bump_tex_mult_tex': '',
            'compute_bump_for_shadows': '',
            'map_type': '',
            'maya_compatible': '',
        }

        nodes_properties['TexOutput'] = {
            'alpha_from_intensity': '',
            'alpha_mult': '',
            'alpha_offset': '',
            'bump_amount': '',
            'color_mult': '',
            'color_offset': '',
            'compatibility_with': '',
            'invert': '',
            'invert_alpha': '',
            'nouvw_color': '',
            'texmap': '',
        }

        nodes_properties['TexBitmap'] = {
            'alpha_from_intensity': '',
            'alpha_mult': '',
            'alpha_offset': '',
            'bitmap': '',
            'color_mult': '',
            'color_offset': '',
            'compatibility_with': '',
            'h': '',
            'invert': '',
            'invert_alpha': '',
            'jitter': '',
            'nouvw_color': '',
            'placement_type': '',
            'tile_u': '',
            'tile_v': '',
            'u': '',
            'un_noise_phase': '',
            'uv_noise_amount': '',
            'uv_noise_animate': '',
            'uv_noise_levels': '',
            'uv_noise_on': '',
            'uv_noise_size': '',
            'uvwgen': '',
            'v': '',
            'w': '',
        }

        nodes_properties['BitmapBuffer'] = {
        	'allow_negative_colors': '',
        	'color_space': '',
        	'file': '',
        	'filter_blur': '',
        	'filter_type': '',
        	'frame_number': '',
        	'frame_offset': '',
        	'frame_sequence': '',
        	'gamma': '',
        	'ifl_end_condition': '',
        	'ifl_playback_rate': '',
        	'ifl_start_frame': '',
        	'interpolation': '',
        	'load_file': '',
        	'maya_compatible': '',
        	'use_data_window': '',
        }

        nodes_properties['UVWGenMayaPlace2dTexture'] = {
        	'coverage_u_tex': '',
        	'coverage_v_tex': '',
        	'mirror_u': '',
        	'mirror_v': '',
        	'noise_u_tex': '',
        	'noise_v_tex': '',
        	'nsamples': '',
        	'offset_u_tex': '',
        	'offset_v_tex': '',
        	'repeat_u_tex': '',
        	'repeat_v_tex': '',
        	'rotate_frame_tex': '',
        	'rotate_uv_tex': '',
        	'stagger': '',
        	'translate_frame_u_tex': '',
        	'translate_frame_v_tex': '',
        	'uv_set_name': '',
        	'uvw_channel': '',
        	'wrap_u': '',
        	'wrap_v': '',
        }

        nodes_properties['BRDFVRayMtl'] = {
        	'anisotropy': '',
        	'anisotropy_axis': '',
        	'anisotropy_derivation': '',
        	'anisotropy_rotation': '',
        	'brdf_type': '',
        	'diffuse': '',
        	'dispersion': '',
        	'dispersion_on': '',
        	'environment_priority': '',
        	'fog_bias': '',
        	'fog_color': '',
        	'fog_color_tex': '',
        	'fog_mult': '',
        	'fog_unit_scale_on': '',
        	'fresnel': '',
        	'fresnel_ior': '',
        	'fresnel_ior_lock': '',
        	'hilight_glossiness': '',
        	'hilight_glossiness_lock': '',
        	'hilight_soften': '',
        	'opacity': '',
        	'option_cutoff': '',
        	'option_double_sided': '',
        	'option_energy_mode': '',
        	'option_fix_dark_edges': '',
        	'option_glossy_rays_as_gi': '',
        	'option_reflect_on_back': '',
        	'option_use_irradiance_map': '',
        	'refl_imap_color_thresh': '',
        	'refl_imap_max_rate': '',
        	'refl_imap_min_rate': '',
        	'refl_imap_norm_thresh': '',
        	'refl_imap_samples': '',
        	'refl_interpolation_on': '',
        	'reflect': '',
        	'reflect_affect_alpha': '',
        	'reflect_depth': '',
        	'reflect_dim_distance': '',
        	'reflect_dim_distance_falloff': '',
        	'reflect_dim_distance_on': '',
        	'reflect_exit_color': '',
        	'reflect_glossiness': '',
        	'reflect_subdivs': '',
        	'reflect_trace': '',
        	'refr_imap_color_thresh': '',
        	'refr_imap_max_rate': '',
        	'refr_imap_min_rate': '',
        	'refr_imap_norm_thresh': '',
        	'refr_imap_samples': '',
        	'refr_interpolation_on': '',
        	'refract': '',
        	'refract_affect_alpha': '',
        	'refract_affect_shadows': '',
        	'refract_depth': '',
        	'refract_exit_color': '',
        	'refract_exit_color_on': '',
        	'refract_glossiness': '',
        	'refract_ior': '',
        	'refract_subdivs': '',
        	'refract_trace': '',
        	'roughness': '',
        	'self_illumination': '',
        	'self_illumination_gi': '',
        	'translucency': '',
        	'translucency_color': '',
        	'translucency_light_mult': '',
        	'translucency_scatter_coeff': '',
        	'translucency_scatter_dir': '',
        	'translucency_thickness': '',
        }

        nodes_properties['TexLayered'] = {
        	'alpha': '',
        	'alpha_mult': '',
        	'alpha_offset': '',
        	'blend_modes': '',
        	'color_mult': '',
        	'color_offset': '',
        	'nouvw_color': '',
        	'textures': '',
        }

        nodes_properties['TexAColor'] = {
        	'texture': '',
        }

        nodes_properties['TexAColorOp'] = {
        	'color_a': '',
        	'color_b': '',
        	'mode': '',
        	'mult_a': '',
        	'mult_b': '',
        	'result_alpha': '',
        }

        nodes_properties['TexFalloff'] = {
        	'alpha_from_intensity': '',
        	'alpha_mult': '',
        	'alpha_offset': '',
        	'blend_input': '',
        	'color1': '',
        	'color2': '',
        	'color_mult': '',
        	'color_offset': '',
        	'compatibility_with': '',
        	'direction_type': '',
        	'dist_extrapolate': '',
        	'dist_far': '',
        	'dist_near': '',
        	'explicit_dir': '',
        	'fresnel_ior': '',
        	'invert': '',
        	'invert_alpha': '',
        	'nouvw_color': '',
        	'type': '',
        	'use_blend_input': '',
        }

        re_nodes = {}
        for node_type in nodes_properties:
            re_nodes[node_type] = {}
            for np in nodes_properties[node_type]:
                re_nodes[node_type][np] = re.compile('^.*?{0}\s*=\s*(?P<{0}>\S+?)\s*;'.format(np), re.MULTILINE)

            re_nodes[node_type]['_main'] = re.compile(r'''^\s*{0}\s+(?P<name>\S+?)\s*\{{
            (?P<content>.*?)
            \}}'''.format(node_type), re.MULTILINE|re.DOTALL|re.VERBOSE)

        for vrsf in vrscene_files:
            with open (vrsf, "r") as myfile:
                data=myfile.read()

            output_node = None
            self.vray_nodes = {}
            for node_type in nodes_properties:
                m = re_nodes[node_type]['_main'].finditer(data)
                if m:
                    for match_node in m:
                        node_data = {
                            '_type' : node_type,
                            '_name' : match_node.group('name')
                        }
                        for np in nodes_properties[node_type]:
                            if np == '_main':
                                continue
                            match_content = re_nodes[node_type][np].search(match_node.group('content'))
                            if match_content:
                                #Prop convertor
                                converted_prop = match_content.group(np)
                                list_match = re.match(r'List\((?P<content>.+?)\)', converted_prop)
                                listint_match = re.match(r'ListInt\((?P<content>.+?)\)', converted_prop)
                                color_match = re.match(r'Color\((?P<content>.+?)\)', converted_prop)
                                acolor_match = re.match(r'AColor\((?P<content>.+?)\)', converted_prop)
                                int_match = re.match(r'(?P<content>\d+)$', converted_prop)
                                float_match = re.match(r'(?P<content>\d+\.\d+)$', converted_prop)
                                str_match = re.match(r'"(?P<content>.*?)"$', converted_prop)
                                if list_match:
                                    vr_list = list_match.group('content')
                                    vr_list = vr_list.split(',')
                                    converted_prop = vr_list
                                elif listint_match:
                                    vr_listint = listint_match.group('content')
                                    vr_listint = vr_listint.split(',')
                                    for val in vr_listint:
                                        val = int(val)
                                    converted_prop = vr_listint
                                elif color_match:
                                    val_color = color_match.group('content')
                                    val_color = val_color.split(',')
                                    converted_prop = vr_color(
                                                        float(val_color[0]),
                                                        float(val_color[1]),
                                                        float(val_color[2]))
                                elif acolor_match:
                                    val_acolor = acolor_match.group('content')
                                    val_acolor = val_acolor.split(',')
                                    converted_prop = vr_acolor(
                                                        float(val_acolor[0]),
                                                        float(val_acolor[1]),
                                                        float(val_acolor[2]),
                                                        float(val_acolor[3]))
                                elif int_match:
                                    converted_prop = int(converted_prop)
                                elif float_match:
                                    converted_prop = float(converted_prop)
                                elif str_match:
                                    vr_str = str_match.group('content')
                                    converted_prop = vr_str
                                else:
                                    converted_prop = vr_link(converted_prop)

                                node_data[np] = converted_prop
                        self.vray_nodes[ match_node.group('name') ] = node_data
                        if node_type == 'MtlSingleBRDF':
                            output_node_name = match_node.group('name')

            output_node = self.vray_nodes[output_node_name]

            self.get_connections(output_node)

            pprint.pprint (self.internal_data)

            # Create Material
            C = context
            D = bpy.data

            mat_name = os.path.split(vrsf)[1]

            exist = True
            try:
                D.materials[mat_name]
            except:
                D.materials.new(name=mat_name)

            mat = D.materials[mat_name]
            mat.use_nodes = True

            #mat.node_tree.nodes['Material Output']
            nodeout_internal = None
            nodeout_cycles = None
            for node in mat.node_tree.nodes:
                if node.type == 'OUTPUT':
                    nodeout_internal = node
                if node.type == 'OUTPUT_MATERIAL':
                    nodeout_cycles = node

            if not nodeout_internal:
                nodeout_internal = mat.node_tree.nodes.new(type='ShaderNodeOutput')
            if not nodeout_cycles:
                nodeout_cycles = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')

            for node in self.internal_data:
                node_type = self.internal_data[node]['_type']
                #print (node_type)
                if node_type == 'image_texture':

                    image = load_image(self.internal_data[node]['image'])

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
                        texture = bpy.data.textures.new(name=name_compat, type='IMAGE')
                        texture.image = image
                        #self.set_texture_options(context, texture)

                    #nodeName = node
                    nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeTexture')
                    nodeoccl.texture = img_texture
                    self.internal_data[node]['_blnode'] = nodeoccl

                    #mat.node_tree.links.new(nodeout_internal.inputs[1], nodeoccl.outputs[0])

                    #nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeTexImage')
                    #nodeoccl.image = image

                    #nodes = material.node_tree.nodes
                    #img = next((node.image for node in nodes if node.type == 'TEX_IMAGE'))

                elif node_type == 'extended_material':
                    nodeName = node
                    nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeExtendedMaterial')
                    nodeoccl.name = nodeName
                    self.internal_data[node]['_blnode'] = nodeoccl
                    #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])
                elif node_type == 'mix_rgb':
                    nodeName = node
                    nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeMixRGB')
                    nodeoccl.name = nodeName
                    self.internal_data[node]['_blnode'] = nodeoccl
                    #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])
                elif node_type == 'geometry':
                    nodeName = node
                    nodeoccl = mat.node_tree.nodes.new(type='ShaderNodeUVMap')
                    nodeoccl.name = nodeName
                    self.internal_data[node]['_blnode'] = nodeoccl
                    #nodeoccl.uv_map = self.internal_data[node]['uv_map']
                    #mat.node_tree.links.new(nodeout_internal.inputs[0], nodeoccl.outputs[0])

            for node in self.internal_data:
                if self.internal_data[node]['_type'] == 'output':
                    out_node = self.internal_data[node]

            def create_links(node):
                print (node["_parent_node"])

            create_links(out_node)

            #for node in self.internal_data:
            #if not '_blnode' in self.internal_data[node]:
            #    continue
            #blnode = self.internal_data[node]['_blnode']
            #if self.internal_data[node]['_type'] == 'extended_material':
            #    mat.node_tree.links.new(nodeout_internal.inputs[0], blnode.outputs[0])
            #elif self.internal_data[node]['_type'] == 'image_texture':
            #    mat.node_tree.links.new(nodeout_internal.inputs[0], blnode.outputs[0])

            #if engine in {'BLENDER_RENDER', 'BLENDER_GAME'}:
            #    img = material.texture_slots[0].texture.image
            #elif engine == 'CYCLES':


            #pprint.pprint (vray_nodes[output_node])

            #pprint.pprint (vray_nodes)

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
