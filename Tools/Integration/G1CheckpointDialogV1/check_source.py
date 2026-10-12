"""Early exact parent/schema/transaction guard, independent of test expectation."""
from prepare import ROOT,OUT,SOURCE,rows,load,sha
import re
def main():
 f=load(OUT/'freeze.json');parent=ROOT/f['parent']['source_snapshot'];assert rows(parent)==f['parent_files']
 assert sha(__import__('pathlib').Path(f['parent_game']))==f['parent_game_sha256']
 assert rows(__import__('pathlib').Path(f['parent_user_root']))==f['parent_user_files']
 b='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/'
 allowed={b+'Public/ParisBridgeMission.h',b+'Private/ParisBridgeMission.cpp',b+'Private/ParisMissionInteraction.cpp',b+'Private/ParisMissionInteraction.h',b+'Private/ParisInteractionProbe.cpp'}
 changed={r['path'] for r in f['parent_files'] if sha(SOURCE/r['path'])!=r['sha256']};assert changed==allowed,changed
 for p in SOURCE.rglob('*.h'):
  def declarations(p):return re.findall(r'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',p.read_text(encoding='utf-8-sig'))
  assert declarations(p)==declarations(parent/p.relative_to(SOURCE)),p
 new=(SOURCE/(b+'Private/ParisBridgeMission.cpp')).read_text(encoding='utf-8-sig');old=(parent/(b+'Private/ParisBridgeMission.cpp')).read_text(encoding='utf-8-sig')
 blocks=[('bool AParisBridgeMission::SaveCheckpoint()','bool AParisBridgeMission::ApplySnapshot('),('bool AParisBridgeMission::ValidateSnapshot(','bool AParisBridgeMission::SaveCheckpoint()'),('bool AParisBridgeMission::ApplySnapshot(','bool AParisBridgePlayerController::InputKey('),('bool AParisBridgeMission::StartMission()','bool AParisBridgeMission::ApplyBridgeNavigationConstraint('),('bool AParisBridgeMission::ApplyBridgeNavigationConstraint(','void AParisBridgeMission::Tick('),('bool AParisBridgeMission::IsSafeBoundary(','bool AParisBridgeMission::ValidateSnapshot('),('void AParisBridgePlayerController::PostProcessInput(',None)]
 for start,end in blocks:assert new[new.index(start):new.index(end) if end else None]==old[old.index(start):old.index(end) if end else None],start
 print('PASS: 52 parent files; only 5 UI/probe files differ; reflected schema and 7 protected blocks exact; user files exact')
if __name__=='__main__':main()
