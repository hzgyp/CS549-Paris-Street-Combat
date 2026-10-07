"""Inventory exact cross-section loops after the single-loop assumption failed."""
import collections,json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from seam import load,BASE,CUT_X
rifle,_=load();pts=np.array([tuple(v.co) for v in rifle.data.vertices]);keys={};vv=[];adj=collections.defaultdict(set)
for p in rifle.data.polygons:
    q=pts[list(p.vertices)]
    if q[:,0].min()>=CUT_X or q[:,0].max()<=CUT_X:continue
    ids=[]
    for a,b in zip(q,np.roll(q,-1,axis=0)):
        if (a[0]-CUT_X)*(b[0]-CUT_X)<0:
            z=a+(CUT_X-a[0])/(b[0]-a[0])*(b-a);k=tuple(np.round(z,7))
            if k not in keys:keys[k]=len(vv);vv.append(z.tolist())
            ids.append(keys[k])
    assert len(ids)==2;a,b=ids;adj[a].add(b);adj[b].add(a)
todo=set(adj);rows=[]
while todo:
    first=min(todo);loop=[first];prev=-1;cur=first
    while True:
        assert len(adj[cur])==2
        nb=next(v for v in sorted(adj[cur]) if v!=prev)
        if nb==first:break
        assert nb not in loop;loop.append(nb);prev,cur=cur,nb
    todo-=set(loop);q=np.array(vv)[loop];c=q[:,1:].mean(axis=0);rad=np.linalg.norm(q[:,1:]-c,axis=1)
    rows.append({'edges':len(loop),'center_yz':c.tolist(),'radius_min_max': [float(rad.min()),float(rad.max())],'bounds':[q.min(axis=0).tolist(),q.max(axis=0).tolist()],'xyz':q.tolist()})
d={'failed_single_loop_assumption':True,'cut_x_m':CUT_X,'components':rows,'authoring':False}
out=BASE/'seam_diagnosis.json';assert not out.exists();out.write_text(json.dumps(d,indent=2));print(json.dumps([{k:v for k,v in r.items() if k!='xyz'} for r in rows]),flush=True)
