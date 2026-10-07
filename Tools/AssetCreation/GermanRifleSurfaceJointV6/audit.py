"""Independent source/blend/fresh-GLB semantic audit; no visual-pass inference."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe import load,ROOT

def snapshot():
    meshes=sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:len(o.data.polygons),reverse=True)
    data=[]
    for o in meshes:
        m=o.data;pos=np.array([tuple(o.matrix_world@v.co) for v in m.vertices],dtype=np.float32)
        ff=np.array([tuple(p.vertices) for p in m.polygons]);uv=np.array([tuple(v.uv) for v in m.uv_layers.active.data],dtype=np.float32).reshape(-1,3,2)
        data.append({'pos':pos,'faces':ff,'uv':uv,'materials':[mat.name for mat in m.materials]})
    images=sorted(hashlib.sha256(bytes(im.packed_file.data)).hexdigest() for im in bpy.data.images if im.packed_file)
    return data,images

def corners(d):
    q=np.concatenate((d['pos'][d['faces']],d['uv']),axis=2)
    # Canonicalize cyclic triangle corner order, without reversing winding.
    pts=q[:,:,:3];first=np.zeros(len(q),dtype=int)
    for c in (1,2):
        prev=pts[np.arange(len(q)),first];n=pts[:,c]
        less=(n[:,0]<prev[:,0])|((n[:,0]==prev[:,0])&(n[:,1]<prev[:,1]))|((n[:,0]==prev[:,0])&(n[:,1]==prev[:,1])&(n[:,2]<prev[:,2]))
        first[less]=c
    q=q[np.arange(len(q))[:,None],(first[:,None]+np.arange(3))%3].reshape(-1,15)
    keys=[q[:,i] for i in reversed([0,1,2,5,6,7,10,11,12,3,4,8,9,13,14])]
    return q[np.lexsort(keys)]

p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--rerun',required=True);p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);dest=Path(a.output).resolve();assert not dest.exists()
load();source,srcimages=snapshot()
proof=json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/boundary_v1b/surface_selection.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(Path(a.candidate)/'Kar98k_JointRepair_V6.blend'),load_ui=False,use_scripts=False);auth,images=snapshot()
assert len(source)==len(auth)==2
delta=np.linalg.norm(auth[0]['pos']-source[0]['pos'],axis=1);changed=set(np.where(delta>0)[0]);allowed=set(proof['selected_vertices']);boundary=set(proof['boundary_vertices'])
assert changed and changed.issubset(allowed) and not changed.intersection(boundary)
assert float(delta.max())<=.0015+2e-8 and np.array_equal(auth[1]['pos'],source[1]['pos'])
assert all(np.array_equal(s['faces'],t['faces']) and np.array_equal(s['uv'],t['uv']) for s,t in zip(source,auth))
assert images==srcimages
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(Path(a.candidate)/'Kar98k_JointRepair_V6.glb'));fresh,frimages=snapshot()
comparisons=[]
for x,y in zip(auth,fresh):
    ca,cb=corners(x),corners(y);assert ca.shape==cb.shape
    err=np.abs(ca-cb);assert err.max()<=2e-7, ('fresh corner position/UV mismatch',float(err.max()))
    comparisons.append({'triangles':len(ca),'cornerPositionUvMaxError':float(err.max()),'finite':bool(np.isfinite(cb).all())})
assert frimages==images
bpy.ops.wm.open_mainfile(filepath=str(Path(a.rerun)/'Kar98k_JointRepair_V6.blend'),load_ui=False,use_scripts=False);repeat,rimages=snapshot()
exact=all(np.array_equal(x['pos'],y['pos']) and np.array_equal(x['faces'],y['faces']) and np.array_equal(x['uv'],y['uv']) and x['materials']==y['materials'] for x,y in zip(auth,repeat))
assert exact and rimages==images
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
glb1=Path(a.candidate)/'Kar98k_JointRepair_V6.glb';glb2=Path(a.rerun)/'Kar98k_JointRepair_V6.glb'
r={'allPass':True,'sourceFacesUvExact':True,'unselectedWoodSlingAndBoundaryVerticesExact':True,
   'changedVertices':len(changed),'maxDisplacementM':float(delta.max()),'sourceOwnImagesExact':True,
   'freshImport':comparisons,'independentRerunGeometryUvMaterialExact':exact,'glbBytesReproduced':sha(glb1)==sha(glb2),
   'atlasSha256':images,'productionAccepted':False,'visualPassInferred':False,
   'unresolved':['root boundary not proved; no material repair','receiver/sights remain soft','complete articulated bolt missing','historical variant/UE/performance untested']}
dest.write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r),flush=True)
