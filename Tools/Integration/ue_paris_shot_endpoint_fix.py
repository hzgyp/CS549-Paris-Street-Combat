"""Bounded common-shot endpoint correction after actual-city failing evidence."""
import hashlib
import json
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ue_paris_graph_helpers import lib, pins, pin, pure, wire
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002/Setup/shot_endpoint_fix_v1.json'
assert not OUT.exists()
inventory = json.loads((ROOT / 'Assets/Integration/CITY_COMBAT_DRAFT_INVENTORY_20261002.json').read_text())
old = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
guarded = inventory['files'] + old['files']
assert all(hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'] for f in guarded)
BASE = '/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2'
report = {'scope': 'Only common shot endpoint; not runtime acceptance', 'errors': []}
try:
    bp = unreal.load_asset(BASE)
    g = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'PC_DoShot')
    traces = [n for n in g.list_all_nodes() if pins.is_valid(lib.find_input_pin(n, 'TraceChannel'))]
    report['trace_pin_values'] = [{str(pins.get_pin_name(p)): pins.get_pin_value(p) for p in lib.list_all_pins(n)} for n in traces]
    candidates = []
    for node in traces:
        start = pins.list_connected_pins(pin(node, 'Start'))
        if not pins.is_valid(lib.find_input_pin(node, 'Radius')) and len(start) == 1:
            source = pins.get_owning_node(start[0])
            if pins.is_valid(lib.find_input_pin(source, 'T')):
                candidates.append(node)
    assert len(candidates) == 1
    bullet = candidates[0]
    end_pin = pin(bullet, 'End')
    end_source = pins.list_connected_pins(end_pin)
    muzzle = pins.list_connected_pins(pin(bullet, 'Start'))[0]
    assert len(end_source) == 1
    aim = end_source[0]
    delta = pure(g, '/Script/Engine.KismetMathLibrary.Subtract_VectorVector', A=aim, B=muzzle)
    normal = pure(g, '/Script/Engine.KismetMathLibrary.Normal', A=delta)
    extension = pure(g, '/Script/Engine.KismetMathLibrary.Multiply_VectorFloat', A=normal, B=2)
    endpoint = pure(g, '/Script/Engine.KismetMathLibrary.Add_VectorVector', A=aim, B=extension)
    assert pins.break_pin_links(end_pin)
    wire(endpoint, end_pin)
    assert lib.compile_blueprint(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    file = next(f for f in inventory['files'] if f['package'] == BASE)
    path = ROOT / file['path']
    report['saved_file'] = dict(file, size_bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    report['status'] = 'saved_endpoint_fix_not_runtime_acceptance'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    report['other_34_drafts_unchanged'] = all(hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256']
        for f in guarded if f.get('package') != BASE)
    OUT.write_text(json.dumps(report, indent=2))
if report['errors']:
    raise RuntimeError('Inspect preserved endpoint correction report')
