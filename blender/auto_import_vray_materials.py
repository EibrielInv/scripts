import os
import bpy
import json
import pprint

D = bpy.data
C = bpy.context

file = D.filepath
file = os.path.split( file )[1]
file = file.split('.')[0]

vrscene_directory = '//vraymaterials/{0}/'.format(file)

print (file)

material_tree = {}
files2open = []

material_tree_file = os.path.join(os.path.split(D.filepath)[0], 'vraymaterials', file, 'material_tree.json')
with open(material_tree_file, 'r') as jfile:
    jtext = jfile.read()
    jdata = json.loads( jtext )

for mat in jdata:
    vrngname = jdata[mat].replace('.', '_')
    matname = '{0}.vrscene'.format(vrngname)
    #print (D.materials[matname])
    vrscene_path = os.path.join(os.path.split(D.filepath)[0], 'vraymaterials', file, matname)
    bpy.ops.vray.import_material(file_path=vrscene_path)

    #Colocar el material en su lugar original
    for obj in D.objects:
        for mslot in obj.material_slots:
            if mslot and mslot.material and not mslot.material.is_library_indirect:
                if mslot.material.name == mat:
                    print ( "{0} -> {1}".format(mslot.material.name, D.materials[matname].name) )
                    mslot.material = D.materials[matname]

    for obj in D.objects:
        for mslot in obj.material_slots:
            if mslot and mslot.material:
                if mslot.material.name[:5] == 'MAsh_':
                    mslot.material.name = mslot.material.name[2:]
                if mslot.material.name[-8:] == '.vrscene':
                    mslot.material.name = mslot.material.name[:-8]
