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

bl_info = {
    "name": "Translucency to Vertex Color",
    "author": "Eibriel",
    "version": (0, 2),
    "blender": (2, 81, 0),
    "location": "View3D > Sidebar > Tool",
    "description": "Bake Translucency to Vertex Color",
    "warning": "",
    "wiki_url": "https://www.patreon.com/eibriel",
    "tracker_url": "https://www.patreon.com/eibriel",
    "category": "Eibriel"}


class eibrielTranslucency (bpy.types.Operator):
    """Fill selected vertex color layer of selected objects with translucency value
    using active object as light source"""
    bl_idname = "t2vc.translucency2vertexcolor"
    bl_label = "Translucency to Vertex Color"
    bl_options = {"REGISTER", "UNDO"}

    max_depth : bpy.props.IntProperty(name="Max Depth", description="High values for higher translucency", default=5, min=0)
    bias : bpy.props.FloatProperty(name="Ray Bias", description="Increment to fix dark spots artifacts", default=0.00001, min=0)

    @classmethod
    def poll(cls, context):
        epoll = True

        a = context.active_object
        objcount = 1
        for ob in context.selected_objects:
            if ob == a:
                continue
            objcount += 1
            if ob.type not in ["MESH"]:
                epoll = False

        if objcount < 2:
            epoll = False

        return epoll

    def test_ray(self, context, from_, to_):
        # vect = mathutils.Vector([to_[0] * self.bias, to_[1] * self.bias, to_[2] * self.bias])
        # ray = context.scene.ray_cast(context.view_layer, from_ + vect, to_)

        direction = from_ - to_
        direction = -direction
        distance = direction.length
        vect = mathutils.Vector([direction.normalized()[0] * self.bias, direction.normalized()[1] * self.bias, direction.normalized()[2] * self.bias])
        D = bpy.data
        # D.objects["Empty.001"].location = from_
        # D.objects["Empty.002"].location = from_ + vect
        # D.objects["Empty.003"].location = direction
        ray = context.scene.ray_cast(context.view_layer, from_ + vect, direction.normalized(), distance=distance)
        if 0:
            ray = (
                True,
                mathutils.Vector((-0.13207609951496124, -0.10863813757896423, 1.3594014644622803)),
                mathutils.Vector((-0.6964025497436523, -0.6247992515563965, -0.35305720567703247)),
                76411,
                bpy.data.objects['Tilia_platyphyllos_04(12.1m).001'],
                mathutils.Matrix(((0.010000000707805157, 0.0, 0.0, 0.0), (0.0, 0.010000000707805157, 4.371139006309477e-10, 0.0), (0.0, -4.371139006309477e-10, 0.010000000707805157, 0.0), (0.0, 0.0, 0.0, 1.0)))
            )
        return ray

    def test_ray_BVH(self, BVH, context, from_, to_):
        vect = mathutils.Vector([to_[0] * self.bias, to_[1] * self.bias, to_[2] * self.bias])
        # ray = context.scene.ray_cast(context.view_layer, from_ + vect, to_)
        raw_ray = BVH.ray_cast(from_ + vect, to_)
        location, normal, index, distance = raw_ray
        # print(raw_ray)
        if location is not None:
            result = True
        else:
            result = False

        ray = (
            result,
            location,
            0,
            0,
            0,
            ()
        )
        # result, location, normal, index, object, matrix
        # print(ray)
        return ray

    def execute(self, context):
        C = context
        D = bpy.data
        light = C.active_object
        objects = C.selected_objects
        max_depth = self.max_depth

        for obj in objects:
            if obj == light:
                continue
            if obj.type != "MESH":
                self.report({'WARNING'}, "{0} is not of type MESH".format(obj.name))
                continue
            mesh = obj.data

            VC = mesh.vertex_colors.active
            if not VC:
                self.report({'WARNING'}, "{0} don't have an active Vertex Color group".format(obj.name))
                continue
            VX = mesh.vertices
            VP = mesh.polygons
            # BVH = mathutils.bvhtree.BVHTree.FromObject(obj, context.view_layer.depsgraph)

            if 0:
                C.window_manager.progress_begin(0, 100)
                count = 0
                progress_max = len(VC.data)
                for d in VC.data:
                    progress = int(count * (100 / progress_max))
                    C.window_manager.progress_update(progress)
                    count += 1
                    d.color = (0, 1, 0, 1)
                C.window_manager.progress_end()

                count = 0
                for p in VP:
                    for v in p.vertices:
                        VC.data[count].color = (0, 0, 1, 1)
                        count += 1

            countt = 0
            pcount = 0
            C.window_manager.progress_begin(0, 100)
            progress_max = len(VP)
            light_loc = light.location
            done_vertex = []
            for p in VP:
                progress = int(pcount * (100 / progress_max))
                C.window_manager.progress_update(progress)
                pcount += 1
                for v in p.vertices:
                    # if v in done_vertex:
                    #     continue
                    # done_vertex.append(v)
                    from_ = VX[v].co
                    mat = obj.matrix_world
                    from_ = mat @ from_
                    ray = self.test_ray(C, from_, light_loc)
                    # result, object, matrix, location, normal = ray
                    result, location, normal, index, object, matrix = ray

                    count = 0
                    while result:
                        # result, object, matrix, location, normal = ray
                        result, location, normal, index, object, matrix = ray
                        if not result:
                            break
                        # world_location = object.matrix_world @ location
                        ray = self.test_ray(C, location, light_loc)
                        count += 1
                        if count >= max_depth:
                            break

                    count = max_depth - count
                    val = float(count) / max_depth
                    VC.data[countt].color = (val, val, val, 1.0)
                    countt += 1
            C.window_manager.progress_end()

        return {'FINISHED'}


class VIEW3D_PT_tools_ETRANSL_object(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Translucency to Vertex Color"
    bl_category = "Tool"

    def draw(self, context):
        self.layout.operator("t2vc.translucency2vertexcolor")


def register():
    # bpy.utils.register_module(__name__)
    bpy.utils.register_class(eibrielTranslucency)
    bpy.utils.register_class(VIEW3D_PT_tools_ETRANSL_object)


def unregister():
    # bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(eibrielTranslucency)
    bpy.utils.unregister_class(VIEW3D_PT_tools_ETRANSL_object)


if __name__ == "__main__":
    register()
