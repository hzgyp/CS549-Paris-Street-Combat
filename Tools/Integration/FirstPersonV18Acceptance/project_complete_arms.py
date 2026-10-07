"""Read-only V18 whole-arm projection in an immutable captured native frame."""
import hashlib
import json
import math
import sys
import traceback
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'WeaponTriggerAlignmentV2'))
from blender_contact_common import STORE, ROOT, FBX, POSES, AUDIT, CALIB, TOPOLOGY, load, mat, skin, transform
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'WeaponTriggerPivotV12'))
from pivot_common import guarded_files

OUT = STORE/'Evidence/FirstPersonV18Acceptance/projection_v1'
V18 = STORE/'Evidence/WeaponPinkyLengthV18/distal_v1'
V16 = STORE/'Evidence/WeaponMarkedGripV16/marked_raise_v1/result.json'
CAPTURE = STORE/'Evidence/ReloadRepairV5/sleeve_native_views_v2/result.json'
assert not OUT.exists(), 'Do not overwrite prior evidence'
OUT.mkdir(parents=True)
paths = [FBX, POSES, AUDIT, CALIB, TOPOLOGY, V16, CAPTURE,
         V18/'result.json', V18/'RightPinkyDistalShorter.blend', Path(__file__)]
hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
r = {'scope':__doc__, 'errors':[], 'native_authored':False,
     'formal_selection':False, 'deleted_files':[],
     'limitations':['Offline projection, not native/gameplay/motion acceptance.',
                    'Recorded ordinary-holding frame; no new framing adaptation.',
                    'Portable original textures, not full native shader parity.']}

def write():
    (OUT/'result.json').write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')

def corners_reverse(mesh):
    positions = [tuple(v.co) for v in mesh.vertices]
    faces = [tuple(p.vertices)[::-1] for p in mesh.polygons]
    slots = [p.material_index for p in mesh.polygons]
    materials = list(mesh.materials)
    uvs = {u.name: [[tuple(u.data[i].uv) for i in p.loop_indices][::-1]
                    for p in mesh.polygons] for u in mesh.uv_layers}
    copy = bpy.data.meshes.new(mesh.name+' - projection parity')
    copy.from_pydata(positions, [], faces)
    for m in materials:
        copy.materials.append(m)
    for p, slot in zip(copy.polygons, slots):
        p.material_index = slot
        p.use_smooth = True
    for name, values in uvs.items():
        layer = copy.uv_layers.new(name=name)
        for p, row in zip(copy.polygons, values):
            for loop, uv in zip(p.loop_indices, row):
                layer.data[loop].uv = uv
    copy.update()
    return copy

try:
    r['guards_before'] = guarded_files()
    assert not r['guards_before']['mismatches']
    capture = json.loads(CAPTURE.read_text())
    sample = capture['captures'][0]['before']
    assert sample['phase'] == 0 and sample['camera_relative'] == [25.,0.,60.] and sample['fov'] == 90
    camera_world, display_world = mat(sample['camera_world']), mat(sample['display_world'])
    d = load()
    raw_bones = {n:mat(t) for n,t in d['poses']['0.0']['bones_component'].items()}
    control_gun = raw_bones['hand_r'] @ d['relative']
    recorded_gun = mat(sample['gun_world'])
    calculated_gun = display_world @ control_gun
    position_error = float(np.linalg.norm(calculated_gun[:3,3]-recorded_gun[:3,3]))
    rotation_delta = np.linalg.inv(recorded_gun[:3,:3]) @ calculated_gun[:3,:3]
    angle_error = math.degrees(math.acos(float(np.clip((np.trace(rotation_delta)-1)/2,-1,1))))
    r['native_frame_control'] = {'gun_position_error_cm':position_error,
                                 'gun_angle_error_degrees':angle_error,
                                 'capture':str(CAPTURE.relative_to(ROOT)),
                                 'camera':sample['camera_world'], 'display':sample['display_world'],
                                 'fov_horizontal':90, 'aspect':[16,9]}
    assert position_error < .01 and angle_error < .001, 'Captured source/frame mismatch'
    original = skin(d['p'],d['weights'],{n:raw_bones[n]@d['invref'][n] for n in d['invref'] if n in raw_bones})
    v18 = json.loads((V18/'result.json').read_text())
    gun0 = np.array(v18['baseline_gun_component_matrix'])
    control_arm = transform(original, np.linalg.inv(gun0))*.01
    control_gun_vertices = transform(d['gp'], np.linalg.inv(gun0)@control_gun)*.01
    bpy.ops.wm.open_mainfile(filepath=str(V18/'RightPinkyDistalShorter.blend'), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    arms = bpy.data.objects['Frozen V16 continuous arms']
    gun = bpy.data.objects['Frozen V16 M1']
    candidate_arm = np.array([tuple(v.co) for v in arms.data.vertices])
    candidate_gun = np.array([tuple(v.co) for v in gun.data.vertices])
    assert len(control_arm)==len(candidate_arm) and len(control_gun_vertices)==len(candidate_gun)
    r['complete_mesh'] = {'arm_vertices':len(arms.data.vertices), 'arm_faces':len(arms.data.polygons),
                          'gun_vertices':len(gun.data.vertices), 'gun_faces':len(gun.data.polygons),
                          'closeup_partial_meshes_used':False}
    assert len(arms.data.polygons)==10943
    # Final blend lives in baseline gun-local metres, native camera matrices in
    # cm. Reflect Y into a right-handed Blender basis and reverse polygon/UV
    # corners in this disposable render copy. Original source remains unchanged.
    S = np.diag([1.,-1.,1.,1.])
    frame = S @ np.linalg.inv(camera_world) @ display_world @ gun0
    frame[:3,3] *= .01
    r['diagnostic_frame_matrix_metres'] = frame.tolist()
    for obj in scene.objects:
        if obj.type=='MESH':
            obj.hide_render=True
    for obj in (arms,gun):
        obj.data=corners_reverse(obj.data)
        obj.hide_render=False
        obj.hide_set(False)
        obj.matrix_world=Matrix(frame.tolist())
    cd = bpy.data.cameras.new('Recorded protected FP camera')
    cam = bpy.data.objects.new(cd.name, cd)
    scene.collection.objects.link(cam)
    cam.matrix_world = Matrix(((0,0,-1,0),(-1,0,0,0),(0,1,0,0),(0,0,0,1)))
    cd.type='PERSP'
    cd.sensor_fit='HORIZONTAL'
    cd.sensor_width=36
    cd.lens=18
    cd.clip_start=.001
    cd.clip_end=50
    scene.camera=cam
    scene.render.resolution_x=1280
    scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.render.pixel_aspect_x=scene.render.pixel_aspect_y=1
    scene.render.film_transparent=False
    # Transform studio lights with the same assembly, no mesh/pose alteration.
    for obj in scene.objects:
        if obj.type=='LIGHT':
            obj.matrix_world=Matrix(frame.tolist())@obj.matrix_world
    renders=[]
    for label,a,g in [('source_control',control_arm,control_gun_vertices),
                       ('accepted_V18',candidate_arm,candidate_gun)]:
        for obj,points in ((arms,a),(gun,g)):
            for vertex,p in zip(obj.data.vertices,points):
                vertex.co=p
            obj.data.update()
        scene.render.filepath=str(OUT/(label+'_first_person.png'))
        bpy.ops.render.render(write_still=True)
        renders.append({'label':label, 'file':label+'_first_person.png'})
    r['renders']=renders
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CompleteArmsProjectionOnly.blend'))
    r['status']='whole_arm_projection_ready_for_visual_review_not_runtime_acceptance'
except Exception:
    r['status']='stopped_diagnostic_error'
    r['errors'].append(traceback.format_exc())
finally:
    r['inputs_unchanged']=all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v for k,v in hashes.items())
    r['input_hashes']=hashes
    r['guards_after']=guarded_files()
    write()
    print(json.dumps({k:r.get(k) for k in ('status','errors','native_frame_control','inputs_unchanged','guards_after')}),flush=True)
    if r['errors'] or not r['inputs_unchanged'] or r['guards_after']['mismatches']:
        raise SystemExit(1)
