"""Manually anchored original-edge loop. No face painting or station search."""
import argparse,collections,heapq,json,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,load,setup
# Traced on actual source top_detail. Conservative steel interior only;
# graph paths, NOT a pixel polygon deciding which faces to modify.
RECEIVER_LANDMARKS=[(486,381),(504,373),(577,373),(598,356),(624,344),(675,349),(692,363),(707,365),
                    (788,372),(794,440),(710,451),(695,450),(676,465),(626,466),(615,448),(597,426),(577,435),(498,435),(489,421)]
def graph(m):
    pos=np.array([tuple(v.co) for v in m.vertices]);ff=np.array([tuple(p.vertices) for p in m.polygons]);keys={};groups=[];vg=[]
    for i,q in enumerate(pos):
        k=tuple(np.round(q,7))
        if k not in keys:keys[k]=len(groups);groups.append([])
        g=keys[k];groups[g].append(i);vg.append(g)
    gp=np.array([pos[ids[0]] for ids in groups]);gf=np.array(vg)[ff];adj=[set() for _ in groups];ef=collections.defaultdict(list)
    for fi,tri in enumerate(gf):
        for u,v in zip(tri,np.roll(tri,-1)):
            u,v=int(u),int(v)
            if u==v:continue
            adj[u].add(v);adj[v].add(u);ef[tuple(sorted((u,v)))].append(fi)
    return pos,ff,gp,gf,groups,np.array(vg),adj,ef
def pick(tree,m,c,px,py):
    r=c.rotation_euler.to_matrix();sc=c.data.ortho_scale
    origin=c.location+r@Vector(((px/1600-.5)*sc,(.5-py/900)*sc*900/1600,0))
    h,n,fi,d=tree.ray_cast(origin,r@Vector((0,0,-1)))
    assert h is not None,('landmark missed',px,py)
    vi=min(m.polygons[fi].vertices,key=lambda v:(m.vertices[v].co-h).length)
    return vi,{'pixel':[px,py],'point':list(h),'face':fi,'vertex':vi}
def prove(rifle,cams):
    m=rifle.data;pos,ff,gp,gf,groups,vg,adj,ef=graph(m)
    tree=BVHTree.FromPolygons([v.co for v in m.vertices],[p.vertices for p in m.polygons],all_triangles=True)
    pairs=[pick(tree,m,cams['top_detail'],*pt) for pt in RECEIVER_LANDMARKS];anchors=[int(vg[vi]) for vi,_ in pairs]
    assert len(set(anchors))==len(anchors),'duplicate manually picked anchors'
    used=set();paths=[]
    for i,a in enumerate(anchors):
        b=anchors[(i+1)%len(anchors)];blocked=(used|set(anchors))-{a,b};p0,p1=gp[a],gp[b];axis=p1-p0;aa=float(axis@axis)
        heap=[(0.,a)];cost={a:0.};parent={}
        while heap:
            g,u=heapq.heappop(heap)
            if g>cost[u]+1e-12:continue
            if u==b:break
            for v in sorted(adj[u]):
                if v in blocked:continue
                mid=(gp[u]+gp[v])*.5;t=np.clip(((mid-p0)@axis)/aa,0,1);dev=float(np.linalg.norm(mid-p0-t*axis))
                ng=g+float(np.linalg.norm(gp[v]-gp[u]))*(1+dev/.0008)
                if ng<cost.get(v,float('inf')):cost[v]=ng;parent[v]=u;heapq.heappush(heap,(ng,v))
        assert b in cost,('disconnected ordered landmarks',i)
        path=[b];u=b
        while u!=a:u=parent[u];path.append(u)
        path.reverse();paths.append(path);used.update(path)
    loop=[u for p in paths for u in p[:-1]];assert len(loop)==len(set(loop))
    barrier={tuple(sorted((int(u),int(v)))) for u,v in zip(loop,loop[1:]+loop[:1])}
    degree=collections.Counter(i for e in barrier for i in e);assert all(v==2 for v in degree.values())
    _,seedrow=pick(tree,m,cams['top_detail'],650,410);seed=seedrow['face'];sel={seed};todo=[seed]
    while todo:
        fi=todo.pop()
        for u,v in zip(gf[fi],np.roll(gf[fi],-1)):
            e=tuple(sorted((int(u),int(v))))
            if e in barrier:continue
            for nb in ef[e]:
                if nb not in sel:sel.add(nb);todo.append(nb)
    ball=set(json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/boundary_v1b/surface_selection.json').read_text())['faces'])
    assert 500<len(sel)<40000 and not(sel&ball),('bad local flood',len(sel),len(sel&ball))
    # Each original loop edge must separate one selected and one retained face.
    failures=[list(e) for e in barrier if sum(fi in sel for fi in ef[e])!=1 or sum(fi not in sel for fi in ef[e])!=1]
    result={'faces':sorted(sel),'loop_groups':loop,'loop_source_vertices':[groups[g][0] for g in loop],
            'boundary_xyz':gp[loop].tolist(),'landmarks':[r for _,r in pairs],'seed':seedrow,
            'simpleConnectedLoop':True,'edgeCount':len(barrier),'boundaryPairFailures':failures,
            'ballFacesExcluded':True,'coincidentDiagnosticToleranceM':1e-7,'screenFacePaint':False}
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    rifle,meshes=load();s,cams=setup();r=prove(rifle,cams)
    (out/'interface.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
    grey=bpy.data.materials.new('RetainedOriginal');grey.diffuse_color=(.5,.52,.55,1);cyan=bpy.data.materials.new('ClosedEdgeReceiverPatch');cyan.diffuse_color=(.03,.65,.85,1)
    rifle.data.materials.clear();rifle.data.materials.append(grey);rifle.data.materials.append(cyan)
    for fi in r['faces']:rifle.data.polygons[fi].material_index=1
    s.display.shading.color_type='MATERIAL'
    for n in ('right_detail','left_detail','top_detail','quarter','reverse'):
        s.camera=cams[n];s.render.filepath=str(out/('proof_'+n+'.png'));bpy.ops.render.render(write_still=True)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'ReceiverInterfaceProof.blend'))
    print(json.dumps({'faces':len(r['faces']),'edges':r['edgeCount'],'pairFailures':len(r['boundaryPairFailures'])}),flush=True)
    assert not r['boundaryPairFailures'],'source boundary pairing failure'
