"""Separate audit path: source/blend/reproduction/fresh GLB corner identity."""
import argparse,hashlib,json,sys,struct
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import INPUT

def snapshot():
    data=[]
    for o in sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.polygons),reverse=True):
        m=o.data
        data.append({'pos':np.array([tuple(o.matrix_world@v.co) for v in m.vertices],dtype=np.float32),
                     'ff':np.array([tuple(p.vertices) for p in m.polygons]),
                     'uv':np.array([tuple(u.uv) for u in m.uv_layers.active.data],dtype=np.float32).reshape(-1,3,2),
                     'norm':np.array([tuple(n.vector) for n in m.corner_normals],dtype=np.float32).reshape(-1,3,3),
                     'materials':[ma.name for ma in m.materials]})
    images=sorted(hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.packed_file)
    return data,images

def canonical(d,normal=False):
    q=np.concatenate((d['pos'][d['ff']],d['uv']),axis=2)
    if normal:q=np.concatenate((q,d['norm']),axis=2)
    pts=q[:,:,:3];first=np.zeros(len(q),int)
    for c in (1,2):
        pr=pts[np.arange(len(q)),first];n=pts[:,c]
        less=(n[:,0]<pr[:,0])|((n[:,0]==pr[:,0])&(n[:,1]<pr[:,1]))|((n[:,0]==pr[:,0])&(n[:,1]==pr[:,1])&(n[:,2]<pr[:,2]))
        first[less]=c
    q=q[np.arange(len(q))[:,None],(first[:,None]+np.arange(3))%3]
    keys=[q[:,c,i] for c,i in reversed([(c,i) for c in range(3) for i in range(5)])]
    return q[np.lexsort(keys)]

def raw_glb(path):
    raw=path.read_bytes();jslen=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+jslen]);start=20+jslen
    binlen=struct.unpack_from('<I',raw,start)[0];payload=raw[start+8:start+8+binlen]
    def access(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
        dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']]
        cols={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];dtype=np.dtype(dt)
        offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',cols*dtype.itemsize)
        return np.ndarray((a['count'],cols),dtype=dtype,buffer=payload,offset=offset,strides=(stride,dtype.itemsize)).copy()
    rows=[]
    for m in doc['meshes']:
        assert len(m['primitives'])==1
        pr=m['primitives'][0];attr=pr['attributes'];pos=access(attr['POSITION']);ns=access(attr['NORMAL']);uv=access(attr['TEXCOORD_0'])
        ff=access(pr['indices']).reshape(-1,3).astype(int)
        pos=pos[:,[0,2,1]]*np.array([1,-1,1],np.float32);ns=ns[:,[0,2,1]]*np.array([1,-1,1],np.float32)
        # glTF UV V is flipped relative to Blender's corner UV.
        uv[:,1]=1-uv[:,1]
        rows.append({'pos':pos,'ff':ff,'uv':uv[ff],'norm':ns[ff]})
    return sorted(rows,key=lambda d:len(d['ff']),reverse=True)

p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--rerun',required=True);p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);dest=Path(a.output).resolve();assert not dest.exists()
bpy.ops.wm.open_mainfile(filepath=str(INPUT),load_ui=False,use_scripts=False);source,si=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate)/'Kar98k_Normals_V7.blend'),load_ui=False,use_scripts=False);auth,ai=snapshot()
assert len(source)==len(auth)==2 and si==ai
assert all(np.array_equal(s[k],t[k]) for s,t in zip(source,auth) for k in ('pos','ff','uv'))
assert all(s['materials']==t['materials'] for s,t in zip(source,auth))
assert np.array_equal(source[1]['norm'],auth[1]['norm'])
assert not np.array_equal(source[0]['norm'],auth[0]['norm'])
bpy.ops.wm.open_mainfile(filepath=str(Path(a.rerun)/'Kar98k_Normals_V7.blend'),load_ui=False,use_scripts=False);rep,ri=snapshot()
assert ri==ai and all(np.array_equal(s[k],t[k]) for s,t in zip(rep,auth) for k in ('pos','ff','uv','norm'))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(Path(a.candidate)/'Kar98k_Normals_V7.glb'));fresh,fi=snapshot()
assert fi==ai and len(fresh)==2
raw=raw_glb(Path(a.candidate)/'Kar98k_Normals_V7.glb')
checks=[]
for s,t,g in zip(auth,fresh,raw):
    x,y=canonical(s,True),canonical(t,True);assert x.shape==y.shape
    uvpos=float(np.abs(x[:,:,:5]-y[:,:,:5]).max());norm=float(np.abs(x[:,:,5:]-y[:,:,5:]).max())
    z=canonical(g,True);assert z.shape==x.shape
    rawuvpos=float(np.abs(x[:,:,:5]-z[:,:,:5]).max());rawnorm=float(np.abs(x[:,:,5:]-z[:,:,5:]).max())
    gn=z[:,:,5:].astype(np.float64);sn=x[:,:,5:].astype(np.float64)
    gc=(gn*sn).sum(axis=2)/(np.linalg.norm(gn,axis=2)*np.linalg.norm(sn,axis=2))
    rawangle=float(np.degrees(np.arccos(np.clip(gc,-1,1))).max())
    sample=np.unravel_index(np.abs(x[:,:,5:]-z[:,:,5:]).argmax(),x[:,:,5:].shape)[:2]
    diagnostic={'rawPositionUv':rawuvpos,'rawNormalMaxComponentError':rawnorm,'rawNormalMaxDegrees':rawangle,
                'sourceNormalAtMax':sn[sample].tolist(),'exportNormalAtMax':gn[sample].tolist(),
                'sourceNormalLengthAtMax':float(np.linalg.norm(sn[sample])),'exportNormalLengthAtMax':float(np.linalg.norm(gn[sample]))}
    print('NORMAL_PAYLOAD_DIAGNOSTIC '+json.dumps(diagnostic),flush=True)
    assert rawuvpos<=2e-7 and rawangle<=.01,('export angular payload',diagnostic)
    # Blender re-encodes imported custom corner normals internally. Diagnose
    # its display roundtrip independently from the actual float32 GLB payload.
    xn=x[:,:,5:].astype(np.float64);yn=y[:,:,5:].astype(np.float64)
    cosine=(xn*yn).sum(axis=2)/(np.linalg.norm(xn,axis=2)*np.linalg.norm(yn,axis=2))
    angles=np.degrees(np.arccos(np.clip(cosine,-1,1)));ma=float(angles.max())
    assert uvpos<=2e-7 and ma<=.3 and np.isfinite(y).all(),(uvpos,norm,ma)
    checks.append({'triangles':len(x),'positionUvMaxError':uvpos,'normalComponentMaxErrorFreshBlender':norm,
                   'freshBlenderNormalMaxDegrees':ma,'rawGlbNormalMaxError':rawnorm,'rawGlbNormalMaxDegrees':rawangle,
                   'rawGlbPositionUvMaxError':rawuvpos,'finite':True,'normalPayloadDiagnostic':diagnostic})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
g1=Path(a.candidate)/'Kar98k_Normals_V7.glb';g2=Path(a.rerun)/'Kar98k_Normals_V7.glb'
r={'allPass':True,'allVertexFaceCornerUvExactToV6':True,'allSourceImagesMaterialsExact':True,'slingNormalsExact':True,
   'independentCleanReproductionExact':True,'glbBytesReproduced':sha(g1)==sha(g2),'glbSha256':sha(g1),'freshImport':checks,
   'visualAcceptanceInferred':False,'wholeRifleFinished':False,'metalSelectionRejected':True}
assert r['glbBytesReproduced']
dest.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r),flush=True)
