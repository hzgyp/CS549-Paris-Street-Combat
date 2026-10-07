"""Texture-only V11 weathering of the untouched, user-approved V10 rifle."""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10/finish_v3'
NAME = 'GermanRifle_SPR_Weathered_V11'
SPEC = importlib.util.spec_from_file_location('v10helpers', Path(__file__).parents[1] / 'GermanRifleSPR_v10/main.py')
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_fingerprint():
    """Protect raw topology, attributes, modifiers, parent and exact transforms."""
    rows = {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        me = obj.data
        h = hashlib.sha256()
        for values in ([tuple(v.co) for v in me.vertices],
                       [tuple(p.vertices) for p in me.polygons],
                       [tuple(n.vector) for n in me.corner_normals],
                       [tuple(u.uv) for u in me.uv_layers.active.data],
                       [tuple(row) for row in obj.matrix_world]):
            h.update(repr(values).encode())
        h.update(repr([(m.name, m.type, [(p.identifier, str(getattr(m, p.identifier)))
                      for p in m.bl_rna.properties if p.type in {'BOOLEAN', 'INT', 'FLOAT', 'ENUM'}])
                      for m in obj.modifiers]).encode())
        h.update((obj.parent.name if obj.parent else '').encode())
        rows[obj.name] = h.hexdigest()
    return rows


def pixels(im):
    w, h = im.size
    data = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(data)
    return data.reshape(h, w, 4)


def field(u, v, rng, count=14):
    """Low-frequency variation, not full-surface pixel noise."""
    result = np.zeros_like(u)
    for _ in range(count):
        result += np.sin(u * rng.uniform(7, 36) + v * rng.uniform(8, 47) + rng.uniform(0, 7))
    return result / count


def scratches(u, v, rng, count, wood=False):
    result = np.zeros_like(u)
    for _ in range(count):
        cx, cy = rng.uniform(.02, .95), rng.uniform(.025, .975)
        length = rng.uniform(.007, .037) if wood else rng.uniform(.003, .014)
        width = rng.uniform(.0007, .0015) if wood else rng.uniform(.00045, .001)
        slope = rng.uniform(-.09, .09) if wood else rng.uniform(-.6, .6)
        transverse = v - cy - slope * (u - cx)
        stroke = np.exp(-((u - cx) / length) ** 6 - (transverse / width) ** 2)
        result = np.maximum(result, stroke * rng.uniform(.3, 1))
    return result


def texture_for_input(bs, socket):
    return bs.inputs[socket].links[0].from_node


def replace_wood(mat):
    bs = mat.node_tree.nodes.get('Principled BSDF')
    base_node = texture_for_input(bs, 'Base Color')
    old = pixels(base_node.image)
    h, w = old.shape[:2]
    u, v = np.meshgrid(np.arange(w) / w, np.arange(h) / h)
    rng = np.random.default_rng(1104)
    variation = field(u, v, rng)
    scratch = scratches(u, v, rng, 75, wood=True)
    # Named stock UV: butt, wrist and foregrip. Not a substance classifier.
    rubbing = np.zeros_like(u)
    for cx, cy, sx, sy, strength in [(.1, .2, .085, .14, .8), (.25, .23, .07, .1, 1),
                                    (.29, .7, .065, .12, .7), (.65, .2, .11, .13, .65)]:
        rubbing += strength * np.exp(-((u-cx)/sx)**2 - ((v-cy)/sy)**2)
    rubbing *= np.clip(.6 + variation * 2, .1, 1)
    dark_pores = np.clip((rng.random(u.shape) - .982) * 40, 0, 1)
    color = old.copy()
    color[:, :, :3] *= (1 + variation * .5 - rubbing * .07 - dark_pores * .08)[:, :, None]
    color[:, :, :3] += scratch[:, :, None] * np.array((.055, .026, .010))
    base_node.image = HELPER.image_data('V11_Walnut_Worn_BaseColor', np.clip(color, 0, 1))
    sep = texture_for_input(bs, 'Roughness')
    orm_node = sep.inputs['Color'].links[0].from_node
    orm = pixels(orm_node.image)
    orm[:, :, 1] = np.clip(orm[:, :, 1] + .025 + variation * .14 - rubbing * .04 + scratch * .045, .55, .77)
    orm_node.image = HELPER.image_data('V11_Walnut_Worn_ORM', orm, 'Non-Color')
    nm = texture_for_input(bs, 'Normal')
    normal_node = nm.inputs['Color'].links[0].from_node
    normal = pixels(normal_node.image)
    du, dv = np.gradient(scratch)
    normal[:, :, 0] = np.clip(normal[:, :, 0] - dv * .014, .45, .55)
    normal[:, :, 1] = np.clip(normal[:, :, 1] - du * .014, .45, .55)
    normal_node.image = HELPER.image_data('V11_Walnut_Worn_Normal', normal, 'Non-Color')
    return {'material': mat.name, 'scratch_mean': float(scratch.mean()),
            'roughness_range': [float(orm[:, :, 1].min()), float(orm[:, :, 1].max())]}


def replace_steel(mat, seed):
    bs = mat.node_tree.nodes.get('Principled BSDF')
    base_node = texture_for_input(bs, 'Base Color')
    old = pixels(base_node.image)
    if old.shape[0] < 512:
        # Constant old furniture image needs sufficient texels for fine wear.
        old = np.broadcast_to(old[0, 0], (1024, 1024, 4)).copy()
    h, w = old.shape[:2]
    u, v = np.meshgrid(np.arange(w) / w, np.arange(h) / h)
    rng = np.random.default_rng(seed)
    variation = field(u, v, rng)
    scratch = scratches(u, v, rng, 115)
    fine = rng.normal(0, .0015, u.shape)
    color = old.copy()
    color[:, :, :3] *= (1 + variation * .12 + fine)[:, :, None]
    # Bluing rubs, not bright silver stripes or orange corrosion.
    color[:, :, :3] += scratch[:, :, None] * np.array((.060, .055, .048))
    stem = mat.name.replace('V10_', 'V11_')
    base_node.image = HELPER.image_data(stem + '_Worn_BaseColor', np.clip(color, 0, 1))
    orm = np.ones_like(old)
    orm[:, :, 1] = np.clip(.49 + variation * .15 + fine * 3 - scratch * .045, .39, .62)
    im = HELPER.image_data(stem + '_Worn_ORM', orm, 'Non-Color')
    tx = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tx.image = im
    sep = mat.node_tree.nodes.new('ShaderNodeSeparateColor')
    mat.node_tree.links.new(tx.outputs['Color'], sep.inputs['Color'])
    mat.node_tree.links.new(sep.outputs['Green'], bs.inputs['Roughness'])
    mat.node_tree.links.new(sep.outputs['Blue'], bs.inputs['Metallic'])
    return {'material': mat.name, 'scratch_mean': float(scratch.mean()),
            'roughness_range': [float(orm[:, :, 1].min()), float(orm[:, :, 1].max())]}


def render(names, prefix):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_percentage = 100
    for name in names:
        scene.camera = bpy.data.objects['View_pbr_' + name]
        scene.render.filepath = str(HELPER.OUT / (prefix + '_' + name + '.png'))
        bpy.ops.render.render(write_still=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--preview', action='store_true')
    a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = Path(a.out).resolve()
    assert not out.exists(), 'Use a new output identity'
    out.mkdir(parents=True)
    HELPER.OUT = out
    source = BASE / 'GermanRifle_SPR_V10.blend'
    guard = {str(path): sha(path) for path in [source, BASE / 'GermanRifle_SPR_V10.glb']}
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    HELPER.SCENE = scene
    before = geometry_fingerprint()
    assert len(before) == 24
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 850
    if a.preview:
        scene.render.resolution_x = 1000
        scene.render.resolution_y = 607
        render(['quarter', 'receiver'], 'before')
    materials = [m for m in bpy.data.materials if m.name.startswith('V10_')]
    wear = []
    for i, mat in enumerate(sorted(materials, key=lambda m: m.name)):
        if mat.name == 'V10_Oiled_Walnut':
            wear.append(replace_wood(mat))
        else:
            wear.append(replace_steel(mat, 1200 + i))
        mat.name = mat.name.replace('V10_', 'V11_')
    assert geometry_fingerprint() == before, 'Geometry/UV/normals/transforms changed'
    render(['quarter', 'receiver'] if a.preview else ['right', 'left', 'quarter', 'top', 'underside', 'receiver'], 'pbr')
    scene.camera = bpy.data.objects['View_pbr_quarter']
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type == 'MESH' or obj.name == 'RifleRoot_Centered':
            obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects['Receiver_Donor_Lower']
    glb = out / (NAME + '.glb')
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True,
                              export_yup=True, export_vertex_color='NONE',
                              export_animations=False, export_apply=True)
    bpy.context.preferences.filepaths.save_version = 0
    # Already a small normal standalone scene; no library write or original-library save.
    bpy.ops.wm.save_as_mainfile(filepath=str(out / (NAME + '.blend')))
    assert all(sha(Path(path)) == value for path, value in guard.items()), 'V10 altered'
    report = {'stage': 'texture_weathering', 'blender': bpy.app.version_string,
              'name': NAME, 'baseline_files': guard, 'geometry_before': before,
              'geometry_after': geometry_fingerprint(), 'geometry_exact': True,
              'pivot_shift': json.loads((BASE / 'build_report.json').read_text())['pivot_shift'],
              'wear': wear, 'sha256_glb': sha(glb), 'sha256_blend': sha(out / (NAME + '.blend')),
              'baseline_form_user_approved': True, 'weathering_user_approved': False,
              'historical_approval': False, 'runtime_approval': False, 'shared': False}
    (out / 'build_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['geometry_exact', 'sha256_glb', 'baseline_form_user_approved']}), flush=True)


if __name__ == '__main__':
    main()
