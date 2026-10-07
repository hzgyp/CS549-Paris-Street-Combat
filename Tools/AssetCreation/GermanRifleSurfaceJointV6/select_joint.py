"""Ray-picked physical surface ring, edge-path separation and face flood."""
import argparse, collections, heapq, json, math, sys
from pathlib import Path
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe import load, camera, setup

def selection(rifle, joint='ball'):
    m=rifle.data; pos=np.array([tuple(v.co) for v in m.vertices]); faces=np.array([tuple(p.vertices) for p in m.polygons])
    # Geometric adjacency across duplicate UV indices only; no mutation or weld.
    keys={};groups=[];vg=[]
    for i,q in enumerate(pos):
        key=tuple(np.round(q,7))
        if key not in keys:keys[key]=len(groups);groups.append([])
        g=keys[key];groups[g].append(i);vg.append(g)
    gp=np.array([pos[ii].mean(axis=0) for ii in groups]);gf=np.array(vg)[faces]
    adj=[set() for _ in groups];ef=collections.defaultdict(list)
    for fi,ff in enumerate(gf):
        for u,v in zip(ff,np.roll(ff,-1)):
            u=int(u);v=int(v)
            if u==v:continue
            adj[u].add(v);adj[v].add(u);ef[tuple(sorted((u,v)))].append(fi)
    tree=BVHTree.FromPolygons([v.co for v in m.vertices],[p.vertices for p in m.polygons],all_triangles=True)
    # Cross-section through the visibly narrow neck above the knob. These
    # locate 16 actual ray hits, never classify material by a volume envelope.
    center=Vector((-.1545,-.0465,.0878) if joint=='ball' else (-.154,-.0255,.105))
    axis=Vector((0,.62,.785) if joint=='ball' else (0,.70,.714)).normalized()
    ex=Vector((1,0,0));ez=axis.cross(ex).normalized();anchors=[];hits=[]
    for i in range(16):
        d=ex*math.cos(i*2*math.pi/16)+ez*math.sin(i*2*math.pi/16)
        h,n,fi,dist=tree.ray_cast(center+d*.026,-d,.026)
        assert h is not None, ('missing neck ray',i)
        verts=list(m.polygons[fi].vertices);vi=min(verts,key=lambda v:(m.vertices[v].co-h).length)
        anchors.append(vg[vi]);hits.append({'ray':i,'face':fi,'vertex':vi,'point':list(h),'normal':list(n)})
    def shortest(start,end):
        # Local surface shortest edge path. Penalize straying from the observed
        # ring station; forbidden from substituting a bounding-box selection.
        todo=[(0.,0.,start)];cost={start:0.};parent={};ax=np.array(axis);ctr=np.array(center)
        while todo:
            _,g,u=heapq.heappop(todo)
            if g>cost[u]+1e-12:continue
            if u==end:
                path=[u]
                while u!=start:u=parent[u];path.append(u)
                return path[::-1]
            for v in sorted(adj[u]):
                edge=float(np.linalg.norm(gp[v]-gp[u]))
                station=abs(float(np.dot((gp[v]+gp[u])*.5-ctr,ax)))
                ng=g+edge*(1+station/.0005)
                if ng<cost.get(v,float('inf')):
                    cost[v]=ng;parent[v]=u
                    heapq.heappush(todo,(ng+float(np.linalg.norm(gp[v]-gp[end])),ng,v))
        raise RuntimeError('disconnected surface landmarks')
    paths=[shortest(anchors[i],anchors[(i+1)%16]) for i in range(16)]
    barrier={tuple(sorted((u,v))) for path in paths for u,v in zip(path,path[1:])}
    degree=collections.Counter(i for e in barrier for i in e)
    assert all(d==2 for d in degree.values()), ('not simple closed surface ring',collections.Counter(degree.values()))
    # Original visible ball-front face from probe_v1 is the flood seed.
    seed=124203;selected={seed};todo=[seed]
    while todo:
        fi=todo.pop()
        for u,v in zip(gf[fi],np.roll(gf[fi],-1)):
            edge=tuple(sorted((int(u),int(v))))
            if edge in barrier:continue
            for nb in ef[edge]:
                if nb not in selected:selected.add(nb);todo.append(nb)
    assert 200<len(selected)<6000, ('ring failed to isolate small handle surface',len(selected))
    selected_vertices=set(int(i) for i in faces[sorted(selected)].ravel())
    boundary_groups=set(degree);boundary_vertices={i for g in boundary_groups for i in groups[g]}
    # Lock any selected coordinate with an incident unselected face as well.
    incident=[set() for _ in groups]
    for fi,ff in enumerate(gf):
        for g in ff:incident[int(g)].add(fi)
    unlocked={g for g in range(len(groups)) if incident[g] and incident[g].issubset(selected) and g not in boundary_groups}
    return {'faces':sorted(selected),'boundary_edges':[list(e) for e in sorted(barrier)],'boundary_groups':sorted(boundary_groups),
            'boundary_vertices':sorted(boundary_vertices),'selected_vertices':sorted(selected_vertices),'editable_groups':sorted(unlocked),
            'landmarks':hits,'seed_face':seed,'diagnostic_coincident_tolerance_m':1e-7},(pos,faces,gp,groups,gf,adj)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--joint',choices=['ball','root'],default='ball')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    rifle,meshes=load();proof,data=selection(rifle,a.joint)
    base=bpy.data.materials.new('OriginalSurfaceGrey');base.diffuse_color=(.53,.55,.58,1)
    highlight=bpy.data.materials.new('RayPickedBallSurface');highlight.diffuse_color=(.03,.6,.9,1)
    m=rifle.data;m.materials.clear();m.materials.append(base);m.materials.append(highlight)
    for fi in proof['faces']:m.polygons[fi].material_index=1
    s=setup()
    for n,e,t,scale in [('side',(-.15,-2,.075),(-.15,-.035,.075),.16),('top',(-.15,-.035,2),(-.15,-.035,.075),.16),
                        ('quarter',(.1,-1,.7),(-.1,0,.075),.46),('underside',(-.3,-.4,-.1),(-.15,-.035,.075),.18)]:
        s.camera=camera(n,e,t,scale);s.render.filepath=str(out/('selection_'+n+'.png'));bpy.ops.render.render(write_still=True)
    (out/'surface_selection.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'SurfaceBoundaryProof.blend'))
    print(json.dumps({'faces':len(proof['faces']),'closed_ring_edges':len(proof['boundary_edges']),'selected_bounds':[data[0][proof['selected_vertices']].min(axis=0).tolist(),data[0][proof['selected_vertices']].max(axis=0).tolist()]}),flush=True)
