"""One bounded local candidate; re-run from immutable base, never generated edits."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector, Matrix

sys.stdout.reconfigure(encoding='utf-8')
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
p.add_argument('--round',type=int,choices=(1,2),default=2)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
root=Path(__file__).resolve().parents[3]
store=root/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1'
source=store/'incoming/kar98k-base-v1.glb'
sha=hashlib.sha256(source.read_bytes()).hexdigest()
assert sha=='a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60'
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
inspection=json.loads((store/'evidence/incoming_v2/inspection.json').read_text())
normalizer=Matrix(inspection['normalizationMatrix'])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==1
body=meshes[0];matrix=normalizer @ body.matrix_world;body.parent=None;body.matrix_world=matrix
bpy.context.view_layer.objects.active=body
body.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
body.name='Kar98k_Body_WithMuseumSling'
# Source-derived display coordinates in meters, not internal engineering data.
# Only the exterior downturned handle protrusion; complete bolt remains a gap.
selection={'x':[-0.195,-0.125],'yBelow':-0.025,'zAbove':0.040}
for face in body.data.polygons:
    c=face.center
    face.select=selection['x'][0]<c.x<selection['x'][1] and c.y<selection['yBelow'] and c.z>selection['zAbove']
selected=sum(f.select for f in body.data.polygons)
if not 100<selected<15000:raise RuntimeError('Handle selection unsafe: '+str(selected))
bpy.context.tool_settings.mesh_select_mode=(False,False,True)
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.separate(type='SELECTED');bpy.ops.object.mode_set(mode='OBJECT')
parts=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(parts)==2
handle=next(o for o in parts if o!=body);handle.name='Kar98k_VisibleBoltHandle_ONLY'
stats=[]
for o,goal in ((body,27500),(handle,1400)):
    bm=bmesh.new();bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    # Preserve source outer appearance; no arbitrary global hole-fill/remesh.
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
    cuts=[e for e in bm.edges if e.is_boundary and all(selection['x'][0]-0.003<v.co.x<selection['x'][1]+0.003 for v in e.verts)
          and (abs(sum(v.co.y for v in e.verts)/2-selection['yBelow'])<0.003 or abs(sum(v.co.z for v in e.verts)/2-selection['zAbove'])<0.003)]
    if cuts:bmesh.ops.holes_fill(bm,edges=cuts,sides=0)
    bm.to_mesh(o.data);bm.free();o.data.update()
    o.data.calc_loop_triangles();before=len(o.data.loop_triangles)
    bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('BoundedWorldReduction','DECIMATE');mod.ratio=min(1,goal/before)
    mod.use_collapse_triangulate=True
    bpy.ops.object.modifier_apply(modifier=mod.name)
    validation_changed=o.data.validate(verbose=True,clean_customdata=True) if a.round==2 else None
    o.data.update()
    for f in o.data.polygons:f.use_smooth=True
    o.data.calc_loop_triangles()
    stats.append({'name':o.name,'trianglesBeforeReduction':before,'triangles':len(o.data.loop_triangles),'uvLayers':[u.name for u in o.data.uv_layers], 'meshValidationChanged':validation_changed})
# Defined glTF-compatible scalar roughness; inherited UV/color/metallic preserved.
for mat in bpy.data.materials:
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
    rough=shader.inputs['Roughness']
    for link in list(rough.links):links.remove(link)
    rough.default_value=0.58

assembly=bpy.data.objects.new('Kar98k_WorldCandidate_Root',None);bpy.context.scene.collection.objects.link(assembly)
for o in parts:o.parent=assembly
assembly['status']='UNSELECTED WORLD CANDIDATE; complete bolt, shape, UE/history acceptance pending'
assembly['source_sha256']=sha
handle['part_limit']='Visible handle only; not entire operating bolt'
handle['pivot_limit']='Approximate external attachment; visual digital prop only'
pivot=Vector((-0.16,-0.025,0.105))
handle.data.transform(Matrix.Translation(-pivot));handle.location=pivot
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
report={'stage':'bounded candidate round'+str(a.round)+', unaccepted','selection':selection,'selectedSourceFaces':selected,
        'sourceSha256':sha,'parts':stats,'completeBoltSeparated':False,'slingRetained':'Museum replacement condition, not German-issued approval',
        'materialChange':'roughness set to glTF-compatible0.58; original color/metallic images retained',
        'digitalPivot':list(pivot),'triangles':sum(s['triangles'] for s in stats)}
(out/'adaptation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(out/('Kar98k_WorldCandidate_v'+str(a.round)+'.blend')))
bpy.ops.object.select_all(action='DESELECT')
for o in parts+[assembly]:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/('Kar98k_WorldCandidate_v'+str(a.round)+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
print(json.dumps(report),flush=True)
