"""Independent analytical parts. Never cuts or overlays source rifle."""
import argparse,collections,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import setup,camera,pbr,save_export
A=Vector((1,0,-.14)).normalized();B=Vector((0,1,0));C=B.cross(A).normalized()*-1
ORIGIN=Vector((0,.016,.08));BASIS=Matrix((A,B,C)).transposed()
OBJECTS=[]
VIEWS=[('all_quarter',(.25,-1,.65),(.175,.016,.055),.86),('all_right',(.175,-1,.055),(.175,.016,.055),.86),
       ('all_left',(.175,1,.055),(.175,.016,.055),.86),('all_top',(.175,.016,1),(.175,.016,.055),.86),
       ('all_bottom',(.175,.016,-1),(.175,.016,.055),.86),
       ('receiver',(-.045,-.28,.32),(-.11,.016,.094),.285),
       ('sight',(.115,-.20,.26),(.055,.016,.096),.20),
       ('muzzle',(.65,-.19,.21),(.49,.016,.013),.17)]
def material(n,col,rough):
    m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1)
    bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=rough
    return m
def finish(o,n,pivot,mat,bevel=0):
    o.name=n;o.data.name=n+'_Mesh';o.data.materials.append(mat)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    if bevel:
        mod=o.modifiers.new('ManufacturedChamfer','BEVEL');mod.width=bevel;mod.segments=3;mod.limit_method='ANGLE'
        bpy.ops.object.modifier_apply(modifier=mod.name)
    # Native mesh topology/UV, no runtime modifier or procedural material dependency.
    for p in o.data.polygons:p.use_smooth=True
    mod=o.modifiers.new('MachinedFaceNormals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.008)
    bpy.ops.object.mode_set(mode='OBJECT')
    # Bake local engineering frame into vertices; declared object origin/pivot.
    for v in o.data.vertices:v.co=BASIS@(o.matrix_world@v.co-Vector(pivot))
    o.matrix_world=Matrix.Identity(4);o.location=ORIGIN+BASIS@Vector(pivot)
    o['candidate_status']='standalone_not_integrated';o['pivot_local_m']=list(pivot)
    OBJECTS.append(o);bpy.ops.object.select_all(action='DESELECT');return o
def mesh(n,verts,faces,pivot,mat,bevel=0):
    d=bpy.data.meshes.new(n);d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(n,d);bpy.context.scene.collection.objects.link(o)
    return finish(o,n,pivot,mat,bevel)
def box(n,center,size,mat,bevel=.0003):
    bpy.ops.object.select_all(action='DESELECT');bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,n,center,mat,bevel)
def tube(n,profile,inner,mat,ry=1,rz=1):
    # Closed annular volume with genuine inner wall; axis local X.
    N=64;verts=[]
    for x,r in profile:
        for j in range(N):
            t=j*2*math.pi/N;verts.append((x,ry*r*math.cos(t),rz*r*math.sin(t)))
    for x,_ in profile:
        for j in range(N):
            t=j*2*math.pi/N;verts.append((x,ry*inner*math.cos(t),rz*inner*math.sin(t)))
    L=len(profile);faces=[]
    for k in range(L-1):
        for j in range(N):
            z=(j+1)%N;a=k*N+j;b=k*N+z;c=(k+1)*N+z;d=(k+1)*N+j
            faces.append((a,b,c,d));faces.append((L*N+a,L*N+d,L*N+c,L*N+b))
    for j in range(N):
        z=(j+1)%N;faces.append((j,L*N+j,L*N+z,z))
        a=(L-1)*N+j;b=(L-1)*N+z;faces.append((a,b,L*N+b,L*N+a))
    return mesh(n,verts,faces,((profile[0][0]+profile[-1][0])/2,0,0),mat)
def wedge(n,x0,x1,width,z0,z1,thick,mat):
    verts=[(x,y,z) for x,z in ((x0,z0),(x1,z1),(x1,z1+thick),(x0,z0+thick)) for y in (-width/2,width/2)]
    faces=[(0,1,3,2),(6,4,5,7),(0,6,7,1),(2,3,5,4),(0,2,4,6),(1,7,5,3)]
    return mesh(n,verts,faces,((x0+x1)/2,0,(z0+z1)/2),mat,.00025)
def orient_outward(o):
    # Consistent independent solids only; no source weld or topology changes.
    import bmesh
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.to_mesh(o.data);bm.free();o.data.update()
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True);OBJECTS.clear()
    dark=material('Own_BluedSteel',(.042,.051,.061),.31)
    bolt=material('Own_BoltSteel',(.19,.205,.22),.29)
    # Receiver is visibly open above lower rails, NOT an enclosing box/plate.
    tube('Receiver_RearBridge',[(-.153,.0172),(-.1525,.0180),(-.1345,.0180),(-.134,.0172)],.0120,dark)
    tube('Receiver_FrontRing',[(-.055,.0188),(-.0545,.0193),(-.0275,.0193),(-.027,.0188)],.0109,dark)
    box('Receiver_LeftRail',(-.094,.013,-.004),(.078,.005,.009),dark)
    box('Receiver_RightRail',(-.094,-.013,-.004),(.078,.005,.009),dark)
    box('Receiver_LowerBridge',(-.094,0,-.010),(.078,.025,.004),dark)
    tube('Bolt_Body',[(-.174,.0102),(-.1735,.0107),(-.0285,.0107),(-.028,.0102)],.0030,bolt)
    tube('Bolt_RearCap',[(-.193,.0115),(-.1924,.0126),(-.1756,.0126),(-.175,.0115)],.0042,dark)
    box('Bolt_Extractor',(-.095,-.0101,.0039),(.075,.0022,.0034),dark,.0002)
    # Static neutral safety flag and hinge; not functional bolt/reload animation.
    box('SafetyFlag',(-.184,.0045,.019),(.0035,.021,.012),dark,.0004)
    box('SafetyFlag_Neck',(-.184,0,.0115),(.0045,.009,.010),dark)
    # Tangent sight: two supports, inclined leaf, separate slider/notch, front hinge.
    wedge('RearSight_Base',-.012,.121,.023,.015,.012,.0045,dark)
    wedge('RearSight_Leaf',-.009,.114,.0175,.026,.018,.0025,dark)
    # Slider clamp assembled around leaf without hiding its center surface.
    box('RearSight_SliderLeft',(.020,.0113,.025),(.011,.0064,.009),dark)
    box('RearSight_SliderRight',(.020,-.0113,.025),(.011,.0064,.009),dark)
    box('RearSight_SliderUnder',(.020,0,.0205),(.011,.023,.0022),dark,.0002)
    # Two notch shoulders leave a real V-like center gap, not solid sight slab.
    box('RearSight_NotchLeft',(-.008,.0048,.030),(.0036,.006,.005),dark,.0002)
    box('RearSight_NotchRight',(-.008,-.0048,.030),(.0036,.006,.005),dark,.0002)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.003,depth=.025,location=(.114,0,.019),rotation=(math.pi/2,0,0))
    finish(bpy.context.object,'RearSight_Hinge',(.114,0,.019),dark,.00015)
    # Geometry marks are shallow *gaps between* leaf rails, not fake dark planes.
    for side in (-1,1):
        wedge('RearSight_ScaleRail_'+str(side),-.002,.108,.003,.0289,.021,.0006,bolt)
        o=OBJECTS[-1];o.location+=B*(side*.006)
    tube('Muzzle_Barrel',[ (.432,.0094),(.504,.0086),(.5418,.0080),(.542,.0078)],.00415,dark)
    tube('Muzzle_FrontBand',[ (.427,.0210),(.4275,.0216),(.4365,.0216),(.437,.0210)],.0194,dark,ry=.9,rz=1.10)
    box('FrontSight_Base',(.525,0,.010),(.027,.008,.005),dark,.0003)
    # Tapered blade has a slim top and a clear supported base.
    verts=[(x,y,z) for z,x0,x1,half in ((.0125,.518,.532,.0017),(.021,.524,.529,.00065)) for x in (x0,x1) for y in (-half,half)]
    faces=[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
    mesh('FrontSight_Blade',verts,faces,(.525,0,.0125),dark,.00012)
    for o in OBJECTS:orient_outward(o)
    return list(OBJECTS)
def audit(meshes):
    import bmesh
    rows=[]
    for o in meshes:
        m=o.data;m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m)
        crossed=[]
        for p in m.polygons:
            q=[m.vertices[v].co for v in p.vertices]
            dots=[(q[(i+1)%len(q)]-q[i]).cross(q[(i+2)%len(q)]-q[(i+1)%len(q)]).dot(p.normal) for i in range(len(q))]
            if min(dots)<-1e-12:crossed.append(p.index)
        row={'name':o.name,'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'uv_layers':len(m.uv_layers),'crossed_convex_faces':crossed,
             'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':float(bm.calc_volume(signed=True)),
             'bounds_world_m':[[min((o.matrix_world@v.co)[i] for v in m.vertices) for i in range(3)],[max((o.matrix_world@v.co)[i] for v in m.vertices) for i in range(3)]],
             'pivot_world_m':list(o.location)}
        bm.free();assert row['nonmanifold_edges']==0 and row['volume_m3']>0 and row['uv_layers']==1 and not crossed,row
        rows.append(row)
    return {'standalone_only':True,'original_rifle_loaded_or_cut':False,'parts':rows,'triangles':sum(r['triangles'] for r in rows)}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--pbr',action='store_true');p.add_argument('--skip-renders',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
    meshes=build();s,_=setup();cams={n:camera('Parts_'+n,e,t,sc) for n,e,t,sc in VIEWS}
    d=audit(meshes);(out/'metrics.json').write_text(json.dumps(d,indent=2))
    if a.pbr:pbr()
    for n in cams:
        s.camera=cams[n];s.render.filepath=str(out/(n+'.png'))
        if not a.skip_renders:bpy.ops.render.render(write_still=True)
    save_export(meshes,out,'Kar98k_StandaloneMechanical_V8C')
    print(json.dumps({'parts':len(meshes),'triangles':d['triangles'],'standalone_only':True}),flush=True)
