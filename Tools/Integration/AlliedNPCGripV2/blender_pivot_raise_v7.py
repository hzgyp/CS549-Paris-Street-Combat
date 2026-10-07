"""One marked-pivot raise and original-length Allied support-arm comparison."""
import sys
import math
import traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0, str(Path(__file__).parent))
from common import *
sys.path.insert(0, str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat, transform, intersection_pairs

MEASURE=BASE/'pivot_raise_measure_v7/result.json'
GEOMETRY=MEASURE.parent/'geometry.npz'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
OUT=BASE/'pivot_raise_trial_v7'
assert not OUT.exists()
OUT.mkdir(parents=True)
inputs=(MEASURE,GEOMETRY,TOPO,Path(__file__))
r={'errors':[], 'status':'starting', 'guards_before':guards(),
   'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
   'source_model_weights_actions_modified':False, 'native_authored':False,
   'formal_selected':False, 'contact_or_gameplay_accepted':False}

def swing(a,b):
    return np.array(Vector(a).rotation_difference(Vector(b)).to_matrix(),float)

def encode(m):
    t,q,s=Matrix(m).decompose()
    return {'t':list(t),'q':[q.x,q.y,q.z,q.w],'s':list(s)}

def left_chain(bones, target, parents):
    shoulder=bones['upperarm_l'][:3,3]
    elbow=bones['lowerarm_l'][:3,3]
    wrist=bones['hand_l'][:3,3]
    goal=target[:3,3]
    la=float(np.linalg.norm(elbow-shoulder));lb=float(np.linalg.norm(wrist-elbow))
    reach=float(np.linalg.norm(goal-shoulder))
    assert abs(la-lb)+1e-5<reach<la+lb-1e-5,'Original-length left arm cannot reach target'
    line=(goal-shoulder)/reach
    bend=elbow-shoulder-line*np.dot(elbow-shoulder,line)
    assert np.linalg.norm(bend)>1e-6,'Degenerate source elbow plane'
    bend/=np.linalg.norm(bend)
    along=(la*la-lb*lb+reach*reach)/(2*reach)
    new_elbow=shoulder+line*along+bend*math.sqrt(max(0,la*la-along*along))
    explicit={'hand_l':target.copy()}
    for name,position,old,new in (
        ('upperarm_l',shoulder,elbow-shoulder,new_elbow-shoulder),
        ('lowerarm_l',new_elbow,wrist-elbow,goal-new_elbow)):
        m=bones[name].copy();m[:3,:3]=swing(old,new)@m[:3,:3];m[:3,3]=position
        explicit[name]=m
    result={}
    def get(name):
        if name not in result:
            parent=parents.get(name)
            if name in explicit:result[name]=explicit[name]
            elif parent in bones:result[name]=get(parent)@np.linalg.inv(bones[parent])@bones[name]
            else:result[name]=bones[name].copy()
        return result[name]
    for n in bones:get(n)
    return result,{'upper_cm':la,'forearm_cm':lb,'target_reach_cm':reach,
                  'max_reach_cm':la+lb,'wrist_motion_cm':float(np.linalg.norm(goal-wrist))}

try:
    m=read(MEASURE)
    assert not m['errors'] and m['inputs_unchanged'] and m['guards_after']==611
    assert all(sha(ROOT/p)==h for p,h in m['input_hashes'].items())
    d=np.load(GEOMETRY)
    names=m['bone_names'];parents=m['parents']
    bones={n:mat(t) for n,t in m['before_bones'].items()}
    gb=mat(m['before_gun_world']);pivot=np.array(m['pivot_world_cm'])
    blade=transform(np.array([m['blade_gun_cm']]),gb)[0]
    pad=np.array(m['index_pad_world_cm'])
    rotation=swing(blade-pivot,pad-pivot)
    angle=math.degrees(math.acos(np.clip((np.trace(rotation)-1)/2,-1,1)))
    assert angle<=30,'Bounded raise exceeds 30 degrees'
    change=np.eye(4);change[:3,:3]=rotation;change[:3,3]=pivot-rotation@pivot
    ga=change@gb
    muzzle_local=d['gun_local_cm'][np.argmax(d['gun_local_cm'][:,1])]
    muzzle_before=transform(muzzle_local[None,:],gb)[0]
    muzzle_after=transform(muzzle_local[None,:],ga)[0]
    assert muzzle_after[2]>muzzle_before[2],'Derived fit does not raise muzzle'
    candidate,reach=left_chain(bones,change@bones['hand_l'],parents)
    allowed=set()
    for n in names:
        parent=n
        while parent in parents:
            if parent=='upperarm_l':allowed.add(n);break
            parent=parents[parent]
    protected=max(float(np.abs(candidate[n]-bones[n]).max()) for n in names if n not in allowed)
    digit_error=max(float(np.abs(np.linalg.inv(candidate[parents[n]])@candidate[n]-
                      np.linalg.inv(bones[parents[n]])@bones[n]).max())
                    for n in names if n.endswith('_l') and n.startswith(('index_','middle_','ring_','pinky_','thumb_')))
    assert protected<1e-8 and digit_error<1e-8
    weights=d['weights'];rest=d['rest_native_cm'];ref=d['reference_matrices']
    after=np.zeros_like(rest)
    for j,n in enumerate(names):
        after+=weights[:,j,None]*transform(rest,candidate[n]@np.linalg.inv(ref[j]))
    after/=weights.sum(1)[:,None]
    before=d['skin_world_cm'];tri=d['skin_triangles']
    right_ids=[j for j,n in enumerate(names) if n=='hand_r' or (n.endswith('_r') and n.startswith(('index_','middle_','ring_','pinky_','thumb_')))]
    right_mask=np.any(weights[:,right_ids]>0,axis=1)
    right_skin=float(np.linalg.norm(after[right_mask]-before[right_mask],axis=1).max())
    unaffected=np.all(weights[:,[names.index(n) for n in allowed]]==0,axis=1)
    unaffected_skin=float(np.linalg.norm(after[unaffected]-before[unaffected],axis=1).max())
    palm=weights[:,names.index('hand_l')]>.99999
    palm_tracking=float(np.linalg.norm(after[palm]-transform(before[palm],change),axis=1).max())
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1)
    aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    severe=int(np.sum((aa>3*np.maximum(ab,1e-8)) & (aa-ab>2)))
    length_error=max(abs(np.linalg.norm(candidate[b][:3,3]-candidate[a][:3,3])-
                         np.linalg.norm(bones[b][:3,3]-bones[a][:3,3]))
                     for a,b in (('upperarm_l','lowerarm_l'),('lowerarm_l','hand_l')))
    preservation={'protected_bone_matrix_error':protected,'digit_local_matrix_error':digit_error,
        'right_skin_cm':right_skin,'unaffected_skin_cm':unaffected_skin,'palm_tracking_cm':palm_tracking,
        'arm_length_error_cm':float(length_error),'new_severe_edges':severe,
        'max_extra_edge_cm':float((aa-ab).max()),
        'pivot_drift_cm':float(np.linalg.norm(transform(np.array([m['pivot_gun_cm']]),ga)[0]-pivot))}
    r.update(angle_deg=angle,axis_world=np.array(Vector(blade-pivot).cross(Vector(pad-pivot))).tolist(),
        preservation=preservation,reach=reach,muzzle_raise_cm=float(muzzle_after[2]-muzzle_before[2]),
        before_gun_world=m['before_gun_world'],after_gun_world=encode(ga),
        before_bones=m['before_bones'],after_bones={n:encode(candidate[n]) if n in allowed else m['before_bones'][n] for n in names},
        mesh_world=m['mesh_world'],parents=parents,bone_names=names,pivot_world_cm=pivot.tolist(),
        pad_world_cm=pad.tolist(),blade_gun_cm=m['blade_gun_cm'],allowed_bones=sorted(allowed))
    assert right_skin<.001 and unaffected_skin<.001 and palm_tracking<.05
    assert length_error<.01 and severe==0 and preservation['pivot_drift_cm']<.001
    topology=read(TOPO);parts={c['id']:set(c['triangle_ids']) for c in topology['components']}
    origin=np.array(m['mesh_world']['t']);gt=d['gun_triangles']
    contacts={}
    for label,points,gunmat in (('before',before,gb),('after',after,ga)):
        gun=transform(d['gun_local_cm'],gunmat)-origin
        ids=np.array(sorted(parts[5]),int)
        tree=BVHTree.FromPolygons([Vector(x) for x in gun],gt[ids].tolist(),all_triangles=True)
        hit,normal,face,gap=tree.find_nearest(Vector(pad-origin))
        digits={}
        for digit in ('index','thumb','middle','ring','pinky'):
            indices=[j for j,n in enumerate(names) if n.startswith(digit+'_') and n.endswith('_r')]
            mask=weights[:,indices].sum(1)>.1
            faces=tri[np.all(mask[tri],axis=1)]
            pairs=intersection_pairs(points-origin,faces,gun,gt)
            digits[digit]={part:len({a for a,b in pairs if b in parts[partid]})
                           for part,partid in (('stock',0),('guard',4),('blade',5))}
        contacts[label]={'actual_pad_to_blade_cm':float(gap),
            'landmark_pad_to_blade_cm':float(np.linalg.norm(transform(np.array([m['blade_gun_cm']]),gunmat)[0]-pad)),
            'digits':digits}
    r['contact']=contacts
    r['contact_gate_passed']=(contacts['after']['actual_pad_to_blade_cm']<=.3 and
        all(contacts['after']['digits'][n]['stock']==0 for n in ('index','thumb')) and
        contacts['after']['digits']['index']['guard']==0)
    r['status']='pivot_raise_static_comparison_only' if r['contact_gate_passed'] else 'stopped_contact_gate_static_comparison_only'
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,
        skin_triangles=tri,before_gun_world_cm=transform(d['gun_local_cm'],gb),
        after_gun_world_cm=transform(d['gun_local_cm'],ga),gun_triangles=gt)
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
    r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','angle_deg','muzzle_raise_cm','reach','preservation','contact')})
