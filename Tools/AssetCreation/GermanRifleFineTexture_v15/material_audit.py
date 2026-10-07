"""Fresh V15 material/detail gates; protected V14 stays read-only."""
import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


M = module('v15_material_audit_authoring', Path(__file__).with_name('main.py'))


def embedded(path):
    raw = path.read_bytes()
    assert raw[:4] == b'glTF' and struct.unpack_from('<I', raw, 4)[0] == 2
    assert struct.unpack_from('<I', raw, 8)[0] == len(raw), 'GLB length'
    size, kind = struct.unpack_from('<II', raw, 12)
    assert kind == 0x4E4F534A, 'First GLB chunk must be JSON'
    document = json.loads(raw[20:20 + size])
    binary_size, binary_kind = struct.unpack_from('<II', raw, 20 + size)
    assert binary_kind == 0x004E4942, 'Embedded binary chunk required'
    binary = raw[28 + size:28 + size + binary_size]
    images, dimensions = {}, {}
    for image in document['images']:
        assert 'uri' not in image and image['mimeType'] == 'image/png'
        view = document['bufferViews'][image['bufferView']]
        offset = view.get('byteOffset', 0)
        assert view.get('buffer', 0) == 0
        payload = binary[offset:offset + view['byteLength']]
        assert len(payload) == view['byteLength']
        assert payload[:8] == b'\x89PNG\r\n\x1a\n' and payload[12:16] == b'IHDR'
        assert image['name'] not in images, ('Duplicate image name', image['name'])
        images[image['name']] = hashlib.sha256(payload).hexdigest()
        dimensions[image['name']] = list(struct.unpack_from('>II', payload, 16))
    return images, document, dimensions


def bindings():
    rows = {}
    deps = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            counts = {}
            for triangle in mesh.loop_triangles:
                name = mesh.materials[triangle.material_index].name
                points = np.array([tuple(obj.matrix_world @ mesh.vertices[i].co)
                                   for i in triangle.vertices])
                row = counts.setdefault(name, {'triangles': 0, 'area_m2': 0})
                row['triangles'] += 1
                row['area_m2'] += float(np.linalg.norm(np.cross(
                    points[1] - points[0], points[2] - points[0])) * .5)
            rows[obj.name] = counts
        finally:
            evaluated.to_mesh_clear()
    return rows


def image_name(document, texture_info):
    texture = document['textures'][texture_info['index']]
    return document['images'][texture['source']]['name']


def wood_images(document, material):
    pbr = material['pbrMetallicRoughness']
    return {image_name(document, pbr['baseColorTexture']),
            image_name(document, pbr['metallicRoughnessTexture']),
            image_name(document, material['normalTexture'])}


def signature(document, material):
    """Resolve exporter texture indices before semantic material comparison."""
    def walk(value):
        if isinstance(value, list):
            return [walk(item) for item in value]
        if isinstance(value, dict):
            answer = {key: walk(item) for key, item in value.items()}
            if 'index' in value:
                answer['index'] = image_name(document, value)
            return answer
        return value
    return walk(material)


def render_close_views(out):
    H = M.H
    H.OUT = out
    H.SCENE = scene = bpy.context.scene
    H.PIVOT = M.V.M.P.PIVOT
    scene.world = bpy.data.worlds.new('V15_Fresh_Studio')
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes['Background']
    background.inputs[0].default_value = (.12, .12, .12, 1)
    background.inputs[1].default_value = .7
    lights = [((.1, -1, 1.5), 170, 1.4),
              ((.2, 1, 1), 110, 1.2),
              ((.4, -.5, -1), 45, 1)]
    for index, (location, energy, size) in enumerate(lights):
        light = bpy.data.objects.new('V15_FreshLight' + str(index),
                                    bpy.data.lights.new('V15_FreshLight' + str(index), 'AREA'))
        scene.collection.objects.link(light)
        light.location = Vector(location) - H.PIVOT
        light.rotation_euler = (Vector((.17, 0, -.03)) - H.PIVOT - light.location).to_track_quat('-Z', 'Y').to_euler()
        light.data.energy = energy
        light.data.shape = 'DISK'
        light.data.size = size
    scene.view_settings.view_transform = 'AgX'
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 729
    scene.render.resolution_percentage = 100
    views = [('stock', (-.283, 0, -.085), (.08, -1, .22), .28),
             ('handguard', (.43, 0, .007), (.1, -1, .7), .36)]
    for args in views:
        M.V.render_close(*args, prefix='fresh')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    candidate = Path(args.candidate).resolve()
    out = Path(args.out).resolve()
    assert not out.exists(), 'Use a new output identity'
    out.mkdir(parents=True)
    report = {'passed': False}
    try:
        source = candidate / (M.NAME + '.blend')
        glb = candidate / (M.NAME + '.glb')
        baseline_glb = M.BASE / (M.SOURCE_NAME + '.glb')
        files = [source, glb, M.BASE / (M.SOURCE_NAME + '.blend'), baseline_glb]
        guard = {str(path): M.W.sha(path) for path in files}
        bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
        authored = bindings()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(glb))
        fresh = bindings()
        assert authored.keys() == fresh.keys(), 'Fresh mesh identities'
        assert len(authored) == 24, ('Mesh count', len(authored))
        for name, row in authored.items():
            assert row.keys() == fresh[name].keys(), (name, 'Material names')
            for material, count in row.items():
                actual = fresh[name][material]
                assert count['triangles'] == actual['triangles'], (name, material, 'Triangles')
                assert abs(count['area_m2'] - actual['area_m2']) < 1e-7, (name, material, 'Area')
        old_images, old_doc, _ = embedded(baseline_glb)
        current, document, sizes = embedded(glb)
        old_materials = {material['name']: material for material in old_doc['materials']}
        new_materials = {material['name']: material for material in document['materials']}
        # V14 side normals retain V13 names: determine actual old image ownership
        # from material references rather than assuming a V14 filename prefix.
        allowed = set().union(*(wood_images(old_doc, old_materials[name]) for name in M.WOOD))
        assert len(allowed) == 6, ('Replaced wood PNG count', allowed)
        protected = sorted(set(old_images) - allowed)
        assert len(protected) == 30, ('Protected PNG count', len(protected))
        for name in protected:
            assert current.get(name) == old_images[name], (name, 'Protected PNG changed')
        expected = {name + '_' + channel for name in M.WOOD.values()
                    for channel in ['BaseColor', 'Normal', 'ORM']}
        assert set(current) == set(protected) | expected, ('Unexpected image set', set(current) ^ (set(protected) | expected))
        assert len(current) == 36
        assert 'KHR_materials_specular' in document.get('extensionsUsed', []), 'Response extension missing'
        responses = {}
        for old_name, name in M.WOOD.items():
            material = new_materials[name]
            assert wood_images(document, material) == {name + '_' + channel for channel in ['BaseColor', 'Normal', 'ORM']}
            factor = material['extensions']['KHR_materials_specular']['specularFactor']
            assert abs(factor - .36) < 1e-6, (name, 'Specular factor', factor)
            normal_strength = material['normalTexture'].get('scale', 1)
            assert abs(normal_strength - .45) < 1e-6, (name, 'GLB normal strength', normal_strength)
            bs = bpy.data.materials[name].node_tree.nodes.get('Principled BSDF')
            assert bs is not None, (name, 'Fresh Principled shader')
            specular = bs.inputs['Specular IOR Level'].default_value
            assert abs(specular - .18) < 1e-6, (name, 'Fresh specular', specular)
            assert bs.inputs['Coat Weight'].default_value == 0, (name, 'Unexpected coat')
            normal = M.W.texture_for_input(bs, 'Normal')
            strength = normal.inputs['Strength'].default_value
            assert abs(strength - .45) < 1e-6, (name, 'Fresh normal strength', strength)
            expected_size = list(M.SIZES[old_name])
            for channel in ['BaseColor', 'Normal', 'ORM']:
                image = name + '_' + channel
                assert sizes[image] == expected_size, (image, 'PNG size', sizes[image], expected_size)
                assert list(bpy.data.images[image].size) == expected_size, (image, 'Fresh image size')
            responses[name] = {'specular_factor': factor,
                               'fresh_specular_ior_level': specular,
                               'normal_strength': strength,
                               'image_dimensions': expected_size}
        outside = sorted(set(old_materials) - set(M.WOOD))
        assert len(outside) == 12, ('Outside-scope material count', len(outside))
        assert set(new_materials) == set(outside) | set(M.WOOD.values()), 'Unexpected material set'
        for name in outside:
            assert signature(old_doc, old_materials[name]) == signature(document, new_materials[name]), (name, 'Outside-scope definition changed')
        if args.render:
            render_close_views(out)
        assert all(M.W.sha(Path(path)) == digest for path, digest in guard.items()), 'Read-only input guard'
        report.update({'passed': True, 'authored_bindings': authored, 'fresh_bindings': fresh,
                       'replaced_wood_png_payloads': sorted(allowed),
                       'protected_png_payloads': protected,
                       'all_protected_embedded_bytes_exact': True,
                       'outside_scope_material_definitions_exact': outside,
                       'wood_responses': responses, 'embedded_image_dimensions': sizes,
                       'extensions_used': document.get('extensionsUsed', []),
                       'material_count': len(document['materials']),
                       'primitive_count': sum(len(mesh['primitives']) for mesh in document['meshes']),
                       'embedded_images': len(current), 'input_files': guard,
                       'visual_acceptance': False, 'runtime_acceptance': False})
    except Exception as error:
        report['error'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'material_audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({key: report[key] for key in
                     ['passed', 'material_count', 'primitive_count', 'embedded_images']}), flush=True)


if __name__ == '__main__':
    main()
