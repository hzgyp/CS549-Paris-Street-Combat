"""Audit existing V3 extraction round trip with measured FBX precision; no mesh edits."""
import bpy, json, hashlib
from pathlib import Path
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3/exchange_v1'
OUT=BASE/'roundtrip_precision_v1.json'
assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(BASE/'ContinuousArmsV3.blend'))

def snapshot():
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    rows=[]
    for o in meshes:
        for v in o.data.vertices:
            rows.append({'point':o.matrix_world@v.co,'weights':{o.vertex_groups[g.group].name:g.weight for g in v.groups if g.weight>1e-6}})
    return {'bones':{b.name:{'parent':b.parent.name if b.parent else None,'matrix':rig.matrix_world@b.matrix_local} for b in rig.data.bones},
            'vertices':rows,'meshes':[(len(o.data.vertices),len(o.data.polygons),len(o.data.uv_layers)) for o in meshes]}

before=snapshot()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(BASE/'SK_PC_ContinuousArmsV3.fbx'),automatic_bone_orientation=False,use_anim=False,use_custom_normals=True)
after=snapshot()
tree=KDTree(len(before['vertices']))
for i,v in enumerate(before['vertices']):tree.insert(v['point'],i)
tree.balance()
max_position=max_weight=0
missing=0
for v in after['vertices']:
    possible=tree.find_range(v['point'],.00002)
    if not possible:missing+=1;continue
    def weight_error(i):
        original=before['vertices'][i]['weights']
        return max(abs(original.get(n,0)-v['weights'].get(n,0)) for n in original.keys()|v['weights'].keys())
    p,index,distance=min(possible,key=lambda row:(weight_error(row[1]),row[2]))
    max_position=max(max_position,distance);max_weight=max(max_weight,weight_error(index))
bone_delta=max(abs(x-y) for n in before['bones'] for ra,rb in zip(before['bones'][n]['matrix'],after['bones'][n]['matrix']) for x,y in zip(ra,rb))
hierarchy=set(before['bones'])==set(after['bones']) and all(before['bones'][n]['parent']==after['bones'][n]['parent'] for n in before['bones'])
report={'scope':__doc__,'geometry_counts_match':before['meshes']==after['meshes'],'bone_hierarchy_match':hierarchy,
        'world_bone_matrix_max_delta':bone_delta,'max_position_m':max_position,'max_skin_weight_delta':max_weight,'unmatched_vertices':missing,
        'tolerances':{'position_m':.00002,'world_bone_matrix':.00001,'weight':.00001},
        'native_or_visual_acceptance':False,
        'passed':hierarchy and before['meshes']==after['meshes'] and missing==0 and max_weight<.00001 and bone_delta<.00001}
report['fbx_sha256']=hashlib.sha256((BASE/'SK_PC_ContinuousArmsV3.fbx').read_bytes()).hexdigest()
OUT.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
assert report['passed'],report
print('CS549_ROUNDTRIP_PRECISION',report)
