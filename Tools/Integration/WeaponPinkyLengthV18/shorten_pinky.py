"""ONE existing-pose right-pinky root scale, preserving all source assets."""
import sys
import hashlib
import traceback
from pathlib import Path
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12'))
from pivot_common import *

BASE = STORE/'Evidence/WeaponPinkyLengthV18'
OUT = BASE/'shorten_v1'
CURRENT = STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/result.json'
PRESENT = STORE/'Evidence/WeaponTexturedViewsV17/presentation_v2'
assert not OUT.exists()
OUT.mkdir(parents=True)
SCALE = .90
NAMES = ['pinky_01_r','pinky_02_r','pinky_03_r']
inputs = [FBX,POSES,AUDIT,INDEX,CURRENT,PRESENT/'result.json',PRESENT/'TexturedV16Inspection.blend',
          BASE/'probe_v1/result.json',Path(__file__),
          Path(__file__).resolve().parents[1]/'WeaponTriggerAlignmentV2/blender_contact_common.py',
          Path(__file__).resolve().parents[1]/'WeaponWholeWristV11/wrist_common.py',
          Path(__file__).resolve().parents[1]/'WeaponTriggerPivotV12/pivot_common.py']
hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
r = {'errors':[],'scope':__doc__,'scale_factor':SCALE,'native_authored':False,'source_actions_modified':False}

def write():
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')

def shortened(bones):
    result = {n:m.copy() for n,m in bones.items()}
    root = bones[NAMES[0]][:3,3]
    for n in NAMES:
        result[n][:3,:3] *= SCALE
        result[n][:3,3] = root+SCALE*(bones[n][:3,3]-root)
    return result

def attributes():
    return {o.name:{'positions_m': [list(v.co) for v in o.data.vertices],
                    'triangles':[list(p.vertices) for p in o.data.polygons],
                    'uv_sha256':{u.name:hashlib.sha256(np.array([list(x.uv) for x in u.data],dtype=np.float64).tobytes()).hexdigest() for u in o.data.uv_layers},
                    'materials':[m.name for m in o.data.materials],
                    'slot_sha256':hashlib.sha256(np.array([p.material_index for p in o.data.polygons],dtype=np.int64).tobytes()).hexdigest()}
            for o in bpy.context.scene.objects if o.type=='MESH'}

try:
    r['guards_before'] = guarded_files()
    assert not r['guards_before']['mismatches']
    d = load()
    probe = json.loads((BASE/'probe_v1/result.json').read_text())
    assert probe['current_pinky_unmodified_from_D059'] and not probe['errors']
    current = json.loads(CURRENT.read_text())
    b0 = {n:np.array(v) for n,v in current['candidate_component_bones'].items()}
    gun0 = np.array(current['baseline_gun_component_matrix'])
    changed = shortened(b0)
    before,after = evaluate(d,b0,gun0),evaluate(d,changed,gun0)
    affected = np.array([sum(w.get(n,0) for n in NAMES)>1e-8 for w in d['weights']])
    boundary = affected & d['digits']['ring']
    parents = d['model']['parents']
    accepted = json.loads(INDEX.read_text())
    phases = []
    for phase in d['poses']:
        b = b0 if phase=='0.0' else baseline(d,float(phase),accepted)
        c = shortened(b)
        old,new = evaluate(d,b,gun0),evaluate(d,c,gun0)
        row = {'phase_s':float(phase),
               'root_delta_cm':float(np.linalg.norm(c[NAMES[0]][:3,3]-b[NAMES[0]][:3,3])),
               'index_skin_delta_cm':float(np.max(np.linalg.norm(new[d['digits']['index']]-old[d['digits']['index']],axis=1))),
               'unaffected_skin_delta_cm':float(np.max(np.linalg.norm(new[~affected]-old[~affected],axis=1))),
               'ring_boundary_delta_cm':float(np.max(np.linalg.norm(new[boundary]-old[boundary],axis=1))),
               'child_local_matrix_delta':max(float(np.max(abs(np.linalg.inv(c[parents[n]])@c[n]-np.linalg.inv(b[parents[n]])@b[n]))) for n in NAMES[1:]),
               'other_bone_delta':max(float(np.max(abs(c[n]-b[n]))) for n in b if n not in NAMES),
               'joint_distance_ratios':[float(np.linalg.norm(c[v][:3,3]-c[u][:3,3])/np.linalg.norm(b[v][:3,3]-b[u][:3,3])) for u,v in zip(NAMES[:-1],NAMES[1:])],
               **edge_check(d,old,new)}
        assert row['root_delta_cm']<1e-10 and row['index_skin_delta_cm']<.0001
        assert row['unaffected_skin_delta_cm']<.0001 and row['ring_boundary_delta_cm']<.1
        assert row['child_local_matrix_delta']<1e-10 and row['other_bone_delta']==0
        assert max(abs(v-SCALE) for v in row['joint_distance_ratios'])<1e-10
        assert not row['new_severe_edges']
        phases.append(row)
    ta = d['tri'][np.all(d['digits']['pinky'][d['tri']],axis=1)]
    tb = d['tri'][np.all(d['digits']['ring'][d['tri']],axis=1)]
    self_before,self_after = len(nonadjacent_pairs(before,ta,tb)),len(nonadjacent_pairs(after,ta,tb))
    assert self_after<=self_before,'New ring/pinky self-crossing'
    pad_id = int(json.loads((STORE/'Evidence/WeaponTriggerPivotV12/landmarks_v1/result.json').read_text())['actual_index_pad_triangle'])
    gp = transform(d['gp'],np.array(current['rigid_change_gun_local']))
    r.update(phases=phases,current_pinky_source_audit=probe['current_pinky_vs_source_local_matrix_delta'],
             affected_vertices=int(affected.sum()),ring_boundary_vertices=np.flatnonzero(boundary).tolist(),
             ring_pinky_self_crossings={'before':self_before,'after':self_after},
             contact_before=contact(d,before,gp,pad_id),contact_after=contact(d,after,gp,pad_id),
             candidate_component_bones={n:v.tolist() for n,v in changed.items()},
             baseline_gun_component_matrix=gun0.tolist())
    # An editable original source armature carries the same copied pose and the
    # root scale. Source mesh/weights/rest bones stay intact; no action is baked.
    rig,source = d['rig'],d['source']
    source_points = np.array([list(source.matrix_world@v.co) for v in source.data.vertices])
    fit = np.linalg.lstsq(np.column_stack([source_points,np.ones(len(source_points))]),d['p'],rcond=None)[0]
    F = np.eye(4)
    F[:3,:] = fit.T
    original_world = np.array(rig.matrix_world)
    order = sorted(rig.pose.bones,key=lambda p:len(p.parent_recursive))
    for pb in order:
        if pb.name in changed:
            deform = changed[pb.name]@d['invref'][pb.name]
            world_deform = np.linalg.inv(F)@deform@F
            target = np.linalg.inv(original_world)@world_deform@original_world@np.array(pb.bone.matrix_local)
            pb.matrix = Matrix(target.tolist())
            bpy.context.view_layer.update()
    bpy.context.view_layer.update()
    evaluated = source.evaluated_get(bpy.context.evaluated_depsgraph_get())
    md = evaluated.to_mesh()
    actual_native = transform(np.array([list(evaluated.matrix_world@v.co) for v in md.vertices]),F)
    evaluated.to_mesh_clear()
    actual = transform(actual_native,np.linalg.inv(gun0))
    rig_error = float(np.max(np.linalg.norm(actual-after,axis=1)))
    r['editable_rig_skin_max_error_cm'] = rig_error
    assert rig_error<.002,'Actual copied rig does not reproduce the scaled skin'
    original_objects = [source,rig]
    # Align the complete source collection into the fixed diagnostic frame.
    display = bpy.data.objects.new('Editable source rig - offline length adapter',None)
    bpy.context.scene.collection.objects.link(display)
    display.matrix_world = Matrix((np.diag([.01,.01,.01,1])@np.linalg.inv(gun0)@F).tolist())
    for obj in original_objects:
        if obj.parent not in original_objects:
            saved = obj.matrix_world.copy()
            obj.parent = display
            obj.matrix_parent_inverse = Matrix.Identity(4)
            obj.matrix_basis = saved
        obj.hide_render = True
    dependency = OUT/'editable_rig_dependency.blend'
    bpy.data.libraries.write(str(dependency),{display,source,rig},fake_user=False,compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(PRESENT/'TexturedV16Inspection.blend'),load_ui=False,use_scripts=False)
    names = ['Frozen V16 continuous arms','Fixed right raised_v16 original-textured','Support raised_v16 original-textured']
    existing = {n:np.array([list(v.co) for v in bpy.data.objects[n].data.vertices])*100 for n in names}
    assert max(float(np.max(np.linalg.norm(v-before,axis=1))) for v in existing.values())<.0001
    r['geometry_before'] = attributes()
    scene = bpy.context.scene
    renders = []
    for condition,points in [('before',before),('shorter',after)]:
        for n in names:
            mesh = bpy.data.objects[n].data
            for vertex,pos in zip(mesh.vertices,points*.01):
                vertex.co = pos
            mesh.update()
        for view in ['front_trigger_side','side_stock_end','top','whole_arms_context']:
            context = view=='whole_arms_context'
            bpy.data.objects[names[0]].hide_render = not context
            for n in names[1:]:
                bpy.data.objects[n].hide_render = context
            scene.camera = bpy.data.objects[view]
            scene.render.filepath = str(OUT/(condition+'_'+view+'.png'))
            bpy.ops.render.render(write_still=True)
            renders.append({'condition':condition,'view':view,'file':condition+'_'+view+'.png'})
    bpy.data.objects[names[0]].hide_render = True
    for n in names[1:]:
        bpy.data.objects[n].hide_render = False
    with bpy.data.libraries.load(str(dependency),link=False) as (src,dst):
        dst.objects = src.objects
    for obj in dst.objects:
        if obj:
            scene.collection.objects.link(obj)
            obj.hide_render = True
            obj.hide_set(True)
    r['geometry_after'] = attributes()
    r['renders'] = renders
    r['original_textures'] = json.loads((PRESENT/'result.json').read_text())['images']
    bpy.context.preferences.filepaths.save_version = 0
    scene.camera = bpy.data.objects['front_trigger_side']
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'RightPinkyShorter10Percent.blend'))
    r['blend_sha256'] = hashlib.sha256((OUT/'RightPinkyShorter10Percent.blend').read_bytes()).hexdigest()
    r['status'] = 'bounded_length_copy_ready_for_visual_review_not_native_selection'
except Exception:
    r['status']='stopped'
    r['errors'].append(traceback.format_exc())
finally:
    r['input_hashes']=hashes
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
    r['guards_after']=guarded_files()
    write()
    print(json.dumps({k:r.get(k) for k in ['status','errors','editable_rig_skin_max_error_cm','affected_vertices','ring_pinky_self_crossings','inputs_unchanged','guards_after']}),flush=True)
    if r['errors'] or not r['inputs_unchanged'] or r['guards_after']['mismatches']:
        raise SystemExit(1)
