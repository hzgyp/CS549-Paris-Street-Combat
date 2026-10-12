"""Readonly final source, runtime, launcher and receipt closure."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read,write,rows,sha,INNER,OUT
base=ROOT/'tmp/g1-combat-ui-20261011';d=read(base/'DELIVERY_20261011.json')
source=ROOT/d['source_snapshot'];manifest=ROOT/d['source_manifest']
assert sha(manifest)==d['source_manifest_sha256']
assert rows(source)==read(manifest)['files'] and len(rows(source))==67
assert rows(source)==rows(OUT/d['revision']/'compiled-source-game')
normal=ROOT/d['playable_directory'];assert rows(normal)==d['normal_files']
assert sha(normal/INNER)==d['game_sha256']
wrapper=b'@echo off\r\ncall "%~dp0tmp\\Playtest-G1-CombatUI-20261011\\PLAY_COMBAT_UI.cmd"\r\n'
assert (ROOT/'PLAY_COMBAT_UI.cmd').read_bytes()==wrapper
assert (ROOT/'PLAY_TACTICAL_EQUIPMENT.cmd').read_bytes()==wrapper
launcher=(normal/'PLAY_COMBAT_UI.cmd').read_text('utf-8')
assert 'G1CombatUI20261011' in launcher and 'ParisCombatUIV1' in launcher
assert not any(s in launcher for s in ['Probe','EquipmentCheck','Observer','Out=','Solo','Background'])
review=read(ROOT/'Docs/Development/CURRENT_UI_REVIEW.json')
assert review['game_sha256']==d['game_sha256'] and review['revision']==d['revision']
assert len(d['checks'])==19
for c in d['checks']:
    result=ROOT/c['result'];assert sha(result)==c['result_sha256'] and read(result)['status'].startswith('pass')
    launch=read(result.parent/'launch.json');assert launch['exit_code']==0 and launch['game_sha256']==d['game_sha256']
for rel in [d['implementation'],d['result'],'Docs/Development/CURRENT_UI_REVIEW.md']:
    assert (ROOT/rel).is_file()
receipt=dict(status='pass',source_files=67,normal_files=len(d['normal_files']),source_manifest_sha256=d['source_manifest_sha256'],game_sha256=d['game_sha256'],actual_same_Game_checks=19,normal_no_probes=True,formal_not_adopted=True,manual_review='pending')
write(base/'DELIVERY_CLOSURE_20261011.json',receipt)
print(receipt)
