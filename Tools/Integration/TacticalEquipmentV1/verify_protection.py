from prepare import ROOT,OUT,read,rows,sha,write
from pathlib import Path
import argparse,re
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
f=read(OUT/'freeze.json');parent=ROOT/f['parent']['source_snapshot'];project=OUT/a.revision/'Project'
assert rows(parent)==f['parent_files']
changed=[]
for r in f['parent_files']:
    if sha(project/r['path'])!=r['sha256']:changed.append(r['path'])
b='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/'
allowed={b+'Private/ParisBridgeMission.cpp',b+'Private/ParisMissionInteraction.cpp',b+'Private/ParisBridgeMissionV1.cpp',b+'Public/ParisBridgeMission.h',b+'ParisBridgeMissionV1.Build.cs'}
assert set(changed)==allowed,changed
for r in f['parent_files']:
    if r['path'].endswith('.h'):
        def reflection(p):return re.findall(rb'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',p.read_bytes())
        assert reflection(parent/r['path'])==reflection(project/r['path']),r['path']
new=(project/(b+'Private/ParisBridgeMission.cpp')).read_bytes();old=(parent/(b+'Private/ParisBridgeMission.cpp')).read_bytes()
new=new.replace(b'    if(ParisTacticalEquipment::OwnsNavigation(Controller))return true;\r\n',b'')
def block(s,start,end):return s[s.index(start):s.index(end,s.index(start))] if end else s[s.index(start):]
protected=[(b'bool AParisBridgeMission::IsSafeBoundary(',b'FString AParisBridgeMission::CaptureSnapshot('),(b'bool AParisBridgeMission::SaveCheckpoint()',b'bool AParisBridgeMission::ApplySnapshot('),(b'bool AParisBridgeMission::StartMission()',b'bool AParisBridgeMission::ApplyBridgeNavigationConstraint('),(b'bool AParisBridgeMission::ApplyBridgeNavigationConstraint(',b'void AParisBridgeMission::Tick('),(b'void AParisBridgePlayerController::PostProcessInput(',None)]
for start,end in protected:assert block(new,start,end)==block(old,start,end),start
interaction=b+'Private/ParisMissionInteraction.cpp'
for start,end in [(b'FString AParisBridgeMission::CheckpointSaveBlockReason()',b'bool AParisBridgeMission::InteractCheckpoint()'),(b'bool AParisBridgeMission::InteractCheckpoint()',b'bool AParisBridgePlayerController::InteractionMenuVisible()')]:
    old_i=(parent/interaction).read_bytes();new_i=(project/interaction).read_bytes()
    assert block(new_i,start,end)==block(old_i,start,end),start
for r in f['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
assert sha(ROOT/'Assets/Sync/CATALOG.json')==f['catalog_sha256']
assert rows(Path(f['user_root']))==f['user_files']
inner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
assert sha(ROOT/f['parent']['playable_directory']/inner)==f['parent']['game_sha256']
write(OUT/a.revision/'protection.json',dict(status='pass',native_files=len(f['protected_native']),parent_files=len(f['parent_files']),changed_parent_files=changed,preserved_original_reflection=True,protected_algorithms=len(protected)+2,original_normal_user_files=len(f['user_files']),catalog_exact=True,parent_game_exact=True))
print('PASS native/source/reflection/journal/input/navigation/Catalog/parent Game/original user-save protection')
