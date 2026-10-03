"""Read-only referencer gate before offline archival of exact unselected FP001 assets."""
import json, traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'tmp/failure-archive-20261003/dependencies.json'
report = {'scope': 'Read-only seven-package FP001 referencer audit; no saves', 'errors': []}
try:
    records = json.loads((ROOT / 'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json').read_text())['files']
    packages = {x['package'] for x in records}
    assert len(packages) == 7 and all('/FirstPersonViewV1/' in p for p in packages)
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    options = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True,
        include_searchable_names=True, include_soft_management_references=True, include_hard_management_references=True)
    report['referencers'] = {p: [str(x) for x in registry.get_referencers(p, options)] for p in sorted(packages)}
    report['external_referencers'] = {p: [x for x in rs if x not in packages] for p, rs in report['referencers'].items()}
    assert not any(report['external_referencers'].values()), report['external_referencers']
    report['passed'] = True
except Exception:
    report['passed'] = False
    report['errors'].append(traceback.format_exc())
finally:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + '\n')
    unreal.SystemLibrary.quit_editor()
