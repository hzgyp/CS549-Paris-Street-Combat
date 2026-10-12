from pathlib import Path
import sys,argparse,re
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,sha,rows,INNER
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
freeze=read(ROOT/'tmp/g1-combat-ui-20261011/freeze.json');old=ROOT/freeze['parent']['source_snapshot'];new=OUT/a.revision/'Project'
assert rows(old)==freeze['parent_files']
changed=[r['path'] for r in freeze['parent_files'] if sha(new/r['path'])!=r['sha256']]
base='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/'
allowed={base+n for n in ['ParisBridgeMission.cpp','ParisMissionInteraction.cpp','ParisBridgeMissionV1.cpp','ParisInteractionProbe.cpp','ParisP1Probe.cpp','ParisTacticalEquipment.cpp','ParisEquipmentChecks.inl']}
allowed.add(base.replace('Private/','Public/')+'ParisBridgeMission.h')
assert set(changed)==allowed,changed
for r in freeze['parent_files']:
    if r['path'].endswith('.h'):
        assert re.findall(rb'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',(old/r['path']).read_bytes())==re.findall(rb'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',(new/r['path']).read_bytes()),r['path']
def block(s,start,end):return s[s.index(start):s.index(end,s.index(start))] if end else s[s.index(start):]
mission=base+'ParisBridgeMission.cpp';prior=(old/mission).read_bytes();after=(new/mission).read_bytes().replace(b'#include "ParisCombatUI.h"\r\n',b'')
assert block(prior,b'#include "ParisTacticalEquipment.h"',b'void AParisBridgeHUD::DrawHUD()')==block(after,b'#include "ParisTacticalEquipment.h"',b'void AParisBridgeHUD::DrawHUD()')
assert block(prior,b'namespace ParisPronePrediction',None)==block(after,b'namespace ParisPronePrediction',None)
interaction=base+'ParisMissionInteraction.cpp';prior=(old/interaction).read_bytes();after=(new/interaction).read_bytes().replace(b'#include "ParisCombatUI.h"\r\n',b'')
assert block(prior,b'#include "ParisMissionInteraction.h"',b'bool AParisBridgePlayerController::InteractionMenuVisible()')==block(after,b'#include "ParisMissionInteraction.h"',b'bool AParisBridgePlayerController::InteractionMenuVisible()')
assert block(prior,b'void AParisBridgeMission::SetCheckpointDialog',None)==block(after,b'void AParisBridgeMission::SetCheckpointDialog',None)
equipment=base+'ParisTacticalEquipment.cpp';assert (old/equipment).read_bytes()==(new/equipment).read_bytes().replace(b'#include "ParisCombatUI.h"\r\n',b'')
original=freeze['original_freeze']
for r in original['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
assert sha(ROOT/'Assets/Sync/CATALOG.json')==original['catalog_sha256']
assert rows(Path(original['user_root']))==original['user_files']
assert rows(Path(freeze['mine_user_root']))==freeze['mine_user_files']
assert rows(ROOT/freeze['parent']['playable_directory'])==freeze['parent_normal_files']
formal=ROOT/original['parent']['source_snapshot'];assert rows(formal)==original['parent_files']
assert sha(ROOT/original['parent']['playable_directory']/INNER)==original['parent']['game_sha256']
write(OUT/a.revision/'ui-protection.json',dict(status='pass',native_files=len(original['protected_native']),parent_files=len(freeze['parent_files']),changed_parent_files=changed,original_reflection_exact=True,mission_before_HUD_exact=True,gun_ammo_save_navigation_algorithms_exact=True,checkpoint_write_readback_UI_exact=True,equipment_algorithms_exact=True,original_and_mine_user_files_exact=True,parent_normal_package_exact=True,catalog_exact=True,formal_source_and_Game_exact=True))
print('PASS UI-only boundary / native / fingers / gun / save / parent / users / Catalog')
