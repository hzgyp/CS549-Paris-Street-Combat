"""Read-only V12 UV ownership and real edge inspection; no source save."""
import sys, argparse, json, importlib.util
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-m1-texture-v12/finish_v1'
def module(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
W=module('wear_base',Path(__file__).parents[1]/'GermanRifleSPR_v11/main.py')
PIVOT=Vector(json.loads((BASE/'build_report.json').read_text())['pivot_shift'])

def raster(obj, faces, size):
    """UV pixel-center barycentrics; overlap conflicts compare actual surface positions."""
    width,height=(size,size) if isinstance(size,int) else size
    extent=np.array((width,height))
    me=obj.data;me.calc_loop_triangles()
    xyz=np.full((height,width,3),np.nan,np.float32)
    ids=np.full((height,width),-1,np.int32)
    conflict=np.zeros((height,width),bool)
    verts=np.array([tuple(obj.matrix_world@v.co+PIVOT) for v in me.vertices])
    uv=np.array([tuple(v.uv) for v in me.uv_layers.active.data])
    for tri in me.loop_triangles:
        if tri.polygon_index not in faces:continue
        t=uv[list(tri.loops)]
        if t.min() < -1e-6 or t.max()>1+1e-6:continue
        lo=np.maximum(0,np.floor(t.min(0)*extent-.5).astype(int));hi=np.minimum(extent-1,np.ceil(t.max(0)*extent-.5).astype(int))
        if np.any(hi<lo):continue
        x,y=np.meshgrid((np.arange(lo[0],hi[0]+1)+.5)/width,(np.arange(lo[1],hi[1]+1)+.5)/height)
        den=(t[1,1]-t[2,1])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,1]-t[2,1])
        if abs(den)<1e-15:continue
        a=((t[1,1]-t[2,1])*(x-t[2,0])+(t[2,0]-t[1,0])*(y-t[2,1]))/den
        b=((t[2,1]-t[0,1])*(x-t[2,0])+(t[0,0]-t[2,0])*(y-t[2,1]))/den
        c=1-a-b;mask=(a>=-1e-7)&(b>=-1e-7)&(c>=-1e-7)
        pos=a[...,None]*verts[tri.vertices[0]]+b[...,None]*verts[tri.vertices[1]]+c[...,None]*verts[tri.vertices[2]]
        region=xyz[lo[1]:hi[1]+1,lo[0]:hi[0]+1];ri=ids[lo[1]:hi[1]+1,lo[0]:hi[0]+1]
        both=mask&(ri>=0)
        conflict[lo[1]:hi[1]+1,lo[0]:hi[0]+1] |= both & (np.linalg.norm(region-pos,axis=2)>.001)
        region[mask]=pos[mask];ri[mask]=tri.polygon_index
    return xyz,ids,conflict

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    out=Path(a.out);assert not out.exists();out.mkdir(parents=True)
    source=BASE/'GermanRifle_M1Texture_V12.blend';guard=W.sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    rows={}
    for ob in sorted([o for o in bpy.context.scene.objects if o.type=='MESH'],key=lambda o:o.name):
        me=ob.data;uv=np.array([tuple(u.uv) for u in me.uv_layers.active.data]);v=np.array([tuple(ob.matrix_world@x.co+PIVOT) for x in me.vertices])
        mats=[]
        for i,slot in enumerate(ob.material_slots):
            faces={p.index for p in me.polygons if p.material_index==i}
            _,ids,c=raster(ob,faces,256)
            mats.append({'slot':i,'name':slot.material.name,'faces':len(faces),'occupied':int((ids>=0).sum()),'conflicting_pixels':int(c.sum()),
                         'images':{n.image.name:list(n.image.size) for n in slot.material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}})
        row={'vertices':len(me.vertices),'faces':len(me.polygons),'bounds_design':[v.min(0).tolist(),v.max(0).tolist()],
             'uv_range':[uv.min(0).tolist(),uv.max(0).tolist()],'materials':mats}
        if ob.name.startswith('Wood_'):
            caps=[p.index for p in me.polygons if len(p.vertices)>4]
            side=set(range(len(me.polygons)))-set(caps)
            _,ids,c=raster(ob,side,512)
            row['side_conflicts_512']=int(c.sum());row['cap_faces']=[{'id':i,'normal':list(me.polygons[i].normal),'center':list(ob.matrix_world@me.polygons[i].center+PIVOT)} for i in caps]
            # Actual first ring ordered points; use these to select continuous exposed ridge chains.
            n=len(me.polygons[caps[0]].vertices);row['ring_count']=n
            ring=v[:n];row['first_ring']=[{'j':j,'co':list(pt)} for j,pt in enumerate(ring)]
            row['mid_ring']=[{'j':j,'co':list(pt)} for j,pt in enumerate(v[(len(v)//n//2)*n:(len(v)//n//2+1)*n])]
            # Adjacency/convexity uses real polygon normals and centers, never UV edges.
            edges={tuple(sorted(e.vertices)):[] for e in me.edges}
            for f in me.polygons:
                for e in f.edge_keys:edges[tuple(sorted(e))].append(f.index)
            proof=[]
            for key,adj in edges.items():
                if len(adj)!=2:continue
                f,g=[me.polygons[i] for i in adj]
                angle=float(f.normal.angle(g.normal))
                convex=float(f.normal.dot(g.center-f.center)) < -1e-7
                if caps[0] in adj and convex:proof.append({'edge':list(key),'faces':adj,'angle_rad':angle,'convex':True})
            row['butt_cap_convex_edges']=proof
        rows[ob.name]=row
    report={'stage':'read_only_preflight','blender':bpy.app.version_string,'source_sha256':guard,'geometry':W.geometry_fingerprint(),'objects':rows}
    assert W.sha(source)==guard
    (out/'preflight.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:{'uv':v['uv_range'],'conflicts':[m['conflicting_pixels'] for m in v['materials']], 'side_conflicts':v.get('side_conflicts_512'),'caps':v.get('cap_faces')} for k,v in rows.items()}),flush=True)
if __name__=='__main__':main()
