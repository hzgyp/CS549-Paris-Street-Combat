"""Explicit manual steel boundary unfolding; discard bad interior, new cap skin."""
import json,math,collections
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from seam import ROOT,BASE

def ear_triangles(q,omitted):
    def cr(a,b):return a[0]*b[1]-a[1]*b[0]
    points=q[:,:2];ids=[i for i in range(len(q)) if i not in omitted]
    if sum(cr(points[a],points[b]) for a,b in zip(ids,ids[1:]+ids[:1]))<0:ids.reverse()
    tris=[]
    while len(ids)>3:
        found=False
        for k,b in enumerate(ids):
            a=ids[k-1];c=ids[(k+1)%len(ids)];pa,pb,pc=points[[a,b,c]]
            if cr(pb-pa,pc-pb)<=1e-16:continue
            occupied=False
            for z in ids:
                if z in (a,b,c):continue
                p=points[z]
                if min(cr(pb-pa,p-pa),cr(pc-pb,p-pb),cr(pa-pc,p-pc))>=-1e-17:occupied=True;break
            if occupied:continue
            tris.append((a,b,c));ids.pop(k);found=True;break
        assert found,('no simple polygon ear',len(ids))
    tris.append(tuple(ids))
    # Reinsert every purposely collinear boundary point into its own edge's triangle.
    for first,last in ((50,56),(93,99)):
        k=next(i for i,t in enumerate(tris) if first in t and last in t);tri=tris.pop(k);other=next(i for i in tri if i not in (first,last))
        for a,b in zip(range(first,last),range(first+1,last+1)):
            t=(a,b,other)
            if cr(points[b]-points[a],points[other]-points[b])<0:t=t[::-1]
            tris.append(t)
    assert len(tris)==len(q)-2
    return tris

def crosses(q):
    def cross(a,b):return a[0]*b[1]-a[1]*b[0]
    out=[]
    for i in range(len(q)):
        for j in range(i+2,len(q)):
            if i==0 and j==len(q)-1:continue
            a,b=q[i,:2],q[(i+1)%len(q),:2];c,d=q[j,:2],q[(j+1)%len(q),:2];ab=b-a;cd=d-c
            if cross(ab,c-a)*cross(ab,d-a)<-1e-20 and cross(cd,a-c)*cross(cd,b-c)<-1e-20:out.append([i,j])
    return out

def rebuild(o,mat,out):
    r=json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/interface_v1/interface.json').read_text());q=np.array(r['boundary_xyz']);before=q.copy();assert crosses(q)==[[51,54],[94,96],[94,97]]
    moved=[]
    for first,last in ((50,56),(93,99)):
        lengths=np.linalg.norm(np.diff(q[first:last+1,:2],axis=0),axis=1);t=np.r_[0,np.cumsum(lengths)]/sum(lengths)
        for i in range(first+1,last):q[i,:2]=q[first,:2]*(1-t[i-first])+q[last,:2]*t[i-first];moved.append(i)
    assert not crosses(q),'manual unfold still intersects'
    disp=np.linalg.norm(q-before,axis=1);assert disp.max()<.003
    m=o.data;source=[tuple(v.co) for v in m.vertices];keys={tuple(np.round(before[i],7)):q[i] for i in moved};changed={}
    for i,p in enumerate(source):
        k=tuple(np.round(p,7))
        if k in keys:changed[i]=keys[k]
    ballfaces=json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-joint-v6/boundary_v1b/surface_selection.json').read_text())['faces'];ballverts={v for f in ballfaces for v in m.polygons[f].vertices};assert not(set(changed)&ballverts)
    proof={'same_selected_source_faces':len(r['faces']),'same_boundary_edges':len(q),'crossings_before':crosses(before),'crossings_after':crosses(q),'manual_boundary_rows':moved,'source_copies_moved':len(changed),'max_boundary_move_m':float(disp.max()),'before_delete_pass':True}
    (out/'receiver_boundary_proof.json').write_text(json.dumps(proof,indent=2))
    # Flat XY ear tessellation, then conforming subdivision. Exact original loop order.
    ff=ear_triangles(q,set(moved))
    bm=bmesh.new();bv=[bm.verts.new(tuple(z)) for z in q]
    for f in ff:
        pp=np.cross(q[f[1]]-q[f[0]],q[f[2]]-q[f[0]])
        bm.faces.new(tuple(bv[i] for i in (f if pp[2]>0 else f[::-1])))
    assert all(len(e.link_faces) in (1,2) for e in bm.edges)
    assert all(f.calc_area()>1e-14 for f in bm.faces)
    # Three midpoint subdivisions on INTERNAL edges only; original root edges untouched.
    for _ in range(3):
        es=[e for e in bm.edges if e.is_manifold];bmesh.ops.subdivide_edges(bm,edges=es,cuts=1,use_grid_fill=False)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.verts.ensure_lookup_table();boundaryverts={v for e in bm.edges if e.is_boundary for v in e.verts}
    assert len(boundaryverts)==len(q),'boundary unexpectedly subdivided'
    # Hand-authored cap control stations, not data-fit/profile search.
    controls=[(-.195,.017,.124,.009),(-.184,.016,.123,.012),(-.154,.016,.116,.012),(-.146,.016,.114,.020),(-.120,.016,.110,.020),(-.114,.016,.108,.013),(-.083,.016,.104,.014)]
    cx=np.array([v[0] for v in controls]);cy=np.array([v[1] for v in controls]);cz=np.array([v[2] for v in controls]);cr=np.array([v[3] for v in controls])
    for v in bm.verts:
        if v in boundaryverts:continue
        x,y,z=v.co;dist=min(float(np.linalg.norm(np.array((x,y))- (a[:2]+np.clip(np.dot(np.array((x,y))-a[:2],b[:2]-a[:2])/np.dot(b[:2]-a[:2],b[:2]-a[:2]),0,1)*(b[:2]-a[:2])))) for a,b in zip(q,np.roll(q,-1,axis=0)))
        center=np.interp(x,cx,cy);rad=np.interp(x,cx,cr);target=np.interp(x,cx,cz)+math.sqrt(max(0,rad*rad-(y-center)**2));t=min(1,dist/.003);t=t*t*(3-2*t);v.co.z=z*(1-t)+target*t
    incidence=collections.Counter(len(e.link_faces) for e in bm.edges)
    (out/'skin_construction_diagnosis.json').write_text(json.dumps({'edge_incidence':dict(incidence),'exceptional_edges':[[list(e.verts[0].co),list(e.verts[1].co),len(e.link_faces)] for e in bm.edges if len(e.link_faces) not in (1,2)],'small_faces':sum(f.calc_area()<=1e-14 for f in bm.faces)},indent=2))
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(len(e.link_faces) in (1,2) for e in bm.edges)
    assert sum(e.is_boundary for e in bm.edges)==len(q);assert all(f.calc_area()>1e-14 for f in bm.faces)
    d=bpy.data.meshes.new('V9_Receiver_Skin_Mesh');bm.to_mesh(d);bm.free();skin=bpy.data.objects.new('V9_Receiver_Skin',d);bpy.context.scene.collection.objects.link(skin);d.materials.append(mat)
    for p in d.polygons:p.use_smooth=True
    uv=d.uv_layers.new(name='Own_XY_SurfaceUV')
    for p in d.polygons:
        for l in p.loop_indices:
            v=d.vertices[d.loops[l].vertex_index].co;uv.data[l].uv=((v.x+.195)/.113,(v.y+.0061)/.046)
    # Source copies move only at documented steel fold; all other source verts/UV retained.
    verts=[tuple(changed.get(i,p)) for i,p in enumerate(source)];sel=set(r['faces']);kept=[p for p in m.polygons if p.index not in sel]
    faces=[tuple(p.vertices) for p in kept];uv0=m.uv_layers.active;cn0=[tuple(n.vector) for n in m.corner_normals];uvs=[[tuple(uv0.data[l].uv) for l in p.loop_indices] for p in kept];normals=[cn0[l] for p in kept for l in p.loop_indices]
    nd=bpy.data.meshes.new('V9_SourceMinusUpperSteel');nd.from_pydata(verts,[],faces);nd.update()
    for material in m.materials:nd.materials.append(material)
    layer=nd.uv_layers.new(name=uv0.name)
    for p,oldp,us in zip(nd.polygons,kept,uvs):
        p.material_index=oldp.material_index;p.use_smooth=True
        for l,u in zip(p.loop_indices,us):layer.data[l].uv=u
        if set(p.vertices)&set(changed):
            for l in p.loop_indices:normals[l]=tuple(p.normal)
    nd.normals_split_custom_set(normals);nd.update();o.data=nd
    assert all(tuple(nd.vertices[i].co)==p for i,p in enumerate(source) if i not in changed)
    d.calc_loop_triangles();proof.update({'replacement_triangles':len(d.loop_triangles),'skin_one_matching_boundary':True,'original_nonboundary_positions_exact':True,'original_retained_corner_uv_exact':True,'complete_receiver_mechanics':False})
    (out/'receiver_metrics.json').write_text(json.dumps(proof,indent=2));return skin,proof
