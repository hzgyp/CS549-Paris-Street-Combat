"""Read actual trigger geometry; ONE marked camera-plane alignment, no fit scan."""
import struct
import numpy as np
from PIL import Image, ImageFilter
from common import *
OUT=BASE/'marked_landmarks_v1';assert not OUT.exists(),'Preserve identity'
assert guards()==618
old=read(REFERENCE/'result.json');assert not old['errors']
pose=old['pairs']['german']
view=next(c for c in old['captures'] if c['faction']=='german' and c['view']=='right')
model=read(ROOT/'Assets/Sync/manifests/german-rifle-model.json')
assert any(f['path']==GLB.relative_to(ROOT).as_posix() and f['sha256']==sha(GLB) for f in model['files'])
original=np.asarray(Image.open(REFERENCE/'german_right.png').convert('RGB'),dtype=float)/255
marked=np.asarray(Image.open(MARKING).convert('RGB'),dtype=float)/255
# Image registration only; not gun-position or pose parameter sampling.
gray=original.mean(axis=2);user=marked.mean(axis=2)
gy,gx=np.gradient(gray)
yy,xx=np.mgrid[20:min(730,user.shape[0]-20):4,20:min(1200,user.shape[1]-20):4]
mask=(user[yy,xx]>.06)&~((marked[yy,xx,0]>.6)&(marked[yy,xx,0]>marked[yy,xx,1]*1.6))
x=xx[mask].astype(float);y=yy[mask].astype(float);values=user[yy[mask],xx[mask]]
def sample(a,X,Y):
    X=np.clip(X,0,a.shape[1]-1.001);Y=np.clip(Y,0,a.shape[0]-1.001)
    ix=X.astype(int);iy=Y.astype(int);u=X-ix;v=Y-iy
    return a[iy,ix]*(1-u)*(1-v)+a[iy,ix+1]*u*(1-v)+a[iy+1,ix]*(1-u)*v+a[iy+1,ix+1]*u*v
par=np.array([1.25,1.25,0.,0.])
# One presentation correction: broad silhouettes initialize raw-pixel matching.
# Final raw RMS gate is unchanged; no gun transform is tried here.
for blur in (5,1,0):
    init_gray=np.asarray(Image.open(REFERENCE/'german_right.png').convert('RGB').filter(ImageFilter.GaussianBlur(blur)),dtype=float).mean(2)/255
    init_user=np.asarray(Image.open(MARKING).convert('RGB').filter(ImageFilter.GaussianBlur(blur/1.25)),dtype=float).mean(2)/255
    iygrad,ixgrad=np.gradient(init_gray)
    for _ in range(40):
        X=x*par[0]+par[2];Y=y*par[1]+par[3]
        residual=sample(init_gray,X,Y)-init_user[yy[mask],xx[mask]]
        dx=sample(ixgrad,X,Y);dy=sample(iygrad,X,Y)
        jac=np.stack([dx*x,dy*y,dx,dy],axis=1)
        weights=np.minimum(1,.06/np.maximum(np.abs(residual),1e-6))
        step=np.linalg.lstsq(jac*weights[:,None],residual*weights,rcond=None)[0]
        par-=step
        if np.linalg.norm(step)<.001:break
rms=float(np.sqrt(np.mean((sample(gray,x*par[0]+par[2],y*par[1]+par[3])-values)**2)))
assert rms<.035 and all(1.2<v<1.3 for v in par[:2]),('Registration ambiguous',par.tolist(),rms)
def original_pixel(p):return [float(p[0]*par[0]+par[2]),float(p[1]*par[1]+par[3])]
# Manual interpretation of the visible arrow endpoints; no inferred finger pose.
target_px=original_pixel([734,341]);arrow_tip=original_pixel([779,435])
b=GLB.read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);blob=b[28+n:]
def accessor(index):
    a=j['accessors'][index];v=j['bufferViews'][a['bufferView']]
    assert 'sparse' not in a and 'byteStride' not in v
    dims={'SCALAR':1,'VEC3':3}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]
    return np.frombuffer(blob,dtype=dtype,count=a['count']*dims,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dims)
import_cfg=read(ROOT/'tmp/german-rifle-ue-v1/preflight_v1.json')
offset=np.array(import_cfg['native_import_offset_cm'])
assert import_cfg['native_import_yaw_deg']==90
nodes={node['name']:node for node in j['nodes'] if 'mesh' in node}
assert len(nodes)==24 and all('matrix' not in q and 'rotation' not in q and 'scale' not in q for q in j['nodes'])
def positions(node,prim):
    a=accessor(prim['attributes']['POSITION']).astype(float)+np.array(node.get('translation',[0,0,0]))
    # glTF -> UE (X,-Z,Y), then original native yaw90 and import translation.
    return np.stack([a[:,2],a[:,0],a[:,1]],axis=1)*100+offset
all_vertices=np.concatenate([positions(node,p) for node in nodes.values() for p in j['meshes'][node['mesh']]['primitives']])
native=read(STORE/'Evidence/GermanRifleUEV1/import_v3/result.json')
bounds_error=float(max(np.max(np.abs(all_vertices.min(axis=0)-native['bounds_min_cm'])),np.max(np.abs(all_vertices.max(axis=0)-native['bounds_max_cm']))))
assert bounds_error<.01,bounds_error
eye=np.array(view['eye_cm']);center=np.array(view['target_cm']);forward=center-eye;forward/=np.linalg.norm(forward)
right=np.cross([0,0,1],forward);right/=np.linalg.norm(right);up=np.cross(forward,right)
width=view['ortho_width_cm'];W,H=original.shape[1],original.shape[0]
def project(point):
    d=np.array(point)-center
    return np.array([W/2+np.dot(d,right)*W/width,H/2-np.dot(d,up)*W/width])
trigger=nodes['Trigger_Donor'];verts=[]
for p in j['meshes'][trigger['mesh']]['primitives']:
    a=positions(trigger,p);verts.extend(a[accessor(p['indices']).ravel().reshape(-1,3)])
triangles=np.asarray(verts);best=None
for i,t in enumerate(triangles):
    points=np.array([project(tm.point(pose['gun_world'],v)) for v in t])
    A=np.column_stack([points[1]-points[0],points[2]-points[0]])
    if abs(np.linalg.det(A))<1e-8:continue
    uv=np.linalg.solve(A,np.array(arrow_tip)-points[0]);weights=np.array([1-uv.sum(),*uv])
    if np.all(weights>=0):candidates=[weights]
    else:
        candidates=[]
        for k,l in ((0,1),(1,2),(2,0)):
            d=points[l]-points[k];s=np.clip(np.dot(np.array(arrow_tip)-points[k],d)/max(np.dot(d,d),1e-12),0,1)
            w=np.zeros(3);w[k]=1-s;w[l]=s;candidates.append(w)
    for weights in candidates:
        q=weights@points;distance=float(np.linalg.norm(q-arrow_tip))
        if best is None or distance<best[0]:best=(distance,i,weights@t,q,weights)
assert best is not None and best[0]<25,('Arrow does not identify actual trigger',None if best is None else best[0])
blade_local=best[2];blade_world=np.array(tm.point(pose['gun_world'],blade_local))
blade_px=project(blade_world)
delta=((target_px[0]-blade_px[0])*width/W)*right-((target_px[1]-blade_px[1])*width/W)*up
target_world=blade_world+delta
assert abs(np.dot(delta,forward))<1e-8 and np.linalg.norm(delta)<10
payload={'status':'measured_one_marked_translation','guards':618,'reference_sha256':sha(REFERENCE/'result.json'),
    'model':row(GLB),'marking_sha256':sha(MARKING),'registration_user_to_native':par.tolist(),'registration_gray_rms':rms,
    'manual_user_target_pixel':[734,341],'manual_user_arrow_tip_pixel':[779,435],
    'native_target_pixel':target_px,'native_arrow_tip_pixel':arrow_tip,'native_blade_pixel':blade_px.tolist(),
    'trigger_surface_triangle':int(best[1]),'trigger_surface_barycentric':best[4].tolist(),'arrow_to_trigger_px':best[0],
    'native_import_bounds_error_cm':bounds_error,'blade_gun_cm':blade_local.tolist(),
    'target_hand_cm':tm.inverse_point(pose['bone_world']['hand_r'],target_world.tolist()),
    'delta_reference_world_cm':delta.tolist(),'translation_cm':float(np.linalg.norm(delta)),
    'depth':'Retained original trigger camera depth; image does not establish skin depth/contact',
    'fixed_source':pose,'contact_accepted':False}
assert guards()==618
write(OUT/'result.json',payload)
print(json.dumps({k:payload[k] for k in ('status','registration_gray_rms','native_import_bounds_error_cm','arrow_to_trigger_px','delta_reference_world_cm','translation_cm')}))
