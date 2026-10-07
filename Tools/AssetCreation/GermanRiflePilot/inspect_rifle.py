"""Clean-process, non-destructive inspection of the single Aholo prop base.

Run with Blender --background --factory-startup --disable-autoexec --python ...
-- --input BASE.glb --output EVIDENCE_NEW_DIRECTORY. Refuses occupied outputs.
No semantic segmentation or acceptance is inferred from successful import.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix

sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser()
p.add_argument('--input',required=True)
p.add_argument('--output',required=True)
p.add_argument('--keep-pose',action='store_true')
p.add_argument('--keep-names',action='store_true')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(args.input).resolve();out=Path(args.output).resolve()
out.mkdir(parents=True,exist_ok=False)
sha=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
if not meshes: raise RuntimeError('No imported geometry')

def bounds(objects):
    points=[o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
    low=Vector(tuple(min(v[i] for v in points) for i in range(3)))
    high=Vector(tuple(max(v[i] for v in points) for i in range(3)))
    return low,high

lo,hi=bounds(meshes);rawlo,rawhi=lo.copy(),hi.copy()
points=np.array([list(o.matrix_world @ v.co) for o in meshes for v in o.data.vertices],dtype=float)
values,vectors=np.linalg.eigh(np.cov(points.T));long=Vector(vectors[:,np.argmax(values)].tolist())
# The provider pose is diagonal. Align the inspection frame, not the shape.
if long.y>0:long=-long
up=(Vector((0,0,1))-long*long.dot(Vector((0,0,1)))).normalized()
across=up.cross(long).normalized()
rotation=Matrix((long,across,up)).to_4x4()
aligned=np.array([list(rotation.to_3x3() @ Vector(v)) for v in points])
amin=Vector(aligned.min(axis=0).tolist());amax=Vector(aligned.max(axis=0).tolist())
length=(amax-amin).x
normalizer=Matrix.Scale(1.105/length,4) @ Matrix.Translation(-(amin+amax)/2) @ rotation
if args.keep_pose:normalizer=Matrix.Identity(4)
original_nodes=[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrixWorld':[list(r) for r in o.matrix_world]} for o in bpy.context.scene.objects]
for i,o in enumerate(meshes):
    if not args.keep_names:o.name=f'IncomingBase_{i:02d}'
    matrix=normalizer @ o.matrix_world
    o.parent=None
    o.matrix_world=matrix
    bpy.context.view_layer.objects.active=o
    o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.select_set(False)
bpy.context.view_layer.update()
lo,hi=bounds(meshes)

def topology(o):
    m=o.data;m.calc_loop_triangles()
    parents=list(range(len(m.vertices)))
    def find(i):
        while parents[i]!=i: parents[i]=parents[parents[i]];i=parents[i]
        return i
    for e in m.edges:
        a,b=map(find,e.vertices)
        if a!=b: parents[b]=a
    components={}
    for v in m.vertices:
        c=components.setdefault(find(v.index),{'vertices':0,'min':[float('inf')]*3,'max':[float('-inf')]*3})
        c['vertices']+=1
        for k in range(3):c['min'][k]=min(c['min'][k],v.co[k]);c['max'][k]=max(c['max'][k],v.co[k])
    uses={}
    for face in m.polygons:
        for edge in face.edge_keys:uses[edge]=uses.get(edge,0)+1
    return {'name':o.name,'vertices':len(m.vertices),'triangles':len(m.loop_triangles),
            'uvLayers':[u.name for u in m.uv_layers],
            'materialSlots':[s.material.name if s.material else None for s in o.material_slots],
            'boundaryEdges':sum(v==1 for v in uses.values()),'nonmanifoldOverusedEdges':sum(v>2 for v in uses.values()),
            'degeneratePolygons':sum(f.area<1e-12 for f in m.polygons),
            'indexComponentCount':len(components),
            'indexComponentsLargest20':sorted(components.values(),key=lambda c:c['vertices'],reverse=True)[:20]}

report={'stage':'incoming geometry/appearance review; not accepted',
        'blender':bpy.app.version_string,'input':str(source),'inputSha256':sha,
        'rawBounds':{'min':list(rawlo),'max':list(rawhi)},
        'principalAxis':list(long),'normalizationMatrix':[list(r) for r in normalizer],
        'displayDimensions':list(hi-lo),'displayScaleRule':'principal long-axis extent 1.105m; orientation only, no shape edit',
        'meshes':[topology(o) for o in meshes],
        'materials':[], 'images':[], 'originalImportedNodes':original_nodes,'keepPose':args.keep_pose}
for mat in bpy.data.materials:
    report['materials'].append({'name':mat.name,'nodes':[n.bl_idname for n in mat.node_tree.nodes] if mat.use_nodes else []})
for img in bpy.data.images:
    report['images'].append({'name':img.name,'size':list(img.size),'packed':bool(img.packed_file),'source':img.source})
for o in meshes:
    diagnostic=o.data.copy()
    report.setdefault('meshValidationDiagnostic',[]).append({'object':o.name,'wouldChange':diagnostic.validate(verbose=True,clean_customdata=False)})
    bpy.data.meshes.remove(diagnostic)
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    report.setdefault('weldedDiagnostic',[]).append({'object':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),
        'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges)})
    bm.free()
(out/'inspection.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
scene.render.resolution_x=1440;scene.render.resolution_y=810;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world=bpy.data.worlds.new('InspectionWorld');scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.14,0.16,0.19,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0.6
scene.view_settings.view_transform='AgX'

def camera(name,eye,target=(0,0,0),scale=1.30):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);scene.collection.objects.link(o)
    o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    data.type='ORTHO';data.ortho_scale=scale;data.clip_start=0.001;data.clip_end=100
    return o
cams={
 'right_side':camera('Reference_RightSide_1736212',(0,-3,0)),
 'left_side':camera('Reference_LeftSide_1736206',(0,3,0)),
 'top':camera('Reference_TopDetail_1736128',(0,0,3)),
 'bottom':camera('Reference_BottomDetail_1736089',(0,0,-3)),
 'three_quarter':camera('Depth_ThreeQuarter',(0.75,-2,1.2)),
 'reverse_quarter':camera('Depth_ReverseQuarter',(-0.75,2,1.2)),
}
# Clay views prevent textures concealing negative-space and thickness defects.
scene.render.engine='BLENDER_WORKBENCH'
sh=scene.display.shading;sh.light='STUDIO';sh.color_type='SINGLE';sh.single_color=(0.62,0.65,0.69)
sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.show_specular_highlight=True
sh.background_type='WORLD';sh.show_object_outline=False
for name,cam in cams.items():
    scene.camera=cam;scene.render.filepath=str(out/('clay_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
for name,position,energy,size in [('Key',(0,-1.2,2),120,2),('Fill',(0,1,1),65,1.5),('Rim',(-0.3,0.5,1.6),75,1)]:
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=position
    o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
for name in ('right_side','left_side','top','three_quarter'):
    scene.camera=cams[name];scene.render.filepath=str(out/('pbr_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
scene.camera=cams['three_quarter']
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/'incoming_inspection.blend'))
if hashlib.sha256(source.read_bytes()).hexdigest()!=sha:raise RuntimeError('Incoming bytes changed')
print(json.dumps({'inspection':str(out),'triangles':sum(x['triangles'] for x in report['meshes']),'inputUnchanged':True}),flush=True)
