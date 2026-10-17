#include "ParisTutorial.h"
#include "ParisTutorialSoundscape.h"
#include "ParisMedicalKits.h"
#include "ParisBridgeMission.h"
#include "ParisEquipmentState.h"
#include "ParisTacticalEquipment.h"
#include "ParisCombatUI.h"
#include "AIController.h"
#include "BrainComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/BoxComponent.h"
#include "Camera/CameraActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerInput.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"
#include "Perception/PawnSensingComponent.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"

bool ParisProneStrafeCheck(ACharacter* Player,FVector Delta,bool& BodyClear,bool& Supported);
bool ParisProneFutureBlocked(const ACharacter* Player);
bool ParisProneTurnBlocked(const ACharacter* Player);

namespace ParisTutorial {
namespace {
enum EStep {Before=0,Look,Walk,Run,Jump,Crouch,Crawl,Stand,Fire,Reload,Frag,Smoke,Supply,Disarm,Recruit,CP0,Combat,CP1,Complete};
constexpr int BasicMask=(1<<13)-1;
const FVector StartFeet(91.186979,-22140.678907,98.089),WalkFeet(-1200,-22700,97.280),RunFeet(390,-21875,97.283);
const FVector CrawlStart(-152.397309,-22340.170222,97.169),CrawlEnd(153.216635,-22159.461553,98.853);
const FVector ThrowFeet(-1200,-22700,97.280),SupplyFeet(500,-21875,97.283),MineFeet(800,-21675,99.442);
const FVector AllyFeet[2]={FVector(850,-21475,109.228),FVector(900,-21200,97.561)};
const FVector CP0Feet(1200,-21400,100.802),PracticeFeet(-500,-22350,109.228);
struct FState {
    bool Configured=false,Joined[2]={false,false},History[2]={false,false};
    bool Skipped=false,CombatOpen=false,Done=false,CP0Saved=false;
    bool JumpAir=false,CrawlArmed=false,ERelease=false,SwallowClick=false;
    int Stage=Before,Mask=0,Dialog=-1,Choice=1;
    double StageAt=0,NextFollow=0,CrawlDistance=0,RunDistance=0,CrouchClock=0;
    double CrawlAxisTravel[4]={0,0,0,0};
    int ShotStart=0,FragStart=0,SmokeStart=0;
    FVector PreviousFeet=FVector::ZeroVector;FRotator LookStart=FRotator::ZeroRotator;
};
TMap<UWorld*,FState> States;
FDelegateHandle Cleanup;
double Num(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!P)return -1;const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):P->GetSignedIntPropertyValue(V);}
bool Flag(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),K):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
FName Name(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr;return P?P->GetPropertyValue_InContainer(O):NAME_None;}
void PutNum(UObject* O,const TCHAR* K,double Value){auto* P=FindFProperty<FNumericProperty>(O->GetClass(),K);check(P);void* V=P->ContainerPtrToValuePtr<void>(O);if(P->IsFloatingPoint())P->SetFloatingPointPropertyValue(V,Value);else P->SetIntPropertyValue(V,int64(Value));}
bool Dead(const ACharacter* C){return !IsValid(C)||Flag(C,TEXT("IsDead"))||Num(C,TEXT("Health"))<=0;}
ACharacter* Pawn(UWorld* W,const TCHAR* Id){const FName Tag(*(FString(TEXT("G1_"))+Id));for(TActorIterator<ACharacter>I(W);I;++I)if(I->ActorHasTag(Tag))return *I;return nullptr;}
FState& State(const AParisBridgeMission* M){
    if(!Cleanup.IsValid())Cleanup=FWorldDelegates::OnWorldCleanup.AddLambda([](UWorld* W,bool,bool){States.Remove(W);ClearWorld(W);});
    return States.FindOrAdd(M->GetWorld());
}
void Log(AParisBridgeMission* M,const TCHAR* Event){const auto& S=State(M);UE_LOG(LogTemp,Display,TEXT("PARIS_TUTORIAL_EVENT event=%s stage=%d mask=%d joined=%d%d history=%d%d combat=%d cp0_saved=%d"),Event,S.Stage,S.Mask,S.Joined[0],S.Joined[1],S.History[0],S.History[1],S.CombatOpen,S.CP0Saved);}
void Family(UWorld* W,ACharacter* C,bool Visible,bool Collision){
    if(!IsValid(C))return;C->SetActorHiddenInGame(!Visible);if(Dead(C))return;
    if(!Collision&&C->GetActorEnableCollision())C->GetCharacterMovement()->DisableMovement();
    if(Collision&&!C->GetActorEnableCollision())C->GetCharacterMovement()->SetMovementMode(MOVE_Walking);
    C->SetActorEnableCollision(Collision);
    TArray<UPawnSensingComponent*> Sensors;C->GetComponents(Sensors);
    auto* M=AParisBridgeMission::Find(C);for(auto* Sensor:Sensors)Sensor->SetSensingUpdatesEnabled(Collision&&M&&State(M).CombatOpen);
    for(TActorIterator<AActor>I(W);I;++I)if(*I!=C){
        bool Related=I->GetOwner()==C||I->IsAttachedTo(C);
        if(auto* P=FindFProperty<FObjectPropertyBase>(I->GetClass(),TEXT("Combatant")))Related|=P->GetObjectPropertyValue_InContainer(*I)==C;
        if(Related)I->SetActorHiddenInGame(!Visible);
    }
}
void Visibility(AParisBridgeMission* M){
    auto& S=State(M);UWorld* W=M->GetWorld();
    for(int I=0;I<2;++I)Family(W,Pawn(W,I==0?TEXT("Ally1"):TEXT("Ally2")),S.Stage>=Recruit||S.Joined[I],S.Stage>=Recruit);
    for(const TCHAR* Id:{TEXT("German1"),TEXT("German2"),TEXT("German3")})Family(W,Pawn(W,Id),S.CombatOpen,S.CombatOpen);
    auto& E=ParisTacticalEquipment::Session(W);
    if(E.Traps.Num()==3){
        for(int I=0;I<2;++I)if(S.CombatOpen&&E.Traps[I].State==TEXT("Dormant"))E.Traps[I].State=TEXT("Armed");
        if(S.Stage==Disarm&&E.Traps[2].State==TEXT("Dormant"))E.Traps[2].State=TEXT("Armed");
        for(auto& T:E.Traps)if(T.Visual.IsValid())T.Visual->SetActorHiddenInGame(T.State!=TEXT("Armed"));
    }
}
void Stage(AParisBridgeMission* M,int Value){
    auto& S=State(M);auto* P=Pawn(M->GetWorld(),TEXT("Player"));auto& E=ParisTacticalEquipment::Session(M->GetWorld());
    if(S.Stage>Before&&S.Stage<=Disarm)S.Mask|=1<<(S.Stage-1);
    S.Stage=Value;S.StageAt=M->GetWorld()->GetTimeSeconds();S.PreviousFeet=P->GetNavAgentLocation();
    S.ShotStart=int(Num(P,TEXT("ShotSequence")));S.FragStart=E.FragThrown;S.SmokeStart=E.SmokeThrown;
    S.JumpAir=false;S.CrawlArmed=false;S.CrawlDistance=S.RunDistance=S.CrouchClock=0;for(double& V:S.CrawlAxisTravel)V=0;
    if(auto* PC=UGameplayStatics::GetPlayerController(M,0))S.LookStart=PC->GetControlRotation();
    Visibility(M);Log(M,TEXT("stage_enter"));
}
bool Facing(APlayerController* PC,ACharacter* C){
    if(Dead(C)||FVector::Dist2D(PC->GetPawn()->GetActorLocation(),C->GetActorLocation())>220)return false;
    FVector Eye;FRotator R;PC->GetPlayerViewPoint(Eye,R);const FVector Target=C->GetActorLocation()+FVector(0,0,30);
    return FVector::DotProduct(R.Vector(),(Target-Eye).GetSafeNormal())>=.65&&PC->LineOfSightTo(C);
}
void Follow(AParisBridgeMission* M){
    auto& S=State(M);double Now=M->GetWorld()->GetTimeSeconds();if(S.CombatOpen&&M->Phase!=TEXT("Won")||Now<S.NextFollow)return;S.NextFollow=Now+.8;
    auto* P=Pawn(M->GetWorld(),TEXT("Player"));auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(M->GetWorld());if(!Nav||Dead(P))return;
    for(int I=0;I<2;++I)if(S.Joined[I]){auto* C=Pawn(M->GetWorld(),I==0?TEXT("Ally1"):TEXT("Ally2"));auto* A=C?Cast<AAIController>(C->GetController()):nullptr;if(Dead(C)||!A)continue;
        if(!Flag(A,TEXT("SquadEnabled"))){auto* F=A->FindFunction(TEXT("PC_EnableCombat"));if(F){FStructOnScope Args(F);if(auto* B=FindFProperty<FBoolProperty>(F,TEXT("Enabled")))B->SetPropertyValue_InContainer(Args.GetStructMemory(),true);A->ProcessEvent(F,Args.GetStructMemory());}if(A->GetBrainComponent())A->GetBrainComponent()->StopLogic(TEXT("Tutorial noncombat follow; no combat tree"));}
        FVector Want=P->GetNavAgentLocation()+FVector(-200,I==0?-110:110,0);FNavLocation N;
        if(Nav->ProjectPointToNavigation(Want,N,FVector(40,40,150))){auto* Path=UNavigationSystemV1::FindPathToLocationSynchronously(M->GetWorld(),C->GetNavAgentLocation(),N.Location,C);if(Path&&Path->IsValid()&&!Path->IsPartial())A->MoveToLocation(N.Location,55,true,true,true,false,nullptr,false);}
    }
}
}
FVector PlayerStartFeet(){return StartFeet;}
bool HasGuidanceGoal(const AParisBridgeMission* M){
    const int S=State(M).Stage;
    if(S==Jump||S==Crouch||S==Crawl||S==Stand||S==Fire||S==Reload)return false;
    if(S==Frag||S==Smoke){const auto& E=ParisTacticalEquipment::Session(M->GetWorld());return (S==Frag&&E.Frag==0||S==Smoke&&E.Smoke==0)&&E.ThrowKind.IsEmpty()&&E.Balls.IsEmpty();}
    return S>=Walk&&S!=Stand;
}
void SetInitialBudget(ACharacter* P){PutNum(P,TEXT("LoadedAmmo"),4);PutNum(P,TEXT("ReserveAmmo"),8);}
void ConfigureReady(AParisBridgeMission* M){
    if(!Enabled())return;auto& S=State(M);if(S.Configured)return;S.Configured=true;S.StageAt=M->GetWorld()->GetTimeSeconds();
    M->LivingAllies=0;Visibility(M);Log(M,TEXT("configured"));
}
bool StartTraining(AParisBridgeMission* M){
    if(!Enabled()||M->Phase!=TEXT("Ready"))return false;ConfigureReady(M);M->Phase=TEXT("Training");
    if(auto* PC=UGameplayStatics::GetPlayerController(M,0)){PC->ResetIgnoreMoveInput();PC->ResetIgnoreLookInput();}
    Stage(M,Look);M->Feedback=TEXT("Basic training. Follow one instruction at a time. Esc pauses and releases the cursor.");return true;
}
bool CombatStarted(const AParisBridgeMission* M){return Enabled()&&State(M).CombatOpen;}
void OpenCombat(AParisBridgeMission* M){auto& S=State(M);S.CombatOpen=true;Stage(M,Combat);Visibility(M);}
bool BrainAllowed(const ACharacter* C){
    if(!Enabled())return true;auto* M=AParisBridgeMission::Find(C);if(!M)return true;auto& S=State(M);
    if(C->ActorHasTag(TEXT("G1_Ally1")))return S.CombatOpen&&S.Joined[0];
    if(C->ActorHasTag(TEXT("G1_Ally2")))return S.CombatOpen&&S.Joined[1];return S.CombatOpen;
}
bool CombatantActive(const ACharacter* C){
    if(!Enabled())return true;auto* M=AParisBridgeMission::Find(C);if(!M)return true;const auto& S=State(M);
    if(C->ActorHasTag(TEXT("G1_German1"))||C->ActorHasTag(TEXT("G1_German2"))||C->ActorHasTag(TEXT("G1_German3")))return S.CombatOpen;
    if(C->ActorHasTag(TEXT("G1_Ally1"))||C->ActorHasTag(TEXT("G1_Ally2")))return S.Stage>=Recruit;
    return true;
}
int Step(const AParisBridgeMission* M){return State(M).Stage;}
int JoinedCount(const AParisBridgeMission* M){auto& S=State(M);return int(S.Joined[0]&&!Dead(Pawn(M->GetWorld(),TEXT("Ally1"))))+int(S.Joined[1]&&!Dead(Pawn(M->GetWorld(),TEXT("Ally2"))));}
bool TrainingCheckpoint(const AParisBridgeMission* M){return Enabled()&&State(M).Stage==CP0&&!State(M).CombatOpen;}
bool TrainingCheckpointSaved(const AParisBridgeMission* M){return TrainingCheckpoint(M)&&State(M).CP0Saved;}
bool TrainingCheckpointUnlocked(const AParisBridgeMission* M){const auto& S=State(M);return TrainingCheckpoint(M)&&S.Mask==BasicMask&&(S.History[0]&&S.History[1]||S.Skipped);}
bool ForwardDeparture(const AParisBridgeMission* M){
 const auto& S=State(M);if(!TrainingCheckpointUnlocked(M)||!S.CP0Saved||S.Dialog!=-1||M->CheckpointDialogVisible())return false;
 auto* P=Pawn(M->GetWorld(),TEXT("Player"));if(Dead(P)||!P->GetCharacterMovement()->IsMovingOnGround())return false;
 const FVector Delta=P->GetNavAgentLocation()-CP0Feet,Forward=(M->FarBankFeet-CP0Feet).GetSafeNormal2D();
 return Delta.Size2D()>M->CheckpointRadius+40&&FVector::DotProduct(Delta,Forward)>100&&FMath::Abs(Delta.Z)<100;
}
FVector CheckpointFeet(const AParisBridgeMission* M){return TrainingCheckpoint(M)?CP0Feet:M->BridgeheadFeet;}
bool DialogVisible(const AParisBridgeMission* M){return Enabled()&&State(M).Dialog!=-1;}
int DialogChoice(const AParisBridgeMission* M){return State(M).Choice;}
FString DialogName(const AParisBridgeMission* M){int D=State(M).Dialog;return D>=0?FString::Printf(TEXT("RECRUIT ALLY %d"),D+1):D==-2?TEXT("CONTINUE WITHOUT SAVING?"):TEXT("CONTINUE SOLO?");}
bool LargePrompt(const AParisBridgeMission* M){return Enabled()&&State(M).Stage>Before&&M->GetWorld()->GetTimeSeconds()-State(M).StageAt<4;}
FVector Goal(const AParisBridgeMission* M){
    const auto& S=State(M);const auto& E=ParisTacticalEquipment::Session(M->GetWorld());
    if((S.Stage==Frag&&E.Frag==0||S.Stage==Smoke&&E.Smoke==0)&&E.ThrowKind.IsEmpty()&&E.Balls.IsEmpty())return SupplyFeet+FVector(-110,0,0);
    switch(S.Stage){case Before:case Look:return StartFeet;case Walk:return WalkFeet;case Run:case Jump:case Crouch:return RunFeet;case Crawl:return S.CrawlArmed?Pawn(M->GetWorld(),TEXT("Player"))->GetNavAgentLocation():CrawlStart;case Stand:return Pawn(M->GetWorld(),TEXT("Player"))->GetNavAgentLocation();case Fire:case Reload:return ThrowFeet;case Frag:case Smoke:return ThrowFeet;case Supply:return SupplyFeet+FVector(-110,0,0);case Disarm:return MineFeet+FVector(0,-170,0);case Recruit:return !S.History[0]&&!Dead(Pawn(M->GetWorld(),TEXT("Ally1")))?AllyFeet[0]:AllyFeet[1];case CP0:return S.CP0Saved?M->FarBankFeet:CP0Feet;case Combat:return M->FarBankFeet;default:return M->BridgeheadFeet;}
}
FString Heading(const AParisBridgeMission* M){
    if(TrainingCheckpointSaved(M))return TEXT("BASIC TRAINING SAVED");
    if(State(M).Stage==Crawl)return TEXT("PRACTISE PRONE MOVEMENT");
    const TCHAR* Titles[]={TEXT("BASIC TRAINING"),TEXT("LOOK AROUND"),TEXT("WALK TO THE MARKER"),TEXT("RUN TO THE MARKER"),TEXT("JUMP AND LAND"),TEXT("CROUCH"),TEXT("CRAWL ALONG THE ROAD"),TEXT("STAND UP"),TEXT("FIRE TWO ROUNDS"),TEXT("RELOAD YOUR RIFLE"),TEXT("THROW A FRAG GRENADE"),TEXT("THROW A SMOKE GRENADE"),TEXT("RESUPPLY YOUR EQUIPMENT"),TEXT("DISARM THE TRAINING MINE"),TEXT("RECRUIT YOUR TWO ALLIES"),TEXT("TRAINING CHECKPOINT"),TEXT("SECURE THE BRIDGEHEAD"),TEXT("SAVE AT THE BRIDGEHEAD"),TEXT("BEGINNER MISSION COMPLETE")};return Titles[FMath::Clamp(State(M).Stage,0,int(Complete))];
}
FString KeyHint(const AParisBridgeMission* M){return HudInstruction(M);}
FString Guidance(const AParisBridgeMission* M){
    const auto& S=State(M);const auto& E=ParisTacticalEquipment::Session(M->GetWorld());
    if(S.Stage==Look)return TEXT("Move the mouse left or right to turn your view.");
    if(S.Stage==Walk)return TEXT("Walk to the road marker. The distance display shows how far remains.");
    if(S.Stage==Run)return TEXT("Hold Shift to run at least 12 metres in total, then reach the marker.");
    if(S.Stage==Crouch)return TEXT("Press Ctrl to crouch and wait briefly for the posture to settle.");
    if(S.Stage==Crawl){
        if(!S.CrawlArmed)return TEXT("Press Z on clear, level ground. Crawl in all four WASD directions and cover 2.5 metres in total.");
        return FString::Printf(TEXT("W[%s] S[%s] A[%s] D[%s]  |  %.1f / 2.5 m  |  Move each direction, then this lesson advances automatically."),S.CrawlAxisTravel[0]>=15?TEXT("OK"):TEXT("--"),S.CrawlAxisTravel[1]>=15?TEXT("OK"):TEXT("--"),S.CrawlAxisTravel[2]>=15?TEXT("OK"):TEXT("--"),S.CrawlAxisTravel[3]>=15?TEXT("OK"):TEXT("--"),FMath::Min(2.5,S.CrawlDistance/100));
    }
    if(S.Stage==Recruit){
        if(!S.History[0]&&Dead(Pawn(M->GetWorld(),TEXT("Ally1")))||!S.History[1]&&Dead(Pawn(M->GetWorld(),TEXT("Ally2"))))return TEXT("An unrecruited ally is unavailable. Press E away from other allies to review continuing without them, or F6 to restart.");
        return FString::Printf(TEXT("%d / 2 recruitment lessons complete - talk and confirm Join"),int(S.History[0])+int(S.History[1]));
    }
    if(S.Stage==CP0)return S.CP0Saved?TEXT("Training saved. Walk forward out of the circle towards bridge C to continue; Enter also continues while inside the circle."):TEXT("Inside the gold circle: E saves training; Enter offers continue without saving.");
    if(S.Stage==Combat)return FString::Printf(TEXT("%d / 3 guards eliminated - eliminate all three to unlock the checkpoint"),3-M->LivingDefenders);
    if(S.Stage==Complete)return TEXT("Your bridgehead progress is saved. The beginner mission is complete.");
    if((S.Stage==Frag&&E.Frag==0||S.Stage==Smoke&&E.Smoke==0)&&E.ThrowKind.IsEmpty()&&E.Balls.IsEmpty()&&!(S.Stage==Frag?E.FragThrown>S.FragStart:E.SmokeThrown>S.SmokeStart))return TEXT("Practice stock depleted? Use the resupply teaching box; F6 restarts training if empty.");
    if(S.Stage==Disarm)return E.Traps.Num()==3&&E.Traps[2].State==TEXT("Spent")?TEXT("Training mine destroyed. F6 restarts this training attempt."):TEXT("Stay clear of the mine. Stop within 2 metres, aim at it and hold E for 2 seconds. Releasing E, moving or looking away cancels.");
    if(S.Stage==Frag||S.Stage==Smoke){
        if(S.Stage==Frag&&E.FragThrown>S.FragStart)return TEXT("Grenade thrown. Stay clear and wait for the explosion and throwing action to finish.");
        if(S.Stage==Smoke&&E.SmokeThrown>S.SmokeStart)return TEXT("Smoke grenade thrown. Wait for smoke to appear and the throwing action to finish.");
        return TEXT("Throw into a distant open space. Esc cancels before release. Stay clear of the blast.");
    }
    if(S.Stage==Supply)return TEXT("Aim at the box and press E to take available ammunition and grenades. Receiving at least one item completes this step; the rifle magazine is not reloaded.");
    if(S.Stage==Fire)return TEXT("Select the rifle with the wheel, then fire two shots in any direction.");
    if(S.Stage==Reload)return TEXT("Select the rifle and press R. This step completes when 8 rounds are loaded and the reload has finished. F6 restarts training if ammunition is insufficient.");
    if(S.Stage==Jump)return TEXT("Press Space to jump, then land. No particular location or obstacle is required.");
    if(S.Stage==Stand)return TEXT("Prone movement complete. Press Z to stand, then continue to the shooting lesson.");
    if(S.Stage==CP1)return TEXT("All three guards are eliminated. Enter the gold circle and save successfully to finish the beginner mission.");
    return TEXT("Complete the action at your own pace. Esc opens help and releases the mouse.");
}
#include "ParisTutorialHUD.inl"
bool TickTraining(AParisBridgeMission* M,float DT){
    if(!Enabled())return false;ConfigureReady(M);auto& S=State(M);auto* P=Pawn(M->GetWorld(),TEXT("Player"));
    M->LivingAllies=JoinedCount(M);
    if(S.CombatOpen){if(M->Phase==TEXT("Won")){if(!S.Done&&S.Stage==Combat)Stage(M,CP1);Follow(M);}return false;}
    if(M->Phase!=TEXT("Training")&&M->Phase!=TEXT("TrainingCheckpoint"))return false;
    if(Dead(P)){S.Dialog=-1;M->Phase=TEXT("Lost");M->Feedback=TEXT("Training lost. F9 loads your checkpoint; F6 starts a new training attempt.");return true;}
    auto& E=ParisTacticalEquipment::Session(M->GetWorld());const FVector Feet=P->GetNavAgentLocation();const bool Ground=P->GetCharacterMovement()->IsMovingOnGround();
    const FVector ActualDelta=Feet-S.PreviousFeet;const double Travel=ActualDelta.Size2D();S.PreviousFeet=Feet;
    if(S.Dialog!=-1)return true;
    if(ForwardDeparture(M)){Log(M,TEXT("saved_checkpoint_forward_departure"));return !M->StartTutorialCombat();}
    bool Next=false;
    switch(S.Stage){
    case Look:{auto* PC=UGameplayStatics::GetPlayerController(M,0);Next=PC&&FMath::Abs(FMath::FindDeltaAngleDegrees(S.LookStart.Yaw,PC->GetControlRotation().Yaw))>=12;break;}
    case Walk:Next=Ground&&FVector::Dist2D(Feet,WalkFeet)<75;break;
    case Run:if(Ground&&P->GetVelocity().Size2D()>300)S.RunDistance+=Travel;Next=S.RunDistance>=1200&&FVector::Dist2D(Feet,RunFeet)<90;break;
    case Jump:if(P->GetCharacterMovement()->IsFalling()&&P->GetVelocity().Z>10)S.JumpAir=true;Next=S.JumpAir&&Ground;break;
    case Crouch:if(Ground&&Num(P,TEXT("DesiredPosture"))==1&&P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()<75)S.CrouchClock+=DT;Next=S.CrouchClock>.5;break;
    case Crawl:{
        if(Ground&&Num(P,TEXT("DesiredPosture"))==2&&P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()<35){
            if(!S.CrawlArmed){S.CrawlArmed=true;S.PreviousFeet=Feet;Log(M,TEXT("crawl_started"));}
            else if(Travel>.01&&Travel<40){
                const double Forward=FVector::DotProduct(ActualDelta,P->GetActorForwardVector()),Side=FVector::DotProduct(ActualDelta,P->GetActorRightVector());
                const double F=P->GetInputAxisValue(TEXT("PC_MoveForward")),R=P->GetInputAxisValue(TEXT("PC_MoveRight"));
                if(F>.1&&Forward>0)S.CrawlAxisTravel[0]+=Forward;
                if(F<-.1&&Forward<0)S.CrawlAxisTravel[1]-=Forward;
                if(R<-.1&&Side<0)S.CrawlAxisTravel[2]-=Side;
                if(R>.1&&Side>0)S.CrawlAxisTravel[3]+=Side;
                if(FMath::Abs(F)>.1||FMath::Abs(R)>.1)S.CrawlDistance+=Travel;
            }
        }
        Next=S.CrawlArmed&&S.CrawlDistance>=250;for(double V:S.CrawlAxisTravel)Next&=V>=15;
        if(Next)Log(M,TEXT("crawl_complete_four_directions"));break;
    }
    case Stand:Next=Ground&&Num(P,TEXT("DesiredPosture"))==0&&P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()>90&&Name(P,TEXT("ActionState"))==TEXT("Ready");break;
    case Fire:Next=Num(P,TEXT("ShotSequence"))-S.ShotStart>=2;break;
    case Reload:Next=Num(P,TEXT("LoadedAmmo"))==8&&Name(P,TEXT("ActionState"))==TEXT("Ready");break;
    case Frag:Next=E.FragThrown>S.FragStart&&E.ThrowKind.IsEmpty();for(const auto& B:E.Balls)if(B.Kind==TEXT("Frag"))Next=false;break;
    case Smoke:Next=E.SmokeThrown>S.SmokeStart&&!E.Clouds.IsEmpty()&&E.ThrowKind.IsEmpty();break;
    case Supply:Next=E.SupplyTutorialConfirmed;break;
    case Disarm:Next=E.Traps.Num()==3&&E.Traps[2].State==TEXT("Disarmed");if(E.Traps.Num()==3&&E.Traps[2].State==TEXT("Spent"))M->Feedback=TEXT("Training mine destroyed. F6 restarts this training attempt.");break;
    case Recruit:Next=S.History[0]&&S.History[1]||S.Skipped;break;
    default:break;
    }
    if(Next){Stage(M,S.Stage+1);if(S.Stage==CP0)M->Phase=TEXT("TrainingCheckpoint");}
    Follow(M);
    if(HasGuidanceGoal(M)&&S.Stage<CP0){const FVector At=Goal(M);DrawDebugCircle(M->GetWorld(),At+FVector(0,0,8),55,48,FColor(175,205,151),false,-1,0,1.25,FVector(1,0,0),FVector(0,1,0),false);}
    if(S.Stage==Walk||S.Stage==Run){auto* Path=UNavigationSystemV1::FindPathToLocationSynchronously(M->GetWorld(),Feet,Goal(M),P);if(Path&&Path->IsValid()&&!Path->IsPartial())for(int I=1;I<Path->PathPoints.Num();++I)DrawDebugLine(M->GetWorld(),Path->PathPoints[I-1]+FVector(0,0,8),Path->PathPoints[I]+FVector(0,0,8),FColor(175,205,151),false,-1,0,1.8);}
    return true;
}
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& A){
    auto* M=AParisBridgeMission::Find(PC);if(!Enabled()||!M)return false;auto& S=State(M);
    if(A.Key==EKeys::LeftMouseButton&&S.SwallowClick){if(A.Event==IE_Released)S.SwallowClick=false;return true;}
    if(S.Dialog!=-1){
        if(A.Key==EKeys::E&&A.Event==IE_Released){S.ERelease=true;return true;}
        if(A.Event!=IE_Pressed)return A.Event!=IE_Released;
        if(A.Key==EKeys::Escape){ParisTutorialSoundscape::CancelGreeting(M,S.Dialog);S.Dialog=-1;Log(M,TEXT("dialog_cancel"));return true;}
        if(A.Key==EKeys::Left||A.Key==EKeys::Right){S.Choice=1-S.Choice;return true;}
        bool Commit=A.Key==EKeys::Enter||A.Key==EKeys::E&&S.ERelease;
        if(A.Key==EKeys::LeftMouseButton){float X,Y;int W,H;if(PC->GetMousePosition(X,Y)){PC->GetViewportSize(W,H);X*=1920.f/W;Y*=1080.f/H;if(Y>=640&&Y<=700){if(X>=650&&X<=910){S.Choice=0;Commit=true;}else if(X>=1010&&X<=1270){S.Choice=1;Commit=true;}}}S.SwallowClick=true;}
        if(Commit){const int D=S.Dialog;S.Dialog=-1;if(S.Choice!=0)ParisTutorialSoundscape::CancelGreeting(M,D);if(S.Choice==0){
            if(D>=0){auto* C=Pawn(M->GetWorld(),D==0?TEXT("Ally1"):TEXT("Ally2"));if(!Dead(C)&&JoinedCount(M)<2&&!S.Joined[D]){S.Joined[D]=S.History[D]=true;Log(M,TEXT("recruited"));ParisTutorialSoundscape::Recruited(M,D);}}
            else if(D==-3){S.Skipped=true;Log(M,TEXT("recruitment_explicitly_skipped"));}
            else if(D==-2)M->StartTutorialCombat();
        }}return true;
    }
    if(ParisCombatUI::IsOpen(PC)||M->CheckpointDialogVisible())return false;
    if(A.Event==IE_Pressed&&A.Key==EKeys::Enter&&TrainingCheckpoint(M)&&M->InsideCheckpoint()){
        if(S.CP0Saved)M->StartTutorialCombat();else{M->DismissCheckpointPrompt();S.Dialog=-2;S.Choice=1;S.ERelease=false;}return true;
    }
    if(M->CheckpointPromptVisible||(A.Key==EKeys::E&&M->InsideCheckpoint()))return false;
    if(A.Event==IE_Pressed&&A.Key==EKeys::E&&S.Stage>=Recruit){
        if(S.CombatOpen&&M->LivingDefenders>0)for(const TCHAR* Id:{TEXT("German1"),TEXT("German2"),TEXT("German3")})if(auto* Enemy=Pawn(M->GetWorld(),Id))if(!Dead(Enemy)&&PC->LineOfSightTo(Enemy)){M->Feedback=TEXT("Recruitment unavailable during enemy contact.");return false;}
        for(int I=0;I<2;++I)if(!S.History[I]&&Facing(PC,Pawn(M->GetWorld(),I==0?TEXT("Ally1"):TEXT("Ally2")))){S.Dialog=I;S.Choice=0;S.ERelease=false;Log(M,TEXT("recruit_dialog_open"));ParisTutorialSoundscape::Greeting(M,I);return true;}
        for(int I=0;I<2;++I)if(S.History[I]&&Facing(PC,Pawn(M->GetWorld(),I==0?TEXT("Ally1"):TEXT("Ally2")))){M->Feedback=TEXT("This ally has already joined your squad.");return true;}
        if(Dead(Pawn(M->GetWorld(),TEXT("Ally1")))&&!S.History[0]||Dead(Pawn(M->GetWorld(),TEXT("Ally2")))&&!S.History[1]){S.Dialog=-3;S.Choice=1;S.ERelease=false;return true;}
    }
    return false;
}
bool SupplyAllowed(UWorld* W,const FString& Id){if(!Enabled())return true;auto* M=AParisBridgeMission::Find(W);if(!M)return false;int Stage=State(M).Stage;return Id==TEXT("Supply3")?false:Id==TEXT("Supply1")?Stage>=Frag:Stage>=Supply;}
FVector SiteXY(bool Trap,int I){const FVector T[]={FVector(6637.5,-20137.5,0),FVector(7637.5,-20487.5,0),MineFeet};const FVector B[]={SupplyFeet,FVector(6062.5,-20462.5,0),PracticeFeet};return Trap?T[I]:B[I];}
void InitializeEquipment(UWorld*,ParisTacticalEquipment::FEquipmentSession& S){S.Frag=S.Smoke=1;for(auto& T:S.Traps)T.State=TEXT("Dormant");S.ConsolidatedSupply=true;S.Supplies[0].Remaining=24;S.Supplies[0].FragRemaining=S.Supplies[0].SmokeRemaining=3;S.Supplies[2].Remaining=S.Supplies[2].FragRemaining=S.Supplies[2].SmokeRemaining=0;S.Supplies[2].Retired=true;}
void Saved(AParisBridgeMission* M){auto& S=State(M);if(TrainingCheckpoint(M)){S.CP0Saved=true;Log(M,TEXT("cp0_saved"));}else if(M->Phase==TEXT("Won")){S.Done=true;Stage(M,Complete);Log(M,TEXT("cp1_saved_tutorial_complete"));}}
#include "ParisTutorialSave.inl"
#include "ParisTutorialProbe.inl"
#include "ParisTutorialStartupProbe.inl"
}
