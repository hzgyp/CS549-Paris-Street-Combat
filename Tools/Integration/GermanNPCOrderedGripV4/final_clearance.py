"""One measured <=0.5cm whole-left-arm clearance correction; no digits or gun edits."""
import sys,json,traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import *
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs
sys.path.insert(0,str(Path(__file__).parent))
from arm_fit import arm_targets,encode
BASE=STORE/'Evidence/GermanNPCOrderedGripV4'
PREV=BASE/'offline_v6/result.json';DATA=PREV.parent/'geometry.npz'
OUT=BASE/'final_clearance_v7';assert not OUT.exists();OUT.mkdir(parents=True)
old=read(PREV);r=dict(old);r['errors']=[];r['inputs']=old['inputs']+[row(p) for p in (PREV,DATA,Path(__file__),Path(__file__).with_name('arm_fit.py'))]
r['guards_before']=guards();write(OUT/'result.json',r)
try:
    assert not old['errors'] and old['new_severe_edges']==0
    d=np.load(DATA);parents=old['parents'];names=old['bone_names'];weights=d['weights'];rest=d['rest_native_cm'];ref=d['reference_matrices'];tri=d['skin_triangles']
    before={n:mat(t) for n,t in old['after_bones'].items()}
    support=np.array(tm.point(old['after_gun_world'],old['support_gun_cm']))
    away=np.array(old['left_palm_target_world_cm'])-support;away/=np.linalg.norm(away)
    delta=away*.499999
    target=before['hand_l'].copy();target[:3,3]+=delta
    after,checks=arm_targets(before,{'l':target},parents)
    skin=np.zeros_like(rest)
    for j,n in enumerate(names):skin+=weights[:,j,None]*transform(rest,after[n]@np.linalg.inv(ref[j]))
    skin/=weights.sum(1)[:,None]
    protected=[n for n in names if not n.endswith('_l') or not n.startswith(('upperarm_','lowerarm_','hand_','thumb_','index_','middle_','ring_','pinky_'))]
    assert max(np.max(abs(after[n]-before[n])) for n in protected)<1e-8
    digiterr=max(np.max(abs(np.linalg.inv(after[parents[n]])@after[n]-np.linalg.inv(before[parents[n]])@before[n]))
        for n in names if n.startswith(('thumb_','index_','middle_','ring_','pinky_')))
    assert digiterr<1e-8
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    # Compare complete final source deformation with original V3, not only the
    # tiny clearance delta, preserving the original severe-edge definition.
    b=d['before_skin'];lb=np.linalg.norm(b[edges[:,0]]-b[edges[:,1]],axis=1);la=np.linalg.norm(skin[edges[:,0]]-skin[edges[:,1]],axis=1)
    severe=int(np.sum((la>lb*3)&(la-lb>2)));assert severe==0
    g=d['gun_local_cm'];gt=d['gun_triangles'];worldgun=transform(g,mat(old['after_gun_world']))
    counts={}
    for digit in ('thumb','index','middle','ring','pinky'):
        ids=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_l')]
        mask=weights[:,ids].sum(1)>0;faces=np.flatnonzero(np.any(mask[tri],axis=1))
        pairs=intersection_pairs(skin,tri[faces],worldgun,gt);counts[digit]=len({a for a,b in pairs})
    beforecounts={d:old['after_crossing_faces'][d+'_l']['whole'] for d in counts}
    assert sum(counts.values())<sum(beforecounts.values()),(beforecounts,counts)
    r.update(status='ordered_clearance_candidate_requires_native_review',
        after_bones={n:encode(v) for n,v in after.items()},
        left_clearance_delta_world_cm=delta.tolist(),left_clearance_delta_cm=float(np.linalg.norm(delta)),
        left_palm_target_world_cm=(np.array(old['left_palm_target_world_cm'])+delta).tolist(),
        left_target_standoff_cm=.799999,
        left_crossing_counts_before_correction=beforecounts,left_crossing_counts_after_correction=counts,
        digit_local_matrix_error=digiterr,new_severe_edges=severe,max_extra_skin_edge_cm=float(np.max(la-lb)),
        clearance_original_length_checks=checks,guards_after=guards(),
        preserved_gun_and_right=True,contact_accepted=False)
    np.savez_compressed(OUT/'geometry.npz',skin=skin,before_skin=b,skin_triangles=tri,gun_local_cm=g,gun_triangles=gt,
        rest_native_cm=rest,weights=weights,reference_matrices=ref)
    write(OUT/'result.json',r)
    print(json.dumps({k:r[k] for k in ('status','left_clearance_delta_cm','left_crossing_counts_before_correction','left_crossing_counts_after_correction','new_severe_edges')}))
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserved';write(OUT/'result.json',r);print(r['errors'][-1])
