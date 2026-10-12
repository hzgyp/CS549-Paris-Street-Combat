"""Exterior-only inert game prop. No internal explosive/igniter mechanisms."""
import bpy, math, json, sys, argparse, hashlib
from pathlib import Path
from mathutils import Vector
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GrenadeModels/20261011/smoke'
ap=argparse.ArgumentParser();ap.add_argument('--stage',choices=['geometry','finish','verify'],required=True);ap.add_argument('--identity',default='v1')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT=BASE/(args.stage+'_'+args.identity);assert not OUT.exists(),'Preserve artifact identity'
OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('StudioWorld');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.15,.17,.19,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
scene.view_settings.view_transform='AgX'
scene.view_settings.exposure=-2.5
parts=[]

def material(name,color,metal,rough,paint=False):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    if paint:
        coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=85;noise.inputs['Detail'].default_value=3
        l.new(coord.outputs['Generated'],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB')
        r.color_ramp.elements[0].position=.25;r.color_ramp.elements[0].color=(.13,.145,.14,1)
        r.color_ramp.elements[1].position=.72;r.color_ramp.elements[1].color=(.26,.28,.27,1)
        l.new(noise.outputs['Fac'],r.inputs['Fac']);l.new(r.outputs['Color'],p.inputs['Base Color'])
        r.color_ramp.elements.new(.79).color=(.13,.049,.022,1)
        edge=n.new('ShaderNodeNewGeometry');wear=n.new('ShaderNodeValToRGB')
        wear.color_ramp.elements[0].position=.515;wear.color_ramp.elements[0].color=(0,0,0,1)
        wear.color_ramp.elements[1].position=.58;wear.color_ramp.elements[1].color=(.6,.6,.6,1)
        mix=n.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.28,.29,.23,1)
        l.new(edge.outputs['Pointiness'],wear.inputs['Fac']);l.new(wear.outputs['Color'],mix.inputs[0]);l.new(r.outputs['Color'],mix.inputs[1]);l.new(mix.outputs[0],p.inputs['Base Color'])
        roughness=n.new('ShaderNodeMapRange');roughness.inputs['To Min'].default_value=.46;roughness.inputs['To Max'].default_value=.78
        l.new(noise.outputs['Fac'],roughness.inputs['Value']);l.new(roughness.outputs['Result'],p.inputs['Roughness'])
        grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=420;grain.inputs['Detail'].default_value=2
        l.new(coord.outputs['Generated'],grain.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.00012
        l.new(grain.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m
paint=material('WornOlivePaint',(.12,.16,.055),.38,.62,True)
steel=material('EdgeSteel',(.25,.28,.23),.88,.43)
rubber=material('DarkSealingRubber',(.014,.02,.013),0,.88)
ivory=material('AgedStencil',(.65,.46,.07),.05,.76)
clay=material('ReviewClay',(.42,.44,.46),0,.65)

def finish(o,mat):
    o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    parts.append(o);return o

def lathe(name,profile,mat,segments=96):
    vertices=[];rings=[];faces=[]
    for radius,z in profile:
        if radius==0:rings.append([len(vertices)]);vertices.append((0,0,z/100))
        else:
            ring=[]
            for i in range(segments):
                a=2*math.pi*i/segments;ring.append(len(vertices));vertices.append((radius*math.cos(a)/100,radius*math.sin(a)/100,z/100))
            rings.append(ring)
    for a,b in zip(rings,rings[1:]):
        for i in range(segments):
            j=(i+1)%segments
            if len(a)==1:faces.append((a[0],b[j],b[i]))
            elif len(b)==1:faces.append((a[i],a[j],b[0]))
            else:faces.append((a[i],a[j],b[j],b[i]))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);return finish(o,mat)

def torus(name,r,t,z,mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=8,location=(0,0,z/100),major_radius=r/100,minor_radius=t/100)
    o=bpy.context.object;o.name=name;return finish(o,mat)

def box(name,location,size,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=Vector(location)/100);o=bpy.context.object;o.name=name;o.dimensions=Vector(size)/100
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel=o.modifiers.new('ManufacturedRoundedEdge','BEVEL');bevel.width=.0008;bevel.segments=3
    weighted=o.modifiers.new('StableManufacturedNormals','WEIGHTED_NORMAL');weighted.keep_sharp=True
    return finish(o,mat)

def tube(name,points,r,mat):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=r/100;c.bevel_resolution=3
    s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,xyz in zip(s.bezier_points,points):p.co=Vector(xyz)/100;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);c.materials.append(mat);parts.append(o);return o

if args.stage!='verify':
    # 1943 external silhouette: gray round can, rolled ends, closed cap,
    # attached flat lever and ring. Exterior only, no internal construction.
    lathe('ClosedSmokeCan',[(0,-6.25),(2.9,-6.25),(3.12,-6.18),(3.175,-6.05),(3.175,5.98),(3.10,6.15),(2.97,6.25),(0,6.25)],paint)
    torus('BottomRolledSeam',3.12,.09,-6.12,steel)
    torus('UpperRolledSeam',3.12,.085,6.10,steel)
    lathe('ClosedTopCollar',[(0,6.25),(1.12,6.25),(1.12,6.85),(.96,7.05),(0,7.05)],steel,64)
    box('ClosedExternalCap',(0,0,7.30),(2.05,1.52,1.1),steel)
    # Continuous ribbon follows the top and one side; width is visible in 3D.
    profile=[(-1.0,7.95),(1.10,7.95),(1.8,7.65),(3.28,6.18),(3.36,5.8),(3.36,-4.45)]
    vertices=[]
    for x,z in profile:
        for y,dz in [(-.65,-.075),(.65,-.075),(.65,.075),(-.65,.075)]:vertices.append((x/100,y/100,(z+dz)/100))
    faces=[(3,2,1,0)]
    for i in range(len(profile)-1):
        for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
    k=(len(profile)-1)*4;faces.append((k,k+1,k+2,k+3))
    mesh=bpy.data.meshes.new('BentLever');mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new('ConnectedBentLever',mesh);bpy.context.collection.objects.link(o)
    b=o.modifiers.new('RoundedLeverEdges','BEVEL');b.width=.00055;b.segments=3;finish(o,steel)
    ring=torus('AttachedPullRing',1.32,.095,7.17,steel);ring.rotation_euler.x=math.pi/2;ring.location.y=-.009
    tube('RingAttachment',[(0,-.6,7.6),(0,-1.0,7.6),(0,-1.0,6.3)],.07,steel)
    for z in [-2.4,3.9]:lathe('YellowIdentificationBand',[(3.18,z-.26),(3.18,z+.26)],ivory)
    # Curved exterior lettering: no borrowed photo/modern lot number.
    for text,z,size in [('HC',1.1,1.42),('SMOKE',-4.25,.84)]:
        spacing=size*.68
        for i,char in enumerate(text):
            angle=(i-(len(text)-1)/2)*spacing/3.18
            bpy.ops.object.text_add(location=(math.sin(angle)*.03187,-math.cos(angle)*.03187,z/100))
            o=bpy.context.object;o.name='CurvedStencil_'+char;o.data.body=char;o.data.align_x='CENTER';o.data.size=size/100;o.data.extrude=0;o.rotation_euler=(math.pi/2,0,angle);o.data.materials.append(ivory);parts.append(o)
    for o in list(parts):
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();mine=bpy.context.object;mine.name='ANM8SmokeExterior'
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=1.15,island_margin=.016,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
else:
    bpy.ops.import_scene.gltf(filepath=str(BASE/('finish_'+args.identity)/'ANM8Smoke.glb'))
    meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==1;mine=meshes[0]

def light(name,loc,power,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.025))-o.location).to_track_quat('-Z','Y').to_euler()

def render_views(prefix,override=None):
    light('Key',(.5,-.7,.8),75,.6);light('Fill',(-.55,-.2,.45),45,.6);light('Rim',(.1,.5,.65),65,.45)
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.064));floor=bpy.context.object;floor.name='StudioOnlyGround';floor.data.materials.append(material('StudioFloor',(.10,.115,.12),0,.8))
    for name,loc in [('three_quarter',(.42,-.48,.37)),('top',(0,-.005,.43)),('side',(0,-.58,.01)),('rear',(-.44,.36,.28))]:
        d=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(cam);cam.location=loc;cam.rotation_euler=(Vector((0,0,.01))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=.21;scene.camera=cam
        scene.view_layers[0].material_override=override;scene.render.filepath=str(OUT/(prefix+'_'+name+'.png'));bpy.ops.render.render(write_still=True)
    scene.view_layers[0].material_override=None
    bpy.data.objects.remove(floor,do_unlink=True)
    for o in list(scene.objects):
        if o.type in ['LIGHT','CAMERA']:bpy.data.objects.remove(o,do_unlink=True)

mesh=mine.data;mesh.calc_loop_triangles();triangles=len(mesh.loop_triangles)
bounds=[mine.matrix_world@Vector(v) for v in mine.bound_box]
dimensions=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)]
assert 2000<=triangles<=15000,triangles
assert .06<dimensions[0]<.08 and .06<dimensions[1]<.075 and .14<dimensions[2]<.17,dimensions

if args.stage=='geometry':
    render_views('clay',clay);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ANM8SmokeGeometry.blend'))
elif args.stage=='finish':
    bpy.context.view_layer.objects.active=mine;mine.select_set(True)
    images={}
    for kind in ['albedo','roughness','metallic','normal']:
        img=bpy.data.images.new('Smoke_'+kind,1024,1024,alpha=False);img.colorspace_settings.name='sRGB' if kind=='albedo' else 'Non-Color';images[kind]=img
        originals=[]
        for mat in mine.data.materials:
            nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=nodes.get('Principled BSDF');output=nodes.get('Material Output')
            target=nodes.new('ShaderNodeTexImage');target.image=img;nodes.active=target
            if kind in ['roughness','metallic']:
                original=output.inputs['Surface'].links[0].from_socket;links.remove(output.inputs['Surface'].links[0]);em=nodes.new('ShaderNodeEmission');socket=p.inputs[kind.title()]
                if socket.is_linked:links.new(socket.links[0].from_socket,em.inputs['Color'])
                else:em.inputs['Color'].default_value=(socket.default_value,)*3+(1,)
                links.new(em.outputs[0],output.inputs['Surface']);originals.append((mat,original,em))
        scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True;scene.render.bake.margin=8
        bpy.ops.object.bake(type='DIFFUSE' if kind=='albedo' else ('NORMAL' if kind=='normal' else 'EMIT'))
        img.filepath_raw=str(OUT/('smoke_'+kind+'.png'));img.file_format='PNG';img.save()
        for mat,original,em in originals:mat.node_tree.links.new(original,mat.node_tree.nodes['Material Output'].inputs['Surface']);mat.node_tree.nodes.remove(em)
    packed=np.ones((1024*1024,4),dtype=np.float32)
    for channel,key in [(1,'roughness'),(2,'metallic')]:packed[:,channel]=np.array(images[key].pixels[:],dtype=np.float32).reshape((-1,4))[:,0]
    orm=bpy.data.images.new('Smoke_ORM',1024,1024,alpha=False);orm.colorspace_settings.name='Non-Color';orm.pixels.foreach_set(packed.ravel());orm.filepath_raw=str(OUT/'smoke_orm.png');orm.file_format='PNG';orm.save()
    final=bpy.data.materials.new('ANM8SmokeBakedPBR');final.use_nodes=True;n=final.node_tree.nodes;l=final.node_tree.links;p=n.get('Principled BSDF')
    color=n.new('ShaderNodeTexImage');color.image=images['albedo'];l.new(color.outputs['Color'],p.inputs['Base Color'])
    tex=n.new('ShaderNodeTexImage');tex.image=orm;sep=n.new('ShaderNodeSeparateColor');l.new(tex.outputs['Color'],sep.inputs['Color']);l.new(sep.outputs['Green'],p.inputs['Roughness']);l.new(sep.outputs['Blue'],p.inputs['Metallic'])
    normal=n.new('ShaderNodeTexImage');normal.image=images['normal'];nm=n.new('ShaderNodeNormalMap');l.new(normal.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],p.inputs['Normal'])
    mine.data.materials.clear();mine.data.materials.append(final)
    for poly in mesh.polygons:poly.material_index=0
    bpy.ops.object.select_all(action='DESELECT');mine.select_set(True);bpy.context.view_layer.objects.active=mine
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'ANM8Smoke.blend'))
    bpy.ops.export_scene.gltf(filepath=str(OUT/'ANM8Smoke.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    mesh.calc_loop_triangles();mesh.calc_tangents(uvmap=mesh.uv_layers.active.name)
    verts=[]
    for tri in mesh.loop_triangles:
        for loop_id in [tri.loops[0],tri.loops[2],tri.loops[1]]:
            loop=mesh.loops[loop_id];v=mesh.vertices[loop.vertex_index].co;normal=mesh.corner_normals[loop_id].vector;tangent=loop.tangent;uv=mesh.uv_layers.active.data[loop_id].uv
            verts.append([v.x*100,-v.y*100,v.z*100,normal.x,-normal.y,normal.z,tangent.x,-tangent.y,tangent.z,loop.bitangent_sign,uv.x,1-uv.y])
    (OUT/'smoke_geometry.json').write_text(json.dumps({'schema':1,'triangles':triangles,'vertices':verts,'dimensions_m':dimensions},separators=(',',':')),encoding='utf-8')
    render_views('pbr')
else:render_views('fresh_glb')

report={'stage':args.stage,'blender':bpy.app.version_string,'triangles':triangles,'dimensions_m':dimensions,'uv_layers':len(mesh.uv_layers),'materials':[m.name for m in mine.data.materials],'default_gray_accepted':False,'purpose':'exterior-only AN-M8-inspired gray/yellow 1943 game prop, approximate art dimensions; no mechanism or exact lot certification'}
(OUT/'REPORT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('PRESSURE_MINE_STAGE_COMPLETE',json.dumps(report),flush=True)
