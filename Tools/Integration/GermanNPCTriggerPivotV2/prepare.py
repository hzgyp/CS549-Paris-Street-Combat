"""One marked top-plane gun rotation around the actual retained trigger point."""
import sys,struct,math,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'GermanNPCGripV1'))
from common import *
V1=BASE/'native_views_v1'
DEST=STORE/'Evidence/GermanNPCTriggerPivotV2'
OUT=DEST/'marked_rotation_v1'
MARK=Path('C:/Users/hzgyp/AppData/Local/Temp/codex-clipboard-a0a570d0-dd95-4430-bbc5-7bf39bc7f161.png')
assert not OUT.exists(),'Preserve occupied proof'
assert guards()==618
r=read(V1/'result.json');assert not r['errors'] and r['all_bones_exact']
fit=read(BASE/'marked_landmarks_v1/result.json')
assert sha(GLB)==fit['model']['sha256']
presentation=read(V1/'presentation.json')
for f in presentation['native_originals']:
    assert sha(ROOT/f['path'])==f['sha256']
source=np.asarray(Image.open(V1/'after_top.png').convert('RGB'),dtype=float)/255
mark=np.asarray(Image.open(MARK).convert('RGB'),dtype=float)/255
gray=source.mean(2);user=mark.mean(2)
yy,xx=np.mgrid[34:285:2,15:415:2]
mask=(user[yy,xx]>.06)&~((mark[yy,xx,0]>.6)&(mark[yy,xx,0]>mark[yy,xx,1]*1.6))
x=xx[mask].astype(float);y=yy[mask].astype(float)
def sample(a,X,Y):
    X=np.clip(X,0,a.shape[1]-1.001);Y=np.clip(Y,0,a.shape[0]-1.001)
    ix=X.astype(int);iy=Y.astype(int);u=X-ix;v=Y-iy
    return a[iy,ix]*(1-u)*(1-v)+a[iy,ix+1]*u*(1-v)+a[iy+1,ix]*(1-u)*v+a[iy+1,ix+1]*u*v
par=np.array([1600/434,1000/271,0.,-26*1000/271])
for blur in (5,1,0):
    a=np.asarray(Image.open(V1/'after_top.png').convert('RGB').filter(ImageFilter.GaussianBlur(blur)),dtype=float).mean(2)/255
    b=np.asarray(Image.open(MARK).convert('RGB').filter(ImageFilter.GaussianBlur(blur/3.68)),dtype=float).mean(2)/255
    gy,gx=np.gradient(a)
    for _ in range(40):
        X=x*par[0]+par[2];Y=y*par[1]+par[3]
        residual=sample(a,X,Y)-b[yy[mask],xx[mask]]
        dx=sample(gx,X,Y);dy=sample(gy,X,Y)
        jac=np.stack([dx*x,dy*y,dx,dy],axis=1)
        weights=np.minimum(1,.06/np.maximum(np.abs(residual),1e-6))
        step=np.linalg.lstsq(jac*weights[:,None],residual*weights,rcond=None)[0]
        par-=step
        if np.linalg.norm(step)<.001:break
rms=float(np.sqrt(np.mean((sample(gray,x*par[0]+par[2],y*par[1]+par[3])-user[yy[mask],xx[mask]])**2)))
assert rms<.035 and all(3.5<v<3.9 for v in par[:2]),('Registration ambiguous',par.tolist(),rms)
def px(p):return np.array([p[0]*par[0]+par[2],p[1]*par[1]+par[3]])
stock_px=px([213,177]);palm_px=px([249,190])
blob=GLB.read_bytes();n=struct.unpack_from('<I',blob,12)[0];g=json.loads(blob[20:20+n]);bin_data=blob[28+n:]
def accessor(index):
    a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
    assert 'sparse' not in a and 'byteStride' not in v
    dims={'SCALAR':1,'VEC3':3}[a['type']]
    dtype={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]
    return np.frombuffer(bin_data,dtype=dtype,count=a['count']*dims,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],dims)
import_cfg=read(ROOT/'tmp/german-rifle-ue-v1/preflight_v1.json')
offset=np.array(import_cfg['native_import_offset_cm']);assert import_cfg['native_import_yaw_deg']==90
nodes={v['name']:v for v in g['nodes'] if 'mesh' in v}
assert all('matrix' not in v and 'rotation' not in v and 'scale' not in v for v in g['nodes'])
def vertices(node,p):
    a=accessor(p['attributes']['POSITION']).astype(float)+np.array(node.get('translation',[0,0,0]))
    return np.stack([a[:,2],a[:,0],a[:,1]],axis=1)*100+offset
all_v=np.concatenate([vertices(node,p) for node in nodes.values() for p in g['meshes'][node['mesh']]['primitives']])
native=read(STORE/'Evidence/GermanRifleUEV1/import_v3/result.json')
bounds_error=float(max(np.max(np.abs(all_v.min(0)-native['bounds_min_cm'])),np.max(np.abs(all_v.max(0)-native['bounds_max_cm']))))
assert bounds_error<.01
camera=next(c for c in r['captures'] if c['file']=='after_top.png')
center=np.array(camera['target_cm']);axis=np.array([0.,0.,1.])
# Native top capture uses ACTOR yaw, not the skeletal mesh/root yaw.
front=next(c for c in r['captures'] if c['file']=='after_front.png')
up=np.array(front['eye_cm'])-np.array(front['target_cm']);up[2]=0;up/=np.linalg.norm(up)
right=np.cross(axis,up);right/=np.linalg.norm(right)
width=camera['width_cm'];gun=r['after']['gun_world']
def project(p):
    d=np.array(p)-center
    return np.array([800+np.dot(d,right)*1600/width,500-np.dot(d,up)*1600/width])
stock=nodes['Wood_ContinuousStock'];triangles=[]
for p in g['meshes'][stock['mesh']]['primitives']:
    triangles.extend(vertices(stock,p)[accessor(p['indices']).ravel().reshape(-1,3)])
best=None
for i,t in enumerate(np.asarray(triangles)):
    world=np.array([tm.point(gun,p) for p in t]);points=np.array([project(p) for p in world])
    A=np.column_stack([points[1]-points[0],points[2]-points[0]])
    if abs(np.linalg.det(A))<1e-8:continue
    uv=np.linalg.solve(A,stock_px-points[0]);w=np.array([1-uv.sum(),*uv])
    if np.all(w>=0):candidates=[w]
    else:
        candidates=[]
        for k,l in ((0,1),(1,2),(2,0)):
            d=points[l]-points[k];s=np.clip(np.dot(stock_px-points[k],d)/max(np.dot(d,d),1e-12),0,1)
            ww=np.zeros(3);ww[k]=1-s;ww[l]=s;candidates.append(ww)
    for w in candidates:
        hit=w@world;distance=float(np.linalg.norm(w@points-stock_px))
        rank=(round(distance,6),-hit[2])
        if best is None or rank<best[0]:best=(rank,i,w@t,hit,w)
assert best and best[0][0]<15,('Marked point misses actual stock',None if best is None else best[0])
stock_world=best[3];pivot=np.array(tm.point(gun,fit['blade_gun_cm']))
target=stock_world+(palm_px-project(stock_world))[0]*width/1600*right-(palm_px-project(stock_world))[1]*width/1600*up
v=stock_world-pivot;w=target-pivot
vflat=v-axis*np.dot(axis,v);wflat=w-axis*np.dot(axis,w)
assert min(np.linalg.norm(vflat),np.linalg.norm(wflat))>.1
angle=math.atan2(np.dot(axis,np.cross(vflat,wflat)),np.dot(vflat,wflat))
assert abs(math.degrees(angle))<=45,('Rotation exceeds plan',math.degrees(angle))
q=[*(axis*math.sin(angle/2)),math.cos(angle/2)]
new_gun={'t':(pivot+np.array(tm.rotate(q,np.array(gun['t'])-pivot))).tolist(),'q':tm.qmul(q,gun['q']),'s':gun['s']}
new_stock=np.array(tm.point(new_gun,best[2]));new_pivot=tm.point(new_gun,fit['blade_gun_cm'])
before_dist=float(np.linalg.norm(project(stock_world)-palm_px)*width/1600)
after_dist=float(np.linalg.norm(project(new_stock)-palm_px)*width/1600)
assert after_dist<before_dist and math.dist(pivot,new_pivot)<1e-8
H=r['after']['bones']['hand_r']
hand_relative={'t':tm.inverse_point(H,gun['t']),'q':tm.qmul(tm.qinv(H['q']),gun['q']),'s':gun['s']}
payload={'status':'one_marked_trigger_pivot_rotation','guards':618,'v1_result':row(V1/'result.json'),
    'v1_landmarks':row(BASE/'marked_landmarks_v1/result.json'),'model':row(GLB),'marking_sha256':sha(MARK),
    'registration_user_to_native':par.tolist(),'registration_gray_rms':rms,'native_import_bounds_error_cm':bounds_error,
    'camera':camera,'camera_right':right.tolist(),'camera_up':up.tolist(),'manual_stock_pixel':[213,177],
    'manual_palm_pixel':[249,190],'native_stock_pixel':stock_px.tolist(),'native_palm_pixel':palm_px.tolist(),
    'actual_stock_projected':project(stock_world).tolist(),'stock_surface_triangle':best[1],
    'stock_surface_barycentric':best[4].tolist(),'stock_surface_screen_error_px':best[0][0],
    'stock_gun_cm':best[2].tolist(),'pivot_gun_cm':fit['blade_gun_cm'],'pivot_world_cm':pivot.tolist(),
    'axis_world':axis.tolist(),'axis_hand':tm.rotate(tm.qinv(H['q']),axis.tolist()),'angle_deg':math.degrees(angle),
    'source_gun_world':gun,'source_hand_world':H,'v1_gun_hand_relative':hand_relative,
    'new_gun_world':new_gun,'stock_target_world_cm':target.tolist(),
    'stock_screen_gap_before_cm':before_dist,'stock_screen_gap_after_cm':after_dist,
    'radial_mismatch_cm':float(abs(np.linalg.norm(vflat)-np.linalg.norm(wflat))),
    'depth':'Top-plane target retains stock height; no inferred palm skin depth or complete grip acceptance',
    'all_bones_fixed':True,'contact_accepted':False}
assert guards()==618
write(OUT/'result.json',payload)
print(json.dumps({k:payload[k] for k in ('status','registration_gray_rms','native_import_bounds_error_cm','stock_surface_screen_error_px','angle_deg','stock_screen_gap_before_cm','stock_screen_gap_after_cm','radial_mismatch_cm')}))
