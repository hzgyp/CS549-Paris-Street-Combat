"""ONE user-requested extra index03 existing-action curl; every other bone/gun fixed."""
import ast,sys,math,traceback
from pathlib import Path
import numpy as np
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from common import *
sys.path.insert(0,str(ROOT/'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat,transform,intersection_pairs

PREVIOUS=BASE/'index_curl_native_v11/result.json'
ORIGINAL=BASE/'trigger_fit_native_v10/result.json'
MEASURE=BASE/'pivot_raise_measure_v7/result.json';GEOMETRY=MEASURE.parent/'geometry.npz'
POSES=STORE/'Evidence/ReloadIndexContactV6/contact_exchange_v1/result.json'
AUDIT=STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
TOPO=STORE/'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
HELPER=Path(__file__).with_name('blender_pivot_raise_v7.py')
OUT=BASE/'tip_curl_v12';assert not OUT.exists();OUT.mkdir(parents=True)
paths=(PREVIOUS,ORIGINAL,MEASURE,GEOMETRY,POSES,AUDIT,TOPO,HELPER,Path(__file__))
r={'errors':[],'status':'starting','guards_before':guards(),'input_hashes':{p.relative_to(ROOT).as_posix():sha(p) for p in paths},
   'source_model_weights_actions_modified':False,'native_authored':False,'formal_selected':False,
   'contact_or_gameplay_accepted':False,'comparison_only':True}
functions=[n for n in ast.parse(HELPER.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='encode']
exec(compile(ast.Module(body=functions,type_ignores=[]),str(HELPER)+':encode_only','exec'),globals())
try:
    prev,original,m,poses,audit,topo=map(read,(PREVIOUS,ORIGINAL,MEASURE,POSES,AUDIT,TOPO))
    assert prev['inputs_unchanged'] and not prev['errors'] and prev['guards_after']==611
    assert all(sha(ROOT/p)==h for p,h in prev['input_hashes'].items())
    d=np.load(GEOMETRY);names=m['bone_names'];parents=m['parents'];weights=d['weights'];tri=d['skin_triangles']
    rest=d['rest_native_cm'];ref=d['reference_matrices'];bones={n:mat(t) for n,t in prev['after']['bones'].items()}
    gb=mat(prev['after']['gun_world']);origin=bones['hand_r'][:3,3].copy()
    source={n:mat(t) for n,t in poses['clips']['owner_reload']['samples']['2.2']['bones_component'].items()}
    n='index_03_r';parent=parents[n]
    actual_ref=np.linalg.inv(ref[names.index(parent)])@ref[names.index(n)]
    source_ref=np.linalg.inv(mat(audit['models']['owner']['ref_component'][parent]))@mat(audit['models']['owner']['ref_component'][n])
    frame_error=float(np.abs(actual_ref-source_ref).max());assert frame_error<.001
    current_local=np.linalg.inv(bones[parent])@bones[n]
    original_local=np.linalg.inv(mat(original['after']['bones'][parent]))@mat(original['after']['bones'][n])
    source_local=np.linalg.inv(source[parent])@source[n]
    q0=Matrix(original_local).to_quaternion();qs=Matrix(source_local).to_quaternion()
    qc=Matrix(current_local).to_quaternion();qnew=q0.slerp(qs,.5)
    local=current_local.copy();local[:3,:3]=np.array(qnew.to_matrix(),float)*np.linalg.norm(current_local[:3,:3],axis=0)
    afterbones=dict(bones);afterbones[n]=bones[parent]@local
    delta=math.degrees(qc.rotation_difference(qnew).angle);total=math.degrees(q0.rotation_difference(qnew).angle)
    assert 3<delta<4 and 10<total<11
    def skin(pose):
        result=np.zeros_like(rest)
        for j,b in enumerate(names):result+=weights[:,j,None]*transform(rest,pose[b]@np.linalg.inv(ref[j]))
        return result/weights.sum(1)[:,None]
    before=skin(bones);after=skin(afterbones);gp=d['gun_local_cm'];gt=d['gun_triangles'];gun=transform(gp,gb)-origin
    parts={q['id']:set(q['triangle_ids']) for q in topo['components']};digitfaces={}
    for digit in ('index','thumb','middle','ring','pinky'):
        ids=[j for j,b in enumerate(names) if b.startswith(digit+'_') and b.endswith('_r')]
        mask=weights[:,ids].sum(1)>.1;digitfaces[digit]=tri[np.all(mask[tri],axis=1)]
    blade=BVHTree.FromPolygons([Vector(p) for p in gun],gt[sorted(parts[5])].tolist(),all_triangles=True)
    padvertices=[21415,21418,21422]
    def contact(body):
        pad=(body-origin)[padvertices].mean(0);hit,normal,face,gap=blade.find_nearest(Vector(pad));ct={}
        for digit,faces in digitfaces.items():
            pairs=intersection_pairs(body-origin,faces,gun,gt)
            ct[digit]={part:len({a for a,b in pairs if b in parts[i]}) for part,i in (('stock',0),('guard',4),('blade',5))}
        return {'actual_pad_to_blade_cm':float(gap),'pad_world_cm':(pad+origin).tolist(),'digits':ct}
    neighbors=np.concatenate([digitfaces[b] for b in ('thumb','middle','ring','pinky')])
    def selfpairs(body):
        return {(a,b) for a,b in intersection_pairs(body-origin,digitfaces['index'],body-origin,neighbors)
                if not set(digitfaces['index'][a])&set(neighbors[b])}
    edges=np.unique(np.sort(np.concatenate([tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]]),axis=1),axis=0)
    ab=np.linalg.norm(before[edges[:,1]]-before[edges[:,0]],axis=1);aa=np.linalg.norm(after[edges[:,1]]-after[edges[:,0]],axis=1)
    unaffected=weights[:,names.index(n)]==0
    locals_error=max(float(np.abs(np.linalg.inv(afterbones[parents[b]])@afterbones[b]-np.linalg.inv(bones[parents[b]])@bones[b]).max())
        for b in names if b!=n and b in parents and parents[b] in bones)
    preserve={'protected_bone_matrix_error':max(float(np.abs(afterbones[b]-bones[b]).max()) for b in names if b!=n),
        'other_local_matrix_error':locals_error,'right_wrist_matrix_error':float(np.abs(afterbones['hand_r']-bones['hand_r']).max()),
        'unaffected_skin_cm':float(np.linalg.norm(after[unaffected]-before[unaffected],axis=1).max()),
        'index03_local_translation_error_cm':float(np.linalg.norm(local[:3,3]-current_local[:3,3])),
        'index03_local_scale_error':float(np.abs(np.linalg.norm(local[:3,:3],axis=0)-np.linalg.norm(current_local[:3,:3],axis=0)).max()),
        'new_severe_edges':int(np.sum((aa>3*np.maximum(ab,1e-8))&(aa-ab>2))),
        'max_extra_edge_cm':float((aa-ab).max()),'new_index_neighbor_self_pairs':len(selfpairs(after)-selfpairs(before))}
    baseline=contact(before);final=contact(after)
    r.update(reference_local_matrix_error=frame_error,additional_curl_deg=delta,total_curl_deg=total,
        selected_existing_pose={'clip':poses['clips']['owner_reload']['asset'],'sample_s':2.2,'strength_from_original':.5,'local_rotation_only':'index_03_r'},
        before_bones=prev['after']['bones'],after_bones={b:encode(afterbones[b]) if b==n else prev['after']['bones'][b] for b in names},
        before_gun_world=prev['after']['gun_world'],after_gun_world=prev['after']['gun_world'],gun_transform_exact=True,
        preservation=preserve,baseline_contact=baseline,final_contact=final,pad_world_cm=final['pad_world_cm'],pad_skin_vertices=padvertices,
        mesh_world=m['mesh_world'],parents=parents,bone_names=names,allowed_bones=[n],source_index_local_transform=encode(source_local))
    np.savez_compressed(OUT/'geometry.npz',before_skin_world_cm=before,after_skin_world_cm=after,skin_triangles=tri,
        before_gun_world_cm=transform(gp,gb),after_gun_world_cm=transform(gp,gb),gun_triangles=gt)
    comparison_gate=(preserve['protected_bone_matrix_error']<1e-8 and preserve['other_local_matrix_error']<1e-8 and preserve['unaffected_skin_cm']<.001
        and preserve['new_severe_edges']==0 and preserve['new_index_neighbor_self_pairs']==0
        and final['digits']['index']['stock']==0 and final['digits']['index']['guard']==0)
    r['comparison_gate_passed']=comparison_gate
    r['contact_gate_passed']=sum(final['digits']['index'].values())==0 and final['actual_pad_to_blade_cm']<=.2
    assert comparison_gate,'Requested one-tip comparison deformation/protection/stock/guard gate failed'
    r['status']='tip_curl_v12_comparison_ready'
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed_preserved'
finally:
    r['inputs_unchanged']=all(sha(ROOT/p)==h for p,h in r['input_hashes'].items());r['guards_after']=guards();write(OUT/'result.json',r)
    print({k:r.get(k) for k in ('status','errors','additional_curl_deg','total_curl_deg','baseline_contact','final_contact','preservation')},flush=True)
