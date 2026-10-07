"""Fresh GLB gates plus external-handle exploded diagnostic (not reload)."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import bpy
from mathutils import Vector

p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--expected',required=True);p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(a.input).resolve();expected=json.loads(Path(a.expected).read_text());out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False)
raw=source.read_bytes();sha=hashlib.sha256(raw).hexdigest()
assert raw[:4]==b'glTF'
length,kind=struct.unpack_from('<II',raw,12);assert kind==0x4E4F534A
gltf=json.loads(raw[20:20+length])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];checks={}
root=bpy.data.objects.get('Kar98k_WorldCandidate_Root');handle=bpy.data.objects.get('Kar98k_VisibleBoltHandle_ONLY');body=bpy.data.objects.get('Kar98k_Body_WithMuseumSling')
checks['namedPartsAndRoot']=len(meshes)==2 and all(x is not None for x in (root,handle,body))
checks['parentHierarchy']=all(o.parent==root for o in meshes)
counts={};valid={}
for o in meshes:
    o.data.calc_loop_triangles();counts[o.name]=len(o.data.loop_triangles)
    copy=o.data.copy();valid[o.name]=not copy.validate(verbose=True,clean_customdata=False);bpy.data.meshes.remove(copy)
checks['sourceExportTriangleParity']=counts=={x['name']:x['triangles'] for x in expected['parts']}
checks['triangleBudget']=sum(counts.values())<=30000
checks['meshStructuralValidity']=all(valid.values())
checks['finiteVerticesUV']=all(math.isfinite(float(x)) for o in meshes for v in o.data.vertices for x in v.co) and all(o.data.uv_layers for o in meshes) and all(math.isfinite(float(x)) for o in meshes for layer in o.data.uv_layers for uv in layer.data for x in uv.uv)
points=[o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
dims=[max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)]
checks['scaleTolerance']=abs(dims[0]-1.105)<0.002
checks['packedTextures']=len([i for i in bpy.data.images if i.size[0]>0 and i.packed_file])>=2
checks['materialPresent']=all(o.data.materials for o in meshes)
checks['noExternalGLTFURIs']=all('uri' not in b for b in gltf.get('buffers',[])) and all('uri' not in i for i in gltf.get('images',[]))
checks['pivotExportParity']=handle is not None and (handle.location-Vector(expected['digitalPivot'])).length<1e-5
report={'artifact':str(source),'sha256':sha,'checks':checks,'technicalBasicPass':all(checks.values()),
        'trianglesByPart':counts,'totalTriangles':sum(counts.values()),'dimensions':dims,
        'glTFMaterials':gltf.get('materials',[]),
        'limitations':['No whole independent operating bolt','No mechanical/reload animation','No UE/history/visual production acceptance','Museum replacement sling retained','Nonmanifold/close-form risks require separate acceptance']}

scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
sh=scene.display.shading;sh.light='STUDIO';sh.color_type='OBJECT';sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD'
body.color=(0.40,0.43,0.48,1);handle.color=(0.95,0.47,0.09,1)
camdata=bpy.data.cameras.new('HandleDiagnostic_NotReload');cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam)
target=Vector((-0.16,-0.025,0.085));cam.location=target+Vector((0.05,-0.6,0.3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=0.30;scene.camera=cam
original=handle.location.copy();original_body_matrix=body.matrix_world.copy();original_body_coords=tuple(tuple(v.co) for v in body.data.vertices)
for label,offset in [('rest',Vector((0,0,0))),('exploded_not_reload',Vector((0,-0.055,0)))]:
    handle.location=original+offset;bpy.context.view_layer.update()
    scene.render.filepath=str(out/('handle_'+label+'.png'));bpy.ops.render.render(write_still=True)
handle.location=original;bpy.context.view_layer.update()
report['checks']['bodyUnchangedInHandleDiagnostic']=body.matrix_world==original_body_matrix and tuple(tuple(v.co) for v in body.data.vertices)==original_body_coords
report['checks']['restPoseRestored']=(handle.location-original).length<1e-7
report['checks']['inputBytesUnchanged']=hashlib.sha256(source.read_bytes()).hexdigest()==sha
report['technicalBasicPass']=all(report['checks'].values())
(out/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'technicalBasicPass':report['technicalBasicPass'],'checks':report['checks'],'triangles':report['totalTriangles'],'dimensions':dims}))
raise SystemExit(0 if report['technicalBasicPass'] else 1)
