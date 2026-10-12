from pathlib import Path
import re
root=Path(__file__).resolve().parents[3]
p=root/'tmp/g1-tactical-equipment-20261010/candidate_equipment_wheel_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
def edit(name,fn):
    f=p/name;t=f.read_text('utf-8');f.write_text(fn(t),encoding='utf-8')
def replace_function(t,signature,new):
    start=t.index(signature);a=t.index('{',start);depth=1;i=a+1
    while depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
    return t[:start]+new+t[i:]
edit('ParisEquipmentState.h',lambda t:t.replace('int32 OriginalAnimMode=0;','int32 SelectedSlot=0; // 0 rifle, 1 frag, 2 smoke; transient, never serialized\n    bool PrimaryHeld=false,SuppressPrimary=false,HadWindowFocus=false;\n    FString SelectedVisualKind;\n    TWeakObjectPtr<AActor> SelectedVisual;\n    int32 OriginalAnimMode=0;'))
edit('ParisTacticalEquipment.cpp',lambda t:t.replace('#include "Engine/World.h"','#include "Engine/World.h"\n#include "Engine/GameViewportClient.h"'))
helper='''
const TCHAR* SlotKind(int32 Slot){return Slot==1?TEXT("Frag"):Slot==2?TEXT("Smoke"):TEXT("Rifle");}
void ClearSelectedVisual(FEquipmentSession& S){if(S.SelectedVisual.IsValid())S.SelectedVisual->Destroy();S.SelectedVisual.Reset();S.SelectedVisualKind.Empty();}
void SelectionTick(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S){
    auto* P=UGameplayStatics::GetPlayerCharacter(W,0);
    if(Dead(P)||(!M->AllowsPlay()&&M->Phase!=TEXT("Won"))){ClearSelectedVisual(S);S.SelectedSlot=0;S.PrimaryHeld=false;return;}
    if(!S.ThrowKind.IsEmpty()){ClearSelectedVisual(S);return;}
    if(S.SelectedSlot==0){ClearSelectedVisual(S);return;}
    auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized")))return;
    HideGun(W,P,true);
    const FString Kind=SlotKind(S.SelectedSlot);
    if(S.SelectedVisualKind!=Kind)ClearSelectedVisual(S);
    if(!S.SelectedVisual.IsValid()){
        S.SelectedVisual=Prop(W,Kind,P->GetActorLocation());S.SelectedVisualKind=Kind;
        if(auto* Pose=Cast<UPoseableMeshComponent>(Obj(D,TEXT("Pose")))){S.SelectedVisual->AttachToComponent(Pose,FAttachmentTransformRules::SnapToTargetNotIncludingScale,TEXT("hand_r"));const FVector Palm=Pose->GetSocketLocation(TEXT("middle_01_r"));const FVector Tips=(Pose->GetSocketLocation(TEXT("middle_03_r"))+Pose->GetSocketLocation(TEXT("ring_03_r")))*.5;const FVector Center=(Palm+Tips)*.5;S.SelectedVisual->SetActorRelativeLocation(Pose->GetSocketTransform(TEXT("hand_r")).InverseTransformPosition(Center));}
    }
}
'''
edit('ParisTacticalEquipment.cpp',lambda t:t.replace('void EndThrow(',helper+'void EndThrow(',1).replace('HideGun(W,P,Died);','if(S.ThrowStage==TEXT("Release"))S.SelectedSlot=0;HideGun(W,P,Died||S.SelectedSlot!=0);',1).replace('S.OriginalAnimMode=P->GetMesh()->GetAnimationMode();','ClearSelectedVisual(S);S.OriginalAnimMode=P->GetMesh()->GetAnimationMode();',1))
newinput='''bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& Params){
    auto* M=AParisBridgeMission::Find(PC);if(!M||(!M->AllowsPlay()&&M->Phase!=TEXT("Won")))return false;auto* W=PC->GetWorld();auto& S=Session(W);
    const bool Primary=Params.Key==EKeys::LeftMouseButton;
    if(Primary){if(Params.Event==IE_Pressed)S.PrimaryHeld=true;else if(Params.Event==IE_Released){S.PrimaryHeld=false;if(S.SuppressPrimary){S.SuppressPrimary=false;return true;}}}
    if(Params.Key==EKeys::E&&M->InsideCheckpoint()){if(!S.ThrowKind.IsEmpty()){S.SelectedSlot=0;S.SuppressPrimary=S.PrimaryHeld;EndThrow(W,S);}S.EHeld=false;S.DisarmClock=0;return false;}
    int32 Wheel=0;
    if(Params.Event==IE_Pressed){if(Params.Key==EKeys::MouseScrollDown)Wheel=1;else if(Params.Key==EKeys::MouseScrollUp)Wheel=-1;}
    if(Params.Key==EKeys::MouseWheelAxis&&Params.Event==IE_Axis&&Params.AmountDepressed!=0)Wheel=Params.AmountDepressed>0?-1:1;
    if(Wheel){
        if(S.ThrowStage==TEXT("Release")||S.ThrowCommitted)return true;
        auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(S.ThrowKind.IsEmpty()&&Name(P,TEXT("ActionState"))!=TEXT("Ready"))return true;
        S.EHeld=false;S.DisarmClock=0;S.InteractId.Empty();
        if(S.PrimaryHeld){S.SuppressPrimary=true;PC->APlayerController::InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,IE_Released,0));}
        PC->APlayerController::InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::RightMouseButton,IE_Released,0));
        S.SelectedSlot=(S.SelectedSlot+Wheel+3)%3;ClearSelectedVisual(S);
        if(!S.ThrowKind.IsEmpty()&&S.ThrowStage!=TEXT("Cancel")){S.ReleaseQueued=false;PlayThrow(W,S,TEXT("Cancel"));}
        HideGun(W,P,S.SelectedSlot!=0||!S.ThrowKind.IsEmpty());Event(W,TEXT("select"),SlotKind(S.SelectedSlot));return true;
    }
    if(Params.Key==EKeys::MouseScrollDown||Params.Key==EKeys::MouseScrollUp||Params.Key==EKeys::MouseWheelAxis)return true;
    if(S.EHeld){if(Params.Key==EKeys::Escape&&Params.Event==IE_Pressed){S.EHeld=false;S.DisarmClock=0;S.InteractId.Empty();Notice(W,TEXT("DISARM CANCELLED"));return true;}if(Primary||Params.Key==EKeys::R)return true;}
    if(!S.ThrowKind.IsEmpty()){
        if(Primary&&Params.Event==IE_Released&&(S.ThrowStage==TEXT("Start")||S.ThrowStage==TEXT("Hold")))S.ReleaseQueued=true;
        if(Params.Key==EKeys::Escape&&Params.Event==IE_Pressed){if(S.ThrowStage==TEXT("Start")||S.ThrowStage==TEXT("Hold")){S.ReleaseQueued=false;S.SelectedSlot=0;S.SuppressPrimary=S.PrimaryHeld;PlayThrow(W,S,TEXT("Cancel"));}return true;}
        if(Primary||Params.Key==EKeys::RightMouseButton||Params.Key==EKeys::R||Params.Key==EKeys::E)return true;
    }
    if(Primary){if(S.SuppressPrimary)return true;if(S.SelectedSlot!=0){if(Params.Event==IE_Pressed){S.EHeld=false;S.DisarmClock=0;S.InteractId.Empty();BeginThrow(W,SlotKind(S.SelectedSlot));}return true;}}
    if(S.SelectedSlot!=0&&(Params.Key==EKeys::R||Params.Key==EKeys::RightMouseButton))return true;
    // Old direct throw keys are retired. Rifle primary input still reaches its original binding.
    if(Params.Key==EKeys::G||Params.Key==EKeys::Q)return true;
    return WorldInput(W,S,Params);
}'''
edit('ParisTacticalEquipment.cpp',lambda t:replace_function(t,'bool Input(AParisBridgePlayerController* PC',newinput))
edit('ParisTacticalEquipment.cpp',lambda t:t.replace('ThrowTick(W,S,DT);BallTick(W,S,DT);','ThrowTick(W,S,DT);SelectionTick(W,M,S);\n    if(auto* Viewport=W->GetGameViewport()){const bool Focus=Viewport->Viewport&&Viewport->Viewport->HasFocus();if(S.HadWindowFocus&&!Focus&&!S.ThrowKind.IsEmpty()&&(S.ThrowStage==TEXT("Start")||S.ThrowStage==TEXT("Hold"))){S.SelectedSlot=0;S.ReleaseQueued=false;S.SuppressPrimary=true;S.PrimaryHeld=false;PlayThrow(W,S,TEXT("Cancel"));}S.HadWindowFocus=Focus;}\n    BallTick(W,S,DT);',1).replace('void ClearVisuals(FEquipmentSession& S){','void ClearVisuals(FEquipmentSession& S){ClearSelectedVisual(S);S.SelectedSlot=0;S.PrimaryHeld=false;S.SuppressPrimary=false;',1))
edit('ParisTacticalEquipment.cpp',lambda t:replace_function(t,'FString HudInventory(UWorld* W)', '''FString HudInventory(UWorld* W){auto& S=Session(W);return FString::Printf(TEXT("WHEEL  [%s]  FRAG %d  SMOKE %d"),SlotKind(S.SelectedSlot),S.Frag,S.Smoke);}''').replace('FString::Printf(TEXT("RELEASE %s TO THROW  /  ESC CANCEL"),S.ThrowKind==TEXT("Frag")?TEXT("G"):TEXT("Q"))','FString(TEXT("RELEASE LEFT MOUSE TO THROW  /  ESC CANCEL"))'))
edit('ParisTacticalEquipment.cpp',lambda t:t.replace('return FString();}\nfloat HudProgress','if(S.SelectedSlot!=0)return (S.SelectedSlot==1?S.Frag:S.Smoke)>0?TEXT("HOLD LEFT MOUSE TO PREPARE  /  RELEASE TO THROW"):TEXT("NO GRENADES REMAIN  /  WHEEL TO SWITCH");return FString();}\nfloat HudProgress',1))
edit('ParisCombatUI.cpp',lambda t:t.replace('{{TEXT("G"),TEXT("Frag grenade"),TEXT("Hold to prepare; release to throw")},{TEXT("Q"),TEXT("Smoke grenade"),TEXT("Hold to prepare; release to throw")},{TEXT("ESC"),TEXT("Cancel preparation"),TEXT("Cancel before release without spending equipment")}}','{{TEXT("WHEEL"),TEXT("Select equipment"),TEXT("Cycle rifle, frag and smoke; up reverses the order")},{TEXT("LEFT MOUSE"),TEXT("Prepare / throw"),TEXT("Hold to pull pin; release to throw selected grenade")},{TEXT("ESC / WHEEL"),TEXT("Cancel preparation"),TEXT("Before release: cancel without spending; press again to use")}}').replace('TEXT("Hold G / Q to prepare. Release to throw; ESC cancels before release.")','TEXT("Hold left mouse to prepare. Release to throw; ESC cancels before release.")'))
hud='''for(int32 I=0;I<3;++I){const double X=765+I*180;const bool Selected=E.SelectedSlot==I;const int32 Count=I==1?E.Frag:E.Smoke;const auto C=Selected?Ivory:Muted;P.Line(X+8,1049,X+162,1049,Selected?Brass:Muted,Selected?3:1);if(Selected)P.Text(TEXT("SELECTED"),X+20,950,14,Brass);P.Key(I==0?TEXT("1"):I==1?TEXT("2"):TEXT("3"),X+10,991,35);if(I==0){P.Line(X+57,1007,X+92,1007,C,3);P.Line(X+61,1007,X+56,1014,C,3);}else {P.Circle(X+75,1009,12,C);P.Line(X+68,993,X+81,993,C,2);P.Line(X+79,993,X+88,1000,C,2);}P.Text(I==0?TEXT("RIFLE"):I==1?TEXT("FRAG"):TEXT("SMOKE"),X+53,980,18,C);if(I)P.Text(FString::FromInt(Count),X+112,1008,27,Count?C:Muted);}P.Text(TEXT("MOUSE WHEEL TO SWITCH"),811,1060,14,Muted);'''
# Numbers label slots, not keyboard shortcuts. Use a neutral dot instead of misleading keys.
hud=hud.replace('P.Key(I==0?TEXT("1"):I==1?TEXT("2"):TEXT("3"),X+10,991,35);','P.Circle(X+27,1009,5,Selected?Brass:Muted);')
edit('ParisCombatUI.cpp',lambda t: t[:t.index(' for(int32 I=0;I<2;++I){const double X=815')]+ '\n '+hud+'\n'+t[t.index(' FString Category,Copy;'):])
edit('ParisCombatUI.cpp',lambda t:t.replace('if(U.TutorialCategory==TEXT("save")&&!M->CheckpointPromptVisible)','if((U.TutorialCategory==TEXT("save")&&!M->CheckpointPromptVisible)||(U.TutorialCategory==TEXT("throw")&&(E.ThrowKind.IsEmpty()||E.ThrowStage==TEXT("Cancel")||E.ThrowStage==TEXT("Release"))))'))
# Adapt old probe aliases to real wheel + primary presses. These are opt-in only.
adapter='''void CheckEquipmentKey(AParisBridgePlayerController* PC,FKey K,bool Down){if(Down){auto& E=Session(PC->GetWorld());const int32 Slot=K==EKeys::G?1:2;for(int32 I=0;I<3&&E.SelectedSlot!=Slot;++I){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseScrollDown,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseScrollDown,IE_Released,0));}}PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,Down?IE_Pressed:IE_Released,Down?1:0));}
'''
edit('ParisEquipmentChecks.inl',lambda t:t.replace('void Tap(AParisBridgePlayerController* PC,FKey K){',''+adapter+'void Tap(AParisBridgePlayerController* PC,FKey K){if(K==EKeys::G||K==EKeys::Q){CheckEquipmentKey(PC,K,true);CheckEquipmentKey(PC,K,false);return;}',1).replace('finite_inventory_and_active_effects_restore','finite_inventory_and_active_effects_restore').replace('M->SaveSerial>=1&&M->LivingDefenders==0&&M->CheckpointUnlocked()&&S.Restored','M->SaveSerial>=1&&M->LivingDefenders==0&&M->CheckpointUnlocked()&&S.Restored&&S.SelectedSlot==0'))
edit('ParisTacticalEquipment.cpp',lambda t:re.sub(r'PC->InputKey\(FInputKeyEventArgs::CreateSimulated\(EKeys::([GQ]),IE_(Pressed|Released),[10]\)\)',lambda m:'CheckEquipmentKey(PC,EKeys::'+m[1]+','+('true' if m[2]=='Pressed' else 'false')+')',t).replace('original fixed attachment and animations, G/Q prepare/cancel','original fixed attachment and animations, wheel/primary prepare/cancel'))
# Original throw probe cancelled a held key but never released it. New control explicitly releases.
edit('ParisTacticalEquipment.cpp',lambda t:t.replace('CheckStep==6&&CheckClock>1.4){Picture','CheckStep==6&&CheckClock>1.4){CheckEquipmentKey(PC,EKeys::G,false);Picture',1))
uiadapter='''void Key(APlayerController* PC,FKey K,bool Down){if(K==EKeys::G||K==EKeys::Q){if(Down){auto& E=ParisTacticalEquipment::Session(PC->GetWorld());for(int32 I=0;I<3&&E.SelectedSlot!=(K==EKeys::G?1:2);++I){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseScrollDown,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseScrollDown,IE_Released,0));}}K=EKeys::LeftMouseButton;}PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1.f:0.f));}'''
edit('ParisCombatUIProbe.cpp',lambda t:replace_function(t,'void Key(APlayerController* PC',uiadapter).replace('real G/Q preparation','real wheel/primary preparation'))
edit('ParisPlayerDeathProbe.inl',lambda t:replace_function(t,'void Tap(APlayerController* PC,FKey K)', '''void Tap(APlayerController* PC,FKey K){if(K==EKeys::G||K==EKeys::Q){auto& E=ParisTacticalEquipment::Session(PC->GetWorld());for(int32 I=0;I<3&&E.SelectedSlot!=(K==EKeys::G?1:2);++I){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseScrollDown,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseScrollDown,IE_Released,0));}K=EKeys::LeftMouseButton;}PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Released,0));}'''))
print('Authored isolated equipment controls')
