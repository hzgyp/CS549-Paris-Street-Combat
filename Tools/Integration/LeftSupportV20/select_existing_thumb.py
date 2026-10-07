"""Compare recorded existing thumb poses; no angle fitting or source mutation."""
import hashlib,json,sys,traceback
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerPivotV12'))
from pivot_common import *
SOURCE=STORE/'Evidence/WeaponPinkyLengthV18/distal_v1'
OUT=STORE/'Evidence/LeftSupportV20/thumb_source_compare_v1'
assert not OUT.exists();OUT.mkdir(parents=True)
r={'errors':[],'scope':__doc__,'candidate_authored':False,'source_clips_changed':False,'comparisons':[]}
NAMES=('thumb_01_l','thumb_02_l','thumb_03_l')
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def qrow(m):
    q=Matrix((m[:3,:3]/np.linalg.norm(m[:3,:3],axis=0)).tolist()).to_quaternion()
    return [q.x,q.y,q.z,q.w]
try:
    r['guards_before']=guarded_files();assert not r['guards_before']['mismatches']
    d=load();parents=d['model']['parents']
    source=json.loads((SOURCE/'result.json').read_text())
    bones={n:np.array(v) for n,v in source['candidate_component_bones'].items()}
    gun0=np.array(source['baseline_gun_component_matrix'])
    change=np.array(json.loads((STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/result.json').read_text())['rigid_change_gun_local'])
    gp=transform(d['gp'],change);before=evaluate(d,bones,gun0)
    goal=json.loads((STORE/'Evidence/LeftSupportV20/pivot_goal_v1/result.json').read_text())
    padids=np.array(goal['thumb_pad_triangles'],int)
    thumb=np.array([sum(w.get(n,0) for n in NAMES)>.1 for w in d['weights']])
    tf=d['tri'][np.all(thumb[d['tri']],axis=1)]
    other=np.array([sum(v for n,v in w.items() if n.endswith('_l') and n.startswith(('index_','middle_','ring_','pinky_')))>.1 for w in d['weights']])
    otherfaces=d['tri'][np.all(other[d['tri']],axis=1)]
    stock=np.array(next(c['triangle_ids'] for c in d['topo']['components'] if c['id']==0),int)
    tree=BVHTree.FromPolygons([Vector(v) for v in gp],d['gt'][stock][:,::-1].tolist(),all_triangles=True)
    basefaces={a for a,b in intersection_pairs(before,tf,gp,d['gt'])}
    base_self=len(nonadjacent_pairs(before,tf,otherfaces))
    r['baseline']={'thumb_gun_faces':len(basefaces),'thumb_other_digit_self_pairs':base_self,
                   'thumb_pad_mean_gap_cm':float(np.mean([tree.find_nearest(Vector(v))[3] for v in before[d['tri'][padids]].mean(1)]))}
    clips=json.loads(POSES.read_text())['clips'];candidates={}
    for clip in ('owner_reload','owner_idle'):
        for phase,sample in clips[clip]['samples'].items():
            src={n:mat(v) for n,v in sample['bones_component'].items()}
            current={n:m.copy() for n,m in bones.items()};locals_selected={}
            for n in NAMES:
                old=np.linalg.inv(bones[parents[n]])@bones[n]
                local=np.linalg.inv(src[parents[n]])@src[n]
                old[:3,:3]=local[:3,:3]/np.linalg.norm(local[:3,:3],axis=0)*np.linalg.norm(old[:3,:3],axis=0)
                current[n]=current[parents[n]]@old
                locals_selected[n]=qrow(old)
            after=evaluate(d,current,gun0)
            newfaces={a for a,b in intersection_pairs(after,tf,gp,d['gt'])}
            selfpairs=len(nonadjacent_pairs(after,tf,otherfaces))
            pad=after[d['tri'][padids]].mean(1)
            gap=float(np.mean([tree.find_nearest(Vector(v))[3] for v in pad]))
            row={'clip':clips[clip]['asset'],'phase_s':float(phase),
                 'thumb_pad_mean_gap_cm':gap,'thumb_gun_faces':len(newfaces),
                 'new_thumb_crossing_faces':len(newfaces-basefaces),'thumb_other_digit_self_pairs':selfpairs,
                 'unaffected_skin_delta_cm':float(np.max(np.linalg.norm(after[~thumb]-before[~thumb],axis=1))),
                 'right_skin_delta_cm':float(np.max(np.linalg.norm(after[d['masks']['r']]-before[d['masks']['r']],axis=1))),
                 **edge_check(d,before,after),'existing_local_rotations':locals_selected}
            row['contact_gate_passed']=bool(not row['new_thumb_crossing_faces'] and selfpairs<=base_self and row['unaffected_skin_delta_cm']<.0001 and row['right_skin_delta_cm']<.0001 and not row['new_severe_edges'] and gap<r['baseline']['thumb_pad_mean_gap_cm']-.1)
            key=f'{clip}_{phase}';row['identity']=key;r['comparisons'].append(row);candidates[key]=current;write()
    viable=[x for x in r['comparisons'] if x['contact_gate_passed']]
    if viable:
        chosen=min(viable,key=lambda x:x['thumb_pad_mean_gap_cm'])
        r['chosen_existing_pose']=chosen
        r['candidate_component_bones']={n:v.tolist() for n,v in candidates[chosen['identity']].items()}
        r['status']='existing_thumb_pose_found_requires_visual_fresh_native_review'
    else:r['status']='no_recorded_existing_thumb_pose_passes'
    r['pose_cache_sha256']=hashlib.sha256(POSES.read_bytes()).hexdigest()
except Exception:r['errors'].append(traceback.format_exc());r['status']='stopped'
finally:
    r['guards_after']=guarded_files();write()
    print(json.dumps({k:r.get(k) for k in ['status','errors','baseline','chosen_existing_pose','guards_after']}),flush=True)
    if r['errors'] or r['guards_after']['mismatches']:raise SystemExit(1)
