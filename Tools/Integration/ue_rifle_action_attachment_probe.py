"""Unsaved gun-only left shift and action fitting; no pose/model/camera changes."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ['CS549_RIFLE_ACTION_PROBE_IDENTITY']
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/RifleActionAttachmentV3' / IDENTITY
assert not OUT.exists()
OUT.mkdir(parents=True)
inventory = json.loads((ROOT / 'Assets/Integration/CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json').read_text())
deps = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text())
records = inventory['files'] + deps['files'] + inventory['retained_unselected_rejected_trial']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert all((ROOT / e['path']).stat().st_size == e['size_bytes'] and digest(ROOT / e['path']) == e['sha256'] for e in records)
report = {'scope': __doc__, 'status': 'initializing', 'errors': [], 'samples': [], 'captures': []}
sources = {}

def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2))

def xyz(v):
    return [v.x, v.y, v.z]

def bone(n):
    return mesh.get_socket_location(n)

def center(side):
    fingers = ('middle', 'ring', 'pinky') if side == 'r' else ('index', 'middle', 'ring', 'pinky')
    names = [f + '_0' + str(s) + '_' + side for f in fingers for s in (2, 3)] + ['thumb_02_' + side, 'thumb_03_' + side]
    return sum((bone(n) for n in names), unreal.Vector()) / len(names)

def mount(profile):
    root.set_editor_property('relative_location', unreal.Vector(*profile['location']))
    r = profile['rotation']
    root.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))

def relative():
    r = root.get_editor_property('relative_rotation')
    return {'location': xyz(root.get_editor_property('relative_location')), 'rotation': [r.pitch, r.yaw, r.roll]}

def fit(right, direction, left_cm):
    assert direction.length() > .01
    aim = unreal.MathLibrary.find_look_at_rotation(right, right + direction)
    rotation = unreal.Rotator(pitch=0, yaw=aim.yaw-90, roll=-aim.pitch)
    weapon.set_actor_rotation(rotation, False)
    anchor = unreal.Vector(-left_cm, -8, 0)
    world_anchor = unreal.MathLibrary.transform_location(weapon.get_actor_transform(), anchor)
    weapon.set_actor_location(weapon.get_actor_location() + right - world_anchor, False, False)

def views(name):
    mid = (bone('hand_l') + bone('hand_r')) / 2
    # Raised reload frames need wider whole-arm framing, not cropped fingers.
    for label, offset, fov in (('side', unreal.Vector(150, -110, 70), 50),
                               ('front', unreal.Vector(160, 120, 50), 50),
                               ('fp', None, 90)):
        if offset is not None:
            point = mid + offset
            rotation = unreal.MathLibrary.find_look_at_rotation(point, mid)
        else:
            eye = player.get_component_by_class(unreal.CameraComponent)
            point, rotation = eye.get_world_location(), eye.get_world_rotation()
        camera.set_actor_location(point, False, False)
        camera.set_actor_rotation(rotation, False)
        capture.set_editor_property('fov_angle', fov)
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        for _ in range(3):
            capture.capture_scene()
        filename = name + '_' + label + '.png'
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
        report['captures'].append(filename)
        write()

try:
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001')
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.Character):
            actors.destroy_actor(a)
    player = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'), unreal.Vector(0, 0, 100))
    mesh = player.get_component_by_class(unreal.SkeletalMeshComponent)
    mesh.set_anim_instance_class(unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_Allied_Stride_v1'))
    mesh.set_update_animation_in_editor(True)
    weapon = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector())
    root = weapon.static_mesh_component
    root.set_mobility(unreal.ComponentMobility.MOVABLE)
    root.set_static_mesh(unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'))
    root.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    assert weapon.attach_to_component(mesh, 'hand_r', unreal.AttachmentRule.KEEP_RELATIVE,
                                     unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
    light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(80, -80, 220))
    component = light.get_component_by_class(unreal.PointLightComponent)
    component.set_editor_property('intensity', 20)
    component.set_editor_property('attenuation_radius', 700)
    camera = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector())
    capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('capture_every_frame', False)
    capture.set_editor_property('capture_on_movement', False)
    capture.set_editor_property('override_custom_near_clipping_plane', True)
    capture.set_editor_property('custom_near_clipping_plane', 1)
    target = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1), False)
    capture.set_editor_property('texture_target', target)
    keys = ('hand_l', 'hand_r', 'thumb_02_r', 'thumb_03_r', 'index_02_r', 'index_03_r', 'middle_02_l', 'middle_03_l')
    for name, fractions in (('Rifle_Idle', (0,)), ('Rifle_WalkFwdLoop', (0, .25, .5, .75)),
                            ('Rifle_Reload_2', (0, .25, .5, .75, .99))):
        clip = unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/' + name)
        p = STORE / ('Content/RifleAnimsetPro/Animations/InPlace/' + name + '.uasset')
        sources[p] = digest(p)
        for fraction in fractions:
            seconds = clip.get_play_length() * fraction
            mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
            mesh.override_animation_data(clip, False, False, seconds, 1)
            assert abs(mesh.get_position() - seconds) < .001
            unreal.AutomationLibrary.finish_loading_before_screenshot()
            original = {n: xyz(bone(n)) for n in keys}
            right, left = center('r'), center('l')
            stem = name + '_' + str(round(fraction*100))
            sample = {'clip': name, 'fraction': fraction, 'seconds': seconds, 'hands': original,
                      'grasp_distance_cm': (left-right).length(), 'candidates': []}
            mount(inventory['rifle_attachment'])
            if fraction in (0, .25, .5, .99):
                views(stem + '_before')
            for amount in ((.5, 1) if name == 'Rifle_Idle' else (.5,)):
                direction = left-right
                fit(right, direction, amount)
                sample['candidates'].append(dict(name='two_grasp_left' + str(amount), **relative()))
                if fraction in (0, .25, .5, .99):
                    views(stem + '_two_grasp_left' + str(amount).replace('.', '_'))
            if name == 'Rifle_Reload_2':
                fit(right, bone('index_03_r') - bone('index_02_r'), 1)
                sample['candidates'].append(dict(name='right_index_left1', **relative()))
                if fraction in (.25, .5, .99):
                    views(stem + '_right_index_left1')
                mount(inventory['rifle_attachment'])
                anchor = unreal.Vector(-.5, -8, 0)
                world_anchor = unreal.MathLibrary.transform_location(weapon.get_actor_transform(), anchor)
                weapon.set_actor_location(weapon.get_actor_location() + right - world_anchor, False, False)
                sample['candidates'].append(dict(name='right_wrist_left0_5', **relative()))
                if fraction in (0, .25, .5, .99):
                    views(stem + '_right_wrist_left0_5')
            sample['original_hands_unchanged'] = original == {n: xyz(bone(n)) for n in keys}
            assert sample['original_hands_unchanged']
            report['samples'].append(sample)
            write()
    report['status'] = 'unsaved_action_candidates_require_visual_review'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    report['protected_36_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in records)
    report['source_clips_unchanged'] = all(digest(p) == h for p, h in sources.items())
    write()
    unreal.SystemLibrary.quit_editor()
