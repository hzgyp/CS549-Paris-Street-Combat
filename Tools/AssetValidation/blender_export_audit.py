"""Fresh-import UE-exported FBX files and measure geometry, UVs and skin weights."""
import bpy
import json
import math
import os
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalWorking/Validation/UE582/2026-09-30-v1/Evidence'
EXPORTS = OUT / 'Exports' / os.environ.get('CS549_FBX_SUBDIR', '')
REPORT_FILE = OUT / ('blender_export_audit_resaved.json' if os.environ.get('CS549_FBX_SUBDIR') else 'blender_export_audit.json')
if os.environ.get('CS549_FBX_AUDIT_DIR'):
    EXPORTS = Path(os.environ['CS549_FBX_AUDIT_DIR']).resolve()
    OUT = EXPORTS
    REPORT_FILE = OUT / 'blender_export_audit.json'
report = {'blender': bpy.app.version_string, 'scope': 'Fresh FBX import metrics; no model repair or gameplay validation.',
          'models': [], 'animations': [], 'errors': []}
for file in sorted(EXPORTS.glob('*.fbx')):
    if file.stem.startswith(('Rifle_', 'W2_')):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        try:
            bpy.ops.import_scene.fbx(filepath=str(file), automatic_bone_orientation=False, use_anim=True)
            report['animations'].append({'file': file.name,
                'fps': bpy.context.scene.render.fps / bpy.context.scene.render.fps_base,
                'armatures': sum(obj.type == 'ARMATURE' for obj in bpy.data.objects),
                'actions': [{'name': action.name, 'frame_range': list(action.frame_range)}
                            for action in bpy.data.actions]})
        except Exception as exc:
            report['errors'].append({'file': file.name, 'error': str(exc)})
        REPORT_FILE.write_text(json.dumps(report, indent=2), encoding='utf-8')
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    try:
        bpy.ops.import_scene.fbx(filepath=str(file), automatic_bone_orientation=False,
                                 use_anim=False, use_custom_normals=True)
        armatures = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE']
        meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        bone_names = {bone.name for rig in armatures for bone in rig.data.bones}
        model = {'file': file.name, 'armatures': len(armatures), 'meshes': [],
                 'bone_count': len(bone_names), 'bones': sorted(bone_names)}
        for obj in meshes:
            mesh = obj.data
            mesh.calc_loop_triangles()
            influence_counts = Counter()
            unweighted = 0
            bad_weight_sums = 0
            min_sum, max_sum = math.inf, -math.inf
            for vertex in mesh.vertices:
                weights = [group.weight for group in vertex.groups
                           if obj.vertex_groups[group.group].name in bone_names and group.weight > 0.00001]
                influence_counts[len(weights)] += 1
                weight_sum = sum(weights)
                min_sum = min(min_sum, weight_sum)
                max_sum = max(max_sum, weight_sum)
                if not weights:
                    unweighted += 1
                elif abs(weight_sum - 1) > .001:
                    bad_weight_sums += 1
            points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
            minimum = [min(getattr(v, axis) for v in points) for axis in ('x', 'y', 'z')]
            maximum = [max(getattr(v, axis) for v in points) for axis in ('x', 'y', 'z')]
            degenerate = sum((mesh.vertices[tri.vertices[1]].co - mesh.vertices[tri.vertices[0]].co).cross(
                            mesh.vertices[tri.vertices[2]].co - mesh.vertices[tri.vertices[0]].co).length_squared < 1e-16
                            for tri in mesh.loop_triangles)
            model['meshes'].append({'name': obj.name, 'vertices': len(mesh.vertices),
                'triangles': len(mesh.loop_triangles), 'uv_layers': len(mesh.uv_layers),
                'material_slots': len(obj.material_slots), 'degenerate_triangles': degenerate,
                'bounds_min_m': minimum, 'bounds_max_m': maximum,
                'dimensions_m': [b - a for a, b in zip(minimum, maximum)],
                'influence_counts': dict(influence_counts), 'unweighted_vertices': unweighted,
                'weight_sum_outside_0_001': bad_weight_sums, 'weight_sum_min': min_sum,
                'weight_sum_max': max_sum, 'armature_modifiers': sum(m.type == 'ARMATURE' for m in obj.modifiers)})
        report['models'].append(model)
        # Preserve a useful editable diagnostic copy of complete representative bodies.
        if os.environ.get('CS549_KEEP_DIAGNOSTIC_BLEND') == '1' and file.stem in ('SK_WWII_GermanSoldier_varA', 'SK_WWII_GermanSoldier_varB',
                         'SK_WWII_US_Paratrooper_simple', 'SK_WWII_US_Paratrooper_simpleB'):
            bpy.ops.wm.save_as_mainfile(filepath=str(EXPORTS / (file.stem + '_diagnostic.blend')))
    except Exception as exc:
        report['errors'].append({'file': file.name, 'error': str(exc)})
    REPORT_FILE.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('CS549_BLENDER_AUDIT_DONE', len(report['models']), 'errors', len(report['errors']))
