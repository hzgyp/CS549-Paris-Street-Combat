"""Normal-speed transient complete-arm review; never save the editor city."""
import hashlib
import json
import os
import sys
import time
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).parent))
from ue_continuous_arms_runtime_trial import BASE, ROOT, RuntimeTrial, trial_records

identity = os.environ['CS549_ARMS_HUMAN_IDENTITY']
assert identity.replace('_', '').isalnum()
out = BASE/identity
assert not out.exists(), 'Preserve occupied evidence identity'
out.mkdir()
for name in ('ue_continuous_arms_human_preview.py', 'ue_continuous_arms_runtime_trial.py', 'ue_continuous_arms_dynamic.py'):
    (out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
records = trial_records()

def guard():
    return all((ROOT/f['path']).stat().st_size == f['size_bytes'] and
               hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest() == f['sha256'] for f in records)

assert guard(), 'Protected native bytes differ'
report = {'status': 'starting_human_review', 'pid': os.getpid(), 'errors': [],
          'native_count': len(records), 'native_bytes_unchanged': True,
          'native_saved': False, 'human_acceptance': False, 'normal_speed': True}
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
started = time.monotonic()
warmup = None
trial = None
callback = None

def write():
    (out/'result.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')

def stop(status):
    report['status'] = status
    report['native_bytes_unchanged'] = guard()
    write()
    unreal.unregister_slate_post_tick_callback(callback)
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)

def tick(delta):
    global warmup, trial
    try:
        world = editor.get_game_world()
        player = unreal.GameplayStatics.get_player_pawn(world, 0) if world else None
        if not player:
            if trial is not None:
                stop('human_ended_pie_not_acceptance')
                return
            assert time.monotonic()-started < 300, 'Preview PIE startup timeout'
            return
        if warmup is None:
            warmup = time.monotonic()
        if time.monotonic()-warmup < 20:
            return
        if trial is None:
            trial = RuntimeTrial(world, player)
            snapshot = trial.snapshot()
            assert snapshot['display_bound'] and snapshot['original_anim_class'] == 'ABP_PC_Allied_Stride_v1_C'
            assert max(abs(a-b) for a,b in zip(snapshot['camera_relative_cm'], (25,0,60))) < 1e-6
            assert abs(snapshot['fov']-90) < 1e-6 and snapshot['finger_local_delta'] < 1e-6
            report['initial_snapshot'] = snapshot
            report['status'] = 'ready_user_owned_runtime_only_review'
            report['native_bytes_unchanged'] = guard()
            assert report['native_bytes_unchanged']
            write()
            unreal.log('Complete arms preview ready: click game viewport; WASD / mouse / left click / R. Esc ends PIE. No city save.')
        trial.update()
    except Exception:
        report['errors'].append(traceback.format_exc())
        stop('failed_review_callback')
        levels.editor_request_end_play()
        unreal.log_error(report['errors'][-1])

unreal.EditorPythonScripting.set_keep_python_script_alive(True)
callback = unreal.register_slate_post_tick_callback(tick)
write()
levels.editor_request_begin_play()
