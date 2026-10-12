"""Optional isolated photo fixture; never active in the normal launcher."""
from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'tmp/g1-tactical-equipment-20261010/candidate_grenade_models_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisTacticalEquipment.cpp'
text=p.read_text('utf-8');assert 'void GrenadeModelCheck(' not in text
fixture='''
void GrenadeModelCheck(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S,AParisBridgePlayerController* PC,ACharacter* P,float DT){
    CheckClock+=DT;
    if(CheckStep==0){if(M->Phase!=TEXT("Ready"))return;auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized"))){if(CheckClock>20)FinishCheck(W,false,TEXT("formal_FP_timeout"));return;}
        M->StartMission();HoldBrains(W);PC->SetControlRotation(FRotator(-5,0,0));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::G,IE_Pressed,1));CheckStep=1;CheckClock=0;return;}
    if(CheckStep==1&&S.ThrowStage==TEXT("Hold")&&CheckClock>1.2){Picture(TEXT("frag_held.png"));CheckStep=2;CheckClock=0;}
    else if(CheckStep==2&&CheckClock>.3){Tap(PC,EKeys::Escape);PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::G,IE_Released,0));CheckStep=3;CheckClock=0;}
    else if(CheckStep==3&&S.ThrowKind.IsEmpty()&&CheckClock>1.1){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Q,IE_Pressed,1));CheckStep=4;CheckClock=0;}
    else if(CheckStep==4&&S.ThrowStage==TEXT("Hold")&&CheckClock>1.2){Picture(TEXT("smoke_held.png"));CheckStep=5;CheckClock=0;}
    else if(CheckStep==5&&CheckClock>.3){Tap(PC,EKeys::Escape);PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Q,IE_Released,0));CheckStep=6;CheckClock=0;}
    else if(CheckStep==6&&S.ThrowKind.IsEmpty()&&CheckClock>1.1){
        const FVector Feet=P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
        FVector At;const FVector Forward=PC->GetControlRotation().Vector().GetSafeNormal2D();
        if(!Site(W,Feet+Forward*125,At)){FinishCheck(W,false,TEXT("ground_photo_native_admission"));return;}
        Prop(W,TEXT("Frag"),At+FVector(0,-10,6.0));Prop(W,TEXT("Smoke"),At+FVector(0,10,6.25));
        AimPoint(PC,At+FVector(0,0,3));Event(W,TEXT("fixture"),TEXT("two exterior display-only props on native ground; no gameplay ball/timer/actor damage"));CheckStep=7;CheckClock=0;
    }else if(CheckStep==7&&CheckClock>1.0){Picture(TEXT("ground_models.png"));CheckStep=8;CheckClock=0;}
    else if(CheckStep==8&&CheckClock>.3){FinishCheck(W,S.Frag==2&&S.Smoke==2&&S.FragThrown==0&&S.SmokeThrown==0&&S.ThrowKind.IsEmpty(),TEXT("original fixed attachment and animations, G/Q prepare/cancel without spend; ground exterior fixture"));}
    if(CheckClock>30)FinishCheck(W,false,TEXT("model_photo_timeout"));
}
'''
pos=text.index('void Check(UWorld*');text=text[:pos]+fixture+text[pos:]
needle='    if(CheckMode!=TEXT("throw"))'
text=text.replace(needle,'    if(CheckMode==TEXT("models")){GrenadeModelCheck(W,M,S,PC,P,DT);return;}\n'+needle)
p.write_text(text,encoding='utf-8')
