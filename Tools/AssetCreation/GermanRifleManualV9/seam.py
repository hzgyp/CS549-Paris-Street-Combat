"""Single author-chosen barrel seam; actual ordered contour, no hull/sweep."""
import argparse,collections,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-manual-v9'
INPUT=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-finish-v7/normals_v1/Kar98k_Normals_V7.blend'
CUT_X=.480
def load():
    inv=json.loads((ROOT/'Assets/Integration/GERMAN_RIFLE_FINISH_INVENTORY_20261003.json').read_text())
    row=next(r for r in inv['files'] if r['path']==INPUT.relative_to(ROOT).as_posix());assert hashlib.sha256(INPUT.read_bytes()).hexdigest()==row['sha256']
    bpy.ops.wm.open_mainfile(filepath=str(INPUT),load_ui=False,use_scripts=False)
    meshes=sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:len(o.data.polygons),reverse=True)
    return meshes[0],meshes
def proof(m):
    pts=np.array([tuple(v.co) for v in m.vertices]);edges={};vertices=[];adj=collections.defaultdict(set);selected=[]
    for p in m.polygons:
        v=pts[list(p.vertices)];side=v[:,0]-CUT_X
        if np.max(side)>0:selected.append(p.index)
        if np.min(side)>=0 or np.max(side)<=0:continue
        hits=[]
        for a,b in zip(v,np.roll(v,-1,axis=0)):
            if (a[0]-CUT_X)*(b[0]-CUT_X)<0:
                t=(CUT_X-a[0])/(b[0]-a[0]);q=a+t*(b-a);key=tuple(np.round(q,7))
                if key not in edges:edges[key]=len(vertices);vertices.append(q.tolist())
                hits.append(edges[key])
        assert len(hits)==2
        a,b=hits;adj[a].add(b);adj[b].add(a)
    degree=collections.Counter(len(z) for z in adj.values());assert set(degree)=={2},degree
    loop=[0];prev=-1;cur=0
    while True:
        nb=next(v for v in sorted(adj[cur]) if v!=prev)
        if nb==0:break
        assert nb not in loop;loop.append(nb);prev,cur=cur,nb
    assert len(loop)==len(vertices),('multiple components',len(loop),len(vertices))
    q=np.array(vertices)[loop];center=q[:,1:].mean(axis=0);angles=np.arctan2(q[:,2]-center[1],q[:,1]-center[0]);d=np.angle(np.exp(1j*(np.roll(angles,-1)-angles)))
    assert np.all(d>0) or np.all(d<0),'radial contour doubles back'
    if np.all(d<0):q=q[::-1]
    radius=np.linalg.norm(q[:,1:]-center,axis=1)
    assert .004<radius.min()<radius.max()<.020,('not barrel',float(radius.min()),float(radius.max()))
    r={'cut_x_m':CUT_X,'ordered_boundary_xyz':q.tolist(),'boundary_edges':len(q),'center_yz':center.tolist(),'radius_min_max_m':[float(radius.min()),float(radius.max())],
       'one_connected_degree2_loop':True,'radial_order_valid':True,'removed_front_face_count_including_split':len(selected),'source_faces':selected,
       'semantic_review_pending':True,'no_authoring':True}
    return r
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    rifle,meshes=load();r=proof(rifle.data);(out/'seam.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ('ordered_boundary_xyz','source_faces')}),flush=True)
