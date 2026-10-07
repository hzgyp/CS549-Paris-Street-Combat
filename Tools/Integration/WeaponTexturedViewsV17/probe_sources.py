"""Read-only source UV/material inventory for a frozen V16 presentation."""
import hashlib
import json
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
LAB = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001'
OUT = STORE / 'Evidence/WeaponTexturedViewsV17/source_probe_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
paths = [STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx',
         STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/Sm_M1_Garand.fbx',
         LAB/'Exchange/SK_M1_Garand.blend', LAB/'Exchange/SK_WWII_US_Paratrooper_simple.blend']
hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
report = []
for p in paths:
    if p.suffix == '.fbx':
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(p), automatic_bone_orientation=False, use_anim=False)
    else:
        bpy.ops.wm.open_mainfile(filepath=str(p), load_ui=False, use_scripts=False)
    row = {'source':str(p.relative_to(ROOT)), 'meshes':[], 'materials':[]}
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        obj.data.calc_loop_triangles()
        row['meshes'].append({'name':obj.name, 'vertices':len(obj.data.vertices),
                             'triangles':len(obj.data.loop_triangles),
                             'uv_layers':[u.name for u in obj.data.uv_layers],
                             'materials':[m.name if m else None for m in obj.data.materials],
                             'slot_counts':{str(i):sum(t.material_index==i for t in obj.data.loop_triangles)
                                            for i in range(len(obj.data.materials))}})
    for mat in bpy.data.materials:
        row['materials'].append({'name':mat.name, 'native_material':mat.get('native_material'),
                                 'images':[{'name':n.image.name, 'file':bpy.path.abspath(n.image.filepath),
                                            'size':list(n.image.size), 'color_space':n.image.colorspace_settings.name,
                                            'file_exists':Path(bpy.path.abspath(n.image.filepath)).is_file()}
                                           for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
                                           if mat.use_nodes else []})
    report.append(row)
unchanged = all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
result = {'sources':report, 'input_hashes':hashes, 'inputs_unchanged':unchanged}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result),flush=True)
assert unchanged
