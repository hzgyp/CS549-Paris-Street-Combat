"""One-time guarded removal of four vendor documentation helpers from team entry."""
import hashlib
import json
import shutil
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/Packaging/entry_fix_v1'
assert not OUT.exists(), 'Preserve occupied correction/recovery identity'
DEST = ROOT / 'Assets/Integration/CITY_PACKAGE_DRAFT_INVENTORY_20261002.json'
assert not DEST.exists(), 'Refuse existing package checkpoint'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
inventory = json.loads((ROOT / 'Assets/Integration/CITY_COMBAT_DRAFT_INVENTORY_20261002.json').read_text())
older = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
map_item = next(f for f in inventory['files'] if f['package'] == ENTRY)
map_file = ROOT / map_item['path']
guarded = {ROOT / f['path']: f['sha256'] for f in inventory['files'] + older['files']}
for path in (STORE / 'Content/WW2City/Maps').rglob('*.umap'):
    guarded[path] = hashlib.sha256(path.read_bytes()).hexdigest()
report = {'scope': 'Remove only team-root documentation helpers; no vendor resave or gameplay redesign',
          'removed': [], 'errors': [], 'before': map_item}
try:
    for path, expected in guarded.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected, str(path)
    audit = json.loads((OUT.parent / 'dependencies_v2.json').read_text())
    assert audit['status'] == 'pass_readonly_dependency_audit' and audit['guarded_bytes_unchanged']
    allowed = {x['path']: x['class'] for x in audit['placed_showcase_actors']}
    assert len(allowed) == 4
    assert all(p.startswith(ENTRY + '.' + ENTRY.rsplit('/', 1)[-1] + ':PersistentLevel.') for p in allowed)
    assert unreal.EditorLevelLibrary.load_level(ENTRY)
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = {a.get_path_name(): a for a in subsystem.get_all_level_actors()}
    assert all(p in actors and actors[p].get_class().get_path_name() == c for p, c in allowed.items())
    OUT.mkdir(parents=True)
    recovery = OUT / 'LV_ParisStreetCombat_V1_before.umap'
    shutil.copyfile(map_file, recovery)
    assert hashlib.sha256(recovery.read_bytes()).hexdigest() == map_item['sha256']
    for path in sorted(allowed):
        assert subsystem.destroy_actor(actors[path]), path
        report['removed'].append(path)
    assert unreal.EditorAssetLibrary.save_asset(ENTRY, only_if_is_dirty=False)
    after = dict(map_item, size_bytes=map_file.stat().st_size, sha256=hashlib.sha256(map_file.read_bytes()).hexdigest())
    report['after'] = after
    report['other_guarded_bytes_unchanged'] = all(hashlib.sha256(p.read_bytes()).hexdigest() == h
                                               for p, h in guarded.items() if p != map_file)
    assert report['other_guarded_bytes_unchanged']
    inventory['scope'] = 'Current seven city/combat/HUD packages after removal of four documentation helpers; cooking/runtime acceptance recorded separately'
    inventory['previous_checkpoint'] = 'CITY_COMBAT_DRAFT_INVENTORY_20261002.json is historical after the documented team entry correction; do not restore its map over this checkpoint'
    inventory['evidence'] = str((OUT / 'result.json').relative_to(ROOT)).replace('\\', '/')
    inventory['files'] = [after if f['package'] == ENTRY else f for f in inventory['files']]
    inventory['total_size_bytes'] = sum(f['size_bytes'] for f in inventory['files'])
    DEST.write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    report['status'] = 'saved_team_entry_documentation_cleanup_not_package_acceptance'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_PACKAGE_ENTRY_FIX ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved correction/recovery report')
