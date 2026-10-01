"""Fresh exchange/source checks independent of the repair's live Blender state."""
import bpy
import hashlib
import json
import math
import os
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = Path(os.environ.get('CS549_ASSET_LAB', ROOT / 'Assets/LocalWorking/Validation/UE582/2026-09-30-v1'))
OUT = LAB / 'Evidence/Repair20261001'
DEST = OUT / 'Exchange'
repair = json.loads((OUT / 'exchange_repair.json').read_text(encoding='utf-8'))
expected = {r['file']: r for r in repair['meshes'] + repair['animations']}
report = {'blender': bpy.app.version_string, 'meshes': [], 'animations': [], 'sources': [], 'errors': []}


def bone_map():
    return {b.name: b.parent.name if b.parent else None for rig in bpy.data.objects if rig.type == 'ARMATURE' for b in rig.data.bones}


for file in sorted(DEST.glob('*.fbx')):
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.render.fps = 30
        bpy.ops.import_scene.fbx(filepath=str(file), automatic_bone_orientation=False, use_anim=file.stem.startswith('Rifle_'))
        checksum = hashlib.sha256(file.read_bytes()).hexdigest()
        hierarchy = bone_map()
        if file.stem.startswith('Rifle_'):
            fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
            action = list(bpy.data.actions)[0]
            start, end = action.frame_range
            seconds = (end - start) / fps
            report['animations'].append({'file': file.name, 'sha256': checksum, 'fps': fps, 'seconds': seconds,
                'error_seconds': abs(seconds - expected[file.name]['source_seconds']),
                'frame_range': [start, end], 'bones': len(hierarchy)})
        else:
            bad, unweighted = 0, 0
            triangles = 0
            for obj in [o for o in bpy.data.objects if o.type == 'MESH']:
                obj.data.calc_loop_triangles()
                triangles += len(obj.data.loop_triangles)
                if hierarchy:
                    for vertex in obj.data.vertices:
                        weights = [g.weight for g in vertex.groups if obj.vertex_groups[g.group].name in hierarchy]
                        unweighted += not weights
                        bad += bool(weights) and abs(sum(weights) - 1) > .001
            report['meshes'].append({'file': file.name, 'sha256': checksum, 'bad_weight_sums': bad, 'unweighted': unweighted,
                'triangles': triangles, 'same_triangles': triangles == expected[file.name]['before']['triangles'],
                'same_hierarchy': hierarchy == expected[file.name]['before']['hierarchy']})
    except Exception:
        report['errors'].append({'file': file.name, 'error': traceback.format_exc()})

for file in sorted(DEST.glob('*.blend')):
    try:
        bpy.ops.wm.open_mainfile(filepath=str(file))
        missing = []
        for image in bpy.data.images:
            if image.source == 'FILE':
                path = Path(bpy.path.abspath(image.filepath))
                if not path.is_file():
                    missing.append(str(path))
                else:
                    image.reload()
        report['sources'].append({'file': file.name, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'missing_images': missing,
            'file_images': sum(i.source == 'FILE' for i in bpy.data.images)})
    except Exception:
        report['errors'].append({'file': file.name, 'error': traceback.format_exc()})
(OUT / 'exchange_fresh_verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print('CS549_FRESH_EXCHANGE_DONE', len(report['meshes']), len(report['animations']), len(report['sources']), len(report['errors']))
