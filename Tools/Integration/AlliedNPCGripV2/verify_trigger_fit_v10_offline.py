"""Fresh-read delivered full skin, rigid transform and immutable source cache."""
import numpy as np
from common import *
out=BASE/'trigger_pad_v10d';r=read(out/'result.json')
m=read(BASE/'pivot_raise_measure_v7/result.json')
assert r['contact_gate_passed'] and not r['errors'] and r['inputs_unchanged']
assert guards()==r['guards_before']==r['guards_after']==611
assert all(sha(ROOT/p)==h for p,h in r['input_hashes'].items())
source=np.load(BASE/'pivot_raise_measure_v7/geometry.npz')
saved=np.load(out/'geometry.npz')
def matrix(t):
    x,y,z,w=t['q'];norm=x*x+y*y+z*z+w*w;assert norm>1e-10
    q=2/norm
    a=np.array([[1-q*(y*y+z*z),q*(x*y-z*w),q*(x*z+y*w)],
                [q*(x*y+z*w),1-q*(x*x+z*z),q*(y*z-x*w)],
                [q*(x*z-y*w),q*(y*z+x*w),1-q*(x*x+y*y)]])
    out=np.eye(4);out[:3,:3]=a*np.array(t['s']);out[:3,3]=t['t'];return out
def transform(p,t):return p@t[:3,:3].T+t[:3,3]
errors={}
for label in ('before','after'):
    skin=np.zeros_like(source['rest_native_cm']);weights=source['weights']
    for j,n in enumerate(m['bone_names']):
        skin+=weights[:,j,None]*transform(source['rest_native_cm'],matrix(r[label+'_bones'][n])@np.linalg.inv(source['reference_matrices'][j]))
    skin/=weights.sum(1)[:,None]
    errors[label+'_skin_cm']=float(np.linalg.norm(skin-saved[label+'_skin_world_cm'],axis=1).max())
    gun=transform(source['gun_local_cm'],matrix(r[label+'_gun_world']))
    errors[label+'_gun_cm']=float(np.linalg.norm(gun-saved[label+'_gun_world_cm'],axis=1).max())
assert np.array_equal(saved['skin_triangles'],source['skin_triangles'])
assert np.array_equal(saved['gun_triangles'],source['gun_triangles'])
assert max(errors.values())<.003,errors
pad=np.array(r['selected_surface_record']['actual_index_skin_vertices'])
actual=saved['after_skin_world_cm'][pad].mean(0)
paderror=float(np.linalg.norm(actual-np.array(r['pad_world_cm'])))
assert paderror<.001
write(out/'fresh_read_verification.json',{'guards':611,'input_hashes_exact':True,
    'source_triangles_exact':True,'geometry_sha256':sha(out/'geometry.npz'),
    'encoded_transform_vs_full_skin_errors_cm':errors,'actual_distal_face_pad_error_cm':paderror,
    'index_contact':r['final_contact']['digits']['index'],'local_index_gate':True,
    'runtime_motion_or_formal_asset_accepted':False})
print({'fresh_read':True,'guards':611,'errors_cm':errors,'actual_pad_error_cm':paderror})
