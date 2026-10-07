"""Bounded real-surface ball profile repair; original maps/materials retained."""
import argparse,hashlib,heapq,json,sys
from pathlib import Path
import bpy,numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from probe import load,ROOT

PROOF=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/boundary_v1b/surface_selection.json'
MAX_MOVE=.0015

def arr(m):
    return np.array([tuple(v.co) for v in m.vertices]),np.array([tuple(p.vertices) for p in m.polygons]),np.array([tuple(u.uv) for u in m.uv_layers.active.data])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    rifle,meshes=load();m=rifle.data;pos,faces,uv=arr(m)
    proof=json.loads(PROOF.read_text());selected=set(proof['faces']);keys={};groups=[];vg=[]
    for i,q in enumerate(pos):
        key=tuple(np.round(q,7))
        if key not in keys:keys[key]=len(groups);groups.append([])
        g=keys[key];groups[g].append(i);vg.append(g)
    gp=np.array([pos[ii].mean(axis=0) for ii in groups]);gf=np.array(vg)[faces]
    adjacent=[set() for _ in groups]
    for ff in gf[proof['faces']]:
        for u,v in zip(ff,np.roll(ff,-1)):
            if u!=v:adjacent[u].add(int(v));adjacent[v].add(int(u))
    distance={g:0. for g in proof['boundary_groups']};todo=[(0.,g) for g in distance];heapq.heapify(todo)
    while todo:
        d,u=heapq.heappop(todo)
        if d>distance[u]+1e-12:continue
        for v in adjacent[u]:
            nd=d+float(np.linalg.norm(gp[u]-gp[v]))
            if nd<distance.get(v,float('inf')):distance[v]=nd;heapq.heappush(todo,(nd,v))
    editable=set(proof['editable_groups'])
    fit_ids=[g for g in sorted(editable) if distance.get(g,0)>.005]
    q=gp[fit_ids];A=np.column_stack((2*q,np.ones(len(q))));b=(q*q).sum(axis=1)
    sol=np.linalg.lstsq(A,b,rcond=None)[0];center=sol[:3];radius=float(np.sqrt(sol[3]+np.dot(center,center)))
    assert .010<radius<.030, ('implausible source-fitted ball radius',radius)
    old_normals=np.array([tuple(n.vector) for n in m.corner_normals]);new_normals=old_normals.copy();weight={};newpos=pos.copy()
    for g in sorted(editable):
        t=min(1.,distance.get(g,0)/.005);w=t*t*(3-2*t);weight[g]=w
        delta=gp[g]-center;ideal=center+delta/np.linalg.norm(delta)*radius
        change=(ideal-gp[g])*w;length=float(np.linalg.norm(change))
        if length>MAX_MOVE:change*=MAX_MOVE/length
        for vi in groups[g]:newpos[vi]+=change;m.vertices[vi].co=newpos[vi]
    # Consistent smooth manufactured-ball normals, feathered into unchanged
    # source neck; no global smoothing of wood, UV weld or polygon replacement.
    for poly in m.polygons:
        if poly.index not in selected:continue
        for li in poly.loop_indices:
            vi=m.loops[li].vertex_index;g=vg[vi];w=weight.get(g,0)
            if not w:continue
            normal=newpos[vi]-center;normal/=np.linalg.norm(normal)
            n=old_normals[li]*(1-w)+normal*w;n/=np.linalg.norm(n);new_normals[li]=n
    m.normals_split_custom_set([tuple(n) for n in new_normals]);m.update()
    after,af,au=arr(m);moves=np.linalg.norm(after-pos,axis=1);changed=np.where(moves>0)[0]
    allowed={i for g in editable for i in groups[g]}
    assert set(changed).issubset(allowed) and moves.max()<=MAX_MOVE+2e-8
    assert np.array_equal(faces,af) and np.array_equal(uv,au)
    assert all(np.array_equal(after[i],pos[i]) for i in proof['boundary_vertices'])
    stats={'blender':bpy.app.version_string,'proofSha256':hashlib.sha256(PROOF.read_bytes()).hexdigest(),
           'selectedFaces':len(selected),'changedVertices':len(changed),'ballCenter':center.tolist(),'ballRadiusM':radius,
           'maxDisplacementM':float(moves.max()),'meanDisplacementM':float(moves[changed].mean()),
           'positionsSha256':hashlib.sha256(after.astype('<f4').tobytes()).hexdigest(),
           'sourcePositionsSha256':hashlib.sha256(pos.astype('<f4').tobytes()).hexdigest(),
           'facesSha256':hashlib.sha256(af.astype('<i4').tobytes()).hexdigest(),'uvSha256':hashlib.sha256(au.astype('<f4').tobytes()).hexdigest(),
           'woodAndUnselectedPositionsExact':True,'boundaryPositionsExact':True,'topologyUvExact':True,
           'materialChanges':False,'rootBoundary':'failed simple-ring gate; no material adaptation',
           'triangles':sum(len(o.data.polygons) for o in meshes),'visualAcceptance':'Requires inspected before/after views; not inferred'}
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'Kar98k_JointRepair_V6.blend'))
    bpy.ops.object.select_all(action='DESELECT')
    for o in meshes:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/'Kar98k_JointRepair_V6.glb'),export_format='GLB',use_selection=True,export_yup=True)
    stats['glbSha256']=hashlib.sha256((out/'Kar98k_JointRepair_V6.glb').read_bytes()).hexdigest()
    (out/'build.json').write_text(json.dumps(stats,indent=2),encoding='utf-8');print(json.dumps(stats),flush=True)
