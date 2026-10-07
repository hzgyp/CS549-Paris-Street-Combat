"""Read-only segmentation structure/shape audit, colored and isolated evidence.

No geometry repair, semantic label invention, export rewrite or acceptance claim.
Run from a clean Blender process with -- --input parts.glb --output NEW_DIR.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector, Matrix
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[3]
ORIGINAL=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/incoming/kar98k-base-v1.glb'
NORMAL_FILE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v2/inspection.json'
p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(a.input).resolve();out=Path(a.output).resolve()
out.mkdir(parents=True,exist_ok=False)
M=Matrix(json.loads(NORMAL_FILE.read_text())['normalizationMatrix'])

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def import_model(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.context.scene.objects if o.type=='MESH']

def points(objects):
    return np.array([list(o.matrix_world@v.co) for o in objects for v in o.data.vertices])

def triangles(objects):
    for o in objects:o.data.calc_loop_triangles()
    return sum(len(o.data.loop_triangles) for o in objects)

orig=import_model(ORIGINAL);op=points(orig);original_tri=triangles(orig)
original_images={i.name:digest(Path(i.filepath)) if i.filepath and Path(i.filepath).is_file() else
                 hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None for i in bpy.data.images}
parts=import_model(source);pp=points(parts)
if not parts:raise RuntimeError('No parts')
report={'stage':'semantic-part diagnostic only','sourceSha256':digest(source),
        'originalSha256':digest(ORIGINAL),'originalTriangles':original_tri,'resultTriangles':triangles(parts),
        'originalBounds':[op.min(axis=0).tolist(),op.max(axis=0).tolist()],
        'resultBounds':[pp.min(axis=0).tolist(),pp.max(axis=0).tolist()],
        'parts':[],'originalPackedImageHashes':original_images,
        'resultImages':[{'name':i.name,'size':list(i.size),'packed':bool(i.packed_file),
                         'packedSha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None} for i in bpy.data.images]}
# Raw world coordinates: do not fit scales/poses to conceal changed shape.
def distances(A,B):
    kd=KDTree(len(B))
    for i,v in enumerate(B):kd.insert(v,i)
    kd.balance();idx=np.linspace(0,len(A)-1,min(len(A),10000),dtype=int)
    d=np.array([kd.find(A[i])[2] for i in idx])
    return {'samples':len(d),'max':float(d.max()),'p95':float(np.percentile(d,95)),'mean':float(d.mean()),
            'units':'raw provider units; sampled nearest-vertex distance, not Hausdorff/surface/UV acceptance'}
report['resultToOriginal']=distances(pp,op);report['originalToResult']=distances(op,pp)
colors=[(.75,.25,.15,1),(.18,.50,.78,1),(.40,.70,.30,1),(.77,.60,.18,1),(.63,.33,.73,1),(.22,.70,.65,1)]
for i,o in enumerate(parts):
    raw=o.matrix_world.copy();q=np.array([list(raw@v.co) for v in o.data.vertices])
    report['parts'].append({'id':i,'cloudName':o.name,'triangles':len(o.data.loop_triangles),
        'vertices':len(o.data.vertices),'rawBounds':[q.min(axis=0).tolist(),q.max(axis=0).tolist()],
        'uvLayers':[u.name for u in o.data.uv_layers],
        'materialSlots':[s.material.name if s.material else None for s in o.material_slots],
        'internalDataWouldChange':o.data.copy().validate(clean_customdata=False),
        'semanticMeaning':'not inferred from cloud name'})
    o.parent=None;o.matrix_world=M@raw;o.color=colors[i%len(colors)]
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1440;scene.render.resolution_y=810;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.world=bpy.data.worlds.new('PartDiagnosticWorld')
scene.world.color=(.06,.07,.09)
sh=scene.display.shading;sh.light='STUDIO';sh.color_type='OBJECT';sh.show_cavity=True;sh.cavity_type='BOTH'
sh.background_type='WORLD';sh.show_object_outline=True
def render(name,eye,target=(0,0,0),scale=1.3):
    d=bpy.data.cameras.new(name);c=bpy.data.objects.new(name,d);scene.collection.objects.link(c)
    c.location=eye;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
    d.type='ORTHO';d.ortho_scale=scale;d.clip_start=.001;d.clip_end=100
    scene.camera=c;scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
render('colored_right',(0,-3,0));render('colored_top',(0,0,3))
render('colored_quarter',(.75,-2,1.2))
for i,o in enumerate(parts[:12]):
    for other in parts:other.hide_render=(other!=o)
    bpy.context.view_layer.update()
    q=[o.matrix_world@Vector(c) for c in o.bound_box]
    lo=Vector(tuple(min(v[k] for v in q) for k in range(3)));hi=Vector(tuple(max(v[k] for v in q) for k in range(3)))
    center=(lo+hi)/2;scale=max((hi-lo).length*1.15,.12)
    render('isolated_part_'+str(i),center+Vector((.6,-2,1.2)),center,scale)
for o in parts:o.hide_render=False
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'part_diagnostic.blend'))
report['isolatedViews']=min(len(parts),12)
(out/'audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'parts':len(parts),'triangles':report['resultTriangles'],'resultToOriginal':report['resultToOriginal']}))
