"""Hash-guarded correction of three accidentally vector-promoted multipliers."""
import hashlib
import json
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ue_paris_graph_helpers import lib, pins, pin, pure, wire
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/CityGameplay20261002'
OUT = EVIDENCE / 'Setup/shot_scalar_fix_v2.json'
assert not OUT.exists()
inventory = json.loads((ROOT / 'Assets/Integration/CITY_COMBAT_DRAFT_INVENTORY_20261002.json').read_text())
old = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
guarded = inventory['files'] + old['files']
assert all(hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'] for f in guarded)
BASE = '/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2'
report = {'scope': 'Three typed scalar operand fixes; not runtime acceptance', 'changed': [], 'errors': []}
try:
    bp = unreal.load_asset(BASE)
    g = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'PC_DoShot')
    nodes = [n for n in g.list_all_nodes() if str(lib.get_node_title(n)) == 'vector * vector']
    assert len(nodes) == 3
    # Exact node IDs and values were captured in shot_graph_audit_v1.json.
    values = {'K2Node_PromotableOperator_11': 20000.0,
              'K2Node_PromotableOperator_13': .1,
              'K2Node_PromotableOperator_19': 2.0}
    assert {n.get_name() for n in nodes} == set(values)
    for node in nodes:
        b = pin(node, 'B')
        assert not pins.list_connected_pins(b)
        amount = values[node.get_name()]
        # Explicit uniform vector scale is mathematically scalar multiplication;
        # it avoids silently retyping a disconnected literal during promotion.
        scale = pure(g, '/Script/Engine.KismetMathLibrary.MakeVector', X=amount, Y=amount, Z=amount)
        wire(scale, b)
        title = str(lib.get_node_title(node))
        assert title == 'vector * vector' and len(pins.list_connected_pins(b)) == 1, title
        report['changed'].append({'node': node.get_name(), 'title': title, 'scalar': values[node.get_name()]})
    assert lib.compile_blueprint(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    file = next(f for f in inventory['files'] if f['package'] == BASE)
    path = ROOT / file['path']
    report['saved_file'] = dict(file, size_bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    report['status'] = 'saved_explicit_uniform_scale_fix_not_runtime_acceptance'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    report['other_34_drafts_unchanged'] = all(hashlib.sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256']
        for f in guarded if f.get('package') != BASE)
    OUT.write_text(json.dumps(report, indent=2))
if report['errors']:
    raise RuntimeError('Inspect preserved scalar correction report')
