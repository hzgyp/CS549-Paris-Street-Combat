"""Fresh clean-process skin reconstruction and rigid hand/gun relations."""
import numpy as np
from common import *
out=BASE/'firing_assembly_v13';r=read(out/'result.json');m=read(BASE/'pivot_raise_measure_v7/result.json')
assert r['comparison_gate_passed'] and not r['errors'] and r['inputs_unchanged']
assert guards()==r['guards_before']==r['guards_after']==611
assert all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
source=np.load(BASE/'pivot_raise_measure_v7/geometry.npz');saved=np.load(out/'geometry.npz')
def matrix(t):
    x,y,z,w=t['q'];f=2/(x*x+y*y+z*z+w*w)
    q=np.array([[1-f*(y*y+z*z),f*(x*y-z*w),f*(x*z+y*w)],
        [f*(x*y+z*w),1-f*(x*x+z*z),f*(y*z-x*w)],
        [f*(x*z-y*w),f*(y*z+x*w),1-f*(x*x+y*y)]])
    value=np.eye(4);value[:3,:3]=q*np.array(t['s']);value[:3,3]=t['t'];return value
def transform(p,m):return p@m[:3,:3].T+m[:3,3]
errors={};relations={};digitlocals={}
for label in ('before','after'):
    skin=np.zeros_like(source['rest_native_cm']);w=source['weights']
    for j,n in enumerate(m['bone_names']):skin+=w[:,j,None]*transform(source['rest_native_cm'],matrix(r[label+'_bones'][n])@np.linalg.inv(source['reference_matrices'][j]))
    skin/=w.sum(1)[:,None];gun=transform(source['gun_local_cm'],matrix(r[label+'_gun_world']))
    errors[label+'_skin_cm']=float(np.linalg.norm(skin-saved[label+'_skin_world_cm'],axis=1).max())
    errors[label+'_gun_cm']=float(np.linalg.norm(gun-saved[label+'_gun_world_cm'],axis=1).max())
for s in ('r','l'):
    a=np.linalg.inv(matrix(r['after_bones']['hand_'+s]))@matrix(r['after_gun_world'])
    b=np.linalg.inv(matrix(r['before_bones']['hand_'+s]))@matrix(r['before_gun_world'])
    relations[s]=float(np.abs(a-b).max())
for n in m['bone_names']:
    if not n.startswith(('index_','thumb_','middle_','ring_','pinky_')):continue
    p=m['parents'][n]
    a=np.linalg.inv(matrix(r['after_bones'][p]))@matrix(r['after_bones'][n])
    b=np.linalg.inv(matrix(r['before_bones'][p]))@matrix(r['before_bones'][n]);digitlocals[n]=float(np.abs(a-b).max())
assert max(errors.values())<.003 and max(relations.values())<.001 and max(digitlocals.values())<.001
assert np.array_equal(saved['skin_triangles'],source['skin_triangles']) and np.array_equal(saved['gun_triangles'],source['gun_triangles'])
origin=np.array(r['before_bones']['upperarm_r']['t']);faces=source['skin_triangles']
sw=source['weights'][:,[m['bone_names'].index(j) for j in ('upperarm_r','clavicle_r','upperarm_twist_01_r')]].sum(1)
sf=faces[(sw[faces].max(1)>.3)&(np.linalg.norm(saved['before_skin_world_cm'][faces].mean(1)-origin,axis=1)<12)]
triangles=saved['after_skin_world_cm'][sf]-origin;p=np.array(r['butt_target_world_cm'])-origin
a,b,c=triangles[:,0],triangles[:,1],triangles[:,2];u=b-a;v=c-a;normal=np.cross(u,v);area=np.sum(normal*normal,axis=1)
valid=area>1e-12;plane=p-(np.sum((p-a)*normal,axis=1)/np.maximum(area,1e-12))[:,None]*normal
uu=np.sum(u*u,axis=1);uv=np.sum(u*v,axis=1);vv=np.sum(v*v,axis=1);qp=plane-a
up=np.sum(qp*u,axis=1);vp=np.sum(qp*v,axis=1);den=uu*vv-uv*uv
s=(vv*up-uv*vp)/np.maximum(den,1e-12);t=(uu*vp-uv*up)/np.maximum(den,1e-12)
candidates=[]
for first,last in ((a,b),(b,c),(c,a)):
    edge=last-first;fraction=np.clip(np.sum((p-first)*edge,axis=1)/np.maximum(np.sum(edge*edge,axis=1),1e-12),0,1)
    candidates.append(first+fraction[:,None]*edge)
candidates.append(plane);candidates=np.stack(candidates,axis=1)
dist=np.linalg.norm(candidates-p,axis=2);dist[:,3]=np.where(valid&(s>=0)&(t>=0)&(s+t<=1),dist[:,3],np.inf)
i,j=np.unravel_index(np.argmin(dist),dist.shape)
shoulder={'rear_butt_center_to_actual_final_shoulder_surface_cm':float(dist[i,j]),
    'closest_skin_world_cm':(candidates[i,j]+origin).tolist(),'triangle':sf[i].tolist(),
    'closed_solid_penetration_or_complete_butt_seating_proved':False}
write(out/'fresh_read_verification.json',{'guards':611,'input_hashes_exact':True,'source_triangles_exact':True,
    'errors_cm':errors,'hand_relative_gun_errors':relations,'max_digit_local_error':max(digitlocals.values()),
    'geometry_sha256':sha(out/'geometry.npz'),'shoulder_surface_check':shoulder,'comparison_only':True,'formal_selected':False})
print({'fresh_read':True,'guards':611,'errors':errors,'relations':relations,'digits':max(digitlocals.values()),'shoulder':shoulder})
