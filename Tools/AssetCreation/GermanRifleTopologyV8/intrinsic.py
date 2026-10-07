"""Tutte disk proof of the unchanged region; no rifle geometry authoring."""
import collections,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import BASE,load
from interface import graph

def parameterize(m,r):
    pos,ff,gp,gf,groups,vg,adj,ef=graph(m)
    faces=gf[r['faces']];uids=sorted(set(faces.flatten().tolist()));lookup={u:i for i,u in enumerate(uids)}
    tris=np.array([[lookup[u] for u in f] for f in faces]);boundary=[lookup[u] for u in r['loop_groups']]
    counts=collections.Counter(tuple(sorted((int(a),int(b)))) for f in tris for a,b in zip(f,np.roll(f,-1)))
    expected={tuple(sorted((a,b))) for a,b in zip(boundary,boundary[1:]+boundary[:1])}
    assert set(e for e,n in counts.items() if n==1)==expected and all(n in (1,2) for n in counts.values())
    assert len(uids)-len(counts)+len(tris)==1
    local=[set() for _ in uids]
    for a,b in counts:local[a].add(b);local[b].add(a)
    todo=[0];seen={0}
    while todo:
        for v in local[todo.pop()]:
            if v not in seen:seen.add(v);todo.append(v)
    assert len(seen)==len(uids)
    pts=gp[uids];length=np.linalg.norm(np.roll(pts[boundary],-1,axis=0)-pts[boundary],axis=1)
    angles=np.concatenate([[0],np.cumsum(length[:-1])])/length.sum()*2*np.pi
    uv=np.zeros((len(uids),2));uv[boundary]=np.column_stack([np.cos(angles),np.sin(angles)])
    inside=sorted(set(range(len(uids)))-set(boundary));il={u:i for i,u in enumerate(inside)}
    matrix=np.zeros((len(inside),len(inside)));rhs=np.zeros((len(inside),2))
    for u,i in il.items():
        matrix[i,i]=len(local[u])
        for v in local[u]:
            if v in il:matrix[i,il[v]]=-1
            else:rhs[i]+=uv[v]
    uv[inside]=np.linalg.solve(matrix,rhs)
    a=uv[tris[:,1]]-uv[tris[:,0]];b=uv[tris[:,2]]-uv[tris[:,0]];areas=a[:,0]*b[:,1]-a[:,1]*b[:,0]
    assert np.min(np.abs(areas))>1e-10 and (np.all(areas>0) or np.all(areas<0)),('folded intrinsic domain',float(areas.min()),float(areas.max()))
    return {'source_groups':uids,'xyz':pts.tolist(),'uv':uv.tolist(),'triangles':tris.tolist(),'boundary':boundary,
            'boundary_xyz_max_difference_m':float(np.max(np.abs(pts[boundary]-np.array(r['boundary_xyz'])))),
            'euler':1,'manifold_disk':True,'consistent_orientation':True,'min_double_area':float(np.min(np.abs(areas))),
            'faces':len(tris),'vertices':len(uids),'edges':len(counts)}
if __name__=='__main__':
    out=BASE/'intrinsic_v1';out.mkdir(exist_ok=False)
    rifle,_=load();r=json.loads((BASE/'interface_v1/interface.json').read_text());d=parameterize(rifle.data,r)
    (out/'intrinsic.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k not in ('source_groups','xyz','uv','triangles','boundary')}),flush=True)
