"""Deterministic exterior-only Kar98k refinement from immutable Aholo base.

No cloud requests, stock remesh, welding, collapse decimation or game writes.
Exact bounded volume subtraction retains original triangle UVs and interpolates
new cut corners. Exterior hardware is explicit editable beveled geometry.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--revision',type=int,choices=(3,),default=3)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
ROOT=Path(__file__).resolve().parents[3]
OLD=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1'
SOURCE=OLD/'incoming/kar98k-base-v1.glb'
BASE_SHA='a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==BASE_SHA
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SOURCE))
old=next(o for o in bpy.data.objects if o.type=='MESH')
norm=Matrix(json.loads((OLD/'evidence/incoming_v2/inspection.json').read_text())['normalizationMatrix'])
world=norm @ old.matrix_world;old.parent=None;old.matrix_world=world
bpy.context.view_layer.objects.active=old;old.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
old.select_set(False)

# Visual exterior axis inferred from the normalized source, not a production
# drawing. No chamber/bore/locking surfaces/internal ammunition are constructed.
axis_x=Vector((1,.021,-.135)).normalized()
axis_y=Vector((-axis_x.y,axis_x.x,0)).normalized()
axis_z=axis_x.cross(axis_y).normalized()
frame=Matrix((axis_x,axis_y,axis_z)).transposed().to_4x4()
frame.translation=Vector((0,.010,.103))
inv=frame.inverted()

# local exterior cut volumes, m; full exact clipping replaces centroid cuts.
volumes=[('receiver_exterior',(-.254,-.042),(-.150,.150),(-.020,.150)),
         ('handle_protrusion',(-.200,-.116),(-.150,-.021),(-.065,.150)),
         ('rear_sight',(-.043,.144),(-.050,.050),(-.009,.150)),
         ('generated_front',(.416,1.0),(-.150,.150),(-.300,.150))]
src=old.data;src.calc_loop_triangles()
pos=[v.co.copy() for v in src.vertices]
loc=[inv @ q for q in pos]
uv=src.uv_layers.active.data
normals=src.corner_normals
faces=[];loop_uv=[];loop_n=[];face_m=[];orig_face=[]
cache={};deleted=0;cut_faces=0;retained=0;uv_max_error=0

def clip(poly,axis,threshold,positive):
    """Return halfspace polygon, retaining IDs/UV/normals at untouched corners."""
    result=[]
    for i,b in enumerate(poly):
        c=poly[i-1];dc=(loc[c[0]][axis]-threshold)*(1 if positive else -1);db=(loc[b[0]][axis]-threshold)*(1 if positive else -1)
        ci=dc>=-1e-10;bi=db>=-1e-10
        if ci!=bi:
            t=dc/(dc-db)
            key=(min(c[0],b[0]),max(c[0],b[0]),axis,threshold)
            if key not in cache:
                cache[key]=len(pos);pos.append(pos[c[0]].lerp(pos[b[0]],t));loc.append(loc[c[0]].lerp(loc[b[0]],t))
            result.append((cache[key],c[1].lerp(b[1],t),c[2].lerp(b[2],t).normalized()))
        if bi:result.append(b)
    # Avoid numerical duplicate corners produced at exact plane vertices.
    clean=[]
    for q in result:
        if not clean or (pos[q[0]]-pos[clean[-1][0]]).length>1e-10:clean.append(q)
    if len(clean)>1 and (pos[clean[0][0]]-pos[clean[-1][0]]).length<1e-10:clean.pop()
    return clean

def subtract(poly,volume):
    ranges=volume[1:]
    if any(max(loc[q[0]][k] for q in poly)<bounds[0]-1e-10 or min(loc[q[0]][k] for q in poly)>bounds[1]+1e-10 for k,bounds in enumerate(ranges)):
        return [poly],False
    pending=poly;outside=[]
    for axis,bounds in enumerate(ranges):
        for threshold,positive in ((bounds[0],True),(bounds[1],False)):
            part=clip(pending,axis,threshold,not positive)
            if len(part)>=3:outside.append(part)
            pending=clip(pending,axis,threshold,positive)
            if len(pending)<3:return outside,True
    return outside,True

for index,f in enumerate(src.polygons):
    poly=[(src.loops[i].vertex_index,uv[i].uv.copy(),normals[i].vector.copy()) for i in f.loop_indices]
    pieces=[poly];changed=False
    for volume in volumes:
        new=[]
        for part in pieces:
            parts,did=subtract(part,volume);new.extend(parts);changed=changed or did
        pieces=new
        if not pieces:break
    if not pieces:deleted+=1
    elif changed:cut_faces+=1
    else:retained+=1
    for part in pieces:
        for j in range(1,len(part)-1):
            tri=[part[0],part[j],part[j+1]]
            if (pos[tri[1][0]]-pos[tri[0][0]]).cross(pos[tri[2][0]]-pos[tri[0][0]]).length<1e-13:continue
            faces.append([q[0] for q in tri]);loop_uv.extend(tuple(q[1]) for q in tri);loop_n.extend(tuple(q[2]) for q in tri);face_m.append(f.material_index)
            orig_face.append(index if not changed else -1)
        if not changed:
            uv_max_error=max(uv_max_error,max((q[1]-uv[i].uv).length for q,i in zip(part,f.loop_indices)))
    if index%100000==0:print('Source faces processed',index,flush=True)

used=sorted({i for f in faces for i in f});remap={j:i for i,j in enumerate(used)}
m=bpy.data.meshes.new('Kar98k_RetainedSourceUV_Surface');m.from_pydata([pos[i] for i in used],[],[[remap[i] for i in f] for f in faces]);m.update()
u=m.uv_layers.new(name='UVMap');u.data.foreach_set('uv',np.array(loop_uv,dtype=np.float32).ravel())
for mat in src.materials:m.materials.append(mat)
for f,mi in zip(m.polygons,face_m):f.material_index=mi;f.use_smooth=True
m.normals_split_custom_set(loop_n)
body=bpy.data.objects.new('Kar98k_OriginalWoodGuardSling',m);bpy.context.scene.collection.objects.link(body)
body['uv_policy']='Original corners retained exactly; cut corners linearly interpolated; no weld/decimate'
body['historical_limit']='Museum replacement sling retained; not approved German-issued sling'
bpy.data.objects.remove(old,do_unlink=True)
# Preserve retained texture maps; bound overly shiny generated appearance.
for mat in m.materials:
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    for link in list(shader.inputs['Roughness'].links):mat.node_tree.links.remove(link)
    shader.inputs['Roughness'].default_value=.64

root=bpy.data.objects.new('Kar98k_RefinedWorldMaster_V2',None);bpy.context.scene.collection.objects.link(root);body.parent=root
hardware=bpy.data.objects.new('Kar98k_ExteriorHardware',None);bpy.context.scene.collection.objects.link(hardware);hardware.parent=root;hardware.matrix_world=frame
bolt=bpy.data.objects.new('Kar98k_VisibleBoltAssembly',None);bpy.context.scene.collection.objects.link(bolt);bolt.parent=hardware
bolt['limit']='Whole exposed visual bolt with connected handle; no internal mechanism or reload action'
root['status']='LOCAL DETAIL MASTER; UE/LOD/history/action/production selection pending'
root['source_sha256']=BASE_SHA

def material(name,color,metallic,roughness):
    t=bpy.data.materials.new(name);t.use_nodes=True
    p=t.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=roughness
    t.diffuse_color=(*color,1)
    return t
steel=material('DarkBluedSteel',(.045,.052,.060),.87,.43)
edge=material('WornSteelDetails',(.10,.113,.125),.90,.37)
black=material('SightBlack',(.024,.028,.031),.75,.53)
wood_cap=material('BoundedStockInletWood',(.135,.052,.020),0,.68)
# Packed glTF-compatible subtle roughness grain, not a shader that disappears.
rng=np.random.default_rng(9803);size=256
grain=np.clip(.43+rng.normal(0,.018,(size,size)),.36,.51)
im=bpy.data.images.new('SteelMicroRoughness',width=size,height=size,alpha=True)
pixels=np.ones((size,size,4),dtype=np.float32);pixels[:,:,:3]=grain[:,:,None]
im.pixels.foreach_set(pixels.ravel());im.colorspace_settings.name='Non-Color';im.pack()
tex=steel.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
steel.node_tree.links.new(tex.outputs['Color'],steel.node_tree.nodes.get('Principled BSDF').inputs['Roughness'])

# Derived cut-interface surfaces, not another box classifier or a stock remesh.
# Each is a visible local closure attached to the retained surface. Hulls are
# conservative exterior closures, not claims of globally watertight retopology.
cap_stats=[]
def cap_from_cut(name,axis,threshold,volume,reverse=False):
    indices=[i for i in used if abs(loc[i][axis]-threshold)<3e-7 and all(volume[k+1][0]-1e-6<=loc[i][k]<=volume[k+1][1]+1e-6 for k in range(3))]
    axes=[k for k in range(3) if k!=axis]
    points=sorted(set((round(loc[i][axes[0]],7),round(loc[i][axes[1]],7)) for i in indices))
    if len(points)<3:return
    def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower=[]
    for point in points:
        while len(lower)>=2 and cross(lower[-2],lower[-1],point)<=0:lower.pop()
        lower.append(point)
    upper=[]
    for point in reversed(points):
        while len(upper)>=2 and cross(upper[-2],upper[-1],point)<=0:upper.pop()
        upper.append(point)
    hull=lower[:-1]+upper[:-1]
    verts=[]
    for point in hull:
        v=[0,0,0];v[axis]=threshold
        for k,t in zip(axes,point):v[k]=t
        verts.append(tuple(frame @ Vector(v)))
    face=list(range(len(hull)))
    if reverse:face.reverse()
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[face]);mesh.update()
    layer=mesh.uv_layers.new(name='UVMap')
    for loop in mesh.loops:
        x,y=hull[loop.vertex_index];layer.data[loop.index].uv=(x*12,y*12)
    o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=root;o.data.materials.append(wood_cap)
    cap_stats.append({'name':name,'planeAxis':axis,'plane':threshold,'sourceBoundaryPoints':len(indices),'hullVertices':len(hull)})
    return o

caps=[]
for name,axis,threshold,volume,reverse in [('StockReceiverInletClosure',2,-.020,volumes[0],False),('StockSightInletClosure',2,-.009,volumes[2],False),
        ('StockHandleInletClosure',1,-.021,volumes[1],False),('StockHandleLowerClosure',2,-.065,volumes[1],False)]:
    obj=cap_from_cut(name,axis,threshold,volume,reverse)
    if obj:caps.append(obj)
assert len(caps)>=3

made=[]
def finish(o,name,mat,parent=hardware,bevel=0):
    o.name=name;o.parent=parent;o.data.materials.clear();o.data.materials.append(mat)
    if bevel:
        d=o.modifiers.new('ManufacturedEdgeBevel','BEVEL');d.width=bevel;d.segments=3;d.limit_method='ANGLE';d.harden_normals=True
    bpy.context.view_layer.objects.active=o
    # Explicit UVs for packed roughness, simple exterior cylindrical/box parts.
    if not o.data.uv_layers:
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(60),island_margin=.015);bpy.ops.object.mode_set(mode='OBJECT')
    made.append(o);return o

def box(name,center,scale,mat=steel,bevel=.00065,parent=hardware):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o=bpy.context.object;o.location=center;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return finish(o,name,mat,parent,bevel)

def revolved(name,profile,center_y=0,center_z=0,mat=steel,parent=hardware,n=64):
    verts=[(x,center_y+r*math.sin(2*math.pi*j/n),center_z+r*math.cos(2*math.pi*j/n)) for x,r in profile for j in range(n)]
    faces=[]
    for k in range(len(profile)-1):
        for j in range(n):faces.append((k*n+j,(k+1)*n+j,(k+1)*n+(j+1)%n,k*n+(j+1)%n))
    faces.append(tuple(range(n)));faces.append(tuple(reversed([(len(profile)-1)*n+j for j in range(n)])))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o)
    for f in mesh.polygons:f.use_smooth=len(f.vertices)==4
    return finish(o,name,mat,parent)

def tube_between(name,points,radius,mat=steel,parent=hardware,n=32):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=4;curve.bevel_depth=radius;curve.bevel_resolution=4;curve.use_fill_caps=True
    s=curve.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for b,p in zip(s.bezier_points,points):b.co=p;b.handle_left_type='AUTO';b.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,curve);bpy.context.scene.collection.objects.link(o)
    bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.ops.object.convert(target='MESH')
    for f in o.data.polygons:f.use_smooth=True
    return finish(o,name,mat,parent)

# Receiver exterior: bed rail supports exposed bolt, rear bridge and front ring.
box('ReceiverBed',(-.148,0,-.019),(.216,.045,.007),steel,.001)
box('ReceiverLeftRail',(-.146,.020,-.003),(.145,.008,.026),steel,.001)
box('ReceiverRightRail',(-.144,-.020,-.012),(.150,.008,.014),steel,.0008)
box('HandleInletExteriorPlate',(-.163,-.023,-.022),(.044,.006,.014),steel,.001)
revolved('ReceiverFrontRing',[(-.077,.019),(-.075,.020),(-.046,.020),(-.044,.0185)],mat=steel)
revolved('ReceiverRearBridge',[(-.180,.018),(-.178,.019),(-.157,.019),(-.155,.018)],mat=steel)
revolved('VisibleBoltCylinder',[(-.231,.010),(-.229,.0118),(-.076,.0118),(-.074,.011)],mat=edge,parent=bolt)
revolved('BoltRearShroud',[(-.238,.008),(-.237,.0125),(-.209,.0125),(-.207,.011)],mat=steel,parent=bolt)
box('BoltExtractorExterior',(-.146,.007,.010),(.111,.005,.0036),steel,.00055,parent=bolt)
revolved('BoltHandleCollar',[(-.180,.0118),(-.178,.015),(-.164,.015),(-.162,.012)],mat=steel,parent=bolt)
tube_between('BoltHandleStem',[(-.169,-.011,0),(-.171,-.025,-.008),(-.164,-.047,-.030),(-.158,-.056,-.052)],.0053,parent=bolt)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=.0125,location=(-.158,-.057,-.055))
knob=bpy.context.object
for f in knob.data.polygons:f.use_smooth=True
finish(knob,'BoltHandleKnob',steel,bolt)
box('BoltSafetyLeaf',(-.228,.007,.018),(.018,.006,.014),steel,.001,parent=bolt)
box('RearTang',(-.247,0,-.018),(.027,.016,.005),steel,.0008)

# Visible sight housing, tangent leaf and notch. No readable ballistic scale.
revolved('BarrelRearExterior',[(-.045,.015),(-.039,.014),(.126,.012)],mat=steel)
box('RearSightInletPlate',(.049,0,-.009),(.192,.031,.005),steel,.001)
box('RearSightBed',(.030,0,.013),(.126,.024,.007),steel,.001)
leaf=box('TangentSightLeaf',(.036,0,.023),(.118,.014,.004),edge,.00055)
leaf.rotation_euler.y=-.055
box('SightSlider',(.066,0,.028),(.016,.025,.009),steel,.00065)
for y in (-.006,.006):box('RearSightNotchEar',(-.020,y,.025),(.009,.004,.008),black,.00045)
for i in range(10):box('SightGraduation_%02d'%i,(-.004+i*.009,-.004,.026),(.0006,.0035,.00025),black,.00008)
for x in (-.023,.116):
    screw=revolved('SightPin_%s'%str(x),[(x-.002,.0035),(x+.002,.0035)],center_z=.021,mat=edge,n=32)

# Replace generated muzzle nubs and barrel loop artifact with an exterior tube.
band=revolved('FrontBandTransition',[(.408,.022),(.410,.023),(.437,.023),(.440,.021)],center_z=0,mat=steel)
band.scale.z=1.20;band.location.z=-.017
# Exterior mouth recess only: intentionally no internal bore/chamber geometry.
revolved('FrontBarrel',[(.430,.0078),(.433,.0076),(.550,.0066),(.5525,.0062),(.5525,.0038),(.548,.0038)],mat=steel,n=96)
box('MuzzleCavityDark',(.548,0,0),(.0005,.0068,.0068),black,.0001)
revolved('FrontSightSaddle',[(.522,.0067),(.523,.008),(.533,.008),(.534,.0067)],mat=steel)
box('FrontSightBase',(.529,0,.0085),(.015,.011,.0045),steel,.0007)
box('FrontSightBlade',(.529,0,.014),(.008,.0026,.009),black,.0005)
box('ExteriorBayonetLug',(.447,0,-.030),(.030,.010,.008),steel,.0015)
box('LugSupport',(.433,0,-.030),(.010,.015,.014),steel,.001)

# Render-independent metrics measured on evaluated modifiers, not source cubes.
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();stats=[]
for o in [body]+made+caps:
    eo=o.evaluated_get(deps);em=eo.to_mesh();em.calc_loop_triangles()
    stats.append({'name':o.name,'parent':o.parent.name,'triangles':len(em.loop_triangles),'uvLayers':[u.name for u in em.uv_layers],'materials':[mat.name for mat in em.materials]});eo.to_mesh_clear()
total=sum(s['triangles'] for s in stats);assert total<=350000
report={'stage':'local structural refinement; production approval pending','revision':a.revision,'blender':bpy.app.version_string,'sourceSha256':BASE_SHA,
        'axisFrame':[list(r) for r in frame],'exactCutVolumes':volumes,'unchangedOriginalFaces':retained,'removedOriginalFaces':deleted,'clippedOriginalFaces':cut_faces,
        'unchangedCornerUvMaxError':uv_max_error,'stockGlobalWeldOrDecimate':False,'completeVisibleBoltAssembly':True,'internalMechanismOrReload':False,
        'parts':stats,'derivedInterfaceCaps':cap_stats,'triangles':total,'runtimeLodReady':False,'sling':'Museum replacement retained, historical approval pending'}
assert uv_max_error==0
(out/'refinement.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
# Save source with editable bevel stacks; export only geometry/semantic roots.
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'Kar98k_RefinedMaster_V2.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in [root,hardware,bolt,body]+made+caps:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'Kar98k_RefinedMaster_V2.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=False)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==BASE_SHA
print(json.dumps({'output':str(out),'triangles':total,'retainedFaces':retained,'originalUvError':uv_max_error}),flush=True)
