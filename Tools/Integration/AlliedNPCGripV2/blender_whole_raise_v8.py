"""One user-requested +0.3cm world-Z gun raise; mature digit pose unchanged."""
import ast
import sys
import math
import traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
import transform_math as tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs

PREVIOUS=BASE/'pivot_raise_native_v7b/result.json'
MEASURE=BASE/'pivot_raise_measure_v7/result.json'
GEOMETRY=MEASURE.parent/'geometry.npz'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
HELPER=Path(__file__).with_name('blender_pivot_raise_v7.py')
OUT=BASE/'whole_raise_trial_v8'
assert not OUT.exists();OUT.mkdir(parents=True)
inputs=(PREVIOUS,MEASURE,GEOMETRY,TOPO,HELPER,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
   'source_model_weights_actions_modified':False,'native_authored':False,
   'formal_selected':False,'contact_or_gameplay_accepted':False}

# Only the three reviewed PURE functions are extracted. No old author module,
# top-level setup, angular fitter, I/O, guard epoch or candidate runs.
tree=ast.parse(HELPER.read_text(encoding='utf-8'))
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('swing','encode','left_chain')]
assert len(functions)==3
exec(compile(ast.Module(body=functions,type_ignores=[]),str(HELPER)+':pure_helpers','exec'),globals())

try:
    previous=read(PREVIOUS);m=read(MEASURE)
    assert previous['status']=='pivot_raise_v7_native_views_require_user_review' and not previous['errors']
    assert previous['inputs_unchanged'] and previous['guards_after']==611
    assert all(sha(ROOT/p)==h for p,h in previous['input_hashes'].items())
    assert m['inputs_unchanged'] and not m['errors'] and m['guards_after']==611
    d=np.load(GEOMETRY);names=m['bone_names'];parents=m['parents']
    original=previous['after']['bones'];bones={n:mat(t) for n,t in original.items()}
    gb=mat(previous['after']['gun_world']);change=np.eye(4);change[2,3]=.3
    ga=change@gb
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
        out=np.zeros_like(rest)
        for j,n in enumerate(names):out+=weights[:,j,None]*transform(rest,pose[n]@np.linalg.inv(ref[j]))
        return out/weights.sum(1)[:,None]
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
    preservation={'protected_bone_matrix_error':protected,'digit_local_matrix_error':digit_error,
        'right_skin_cm':right_skin,'unaffected_skin_cm':unaffected_skin,'palm_tracking_cm':palm_tracking,
        'arm_length_error_cm':float(length_error),'new_severe_edges':severe,'max_extra_edge_cm':float((aa-ab).max())}
    after_gun={**previous['after']['gun_world'],'t':[previous['after']['gun_world']['t'][0],previous['after']['gun_world']['t'][1],previous['after']['gun_world']['t'][2]+.3]}
    r.update(translation_world_cm=[0,0,.3],angle_change_deg=0,gun_q_scale_exact=True,
        before_bones=original,after_bones={n:encode(candidate[n]) if n in allowed else original[n] for n in names},
        before_gun_world=previous['after']['gun_world'],after_gun_world=after_gun,
        preservation=preservation,reach=reach,mesh_world=m['mesh_world'],parents=parents,bone_names=names,
        allowed_bones=sorted(allowed),pad_world_cm=tm.point(original['hand_r'],m['pad_hand_cm']),
        blade_gun_cm=m['blade_gun_cm'],previous_marked_pivot_gun_cm=m['pivot_gun_cm'])
    assert right_skin<.001 and unaffected_skin<.001 and palm_tracking<.05 and length_error<.01 and severe==0
    topology=read(TOPO);parts={c['id']:set(c['triangle_ids']) for c in topology['components']}
    origin=np.array(m['mesh_world']['t']);pad=np.array(r['pad_world_cm']);gt=d['gun_triangles'];contacts={}
    for label,points,gunmat in (('before',before,gb),('after',after,ga)):
        gun=transform(d['gun_local_cm'],gunmat)-origin
        ids=np.array(sorted(parts[5]),int)
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
    r['status']='whole_raise_v8_static_comparison_only' if r['contact_gate_passed'] else 'stopped_contact_gate_static_comparison_only'
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(d['gun_local_cm'],gb),after_gun_world_cm=transform(d['gun_local_cm'],ga),gun_triangles=gt)
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
    r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','translation_world_cm','preservation','contact')})
