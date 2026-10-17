// Source-only Ctrl presentation bridge. Original Blueprint/movement own posture.
#include "ParisCrouchTransition.h"
#include "ParisCrouchTransitionPolicy.h"
#include "ParisBridgeMission.h"
#include "ParisCombatUI.h"
#include "ParisProneTransition.h"
#include "ParisTraversal.h"
#include "ParisTacticalEquipment.h"
#include "ParisEquipmentState.h"
#include "ParisFirstPersonApprovedActor.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/Skeleton.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "UObject/UnrealType.h"
#include "Dom/JsonObject.h"

namespace ParisCrouchTransition {
namespace {
double Num(const UObject* O,const TCHAR* K){const auto* F=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!F)return -1;const void* V=F->ContainerPtrToValuePtr<void>(O);return F->IsFloatingPoint()?F->GetFloatingPointPropertyValue(V):F->GetSignedIntPropertyValue(V);}
bool Flag(const UObject* O,const TCHAR* K){const auto* F=O?FindFProperty<FBoolProperty>(O->GetClass(),K):nullptr;return F&&F->GetPropertyValue_InContainer(O);}
FName Name(const UObject* O,const TCHAR* K){const auto* F=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr;return F?F->GetPropertyValue_InContainer(O):NAME_None;}
void SetName(UObject* O,const TCHAR* K,FName V){if(auto* F=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr)F->SetPropertyValue_InContainer(O,V);}
void SetNum(UObject* O,const TCHAR* K,double V){auto* F=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;check(F);void* D=F->ContainerPtrToValuePtr<void>(O);if(F->IsFloatingPoint())F->SetFloatingPointPropertyValue(D,V);else F->SetIntPropertyValue(D,int64(V));}
UObject* Obj(const UObject* O,const TCHAR* K){const auto* F=O?FindFProperty<FObjectPropertyBase>(O->GetClass(),K):nullptr;return F?F->GetObjectPropertyValue_InContainer(O):nullptr;}
void Call(UObject* O,const TCHAR* K){if(auto* F=O?O->FindFunction(K):nullptr)O->ProcessEvent(F,nullptr);}
bool Alive(const ACharacter* P){return P&&!Flag(P,TEXT("IsDead"))&&Num(P,TEXT("Health"))>0;}
bool OurAction(const ACharacter* P){const FName A=Name(P,TEXT("ActionState"));return A==TEXT("CrouchEntering")||A==TEXT("CrouchExiting");}
FVector Feet(const ACharacter* P){return P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());}
struct FState {
    TWeakObjectPtr<ACharacter> Player;
    TWeakObjectPtr<AParisBridgePlayerController> PC;
    TWeakObjectPtr<UCameraComponent> Camera;
    TWeakObjectPtr<UAnimSequence> Clip;
    FTransform BaseCamera;
    FVector StartEye,StartFeet,LastEye;
    FString Generation,Reason=TEXT("NotStarted"),LastFeedback;
    double Restore=-1,At=0,Age=0,Duration=0,OldPosture=0,GoalHalf=0,CameraAlpha=0,MaxEyeStep=0;
    bool Running=false,Entering=false,Committing=false,Locks=false;
    int32 Starts=0,Completions=0,Rejects=0,Cancels=0;
};
TMap<TWeakObjectPtr<UWorld>,FState> States;
FDelegateHandle PreHandle,PostHandle,CleanupHandle;
void Event(FState& S,const TCHAR* Kind,const FString& Why){S.Reason=Why;UE_LOG(LogTemp,Display,TEXT("PARIS_CROUCH_TRANSITION %s %s"),Kind,*Why);}
void Unlock(FState& S){if(S.Locks&&S.PC.IsValid()){S.PC->SetIgnoreMoveInput(false);S.PC->SetIgnoreLookInput(false);}S.Locks=false;}
void Refresh(ACharacter* P){P->GetMesh()->UpdateComponentToWorld();P->GetMesh()->RefreshBoneTransforms();for(TActorIterator<AParisFirstPersonApprovedActor> I(P->GetWorld());I;++I)if(I->GetOwner()==P&&I->Initialized)I->RefreshUnifiedPresentation();ParisTraversal::RefreshObserver(P->GetWorld());}
void CameraUpdate(FState& S){if(S.PC.IsValid()&&S.PC->PlayerCameraManager)S.PC->PlayerCameraManager->UpdateCamera(0);}
bool SameLifecycle(const FState& S){auto* P=S.Player.Get();auto* M=P?AParisBridgeMission::Find(P->GetWorld()):nullptr;return P&&S.PC.IsValid()&&S.PC->GetPawn()==P&&M&&M->RunGeneration==S.Generation&&Num(P,TEXT("RestoreGeneration"))==S.Restore;}
void Stop(FState& S,bool Complete,const FString& Why){
    if(S.Camera.IsValid())S.Camera->SetRelativeTransform(S.BaseCamera);
    Unlock(S);S.Running=false;S.Committing=false;
    if(Complete)++S.Completions;else ++S.Cancels;
    if(auto* P=S.Player.Get();Alive(P)&&OurAction(P)&&SameLifecycle(S)){
        SetName(P,TEXT("ActionState"),TEXT("Ready"));SetName(P,TEXT("ActivePose"),NAME_None);
        Call(P,TEXT("PC_UpdateActionPose"));Refresh(P);
    }
    CameraUpdate(S);Event(S,Complete?TEXT("complete"):TEXT("cancel"),Why);
}
void RestorePosture(FState& S){
    auto* P=S.Player.Get();if(!Alive(P)||!OurAction(P)||!SameLifecycle(S))return;
    SetNum(P,TEXT("DesiredPosture"),S.OldPosture);Call(P,TEXT("PC_UpdateActions"));
    // Engine admission remains enabled; never assign capsule size or teleport.
    if(S.OldPosture==1)P->GetCharacterMovement()->Crouch(false);
    else P->GetCharacterMovement()->UnCrouch(false);
    P->GetMesh()->UpdateComponentToWorld();
}
bool StandingVolumeClear(ACharacter* P){
    auto* C=P->GetCapsuleComponent();FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisCrouchStandVolume),false,P);FCollisionResponseParams R;
    C->InitSweepCollisionParams(Q,R);
    // Match actual movement collision responses. Tiny shrink excludes floor tangency.
    return !P->GetWorld()->OverlapBlockingTestByChannel(C->GetComponentLocation(),C->GetComponentQuat(),C->GetCollisionObjectType(),C->GetCollisionShape(-UE_KINDA_SMALL_NUMBER*10.f),Q,R);
}
bool Request(AParisBridgePlayerController* PC,FString& Why){
    auto* W=PC->GetWorld();auto* M=AParisBridgeMission::Find(W);auto* P=Cast<ACharacter>(PC->GetPawn());auto& S=States.FindOrAdd(W);
    if(!M||!P||W->IsPaused()||(!M->AllowsPlay()&&M->Phase!=TEXT("Won"))||ParisCombatUI::IsOpen(PC)||M->CheckpointDialogVisible()||!Alive(P)||!P->GetCharacterMovement()->IsMovingOnGround()){
        Why=TEXT("Stand on supported ground before changing posture");return false;
    }
    if(S.Running||ParisProneTransition::Active(P)||ParisTraversal::Active(P)){Why=TEXT("Finish the current posture change");return false;}
    auto& E=ParisTacticalEquipment::Session(W);
    const FName Action=Name(P,TEXT("ActionState"));
    if((Action!=TEXT("Ready")&&Action!=TEXT("Reloading"))||!E.ThrowKind.IsEmpty()){
        Why=TEXT("Finish the current posture change");return false;
    }
    bool DisplayReady=false;for(TActorIterator<AParisFirstPersonApprovedActor> I(W);I;++I)if(I->GetOwner()==P&&I->Initialized)DisplayReady=true;
    auto* Mesh=P->GetMesh();auto* Camera=Cast<UCameraComponent>(Obj(P,TEXT("ParisPlayerCamera")));
    if(!DisplayReady||!Mesh->GetSkeletalMeshAsset()||!Camera||!Camera->GetAttachParent()){Why=TEXT("Player display preparing");return false;}
    const bool Entering=!P->bIsCrouched;const double Old=Num(P,TEXT("DesiredPosture"));
    if(Old!=(Entering?0:1)){Why=TEXT("Finish the current posture change");return false;}
    const TCHAR* ClipName=Entering?TEXT("Rifle_Idle2Crouch"):TEXT("Rifle_Crouch2Idle");
    auto* Clip=LoadObject<UAnimSequence>(nullptr,*FString::Printf(TEXT("/Game/RifleAnimsetPro/Animations/InPlace/%s.%s"),ClipName,ClipName));
    if(!Clip||!Clip->GetSkeleton()||!Clip->GetSkeleton()->IsCompatibleMesh(Mesh->GetSkeletalMeshAsset())||Clip->HasRootMotion()||!FMath::IsFinite(Clip->GetPlayLength())||Clip->GetPlayLength()<.05f||Clip->GetPlayLength()>10.f){
        Why=TEXT("Native posture clip missing or incompatible");return false;
    }
    const FTransform Base=Camera->GetRelativeTransform();const FVector Eye=Camera->GetComponentLocation(),StartFeet=Feet(P);
    Call(P,TEXT("PC_ActionCrouch"));
    if(Num(P,TEXT("DesiredPosture"))!=(Entering?1:0)){Why=TEXT("Original posture request rejected");return false;}
    SetName(P,TEXT("ActionState"),Entering?TEXT("CrouchEntering"):TEXT("CrouchExiting"));
    Call(P,TEXT("PC_UpdateActions"));
    double GoalHalf=0;
    if(Entering){
        // Let the native Blueprint choose its own crouch height, then hold the
        // original standing endpoint until the full descent clip has completed.
        GoalHalf=FMath::Max(P->GetCapsuleComponent()->GetUnscaledCapsuleRadius(),P->GetCharacterMovement()->GetCrouchedHalfHeight())*P->GetCapsuleComponent()->GetShapeScale();
        SetNum(P,TEXT("DesiredPosture"),Old);Call(P,TEXT("PC_UpdateActions"));
    }else{
        P->GetCharacterMovement()->UnCrouch(false);
        if(P->bIsCrouched){
            SetNum(P,TEXT("DesiredPosture"),Old);Call(P,TEXT("PC_UpdateActions"));
            SetName(P,TEXT("ActionState"),TEXT("Ready"));SetName(P,TEXT("ActivePose"),NAME_None);Call(P,TEXT("PC_UpdateActionPose"));
            Mesh->UpdateComponentToWorld();Camera->SetRelativeTransform(Base);
            Why=TEXT("Not enough headroom to stand");return false;
        }
        GoalHalf=P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    }
    Mesh->UpdateComponentToWorld();
    S.Player=P;S.PC=PC;S.Camera=Camera;S.Clip=Clip;S.BaseCamera=Base;S.StartEye=Eye;S.StartFeet=StartFeet;S.LastEye=Eye;
    S.Generation=M->RunGeneration;S.Restore=Num(P,TEXT("RestoreGeneration"));S.At=W->GetTimeSeconds();S.Age=0;S.Duration=Clip->GetPlayLength();S.OldPosture=Old;S.GoalHalf=GoalHalf;S.CameraAlpha=0;S.MaxEyeStep=0;
    S.Running=true;S.Entering=Entering;S.Committing=false;++S.Starts;
    PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);S.Locks=true;
    P->StopJumping();P->ConsumeMovementInputVector();P->GetCharacterMovement()->StopMovementImmediately();
    SetName(P,TEXT("ActivePose"),FName(ClipName));Mesh->PlayAnimation(Clip,false);
    if(auto* Single=Mesh->GetSingleNodeInstance()){Single->SetPlaying(false);Single->SetPosition(0,false);}
    Mesh->TickAnimation(0,false);Refresh(P);Camera->SetWorldLocation(Eye);CameraUpdate(S);
    if(!S.LastFeedback.IsEmpty()&&M->Feedback==S.LastFeedback)M->Feedback.Reset();S.LastFeedback.Reset();
    Event(S,TEXT("start"),FString::Printf(TEXT("native=%s duration=%.6f goal_half=%.6f"),*Clip->GetPathName(),S.Duration,S.GoalHalf));return true;
}
void Pre(UWorld* W,ELevelTick,float){
    if(!W||!W->IsGameWorld())return;auto* S=States.Find(W);if(!S||!S->Running)return;
    auto* P=S->Player.Get();auto* M=AParisBridgeMission::Find(W);
    if(!P||!M||!SameLifecycle(*S)||!Alive(P)||M->Phase==TEXT("Lost")||M->Phase==TEXT("Ready")){
        Stop(*S,false,TEXT("Original lifecycle interrupted crouch transition"));return;
    }
    if(W->IsPaused())return;
    P->ConsumeMovementInputVector();P->GetCharacterMovement()->StopMovementImmediately();
}
void Post(UWorld* W,ELevelTick,float){
    if(!W||!W->IsGameWorld()||W->IsPaused())return;auto* S=States.Find(W);if(!S||!S->Running)return;
    if(!SameLifecycle(*S)){Stop(*S,false,TEXT("Original restore or possession takes priority"));return;}
    auto* P=S->Player.Get();if(!Alive(P)){Stop(*S,false,TEXT("Death takes priority"));return;}
    if(!OurAction(P)){Stop(*S,false,TEXT("Original action replaced crouch transition"));return;}
    auto* Mesh=P->GetMesh();auto* Single=Mesh->GetSingleNodeInstance();
    if(!Single||Single->GetCurrentAsset()!=S->Clip.Get()){RestorePosture(*S);Stop(*S,false,TEXT("Native crouch motion source lost"));return;}
    if(!S->Entering&&!StandingVolumeClear(P)){
        RestorePosture(*S);if(auto* M=AParisBridgeMission::Find(W))M->Feedback=TEXT("Not enough headroom to stand");
        Stop(*S,false,TEXT("Standing space became blocked; returned to native crouch"));return;
    }
    if(!P->GetCharacterMovement()->IsMovingOnGround()){
        RestorePosture(*S);Stop(*S,false,TEXT("Ground support interrupted crouch transition"));return;
    }
    // Manually sample the native sequence without notifies, as existing vault
    // presentation does. Full duration advances with paused-aware world time;
    // hidden-body animation tick policy cannot freeze or double-advance it.
    const double Elapsed=W->GetTimeSeconds()-S->At;S->Age=FMath::Clamp(Elapsed,0.,S->Duration);
    Single->SetPlaying(false);Single->SetPosition(S->Age,false);Mesh->TickAnimation(0,false);Refresh(P);
    S->CameraAlpha=ParisCrouchTransitionPolicy::CameraAlpha(S->Age,S->Duration);
    if(S->Camera.IsValid()){
        auto* Parent=S->Camera->GetAttachParent();
        if(!Parent){RestorePosture(*S);Stop(*S,false,TEXT("Player camera frame lost"));return;}
        const FVector Natural=Parent->GetComponentTransform().TransformPosition(S->BaseCamera.GetLocation());
        const FVector End=Natural+FVector(0,0,S->GoalHalf-P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
        const FVector Start=S->StartEye+(Feet(P)-S->StartFeet),Eye=FMath::Lerp(Start,End,S->CameraAlpha);
        S->Camera->SetWorldLocation(Eye);S->MaxEyeStep=FMath::Max(S->MaxEyeStep,FVector::Distance(Eye,S->LastEye));S->LastEye=Eye;CameraUpdate(*S);
    }
    const bool AtEndpoint=P->bIsCrouched==S->Entering&&FMath::IsNearlyEqual(double(P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()),S->GoalHalf,.1);
    using namespace ParisCrouchTransitionPolicy;
    switch(Decide(S->Entering,S->Committing,AtEndpoint,S->Age,S->Duration,Elapsed)){
    case Endpoint::CommitCrouch:
        SetNum(P,TEXT("DesiredPosture"),1);Call(P,TEXT("PC_UpdateActions"));P->GetCharacterMovement()->Crouch(false);S->Committing=true;
        Mesh->UpdateComponentToWorld();
        // Capsule admission moves the camera's parent. Preserve the already
        // eased world eye in this same frame, then release its original local
        // transform only at the verified native endpoint (no double drop).
        if(S->Camera.IsValid())S->Camera->SetWorldLocation(S->LastEye);
        if(P->bIsCrouched&&FMath::IsNearlyEqual(double(P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()),S->GoalHalf,.1))Stop(*S,true,TEXT("Native crouch transition complete"));
        else CameraUpdate(*S);
        break;
    case Endpoint::Complete:Stop(*S,true,TEXT("Native crouch transition complete"));break;
    case Endpoint::Timeout:RestorePosture(*S);Stop(*S,false,TEXT("Bounded native crouch endpoint rejected"));break;
    default:break;
    }
}
void Cleanup(UWorld* W,bool,bool){if(auto* S=States.Find(W)){if(S->Camera.IsValid())S->Camera->SetRelativeTransform(S->BaseCamera);Unlock(*S);}States.Remove(W);}
}
bool Active(const ACharacter* P){const auto* S=P?States.Find(P->GetWorld()):nullptr;return S&&S->Running&&S->Player.Get()==P;}
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& K){
    auto* W=PC->GetWorld();auto* P=Cast<ACharacter>(PC->GetPawn());auto& S=States.FindOrAdd(W);
    const bool Ctrl=K.Key==EKeys::LeftControl||K.Key==EKeys::RightControl;
    if(S.Running){
        if(K.Event==IE_Released)return false;
        return Ctrl||K.Key==EKeys::Z||K.Key==EKeys::SpaceBar||K.Key==EKeys::LeftMouseButton||K.Key==EKeys::RightMouseButton||K.Key==EKeys::R||K.Key==EKeys::MouseScrollUp||K.Key==EKeys::MouseScrollDown||K.Key==EKeys::LeftShift||K.Key==EKeys::RightShift||K.Key==EKeys::E||K.Key==EKeys::F5;
    }
    if(!Ctrl||K.Event==IE_Released)return false;
    // Retain the separately accepted prone/vault input owner and native Ctrl
    // from prone policy. The new pair covers standing <-> crouching only.
    if(!P||ParisProneTransition::Active(P)||ParisTraversal::Active(P)||Num(P,TEXT("DesiredPosture"))==2||P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()<40)return false;
    if(K.Event!=IE_Pressed)return true;
    FString Why;if(!Request(PC,Why)){++S.Rejects;Event(S,TEXT("reject"),Why);if(auto* M=AParisBridgeMission::Find(W)){S.LastFeedback=Why;M->Feedback=Why;}}
    return true;
}
TSharedPtr<FJsonObject> Inspect(UWorld* W){
    auto O=MakeShared<FJsonObject>();const auto* S=States.Find(W);
    O->SetBoolField(TEXT("active"),S&&S->Running);O->SetBoolField(TEXT("entering"),S&&S->Entering);
    O->SetNumberField(TEXT("starts"),S?S->Starts:0);O->SetNumberField(TEXT("completions"),S?S->Completions:0);O->SetNumberField(TEXT("rejects"),S?S->Rejects:0);O->SetNumberField(TEXT("cancels"),S?S->Cancels:0);
    O->SetNumberField(TEXT("age"),S?S->Age:0);O->SetNumberField(TEXT("duration"),S?S->Duration:0);O->SetNumberField(TEXT("camera_alpha"),S?S->CameraAlpha:0);O->SetNumberField(TEXT("max_eye_step_cm"),S?S->MaxEyeStep:0);
    O->SetStringField(TEXT("clip"),S&&S->Clip.IsValid()?S->Clip->GetPathName():TEXT("None"));O->SetStringField(TEXT("reason"),S?S->Reason:TEXT("NotStarted"));return O;
}
void Initialize(){PreHandle=FWorldDelegates::OnWorldTickStart.AddStatic(&Pre);PostHandle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Post);CleanupHandle=FWorldDelegates::OnWorldCleanup.AddStatic(&Cleanup);}
void Shutdown(){FWorldDelegates::OnWorldTickStart.Remove(PreHandle);FWorldDelegates::OnWorldPostActorTick.Remove(PostHandle);FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);for(auto& Entry:States)if(Entry.Value.Running)Stop(Entry.Value,false,TEXT("Module shutdown"));States.Empty();}
}
