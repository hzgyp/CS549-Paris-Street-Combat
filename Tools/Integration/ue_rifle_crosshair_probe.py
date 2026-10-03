"""Unsaved rifle/camera convergence and original grasp comparison; no asset saves."""
import hashlib
import json
import math
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
identity = os.environ['CS549_RIFLE_AIM_PROBE_IDENTITY']
assert identity.replace('_', '').isalnum()
OUT = STORE / 'Evidence/CityGameplay20261002/RifleCrosshairV4' / identity
assert not OUT.exists()
OUT.mkdir(parents=True)
inventory = json.loads((ROOT / 'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
deps = json.loads((ROOT / inventory['retained_dependency_inventory']).read_text())
records = inventory['files'] + deps['files'] + inventory['retained_unselected_rejected_trial']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert all((ROOT/e['path']).stat().st_size == e['size_bytes'] and digest(ROOT/e['path']) == e['sha256'] for e in records)
report = {'scope': __doc__, 'status': 'initializing', 'errors': [], 'samples': [], 'captures': []}
sources = {}

def write():
    (OUT/'result.json').write_text(json.dumps(report, indent=2))

def xyz(v):
    return [v.x, v.y, v.z]

def center(side):
    fs = ('middle', 'ring', 'pinky') if side == 'r' else ('index', 'middle', 'ring', 'pinky')
    ns = [f+'_0'+str(s)+'_'+side for f in fs for s in (2, 3)] + ['thumb_02_'+side, 'thumb_03_'+side]
    return sum((mesh.get_socket_location(n) for n in ns), unreal.Vector()) / len(ns)

def orient(origin, target):
    look = unreal.MathLibrary.find_look_at_rotation(origin, target)
    return unreal.Rotator(pitch=0, yaw=look.yaw-90, roll=-look.pitch)

def fit(right, rotation):
    weapon.set_actor_rotation(rotation, False)
    anchor = unreal.MathLibrary.transform_location(weapon.get_actor_transform(), unreal.Vector(-.5, -8, 0))
    weapon.set_actor_location(weapon.get_actor_location()+right-anchor, False, False)

def measure(goal, left, old_support):
    t = weapon.get_actor_transform()
    muzzle = unreal.MathLibrary.transform_location(t, unreal.Vector(0, 83.23, 0))
    direction = unreal.MathLibrary.transform_direction(t, unreal.Vector(0, 1, 0))
    delta = goal-muzzle
    cosine = max(-1, min(1, direction.dot(delta)/delta.length()))
    projection = direction.dot(delta)
    support = unreal.MathLibrary.transform_location(t, support_local)
    return {'muzzle': xyz(muzzle), 'barrel_axis': xyz(direction),
            'target_angle_degrees': math.degrees(math.acos(cosine)),
            'target_ray_miss_cm': (delta-direction*projection).length(),
            'target_in_front': projection > 0,
            'support_anchor_shift_cm': (support-old_support).length(),
            'support_anchor_distance_cm': (support-left).length(),
            'location': xyz(weapon.get_actor_location()),
            'rotation': [weapon.get_actor_rotation().pitch, weapon.get_actor_rotation().yaw, weapon.get_actor_rotation().roll]}

def views(stem):
    mid = (mesh.get_socket_location('hand_l')+mesh.get_socket_location('hand_r'))/2
    for label, offset, fov in (('front', unreal.Vector(160, 120, 50), 50),
                               ('side', unreal.Vector(150, -110, 70), 50), ('fp', None, 90)):
        point = mid+offset if offset is not None else eye.get_world_location()
        rot = unreal.MathLibrary.find_look_at_rotation(point, mid) if offset is not None else eye.get_world_rotation()
        camera.set_actor_location(point, False, False)
        camera.set_actor_rotation(rot, False)
        capture.set_editor_property('fov_angle', fov)
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        for _ in range(3):
            capture.capture_scene()
        name = stem+'_'+label+'.png'
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), name)
        report['captures'].append(name)

try:
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.Character):
            actors.destroy_actor(a)
    player = actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'), unreal.Vector(0, 0, 100))
    mesh = player.get_component_by_class(unreal.SkeletalMeshComponent)
    eye = player.get_component_by_class(unreal.CameraComponent)
    mesh.set_update_animation_in_editor(True)
    weapon = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector())
    weapon.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    weapon.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'))
    weapon.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(80, -80, 220))
    light.get_component_by_class(unreal.PointLightComponent).set_editor_property('intensity', 20)
    light.get_component_by_class(unreal.PointLightComponent).set_editor_property('attenuation_radius', 700)
    camera = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector())
    capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('capture_every_frame', False)
    capture.set_editor_property('override_custom_near_clipping_plane', True)
    capture.set_editor_property('custom_near_clipping_plane', 1)
    target = unreal.RenderingLibrary.create_render_target2d(world, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1), False)
    capture.set_editor_property('texture_target', target)
    support_local = unreal.Vector(-.5, 22.2, 0)
    for clip_name, fractions in (('Rifle_Idle', (0,)), ('Rifle_WalkFwdLoop', (.25, .75))):
        clip = unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/'+clip_name)
        p = STORE/('Content/RifleAnimsetPro/Animations/InPlace/'+clip_name+'.uasset')
        sources[p] = digest(p)
        for fraction in fractions:
            seconds = clip.get_play_length()*fraction
            mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
            mesh.override_animation_data(clip, False, False, seconds, 1)
            assert abs(mesh.get_position()-seconds) < .001
            unreal.AutomationLibrary.finish_loading_before_screenshot()
            original = {n: xyz(mesh.get_socket_location(n)) for n in ('hand_r', 'hand_l', 'thumb_03_r', 'thumb_03_l')}
            right, left = center('r'), center('l')
            held = orient(right, left)
            for pitch in (0, 15, -15):
                eye.set_world_rotation(unreal.Rotator(pitch=pitch, yaw=0, roll=0), False, False)
                for distance in (300, 20000):
                    goal = eye.get_world_location()+eye.get_forward_vector()*distance
                    fit(right, held)
                    old_support = unreal.MathLibrary.transform_location(weapon.get_actor_transform(), support_local)
                    stem = clip_name+'_'+str(round(fraction*100))+'_p'+str(pitch)+'_d'+str(distance)
                    sample = {'clip': clip_name, 'fraction': fraction, 'camera_pitch': pitch, 'camera': xyz(eye.get_world_location()), 'target_distance_cm': distance,
                              'target': xyz(goal), 'before': measure(goal, left, old_support)}
                    if clip_name == 'Rifle_Idle' and distance == 20000:
                        views(stem+'_before')
                    for _ in range(4):
                        fit(right, orient(weapon.get_actor_location(), goal))
                    sample['candidate'] = measure(goal, left, old_support)
                    sample['original_hands_unchanged'] = original == {n: xyz(mesh.get_socket_location(n)) for n in original}
                    assert sample['original_hands_unchanged']
                    if distance == 20000:
                        views(stem+'_aim')
                    report['samples'].append(sample)
                    write()
    report['status'] = 'unsaved_crosshair_candidate_requires_contact_review'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    report['protected_37_unchanged'] = all(digest(ROOT/e['path']) == e['sha256'] for e in records)
    report['source_clips_unchanged'] = all(digest(p) == h for p,h in sources.items())
    write()
    unreal.SystemLibrary.quit_editor()
