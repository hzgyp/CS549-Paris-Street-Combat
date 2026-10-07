"""Read-only matched studio views: current M1 portable reference vs a verified GLB."""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001'
M1 = LAB / 'Exchange/SK_M1_Garand.blend'
V11 = ROOT / 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-weather-v11/finish_v1/GermanRifle_SPR_Weathered_V11.glb'
VIEWS = [('whole', (0, 0, 0), (1, -2, 1.1), 1.30),
         ('receiver', (-.1, 0, .035), (-.15, -1, .65), .47),
         ('stock', (-.38, 0, -.035), (.12, -1, .3), .43)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setup():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 40
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 700
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.world = bpy.data.worlds.new('Matched_Studio')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.12, .12, .12, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .7
    for i, (loc, energy, size) in enumerate([((.1, -1, 1.5), 170, 1.4), ((.2, 1, 1), 110, 1.2), ((.4, -.5, -1), 45, 1)]):
        light = bpy.data.objects.new('MatchedLight' + str(i), bpy.data.lights.new('MatchedLight' + str(i), 'AREA'))
        scene.collection.objects.link(light)
        light.location = loc
        light.rotation_euler = (-light.location).to_track_quat('-Z', 'Y').to_euler()
        light.data.energy = energy
        light.data.shape = 'DISK'
        light.data.size = size
    cameras = {}
    for name, center, direction, scale in VIEWS:
        cam = bpy.data.objects.new('Matched_' + name, bpy.data.cameras.new('Matched_' + name))
        scene.collection.objects.link(cam)
        cam.data.type = 'ORTHO'
        cam.data.ortho_scale = scale
        cam.data.clip_start = .001
        cam.location = Vector(center) + Vector(direction).normalized() * 3
        cam.rotation_euler = (Vector(center) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cameras[name] = cam
    return scene, cameras


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--german', default=str(V11))
    p.add_argument('--variant', default='german_v11')
    p.add_argument('--expected-sha', default='f979fb6a5ad4a725553d73804c3f3efd7a793e55c16129164223bd69ccb55a8d')
    a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = Path(a.out).resolve()
    assert not out.exists(), 'Use a new comparison identity'
    out.mkdir(parents=True)
    german = Path(a.german).resolve()
    assert a.variant.startswith('german_') and a.variant.replace('_','').isalnum()
    inputs = [M1, german] + [LAB / ('Textures/USParatrooper/Textures/M1_Garand/T_M1_Garand_' + s + '.png') for s in ['D', 'N', 'ORM']]
    guard = {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    assert guard[str(german.relative_to(ROOT))] == a.expected_sha
    results = []
    for variant in ['allied_m1', a.variant]:
        if variant == 'allied_m1':
            bpy.ops.wm.open_mainfile(filepath=str(M1), load_ui=False, use_scripts=False)
        else:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.gltf(filepath=str(german))
        meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        if variant == 'allied_m1':
            for obj in meshes:
                transform = Matrix.Rotation(math.pi / 2, 4, 'Z') @ obj.matrix_world
                obj.parent = None
                obj.matrix_world = transform
        # Display alignment only, never saved to any asset input path.
        matrices = {o.name: o.matrix_world.copy() for o in meshes}
        for obj in meshes:
            obj.parent = None
            obj.matrix_world = matrices[obj.name]
        for obj in list(bpy.context.scene.objects):
            if obj not in meshes:
                bpy.data.objects.remove(obj, do_unlink=True)
        points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
        low = Vector([min(p[k] for p in points) for k in range(3)])
        high = Vector([max(p[k] for p in points) for k in range(3)])
        dims = high - low
        assert 1.05 < dims.x < 1.2 and dims.z < .25, (variant, list(dims))
        center = (low + high) / 2
        for obj in meshes:
            obj.location -= center
        materials = set(m for obj in meshes for m in obj.data.materials if m)
        assert all(m.use_nodes for m in materials)
        for im in bpy.data.images:
            if im.source not in {'VIEWER', 'RENDER_RESULT'}:
                assert im.size[0] > 0, ('Missing pixels', im.name)
        scene, cams = setup()
        files = []
        for name, camera in cams.items():
            scene.camera = camera
            png = out / (variant + '_' + name + '.png')
            scene.render.filepath = str(png)
            bpy.ops.render.render(write_still=True)
            files.append({'view': name, 'path': png.relative_to(ROOT).as_posix(), 'sha256': sha(png)})
        bpy.ops.file.pack_all()
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(out / (variant + '_inspection.blend')))
        rows = []
        for im in bpy.data.images:
            if im.source in {'VIEWER', 'RENDER_RESULT'}:
                continue
            rows.append({'name': im.name, 'size': list(im.size), 'color_space': im.colorspace_settings.name, 'packed': bool(im.packed_file)})
        results.append({'variant': variant, 'meshes': len(meshes), 'dimensions_m': list(dims),
                        'materials': sorted(m.name for m in materials), 'images': rows, 'renders': files})
    assert all(sha(ROOT / path) == digest for path, digest in guard.items()), 'Input changed'
    report = {'scope': 'read-only texture comparison', 'blender': bpy.app.version_string,
              'input_sha256': guard, 'inputs_unchanged': True, 'views': VIEWS,
              'samples': 40, 'color_management': 'AgX Medium High Contrast, exposure0 gamma1',
              'native_ue_shader_parity': False, 'new_asset_exported': False, 'variants': results}
    (out / 'comparison.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'inputs_unchanged': True, 'rendered_views': 6}), flush=True)


if __name__ == '__main__':
    main()
