"""Extract only the licensed equipment grenade section; preserve the source."""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
src=root/'tmp/g1-grenade-models-20261011/asset_lookup/equipment_v1'
identity=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v1'
out=root/('Assets/LocalWorking/Experiments/GrenadeModels/20261011/frag_inspection_'+identity)
out.mkdir(parents=True,exist_ok=False)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(src/'Equipment.glb'))
o=next(o for o in bpy.context.scene.objects if o.type=='MESH' and len(o.data.vertices)>100)
for other in list(bpy.data.objects):
    if other!=o:bpy.data.objects.remove(other,do_unlink=True)
o.modifiers.clear();o.parent=None
bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.material_index!=8],context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bm.to_mesh(o.data);bm.free();o.data.update()
coords=[v.co.copy() for v in o.data.vertices];mins=Vector([min(v[i] for v in coords) for i in range(3)]);maxs=Vector([max(v[i] for v in coords) for i in range(3)]);center=(mins+maxs)/2
for v in o.data.vertices:v.co-=center
o.matrix_world.identity();o.name='ExistingMkIISection'
o.data.materials.clear();m=bpy.data.materials.new('MkIIPBR');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
for key,filename in [('D','T_MKII_FRAG_D.tga'),('N','T_MKII_FRAG_N.tga'),('ORM','T_MKII_FRAG_ORM.tga')]:
    image=bpy.data.images.load(str(src/filename));image.colorspace_settings.name='sRGB' if key=='D' else 'Non-Color';tex=n.new('ShaderNodeTexImage');tex.image=image
    if key=='D':l.new(tex.outputs['Color'],p.inputs['Base Color'])
    elif key=='N':normal=n.new('ShaderNodeNormalMap');l.new(tex.outputs['Color'],normal.inputs['Color']);l.new(normal.outputs['Normal'],p.inputs['Normal'])
    else:sep=n.new('ShaderNodeSeparateColor');l.new(tex.outputs['Color'],sep.inputs['Color']);l.new(sep.outputs['Green'],p.inputs['Roughness']);l.new(sep.outputs['Blue'],p.inputs['Metallic'])
o.data.materials.append(m)
for f in o.data.polygons:f.material_index=0
o.data.calc_loop_triangles()
report={'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'section_bbox_m':list(maxs-mins),'uv_layers':len(o.data.uv_layers)}
(out/'REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(report,flush=True)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('StudioWorld');scene.world.color=(.3,.3,.3)
target=Vector((0,0,0));size=max(maxs-mins)*1.5
for name,loc in [('key',(1,-1,1)),('fill',(-1,-.5,.5))]:
    d=bpy.data.lights.new(name,'AREA');d.energy=50;d.size=.5;ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=Vector(loc)*.5;ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
for name,loc in [('front',(.18,-.3,.18)),('rear',(-.18,.3,.10)),('side',(.3,0,.1))]:
    d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=size;scene.camera=ob;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ExistingMkIIInspection.blend'))
