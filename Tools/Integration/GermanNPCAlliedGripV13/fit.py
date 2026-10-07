"""Approved whole-grasp rotation transfer, actual-trigger gun registration."""
import sys, json, struct, traceback
from pathlib import Path
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import ROOT,STORE,GLB,read,write,row,sha,guards,tm
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs
sys.path.insert(0,str(ROOT/'Tools/Integration/GermanNPCOrderedGripV4'))
from arm_fit import encode,arm_targets

BASE=STORE/'Evidence/GermanNPCAlliedGripV13'
REFERENCE='--reference' in sys.argv
OUT=BASE/('transfer_fit_v2' if REFERENCE else 'transfer_fit_v1')
PROBE=BASE/('probe_v2/result.json' if REFERENCE else 'probe_v1/result.json')
GD=STORE/'Evidence/GermanNPCOrderedGripV4/offline_v6/geometry.npz'
AD=STORE/'Evidence/AlliedNPCGripV2/pivot_raise_measure_v7/geometry.npz'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
assert not OUT.exists(); OUT.mkdir(parents=True)
r={'status':'starting','errors':[],'guards_before':guards(),
   'inputs':[row(p) for p in (PROBE,GD,AD,TOPO,GLB,Path(__file__),ROOT/'Tools/Integration/GermanNPCOrderedGripV4/arm_fit.py',ROOT/'Tools/Integration/WeaponTriggerAlignmentV2/blender_contact_common.py')],
   'source_modified':False,'formal_selected':False,'native_tested':False,'contact_accepted':False,'new_motion':False}
try:
    probe=read(PROBE);assert probe['status']=='approved_allied_digit_locals_and_reference_frames_verified'
    for entry in probe['inputs']:assert sha(ROOT/entry['path'])==entry['sha256']
    d=np.load(GD);ad=np.load(AD);names=probe['bone_names'];parents=probe['parents']
    rest=d['rest_native_cm'];w=d['weights'];refs=d['reference_matrices'];tri=d['skin_triangles'];gp=d['gun_local_cm'];gt=d['gun_triangles']
    before={n:mat(v) for n,v in probe['baseline_bones'].items()};ab={n:mat(v) for n,v in probe['allied_bones'].items()}
    q=probe['approved_digit_local_rotations']; after={}; localchecks={}
    def build(n):
        if n in after:return after[n]
        p=parents.get(n)
        if n in q:
            old=np.linalg.inv(before[p])@before[n]; v=encode(old)
            local=mat({'t':v['t'],'q':q[n],'s':v['s']});after[n]=build(p)@local
            actual=encode(np.linalg.inv(after[p])@after[n])
            localchecks[n]={'translation_error_cm':float(np.linalg.norm(np.array(actual['t'])-v['t'])),
                'scale_error':float(np.max(abs(np.array(actual['s'])-v['s']))),
                'donor_rotation_error_deg':tm.angle(actual['q'],q[n]),'change_deg':tm.angle(actual['q'],v['q'])}
        elif p in before and p in q:after[n]=build(p)@np.linalg.inv(before[p])@before[n]
        else:after[n]=before[n].copy()
        return after[n]
    for n in names:build(n)
    assert max(v['translation_error_cm'] for v in localchecks.values())<1e-6
    assert max(v['scale_error'] for v in localchecks.values())<1e-6
    assert max(v['donor_rotation_error_deg'] for v in localchecks.values())<.001
    def skin(b):
        out=np.zeros_like(rest)
        for j,n in enumerate(names):out+=w[:,j,None]*transform(rest,b[n]@np.linalg.inv(refs[j]))
        return out/w.sum(1)[:,None]
    p0=skin(before);p_transfer=skin(after)
    blob=GLB.read_bytes();gltf=json.loads(blob[20:20+struct.unpack_from('<I',blob,12)[0]]);at=0
    groups={'stock':set(),'guard':set(),'blade':set(),'whole':set(range(len(gt)))}
    for node in gltf['nodes']:
        if 'mesh' not in node:continue
        for primitive in gltf['meshes'][node['mesh']]['primitives']:
            count=gltf['accessors'][primitive['indices']]['count']//3;ids=set(range(at,at+count))
            if node['name'].startswith('Wood_'):groups['stock']|=ids
            if node['name'].startswith('Guard_'):groups['guard']|=ids
            if node['name']=='Trigger_Donor':groups['blade']|=ids
            at+=count
    assert at==len(gt)==24466
    topo=read(TOPO);a_parts={int(c['id']):np.array(c['triangle_ids'],int) for c in topo['components']}
    ap=ad['gun_local_cm'];at=ad['gun_triangles'];am=mat(probe['allied_gun_world']);g0=mat(probe['baseline_gun_world'])
    a_blade_local=ap[np.unique(at[a_parts[5]])].mean(0)
    g_blade_local=gp[np.unique(gt[sorted(groups['blade'])])].mean(0)
    # Right hand is the calibration frame, not a donor gun offset. The gun
    # axes have matching semantic +Y muzzle/-Y stock/+Z top in both caches.
    handmap=after['hand_r']@np.linalg.inv(ab['hand_r'])
    ag=handmap@am;gm=g0.copy()
    donor_orientation=ag[:3,:3]/np.linalg.norm(ag[:3,:3],axis=0)
    gm[:3,:3]=donor_orientation*np.linalg.norm(g0[:3,:3],axis=0)
    target_blade=transform(a_blade_local[None],ag)[0]
    gm[:3,3]=target_blade-gm[:3,:3]@g_blade_local
    assert np.linalg.norm(transform(g_blade_local[None],gm)[0]-target_blade)<1e-8
    # Retain the mature Allied support wrist's relationship to an ACTUAL
    # fore-end contact surface; register the German surface instead of copying
    # a player/NPC numeric wrist offset into another gun.
    a_stock=BVHTree.FromPolygons([Vector(v) for v in ap],at[a_parts[0]].tolist(),all_triangles=True)
    donor_support_local=transform(ab['hand_l'][None,:3,3],np.linalg.inv(am))[0]
    loc,normal,face,gap=a_stock.find_nearest(Vector(donor_support_local));assert loc is not None
    a_contact=np.array(loc,float);g_stock=BVHTree.FromPolygons([Vector(v) for v in gp],gt[sorted(groups['stock'])].tolist(),all_triangles=True)
    loc,normal,face,gap=g_stock.find_nearest(Vector(a_contact));assert loc is not None
    g_contact=np.array(loc,float);support=handmap@ab['hand_l']
    support[:3,3]+=transform(g_contact[None],gm)[0]-transform(a_contact[None],ag)[0]
    after,armcheck=arm_targets(after,{'l':support},parents);p1=skin(after);wg0=transform(gp,g0);wg1=transform(gp,gm)
    digitfaces={f'{digit}_{side}':np.flatnonzero(np.any((w[:,[names.index(f'{digit}_{i:02}_{side}') for i in (1,2,3)]].sum(1)>0)[tri],axis=1)) for side in ('r','l') for digit in ('thumb','index','middle','ring','pinky')}
    def contact(p,g):
        out={}
        for digit,fs in digitfaces.items():
            pairs=intersection_pairs(p,tri[fs],g,gt)
            out[digit]={group:sorted({int(fs[a]) for a,b in pairs if b in ids}) for group,ids in groups.items() if group!='whole'}
        return out
    bc,ac=contact(p0,wg0),contact(p1,wg1)
    def indexself(p):
        found=set();ids=digitfaces['index_r']
        for digit in ('thumb_r','middle_r','ring_r','pinky_r'):
            others=digitfaces[digit]
            for a,b in intersection_pairs(p,tri[ids],p,tri[others]):
                x,y=int(ids[a]),int(others[b])
                if not set(tri[x]).intersection(tri[y]):found.add((min(x,y),max(x,y)))
        return found
    before_self=indexself(p0);after_self=indexself(p1)
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    e0=np.linalg.norm(p0[edges[:,0]]-p0[edges[:,1]],axis=1);e1=np.linalg.norm(p1[edges[:,0]]-p1[edges[:,1]],axis=1)
    allowed=list(q)+[n for n in names if n.endswith('_l') and n.startswith(('upperarm_','lowerarm_','hand_'))]
    protected=[n for n in names if n not in allowed]
    protected_error=float(max(np.max(abs(after[n]-before[n])) for n in protected));assert protected_error<1e-8
    new_severe=int(np.sum((e1>3*e0)&(e1-e0>2)))
    # After arm following, reused digit rotations must still match the donor.
    final_errors={n:tm.angle(encode(np.linalg.inv(after[parents[n]])@after[n])['q'],q[n]) for n in q}
    assert max(final_errors.values())<.001
    r.update(bone_names=names,parents=parents,mesh_world=probe['mesh_world'],before_bones=probe['baseline_bones'],
      after_bones={n:encode(b) for n,b in after.items()},before_gun_world=probe['baseline_gun_world'],after_gun_world=encode(gm),
      transferred_digit_local_rotations=q,local_checks=localchecks,final_donor_rotation_errors_deg=final_errors,
      protected_bones=protected,protected_bone_matrix_error=protected_error,
      actual_allied_blade_local_cm=a_blade_local.tolist(),actual_german_blade_local_cm=g_blade_local.tolist(),
      actual_target_blade_cm=target_blade.tolist(),trigger_centroid_registration_error_cm=float(np.linalg.norm(transform(g_blade_local[None],gm)[0]-target_blade)),
      actual_allied_foreend_local_cm=a_contact.tolist(),actual_german_foreend_local_cm=g_contact.tolist(),
      original_length_support_arm_checks=armcheck,before_contact=bc,after_contact=ac,
      before_index_neighbor_self_pairs=len(before_self),after_index_neighbor_self_pairs=len(after_self),new_index_neighbor_self_pairs=len(after_self-before_self),
      new_severe_edges=new_severe,max_extra_skin_edge_cm=float(np.max(e1-e0)),
      gun_translation_from_v11_cm=float(np.linalg.norm(gm[:3,3]-g0[:3,3])),gun_rotation_from_v11_deg=tm.angle(encode(gm)['q'],encode(g0)['q']),
      gun_scale_error=float(np.max(abs(np.linalg.norm(gm[:3,:3],axis=0)-np.linalg.norm(g0[:3,:3],axis=0)))),
      mechanism='30 approved Allied digit local rotations; German actual-blade registration, original-length support arm')
    np.savez_compressed(OUT/'geometry.npz',skin=p1,before_skin=p0,transferred_skin=p_transfer,skin_triangles=tri,gun_before_cm=wg0,gun_after_cm=wg1,gun_triangles=gt)
    assert new_severe==0,'New severe skin edges'
    r['status']='whole_approved_grasp_transferred_actual_gun_fit_requires_visual_review'
except Exception:r['status']='failed_preserved';r['errors'].append(traceback.format_exc())
finally:
    r['guards_after']=guards();r['inputs_unchanged']=all(sha(ROOT/e['path'])==e['sha256'] for e in r['inputs']);write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','gun_translation_from_v11_cm','gun_rotation_from_v11_deg','original_length_support_arm_checks','new_severe_edges','new_index_neighbor_self_pairs')})
    print('Contact faces',{s:{d:{g:len(v) for g,v in x.items()} for d,x in r.get(s,{}).items()} for s in ('before_contact','after_contact')})
