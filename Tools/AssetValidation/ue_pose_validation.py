"""Frame-sampled actual UE skinning, captures and a bounded compatible-rig trial."""
import json
import math
import os
import traceback
from collections import defaultdict
from pathlib import Path
from datetime import datetime
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
repair_mode = os.environ.get('CS549_NATIVE_REPAIR_REGRESSION') == '1'
OUT = LAB / ('Evidence/Repair20261001/NativeRegression' if repair_mode else 'Evidence')
OUT.mkdir(parents=True, exist_ok=True)
REPORT = {'engine': unreal.SystemLibrary.get_engine_version(),
          'started_at': datetime.now().astimezone().isoformat(),
          'samples': [], 'compatible_skeleton_trials': [], 'errors': []}


def checkpoint():
    (OUT / 'ue_pose_validation.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')


def fail(stage):
    REPORT['errors'].append({'stage': stage, 'traceback': traceback.format_exc()})
    checkpoint()


inventory = json.loads((LAB / 'Evidence/ue_load_inventory.json').read_text(encoding='utf-8'))
bone_maps = {a['path']: {b['name']: b['parent'] for b in a.get('bones', [])}
             for a in inventory['assets'] if a.get('class') == 'SkeletalMesh'}
source_path = '/Game/RifleAnimsetPro/UE4_Mannequin/Mesh/SK_Mannequin'
source_mesh = unreal.EditorAssetLibrary.load_asset(source_path)
source_skeleton = source_mesh.get_editor_property('skeleton')
selected = {
    'german_A': '/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varA',
    'german_B': '/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varB',
    'allied_A': '/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple',
    'allied_B': '/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simpleB',
}
if repair_mode:
    originals = dict(selected)
    selected = {label: '/Game/ParisCombat/Characters/Adaptation/Meshes/' + path.split('/')[-1] + '_UE582_v1'
                for label, path in originals.items()}
    for label, target_path in selected.items():
        bone_maps[target_path] = bone_maps[originals[label]]
clips = {'idle': 'Rifle_Idle', 'walk': 'Rifle_WalkFwdLoop', 'run': 'Rifle_RunFwdLoop',
         'fire': 'Rifle_ShootOnce', 'reload': 'Rifle_Reload_2',
         'hit': 'Rifle_Hit_C_1', 'death': 'Rifle_Death_3'}
stage_path = '/Game/ParisCombat/Tests/AssetValidation/PoseStage_' + datetime.now().strftime('%Y%m%d_%H%M%S')
REPORT['stage_path'] = stage_path
REPORT['view_axes'] = {'front': '+Y', 'side': '+X', 'back': '-Y', 'three_quarter': '+X,+Y'}
if not unreal.EditorLevelLibrary.new_level(stage_path):
    raise RuntimeError('Could not create isolated pose stage')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for rotation, intensity in [((-30, -135, 0), 20.0), ((-20, 45, 0), 8.0)]:
    light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 300), unreal.Rotator(*rotation))
    comp = light.get_component_by_class(unreal.DirectionalLightComponent)
    comp.set_intensity(intensity)
    comp.set_cast_shadows(False)
floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -2))
floor.static_mesh_component.set_static_mesh(unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Plane'))
floor.set_actor_scale3d(unreal.Vector(8, 8, 1))
capture_actor = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(420, 0, 95))
capture = capture_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
capture.set_editor_property('projection_type', unreal.CameraProjectionMode.ORTHOGRAPHIC)
capture.set_editor_property('ortho_width', 235.0)
capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
capture.set_editor_property('capture_every_frame', False)
capture.set_editor_property('capture_on_movement', False)
target = unreal.RenderingLibrary.create_render_target2d(world, 900, 1000,
    unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0.04, 0.04, 0.04, 1), False)
capture.set_editor_property('texture_target', target)
model = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
component = model.get_component_by_class(unreal.SkeletalMeshComponent)
loaded = {label: unreal.EditorAssetLibrary.load_asset(path) for label, path in selected.items()}
unreal.AutomationLibrary.finish_loading_before_screenshot()
checkpoints = ('pelvis', 'head', 'hand_l', 'hand_r', 'foot_l', 'foot_r')
for label, mesh_path in selected.items():
    mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
    skeleton = mesh.get_editor_property('skeleton')
    source = bone_maps[source_path]
    target_bones = bone_maps[mesh_path]
    missing = sorted(set(source) - set(target_bones))
    parents = [n for n in source if n in target_bones and source[n] != target_bones[n]]
    if missing or parents:
        REPORT['compatible_skeleton_trials'].append({'mesh': mesh_path, 'applied': False,
            'missing_bones': missing, 'parent_mismatches': parents})
        checkpoint()
        continue
    # A reversible lab-only compatibility declaration, gated by real UE hierarchy.
    skeleton.add_compatible_skeleton(source_skeleton)
    REPORT['compatible_skeleton_trials'].append({'mesh': mesh_path, 'applied': True,
        'skeleton': skeleton.get_path_name(), 'source_skeleton': source_skeleton.get_path_name(),
        'scope': 'lab trial only; not production/historical acceptance'})
    component.set_skeletal_mesh_asset(mesh)
    component.set_update_animation_in_editor(True)
    for action, clip_name in clips.items():
        try:
            sequence = unreal.EditorAssetLibrary.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/' + clip_name)
            length = unreal.AnimationLibrary.get_sequence_length(sequence)
            fractions = [i / 24.0 for i in range(25)] if action in ('walk', 'run') else [0, .25, .5, .75, .999]
            for sample_index, fraction in enumerate(fractions):
                time = length * min(fraction, .999)
                # A new component avoids reuse of the same commandlet-frame anim state.
                # OverrideAnimationData only initializes saved data when mode changes.
                actors.destroy_actor(model)
                model = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
                component = model.get_component_by_class(unreal.SkeletalMeshComponent)
                component.set_skeletal_mesh_asset(mesh)
                component.override_animation_data(sequence, False, False, time, 1.0)
                positions = {}
                for name in checkpoints:
                    transform = component.get_bone_transform(name, unreal.RelativeTransformSpace.RTS_COMPONENT)
                    positions[name] = [transform.translation.x, transform.translation.y, transform.translation.z]
                record = {'mesh': mesh_path, 'label': label, 'action': action,
                    'sequence': sequence.get_path_name(), 'time': time,
                    'bone_positions_cm': positions,
                    'finite': all(math.isfinite(v) for values in positions.values() for v in values),
                    'captures': []}
                if (action not in ('walk', 'run') or sample_index % 6 == 0) and (not repair_mode or sample_index in (0, 12)):
                    views = [('front', (0, 420, 95)), ('side', (420, 0, 95))]
                    if action == 'idle':
                        views += [('back', (0, -420, 95)), ('three_quarter', (330, 330, 95))]
                    for view, location in views:
                        point = unreal.Vector(*location)
                        capture_actor.set_actor_location(point, False, False)
                        capture_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(point, unreal.Vector(0, 0, 95)), False)
                        capture.capture_scene()
                        filename = f'{label}_{action}_{sample_index:02}_{view}.png'
                        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
                        record['captures'].append(filename)
                REPORT['samples'].append(record)
            unreal.log(f'CS549_POSE_PROGRESS {label} {action}')
            checkpoint()
        except Exception:
            fail(label + ' ' + action)
    unreal.EditorAssetLibrary.save_loaded_asset(skeleton, False)
unreal.EditorLevelLibrary.save_current_level()
grouped = defaultdict(list)
for sample in REPORT['samples']:
    grouped[(sample['label'], sample['action'])].append(sample)
REPORT['motion_variation'] = []
for (label, action), samples in grouped.items():
    first = samples[0]['bone_positions_cm']
    maximum = max(math.dist(first[bone], sample['bone_positions_cm'][bone])
                  for sample in samples for bone in checkpoints)
    REPORT['motion_variation'].append({'label': label, 'action': action,
                                      'max_checkpoint_displacement_cm': maximum})
    if action in ('walk', 'run', 'reload', 'death') and maximum < .01:
        REPORT['errors'].append({'stage': label + ' ' + action,
                                'error': 'No measured pose variation; reject stale-frame capture result.'})
REPORT['finished_at'] = datetime.now().astimezone().isoformat()
checkpoint()
unreal.log('CS549_POSE_DONE ' + str(len(REPORT['samples'])))
