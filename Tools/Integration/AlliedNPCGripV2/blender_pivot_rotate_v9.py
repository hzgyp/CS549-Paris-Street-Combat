"""One extra2-degree upward rotation from V7b; never consume V8 translation."""
import ast
import sys
import math
import traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
import transform_math as tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs

PREVIOUS=BASE/'pivot_raise_native_v7b/result.json'
MEASURE=BASE/'pivot_raise_measure_v7/result.json'
GEOMETRY=MEASURE.parent/'geometry.npz'
V7=BASE/'pivot_raise_trial_v7/result.json'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
HELPER=Path(__file__).with_name('blender_pivot_raise_v7.py')
OUT=BASE/'pivot_rotate_trial_v9'
assert not OUT.exists();OUT.mkdir(parents=True)
inputs=(PREVIOUS,MEASURE,GEOMETRY,V7,TOPO,HELPER,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
   'source_model_weights_actions_modified':False,'native_authored':False,
   'formal_selected':False,'contact_or_gameplay_accepted':False,'v8_translation_consumed':False}
# Extract reviewed PURE helpers only, never execute the old angular author.
tree=ast.parse(HELPER.read_text(encoding='utf-8'))
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('swing','encode','left_chain')]
assert len(functions)==3
exec(compile(ast.Module(body=functions,type_ignores=[]),str(HELPER)+':pure_helpers','exec'),globals())

try:
    previous,m,old=read(PREVIOUS),read(MEASURE),read(V7)
    assert previous['status']=='pivot_raise_v7_native_views_require_user_review' and not previous['errors']
    for record in (previous,m,old):
        assert record['inputs_unchanged'] and not record['errors'] and record['guards_after']==611
        assert all(sha(ROOT/p)==h for p,h in record['input_hashes'].items())
    d=np.load(GEOMETRY);names=m['bone_names'];parents=m['parents']
    original=previous['after']['bones'];bones={n:mat(t) for n,t in original.items()}
    gb=mat(previous['after']['gun_world'])
    pivot=transform(np.array([m['pivot_gun_cm']]),gb)[0]
    axis=np.array(old['axis_world'],float);assert np.linalg.norm(axis)>1e-6;axis/=np.linalg.norm(axis)
    half=math.radians(2)/2
    rotation=np.array(Quaternion((math.cos(half),*(axis*math.sin(half)))).to_matrix(),float)
    change=np.eye(4);change[:3,:3]=rotation;change[:3,3]=pivot-rotation@pivot
    ga=change@gb
    muzzle=d['gun_local_cm'][np.argmax(d['gun_local_cm'][:,1])]
    muzzle_raise=float(transform(muzzle[None,:],ga)[0,2]-transform(muzzle[None,:],gb)[0,2])
    assert muzzle_raise>0,'Requested axis must actually raise muzzle'
    candidate,reach=left_chain(bones,change@bones['hand_l'],parents)
    allowed=set()
    for n in names:
        p=n
        while p in parents:
            if p=='upperarm_l':allowed.add(n);break
            p=parents[p]
    protected=max(float(np.abs(candidate[n]-bones[n]).max()) for n in names if n not in allowed)
    digit_error=max(float(np.abs(np.linalg.inv(candidate[parents[n]])@candidate[n]-np.linalg.inv(bones[parents[n]])@bones[n]).max())
        for n in names if n.endswith('_l') and n.startswith(('thumb_','index_','middle_','ring_','pinky_')))
    assert protected<1e-8 and digit_error<1e-8
    weights=d['weights'];rest=d['rest_native_cm'];ref=d['reference_matrices'];tri=d['skin_triangles']
    def skin(pose):
        result=np.zeros_like(rest)
        for j,n in enumerate(names):result+=weights[:,j,None]*transform(rest,pose[n]@np.linalg.inv(ref[j]))
        return result/weights.sum(1)[:,None]
    before=skin(bones);after=skin(candidate)
    right_ids=[j for j,n in enumerate(names) if n=='hand_r' or (n.endswith('_r') and n.startswith(('thumb_','index_','middle_','ring_','pinky_')))]
    right_mask=np.any(weights[:,right_ids]>0,axis=1)
    unaffected=np.all(weights[:,[names.index(n) for n in allowed]]==0,axis=1)
    palm=weights[:,names.index('hand_l')]>.99999
    right_skin=float(np.linalg.norm(after[right_mask]-before[right_mask],axis=1).max())
    unaffected_skin=float(np.linalg.norm(after[unaffected]-before[unaffected],axis=1).max())
    palm_tracking=float(np.linalg.norm(after[palm]-transform(before[palm],change),axis=1).max())
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1)
    aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    severe=int(np.sum((aa>3*np.maximum(ab,1e-8)) & (aa-ab>2)))
    length_error=max(abs(np.linalg.norm(candidate[b][:3,3]-candidate[a][:3,3])-
        np.linalg.norm(bones[b][:3,3]-bones[a][:3,3])) for a,b in (('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l')))
    drift=float(np.linalg.norm(transform(np.array([m['pivot_gun_cm']]),ga)[0]-pivot))
    preservation={'protected_bone_matrix_error':protected,'digit_local_matrix_error':digit_error,
        'right_skin_cm':right_skin,'unaffected_skin_cm':unaffected_skin,'palm_tracking_cm':palm_tracking,
        'arm_length_error_cm':float(length_error),'new_severe_edges':severe,'max_extra_edge_cm':float((aa-ab).max()),'pivot_drift_cm':drift}
    r.update(additional_angle_deg=2,total_angle_from_v6_approx_deg=old['angle_deg']+2,
        axis_world_unit=axis.tolist(),pivot_world_cm=pivot.tolist(),pivot_gun_cm=m['pivot_gun_cm'],
        muzzle_raise_cm=muzzle_raise,independent_translation_world_cm=[0,0,0],
        before_bones=original,after_bones={n:encode(candidate[n]) if n in allowed else original[n] for n in names},
        before_gun_world=previous['after']['gun_world'],after_gun_world=encode(ga),
        preservation=preservation,reach=reach,mesh_world=m['mesh_world'],parents=parents,bone_names=names,
        allowed_bones=sorted(allowed),pad_world_cm=tm.point(original['hand_r'],m['pad_hand_cm']),blade_gun_cm=m['blade_gun_cm'])
    assert right_skin<.001 and unaffected_skin<.001 and palm_tracking<.05 and length_error<.01 and severe==0 and drift<.001
    topology=read(TOPO);parts={c['id']:set(c['triangle_ids']) for c in topology['components']}
    origin=np.array(m['mesh_world']['t']);pad=np.array(r['pad_world_cm']);gt=d['gun_triangles'];contacts={}
    for label,points,gunmat in (('before',before,gb),('after',after,ga)):
        gun=transform(d['gun_local_cm'],gunmat)-origin;ids=np.array(sorted(parts[5]),int)
        tree=BVHTree.FromPolygons([Vector(x) for x in gun],gt[ids].tolist(),all_triangles=True)
        hit,normal,face,gap=tree.find_nearest(Vector(pad-origin));digits={}
        for digit in ('index','thumb','middle','ring','pinky'):
            indices=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_r')]
            mask=weights[:,indices].sum(1)>.1;faces=tri[np.all(mask[tri],axis=1)]
            pairs=intersection_pairs(points-origin,faces,gun,gt)
            digits[digit]={name:len({a for a,b in pairs if b in parts[part]}) for name,part in (('stock',0),('guard',4),('blade',5))}
        contacts[label]={'actual_pad_to_blade_cm':float(gap),'digits':digits}
    r['contact']=contacts
    r['contact_gate_passed']=(contacts['after']['actual_pad_to_blade_cm']<=.3 and
        contacts['after']['digits']['index']['stock']==0 and contacts['after']['digits']['index']['guard']==0 and contacts['after']['digits']['thumb']['stock']==0)
    r['status']='pivot_rotate_v9_static_comparison_only' if r['contact_gate_passed'] else 'stopped_contact_gate_static_comparison_only'
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(d['gun_local_cm'],gb),after_gun_world_cm=transform(d['gun_local_cm'],ga),gun_triangles=gt)
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
    r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','additional_angle_deg','muzzle_raise_cm','preservation','contact')})
