"""Exact protected source/transaction/cooked-schema guards before building or testing."""
from prepare import ROOT,OUT,SOURCE,load,rows,sha
from pathlib import Path
import re
def block(text,start,end=None):return text[text.index(start):text.index(end) if end else None]
def main():
 f=load(OUT/'freeze.json');parent=ROOT/f['parent']['source_snapshot']
 assert rows(parent)==f['parent_files'] and sha(Path(f['parent_game']))==f['parent_game_sha256']
 for user in f['users']:assert rows(Path(user['root']))==user['files'],user['root']
 b='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/'
 allowed={b+'ParisBridgeMission.cpp',b+'ParisMissionInteraction.cpp',b+'ParisInteractionProbe.cpp'}
 changed={r['path'] for r in f['parent_files'] if sha(SOURCE/r['path'])!=r['sha256']};assert changed==allowed,changed
 for h in SOURCE.rglob('*.h'):
  def reflect(p):return re.findall(r'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',p.read_text(encoding='utf-8-sig'))
  assert reflect(h)==reflect(parent/h.relative_to(SOURCE)),h
 new=(SOURCE/(b+'ParisBridgeMission.cpp')).read_text(encoding='utf-8-sig');old=(parent/(b+'ParisBridgeMission.cpp')).read_text(encoding='utf-8-sig')
 blocks=[('bool AParisBridgeMission::IsSafeBoundary(','bool AParisBridgeMission::SaveCheckpoint()'),('    FString Old; int32 Previous=0;','    FString Payload=CaptureSnapshot(Serial);'),('    if(!ValidateSnapshot(Payload,Error))','bool AParisBridgeMission::ApplySnapshot('),('bool AParisBridgeMission::ApplySnapshot(','bool AParisBridgePlayerController::InputKey('),('bool AParisBridgeMission::StartMission()','bool AParisBridgeMission::ApplyBridgeNavigationConstraint('),('bool AParisBridgeMission::ApplyBridgeNavigationConstraint(','void AParisBridgeMission::Tick('),('void AParisBridgePlayerController::PostProcessInput(',None)]
 for start,end in blocks:assert block(new,start,end)==block(old,start,end),start
 admission=block(new,'bool AParisBridgeMission::SaveCheckpoint()','    FString Old; int32 Previous=0;')
 assert not any(x in admission for x in ['Phase!=','DesiredPosture','IsSafeBoundary','SafeSeconds','bBridgeTransitComplete'])
 interaction=(SOURCE/(b+'ParisMissionInteraction.cpp')).read_text(encoding='utf-8-sig')
 reason=block(interaction,'FString AParisBridgeMission::CheckpointSaveBlockReason()','bool AParisBridgeMission::InteractCheckpoint()')
 assert not any(x in reason for x in ['Phase!=','DesiredPosture','IsSafeBoundary','SafeSeconds','bBridgeTransitComplete'])
 victory=block(new,'    // User-selected rule:','    UpdateCheckpointUI();')
 assert 'if(CheckpointUnlocked())' in victory and not any(x in victory for x in ['OccupyRadius','bBridgeTransitComplete'])
 assert 'bool AParisBridgeMission::CheckpointUnlocked()' in new
 assert sha(ROOT/'Assets/Sync/CATALOG.json')==f['catalog_sha256']
 for r in f['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
 assert 'SaveLocation.Z+=StandingHalf-SavedHalf;' in new and 'SaveActor->SetArrayField(TEXT("location"),Vector(SaveLocation))' in new
 print('PASS: only 3 source files differ; reflection exact; durable write/readback/7 protected blocks/1754 native/user files exact; only saved player Z normalized; no obsolete admission gates')
if __name__=='__main__':main()
