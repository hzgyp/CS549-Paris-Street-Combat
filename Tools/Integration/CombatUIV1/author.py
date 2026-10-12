"""Create an additive independent UI candidate from the exact current mine source."""
from pathlib import Path
import sys, json, hashlib, shutil, argparse
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import prepare, OUT, rows, sha, read, write
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
base=ROOT/'tmp/g1-combat-ui-20261011';base.mkdir(exist_ok=True)
current=read(ROOT/'Docs/Development/CURRENT_EQUIPMENT_REVIEW.json')
assert current['game_sha256']=='afc2839d0980a21745510d6f606f0048ff5b85ca872305a036e6011cf619394e'
source=ROOT/current['source_snapshot'];manifest=read(ROOT/current['source_manifest'])
assert rows(source)==manifest['files']
if not (base/'freeze.json').exists():
    user=Path.home()/'AppData/Local/ParisStreetCombat'/current['user_dir']
    write(base/'freeze.json',dict(parent=current,parent_files=rows(source),parent_normal_files=rows(ROOT/current['playable_directory']),mine_user_root=str(user),mine_user_files=rows(user),original_freeze=read(OUT/'freeze.json')))
prepare(a.revision,'candidate_mine_v2')
project=OUT/a.revision/'Project'
assert all(sha(project/r['path'])==r['sha256'] for r in rows(source))
private=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
def edit(p,old,new):
    raw=p.read_bytes();o=old.replace('\n','\r\n').encode();n=new.replace('\n','\r\n').encode()
    assert raw.count(o)==1,(p.name,old[:100],raw.count(o));p.write_bytes(raw.replace(o,n))
for name in ['ParisCombatUI.h','ParisCombatUI.cpp','ParisCombatUIProbe.h','ParisCombatUIProbe.cpp']:
    p=ROOT/'Tools/Integration/CombatUIV1'/name
    (private/name).write_bytes(p.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
public=private.parent/'Public/ParisBridgeMission.h'
edit(public,'    bool InteractionMenuVisible() const;', '    bool SetCombatUIFullTick(bool Value){const bool Prior=bShouldPerformFullTickWhenPaused;bShouldPerformFullTickWhenPaused=Value;return Prior;}\n    bool InteractionMenuVisible() const;')
interaction=private/'ParisMissionInteraction.cpp'
edit(interaction,'#include "ParisMissionInteraction.h"','#include "ParisMissionInteraction.h"\n#include "ParisCombatUI.h"')
edit(interaction,'void AParisBridgePlayerController::RefreshInteractionMenu() {\n    auto* M=', 'void AParisBridgePlayerController::RefreshInteractionMenu() {\n    if(ParisCombatUI::IsOpen(this)){ParisCombatUI::Refresh(this);return;}\n    auto* M=')
edit(interaction,'bool AParisBridgePlayerController::HandleInteractionInput(const FInputKeyEventArgs& Params) {\n    RefreshInteractionMenu();','bool AParisBridgePlayerController::HandleInteractionInput(const FInputKeyEventArgs& Params) {\n    if(ParisCombatUI::Input(this,Params))return true;\n    RefreshInteractionMenu();')
mission=private/'ParisBridgeMission.cpp'
edit(mission,'#include "ParisBridgeMission.h"','#include "ParisBridgeMission.h"\n#include "ParisCombatUI.h"')
edit(mission,'const float S=FMath::Min(Canvas->SizeX/1920.f,Canvas->SizeY/1080.f);','const float S=FMath::Min(Canvas->SizeX/1920.f,Canvas->SizeY/1080.f)*ParisCombatUI::HudScale();')
edit(mission,'    // The approved composition floats over the real world; no generated scene or cards.','    if(ParisCombatUI::DrawMenu(this,M))return;\n    // The approved composition floats over the real world; no generated scene or cards.')
edit(mission,'    Text(Title,130,67,21,','    if(M->Phase==TEXT("Ready")||M->AllowsPlay()){Title=TEXT("SECURE THE G1 BRIDGEHEAD");Detail=FString::Printf(TEXT("%d / 3 GUARDS ELIMINATED  -  CROSS BRIDGE C"),3-M->LivingDefenders);}\n    Text(Title,130,67,21,')
edit(mission,'        Text(ParisTacticalEquipment::HudInventory(GetWorld()),960,1018,13,Ivory,true,30);','        // Key-labelled finite equipment plates are drawn by the additive UI below.')
edit(mission,'const double MX=Screen.X/(Canvas->SizeX/1920.0),MY=Screen.Y/(Canvas->SizeY/1080.0);','const double MX=(Screen.X-OX)/S,MY=(Screen.Y-OY)/S;')
edit(mission,'    if(M->CheckpointPromptVisible)\n    {\n        Halo(960,822','    ParisCombatUI::DrawExtras(this,M);\n    if(M->CheckpointPromptVisible)\n    {\n        Halo(960,822')
edit(mission,'        Text(TEXT("MOUSE / UP / DOWN / TAB    ENTER TO SELECT"),960,941,12,Quiet,true);','        Text(TEXT("MOUSE / UP / DOWN / TAB    ENTER TO SELECT"),960,941,12,Quiet,true);\n        Text(TEXT("ESC  MISSION / SQUAD / CONTROLS"),960,969,14,Brass,true);')
module=private/'ParisBridgeMissionV1.cpp'
edit(module,'#include "ParisTacticalEquipment.h"','#include "ParisTacticalEquipment.h"\n#include "ParisCombatUI.h"\n#include "ParisCombatUIProbe.h"')
edit(module,'  ParisTacticalEquipment::Initialize();','  ParisCombatUI::Initialize();\n  ParisCombatUIProbe::Initialize();\n  ParisTacticalEquipment::Initialize();')
edit(module,'void ShutdownModule()override{ParisTacticalEquipment::Shutdown();','void ShutdownModule()override{ParisCombatUIProbe::Shutdown();ParisCombatUI::Shutdown();ParisTacticalEquipment::Shutdown();')
# Existing opt-in regression drivers now use the same explicit confirmation as humans.
for name in ['ParisInteractionProbe.cpp','ParisP1Probe.cpp','ParisBridgeMissionV1.cpp']:
    p=private/name
    if name!='ParisBridgeMissionV1.cpp':edit(p,'#include "ParisBridgeMission.h"','#include "ParisBridgeMission.h"\n#include "ParisCombatUI.h"')
    raw=p.read_bytes();lines=raw.splitlines(keepends=True)
    found=False
    for i,line in enumerate(lines):
        if line.startswith(b'void Tap('):
            assert line.rstrip().endswith(b'}')
            var='P' if name=='ParisInteractionProbe.cpp' else 'PC'
            extra=f'if((K==EKeys::F6||K==EKeys::F9)&&!ParisCombatUI::Confirmation({var}).IsEmpty()){{{var}->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Left,IE_Pressed,1));{var}->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Left,IE_Released,0));{var}->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Enter,IE_Pressed,1));{var}->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Enter,IE_Released,0));}}'
            lines[i]=line.rstrip()[:-1]+extra.encode()+b'}\r\n';found=True
    assert found,name;p.write_bytes(b''.join(lines))
# Equipment fixtures define their Tap in a private include.
checks=private/'ParisEquipmentChecks.inl'
raw=checks.read_bytes()
tap=next(line for line in raw.splitlines() if line.startswith(b'void Tap('))
assert tap.endswith(b'}')
var='PC'
extra=f'if((K==EKeys::F6||K==EKeys::F9)&&!ParisCombatUI::Confirmation({var}).IsEmpty()){{{var}->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Left,IE_Pressed,1));{var}->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Left,IE_Released,0));{var}->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Enter,IE_Pressed,1));{var}->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Enter,IE_Released,0));}}'
checks.write_bytes(raw.replace(tap,tap[:-1]+extra.encode()+b'}'))
interaction_probe=private/'ParisInteractionProbe.cpp'
edit(interaction_probe,'  Image(TEXT("clean_hud"));Key(Controller,EKeys::W,true);Stage(TEXT("leave"));return;', '  Stage(TEXT("ui_clean_after_save"));return;\n }\n if(Step==TEXT("ui_clean_after_save") && Age>.2){\n  if(!Check(!ParisCombatUI::Inspect(Controller)->GetStringField(TEXT("tutorial")).Contains(TEXT("confirm saving")),TEXT("saved_ack_clears_new_first_use_save_guidance")))return;\n  Image(TEXT("clean_hud"));Key(Controller,EKeys::W,true);Stage(TEXT("leave"));return;')
cpp=private/'ParisTacticalEquipment.cpp'
edit(cpp,'#include "ParisTacticalEquipment.h"','#include "ParisTacticalEquipment.h"\n#include "ParisCombatUI.h"')
write(OUT/a.revision/'ui-authoring.json',dict(status='new_independent_ui',parent='candidate_mine_v2',implementation='Docs/Development/MissionLoopV1/COMBAT_UI_IMPLEMENTATION_20261011_ZH.md',normal_guards='unchanged weapons/save/reflection/native models and assets',new_ui='four pages, true pause, explicit confirmation, equipment and help'))
print('Independent UI candidate authored:',project)
