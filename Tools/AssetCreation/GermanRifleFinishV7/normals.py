"""Physical surface adjacency normal repair; no position/UV/topology changes."""
import argparse,collections,json,math,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import load,setup,pbr,save_export

def repair(m):
    pos=np.array([tuple(v.co) for v in m.vertices]);ff=np.array([tuple(p.vertices) for p in m.polygons]);before=np.array([tuple(n.vector) for n in m.corner_normals])
    _,vg=np.unique(np.round(pos,7),axis=0,return_inverse=True)
    # Face area weights with angular filtering: no actual welding. For a corner,
    # only incident faces within the original local45-degree crease may average.
    cross=np.cross(pos[ff[:,1]]-pos[ff[:,0]],pos[ff[:,2]]-pos[ff[:,0]]);area=np.linalg.norm(cross,axis=1)
    fn=cross/np.maximum(area[:,None],1e-20);incident=collections.defaultdict(list)
    for fi,ids in enumerate(vg[ff]):
        for corner,g in enumerate(ids):incident[int(g)].append((fi,corner))
    cn=np.empty((len(ff),3,3));limit=math.cos(math.radians(45));changed=0
    for rows in incident.values():
        ids=np.array([r[0] for r in rows]);n=fn[ids];weights=area[ids]
        coherent=n@n.T>=limit
        av=coherent@(n*weights[:,None]);av/=np.maximum(np.linalg.norm(av,axis=1)[:,None],1e-20)
        for (fi,corner),v in zip(rows,av):cn[fi,corner]=v
    normals=cn.reshape(-1,3);dot=np.clip((normals*before).sum(axis=1),-1,1);ang=np.degrees(np.arccos(dot))
    m.normals_split_custom_set([tuple(n) for n in normals]);m.update()
    return {'loops':len(normals),'normalDifferenceMedianDegrees':float(np.median(ang)),'normalDifference95Degrees':float(np.percentile(ang,95)),
            'positionTopologyUvChange':False,'creasesDegrees':45,'diagnosticGroupingToleranceM':1e-7}

p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
rifle,meshes=load();s,cams=setup()
for n in ('quarter','top_detail','whole_right'):
    s.camera=cams[n];s.render.filepath=str(out/('before_clay_'+n+'.png'));bpy.ops.render.render(write_still=True)
stats=repair(rifle.data)
for n,c in cams.items():s.camera=c;s.render.filepath=str(out/('after_clay_'+n+'.png'));bpy.ops.render.render(write_still=True)
save_export(meshes,out,'Kar98k_Normals_V7')
(out/'normal_diagnostic.json').write_text(json.dumps(stats,indent=2),encoding='utf-8');print(json.dumps(stats),flush=True)
