"""Fresh inspectable copy: skin/UV/material/rest-rig/weight verification."""
import json
import hashlib
import traceback
from pathlib import Path
import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE=STORE/'Evidence/WeaponPinkyLengthV18'
SOURCE=BASE/'distal_v1'
OUT=BASE/'fresh_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
r={'errors':[],'native_selected':False,'actual_gameplay_tested':False}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def weights(obj):
    return [{obj.vertex_groups[g.group].name:float(g.weight) for g in v.groups} for v in obj.data.vertices]

def rest(rig):
    return {b.name:{'parent':b.parent.name if b.parent else None,'matrix':np.array(b.matrix_local).tolist()}
            for b in rig.data.bones}

try:
    proof=json.loads((SOURCE/'result.json').read_text())
    assert not proof['errors']
    blend=SOURCE/'RightPinkyDistalShorter.blend'
    assert sha(blend)==proof['blend_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False,use_scripts=False)
    for name,row in proof['geometry_after'].items():
        mesh=bpy.data.objects[name].data
        assert np.array_equal(np.array([list(v.co) for v in mesh.vertices]),row['positions_m'])
        assert [list(p.vertices) for p in mesh.polygons]==row['triangles']
        assert [m.name for m in mesh.materials]==row['materials']
        assert hashlib.sha256(np.array([p.material_index for p in mesh.polygons],dtype=np.int64).tobytes()).hexdigest()==row['slot_sha256']
        assert {u.name:hashlib.sha256(np.array([list(x.uv) for x in u.data],dtype=np.float64).tobytes()).hexdigest() for u in mesh.uv_layers}==row['uv_sha256']
    for row in proof['original_textures']:
        image=bpy.data.images[row['name']]
        path=Path(bpy.path.abspath(image.filepath)).resolve()
        assert str(path.relative_to(ROOT))==row['path'] and sha(path)==row['sha256']
        assert list(image.size)==row['size'] and image.colorspace_settings.name==row['color_space']
    for name in ['Frozen V16 M1','Frozen V16 continuous arms','Fixed right raised_v16 original-textured','Support raised_v16 original-textured']:
        a,b=proof['geometry_before'][name],proof['geometry_after'][name]
        assert a['uv_sha256']==b['uv_sha256'] and a['materials']==b['materials'] and a['slot_sha256']==b['slot_sha256']
        if name=='Frozen V16 M1':
            assert a==b,'Gun changed'
    rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    source=next(o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers))
    saved_weights,saved_rest=weights(source),rest(rig)
    saved_source_positions=np.array([list(v.co) for v in source.data.vertices])
    for obj in bpy.context.scene.objects:
        obj.hide_set(False)
    bpy.context.view_layer.update()
    evaluated=source.evaluated_get(bpy.context.evaluated_depsgraph_get())
    md=evaluated.to_mesh()
    actual=np.array([list(evaluated.matrix_world@v.co) for v in md.vertices])*100
    evaluated.to_mesh_clear()
    expected=np.array(proof['geometry_after']['Frozen V16 continuous arms']['positions_m'])*100
    error=float(np.max(np.linalg.norm(actual-expected,axis=1)))
    assert error<.002,'Saved source rig does not reproduce inspected geometry'
    r['fresh_editable_rig_skin_error_cm']=error
    r['pinky_02_local_scale']=list(rig.pose.bones['pinky_02_r'].scale)
    assert max(abs(v-.9) for v in r['pinky_02_local_scale'])<1e-5
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fbx=STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
    bpy.ops.import_scene.fbx(filepath=str(fbx),automatic_bone_orientation=False,use_anim=False)
    original_rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    original_source=next(o for o in bpy.data.objects if o.type=='MESH')
    assert weights(original_source)==saved_weights,'Source weights changed'
    assert rest(original_rig)==saved_rest,'Rest rig changed'
    assert np.array_equal(np.array([list(v.co) for v in original_source.data.vertices]),saved_source_positions)
    assert all(sha(ROOT/k)==v for k,v in proof['input_hashes'].items())
    guard=json.loads((STORE/'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json').read_text())['files']
    assert all((ROOT/x['path']).stat().st_size==x['size_bytes'] and sha(ROOT/x['path'])==x['sha256'] for x in guard)
    assert sha(blend)==proof['blend_sha256']
    r.update(status='fresh_source_rig_and_inspection_verified',checked_images=9,
             original_mesh_rest_rig_weights_exact=True,guards_checked=len(guard),
             inputs_and_blend_unchanged=True,blend_sha256=sha(blend))
except Exception:
    r['status']='stopped'
    r['errors'].append(traceback.format_exc())
finally:
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r),flush=True)
    if r['errors']:
        raise SystemExit(1)
