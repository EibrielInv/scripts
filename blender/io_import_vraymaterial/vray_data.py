import re


class vr_link:
    def __init__(self, link):
        link_list = link.split('::')
        self.output = None
        self.name = link_list[0]
        if len(link_list) > 1:
            self.output = link_list[1]

    def __repr__(self):
        return "vr_link({0}::{1})".format(self.name, self.output)


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


class vray_data:
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

    nodes_properties['TexDirt'] = {
        'affect_reflection_elements': '',
        'affect_result_nodes_inclusive': '',
    	'bias_x': '',
    	'bias_y': '',
    	'bias_z': '',
    	'black_color': '',
    	'consider_same_object_only': '',
    	'distribution': '',
    	'double_sided': '',
    	'environment_occlusion': '',
    	'falloff': '',
    	'glossiness': '',
    	'ignore_for_gi': '',
    	'ignore_self_occlusion': '',
    	'invert_normal': '',
    	'mode': '',
    	'radius': '',
    	'render_nodes_inclusive': '',
    	'subdivs': '',
    	'white_color': '',
    	'work_with_transparency': '',
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

    def convert_prop(prop):
        #Prop convertor
        #converted_prop = match_content.group(np)
        converted_prop = prop
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

        return converted_prop
