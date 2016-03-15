import os
import bpy
import json
import pprint

D = bpy.data
C = bpy.context

file = D.filepath
file = os.path.split( file )[1]
file = file.split('.')[0]

C.scene.vray.Exporter.ntreeExportDirectory = "//vraymaterials/{0}/".format(file)

print (file)

material_tree = {}

for mat in D.materials:
    for n in range(0, len(bpy.data.node_groups)):
        if bpy.data.node_groups[n] == mat.vray.ntree:
            print (mat.vray.ntree.name)
            C.scene.vray.Exporter.ntreeListIndex = n
            bpy.ops.vray.export_nodetree()
            material_tree[ mat.name ] = mat.vray.ntree.name

pprint.pprint (material_tree)

jtext = json.dumps( material_tree )

jpath = os.path.join(file, 'elinker.conf')

file = os.path.join(os.path.split(D.filepath)[0], 'vraymaterials', file, 'material_tree.json')
print (file)

with open(file, 'w') as jfile:
    jfile.write( jtext )
