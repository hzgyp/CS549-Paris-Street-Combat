"""Extract existing complete upper limbs; preserve selected data, then fresh-import audit."""
import bpy
import hashlib
import json
import os
import traceback
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Exchange/SK_WWII_US_Paratrooper_simple.fbx'
EXPECTED = '6dc23e8d4ec793873da65b63f65d462279caf8a5120cb896978628e51ac6fc84'
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3/exchange_v1'
assert not OUT.exists(), 'Preserve occupied exchange identity'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
OUT.mkdir(parents=True)
report = {'scope': __doc__, 'blender': bpy.app.version_string, 'source_sha256': EXPECTED,
          'threshold': .25, 'selection': 'All face vertices have >= .25 summed upper-arm descendant weights',
          'source_modified': False, 'errors': []}

def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

def bones(rig):
    return {b.name: {'parent': b.parent.name if b.parent else None,
                     'matrix': [v for row in b.matrix_local for v in row]} for b in rig.data.bones}

def vertex_signature(obj, vertex):
    point = obj.matrix_world @ vertex.co
    weights = sorted((obj.vertex_groups[g.group].name, round(g.weight, 6)) for g in vertex.groups if g.weight > 1e-6)
    return (tuple(round(x, 5) for x in point), tuple(weights))

def metrics():
    rows = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        obj.data.calc_loop_triangles()
        rows.append({'name': obj.name, 'vertices': len(obj.data.vertices), 'triangles': len(obj.data.loop_triangles),
                     'uv_layers': len(obj.data.uv_layers), 'materials': [m.name for m in obj.data.materials],
                     'unweighted': sum(not v.groups for v in obj.data.vertices),
                     'bad_weight_sums': sum(abs(sum(g.weight for g in v.groups) - 1) > .001 for v in obj.data.vertices)})
    return rows

try:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(SOURCE), automatic_bone_orientation=False, use_anim=False, use_custom_normals=True)
    rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    assert len(rigs) == 1
    rig = rigs[0]
    original_bones = bones(rig)
    arm_names = set()
    for bone in rig.data.bones:
        item = bone
        while item:
            if item.name in ('upperarm_l', 'upperarm_r'):
                arm_names.add(bone.name)
                break
            item = item.parent
    assert {'hand_l', 'hand_r', 'thumb_03_l', 'thumb_03_r'} <= arm_names
    report['source_bones'] = original_bones
    report['source_meshes'] = metrics()
    report['arm_groups'] = sorted(arm_names)
    originals = [o for o in bpy.data.objects if o.type == 'MESH']
    kept = []
    selection_rows = []
    for obj in originals:
        mesh = obj.data
        coverage = [sum(g.weight for g in v.groups if obj.vertex_groups[g.group].name in arm_names) for v in mesh.vertices]
        faces = [p for p in mesh.polygons if all(coverage[i] >= .25 for i in p.vertices)]
        selection_rows.append({'object': obj.name, 'source_faces': len(mesh.polygons), 'retained_faces': len(faces)})
        if not faces:
            bpy.data.objects.remove(obj, do_unlink=True)
            continue
        old_ids = sorted({i for p in faces for i in p.vertices})
        index = {old: new for new, old in enumerate(old_ids)}
        data = bpy.data.meshes.new(obj.name + '_ContinuousArms')
        data.from_pydata([mesh.vertices[i].co[:] for i in old_ids], [], [[index[i] for i in p.vertices] for p in faces])
        data.update()
        for mat in mesh.materials:
            data.materials.append(mat)
        for layer in mesh.uv_layers:
            dest = data.uv_layers.new(name=layer.name)
            for new_poly, old_poly in zip(data.polygons, faces):
                for new_loop, old_loop in zip(new_poly.loop_indices, old_poly.loop_indices):
                    dest.data[new_loop].uv = layer.data[old_loop].uv
        normals = []
        for new_poly, old_poly in zip(data.polygons, faces):
            new_poly.material_index = old_poly.material_index
            new_poly.use_smooth = old_poly.use_smooth
            normals.extend(mesh.corner_normals[i].vector[:] for i in old_poly.loop_indices)
        data.normals_split_custom_set(normals)
        copy = bpy.data.objects.new(obj.name + '_ContinuousArms', data)
        bpy.context.collection.objects.link(copy)
        copy.matrix_world = obj.matrix_world.copy()
        for group in obj.vertex_groups:
            copy.vertex_groups.new(name=group.name)
        for new_id, old_id in enumerate(old_ids):
            for group in mesh.vertices[old_id].groups:
                copy.vertex_groups[group.group].add([new_id], group.weight, 'REPLACE')
        for modifier in obj.modifiers:
            assert modifier.type == 'ARMATURE'
            arm = copy.modifiers.new(modifier.name, 'ARMATURE')
            arm.object = rig
        expected = Counter(vertex_signature(obj, mesh.vertices[i]) for i in old_ids)
        actual = Counter(vertex_signature(copy, v) for v in data.vertices)
        assert expected == actual, 'Extraction changed selected coordinates or weights'
        # Full arm boundaries may exist only near the shoulder, not at an elbow/cuff.
        edge_counts = Counter(tuple(sorted((p.vertices[i], p.vertices[(i+1) % len(p.vertices)]))) for p in data.polygons for i in range(len(p.vertices)))
        boundary = sorted({i for edge, count in edge_counts.items() if count == 1 for i in edge})
        selection_rows[-1]['boundary_vertices'] = len(boundary)
        selection_rows[-1]['boundary_points_m'] = [(copy.matrix_world @ data.vertices[i].co)[:] for i in boundary]
        selection_rows[-1]['retained_original_vertices'] = old_ids
        kept.append(copy)
        bpy.data.objects.remove(obj, do_unlink=True)
    assert kept, 'No continuous arms extracted'
    report['extraction'] = selection_rows
    report['derivative_meshes'] = metrics()
    assert sum(r['bad_weight_sums'] + r['unweighted'] for r in report['derivative_meshes']) == 0
    expected_geometry = Counter(vertex_signature(o, v) for o in kept for v in o.data.vertices)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in [rig] + kept:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'ContinuousArmsV3.blend'))
    filename = OUT / 'SK_PC_ContinuousArmsV3.fbx'
    bpy.ops.export_scene.fbx(filepath=str(filename), use_selection=True, object_types={'ARMATURE', 'MESH'},
                             add_leaf_bones=False, bake_anim=False, mesh_smooth_type='OFF',
                             path_mode='RELATIVE', use_mesh_modifiers=False)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(filename), automatic_bone_orientation=False, use_anim=False, use_custom_normals=True)
    imported_rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    actual_bones = bones(imported_rig)
    assert set(original_bones) == set(actual_bones)
    assert all(original_bones[n]['parent'] == actual_bones[n]['parent'] for n in original_bones)
    max_bone_delta = max(abs(a-b) for n in original_bones for a,b in zip(original_bones[n]['matrix'], actual_bones[n]['matrix']))
    report['fresh_import'] = metrics()
    report['fresh_bone_matrix_max_delta'] = max_bone_delta
    actual_geometry = Counter(vertex_signature(o, v) for o in bpy.data.objects if o.type == 'MESH' for v in o.data.vertices)
    report['fresh_vertex_weight_signature_match'] = expected_geometry == actual_geometry
    assert max_bone_delta < 1e-5
    assert expected_geometry == actual_geometry, 'Round trip changed retained positions or weights'
    assert all(r['unweighted'] == 0 and r['bad_weight_sums'] == 0 for r in report['fresh_import'])
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
    report['source_hash_unchanged'] = True
    report['fbx_sha256'] = hashlib.sha256(filename.read_bytes()).hexdigest()
    report['status'] = 'exchange_checked_not_native_or_visual_acceptance'
except Exception:
    report['errors'].append(traceback.format_exc())
    report['status'] = 'failed'
    write()
    raise
write()
print('CS549_CONTINUOUS_ARMS_EXCHANGE_DONE', report['status'])
