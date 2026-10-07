"""Reconstruct actual Allied native hold; one fixed-hand, stock-pivot gun fit."""
import argparse
import json
import sys
import traceback
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, STORE, BASE, BASELINE, read, write, sha, guards
sys.path.insert(0, str(ROOT / 'Tools/Integration/WeaponTriggerAlignmentV2'))
from blender_contact_common import mat, transform, skin, intersection_pairs

parser = argparse.ArgumentParser()
parser.add_argument('--identity', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
assert args.identity.replace('_', '').isalnum()
OUT = BASE / args.identity
assert not OUT.exists(), 'Never overwrite an inspection identity'
OUT.mkdir(parents=True)
LAB = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1/Evidence/Repair20261001'
FBX = LAB / 'Exchange/SK_WWII_US_Paratrooper_simple.fbx'
AUDIT = STORE / 'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json'
TOPO = STORE / 'Evidence/WeaponTriggerAlignmentV1/topology_v1/result.json'
inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in (BASELINE, FBX, AUDIT, TOPO, Path(__file__))}
r = {'errors': [], 'scope': __doc__, 'native_authored': False,
     'source_pose_mesh_weights_modified': False, 'renders': [],
     'guards_before': guards(), 'input_hashes': inputs}
write(OUT / 'source.json', {'identity': args.identity, 'input_hashes': inputs})

def nearest(points, faces, target):
    b = BVHTree.FromPolygons([Vector(p) for p in points], faces.tolist(), all_triangles=True)
    p, n, i, gap = b.find_nearest(Vector(target))
    assert p is not None
    return np.array(p), int(i), float(gap)

def contact(positions, faces, masks, gun, gt, groups):
    result = {}
    for name, mask in masks.items():
        ids = np.flatnonzero(np.any(mask[faces], axis=1))
        pairs = intersection_pairs(positions, faces[ids], gun, gt)
        result[name] = {part: sorted({int(ids[a]) for a, b in pairs if b in group})
                        for part, group in groups.items()}
    return result

def material(name, color):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*color, 1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .72
    return m

def mesh(name, p, t, materials, slots):
    md = bpy.data.meshes.new(name)
    md.from_pydata((p*.01).tolist(), [], t[:, ::-1].tolist())
    md.update()
    o = bpy.data.objects.new(name, md)
    bpy.context.collection.objects.link(o)
    for m in materials: md.materials.append(m)
    for f, s in zip(md.polygons, slots):
        f.material_index = int(s)
        f.use_smooth = True
    return o

try:
    baseline = read(BASELINE)
    assert not baseline['errors']
    pair = baseline['pairs']['allied']
    assert pair['actor'] == 'PC_City_Ally1'
    assert 'SK_WWII_US_Paratrooper_simple_UE582_v1' in pair['skeletal_mesh']
    assert 'Sm_M1_Garand' in pair['gun_mesh']
    model = read(AUDIT)['models']['owner']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(FBX), automatic_bone_orientation=False, use_anim=False)
    rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    source = next(o for o in bpy.data.objects if o.type == 'MESH')
    names = [n for n in model['ref_component'] if n in rig.data.bones]
    src = np.array([list(rig.matrix_world @ rig.data.bones[n].head_local)+[1] for n in names])
    dst = np.array([model['ref_component'][n]['translation'] for n in names])
    fit = np.linalg.lstsq(src, dst, rcond=None)[0]
    r['reference_alignment'] = {'bones': len(names), 'max_cm': float(np.linalg.norm(src@fit-dst, axis=1).max()),
        'determinant': float(np.linalg.det(fit[:3, :])), 'matrix': fit.tolist()}
    write(OUT / 'result.json', r)
    assert len(names) >= 60 and r['reference_alignment']['max_cm'] < .01
    assert r['reference_alignment']['determinant'] < 0, 'Explicit UE reflection required'
    ref = {n: mat(t) for n, t in model['ref_component'].items()}
    mesh_world = mat(pair['mesh_world'])
    bones = {n: np.linalg.inv(mesh_world)@mat(t) for n, t in pair['bone_world'].items()}
    assert set(ref) <= set(bones), set(ref)-set(bones)
    rest = np.array([list(source.matrix_world @ v.co)+[1] for v in source.data.vertices])@fit
    weights = [{source.vertex_groups[g.group].name: float(g.weight) for g in v.groups if g.weight > 0}
               for v in source.data.vertices]
    assert all(w and abs(sum(w.values())-1) < .001 and set(w) <= set(ref) for w in weights)
    p = skin(rest, weights, {n: bones[n]@np.linalg.inv(ref[n]) for n in ref})
    source.data.calc_loop_triangles()
    tri = np.array([list(t.vertices) for t in source.data.loop_triangles], int)
    slots = np.array([t.material_index for t in source.data.loop_triangles])
    masks = {side: np.array([any(v > 0 and (n == 'hand_'+side or
        (n.endswith('_'+side) and n.startswith(('index_', 'middle_', 'ring_', 'pinky_', 'thumb_'))))
        for n, v in w.items()) for w in weights]) for side in ('r', 'l')}
    for digit in ('index', 'thumb', 'middle', 'ring', 'pinky'):
        masks[digit] = np.array([any(v > 0 and n.startswith(digit+'_') and n.endswith('_r')
            for n, v in w.items()) for w in weights])
    distal = np.array([sum(v for n, v in w.items() if n in ('index_02_r', 'index_03_r')) > .8 for w in weights])
    topo = read(TOPO)
    gp = np.array(topo['gun_points_cm'])
    gt = np.array(topo['gun_triangles'], int)
    local_gun = np.linalg.inv(mesh_world)@mat(pair['gun_world'])
    gun = transform(gp, local_gun)
    parts = {int(c['id']): set(c['triangle_ids']) for c in topo['components']}
    groups = {'stock': parts[0], 'guard': parts[4], 'blade': parts[5], 'whole': set(range(len(gt)))}
    blade_ids = np.array(sorted(groups['blade']), int)
    blade_centroid = gun[np.unique(gt[blade_ids])].mean(0)
    index_faces = tri[np.all(distal[tri], axis=1)]
    assert len(index_faces) > 10
    pad, pad_face, _ = nearest(p, index_faces, blade_centroid)
    blade, blade_face, gap = nearest(gun, gt[blade_ids], pad)
    # Actual stock surface closest to the right wrist/web region. This is a
    # recorded seating pivot, not an average of finger bones treated as contact.
    stock_ids = np.array(sorted(groups['stock']), int)
    pivot, pivot_face, _ = nearest(gun, gt[stock_ids], bones['hand_r'][:3, 3])
    a, b = blade-pivot, pad-pivot
    rotation = Vector(a).rotation_difference(Vector(b)).to_matrix()
    rot = np.array(rotation, float)
    change = np.eye(4)
    change[:3, :3] = rot
    change[:3, 3] = pivot-rot@pivot
    candidate_gun = transform(gun, change)
    new_blade, new_face, new_gap = nearest(candidate_gun, gt[blade_ids], pad)
    before = contact(p, tri, masks, gun, gt, groups)
    after = contact(p, tri, masks, candidate_gun, gt, groups)
    new_right = sorted(set(after['r']['stock']+after['r']['guard'])-set(before['r']['stock']+before['r']['guard']))
    r.update(pose_source=pair, vertices=len(p), triangles=len(tri),
        pad_cm=pad.tolist(), blade_cm=blade.tolist(), blade_triangle=int(blade_ids[blade_face]),
        stock_pivot_cm=pivot.tolist(), stock_pivot_triangle=int(stock_ids[pivot_face]),
        index_pad_to_blade_cm_before=gap, index_pad_to_blade_cm_after=new_gap,
        stock_pivot_radius_cm={'blade': float(np.linalg.norm(a)), 'pad': float(np.linalg.norm(b))},
        candidate_rotation_deg=float(Vector(a).angle(Vector(b))*180/np.pi),
        change_component_matrix=change.tolist(), candidate_gun_component_matrix=(change@local_gun).tolist(),
        candidate_gun_to_hand_matrix=(np.linalg.inv(bones['hand_r'])@change@local_gun).tolist(),
        before_crossing_faces=before, after_crossing_faces=after, new_right_stock_guard_faces=new_right,
        left_support_not_refitted=True, full_contact_accepted=False)
    r['early_trigger_stock_gate'] = new_gap <= .3 and not new_right
    write(OUT / 'result.json', r)
    materials = [material('original slot '+str(i), (.17,.20,.09) if i not in (0,) else (.62,.43,.28))
                 for i in range(max(int(slots.max())+1, 2))]
    body = mesh('Whole Allied source skin; diagnostic only', p, tri, materials, slots)
    gun_materials = [material('wood', (.20,.08,.025)), material('metal', (.14,.16,.17))]
    gun_slots = np.array([0 if i in groups['stock'] else 1 for i in range(len(gt))])
    gun_obj = mesh('Actual M1 diagnostic', gun, gt, gun_materials, gun_slots)
    for o in (source, rig): o.hide_render = True
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x, scene.render.resolution_y = 1200, 900
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new('Diagnostic')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.11,.12,.14,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .45
    cd = bpy.data.cameras.new('Matched camera')
    cam = bpy.data.objects.new('Matched camera', cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cd.type = 'ORTHO'
    center = (bones['hand_r'][:3,3]+bones['hand_l'][:3,3])/2*.01
    for name, delta in (('Key', (-1.5,.8,2)), ('Fill',(1.3,-.5,.8))):
        ld = bpy.data.lights.new(name, 'AREA')
        ld.energy, ld.size = 100, 2
        light = bpy.data.objects.new(name, ld)
        scene.collection.objects.link(light)
        light.location = Vector(center)+Vector(delta)
        light.rotation_euler = (Vector(center)-light.location).to_track_quat('-Z','Y').to_euler()
    views = [('right', [1,0,.02], .65), ('reverse',[-1,0,.02],.65), ('top',[0,0,1],.65),
             ('full_arm',[1,0,.1],1.5)]
    for label, data in (('before', gun), ('candidate', candidate_gun)):
        for v, co in zip(gun_obj.data.vertices, data*.01): v.co = co
        gun_obj.data.update()
        for name, delta, width in views:
            target = center if name != 'full_arm' else (center+bones['spine_03'][:3,3]*.01)/2
            cam.location = Vector(target)+Vector(delta)
            cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
            cd.ortho_scale = width
            scene.render.filepath = str(OUT/(label+'_'+name+'.png'))
            bpy.ops.render.render(write_still=True)
            r['renders'].append(label+'_'+name+'.png')
            write(OUT / 'result.json', r)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'AlliedContactDiagnostic.blend'))
    r['status'] = 'candidate_requires_visual_review' if r['early_trigger_stock_gate'] else 'stopped_contact_gate'
except Exception:
    r['errors'].append(traceback.format_exc())
    r['status'] = 'failed_preflight_or_reconstruction'
finally:
    r['inputs_unchanged'] = all(sha(ROOT/p) == h for p, h in inputs.items())
    r['guards_after'] = guards()
    write(OUT / 'result.json', r)
    print(json.dumps({k:r.get(k) for k in ('status','errors','reference_alignment',
        'early_trigger_stock_gate','candidate_rotation_deg','index_pad_to_blade_cm_before',
        'index_pad_to_blade_cm_after','inputs_unchanged','guards_after')}))
