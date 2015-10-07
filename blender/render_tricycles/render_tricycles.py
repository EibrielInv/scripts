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

# Based on code from Iñigo Quiles:
#http://iquilezles.org/www/articles/simplepathtracing/simplepathtracing.htm

bl_info = {
    'name': "Tricycles Render Engine",
    'author': "Iñigo Quilez, Eibriel",
    'version': (0, 0, 1),
    'blender': (2, 70, 0),
    'location': "Render > Tricycles Render",
    'warning': "Experimental",
    'description': "Python Path Traceing render engine",
    'category': 'Render'}

import bpy, random, math
from bpy.props import FloatProperty, IntProperty, BoolProperty
from mathutils import *

def random2f():
    return Vector((random.random(), random.random()))

def random1f():
    return random.random()

def adapt(selobj):

    # Rotating / panning / zooming 3D view is handled here.
    # Creates a matrix.
    if selobj.rotation_mode == "AXIS_ANGLE":
        # object rotation_quaternionmode axisangle
        ang, x, y, z =  selobj.rotation_axis_angle
        matrix = Matrix.Rotation(-ang, 4, Vector((x, y, z)))
    elif selobj.rotation_mode == "QUATERNION":
        # object rotation_quaternionmode euler
        w, x, y, z = selobj.rotation_quaternion
        x = -x
        y = -y
        z = -z
        quat = Quaternion([w, x, y, z])
        matrix = quat.to_matrix()
        matrix.resize_4x4()
    else:
        # object rotation_quaternionmode euler
        ax, ay, az = selobj.rotation_euler
        mat_rotX = Matrix.Rotation(-ax, 4, 'X')
        mat_rotY = Matrix.Rotation(-ay, 4, 'Y')
        mat_rotZ = Matrix.Rotation(-az, 4, 'Z')
        if selobj.rotation_mode == "XYZ":
            matrix = mat_rotX * mat_rotY * mat_rotZ
        elif selobj.rotation_mode == "XZY":
            matrix = mat_rotX * mat_rotZ * mat_rotY
        elif selobj.rotation_mode == "YXZ":
            matrix = mat_rotY * mat_rotX * mat_rotZ
        elif selobj.rotation_mode == "YZX":
            matrix = mat_rotY * mat_rotZ * mat_rotX
        elif selobj.rotation_mode == "ZXY":
            matrix = mat_rotZ * mat_rotX * mat_rotY
        elif selobj.rotation_mode == "ZYX":
            matrix = mat_rotZ * mat_rotY * mat_rotX
    # handle object scaling
    sx, sy, sz = selobj.scale
    mat_scX = Matrix.Scale(sx, 4, Vector([1, 0, 0]))
    mat_scY = Matrix.Scale(sy, 4, Vector([0, 1, 0]))
    mat_scZ = Matrix.Scale(sz, 4, Vector([0, 0, 1]))
    matrix = mat_scX * mat_scY * mat_scZ * matrix

    return matrix
    
class RenderFrame(bpy.types.Operator):
    """Start Render"""
    bl_idname = "tricycles.render_frame"
    bl_label = "Render Frame"
    bl_description = "Render Current Frame"
        
    def worldMoveObjects(self,  frame ):
        #Go to de current frame (no action needed)
        return

    def worldMoveCamera(self, frame, camera):
        #Get Camera Matrix
        #Camera Position
        ro = camera.location
        ro = Vector((ro.x, ro.y, ro.z));
        
        #Camera rotation TODO
        cm = camera.matrix_world.to_3x3()
        """0,1,0
        1,0,0
        
        1,0, 0
        0,0,-1
        0,1, 0"""

        rotation = Euler((math.radians(180.0), math.radians(0.0), math.radians(90.0)), 'XYZ')
        #Euler.to_matrix()
        rot = cm.to_euler('XYZ')
        rot.rotate(rotation)
        rot[0] = -rot[0]
        cm = rot.to_matrix()
        #cm.rotate(rot)

        uu = cm[0]
        vv = cm[1]
        ww = cm[2]
        #uu.negate()
        #vv.negate()
        #ww.negate()
        #ww = Vector((0, 1, 0))
        #uu = Vector((1, 0, 0))
        #uu = uu.cross(ww)
        #uu.normalize()
        #vv = ww.cross(uu)
        #vv.normalize()
        
        """uu = cm[0]
        vv = cm[1]
        ww = cm[2]"""
        return (ro, uu, vv, ww)

    def worldGetBackground(self, rd):
        scene = bpy.context.scene
        if scene.world:
            ret = scene.world.horizon_color
        else:
            ret = Color()
        return ret

    def worldGetColor(self, obj):
        #We just take the color, no textures will be implemented
        col = obj.color
        col = Color((col[0], col[1], col[2]))
        return col

    def worldApplyLighting(self, pos, nor, rd, obj ):
        """if obj.name=='Sphere':
            dcol = Color((2., 2., 2.))
        else:
            dcol = Color((0., 0., 0.))"""

        dcol = Color((0., 0., 0.))
        esc_obj = bpy.context.scene.objects
        for light in esc_obj:
            if light.type == 'LAMP' and light.data.type=='POINT':
                dist = 1000.
                ro = light.location
                rd[0] = pos[0]-ro[0]
                rd[1] = pos[1]-ro[1]
                rd[2] = pos[2]-ro[2]
                rd.normalize()
                
                ldot = rd.dot(nor)
                ldot = -ldot
                if ldot<0.:
                    ldot=0.

                ray = self.worldIntersect( ro, rd, dist )
                if ray[0] and ray[1]==obj:
                    dcol += light.data.color*light.data.energy*ldot
        
        #dcol = Color((nor.x, nor.y, nor.z))
        #dcol = Color((pos.x, pos.y, pos.z))
        return dcol

    def worldIntersect(self, ro, rd, dist ):
        #Instead of building a BVH, we just trace a ray
        ray = bpy.context.scene.ray_cast(ro, ro+(rd*dist))
        ray = list(ray)
        if ray[0]:
            from_ = ro
            to_ = ro+(rd*dist)
            obj = ray[1]
            localfrom = (from_ - obj.location) * adapt(obj).inverted()
            localto = (to_ - obj.location) * adapt(obj).inverted()
            ray_obj = obj.ray_cast(localfrom, localto)
        
            ray_obj = list(ray_obj)
            
            #normales de local a global
            wmtx = obj.matrix_world
            ray_obj[1] = wmtx.to_3x3().inverted().transposed() * ray_obj[1]
            ray_obj[1].normalize()
            
            ray[4] = ray_obj[1] #nor
        
        return ray
        
    def worldGetBRDFRay(self, pos, nor, eye, obj):
        
        if random1f() > obj.tcl_reflection :
            #Crappy function that fires rays everywhere
            radius = 90.
            eul = Euler((math.radians((random1f()*(radius*2))-radius), math.radians(0.0), math.radians((random1f()*(radius*2))-radius)), 'XYZ')
            nor.rotate(eul)
        else:
            #Hard Reflection
            #-2*(V dot N)*N + V
            nor = -2.*eye.dot(nor)*nor + eye
        
        return nor
        
        #TODO
        #if random1f() < 0.8 :
        #    return cosineDirection( nor )
        #else:
        #    return coneDirection( reflect(eye,nor), 0.9 )

    def rendererCalculateColor(self,  ro, rd, numLevels ):
        # after some recursion level, we just don't gather more light
        if numLevels==0:
            return Color((0.0, 0.0, 0.0))

        # intersect scene
        tres = self.worldIntersect( ro, rd, 100.0 )
            
        # if nothing found, return background color
        if not tres[0]:
           return self.worldGetBackground( rd )

        # get position and normal at the intersection point
        obj = tres[1]
        eye = tres[2]
        pos = tres[3]
        nor = tres[4]
        
        # get color for the surface
        scol = self.worldGetColor( obj )

        # compute direct lighting
        dcol = self.worldApplyLighting( pos, nor, rd, obj )

        # compute indirect lighting
        rd = self.worldGetBRDFRay( pos, nor, rd, obj )
        icol = self.rendererCalculateColor( pos, rd, numLevels-1 )

        # surface * lighting
        dcol = dcol + icol
        tcol = Color((scol[0]*dcol[0], scol[1]*dcol[1], scol[2]*dcol[2]))
        
        #tcol = dcol
        return tcol
        
    def calcPixelColor(self,  pixel, resolution, frameTime):
        shutterAperture = 0.6
        C = bpy.context
        fov = C.scene.camera.data.lens/10
        focusDistance = C.scene.camera.data.dof_distance
        blurAmount = C.scene.tcl_blur_amount
        numLevels = C.scene.tcl_bounces

        samples = C.scene.tcl_samples

        #paths per pixel
        col = Color()
        for i in range(0, samples):
            # screen coords with antialiasing
            p = (-resolution + 2.0*(pixel + random2f())) / resolution.y
            
            # motion blur
            ctime = frameTime + shutterAperture*(1.0/24.0)*random1f()

            # move objects
            self.worldMoveObjects( ctime )

            # get camera position, and right/up/front axis
            (ro, uu, vv, ww) = self.worldMoveCamera( ctime, C.scene.camera )

            # create ray with depth of field
            er = Vector((p.x, p.y, fov))
            er.normalize()
            rd = er.x*uu + er.y*vv + er.z*ww
            
            if focusDistance == 0.:
                blurAmount = 0.
            
                """
            vec3 go = blurAmount*vec3( -1.0 + 2.0*random2f(), 0.0 );
            vec3 gd = normalize( er*focusDistance - go );
            ro += go.x*uu + go.y*vv;
            rd += gd.x*uu + gd.y*vv;
            
            vec3( -1.0 + 2.0*random2f(), 0.0 );"""
            
                rn = random2f()
                rn[0] = -1.+(rn[0]*2.)
                rn[1] = -1.+(rn[1]*2.)
                go = Vector((rn[0], rn[1], 0.0))
                go = blurAmount*go
                
                gd = (er*focusDistance) - go
                gd.normalize()
                ro += go.x*uu + go.y*vv
                rd += gd.x*uu + gd.y*vv


            # accumulate path
            col += self.rendererCalculateColor( ro, rd.normalized(), numLevels )
        col = col / samples
        # apply gamma 
        col = Color((pow(col[0],0.45), pow(col[1],0.45), pow(col[2],0.45) ))
        return col
         
    def invoke(self, context, event):
        C = context
        D = bpy.data
    
        img = context.space_data.image
        print ("Saving to %s(%sw%sh)" % (img.name, img.generated_width, img.generated_height))
        
        resolution = Vector((img.generated_width, img.generated_height))
        frame = 1.

        pix_cache = []
        for x in range(0, int(resolution.x)):
            for y in range(0, int(resolution.y)):
                
                pixel = Vector((x, y))
                col = self.calcPixelColor( pixel, resolution, frame)
                pix_cache.append(col)
                
        pix = 0
        for p in pix_cache:
            img.pixels[pix]=p[0]
            img.pixels[pix+1]=p[1]
            img.pixels[pix+2]=p[2]
            img.pixels[pix+3]=1.
            pix = pix + 4 
                           
        return {'FINISHED'}
        
class TLS_IMAGE_HT_header(bpy.types.Header):
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        space = context.space_data
        #print (sima.type)
        return space.type == 'IMAGE_EDITOR'

    def draw(self, context):
        space = context.space_data
        if not space.image:
            return
        
        layout = self.layout
        layout.operator("tricycles.render_frame", text="", icon="RENDER_STILL")

class RENDER_PT_tricycles_render(bpy.types.Panel):
    bl_label = "Tricycles Render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="The render button is at:")
        layout.label(text="IMAGE EDITOR")
        layout.prop(context.scene, "tcl_samples")
        layout.prop(context.scene, "tcl_blur_amount")
        layout.prop(context.scene, "tcl_bounces")

class OBJECT_PT_tricycles_render(bpy.types.Panel):
    bl_label = "Tricycles Render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        layout.prop(context.active_object, "tcl_reflection")
    
classes =  (TLS_IMAGE_HT_header,
            RENDER_PT_tricycles_render,
            OBJECT_PT_tricycles_render,
            RenderFrame)

def register():
    bpy.types.Scene.tcl_samples = IntProperty(name="Samples",
        description="Number of times Tricycles computes the same pixel",
        default=1,
        min=1)
        
    bpy.types.Scene.tcl_blur_amount = FloatProperty(name="Blur Amount",
        description="DoF Blur Radius",
        default=0.0015,
        min=0.)
    
    bpy.types.Scene.tcl_bounces = IntProperty(name="Bounces",
        description="Number of times a Ray is fired",
        default=3,
        min=0)
        
    bpy.types.Object.tcl_reflection = FloatProperty(name="Reflection",
        description="Probability to fire a Reflection Ray",
        default=0.5,
        min=0.,
        max=1.)
    
    for c in classes:
        bpy.utils.register_class(c)
    
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    
if __name__ == "__main__":
    register()
