"""Bounded active-project six-actor preview, not gameplay/AI acceptance."""
import json
import math
import traceback
from datetime import datetime
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/P2'
OUT.mkdir(parents=True, exist_ok=True)
MAP = '/Game/ParisCombat/Tests/Integration/P2_CharacterPreview_20261001'
REPORT = {'started_at': datetime.now().astimezone().isoformat(),
    'engine': unreal.SystemLibrary.get_engine_version(), 'map': MAP,
    'scope': 'Controlled renderer preview and frame-sampled native poses only; no combatant Blueprint, movement/capsule, AI, gun contact, city lighting or performance acceptance',
    'actors': [], 'poses': [], 'captures': [], 'errors': []}


def checkpoint():
    (OUT / 'presentation.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')


def position(component, bone):
    t = component.get_bone_transform(bone, unreal.RelativeTransformSpace.RTS_COMPONENT).translation
    return [t.x, t.y, t.z]


meshes = {
    'allied_A': 'SK_WWII_US_Paratrooper_simple_UE582_v1',
    'allied_B': 'SK_WWII_US_Paratrooper_simpleB_UE582_v1',
    'german_A': 'SK_WWII_GermanSoldier_varA_UE582_v1',
    'german_B': 'SK_WWII_GermanSoldier_varB_UE582_v1',
}
clips = {'idle': 'Rifle_Idle', 'walk': 'Rifle_WalkFwdLoop', 'run': 'Rifle_RunFwdLoop',
         'fire': 'Rifle_ShootOnce', 'reload': 'Rifle_Reload_2',
         'hit': 'Rifle_Hit_C_1', 'death': 'Rifle_Death_3'}
checkpoint()
try:
    # A rerun must not overwrite an edited diagnostic scene.
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        raise RuntimeError('Preview already exists; preserve it and choose a new dated task identity')
    probe = json.loads((STORE / 'Evidence/P1/active_project_probe.json').read_text(encoding='utf-8'))
    if probe['result'] != 'pass_structural_probe':
        raise RuntimeError('P1 must pass before presentation')
    if not unreal.EditorLevelLibrary.new_level(MAP):
        raise RuntimeError('Cannot create team-owned preview map')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    loaded = {k: unreal.load_asset('/Game/ParisCombat/Characters/Adaptation/Meshes/' + v)
              for k, v in meshes.items()}
    sequences = {k: unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/' + v)
                 for k, v in clips.items()}
    if not all(loaded.values()) or not all(sequences.values()):
        raise RuntimeError('Required native mesh/action missing')
    for rotation, intensity in [((-35, -135, 0), 20), ((-20, 45, 0), 8)]:
        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(240, 140, 400), unreal.Rotator(*rotation))
        component = light.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_intensity(intensity)
        component.set_cast_shadows(True)
    floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(240, 140, -2))
    floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane'))
    floor.set_actor_scale3d(unreal.Vector(14, 14, 1))
    floor.set_actor_label('P2_ControlledFloor_NotMission')
    for x in (-250, 740):
        obstacle = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(x, 140, 50))
        obstacle.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
        obstacle.set_actor_label('P2_ContactObstacle_NotTested')
    roster = [('allied_A', 'idle'), ('allied_B', 'walk'), ('allied_A', 'run'),
              ('german_A', 'idle'), ('german_B', 'walk'), ('german_A', 'run')]
    for index, (label, action) in enumerate(roster):
        loc = unreal.Vector((index % 3) * 240, (index // 3) * 280, 0)
        actor = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, loc)
        actor.set_actor_label('P2_Preview_%d_%s_%s' % (index + 1, label, action))
        component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        component.set_skeletal_mesh_asset(loaded[label])
        component.override_animation_data(sequences[action], True, True, 0, 1)
        component.set_update_animation_in_editor(True)
        REPORT['actors'].append({'label': actor.get_actor_label(), 'mesh': loaded[label].get_path_name(),
            'action': sequences[action].get_path_name(), 'location_cm': [loc.x, loc.y, loc.z],
            'type': 'SkeletalMeshActor preview, not Character/AI'})
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    bones = ('pelvis', 'head', 'hand_l', 'hand_r', 'foot_l', 'foot_r')
    for label, mesh in loaded.items():
        for action, sequence in sequences.items():
            poses = []
            length = unreal.AnimationLibrary.get_sequence_length(sequence)
            for fraction in (0, .5, .999):
                actor = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
                component = actor.get_component_by_class(unreal.SkeletalMeshComponent)
                component.set_skeletal_mesh_asset(mesh)
                component.override_animation_data(sequence, False, False, length * fraction, 1)
                values = {bone: position(component, bone) for bone in bones}
                poses.append({'time': length * fraction, 'bone_positions_cm': values,
                    'finite': all(math.isfinite(v) for p in values.values() for v in p)})
                actors.destroy_actor(actor)
            variation = max(math.dist(poses[0]['bone_positions_cm'][bone], p['bone_positions_cm'][bone])
                            for p in poses for bone in bones)
            REPORT['poses'].append({'mesh': mesh.get_path_name(), 'action': action,
                'sequence': sequence.get_path_name(), 'root_motion': sequence.get_editor_property('enable_root_motion'),
                'samples': poses, 'max_displacement_cm': variation})
            if not all(p['finite'] for p in poses) or (action in ('walk', 'run', 'reload', 'death') and variation < .01):
                REPORT['errors'].append({'pose': label + '/' + action, 'reason': 'Nonfinite or stale pose'})
        checkpoint()
    camera = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(240, 1250, 370))
    capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('capture_every_frame', False)
    capture.set_editor_property('capture_on_movement', False)
    capture.set_editor_property('fov_angle', 48)
    target = unreal.RenderingLibrary.create_render_target2d(world, 1600, 1000,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.04, .04, .04, 1), False)
    capture.set_editor_property('texture_target', target)
    for name, point in [('six_front', (240, 1250, 370)), ('six_side', (1300, 200, 320))]:
        loc = unreal.Vector(*point)
        camera.set_actor_location(loc, False, False)
        camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(loc, unreal.Vector(240, 140, 90)), False)
        capture.capture_scene()
        filename = name + '.png'
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
        REPORT['captures'].append({'file': filename, 'exists': (OUT / filename).exists()})
    capture.set_editor_property('fov_angle', 12.5)
    for label, x, y in [('allied_A', 0, 0), ('allied_B', 240, 0),
                        ('german_A', 0, 280), ('german_B', 240, 280)]:
        loc = unreal.Vector(x + 220, y + 220, 162)
        camera.set_actor_location(loc, False, False)
        camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(loc, unreal.Vector(x, y, 162)), False)
        capture.capture_scene()
        filename = label + '_head.png'
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
        REPORT['captures'].append({'file': filename, 'exists': (OUT / filename).exists()})
    # Do not persist a transient render target reference in the saved map.
    actors.destroy_actor(camera)
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError('Preview map save failed')
    REPORT['map_saved'] = True
except Exception:
    REPORT['errors'].append({'traceback': traceback.format_exc()})
REPORT['finished_at'] = datetime.now().astimezone().isoformat()
REPORT['result'] = 'preview_generated_pending_visual_review' if not REPORT['errors'] else 'fail'
checkpoint()
unreal.log('CS549_PRESENTATION_DONE ' + REPORT['result'])
if REPORT['errors']:
    raise RuntimeError('Read presentation.json; do not label this run accepted')
