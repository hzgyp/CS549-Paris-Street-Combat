"""Fresh glTF import: embedded material closure and alternate skin-weight evidence."""
import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalWorking/Validation/UE582/2026-09-30-v1/Evidence'
report = {'blender': bpy.app.version_string, 'models': [], 'errors': []}
for file in sorted((OUT / 'Exports').glob('*.glb')):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.import_scene.gltf(filepath=str(file))
        bones = {bone.name for obj in bpy.data.objects if obj.type == 'ARMATURE' for bone in obj.data.bones}
        meshes = []
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            sums = [sum(g.weight for g in v.groups if obj.vertex_groups[g.group].name in bones)
                    for v in obj.data.vertices]
            meshes.append({'name': obj.name, 'vertices': len(sums),
                'unweighted_vertices': sum(s < .00001 for s in sums),
                'weight_sum_outside_0_001': sum(abs(s - 1) > .001 for s in sums),
                'min_weight_sum': min(sums), 'max_weight_sum': max(sums),
                'uv_layers': len(obj.data.uv_layers)})
        images = [{'name': image.name, 'size': list(image.size),
                   'has_pixels': image.has_data, 'packed': bool(image.packed_file)}
                  for image in bpy.data.images if image.name not in ('Render Result', 'Viewer Node')]
        report['models'].append({'file': file.name, 'bones': len(bones),
                                 'meshes': meshes, 'images': images})
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'Exports' / (file.stem + '_baked_preview.blend')))
    except Exception as exc:
        report['errors'].append({'file': file.name, 'error': str(exc)})
    (OUT / 'blender_glb_audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('CS549_GLB_AUDIT_DONE', len(report['models']), len(report['errors']))
