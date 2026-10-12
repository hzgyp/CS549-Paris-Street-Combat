"""Create a probe-only child of v4; leave its failed evidence and gameplay unchanged."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,prepare,rows,read,sha,write
parent=OUT/'candidate_ui_v4/Project'; snapshot=OUT/'candidate_ui_v4/compiled-source-game'
prior=rows(snapshot); assert len(prior)==67
assert all(sha(parent/r['path'])==r['sha256'] for r in prior)
assert read(OUT/'candidate_ui_v4/build-game.json')['exit_code']==0
prepare('candidate_ui_v5','candidate_ui_v4')
project=OUT/'candidate_ui_v5/Project'
assert all(sha(project/r['path'])==r['sha256'] for r in prior)
rel='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisCombatUIProbe.cpp'
(project/rel).write_bytes((Path(__file__).with_name('ParisCombatUIProbe.cpp')).read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
assert [r['path'] for r in prior if sha(project/r['path'])!=r['sha256']]==[rel]
write(OUT/'candidate_ui_v5/ui-authoring.json',dict(status='probe_only_child_v4',changed=[rel],reason='MI036 actual Ready Begin mouse action, no assumed Enter selection',gameplay='exact v4 UI and parent mechanisms'))
