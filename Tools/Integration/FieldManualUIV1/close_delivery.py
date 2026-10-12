"""Verify the delivered source, executable, launcher and recorded evidence."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT, INNER, read, rows, sha, write

review = read(ROOT / 'Docs/Development/CURRENT_UI_REVIEW.json')
base = ROOT / 'tmp/g1-field-manual-ui-20261011'
delivery = read(base / 'DELIVERY_20261011.json')
assert review['revision'] == 'candidate_field_manual_v2'
manifest = ROOT / review['source_manifest']
assert sha(manifest) == review['source_manifest_sha256']
source_rows = read(manifest)['files']
assert len(source_rows) == 69
for project in [ROOT / review['source_snapshot'], OUT / review['revision'] / 'compiled-source-game']:
    assert rows(project) == source_rows, str(project)
authoring = ROOT / review['active_authoring_project']
for row in source_rows:
    assert sha(authoring / row['path']) == row['sha256'], row['path']

normal = ROOT / review['playable_directory']
assert rows(normal) == delivery['normal_files']
assert sha(normal / INNER) == review['game_sha256']
runtime = read(OUT / review['revision'] / 'runtime.json')
assert runtime['game_sha256'] == review['game_sha256']
assert sha(Path(runtime['path']) / INNER) == review['game_sha256']
expected = b'@echo off\r\ncall "%~dp0tmp\\Playtest-G1-FieldManualUI-20261011\\PLAY_COMBAT_UI.cmd"\r\n'
for name in ['PLAY_COMBAT_UI.cmd', 'PLAY_FIELD_MANUAL_UI.cmd', 'PLAY_TACTICAL_EQUIPMENT.cmd']:
    assert (ROOT / name).read_bytes() == expected
entry = (normal / 'PLAY_COMBAT_UI.cmd').read_bytes()
assert b'G1FieldManualUI20261011' in entry and b'ParisFieldManualUIV1' in entry
assert not any(token in entry for token in [b'Probe', b'EquipmentCheck', b'Observer', b'Solo', b'Background'])
assert read(ROOT / review['protection'])['status'] == 'pass'
visual = read(ROOT / review['visual_review'])
assert visual['status'] == 'pass' and visual['game_sha256'] == review['game_sha256']
assert read(base / 'LOG_REVIEW.json')['status'] == 'classified_no_new_fatal_or_ensure'
assert len(review['checks']) == 19
for check in review['checks']:
    result = ROOT / check['result']
    assert sha(result) == check['result_sha256']
    assert read(result)['status'] == check['status'] and check['status'].startswith('pass')
    launch = read(result.parent / 'launch.json')
    assert launch['exit_code'] == 0 and launch['game_sha256'] == review['game_sha256']
for name in ['FIELD_MANUAL_UI_IMPLEMENTATION_20261011.md', 'FIELD_MANUAL_UI_IMPLEMENTATION_20261011_ZH.md',
             'FIELD_MANUAL_UI_RESULT_20261011.md', 'FIELD_MANUAL_UI_RESULT_20261011_ZH.md']:
    assert (ROOT / 'Docs/Development/MissionLoopV1' / name).is_file()

write(base / 'FINAL_DELIVERY_CHECK.json', dict(
    status='pass', revision=review['revision'], source_files=len(source_rows),
    source_manifest_sha256=sha(manifest), game_sha256=review['game_sha256'],
    normal_files=len(delivery['normal_files']), source_authoring_compiled_exact=True,
    normal_inventory_exact=True, wrappers_exact=True, final_game_checks=19,
    manual_review=review['manual_review'], publication='none'))
print('PASS delivered69 source, normal inventory, three launchers and19 final-Game results; manual review pending')
