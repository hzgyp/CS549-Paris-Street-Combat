"""Unsaved rigid gun alignment, original mesh/rig/pose/camera unchanged."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ['CS549_RIFLE_TRANSFORM_IDENTITY']
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/WeaponTransformV2' / IDENTITY
assert not OUT.exists()
OUT.mkdir(parents=True)
records = []
for n in ('CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002', 'RELOAD_DRAFT_SNAPSHOT_20261002'):
    records += json.loads((ROOT / ('Assets/Integration/' + n + '.json')).read_text())['files']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert all((ROOT / e['path']).stat().st_size == e['size_bytes'] and digest(ROOT / e['path']) == e['sha256'] for e in records)
report = {'scope': __doc__, 'status': 'initializing', 'errors': [], 'candidates': [], 'captures': [], 'samples': []}
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

def relative():
    r = root.get_editor_property('relative_rotation')
    return {'location': xyz(root.get_editor_property('relative_location')), 'rotation': [r.pitch, r.yaw, r.roll]}

def place(c):
    root.set_editor_property('relative_location', unreal.Vector(*c['location']))
    r = c['rotation']
    root.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))

def shot(name, position, rotation, fov):
    camera.set_actor_location(position, False, False)
    camera.set_actor_rotation(rotation, False)
    capture.set_editor_property('fov_angle', fov)
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    for _ in range(3):
        capture.capture_scene()
    unreal.RenderingLibrary.export_render_target(world, target, str(OUT), name + '.png')
    report['captures'].append(name + '.png')
    write()

def views(name):
    mid = (bone('hand_l') + bone('hand_r')) / 2
    for label, offset in (('side', unreal.Vector(90, -70, 35)), ('front', unreal.Vector(100, 80, 20))):
        point = mid + offset
        shot(name + '_' + label, point, unreal.MathLibrary.find_look_at_rotation(point, mid), 40)
    eye = player.get_component_by_class(unreal.CameraComponent)
    shot(name + '_fp', eye.get_world_location(), eye.get_world_rotation(), 90)

try:
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    stage = '/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001'
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if world.get_path_name() != stage + '.P2_CharacterLifecycle_20261001':
        assert levels.load_level(stage)
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
    light_component = light.get_component_by_class(unreal.PointLightComponent)
    light_component.set_editor_property('intensity', 20)
    light_component.set_editor_property('attenuation_radius', 700)
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
    old = json.loads((STORE / 'Evidence/CityGameplay20261002/WeaponGrip/probe_v2/result.json').read_text())
    clip = unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle')
    idle_file = STORE / 'Content/RifleAnimsetPro/Animations/InPlace/Rifle_Idle.uasset'
    sources[idle_file] = digest(idle_file)
    mesh.override_animation_data(clip, False, False, 0, 1)
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    report['original_grasp_measurements'] = {n: xyz(bone(n)) for side in ('l', 'r') for f in ('hand', 'index_02', 'index_03', 'middle_02', 'middle_03', 'ring_02', 'ring_03', 'pinky_02', 'pinky_03', 'thumb_02', 'thumb_03') for n in (f + '_' + side,)}
    right, left = center('r'), center('l')
    report['estimated_grasp_centers_cm'] = {'right': xyz(right), 'left': xyz(left), 'distance': (left-right).length()}
    report['candidates'] = [dict(name='original_setup', location=old['relative_location'], rotation=old['relative_rotation']),
                            dict(name='previous_mount_original_pose', location=old['experimental_relative_location'], rotation=old['experimental_relative_rotation'])]
    aim = unreal.MathLibrary.find_look_at_rotation(right, left)
    fit_rotation = unreal.Rotator(pitch=0, yaw=aim.yaw-90, roll=-aim.pitch)
    for z in (0, 3, -3):
        weapon.set_actor_rotation(fit_rotation, False)
        anchor = unreal.Vector(0, -8, z)
        world_anchor = unreal.MathLibrary.transform_location(weapon.get_actor_transform(), anchor)
        weapon.set_actor_location(weapon.get_actor_location() + right - world_anchor, False, False)
        c = relative()
        c.update(name='hollow_fit_' + ('zero' if z == 0 else 'lower3' if z == 3 else 'raise3'),
                 experimental_rifle_anchor=xyz(anchor))
        report['candidates'].append(c)
    phase_only = os.environ.get('CS549_RIFLE_TRANSFORM_PHASES') == '1'
    if not phase_only:
        for c in report['candidates']:
            place(c)
            views('idle_' + c['name'])
    # Same original hand transforms must survive every rigid candidate exactly.
    current = {n: xyz(bone(n)) for n in report['original_grasp_measurements']}
    report['original_hand_transforms_unchanged'] = current == report['original_grasp_measurements']
    assert report['original_hand_transforms_unchanged']
    if phase_only:
        fit = json.loads((OUT.parent / 'fit_v1/result.json').read_text())
        assert not fit['errors'] and fit['original_hand_transforms_unchanged']
        selected = next(c for c in fit['candidates'] if c['name'] == 'hollow_fit_zero')
        report['selected'] = selected
        place(selected)
        for name, seconds in (('Rifle_Idle', 0), ('Rifle_ShootOnce', .4),
                              ('Rifle_WalkFwdLoop', .25), ('Rifle_Reload_2', .25),
                              ('Rifle_Reload_2', .5), ('Rifle_Reload_2', .9)):
            asset = unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/' + name)
            p = STORE / ('Content/RifleAnimsetPro/Animations/InPlace/' + name + '.uasset')
            sources[p] = digest(p)
            # Reinitialize single-node playback. Reusing its instance left phases_v1 stale.
            mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
            mesh.override_animation_data(asset, False, False, seconds, 1)
            assert abs(mesh.get_position() - seconds) < .001
            unreal.AutomationLibrary.finish_loading_before_screenshot()
            before = {n: xyz(bone(n)) for n in report['original_grasp_measurements']}
            place(selected)
            views(name + '_' + str(seconds).replace('.', '_'))
            unchanged = before == {n: xyz(bone(n)) for n in before}
            assert unchanged, 'Rigid gun placement must never change source fingers'
            report['samples'].append({'clip': name, 'time': seconds, 'original_hand_transforms_unchanged': unchanged,
                                      'source_hand_positions': before})
        values = [unreal.Vector(*s['source_hand_positions']['hand_l']) for s in report['samples']]
        report['phase_pose_variation_cm'] = max((v - values[0]).length() for v in values)
        assert report['phase_pose_variation_cm'] > 1, 'Reject stale editor pose sampling'
    report['status'] = 'unsaved_rigid_candidates_require_contact_review'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    report['protected_36_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in records)
    report['source_clip_bytes_unchanged'] = all(digest(p) == h for p, h in sources.items())
    write()
    unreal.SystemLibrary.quit_editor()
