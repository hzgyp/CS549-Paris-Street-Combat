import bpy, json, sys
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
src=root/'tmp/g1-grenade-models-20261011/asset_lookup/equipment_v1/Equipment.glb'
out=src.parent/'geometry_inspection';out.mkdir(exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src))
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    o.data.calc_loop_triangles()
    rows.append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'materials':[m.name for m in o.data.materials],'dimensions':list(o.dimensions)})
    print('MESH',rows[-1],flush=True)
(out/'meshes.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'EquipmentInspection.blend'))
