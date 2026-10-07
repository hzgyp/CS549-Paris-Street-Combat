"""Fresh clean-process immutable source skin and fixed grip verification."""
import numpy as np
from common import *
out=BASE/'fp_wrist_v14';r=read(out/'result.json');m=read(BASE/'pivot_raise_measure_v7/result.json')
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
errors={}
for label in ('before','after'):
    skin=np.zeros_like(source['rest_native_cm']);w=source['weights']
    for j,n in enumerate(m['bone_names']):skin+=w[:,j,None]*transform(source['rest_native_cm'],matrix(r[label+'_bones'][n])@np.linalg.inv(source['reference_matrices'][j]))
    skin/=w.sum(1)[:,None];gun=transform(source['gun_local_cm'],matrix(r[label+'_gun_world']))
    errors[label+'_skin_cm']=float(np.linalg.norm(skin-saved[label+'_skin_world_cm'],axis=1).max())
    errors[label+'_gun_cm']=float(np.linalg.norm(gun-saved[label+'_gun_world_cm'],axis=1).max())
assert max(errors.values())<.003
assert r['before_gun_world']==r['after_gun_world']
assert all(r['before_bones'][n]==r['after_bones'][n] for n in m['bone_names'] if n not in r['allowed_bones'])
assert np.array_equal(saved['skin_triangles'],source['skin_triangles']) and np.array_equal(saved['gun_triangles'],source['gun_triangles'])
assert r['baseline_contact']==r['final_contact'] and r['preservation']['new_severe_edges']==0
write(out/'fresh_read_verification.json',{'guards':611,'input_hashes_exact':True,'source_triangles_exact':True,
    'errors_cm':errors,'protected_bones_and_gun_exact':True,'digit_contact_counts_unchanged':True,
    'geometry_sha256':sha(out/'geometry.npz'),'comparison_only':True,'formal_selected':False})
print({'fresh_read':True,'guards':611,'errors':errors})
