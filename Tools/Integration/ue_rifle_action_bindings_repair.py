"""One-time exact-hash correction of new rifle trial instance bindings, no city edit."""
import hashlib
import json
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
BASE = STORE / 'Evidence/CityGameplay20261002/RifleActionAttachmentV3'
OUT = BASE / 'author_v4'
assert not OUT.exists()
prior = json.loads((BASE / 'author_v3/result.json').read_text())
assert prior['status'] == 'saved_unselected_rifle_actor_requires_fresh_runtime_review' and not prior['errors']
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
item = prior['saved_trial']
p = ROOT / item['path']
assert digest(p) == item['sha256']
backup = BASE / 'BeforeBindings/BP_PC_RifleAttachmentV3.uasset'
assert digest(backup) == item['sha256'] and backup.stat().st_size == item['size_bytes']
records = []
for name in ('CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002', 'RELOAD_DRAFT_SNAPSHOT_20261002'):
    d = json.loads((ROOT / ('Assets/Integration/'+name+'.json')).read_text())
    records += d['files'] + d.get('retained_unselected_rejected_trial', [])
assert all(digest(ROOT / e['path']) == e['sha256'] for e in records)
bp = unreal.load_asset(prior['package'])
for name in ('GripMesh', 'Combatant', 'LeftShiftCm'):
    unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(bp, name, True)
assert unreal.BlueprintEditorLibrary.compile_blueprint(bp)
assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
prior.update(scope=__doc__, previous_trial=item, binding_flags_repaired=True,
             protected_36_unchanged=all(digest(ROOT / e['path']) == e['sha256'] for e in records))
assert prior['protected_36_unchanged']
prior['saved_trial'] = dict(item, sha256=digest(p), size_bytes=p.stat().st_size)
OUT.mkdir()
(OUT / 'result.json').write_text(json.dumps(prior, indent=2))
unreal.SystemLibrary.quit_editor()
