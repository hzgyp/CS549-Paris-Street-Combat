"""Bounded existing-rifle grip diagnostic. Probe never saves native packages."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY = os.environ['CS549_GRIP_IDENTITY']
assert IDENTITY.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/WeaponGrip' / IDENTITY
assert not OUT.exists(), 'Preserve occupied evidence'
OUT.mkdir(parents=True)
MAP = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
records = []
for name in ('CITY_NAVIGATION_DRAFT_INVENTORY_20261002', 'RELOAD_DRAFT_SNAPSHOT_20261002'):
    records += json.loads((ROOT / ('Assets/Integration/' + name + '.json')).read_text(encoding='utf-8-sig'))['files']
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
assert all((ROOT / e['path']).stat().st_size == e['size_bytes'] and digest(ROOT / e['path']) == e['sha256'] for e in records)
report = {'scope': 'Unsaved pose/contact probe; no native correction or runtime pass',
          'engine': unreal.SystemLibrary.get_engine_version(), 'samples': [], 'captures': [], 'errors': []}
def save_report():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
def xyz(v):
    return [v.x, v.y, v.z]
def transform(t):
    r = t.rotation.rotator()
    return {'position': xyz(t.translation), 'rotation': [r.pitch, r.yaw, r.roll], 'scale': xyz(t.scale3d)}
def vec(v):
    return unreal.Vector(*v)
def bone(mesh, name):
    return mesh.get_socket_transform(name, unreal.RelativeTransformSpace.RTS_WORLD).translation
def palm(mesh, side):
    knuckles = [bone(mesh, n + '_01_' + side) for n in ('index', 'middle', 'ring', 'pinky')]
    return (bone(mesh, 'hand_' + side) + sum(knuckles, unreal.Vector()) / 4) / 2
camera = None
restorations = []
source_hashes = {}
try:
    sparse = os.environ.get('CS549_GRIP_SPARSE', '0') == '1'
    target_map = '/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001' if sparse else MAP
    current_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if not current_world or current_world.get_path_name() != target_map + '.' + target_map.rsplit('/', 1)[-1]:
        assert unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(target_map)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    roster = actors.get_all_level_actors()
    if sparse:
        for a in roster:
            if isinstance(a, unreal.Character):
                actors.destroy_actor(a)
        cls = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1')
        player = actors.spawn_actor_from_class(cls, unreal.Vector(0, 0, 100))
        player.set_actor_label('PC_City_Player')
        weapon = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, 100))
        weapon.set_actor_label('PC_M1_Appearance_Player')
        weapon.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
        weapon.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'))
        weapon.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        m = player.get_component_by_class(unreal.SkeletalMeshComponent)
        assert weapon.attach_to_component(m, 'hand_r', unreal.AttachmentRule.KEEP_RELATIVE,
                                         unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
        baseline = json.loads((OUT.parent / 'probe_v2/result.json').read_text())
        weapon.static_mesh_component.set_editor_property('relative_location', vec(baseline['relative_location']))
        r = baseline['relative_rotation']
        weapon.static_mesh_component.set_editor_property('relative_rotation', unreal.Rotator(pitch=r[0], yaw=r[1], roll=r[2]))
        light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(80, -80, 220))
        light_component = light.get_component_by_class(unreal.PointLightComponent)
        light_component.set_editor_property('intensity', 20)
        light_component.set_editor_property('attenuation_radius', 700)
        report['scope'] += '; sparse existing stage for contact/light inspection, not city rendering acceptance'
    else:
        player = next(a for a in roster if a.get_actor_label() == 'PC_City_Player')
        weapon = next(a for a in roster if a.get_actor_label() == 'PC_M1_Appearance_Player')
    mesh = player.get_component_by_class(unreal.SkeletalMeshComponent)
    eye = player.get_component_by_class(unreal.CameraComponent)
    mesh.set_update_animation_in_editor(True)
    report['player_mesh'] = mesh.get_skeletal_mesh_asset().get_path_name()
    report['original_weapon_transform'] = transform(weapon.get_actor_transform())
    report['weapon_label'] = weapon.get_actor_label()
    report['camera_transform'] = transform(eye.get_world_transform())
    report['camera_fov'] = eye.get_editor_property('field_of_view')
    # Build rendering resources without modifying the saved map.
    camera = actors.spawn_actor_from_class(unreal.SceneCapture2D, eye.get_world_location())
    capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    for name, value in (('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR),
                        ('capture_every_frame', False), ('capture_on_movement', False),
                        ('override_custom_near_clipping_plane', True), ('custom_near_clipping_plane', 1)):
        capture.set_editor_property(name, value)
    target = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1), False)
    capture.set_editor_property('texture_target', target)
    original_relative = weapon.get_actor_transform()
    original_parent = mesh.get_socket_transform('hand_r', unreal.RelativeTransformSpace.RTS_WORLD)
    # Relative transform from the ordinary scene attachment, before sampling.
    weapon_root = weapon.static_mesh_component
    report['relative_location'] = xyz(weapon_root.get_editor_property('relative_location'))
    rot = weapon_root.get_editor_property('relative_rotation')
    report['relative_rotation'] = [rot.pitch, rot.yaw, rot.roll]
    original_rel_loc = weapon_root.get_editor_property('relative_location')
    original_rel_rot = weapon_root.get_editor_property('relative_rotation')
    candidate_rel_loc = candidate_rel_rot = None
    save_report()
    def shot(name, loc, rotation, fov):
        camera.set_actor_location(loc, False, False)
        camera.set_actor_rotation(rotation, False)
        capture.set_editor_property('fov_angle', fov)
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        for _ in range(3):
            capture.capture_scene()
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), name + '.png')
        report['captures'].append(name + '.png')
        save_report()
    fit_rotation = fit_location = None
    for clip_name, fraction in (('Rifle_Idle', 0), ('Rifle_ShootOnce', .4),
                                ('Rifle_Reload_2', .25), ('Rifle_Reload_2', .5),
                                ('Rifle_Reload_2', .9), ('Rifle_WalkFwdLoop', .25)):
        clip = unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/' + clip_name)
        clip_file = STORE / ('Content/RifleAnimsetPro/Animations/InPlace/' + clip_name + '.uasset')
        source_hashes[clip_file] = digest(clip_file)
        mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
        mesh.override_animation_data(clip, False, False, clip.get_play_length() * fraction, 1)
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        weapon_root.set_editor_property('relative_location', original_rel_loc)
        weapon_root.set_editor_property('relative_rotation', original_rel_rot)
        joints = {n: xyz(bone(mesh, n)) for n in ('hand_r', 'hand_l', 'index_01_r', 'index_02_r',
                  'middle_01_r', 'middle_02_r', 'pinky_01_r', 'index_01_l', 'middle_01_l', 'pinky_01_l')}
        right, left = palm(mesh, 'r'), palm(mesh, 'l')
        name = clip_name + '_' + str(round(fraction * 100))
        report['samples'].append({'name': name, 'time_s': mesh.get_position(), 'joints': joints,
                                 'right_palm': xyz(right), 'left_palm': xyz(left),
                                 'hand_distance_cm': (left - right).length(),
                                 'weapon_transform': transform(weapon.get_actor_transform())})
        shot(name + '_original_fp', eye.get_world_location(), eye.get_world_rotation(), 90)
        mid = (left + right) / 2
        loc = mid + unreal.Vector(90, -70, 35)
        shot(name + '_original_contact', loc, unreal.MathLibrary.find_look_at_rotation(loc, mid), 40)
        correction = os.environ.get('CS549_GRIP_CORRECTION', '0') == '1'
        if correction and clip_name != 'Rifle_Reload_2':
            c = clip.get_editor_property('controller')
            count = unreal.AnimationLibrary.get_num_frames(clip)
            report.setdefault('curl_trials', []).append({'clip': clip_name, 'sampled_key_count': count + 1,
                'left_only': True, 'degrees': [-30, -15, -10], 'source_saved': False})
            for finger in ('index', 'middle', 'ring', 'pinky'):
                for segment, degrees in ((1, -30), (2, -15), (3, -10)):
                    n = finger + '_0' + str(segment) + '_l'
                    keys = [unreal.AnimationLibrary.get_bone_pose_for_time(clip, n, clip.get_play_length() * i / count, False)
                            for i in range(count + 1)]
                    positions = [t.translation for t in keys]
                    rotations = [t.rotation for t in keys]
                    scales = [t.scale3d for t in keys]
                    restorations.append((c, n, positions, rotations, scales))
                    altered = []
                    for t in keys:
                        r = t.rotation.rotator()
                        altered.append(unreal.Rotator(pitch=r.pitch, yaw=r.yaw + degrees, roll=r.roll).quaternion())
                    assert c.set_bone_track_keys(n, positions, altered, scales, False)
            mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
            mesh.override_animation_data(clip, False, False, clip.get_play_length() * fraction, 1)
            unreal.AutomationLibrary.finish_loading_before_screenshot()
        if fit_rotation is None:
            # Experimental grip anchor, not approved model measurements yet.
            forward = left - right
            aim = unreal.MathLibrary.find_look_at_rotation(right, left)
            # Mesh long axis is +Y; orient +Y along the palm-to-palm direction.
            fit_rotation = unreal.Rotator(pitch=0, yaw=aim.yaw - 90, roll=-aim.pitch)
            anchor = unreal.Vector(0, 7, -7) if correction else unreal.Vector(0, -8, -3)
            weapon.set_actor_rotation(fit_rotation, False)
            world_anchor = unreal.MathLibrary.transform_location(weapon.get_actor_transform(), anchor)
            fit_location = weapon.get_actor_location() + right - world_anchor
            weapon.set_actor_location(fit_location, False, False)
            report['experimental_idle_candidate'] = transform(weapon.get_actor_transform())
            report['experimental_relative_location'] = xyz(weapon_root.get_editor_property('relative_location'))
            r = weapon_root.get_editor_property('relative_rotation')
            report['experimental_relative_rotation'] = [r.pitch, r.yaw, r.roll]
            candidate_rel_loc = weapon_root.get_editor_property('relative_location')
            candidate_rel_rot = weapon_root.get_editor_property('relative_rotation')
        weapon_root.set_editor_property('relative_location', candidate_rel_loc)
        weapon_root.set_editor_property('relative_rotation', candidate_rel_rot)
        shot(name + '_candidate_fp', eye.get_world_location(), eye.get_world_rotation(), 90)
        shot(name + '_candidate_contact', loc, unreal.MathLibrary.find_look_at_rotation(loc, mid), 40)
        if sparse and clip_name == 'Rifle_Idle' and not correction:
            for dz in (3, 6):
                weapon.set_actor_location(weapon.get_actor_location() + unreal.Vector(0, 0, dz), False, False)
                report['idle_raise_' + str(dz)] = {
                    'relative_location': xyz(weapon_root.get_editor_property('relative_location')),
                    'relative_rotation': report['experimental_relative_rotation']}
                shot(name + '_raise_' + str(dz) + '_fp', eye.get_world_location(), eye.get_world_rotation(), 90)
                shot(name + '_raise_' + str(dz) + '_contact', loc, unreal.MathLibrary.find_look_at_rotation(loc, mid), 40)
                weapon_root.set_editor_property('relative_location', candidate_rel_loc)
            report['animation_python_api'] = {}
            for n in ('get_controller', 'get_editor_property'):
                report['animation_python_api'][n] = hasattr(clip, n)
            try:
                c = clip.get_editor_property('controller')
                report['controller'] = str(c)
                report['controller_methods'] = [n for n in dir(c) if 'bone' in n or 'bracket' in n]
            except Exception as ex:
                report['controller_read_limitation'] = str(ex)
            report['finger_local_pose'] = {}
            for n in ('index_01_l', 'index_02_l', 'index_03_l', 'middle_01_l', 'middle_02_l', 'middle_03_l',
                      'index_01_r', 'index_02_r', 'index_03_r'):
                report['finger_local_pose'][n] = transform(unreal.AnimationLibrary.get_bone_pose_for_time(clip, n, 0, False))
        save_report()
    report['status'] = 'probe_complete_pending_contact_review'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    for c, n, positions, rotations, scales in reversed(restorations):
        try:
            assert c.set_bone_track_keys(n, positions, rotations, scales, False)
        except Exception:
            report['errors'].append('Memory-key restoration: ' + traceback.format_exc())
    report['source_clip_bytes_unchanged'] = all(digest(p) == h for p, h in source_hashes.items())
    report['protected_35_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in records)
    save_report()
    if report['errors']:
        unreal.log_error(report['errors'][-1])
    unreal.SystemLibrary.quit_editor()
