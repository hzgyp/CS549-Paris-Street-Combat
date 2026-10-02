"""Isolated candidate pose/material/FBX evidence; never alter the Paris game."""
import hashlib
import json
import math
import os
import traceback
from datetime import datetime
from pathlib import Path
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
review_v2 = os.environ.get('CS549_WEAPON_REVIEW_V2') == '1'
OUT = LAB / ('Evidence/CandidateProbe_v2' if review_v2 else 'Evidence/CandidateProbe')
if (OUT / 'candidate_probe.json').exists():
    raise RuntimeError('Evidence exists; choose a new diagnostic directory, do not overwrite')
OUT.mkdir(parents=True, exist_ok=True)
inventory = json.loads((LAB / 'Evidence/ue_load_inventory.json').read_text(encoding='utf-8'))
index = {a['path']: a for a in inventory['assets']}
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'started_at': datetime.now().astimezone().isoformat(),
          'scope': 'arms and generic rifle motion only; no M1 contact/reload certification',
          'exports': [], 'samples': [], 'captures': [], 'errors': []}


def save():
    (OUT / 'candidate_probe.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


arm_path = '/Game/ShooterStarter/Skeletal/Arm_A/SKM_FPS_Arm_A'
source_path = '/Game/Rifle_01/Character/Mesh/SK_Mannequin'
source_bones = {b['name']: b['parent'] for b in index[source_path]['bones']}
target_bones = {b['name']: b['parent'] for b in index[arm_path]['bones']}
extra = set(source_bones) - set(target_bones)
mismatches = [n for n in target_bones if n not in source_bones or target_bones[n] != source_bones[n]]
if extra != {'hand_l_wep', 'hand_r_wep'} or mismatches:
    raise RuntimeError('Unexpected rig differences; no blind compatibility trial')
mesh = unreal.EditorAssetLibrary.load_asset(arm_path)
source_mesh = unreal.EditorAssetLibrary.load_asset(source_path)
mesh.get_editor_property('skeleton').add_compatible_skeleton(source_mesh.get_editor_property('skeleton'))
report['compatibility_trial'] = {'common_bones': len(target_bones), 'ignored_source_helpers': sorted(extra),
    'parent_mismatches': mismatches, 'scope': 'memory-only isolated lab trial, not saved compatibility metadata'}
source_refs = {b['name']: b for b in index[source_path]['bones']}
report['reference_pose_differences'] = []
for bone in index[arm_path]['bones']:
    source = source_refs[bone['name']]
    a, b = bone['ref_local_rotation_xyzw'], source['ref_local_rotation_xyzw']
    dot = abs(sum(x*y for x,y in zip(a,b))) / math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
    angle = math.degrees(2 * math.acos(min(1.0, dot)))
    distance = math.sqrt(sum((x-y)**2 for x,y in zip(bone['ref_local_translation_cm'], source['ref_local_translation_cm'])))
    report['reference_pose_differences'].append({'bone': bone['name'], 'local_rotation_degrees': angle,
        'local_translation_difference_cm': distance})
report['compatibility_trial']['warning'] = 'Matching hierarchy is not a retarget pass; differing bind rotations require an evaluated retarget.'
clips = {'idle': '/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Idle_IP',
         'fire': '/Game/Rifle_01/Animation/In-Place/W2_Stand_Fire_Single_IP',
         'reload_generic': '/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP'}
save()

try:
    if not unreal.EditorLevelLibrary.new_level('/Game/ParisCombat/Tests/WeaponCandidates/Probe_' + datetime.now().strftime('%Y%m%d_%H%M%S')):
        raise RuntimeError('Could not create isolated stage')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for pitch, yaw, intensity in [(-35, -120, 20 if review_v2 else 8), (-20, 50, 8 if review_v2 else 4)]:
        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 300),
            unreal.Rotator(pitch=pitch, yaw=yaw, roll=0))
        comp = light.get_component_by_class(unreal.DirectionalLightComponent)
        comp.set_intensity(intensity)
        comp.set_cast_shadows(False)
    if review_v2:
        sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 300))
        comp = sky.get_component_by_class(unreal.SkyLightComponent)
        comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        comp.set_editor_property('source_type', unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
        comp.set_cubemap(unreal.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'))
        comp.set_intensity(1.0)
        comp.recapture_sky()
    capture_actor = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(-300, 0, 130))
    capture = capture_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('capture_every_frame', False)
    capture.set_editor_property('capture_on_movement', False)
    if review_v2:
        capture.set_editor_property('override_custom_near_clipping_plane', True)
        capture.set_editor_property('custom_near_clipping_plane', 1.0)
        report['capture_condition'] = 'Daylight cubemap fill, 20/8 directional lights, FP 90deg/1cm near; diagnostic only'
    target = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.08, .08, .08, 1), False)
    capture.set_editor_property('texture_target', target)
    sequences = {label: unreal.EditorAssetLibrary.load_asset(path) for label, path in clips.items()}
    if review_v2:
        sequences = {'reference': None, **sequences}
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    model = None
    for action, sequence in sequences.items():
        length = unreal.AnimationLibrary.get_sequence_length(sequence) if sequence else 0
        for sample, fraction in enumerate([0, .15, .3, .5, .7, .85, .999] if sequence else [0]):
            if model:
                actors.destroy_actor(model)
            model = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
            component = model.get_component_by_class(unreal.SkeletalMeshComponent)
            component.set_skeletal_mesh_asset(mesh)
            if sequence:
                component.override_animation_data(sequence, False, False, length * fraction, 1.0)
            positions = {}
            for bone in ['upperarm_l', 'lowerarm_l', 'hand_l', 'index_03_l', 'thumb_03_l',
                         'upperarm_r', 'lowerarm_r', 'hand_r', 'index_03_r', 'thumb_03_r']:
                t = component.get_bone_transform(bone, unreal.RelativeTransformSpace.RTS_COMPONENT).translation
                positions[bone] = [t.x, t.y, t.z]
            report['samples'].append({'action': action, 'sequence': clips.get(action), 'fraction': fraction,
                'time_seconds': length * fraction, 'positions_cm': positions,
                'finite': all(math.isfinite(v) for xyz in positions.values() for v in xyz)})
            views = [('front_minus_y', (0, -250, 145), (0, 0, 140)),
                     ('side_plus_x', (250, 0, 145), (0, 0, 140)),
                     ('fp_minus_y', (0, 15, 160), (0, -70, 140)),
                     ('fp_plus_y', (0, -15, 160), (0, 70, 140))] if review_v2 else [('front', (250, 0, 145), (0, 0, 140)),
                                        ('side', (0, 250, 145), (0, 0, 140)),
                                        ('fp_diagnostic', (-15, 0, 160), (70, 0, 140))]
            for view, location, aim in views:
                point = unreal.Vector(*location)
                capture_actor.set_actor_location(point, False, False)
                capture_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(point, unreal.Vector(*aim)), False)
                capture.set_editor_property('projection_type', unreal.CameraProjectionMode.PERSPECTIVE
                    if view.startswith('fp_') else unreal.CameraProjectionMode.ORTHOGRAPHIC)
                capture.set_editor_property('ortho_width', 160.0)
                capture.set_editor_property('fov_angle', 90.0)
                capture.capture_scene()
                filename = f'{action}_{sample:02d}_{view}.png'
                unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
                report['captures'].append({'action': action, 'fraction': fraction, 'view': view,
                                          'file': filename, 'exists': (OUT / filename).exists()})
            save()
    options = unreal.FbxExportOption()
    options.set_editor_property('fbx_export_compatibility', unreal.FbxExportCompatibility.FBX_2018)
    options.set_editor_property('ascii', False)
    options.set_editor_property('level_of_detail', False)
    options.set_editor_property('collision', False)
    options.set_editor_property('export_preview_mesh', False)
    options.set_editor_property('bake_material_inputs', unreal.FbxMaterialBakeMode.DISABLED)
    paths = [arm_path, arm_path + '_Left', arm_path + '_Right'] + list(clips.values())
    if review_v2:
        paths = []  # Reuse V1 exchange evidence; do not create redundant exports.
    for path in paths:
        asset = unreal.EditorAssetLibrary.load_asset(path)
        file = OUT / (asset.get_name() + '.fbx')
        task = unreal.AssetExportTask()
        task.object, task.filename, task.options = asset, str(file), options
        task.automated, task.prompt, task.replace_identical = True, False, False
        ok = unreal.Exporter.run_asset_export_task(task)
        report['exports'].append({'asset': path, 'file': file.name, 'ok': bool(ok),
            'size_bytes': file.stat().st_size if file.exists() else 0,
            'sha256': hashlib.sha256(file.read_bytes()).hexdigest() if file.exists() else None})
        save()
except Exception:
    report['errors'].append(traceback.format_exc())
report['finished_at'] = datetime.now().astimezone().isoformat()
save()
unreal.log('CS549_WEAPON_CANDIDATE_DONE ' + str(len(report['samples'])))
