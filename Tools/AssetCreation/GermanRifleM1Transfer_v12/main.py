"""Private, texture-only M1 patch transfer. No model, UV or original writes."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
V10 = ROOT / 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-v10/finish_v3'
V11 = ROOT / 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-spr-weather-v11/finish_v1'
TEX = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001/Textures/USParatrooper/Textures/M1_Garand'
NAME = 'GermanRifle_M1Texture_V12'
BOXES = {'wood': (569, 76, 1292, 510), 'steel': (1024, 922, 1229, 1126)}

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

H = module('v10', Path(__file__).parents[1] / 'GermanRifleSPR_v10/main.py')
W = module('v11', Path(__file__).parents[1] / 'GermanRifleSPR_v11/main.py')

def blur(data, radius=5):
    # Actual fine surface information, not new procedural noise. Remove broad
    # source curvature from tangent XY before transplanting to another shape.
    pad = np.pad(data, ((radius, radius), (radius, radius), (0, 0)), mode='reflect')
    integral = np.pad(pad, ((1, 0), (1, 0), (0, 0))).cumsum(0).cumsum(1)
    k = radius * 2 + 1
    return (integral[k:, k:] - integral[:-k, k:] - integral[k:, :-k] + integral[:-k, :-k]) / (k*k)

def mirror(t):
    phase = np.mod(t, 2)
    return np.where(phase <= 1, phase, 2-phase), np.where(phase <= 1, 1, -1)

def sample(data, u, v):
    h, w = data.shape[:2]
    x, y = u*(w-1), v*(h-1)
    ix, iy = np.floor(x).astype(int), np.floor(y).astype(int)
    jx, jy = np.minimum(ix+1, w-1), np.minimum(iy+1, h-1)
    fx, fy = (x-ix)[..., None], (y-iy)[..., None]
    return (data[iy, ix]*(1-fx)+data[iy, jx]*fx)*(1-fy) + (data[jy, ix]*(1-fx)+data[jy, jx]*fx)*fy

def load_patches():
    patches = {key: {} for key in BOXES}
    for suffix in ['D', 'N', 'ORM']:
        im = bpy.data.images.load(str(TEX / ('T_M1_Garand_'+suffix+'.png')), check_existing=False)
        im.colorspace_settings.name = 'sRGB' if suffix == 'D' else 'Non-Color'
        data = W.pixels(im)
        for key, (x0, y0, x1, y1) in BOXES.items():
            # bpy pixels are bottom-up, rectangles were reviewed top-left.
            patch = data[data.shape[0]-y1:data.shape[0]-y0, x0:x1].copy()
            if suffix == 'N':
                xy = patch[:, :, :2]*2-1
                xy[:, :, 1] *= -1  # M1 is DirectX, target is OpenGL.
                patch[:, :, :2] = xy - blur(xy)
            patches[key][suffix] = patch
        bpy.data.images.remove(im)
    return patches

def transfer(mat, patches):
    wood = mat.name == 'V10_Oiled_Walnut'
    patch = patches['wood' if wood else 'steel']
    bs = mat.node_tree.nodes.get('Principled BSDF')
    old_base = W.texture_for_input(bs, 'Base Color').image
    width, height = old_base.size
    width, height = max(1024, width), max(1024, height)
    u, v = np.meshgrid(np.linspace(0, 1, width), np.linspace(0, 1, height))
    # Wood length uses one continuous sample; circumference mirror closes seam.
    # Steel repeats a flat, hardware-free patch in mirrored pairs.
    su, usign = (u, np.ones_like(u)) if wood else mirror(u*4)
    sv, vsign = mirror(v*2 if wood else v*4)
    color = sample(patch['D'], su, sv)
    color[:, :, 3] = 1
    orm = sample(patch['ORM'], su, sv)
    orm[:, :, 0] = 1  # Do not bake M1 positional AO into another shape.
    orm[:, :, 3] = 1
    # One diagnosed preview correction: the source atlas is too glossy on this
    # shape/studio. Preserve its actual variation, adapt scalar response only.
    orm[:, :, 1] = np.clip(.36 + .80*orm[:, :, 1], .58, .82) if wood else np.clip(.30 + .55*orm[:, :, 1], .40, .65)
    if wood:
        orm[:, :, 2] = 0
    else:
        # Retain darker blued-steel intent, using actual M1 dirt/colour variation.
        color[:, :, :3] *= np.array((.64, .69, .75))
    fine = sample(patch['N'], su, sv)[:, :, :2]
    fine[:, :, 0] *= usign
    fine[:, :, 1] *= vsign
    normal = np.ones_like(color)
    if bs.inputs['Normal'].is_linked and not wood:
        old_nm = W.texture_for_input(bs, 'Normal')
        old_image = old_nm.inputs['Color'].links[0].from_node.image
        old = W.pixels(old_image)
        old_vec = sample(old, u, v)[:, :, :3]*2-1
        # Detail perturbation of existing tangent direction; structural donor
        # normals remain, not replaced by M1 receiver geometry.
        old_vec[:, :, :2] += fine * .6
        vec = old_vec / np.maximum(np.linalg.norm(old_vec, axis=2, keepdims=True), 1e-6)
    else:
        xy = fine * .8
        vec = np.concatenate([xy, np.sqrt(np.maximum(1-(xy*xy).sum(2), .01))[:, :, None]], 2)
        vec /= np.linalg.norm(vec, axis=2, keepdims=True)
    normal[:, :, :3] = vec*.5+.5
    stem = mat.name.replace('V10_', 'V12_M1_')
    new = H.principled(stem, (.15,.08,.03) if wood else (.17,.19,.21),
                       0 if wood else 1, .45,
                       H.image_data(stem+'_BaseColor', color),
                       H.image_data(stem+'_Normal', normal, 'Non-Color'),
                       H.image_data(stem+'_ORM', orm, 'Non-Color'))
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material == mat:
                    slot.material = new
    return {'material': new.name, 'surface': 'wood' if wood else 'steel',
            'texture_size': [width, height], 'patch_box_top_left': BOXES['wood' if wood else 'steel'],
            'roughness_range': [float(orm[:,:,1].min()), float(orm[:,:,1].max())]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--preview', action='store_true')
    p.add_argument('--no-render', action='store_true')
    args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    out = Path(args.out).resolve()
    assert not out.exists(), 'New identity required'
    out.mkdir(parents=True)
    H.OUT = out
    files = [V10/'GermanRifle_SPR_V10.blend', V10/'GermanRifle_SPR_V10.glb',
             V11/'GermanRifle_SPR_Weathered_V11.blend', V11/'GermanRifle_SPR_Weathered_V11.glb']
    files += [TEX/('T_M1_Garand_'+s+'.png') for s in ['D','N','ORM']]
    guard = {str(f): W.sha(f) for f in files}
    bpy.ops.wm.open_mainfile(filepath=str(files[0]), load_ui=False, use_scripts=False)
    H.SCENE = scene = bpy.context.scene
    H.PIVOT = Vector(json.loads((V10/'build_report.json').read_text())['pivot_shift'])
    before = W.geometry_fingerprint()
    assert len(before) == 24
    patches = load_patches()
    materials = [m for m in bpy.data.materials if m.name.startswith('V10_')]
    changes = [transfer(mat, patches) for mat in sorted(materials, key=lambda m:m.name)]
    assert W.geometry_fingerprint() == before
    if not args.no_render:
        if args.preview:
            scene.render.resolution_x, scene.render.resolution_y = 1200, 729
            W.HELPER.OUT = out
            W.render(['quarter','receiver'], 'pbr')
            scene.camera = H.camera('V12_Stock_Review', (-.20,0,-.065), (.1,-1,.4), .50)
            scene.render.filepath = str(out/'pbr_stock.png')
            bpy.ops.render.render(write_still=True)
        else:
            H.evidence('pbr', 'CYCLES')
    scene.camera = bpy.data.objects.get('View_pbr_quarter')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type == 'MESH' or obj.name == 'RifleRoot_Centered':
            obj.select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects['Receiver_Donor_Lower']
    glb = out/(NAME+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(glb), export_format='GLB', use_selection=True,
                             export_yup=True, export_vertex_color='NONE',
                             export_animations=False, export_apply=True)
    bpy.context.preferences.filepaths.save_version = 0
    # Drop unreferenced previous materials/images from output, not source files.
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=False, do_recursive=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(NAME+'.blend')))
    assert all(W.sha(Path(f)) == digest for f,digest in guard.items())
    report = {'stage':'M1_texture_transfer','blender':bpy.app.version_string,'name':NAME,
              'baseline_files':guard,'geometry_before':before,'geometry_after':W.geometry_fingerprint(),
              'geometry_exact':True,'pivot_shift':list(H.PIVOT),'changes':changes,
              'normal_method':'DX green inversion; 11x11 high-pass XY; mirrored sampling; donor structure plus detail',
              'albedo_method':'existing M1 linear sRGB sample, no random texture synthesis',
              'roughness_adaptation':'wood clamp(.36+.8*M1_G,.58,.82); steel clamp(.30+.55*M1_G,.40,.65)',
              'sha256_glb':W.sha(glb),'sha256_blend':W.sha(out/(NAME+'.blend')),
              'user_visual_approval':False,'historical_approval':False,'runtime_approval':False,'shared':False}
    (out/'build_report.json').write_text(json.dumps(report,indent=2), encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['geometry_exact','sha256_glb']}), flush=True)

if __name__ == '__main__':
    main()
