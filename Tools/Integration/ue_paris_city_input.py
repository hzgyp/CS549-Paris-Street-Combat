"""Bind existing controls to the new real-city player Blueprint, with hash guards."""
import hashlib
import json
import os
import traceback
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/Setup'
IDENTITY = os.environ.get('CS549_CITY_INPUT_IDENTITY', 'input_v1')
assert IDENTITY.replace('_', '').isalnum()
DEST = OUT / (IDENTITY + '.json')
assert not DEST.exists(), 'Preserve occupied input evidence'
AUTHOR = os.environ.get('CS549_CITY_AUTHOR_IDENTITY', 'author_v4')
authored = json.loads((OUT / (AUTHOR + '.json')).read_text(encoding='utf-8'))
assert authored['status'] == 'saved_asset_backed_city_setup_not_gameplay_acceptance'
TARGET = '/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'
report = {'scope': 'Existing axis/R bindings on actual-city player; no Fire diagnostic, HUD, device/runtime or mission pass',
          'bindings': [], 'errors': []}
lib = unreal.BlueprintEditorLibrary
pins = unreal.BlueprintGraphPinLibrary


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wire(source, destination):
    assert pins.is_valid(source) and pins.is_valid(destination), 'Missing graph pin'
    assert pins.try_create_connection(source, destination), 'Graph connection rejected'


try:
    for item in authored['saved_files']:
        assert digest(ROOT / item['path']) == item['sha256'], 'Unsynchronized setup change: ' + item['path']
    bp = unreal.load_asset(TARGET)
    assert bp
    graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'EventGraph')
    assert graph
    assert not any('InputAxisEvent' in n.get_class().get_name() or 'InputAction' in n.get_class().get_name()
                   for n in graph.list_all_nodes()), 'Refuse existing input events'
    available = graph.list_available_nodes([])
    report['available_input_actions'] = [n for n in available if 'PC' in n and 'Input' in n]
    for index, (axis, request) in enumerate((
        ('PC_MoveForward', 'PC_RequestMoveForward'), ('PC_MoveRight', 'PC_RequestMoveRight'),
        ('PC_LookYaw', 'PC_RequestLookYaw'), ('PC_LookPitch', 'PC_RequestLookPitch'))):
        candidates = [n for n in available if 'AxisEvents' in n and n.rsplit('|', 1)[-1].replace('_', '') == axis.replace('_', '')]
        assert len(candidates) == 1, 'Ambiguous/missing axis event: ' + axis
        event = graph.create_node_from_name(candidates[0], unreal.Vector2D(0, index * 300), [])
        assert event and event.get_class().get_name() == 'K2Node_InputAxisEvent'
        call = graph.add_call_function_node(request)
        assert call, 'Missing inherited request: ' + request
        lib.set_node_pos(call, unreal.IntPoint(450, index * 300))
        wire(lib.find_then_pin(event), lib.find_execute_pin(call))
        wire(lib.find_output_pin(event, 'AxisValue'), lib.find_input_pin(call, 'AxisValue'))
        report['bindings'].append({'axis': axis, 'request': request, 'event': candidates[0]})
    candidates = [n for n in available if 'ActionEvents' in n and n.rsplit('|', 1)[-1].replace('_', '') == 'PCReload']
    assert len(candidates) == 1, 'Ambiguous/missing reload action event'
    event = graph.create_node_from_name(candidates[0], unreal.Vector2D(0, 1200), [])
    call = graph.add_call_function_node('PC_RequestReload')
    assert call
    lib.set_node_pos(call, unreal.IntPoint(450, 1200))
    wire(lib.find_output_pin(event, 'Pressed'), lib.find_execute_pin(call))
    report['bindings'].append({'action': 'PC_Reload', 'key': 'R', 'request': 'PC_RequestReload'})
    assert lib.compile_blueprint(bp), 'City input compile failed'
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report['status'] = 'saved_city_input_bindings_not_device_test'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    snapshot = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
    report['previous_28_drafts_unchanged'] = all(digest(ROOT / f['path']) == f['sha256'] for f in snapshot['files'])
    report['other_setup_files_unchanged'] = all(digest(ROOT / f['path']) == f['sha256'] for f in authored['saved_files']
                                                if f['package'] != TARGET)
    file = STORE / 'Content' / (TARGET.removeprefix('/Game/') + '.uasset')
    report['saved_file'] = {'package': TARGET, 'path': file.relative_to(ROOT).as_posix(),
                            'size_bytes': file.stat().st_size, 'sha256': digest(file)}
    if not report['previous_28_drafts_unchanged'] or not report['other_setup_files_unchanged']:
        report['status'] = 'failed'
        report['errors'].append('Unexpected other native byte change')
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_CITY_INPUT ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved input report')
