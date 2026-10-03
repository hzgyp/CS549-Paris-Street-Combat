"""Bridge-disabled actual-city combat/HUD regression; transient tests, no saves."""
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
EVIDENCE = STORE / 'Evidence/CityGameplay20261002'
IDENTITY = os.environ.get('CS549_COMBAT_PIE_IDENTITY', 'combat_pie_v1')
assert IDENTITY.replace('_', '').isalnum()
OUT = EVIDENCE / 'Runtime' / IDENTITY
assert not OUT.exists()
OUT.mkdir(parents=True)
source = json.loads((EVIDENCE / 'Setup/hud_author_v6.json').read_text())
assert source['status'] == 'saved_actual_city_fire_and_umg_not_runtime_acceptance'
fixed = json.loads((EVIDENCE / 'Setup/shot_scalar_fix_v2.json').read_text())
assert fixed['status'] == 'saved_explicit_uniform_scale_fix_not_runtime_acceptance'
old = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
checkpoint_name = ('CITY_PACKAGE_DRAFT_INVENTORY_20261002.json'
                   if (ROOT / 'Assets/Integration/CITY_PACKAGE_DRAFT_INVENTORY_20261002.json').exists()
                   else 'CITY_COMBAT_DRAFT_INVENTORY_20261002.json')
checkpoint_name = os.environ.get('CS549_CITY_NATIVE_CHECKPOINT', checkpoint_name)
assert checkpoint_name in ('CITY_NAVIGATION_DRAFT_INVENTORY_20261002.json',
                           'CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json',
                           'CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json',
                           'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json',
                           'CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json',
                           'CITY_PACKAGE_DRAFT_INVENTORY_20261002.json',
                           'CITY_COMBAT_DRAFT_INVENTORY_20261002.json')
current = json.loads((ROOT / 'Assets/Integration' / checkpoint_name).read_text())
aim_preview = os.environ.get('CS549_PLAYER_AIM_PREVIEW') == '1'
arms_preview = os.environ.get('CS549_CONTINUOUS_ARMS_MUZZLE_PREVIEW') == '1'
native_preview = os.environ.get('CS549_CONTINUOUS_ARMS_NATIVE_TEST') == '1'
arms_trial = near_blocker = None
assert not (aim_preview and arms_preview), 'Use one transient diagnostic mechanism'
assert not (native_preview and (aim_preview or arms_preview)), 'Native test cannot use Python display adaptation'
if native_preview:
    sys.path.insert(0,str(Path(__file__).parent))
    from ue_continuous_arms_native_runtime import NativeTrial,native_record,PACKAGE as native_package
if arms_preview:
    assert checkpoint_name == 'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json'
    sys.path.insert(0,str(Path(__file__).parent))
    from ue_continuous_arms_runtime_trial import RuntimeTrial,trial_records as arms_records
if os.environ.get('CS549_FIRST_PERSON_VIEW_PREVIEW') == '1':
    raise RuntimeError('FP001 is archived after visual rejection; its preview is retired')
if aim_preview:
    assert checkpoint_name == 'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json'
    sys.path.insert(0, str(Path(__file__).parent))
    from ue_player_aim_runtime_preview import trial_records, stage
guarded = {f['path']: f['sha256'] for f in old['files'] + current['files'] + current.get('retained_unselected_rejected_trial', [])}
if aim_preview:
    guarded.update({f['path']:f['sha256'] for f in trial_records()})
if arms_preview:
    guarded.update({f['path']:f['sha256'] for f in arms_records()})
if native_preview:
    f=native_record();guarded[f['path']]=f['sha256']
assert guarded[fixed['saved_file']['path']] == fixed['saved_file']['sha256'], 'Changed shot graph needs a documented new regression checkpoint'
for file in (STORE / 'Content/WW2City/Maps').glob('*.umap'):
    guarded[file.relative_to(ROOT).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in guarded.items())
report = {'scope': 'Actual-city Blueprint combat and UMG, no physical input/AI/mission/FPS/package acceptance',
          'native_checkpoint': checkpoint_name,
          'engine': unreal.SystemLibrary.get_engine_version(), 'status': 'initializing',
          'cases': [], 'errors': [], 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
start = time.monotonic()
phase = 'waiting'
phase_time = 0
world = player = controller = enemy = ally = weapon = widget = None
callback = None
in_tick = False
index = 0
origin_location = None
widget_class = unreal.load_class(None, '/Game/ParisCombat/UI/CityGameplayV1/WBP_PCParisStatusV1.WBP_PCParisStatusV1_C')
assert widget_class


def checkpoint():
    (OUT / 'combat.json').write_text(json.dumps(report, indent=2))


def prop(a, key):
    return a.get_editor_property(key)


def state(a):
    return {key: str(prop(a, key)) for key in ('Health', 'IsDead', 'ActionState', 'LoadedAmmo',
        'ReserveAmmo', 'RestoreGeneration', 'ShotGeneration', 'ShotSequence', 'ShotOutcome', 'ReloadCommitCount')}


def xyz(v):
    return [v.x, v.y, v.z]


def aim(a):
    cam = player.get_component_by_class(unreal.CameraComponent)
    point = a.get_actor_location() + unreal.Vector(0, 0, 40)
    rotation = unreal.MathLibrary.find_look_at_rotation(cam.get_world_location(), point)
    controller.set_control_rotation(rotation)


def trace_debug():
    cam = player.get_component_by_class(unreal.CameraComponent)
    o = cam.get_world_location()
    d = cam.get_forward_vector()
    muzzle = unreal.MathLibrary.transform_location(weapon.get_actor_transform(), unreal.Vector(0, 83.23, 0))
    hit = unreal.SystemLibrary.line_trace_single(world, o, o + d * 20000,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [player], unreal.DrawDebugTrace.NONE, True)
    def hit_info(h):
        if not h:
            return None
        t = h.to_tuple()
        return {'blocking': bool(t[0]), 'point': xyz(t[5]), 'actor': t[9].get_name() if t[9] else None}
    aim_point = hit.to_tuple()[5] if hit else o + d * 20000
    delta = aim_point - muzzle
    normal = delta / max(delta.length(), .0001)
    args = (unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [player], unreal.DrawDebugTrace.NONE, True)
    original = unreal.SystemLibrary.line_trace_single(world, muzzle, aim_point, *args)
    extended = unreal.SystemLibrary.line_trace_single(world, muzzle, aim_point + normal * 2, *args)
    corridor = unreal.SystemLibrary.sphere_trace_single(world, weapon.get_actor_location(), muzzle, 2, *args)
    return {'camera': xyz(o), 'direction': xyz(d), 'grip': xyz(weapon.get_actor_location()),
            'muzzle': xyz(muzzle), 'camera_hit': hit_info(hit), 'python_bullet_original': hit_info(original),
            'python_bullet_extended': hit_info(extended), 'python_corridor': hit_info(corridor)}


def shot(name, expect, count=1, invoke='PC_PlayerFire', args=()):
    before, target_before, ally_before = state(player), state(enemy), state(ally)
    debug = trace_debug()
    for _ in range(count):
        player.call_method(invoke, args=args)
    after, target_after, ally_after = state(player), state(enemy), state(ally)
    case = {'name': name, 'before': before, 'after': after, 'target_before': target_before,
            'target_after': target_after, 'ally_before': ally_before, 'ally_after': ally_after, 'trace': debug}
    expect(case)
    report['cases'].append(case)
    checkpoint()


def check(c, name, condition):
    c.setdefault('assertions', {})[name] = bool(condition)


def consumed(c):
    return int(c['before']['LoadedAmmo']) - int(c['after']['LoadedAmmo'])


def free(c):
    check(c, 'one_round', consumed(c) == 1)
    check(c, 'one_sequence', int(c['after']['ShotSequence']) - int(c['before']['ShotSequence']) == 1)
    check(c, 'hostile_35_clamped', float(c['target_before']['Health']) - float(c['target_after']['Health']) == min(35, float(c['target_before']['Health'])))
    check(c, 'hostile_result', c['after']['ShotOutcome'] == 'Hostile hit')
    check(c, 'ally_unchanged', c['ally_before']['Health'] == c['ally_after']['Health'])


def reject(c):
    check(c, 'no_round', consumed(c) == 0)
    check(c, 'no_sequence', c['before']['ShotSequence'] == c['after']['ShotSequence'])
    check(c, 'no_damage', c['target_before']['Health'] == c['target_after']['Health'])
    check(c, 'rejected_result', c['after']['ShotOutcome'] == 'Rejected')


def blocked(c):
    check(c, 'one_round', consumed(c) == 1)
    check(c, 'no_hostile_damage', c['target_before']['Health'] == c['target_after']['Health'])
    check(c, 'no_friendly_damage', c['ally_before']['Health'] == c['ally_after']['Health'])
    check(c, 'blocked_result', c['after']['ShotOutcome'] in ('World blocked', 'Barrel blocked', 'Muzzle blocked', 'Friendly blocked'))


def capture(name):
    unreal.SystemLibrary.execute_console_command(world,
        'Shot SHOWUI -nosuffix filename="' + (OUT / (name + '.png')).as_posix() + '"', controller)


def advance(p):
    global phase, phase_time
    phase = p
    phase_time = unreal.GameplayStatics.get_time_seconds(world) if world else 0


def finish(error=None):
    if error:
        report['errors'].append(error)
    report['status'] = 'failed' if error else 'completed_requires_assertion_review'
    levels.editor_request_end_play()
    advance('ending')
    checkpoint()


def tick(delta):
    global in_tick, world, player, controller, enemy, ally, weapon, widget, origin_location, index,arms_trial,near_blocker
    if in_tick:
        return
    in_tick = True
    try:
        if phase == 'ending':
            if not levels.is_in_play_in_editor():
                unreal.unregister_slate_post_tick_callback(callback)
                report['native_bytes_unchanged'] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in guarded.items())
                final = report.get('final_state', {})
                report['ammo_conserved'] = bool(final) and int(final['LoadedAmmo']) + int(final['ReserveAmmo']) + int(final['ShotSequence']) == 18
                report['all_assertions_passed'] = bool(report['cases']) and not report['errors'] and all(all(c.get('assertions', {}).values()) for c in report['cases']) and report.get('reload_conserved', False) and report['ammo_conserved'] and report['native_bytes_unchanged'] and report.get('busy_positive_tested', False)
                report['captures'] = [{'file': p.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                    for p in OUT.glob('*.png')]
                checkpoint()
                unreal.SystemLibrary.quit_editor()
            return
        if time.monotonic() - start > 240:
            finish('Bounded PIE timeout')
            return
        if arms_trial and not native_preview:
            arms_trial.update()
        if phase == 'waiting':
            world = editor.get_game_world()
            player = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
            if not player:
                return
            if aim_preview and not report.get('transient_aim_variant'):
                report['transient_aim_variant'] = stage(world, player)
            controller = unreal.GameplayStatics.get_player_controller(world, 0)
            roster = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character)
                      if a.get_class().get_name().startswith('BP_PCParis')]
            assert len(roster) == 6 and player.get_class().get_name() == 'BP_PCParisPlayerV1_C'
            enemy = min((a for a in roster if prop(a, 'TeamId') == 1), key=lambda a: (a.get_actor_location()-player.get_actor_location()).length())
            ally = next(a for a in roster if a != player and prop(a, 'TeamId') == 0)
            weapon = prop(player, 'WeaponAppearance')
            assert weapon
            report['fresh_runtime'] = [{'class': a.get_class().get_path_name(), 'team': prop(a, 'TeamId'),
                'mesh': a.get_component_by_class(unreal.SkeletalMeshComponent).get_skeletal_mesh_asset().get_path_name(),
                'visibility': str(a.get_component_by_class(unreal.CapsuleComponent).get_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY))}
                for a in roster]
            cam = player.get_component_by_class(unreal.CameraComponent)
            report['camera_local'] = xyz(cam.get_editor_property('relative_location'))
            assert report['camera_local'] == [25, 0, 60]
            if checkpoint_name == 'CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json':
                report['allied_grip_classes'] = [a.get_component_by_class(unreal.SkeletalMeshComponent).get_anim_instance().get_class().get_path_name()
                    for a in roster if prop(a, 'TeamId') == 0]
                assert len(report['allied_grip_classes']) == 3
                assert all('ABP_PC_AlliedGripV1_C' in c for c in report['allied_grip_classes'])
                report['grip_relative_location'] = xyz(weapon.static_mesh_component.get_editor_property('relative_location'))
                assert (unreal.Vector(*report['grip_relative_location']) - unreal.Vector(-13.7277957642, 2.6728878974, 1.7171858011)).length() < .001
            if checkpoint_name == 'CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json':
                report['original_allied_classes'] = [a.get_component_by_class(unreal.SkeletalMeshComponent).get_anim_instance().get_class().get_path_name()
                    for a in roster if prop(a, 'TeamId') == 0]
                assert len(report['original_allied_classes']) == 3
                assert all('ABP_PC_Allied_Stride_v1_C' in c for c in report['original_allied_classes'])
                report['rigid_attachments'] = []
                for a in roster:
                    if prop(a, 'TeamId') != 0:
                        continue
                    w = prop(a, 'WeaponAppearance')
                    assert w and w.get_attach_parent_actor() == a
                    component = w.static_mesh_component
                    loc = xyz(component.get_editor_property('relative_location'))
                    rot = component.get_editor_property('relative_rotation')
                    angles = [rot.pitch, rot.yaw, rot.roll]
                    assert (unreal.Vector(*loc) - unreal.Vector(*current['rifle_attachment']['location'])).length() < .001
                    assert all(abs(x-y) < .001 for x, y in zip(angles, current['rifle_attachment']['rotation']))
                    assert component.get_editor_property('relative_scale3d') == unreal.Vector(1, 1, 1)
                    report['rigid_attachments'].append({'actor': a.get_name(), 'location': loc, 'rotation': angles})
            if checkpoint_name in ('CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json','CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json'):
                report['action_attachments'] = []
                for a in roster:
                    if prop(a, 'TeamId') != 0:
                        continue
                    mesh = a.get_component_by_class(unreal.SkeletalMeshComponent)
                    expected_anim = 'ABP_PC_PlayerRigidAimV4_C' if aim_preview and a == player else 'ABP_PC_Allied_Stride_v1_C'
                    assert expected_anim in mesh.get_anim_instance().get_class().get_path_name()
                    w = prop(a, 'WeaponAppearance')
                    if native_preview and a == player and checkpoint_name == 'CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json':
                        native_actors=[n for n in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if n.get_class().get_name() == 'BP_PC_ContinuousArmsNativeV1_C']
                        assert len(native_actors)==1
                        w=prop(native_actors[0],'WorldGun')
                    expected_weapon = 'BP_PC_PlayerRifleAimV4_C' if aim_preview and a == player else 'BP_PC_RifleAttachmentV3_C'
                    assert w.get_class().get_name() == expected_weapon
                    grip = prop(w, 'GripMesh')
                    assert w.get_attach_parent_actor() == grip.get_owner() and w.get_owner() == a
                    assert prop(w, 'Combatant') == a
                    assert grip == mesh
                    assert abs(prop(w, 'LeftShiftCm') - .5) < .001
                    assert w.static_mesh_component.get_editor_property('relative_scale3d') == unreal.Vector(1, 1, 1)
                    assert 'Sm_M1_Garand' in w.static_mesh_component.get_editor_property('static_mesh').get_path_name()
                    report['action_attachments'].append({'actor': a.get_name(), 'class': w.get_class().get_path_name(), 'left_shift_cm': prop(w, 'LeftShiftCm')})
                assert len(report['action_attachments']) == 3
            advance('warm')
        elif unreal.GameplayStatics.get_time_seconds(world) - phase_time > (4 if phase == 'warm' else .7):
            if phase == 'warm':
                widgets = unreal.WidgetLibrary.get_all_widgets_of_class(world, widget_class, True)
                report['widget_count'] = len(widgets)
                assert len(widgets) == 1
                widget = widgets[0]
                report['widget'] = widget.get_class().get_path_name()
                report['hud_initial_text'] = str(widget.get_editor_property('StatusText').get_text())
                report['initial_state'] = state(player)
                capture('hud_initial')
                origin_location = player.get_actor_location()
                if arms_preview:
                    arms_trial = RuntimeTrial(world,player)
                    weapon = arms_trial.weapon
                    report['continuous_arms_trial'] = arms_trial.n['report']
                if native_preview:
                    if arms_trial is None:
                        if checkpoint_name == 'CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json':
                            existing_actors=[n for n in unreal.GameplayStatics.get_all_actors_of_class(world,unreal.SkeletalMeshActor) if n.get_class().get_name() == 'BP_PC_ContinuousArmsNativeV1_C']
                            assert len(existing_actors)==1
                            existing=existing_actors[0]
                        else:
                            existing=None
                        arms_trial=NativeTrial(world,player,existing)
                    if not arms_trial.initialized():
                        return
                    weapon=arms_trial.weapon
                    report['continuous_arms_trial']={'implementation':'Native Blueprint tick only; no Python display update','snapshot':arms_trial.snapshot()}
                aim(enemy)
                advance('free')
            elif phase == 'free':
                shot('unobstructed_hostile', free)
                shot('same_frame_cooldown', reject)
                capture('hud_hostile_hit')
                advance('friendly_setup')
            elif phase == 'friendly_setup':
                midpoint = (player.get_actor_location() + enemy.get_actor_location()) * .5
                ally.set_actor_location(midpoint, False, False)
                aim(enemy)
                advance('friendly')
            elif phase == 'friendly':
                shot('ally_in_front_of_enemy', blocked)
                ally.set_actor_location(origin_location + unreal.Vector(0, -400, 0), False, False)
                advance('empty')
            elif phase == 'empty':
                shot('empty', reject)
                player.call_method('PC_RequestReload')
                report['reload_started'] = state(player)
                advance('busy')
            elif phase == 'busy':
                shot('busy', reject)
                advance('reload')
            elif phase == 'invalid':
                shot('zero_direction', reject, invoke='PC_RequestFire', args=(origin_location, unreal.Vector()))
                shot('nonfinite_direction', reject, invoke='PC_RequestFire', args=(origin_location, unreal.Vector(float('nan'), 0, 0)))
                shot('nonfinite_origin', reject, invoke='PC_RequestFire', args=(unreal.Vector(float('inf'), 0, 0), unreal.Vector(1, 0, 0)))
                before = state(enemy)
                enemy.call_method('PC_RequestFire', args=(origin_location, unreal.Vector(1, 0, 0)))
                after = state(enemy)
                report['cases'].append({'name': 'unarmed_german_rejects_fire', 'before': before, 'after': after,
                    'assertions': {'no_round': before['LoadedAmmo'] == after['LoadedAmmo'],
                        'no_sequence': before['ShotSequence'] == after['ShotSequence'], 'rejected': after['ShotOutcome'] == 'Rejected'}})
                controller.set_control_rotation(unreal.Rotator(pitch=-80, yaw=0, roll=0))
                advance('world')
            elif phase == 'world':
                shot('existing_road_blocks', blocked)
                aim(enemy)
                advance('embedded')
            elif phase == 'embedded':
                # Runtime-only existing rifle transform crosses the actual road.
                saved_transform = weapon.get_actor_transform()
                weapon.set_actor_location(player.get_actor_location() - unreal.Vector(0, 0, 50), False, False)
                weapon.set_actor_rotation(unreal.Rotator(pitch=0, yaw=0, roll=90), False)
                shot('barrel_crossing_existing_road', blocked)
                weapon.set_actor_transform(saved_transform, False, False)
                advance('new_life')
            elif phase == 'new_life':
                shot('second_unobstructed_hostile', free)
                player.call_method('PC_ResetLifecycle')
                shot('new_generation_clears_stale_cooldown', free)
                report['target_killed'] = state(enemy)
                player.call_method('PC_ApplyDamage', args=(1000.0,))
                shot('dead_player', reject)
                player.call_method('PC_ResetLifecycle')
                advance('final_hud')
            elif phase == 'reload':
                if prop(player, 'LoadedAmmo') > 0 and str(prop(player, 'ActionState')) == 'Reloading' and not report.get('busy_positive_tested'):
                    shot('reload_after_commit_still_rejects_fire', reject)
                    report['busy_positive_tested'] = True
                if unreal.GameplayStatics.get_time_seconds(world) - phase_time < 8:
                    return
                report['reload_finished'] = state(player)
                report['reload_conserved'] = prop(player, 'LoadedAmmo') == 8 and prop(player, 'ReserveAmmo') == 8
                capture('hud_reload_complete')
                advance('invalid')
            elif phase == 'final_hud':
                if checkpoint_name == 'CITY_WEAPON_GRIP_DRAFT_INVENTORY_20261002.json':
                    report['grip_after_reload_death_reset'] = player.get_component_by_class(unreal.SkeletalMeshComponent).get_anim_instance().get_class().get_path_name()
                    assert 'ABP_PC_AlliedGripV1_C' in report['grip_after_reload_death_reset']
                if checkpoint_name in ('CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json', 'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json','CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json'):
                    report['original_pose_after_reload_death_reset'] = player.get_component_by_class(unreal.SkeletalMeshComponent).get_anim_instance().get_class().get_path_name()
                    expected_anim = 'ABP_PC_PlayerRigidAimV4_C' if aim_preview else 'ABP_PC_Allied_Stride_v1_C'
                    assert expected_anim in report['original_pose_after_reload_death_reset']
                report['final_state'] = state(player)
                report['hud_final_text'] = str(widget.get_editor_property('StatusText').get_text())
                capture('hud_final')
                if arms_trial:
                    report['continuous_arms_after_reload_death_reset'] = arms_trial.snapshot()
                    s = report['continuous_arms_after_reload_death_reset']
                    assert s['finger_local_delta'] < 1e-6 and s['display_bound'] and (unreal.Vector(*s['camera_relative_cm'])-unreal.Vector(25,0,60)).length() < 1e-6 and abs(s['fov']-90) < 1e-6
                    player.set_actor_location(origin_location,False,True)
                    player.get_component_by_class(unreal.CharacterMovementComponent).stop_movement_immediately()
                    controller.set_control_rotation(unreal.Rotator())
                    advance('arms_near_setup')
                else:
                    advance('capture_wait')
            elif phase == 'arms_near_setup':
                cam = player.get_component_by_class(unreal.CameraComponent)
                t = cam.get_world_transform()
                t.translation = cam.get_world_location()+cam.get_forward_vector()*80
                t.scale3d = unreal.Vector(.02,3,3)
                api = unreal.get_default_object(unreal.GameplayStatics.static_class())
                near_blocker = api.call_method('BeginDeferredActorSpawnFromClass',args=(world,unreal.StaticMeshActor.static_class(),t,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,None,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
                component = near_blocker.static_mesh_component
                component.set_mobility(unreal.ComponentMobility.MOVABLE)
                component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'))
                component.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
                component.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_IGNORE)
                component.set_collision_response_to_channel(unreal.CollisionChannel.ECC_VISIBILITY,unreal.CollisionResponseType.ECR_BLOCK)
                near_blocker = api.call_method('FinishSpawningActor',args=(near_blocker,t,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
                advance('arms_near_assert')
            elif phase == 'arms_near_assert':
                cam = player.get_component_by_class(unreal.CameraComponent)
                debug = trace_debug()
                hit = debug['camera_hit']
                assert hit and hit['actor'] == near_blocker.get_name()
                distance = (unreal.Vector(*hit['point'])-cam.get_world_location()).length()
                dot = unreal.MathLibrary.transform_direction(weapon.get_actor_transform(),unreal.Vector(0,1,0)).dot(cam.get_forward_vector())
                assert 75 < distance < 85 and dot > .95
                report['continuous_arms_near_wall'] = {'camera_hit_distance_cm':distance,'barrel_camera_dot':dot,'binding':'display actor','ordinary_goal':'200m forward; no claim of close-target barrel convergence'}
                shot('continuous_arms_near_wall_retains_obstruction',blocked)
                report['final_state'] = state(player)
                capture('continuous_arms_near_wall')
                advance('arms_near_wait')
            elif phase == 'arms_near_wait':
                near_blocker.destroy_actor()
                near_blocker = None
                advance('capture_wait')
            elif phase == 'capture_wait':
                finish()
    except Exception:
        finish(traceback.format_exc())
    finally:
        in_tick = False


unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback = unreal.register_slate_post_tick_callback(tick)
checkpoint()
levels.editor_request_begin_play()
