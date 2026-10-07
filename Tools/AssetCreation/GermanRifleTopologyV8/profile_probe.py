"""Early projection and source-profile measurements, no authoring."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import BASE,load
rifle,_=load();m=rifle.data
r=json.loads((BASE/'interface_v1/interface.json').read_text())
b=np.array(r['boundary_xyz']);p=b[:,:2]
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def intersect(a,b,c,d):
    ab=b-a;cd=d-c
    return cross(ab,c-a)*cross(ab,d-a)<-1e-20 and cross(cd,a-c)*cross(cd,b-c)<-1e-20
bad=[]
for i in range(len(p)):
    for j in range(i+2,len(p)):
        if i==0 and j==len(p)-1:continue
        if intersect(p[i],p[(i+1)%len(p)],p[j],p[(j+1)%len(p)]):bad.append([i,j])
area=sum(cross(a,z) for a,z in zip(p,np.roll(p,-1,axis=0)))/2
ids=sorted({v for fi in r['faces'] for v in m.polygons[fi].vertices});q=np.array([tuple(m.vertices[v].co) for v in ids])
rows=[]
for x in np.arange(q[:,0].min()+.002,q[:,0].max(),.004):
    ss=q[abs(q[:,0]-x)<.002]
    if len(ss)<5:continue
    y,z=ss[:,1],ss[:,2];a=np.column_stack([2*y,2*z,np.ones(len(y))]);rhs=y*y+z*z
    c=np.linalg.lstsq(a,rhs,rcond=None)[0];rad=np.sqrt(max(0,c[2]+c[0]**2+c[1]**2))
    resid=np.sqrt((y-c[0])**2+(z-c[1])**2)-rad
    rows.append({'x':float(x),'n':len(ss),'centerY':float(c[0]),'centerZ':float(c[1]),'radius':float(rad),'rms':float(np.sqrt(np.mean(resid**2))),'min':ss.min(axis=0).tolist(),'max':ss.max(axis=0).tolist()})
out={'projectionCrossings':bad,'area':float(area),'bounds':[q.min(axis=0).tolist(),q.max(axis=0).tolist()],'sections':rows}
assert not (BASE/'profile_measurements.json').exists()
(BASE/'profile_measurements.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out),flush=True)
assert not bad and abs(area)>1e-6,'projection not usable'
