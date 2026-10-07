"""Existing V16 closeup objects only; full-arm context retained separately."""
import hashlib
import json
import traceback
from pathlib import Path
import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
STORE = ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = STORE/'Evidence/WeaponTexturedViewsV17'
V1 = BASE/'presentation_v1'
OUT = BASE/'presentation_v2'
FROZEN = STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/FixedMarkedGripMuzzleRaise.blend'
ARM = STORE/'Evidence/ContinuousArmsV3/exchange_v1/SK_PC_ContinuousArmsV3.fbx'
assert not OUT.exists()
OUT.mkdir(parents=True)
r = {'errors':[], 'scope':__doc__, 'native_authored':False, 'pose_changed':False}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def guards():
    rows = json.loads((STORE/'Evidence/ReloadIndexContactV6/map_recovery_v1/result.json').read_text())['files']
    return {'checked':len(rows),'mismatches':[x['path'] for x in rows
            if not (ROOT/x['path']).is_file() or (ROOT/x['path']).stat().st_size!=x['size_bytes']
            or sha(ROOT/x['path'])!=x['sha256']]}

def attributes():
    rows = []
    for obj in sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name):
        mesh = obj.data
        rows.append({'name':obj.name,'vertices':len(mesh.vertices),'triangles':len(mesh.polygons),
                     'positions':sha_array([list(v.co) for v in mesh.vertices],np.float64),
                     'triangles_sha':sha_array([list(p.vertices) for p in mesh.polygons],np.int64),
                     'materials':[m.name for m in mesh.materials],
                     'slots':sha_array([p.material_index for p in mesh.polygons],np.int64),
                     'uvs':{u.name:sha_array([list(x.uv) for x in u.data],np.float64) for u in mesh.uv_layers},
                     'render_uv':next(u.name for u in mesh.uv_layers if u.active_render)})
    return rows

def sha_array(a,dtype):
    return hashlib.sha256(np.array(a,dtype=dtype).tobytes()).hexdigest()

try:
    before = guards()
    assert not before['mismatches']
    previous = json.loads((V1/'result.json').read_text())
    assert not previous['errors']
    hashes = previous['input_hashes'].copy()
    for p in [V1/'TexturedV16Inspection.blend',V1/'result.json',Path(__file__)]:
        hashes[str(p.relative_to(ROOT))] = sha(p)
    assert all(sha(ROOT/k)==v for k,v in hashes.items())
    bpy.ops.wm.open_mainfile(filepath=str(FROZEN),load_ui=False,use_scripts=False)
    frozen = []
    for name in ['Fixed right raised_v16','Support raised_v16']:
        obj = bpy.data.objects[name]
        frozen.append((name,np.array([list(obj.matrix_world@v.co) for v in obj.data.vertices]),
                       np.array([list(p.vertices) for p in obj.data.polygons],int)))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ARM),automatic_bone_orientation=False,use_anim=False)
    mesh = next(o.data for o in bpy.data.objects if o.type=='MESH')
    mesh.calc_loop_triangles()
    triangles = list(mesh.loop_triangles)
    lookup = {tuple(t.vertices):i for i,t in enumerate(triangles)}
    assert len(lookup)==len(triangles)
    uvs = {u.name:np.array([[list(u.data[i].uv) for i in t.loops] for t in triangles]) for u in mesh.uv_layers}
    render_uv = next(u.name for u in mesh.uv_layers if u.active_render)
    active_uv = mesh.uv_layers.active.name
    slots = [t.material_index for t in triangles]
    smooth = [mesh.polygons[t.polygon_index].use_smooth for t in triangles]
    bpy.ops.wm.open_mainfile(filepath=str(V1/'TexturedV16Inspection.blend'),load_ui=False,use_scripts=False)
    full = bpy.data.objects['Frozen V16 continuous arms']
    full_points = np.array([list(v.co) for v in full.data.vertices])
    partials = []
    for name,points,faces in frozen:
        assert np.array_equal(points,full_points), 'Closeup is not the frozen full-arm pose'
        indices = np.array([lookup[tuple(face[::-1])] for face in faces],int)
        new = bpy.data.meshes.new(name+' original-textured')
        new.from_pydata(points.tolist(),[],faces.tolist())
        new.update()
        obj = bpy.data.objects.new(new.name,new)
        bpy.context.scene.collection.objects.link(obj)
        for mat in full.data.materials:
            new.materials.append(mat)
        for p,i in zip(new.polygons,indices):
            p.material_index = {2:0,8:1}[slots[int(i)]]
            p.use_smooth = smooth[int(i)]
        for name,values in uvs.items():
            uv = new.uv_layers.new(name=name)
            for item,value in zip(uv.data,values[indices][:,::-1].reshape(-1,2)):
                item.uv = value
            uv.active_render = name==render_uv
        new.uv_layers.active_index = new.uv_layers.find(active_uv)
        assert np.array_equal(points,np.array([list(v.co) for v in new.vertices]))
        partials.append(obj)
    scene = bpy.context.scene
    full.hide_render = True
    renders = []
    for row in previous['renders']:
        if row['view']=='whole_arms_context':
            full.hide_render = False
            for obj in partials:
                obj.hide_render = True
        scene.camera = bpy.data.objects[row['view']]
        scene.render.filepath = str(OUT/row['path'])
        bpy.ops.render.render(write_still=True)
        renders.append(dict(row,sha256=sha(OUT/row['path'])))
    full.hide_render = True
    for obj in partials:
        obj.hide_render = False
    scene.camera = bpy.data.objects['side_stock_end']
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'TexturedV16Inspection.blend'))
    r.update(status='existing_closeup_three_views_rendered',renders=renders,mesh_attributes=attributes(),
             images=previous['images'],geometry_max_delta_cm=0.,input_hashes=hashes,
             inputs_unchanged=all(sha(ROOT/k)==v for k,v in hashes.items()),
             blend_sha256=sha(OUT/'TexturedV16Inspection.blend'),
             full_arms_retained=True,full_arms_hidden_only_for_existing_closeup_display=True,
             native_ue_shader_parity=False)
    assert r['inputs_unchanged']
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status'] = 'stopped'
finally:
    r['guards_after'] = guards()
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:r.get(k) for k in ['status','errors','inputs_unchanged','geometry_max_delta_cm','guards_after']}),flush=True)
    if r['errors'] or r['guards_after']['mismatches']:
        raise SystemExit(1)
