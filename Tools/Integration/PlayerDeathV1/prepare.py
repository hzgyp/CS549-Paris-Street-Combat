"""Freeze the field-manual parent and author an independent presentation child."""
from pathlib import Path
import argparse,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import prepare,OUT,read,write,sha,rows

ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
base=ROOT/'tmp/g1-player-death-20261011';base.mkdir(exist_ok=True)
parent=read(ROOT/'Docs/Development/CURRENT_UI_REVIEW.json')
assert parent['game_sha256']=='b40590bdec9c27d4a2c2f321ae32c0eca12936923f36d003872df2dabc113d11'
expected=read(ROOT/parent['source_manifest'])['files'];assert rows(ROOT/parent['source_snapshot'])==expected
if not (base/'freeze.json').exists():
    user=Path.home()/'AppData/Local/ParisStreetCombat'/parent['user_dir']
    write(base/'freeze.json',dict(parent=parent,parent_files=expected,parent_normal_files=rows(ROOT/parent['playable_directory']),user_root=str(user),user_files=rows(user),root_trial_wrappers=[dict(path=n,sha256=sha(ROOT/n)) for n in ['PLAY_COMBAT_UI.cmd','PLAY_FIELD_MANUAL_UI.cmd','PLAY_TACTICAL_EQUIPMENT.cmd']]))
prepare(a.revision,'candidate_field_manual_v2')
project=OUT/a.revision/'Project';assert all(sha(project/r['path'])==r['sha256'] for r in expected)
private=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
for n in ['ParisPlayerDeath.h','ParisPlayerDeath.cpp','ParisPlayerDeathProbe.inl','ParisExplosionVisual.inl']:
    (private/n).write_bytes((Path(__file__).parent/n).read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
def replace(name,old,new):
    p=private/name;s=p.read_text('utf-8-sig');assert s.count(old)==1,(name,old);s=s.replace(old,new);p.write_bytes(s.replace('\n','\r\n').encode())
for n in ['ParisBridgeMission.cpp','ParisBridgeMissionV1.cpp','ParisMissionInteraction.cpp','ParisCombatUI.cpp','ParisTacticalEquipment.cpp']:
    replace(n,'#include "ParisCombatUI.h"','#include "ParisCombatUI.h"\n#include "ParisPlayerDeath.h"')
replace('ParisBridgeMissionV1.cpp','  ParisCombatUI::Initialize();','  ParisPlayerDeath::Initialize();\n  ParisCombatUI::Initialize();')
replace('ParisBridgeMissionV1.cpp','void ShutdownModule()override{','void ShutdownModule()override{ParisPlayerDeath::Shutdown();')
replace('ParisBridgeMission.cpp','void AParisBridgeHUD::DrawHUD()\n{','void AParisBridgeHUD::DrawHUD()\n{\n    if(ParisPlayerDeath::Presenting(this))return;')
replace('ParisBridgeMission.cpp','M->Phase==TEXT("Ready")?TEXT("G1 BRIDGEHEAD"):TEXT("MISSION ENDED")','M->Phase==TEXT("Ready")?TEXT("G1 BRIDGEHEAD"):M->Phase==TEXT("Lost")?TEXT("YOU DIED"):TEXT("MISSION ENDED")')
replace('ParisBridgeMission.cpp','if(!M->CheckpointDialogVisible() && !LastFeedback.StartsWith','if(!(MenuVisible && M->Phase==TEXT("Lost")) && !M->CheckpointDialogVisible() && !LastFeedback.StartsWith')
replace('ParisMissionInteraction.cpp','return M && ParisMissionInteraction::MenuPhase(M->Phase);','return M && ParisMissionInteraction::MenuPhase(M->Phase) && !ParisPlayerDeath::Presenting(this);')
replace('ParisMissionInteraction.cpp','bool AParisBridgePlayerController::HandleInteractionInput(const FInputKeyEventArgs& Params) {','bool AParisBridgePlayerController::HandleInteractionInput(const FInputKeyEventArgs& Params) {\n    if(ParisPlayerDeath::Presenting(this))return true;')
replace('ParisCombatUI.cpp','bool Open(AParisBridgePlayerController* PC,int32 Page){','bool Open(AParisBridgePlayerController* PC,int32 Page){if(ParisPlayerDeath::Presenting(PC))return false;')
replace('ParisTacticalEquipment.cpp','#include "ParisEquipmentAudio.inl"','#include "ParisExplosionVisual.inl"\n#include "ParisEquipmentAudio.inl"')
replace('ParisTacticalEquipment.cpp','#include "Camera/PlayerCameraManager.h"','#include "Camera/PlayerCameraManager.h"\n#include "Distributions/DistributionFloatConstantCurve.h"\n#include "Particles/ParticleSystemComponent.h"\n#include "TimerManager.h"')
old='    auto* Flash=Prop(W,TEXT("Blast"),At);auto* Light=NewObject<UPointLightComponent>(Flash);Flash->AddInstanceComponent(Light);Light->SetupAttachment(Flash->GetRootComponent());Light->SetIntensity(6000);Light->SetAttenuationRadius(650);Light->SetLightColor(FLinearColor(1,.58,.22));Light->RegisterComponent();Flash->SetLifeSpan(.12f);'
replace('ParisEquipmentAudio.inl',old,'    ExplosionVisual(W,At);')
replace('ParisPressureMineChecks.inl','CheckClock>(CheckMode==TEXT("mine_post_clear_frag")?6:.5)','CheckClock>4.5&&ParisPlayerDeath::Complete(W)')
write(OUT/a.revision/'death-authoring.json',dict(status='independent_render_candidate',parent=parent['source_snapshot'],native='unchanged',changes='death camera/body visibility/input-HUD delay, transient blast particles, later post-clear fixture actions'))
print(project)
