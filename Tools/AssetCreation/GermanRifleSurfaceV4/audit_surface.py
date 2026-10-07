"""Independent read-only audit of rejected material proofs, NOT visual acceptance."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-surface-v4'
SOURCE=ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-parts-v3/incoming/kar98k-parts-v3-0-recovery.glb'
p=argparse.ArgumentParser();p.add_argument('--output',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);out=Path(a.output).resolve()
assert not out.exists(),'Preserve occupied evidence'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(SOURCE))
norm=Matrix(json.loads((ROOT/'Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-v1/evidence/incoming_v2/inspection.json').read_text())['normalizationMatrix'])
original={}
root=bpy.data.objects.new('AuditSourceRoot',None);bpy.context.scene.collection.objects.link(root)
for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
    # Match the author's Blender transform application, rather than a different
    # chained float32 matrix multiplication (v1 residual was 1.19e-7 m).
    w=norm@o.matrix_world;o.parent=root;o.matrix_world=w
    bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    original[len(o.data.polygons)]={'positions':np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]),
        'faces':np.array([tuple(f.vertices) for f in o.data.polygons]),'uv':np.array([tuple(v.uv) for v in o.data.uv_layers.active.data])}
checks=[]
for identity in ('interface_v1b','contour_v1'):
    bpy.ops.wm.open_mainfile(filepath=str(BASE/identity/'Kar98k_SurfaceMaster_V4.blend'),load_ui=False,use_scripts=False)
    parts=[]
    for o in [o for o in bpy.context.scene.objects if o.type=='MESH']:
        old=original[len(o.data.polygons)]
        xyz=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);uv=np.array([tuple(v.uv) for v in o.data.uv_layers.active.data])
        delta=np.abs(xyz-old['positions']).max()
        parts.append({'name':o.name,'vertices':len(xyz),'faces':len(o.data.polygons),'maxAbsSourcePositionDelta':float(delta),
            'sourcePositionsExact':bool(np.array_equal(xyz,old['positions'])),'faceIndicesExact':bool(np.array_equal(old['faces'],np.array([tuple(f.vertices) for f in o.data.polygons]))),
            'uvExact':bool(np.array_equal(old['uv'],uv))})
    image_checks=[{'name':i.name,'sha256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest()} for i in bpy.data.images if i.packed_file]
    checks.append({'identity':identity,'parts':parts,'packedImages':image_checks,'geometryNotRefined':True,'visualAccepted':False})
result={'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'blender':bpy.app.version_string,'checks':checks,
        'allSourceGeometryAndUvPreserved':all(c['sourcePositionsExact'] and c['faceIndicesExact'] and c['uvExact'] for x in checks for c in x['parts']),
        'visualAccepted':False,'productionAccepted':False}
out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result),flush=True)
assert result['allSourceGeometryAndUvPreserved']
