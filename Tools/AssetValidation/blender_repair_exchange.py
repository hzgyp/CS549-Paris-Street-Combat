"""Bounded exchange repair; keeps native Unreal assets authoritative."""
import bpy
import json
import math
import os
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = Path(os.environ.get('CS549_ASSET_LAB', ROOT / 'Assets/LocalWorking/Validation/UE582/2026-09-30-v1'))
OUT = LAB / 'Evidence/Repair20261001'
DEST = OUT / 'Exchange'
DEST.mkdir(parents=True, exist_ok=True)
INV = json.loads((LAB / 'Evidence/ue_load_inventory.json').read_text(encoding='utf-8'))
PROBE = json.loads((OUT / 'ue_repair_probe.json').read_text(encoding='utf-8'))
TEXTURES = {t['path']: t for t in json.loads((OUT / 'texture_exports.json').read_text(encoding='utf-8'))['textures']}
MATERIALS = {m['path']: m for m in PROBE['materials']}
MESHES = {a['path'].split('/')[-1]: a for a in INV['assets'] if a.get('class') == 'SkeletalMesh'}
LENGTHS = {a['path'].split('/')[-1]: a['sequence_length'] for a in INV['assets'] if a.get('class') == 'AnimSequence' and '/InPlace/' in a['path']}
report = {'blender': bpy.app.version_string, 'meshes': [], 'animations': [], 'errors': [],
    'material_limit': 'Portable PBR editing preview; not a lossless replacement for native UE material graphs or events.'}


def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                yield from bag.fcurves


def snapshot():
    rigs = [o for o in bpy.data.objects if o.type == 'ARMATURE']
    bones = {b.name for rig in rigs for b in rig.data.bones}
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    return {'hierarchy': {b.name: b.parent.name if b.parent else None for r in rigs for b in r.data.bones},
        'triangles': sum(len(o.data.loop_triangles) for o in meshes),
        'vertices': sum(len(o.data.vertices) for o in meshes),
        'unweighted': sum(not any(o.vertex_groups[g.group].name in bones and g.weight > 1e-5 for g in v.groups) for o in meshes for v in o.data.vertices) if rigs else None,
        'bad_weight_sums': sum(abs(sum(g.weight for g in v.groups if o.vertex_groups[g.group].name in bones) - 1) > .001 for o in meshes for v in o.data.vertices) if rigs else None,
        'dimensions': [[*o.dimensions] for o in meshes],
        'uv_layers': [len(o.data.uv_layers) for o in meshes],
        'material_slots': [len(o.material_slots) for o in meshes]}


def texture_node(mat, path, color=False):
    item = TEXTURES.get(path.split('.')[0]) if path else None
    if not item:
        return None
    node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    node.image = bpy.data.images.load(str(OUT / item['file']), check_existing=True)
    node.image.colorspace_settings.name = 'sRGB' if color and item['srgb'] else 'Non-Color'
    node.label = path.split('/')[-1].split('.')[0]
    return node


def portable_material(row):
    mat = bpy.data.materials.new(row['path'].split('/')[-1] + '_portable')
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    links, nodes = mat.node_tree.links, mat.node_tree.nodes
    params = row.get('parameters', {})
    lower = {k.lower(): v for k, v in params.items()}
    base = next((lower[k] for k in ('albedo', 'colour', 'color', 'basecolor') if k in lower), None)
    normal = next((lower[k] for k in ('normal', 'normals', 'normalmap') if k in lower), None)
    orm = next((lower[k] for k in ('ao_rough_metal', 'rmo_mask') if k in lower), None)
    if not base:
        base = next((g.get('texture') for g in row.get('graph', []) if str(g.get('texture', '')).split('.')[0].endswith('_D')), None)
    if 'eyematerial' in row['path'].lower() or row['path'].endswith('/M_Eye'):
        base = params.get('ScleraColor')
        sclera = texture_node(mat, base, True)
        iris = texture_node(mat, params.get('IrisColor'), True)
        if sclera and iris:
            uv = nodes.new('ShaderNodeTexCoord')
            center = nodes.new('ShaderNodeVectorMath'); center.operation = 'SUBTRACT'; center.inputs[1].default_value = (.5, .5, 0)
            links.new(uv.outputs['UV'], center.inputs[0])
            scale = nodes.new('ShaderNodeVectorMath'); scale.operation = 'SCALE'; scale.inputs[3].default_value = 1 / (.159 * 2)
            links.new(center.outputs['Vector'], scale.inputs[0])
            add = nodes.new('ShaderNodeVectorMath'); add.operation = 'ADD'; add.inputs[1].default_value = (.5, .5, 0)
            links.new(scale.outputs['Vector'], add.inputs[0]); links.new(add.outputs['Vector'], iris.inputs['Vector']); iris.extension = 'EXTEND'
            distance = nodes.new('ShaderNodeVectorMath'); distance.operation = 'LENGTH'; links.new(center.outputs['Vector'], distance.inputs[0])
            mask = nodes.new('ShaderNodeMapRange'); mask.clamp = True
            mask.inputs['From Min'].default_value = .145; mask.inputs['From Max'].default_value = .165
            mask.inputs['To Min'].default_value = 1; mask.inputs['To Max'].default_value = 0
            links.new(distance.outputs['Value'], mask.inputs['Value'])
            mix = nodes.new('ShaderNodeMixRGB'); links.new(mask.outputs[0], mix.inputs[0]); links.new(sclera.outputs['Color'], mix.inputs[1]); links.new(iris.outputs['Color'], mix.inputs[2])
            links.new(mix.outputs[0], bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = .15
        normal = None
    else:
        color = texture_node(mat, base, True)
        if color:
            links.new(color.outputs['Color'], bsdf.inputs['Base Color'])
    packed = texture_node(mat, orm)
    if packed:
        split = nodes.new('ShaderNodeSeparateColor'); links.new(packed.outputs['Color'], split.inputs[0])
        links.new(split.outputs['Green'], bsdf.inputs['Roughness']); links.new(split.outputs['Blue'], bsdf.inputs['Metallic'])
    norm = texture_node(mat, normal)
    if norm:
        sep = nodes.new('ShaderNodeSeparateColor'); links.new(norm.outputs['Color'], sep.inputs[0])
        invert = nodes.new('ShaderNodeMath'); invert.operation = 'SUBTRACT'; invert.inputs[0].default_value = 1
        links.new(sep.outputs['Green'], invert.inputs[1])
        comb = nodes.new('ShaderNodeCombineColor')
        links.new(sep.outputs['Red'], comb.inputs['Red']); links.new(invert.outputs[0], comb.inputs['Green']); links.new(sep.outputs['Blue'], comb.inputs['Blue'])
        nmap = nodes.new('ShaderNodeNormalMap'); links.new(comb.outputs[0], nmap.inputs['Color']); links.new(nmap.outputs[0], bsdf.inputs['Normal'])
    mat['native_material'] = row['path']
    mat['limitations'] = report['material_limit']
    return mat


def save_report():
    (OUT / 'exchange_repair.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


for file in sorted((LAB / 'Evidence/Exports/UE582Resaved').glob('*.fbx')):
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.import_scene.fbx(filepath=str(file), automatic_bone_orientation=False, use_anim=file.stem.startswith('Rifle_'))
        bpy.context.scene.render.fps = 30
        bpy.context.scene.render.fps_base = 1
        if file.stem.startswith('Rifle_'):
            action = list(bpy.data.actions)[0]
            first, last = action.frame_range
            length = LENGTHS[file.stem]
            frame_count = round(length * 30)
            for curve in curves(action):
                values = [curve.evaluate(first + n * (last - first) / frame_count) for n in range(frame_count + 1)]
                curve.keyframe_points.clear()
                curve.keyframe_points.add(frame_count + 1)
                for n, value in enumerate(values):
                    key = curve.keyframe_points[n]
                    key.co = (1 + n, value)
                    key.interpolation = 'LINEAR'
                curve.update()
            bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, 1 + frame_count
            bpy.ops.wm.save_as_mainfile(filepath=str(DEST / (file.stem + '.blend')))
            bpy.ops.export_scene.fbx(filepath=str(DEST / file.name), object_types={'ARMATURE'}, add_leaf_bones=False,
                bake_anim=True, bake_anim_use_nla_strips=False, bake_anim_use_all_actions=True,
                bake_anim_simplify_factor=0, path_mode='RELATIVE')
            report['animations'].append({'file': file.name, 'source_seconds': length, 'frames': frame_count,
                'repaired_seconds': frame_count / 30, 'error_seconds': abs(frame_count / 30 - length)})
        else:
            meshes = [o for o in bpy.data.objects if o.type == 'MESH']
            for obj in meshes:
                obj.data.calc_loop_triangles()
            before = snapshot()
            deform = set(before['hierarchy'])
            changed = 0
            for obj in meshes:
                for vertex in obj.data.vertices:
                    groups = [g for g in vertex.groups if obj.vertex_groups[g.group].name in deform]
                    total = sum(g.weight for g in groups)
                    if total > 0 and abs(total - 1) > 1e-7:
                        changed += 1
                        for group in groups:
                            obj.vertex_groups[group.group].add([vertex.index], group.weight / total, 'REPLACE')
            native = MESHES[file.stem]
            material_map = {}
            for slot in native['materials']:
                path = slot['material'].split('.')[0]
                material_map[path.split('/')[-1]] = MATERIALS[path]
            for obj in meshes:
                for slot in obj.material_slots:
                    key = slot.material.name.rsplit('.', 1)[0] if slot.material.name[-4:-3] == '.' else slot.material.name
                    row = material_map.get(key) or next((v for k, v in material_map.items() if key.startswith(k + '_')), None)
                    if row:
                        slot.material = portable_material(row)
                    else:
                        report.setdefault('unmatched_materials', []).append({'file': file.name, 'material': key})
            # Remove unused importer images with vendor-drive references.
            for material in list(bpy.data.materials):
                if material.users == 0:
                    bpy.data.materials.remove(material)
            for image in list(bpy.data.images):
                if image.users == 0:
                    bpy.data.images.remove(image)
            after = snapshot()
            bpy.ops.export_scene.fbx(filepath=str(DEST / file.name), object_types={'ARMATURE', 'MESH'}, add_leaf_bones=False,
                bake_anim=False, mesh_smooth_type='OFF', path_mode='RELATIVE', use_mesh_modifiers=False)
            for image in bpy.data.images:
                if image.source == 'FILE':
                    image.filepath = bpy.path.relpath(image.filepath, start=str(DEST))
            if file.stem in ('SK_WWII_GermanSoldier_varA', 'SK_WWII_GermanSoldier_varB',
                    'SK_WWII_US_Paratrooper_simple', 'SK_WWII_US_Paratrooper_simpleB', 'SK_M1_Garand'):
                bpy.ops.wm.save_as_mainfile(filepath=str(DEST / (file.stem + '.blend')))
            report['meshes'].append({'file': file.name, 'normalized_vertices': changed, 'before': before, 'after': after})
        save_report()
    except Exception:
        report['errors'].append({'file': file.name, 'error': traceback.format_exc()})
        save_report()
print('CS549_EXCHANGE_REPAIR_DONE', len(report['meshes']), len(report['animations']), len(report['errors']))
