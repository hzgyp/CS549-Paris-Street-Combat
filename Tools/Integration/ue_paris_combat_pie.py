"""Bridge-disabled actual-city combat/HUD regression; transient tests, no saves."""
import hashlib
import json
import os
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
current = json.loads((ROOT / 'Assets/Integration' / checkpoint_name).read_text())
guarded = {f['path']: f['sha256'] for f in old['files'] + current['files']}
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
    global in_tick, world, player, controller, enemy, ally, weapon, widget, origin_location, index
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
        if phase == 'waiting':
            world = editor.get_game_world()
            player = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
            if not player:
                return
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
                report['final_state'] = state(player)
                report['hud_final_text'] = str(widget.get_editor_property('StatusText').get_text())
                capture('hud_final')
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
