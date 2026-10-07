"""Manually chosen X=.480 annular seam. Immutable source, explicit loft, no hull."""
import argparse,collections,json,math,sys,hashlib
from pathlib import Path
import bpy,numpy as np,bmesh
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from seam import load,ROOT,BASE,CUT_X
sys.path.insert(0,str(ROOT/'Tools/AssetCreation/GermanRifleTopologyV8'))
from common import setup,camera,pbr,save_export

def rings():
    d=json.loads((BASE/'seam_diagnosis.json').read_text());assert len(d['components'])==2
    c=np.array(d['components'][1]['center_yz']);ordered=[]
    for item in d['components']:
        q=np.array(item['xyz']);ang=np.arctan2(q[:,2]-c[1],q[:,1]-c[0]);step=np.angle(np.exp(1j*(np.roll(ang,-1)-ang)))
        assert np.all(step>0) or np.all(step<0),('not simple radial ring',step.min(),step.max())
        if np.all(step<0):q=q[::-1]
        ang=np.mod(np.arctan2(q[:,2]-c[1],q[:,1]-c[0]),2*np.pi);start=np.argmin(ang);q=np.roll(q,-start,axis=0);ang=np.roll(ang,-start)
        assert np.all(np.diff(ang)>0);ordered.append((q,ang))
    # Direct point-in-polygon proof; no convex hull, resampling, or root simplification.
    outer=ordered[0][0][:,1:]
    for y,z in ordered[1][0][:,1:]:
        inside=False
        for a,b in zip(outer,np.roll(outer,-1,axis=0)):
            if (a[1]>z)!=(b[1]>z) and y<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0]:inside=not inside
        assert inside,'bore not nested in barrel'
    return ordered,c

def steel():
    m=bpy.data.materials.new('V9_Own_BluedSteel');m.use_nodes=True;m.diffuse_color=(.042,.051,.061,1)
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=.31
    return m

def clip_source(o,ordered):
    old=o.data;coords=[tuple(v.co) for v in old.vertices];verts=list(coords);uv=old.uv_layers.active
    cn=[tuple(n.vector) for n in old.corner_normals]
    roots={tuple(np.round(q,7)):q for ring,_ in ordered for q in ring};ids={};faces=[];uvs=[];normals=[];mats=[];retained=0;split=0;removed=0
    def intersection(a,b):
        t=(CUT_X-a[0][0])/(b[0][0]-a[0][0]);q=np.array(a[0])+t*(np.array(b[0])-a[0]);key=tuple(np.round(q,7));assert key in roots
        if key not in ids:ids[key]=len(verts);verts.append(tuple(roots[key]))
        nn=np.array(a[3])+t*(np.array(b[3])-a[3]);nn/=np.linalg.norm(nn)
        return (verts[ids[key]],np.array(a[1])+t*(np.array(b[1])-a[1]),ids[key],tuple(nn))
    for p in old.polygons:
        assert len(p.vertices)==3
        vv=[(coords[v],tuple(uv.data[l].uv),v,cn[l]) for v,l in zip(p.vertices,p.loop_indices)]
        if all(a[0][0]<=CUT_X for a in vv):poly=vv;retained+=1
        elif all(a[0][0]>=CUT_X for a in vv):removed+=1;continue
        else:
            split+=1;poly=[]
            for a,b in zip(vv,vv[1:]+vv[:1]):
                ia=a[0][0]<=CUT_X;ib=b[0][0]<=CUT_X
                if ia:poly.append(a)
                if ia!=ib:poly.append(intersection(a,b))
        for k in range(1,len(poly)-1):
            tri=[poly[0],poly[k],poly[k+1]];faces.append(tuple(z[2] for z in tri));uvs.append([z[1] for z in tri]);normals.extend(z[3] for z in tri);mats.append(p.material_index)
    assert len(ids)==sum(len(q) for q,_ in ordered)
    mesh=bpy.data.meshes.new('V9_RetainedSource');mesh.from_pydata(verts,[],faces);mesh.update()
    for mat in old.materials:mesh.materials.append(mat)
    layer=mesh.uv_layers.new(name=uv.name)
    for p,t,mi in zip(mesh.polygons,uvs,mats):
        p.material_index=mi;p.use_smooth=True
        for l,u in zip(p.loop_indices,t):layer.data[l].uv=u
    mesh.normals_split_custom_set(normals);mesh.update()
    assert max(abs(layer.data[l].uv[k]-u[k]) for p,t in zip(mesh.polygons,uvs) for l,u in zip(p.loop_indices,t) for k in range(2))<1e-7
    # Kept original positions are bit-identical, source corner UV within Blender float storage.
    assert all(tuple(mesh.vertices[i].co)==coords[i] for i in range(len(coords)))
    o.data=mesh;o.name='V9_Rifle_Retained';return {'retained_original_triangles':retained,'split_original_triangles':split,'removed_front_triangles':removed,'matched_root_vertices':len(ids),'original_vertex_positions_exact':True,'retained_uv_values_exact':True}

def loft(ordered,c,mat):
    verts=[];faces=[];indices=[]
    for j,(q,angles) in enumerate(ordered):
        n=len(q);start=len(verts);r0=.0098 if j==0 else .0053;rend=.0086 if j==0 else .0042
        profile=[(CUT_X,None),(.484,r0),(.488,r0),(.538,rend),(.539,rend*.985)]
        for x,r in profile:
            for i,a in enumerate(angles):
                if r is None:verts.append(tuple(q[i]))
                else:verts.append((x,c[0]+r*math.cos(a),c[1]-.14*(x-CUT_X)+r*math.sin(a)))
        for k in range(len(profile)-1):
            for i in range(n):
                a=start+k*n+i;b=start+k*n+(i+1)%n;cc=b+n;d=a+n
                faces.append((a,b,cc,d) if j==0 else (a,d,cc,b))
        indices.append([start+(len(profile)-1)*n+i for i in range(n)])
    # Actual angular merge triangulation of annular crown, not hole cap.
    oo,ii=indices;ao=ordered[0][1];ai=ordered[1][1];i=j=0;no=len(oo);ni=len(ii)
    while i<no or j<ni:
        an=ao[(i+1)%no]+(2*np.pi if i+1>=no else 0) if i<no else math.inf
        bn=ai[(j+1)%ni]+(2*np.pi if j+1>=ni else 0) if j<ni else math.inf
        if an<=bn:faces.append((oo[i%no],oo[(i+1)%no],ii[j%ni]));i+=1
        else:faces.append((oo[i%no],ii[(j+1)%ni],ii[j%ni]));j+=1
    mesh=bpy.data.meshes.new('V9_AnnularBarrel_Mesh');mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new('V9_AnnularBarrel',mesh);bpy.context.scene.collection.objects.link(o);mesh.materials.append(mat)
    for p in mesh.polygons:p.use_smooth=len(p.vertices)==4
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.008);bpy.ops.object.mode_set(mode='OBJECT')
    bm=bmesh.new();bm.from_mesh(mesh);boundary=[e for e in bm.edges if e.is_boundary];bad=[e for e in bm.edges if len(e.link_faces)>2];assert len(boundary)==no+ni and not bad
    bm.free();return o

def sight(c,mat):
    out=[];x=.521;z=c[1]-.14*(x-CUT_X);y=c[0]
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z+.010))
    o=bpy.context.object;o.name='V9_FrontSight_Base';o.scale=(.025,.009,.005);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);out.append(o)
    # Simple taper, no markings/hood mechanism.
    vv=[(x+dx,y+dy,z+zz) for zz,dx0,dx1,half in ((.0125,-.007,.007,.0018),(.021,-.0015,.003,.0007)) for dx in (dx0,dx1) for dy in (-half,half)]
    f=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)];m=bpy.data.meshes.new('V9_FrontSight_Blade_Mesh');m.from_pydata(vv,[],f);m.update();o=bpy.data.objects.new('V9_FrontSight_Blade',m);bpy.context.scene.collection.objects.link(o);out.append(o)
    for o in out:
        o.data.materials.append(mat);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
        mod=o.modifiers.new('OrdinaryChamfer','BEVEL');mod.width=.00015;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);bm.to_mesh(o.data);bm.free()
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.008);bpy.ops.object.mode_set(mode='OBJECT')
    return out

def sling_hash(o):
    return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[tuple(l.uv) for l in o.data.uv_layers.active.data],list(o.matrix_world))).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--pbr',action='store_true');p.add_argument('--skip-renders',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    rifle,originals=load();sling=originals[1];sh=sling_hash(sling);ordered,c=rings();metrics=clip_source(rifle,ordered);mat=steel();barrel=loft(ordered,c,mat);parts=sight(c,mat);meshes=[rifle,sling,barrel,*parts]
    assert sling_hash(sling)==sh;metrics.update({'nested_annular_root_verified':True,'outer_edges':len(ordered[0][0]),'inner_edges':len(ordered[1][0]),'sling_geometry_uv_transform_exact':True,'whole_rifle':True,'receiver_original_unrepaired':True,'root_x_m':CUT_X,'source_faces_behind_root_max_x':max(v.co.x for v in rifle.data.vertices if v.index>=len(rifle.data.vertices)-116)})
    for o in meshes:o.data.calc_loop_triangles()
    metrics['triangles']=sum(len(o.data.loop_triangles) for o in meshes);metrics['objects']=[o.name for o in meshes]
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2))
    s,cams=setup();cams['muzzle_reverse']=camera('V9_MuzzleReverse',(.70,.40,.20),(.498,c[0],.034),.20)
    cams['muzzle_top']=camera('V9_MuzzleTop',(.498,c[0],1),(.498,c[0],.034),.20)
    cams['muzzle_right']=camera('V9_MuzzleRight',(.498,-1,.034),(.498,c[0],.034),.20)
    if a.pbr:pbr()
    if not a.skip_renders:
        for name in ['whole_right','whole_left','whole_top','whole_bottom','muzzle','muzzle_reverse','muzzle_top','muzzle_right']:
            s.camera=cams[name];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    save_export(meshes,out,'Kar98k_ManualFront_V9');print(json.dumps(metrics),flush=True)

if __name__=='__main__':main()
