"""Exact existing left-thumb rotation reuse with true zero-influence audit."""
import hashlib,json,sys,traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerPivotV12'))
from pivot_common import *
SOURCE=STORE/'Evidence/WeaponPinkyLengthV18/distal_v1'
BASE=STORE/'Evidence/LeftSupportV20';OUT=BASE/'reuse_pose_v2'
assert not OUT.exists();OUT.mkdir()
NAMES=('thumb_01_l','thumb_02_l','thumb_03_l')
r={'errors':[],'scope':__doc__,'native_authored':False,'selected_formal':False,'renders':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
try:
    r['guards_before']=guarded_files();assert not r['guards_before']['mismatches']
    compare=json.loads((BASE/'thumb_source_compare_v1/result.json').read_text())
    options=[x for x in compare['comparisons'] if not x['new_thumb_crossing_faces'] and not x['thumb_other_digit_self_pairs'] and not x['new_severe_edges'] and x['thumb_pad_mean_gap_cm']<compare['baseline']['thumb_pad_mean_gap_cm']-.1]
    chosen=min(options,key=lambda x:x['thumb_pad_mean_gap_cm'])
    d=load();parents=d['model']['parents']
    proof=json.loads((SOURCE/'result.json').read_text());b={n:np.array(v) for n,v in proof['candidate_component_bones'].items()}
    gun0=np.array(proof['baseline_gun_component_matrix']);before=evaluate(d,b,gun0)
    c={n:m.copy() for n,m in b.items()}
    for n in NAMES:
        local=np.linalg.inv(b[parents[n]])@b[n]
        x,y,z,w=chosen['existing_local_rotations'][n]
        local[:3,:3]=np.array(Quaternion((w,x,y,z)).to_matrix())*np.linalg.norm(local[:3,:3],axis=0)
        c[n]=c[parents[n]]@local
    after=evaluate(d,c,gun0)
    total=np.array([sum(w.get(n,0) for n in NAMES) for w in d['weights']])
    truly_affected=total>0
    otherdigit=np.array([sum(v for n,v in w.items() if n.endswith('_l') and n.startswith(('index_','middle_','ring_','pinky_')))>.1 for w in d['weights']])
    mixed=np.flatnonzero(truly_affected & otherdigit)
    error=np.linalg.norm(after-before,axis=1)
    r['checks']={'true_unaffected_max_delta_cm':float(error[~truly_affected].max()),
        'right_skin_delta_cm':float(error[d['masks']['r']].max()),
        'other_bone_matrix_delta':max(float(np.max(abs(c[n]-b[n]))) for n in b if n not in NAMES),
        'wrist_matrix_delta':float(np.max(abs(c['hand_l']-b['hand_l']))),
        'shared_other_digit_vertices':mixed.tolist(),
        'shared_other_digit_max_skin_delta_cm':float(error[mixed].max()) if len(mixed) else 0,
        'false_unaffected_vertices_v1':int(((total>0)&(total<=.1)).sum()),
        'local_translation_scale_delta':max(float(np.max(abs((np.linalg.inv(c[parents[n]])@c[n])[:3,3]-(np.linalg.inv(b[parents[n]])@b[n])[:3,3]))) for n in NAMES),
        **edge_check(d,before,after)}
    ck=r['checks'];assert ck['true_unaffected_max_delta_cm']<.0001 and ck['right_skin_delta_cm']<.0001 and ck['other_bone_matrix_delta']==0 and ck['wrist_matrix_delta']==0 and not ck['new_severe_edges']
    # Adjacent skin sharing is reported, not silently treated as another joint
    # edit. A>1mm neighboring-digit change would exceed this bounded reuse.
    assert ck['shared_other_digit_max_skin_delta_cm']<.1
    blend=SOURCE/'RightPinkyDistalShorter.blend';assert sha(blend)==proof['blend_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(blend),load_ui=False,use_scripts=False)
    objects=[bpy.data.objects[n] for n in ['Frozen V16 continuous arms','Fixed right raised_v16 original-textured','Support raised_v16 original-textured']]
    # Existing frozen inspection geometry displays evaluation; full original
    # editable rig is retained below and reposed only with these three locals.
    rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    original_rig_locals={pb.name:pb.matrix_basis.copy() for pb in rig.pose.bones}
    native_ref=d['invref'];order=sorted(rig.pose.bones,key=lambda pb:len(pb.parent_recursive))
    # Scene's exact source rig/world mapping established from accepted static
    # reference bones, not guessed orientation or independent mesh translation.
    source_mesh=next(o for o in bpy.context.scene.objects if o.type=='MESH' and any(m.type=='ARMATURE' for m in o.modifiers))
    rig.hide_set(False);source_mesh.hide_set(False);bpy.context.view_layer.update()
    for pb in order:
        if pb.name not in NAMES:continue
        # Rotation delta in existing parent local frame carries the accepted
        # original Blender bone basis through native component conjugation.
        pass
    center=Vector(json.loads((BASE/'audit_v1/result.json').read_text())['diagnostic_center_m'])
    scene=bpy.context.scene;scene.render.resolution_x=1000;scene.render.resolution_y=800
    cam_specs=[('side',(.5,0,.05)),('reverse',(-.5,0,.05)),('under',(0,0,-.5)),('top',(0,0,.5))]
    for condition,points in [('before',before),('existing_thumb',after)]:
        for obj in objects:
            for vertex,pos in zip(obj.data.vertices,points*.01):vertex.co=pos
            obj.data.update()
        objects[0].hide_render=True;objects[1].hide_render=objects[2].hide_render=False
        for name,offset in cam_specs:
            cd=bpy.data.cameras.new(condition+'_'+name);cd.type='ORTHO';cd.ortho_scale=.28;cd.clip_start=.001
            cam=bpy.data.objects.new(condition+'_'+name,cd);scene.collection.objects.link(cam)
            cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
            scene.camera=cam;file=condition+'_'+name+'.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['renders'].append(file)
        objects[0].hide_render=False;objects[1].hide_render=objects[2].hide_render=True
        scene.camera=bpy.data.objects['whole_arms_context'];file=condition+'_whole_arms.png';scene.render.filepath=str(OUT/file);bpy.ops.render.render(write_still=True);r['renders'].append(file)
    # Inspection-only: editable source rig still holds original pose. Do not
    # mislabel these frozen images as a newly authored playable rig/export.
    r.update(chosen_existing_pose=chosen,baseline=compare['baseline'],candidate_component_bones={n:m.tolist() for n,m in c.items()},
             source_blend_sha256=sha(blend),true_influence_audit_passed=True,
             source_rig_reposed=False,remaining_mean_pad_gap_cm=chosen['thumb_pad_mean_gap_cm'])
    cfg=json.loads((STORE/'Evidence/GripBindingV18/config_v1/binding.json').read_text())
    for n in NAMES:cfg['fingers_local'][n]['q']=chosen['existing_local_rotations'][n]
    (OUT/'binding.json').write_text(json.dumps(cfg,indent=2)+'\n')
    r['config_sha256']=sha(OUT/'binding.json')
    r['status']='bounded_existing_thumb_config_requires_visual_native_review'
except Exception:r['errors'].append(traceback.format_exc());r['status']='stopped'
finally:
    r['guards_after']=guarded_files();write()
    print(json.dumps({k:r.get(k) for k in ['status','errors','checks','chosen_existing_pose','guards_after']}),flush=True)
    if r['errors'] or r['guards_after']['mismatches']:raise SystemExit(1)
