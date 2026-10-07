"""Capture original evaluated NPC grip; no asset author/save/pose correction."""
import os
import sys
import time
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).parent))
from common import *

IDENTITY = os.environ['CS549_NPC_GRIP_CAPTURE_ID']
assert IDENTITY.replace('_', '').isalnum()
OUT = BASE / IDENTITY
assert not OUT.exists()
OUT.mkdir(parents=True)
write(OUT / 'source.json', {'sha256': sha(Path(__file__)), 'identity': IDENTITY})
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
r = {'status': 'starting', 'errors': [], 'pid': os.getpid(), 'map_saved': False,
     'pose_changed': False, 'npc_ai_changed': False, 'captures': [], 'pairs': {},
     'engine': unreal.SystemLibrary.get_engine_version(),
     'german_formal_equipment_selected': False, 'guards_before': check()}
callback = None
start = time.monotonic()
ready = None
ending = None
world = None
capture = target = None
subjects = {}
index = 0
requested = None
busy = False
views = [('front', 'front', 78), ('right', 'right', 78), ('top', 'top', 78),
         ('left', 'left', 78), ('context', 'right', 155),
         ('right_grip', 'right', 28), ('left_support', 'left', 30)]
queue = [(faction, name, axis, width) for faction in ('allied', 'german') for name, axis, width in views]

def xyz(v): return [v.x, v.y, v.z]
def transform(t):
    return {'t': xyz(t.translation), 'q': [t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w], 's': xyz(t.scale3d)}
def path(value): return value.get_path_name() if value else None
def save(): write(OUT / 'result.json', r)

def snapshot(soldier):
    mesh = soldier.mesh
    gun = soldier.get_editor_property('WeaponAppearance')
    assert gun and gun.get_editor_property('GripMesh') == mesh
    assert gun.get_editor_property('Combatant') == soldier
    component = gun.get_component_by_class(unreal.StaticMeshComponent)
    bones = [str(mesh.get_bone_name(i)) for i in range(mesh.get_num_bones())]
    return {'actor': soldier.get_actor_label(), 'class': path(soldier.get_class()),
            'team': int(soldier.get_editor_property('TeamId')),
            'action': str(soldier.get_editor_property('ActionState')),
            'skeletal_mesh': path(mesh.get_skeletal_mesh_asset()),
            'skeleton': path(mesh.get_skeletal_mesh_asset().get_editor_property('skeleton')),
            'anim_class': path(mesh.get_anim_instance().get_class()),
            'materials': [path(mesh.get_material(i)) for i in range(mesh.get_num_materials())],
            'bone_world': {name: transform(mesh.get_socket_transform(name, unreal.RelativeTransformSpace.RTS_WORLD)) for name in bones},
            'mesh_world': transform(mesh.get_world_transform()),
            'gun_class': path(gun.get_class()), 'gun_mesh': path(component.get_editor_property('static_mesh')),
            'gun_materials': [path(component.get_material(i)) for i in range(component.get_num_materials())],
            'gun_world': transform(component.get_world_transform()),
            'gun_parent': path(gun.get_attach_parent_actor()),
            'gun_socket': str(component.get_attach_socket_name()),
            'collision': str(component.get_collision_enabled())}

def finish(error=None):
    global ending
    if ending is not None: return
    if error: r['errors'].append(error)
    if world:
        unreal.GameplayStatics.set_game_paused(world, False)
        unreal.GameplayStatics.set_global_time_dilation(world, 1)
    try: r['guards_after'] = check()
    except Exception: r['errors'].append(traceback.format_exc())
    r['status'] = 'failed_preserved' if r['errors'] else 'captured_baseline_requires_image_and_user_review'
    save()
    if world: levels.editor_request_end_play()
    ending = time.monotonic()

def tick(delta):
    global world, callback, ready, capture, target, index, requested, busy
    if busy: return
    busy = True
    try:
        if ending is not None:
            if time.monotonic() - ending > 3:
                unreal.unregister_slate_post_tick_callback(callback)
                unreal.SystemLibrary.quit_editor()
            return
        assert time.monotonic() - start < 240, 'Capture deadline'
        world = editor.get_game_world()
        player = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
        if not player: return
        if ready is None:
            for faction, label in (('allied', 'PC_City_Ally1'), ('german', 'PC_City_Enemy1')):
                subjects[faction] = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character) if a.get_actor_label() == label)
            capture = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.SceneCapture2D) if a.get_actor_label() == 'PC_NPCGripBaselineCapture').get_component_by_class(unreal.SceneCaptureComponent2D)
            target = unreal.RenderingLibrary.create_render_target2d(world, 1600, 1000,
                unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.12,.14,.17,1), False, False)
            capture.set_editor_property('texture_target', target)
            capture.set_editor_property('primitive_render_mode', unreal.SceneCapturePrimitiveRenderMode.PRM_USE_SHOW_ONLY_LIST)
            capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
            capture.set_editor_property('projection_type', unreal.CameraProjectionMode.ORTHOGRAPHIC)
            capture.set_editor_property('capture_every_frame', False)
            capture.set_editor_property('capture_on_movement', False)
            capture.set_editor_property('show_flag_settings', [unreal.EngineShowFlagsSetting(show_flag_name=name, enabled=False)
                for name in ('Fog','Atmosphere','Bloom','DepthOfField','MotionBlur')])
            ready = time.monotonic()
            return
        if time.monotonic() - ready < 15: return
        if not r['pairs']:
            for faction, soldier in subjects.items():
                assert str(soldier.get_editor_property('ActionState')) == 'Ready'
                assert soldier.get_velocity().length() < .1
                assert 'Stride' in soldier.mesh.get_anim_instance().get_class().get_name()
                soldier.mesh.set_editor_property('pause_anims', True)
                soldier.character_movement.stop_movement_immediately()
                r['pairs'][faction] = snapshot(soldier)
            assert r['pairs']['allied']['team'] == 0 and r['pairs']['german']['team'] == 1
            assert 'RifleAttachmentV3' in r['pairs']['allied']['gun_class']
            assert 'GermanRifleAttachmentV2' in r['pairs']['german']['gun_class']
            # Unlike pause_anims alone, pause the world to preserve attachment
            # and movement clocks together. No manually rewritten pose/gun fit.
            assert unreal.GameplayStatics.set_game_paused(world, True)
            r['capture_pause'] = 'whole native world; not animation-only freeze'
            save()
        if index >= len(queue): finish(); return
        if index == 1 and not (OUT/'early_acceptance.json').is_file():
            return  # Lead inspects the first real image before the remaining views.
        faction, name, axis, width = queue[index]
        soldier = subjects[faction]
        gun = soldier.get_editor_property('WeaponAppearance')
        if requested is None:
            rh, lh = soldier.mesh.get_socket_location('hand_r'), soldier.mesh.get_socket_location('hand_l')
            center = (rh+lh)/2
            if name == 'context': center = (center + soldier.mesh.get_socket_location('spine_03')) / 2
            if name == 'right_grip': center = (rh + soldier.mesh.get_socket_location('index_02_r')) / 2
            if name == 'left_support': center = (lh + soldier.mesh.get_socket_location('thumb_02_l')) / 2
            direction = {'front': soldier.get_actor_forward_vector(), 'right': soldier.get_actor_right_vector(),
                         'left': -soldier.get_actor_right_vector(), 'top': unreal.Vector(0,0,1)}[axis]
            eye = center + direction*250
            capture.set_world_location(eye, False, False)
            rotation = unreal.MathLibrary.find_look_at_rotation(eye, center)
            if axis == 'top': rotation = unreal.Rotator(pitch=-90, yaw=soldier.get_actor_rotation().yaw, roll=0)
            capture.set_world_rotation(rotation, False, False)
            capture.set_editor_property('ortho_width', width)
            capture.clear_show_only_components()
            capture.set_editor_property('show_only_actors', [soldier, gun])
            capture.capture_scene()
            requested = time.monotonic()
            r['captures'].append({'faction': faction, 'view': name, 'axis': axis, 'file': faction+'_'+name+'.png',
                'ortho_width_cm': width, 'eye_cm': xyz(eye), 'target_cm': xyz(center),
                'rotation': [rotation.pitch,rotation.yaw,rotation.roll], 'binding': snapshot(soldier)})
            save()
            return
        if time.monotonic() - requested < 1.5: return
        filename = faction+'_'+name+'.png'
        unreal.RenderingLibrary.export_render_target(world, target, OUT.as_posix(), filename)
        assert (OUT/filename).is_file() and (OUT/filename).stat().st_size > 15000, 'Missing/readability capture gate'
        latest = snapshot(soldier)
        baseline = r['pairs'][faction]
        drift = (unreal.Vector(*latest['gun_world']['t']) - unreal.Vector(*baseline['gun_world']['t'])).length()
        r['captures'][-1]['gun_position_drift_cm'] = drift
        save()
        assert drift < .01, drift
        for bone in ('hand_r','hand_l','index_03_r','thumb_03_l'):
            assert (unreal.Vector(*latest['bone_world'][bone]['t']) - unreal.Vector(*baseline['bone_world'][bone]['t'])).length() < .01, bone
        index += 1
        requested = None
    except Exception: finish(traceback.format_exc())
    finally: busy = False

try:
    by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    soldiers = {key: by_label[label] for key,label in (('allied','PC_City_Ally1'),('german','PC_City_Enemy1'))}
    r['saved_equipment'] = {key: path(a.get_editor_property('WeaponAppearance')) for key,a in soldiers.items()}
    assert soldiers['allied'].get_editor_property('WeaponAppearance')
    soldier = soldiers['german']
    assert soldier.get_editor_property('WeaponAppearance') is None, 'Preserve unexpected already-equipped German'
    cls = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV2')
    gun = actors.spawn_actor_from_class(cls, soldier.get_actor_location(), unreal.Rotator())
    gun.set_actor_label('PC_NPCGripBaselineGermanGun')
    gun.set_editor_property('GripMesh', soldier.mesh)
    gun.set_editor_property('Combatant', soldier)
    gun.set_owner(soldier)
    assert gun.attach_to_component(soldier.mesh, 'hand_r', unreal.AttachmentRule.KEEP_RELATIVE,
        unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
    soldier.set_editor_property('WeaponAppearance', gun)
    cap = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(), unreal.Rotator())
    cap.set_actor_label('PC_NPCGripBaselineCapture')
    # Unsaved shadowless fill for material/contact readability, never a runtime
    # lighting change. Native material graphs and source mesh bytes remain exact.
    for pitch, yaw in ((-25,45),(-25,-135),(-20,135),(-20,-45)):
        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,300), unreal.Rotator(pitch=pitch,yaw=yaw))
        light.set_actor_label('PC_NPCGripBaselineFill')
        component = light.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_intensity(6)
        component.set_cast_shadows(False)
    save()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    callback = unreal.register_slate_post_tick_callback(tick)
    levels.editor_request_begin_play()
except Exception:
    r['status'] = 'failed_startup'; r['errors'].append(traceback.format_exc()); save()
    unreal.SystemLibrary.quit_editor()
