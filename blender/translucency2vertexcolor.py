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
    "name": "Translucency to Vertex Color",
    "author": "Eibriel",
    "version": (0,1),
    "blender": (2, 76, 2),
    "location": "View3D > Tool Shelf > Tools",
    "description": "Bake Translucency to Vertex Color",
    "warning": "",
    "wiki_url": "https://github.com/Eibriel/scripts/wiki",
    "tracker_url": "https://github.com/Eibriel/scripts/issues",
    "category": "Eibriel"}

import bpy
import mathutils

class eibrielSnap (bpy.types.Operator):
    """Snap selected object or bone to active object or bone"""
    bl_idname = "t2vc.translucency2vertexcolor"
    bl_label = "Translucency to Vertex Color"
    bl_options = {"REGISTER", "UNDO"}

    max_depth = bpy.props.IntProperty(name="Max Depth", description="High values for higher translucency", default=5, min=0)
    bias = bpy.props.FloatProperty(name="Ray Bias", description="Increment to fix dark spots artifacts", default=0.000001, min=0)

    @classmethod
    def poll(cls, context):
        epoll = True

        a = context.active_object
        objcount = 1
        for ob in context.selected_objects:
            if ob == a:
                continue
            objcount += 1
            if not ob.type in ["MESH"]:
                epoll = False

        if objcount < 2:
            epoll = False

        return epoll

    def execute(self,context):
        C = context
        D = bpy.data
        light = C.active_object
        objects = C.selected_objects
        max_depth = self.max_depth
        bias = self.bias

        for obj in objects:
            if obj == light:
                continue
            if obj.type != "MESH":
                self.report( {'WARNING'}, "{0} is not of type MESH".format(obj.name) )
                continue
            mesh = obj.data

            VC = mesh.vertex_colors.active
            if not VC:
                self.report( {'WARNING'}, "{0} don't have an active Vertex Color group".format(obj.name) )
                continue
            VX = mesh.vertices
            VP = mesh.polygons

            count=0
            for d in VC.data:
                count += 1
                d.color = (0,1,0)

            count = 0
            for p in VP:
                for v in p.vertices:
                    VC.data[count].color = (0,0,1)
                    count += 1

            def test_ray (from_, to_):
                vect = mathutils.Vector([to_[0]*bias, to_[1]*bias, to_[2]*bias])
                ray = C.scene.ray_cast(from_+vect, to_)
                return ray

            countt = 0
            for p in VP:
                for v in p.vertices:
                    light_loc = light.location
                    from_ = VX[v].co
                    mat = obj.matrix_world
                    from_ = mat * from_
                    ray = test_ray(from_, light_loc)
                    result, object, matrix, location, normal = ray

                    count = 0
                    while result:
                        result, object, matrix, location, normal = ray
                        ray = test_ray(location, light_loc)
                        count += 1
                        if count >= max_depth:
                            break

                    count = max_depth - count
                    val = count / max_depth
                    VC.data[countt].color = (val, val, val)
                    countt += 1

        return {'FINISHED'}

class MovPanelControl(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Translucency to Vertex Color"
    bl_category = "Tools"

    def draw(self, context):
        self.layout.operator("t2vc.translucency2vertexcolor")

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
