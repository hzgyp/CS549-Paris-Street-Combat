// Finite native pose presentation; original posture/collision/damage/journal own state.
#include "ParisProneTransition.h"
#include "ParisBridgeMission.h"
#include "ParisCombatUI.h"
#include "ParisTraversal.h"
#include "ParisPlayerDeath.h"
#include "ParisEquipmentState.h"
#include "ParisTacticalEquipment.h"
#include "ParisFirstPersonApprovedActor.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/Skeleton.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Camera/CameraActor.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "AIController.h"
#include "BrainComponent.h"
#include "Kismet/GameplayStatics.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "UnrealClient.h"
#include "ParisProneNativeCurves.inl"

namespace ParisProneTransition {
namespace {
double Num(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!F)return -1;const auto* V=F->ContainerPtrToValuePtr<void>(O);return F->IsFloatingPoint()?F->GetFloatingPointPropertyValue(V):F->GetSignedIntPropertyValue(V);}
bool Flag(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FBoolProperty>(O->GetClass(),K):nullptr;return F&&F->GetPropertyValue_InContainer(O);}
FName Name(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr;return F?F->GetPropertyValue_InContainer(O):NAME_None;}
void SetName(UObject* O,const TCHAR* K,FName V){if(auto* F=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr)F->SetPropertyValue_InContainer(O,V);}
void SetNum(UObject* O,const TCHAR* K,double V){auto* F=FindFProperty<FNumericProperty>(O->GetClass(),K);check(F);auto* P=F->ContainerPtrToValuePtr<void>(O);if(F->IsFloatingPoint())F->SetFloatingPointPropertyValue(P,V);else F->SetIntPropertyValue(P,int64(V));}
UObject* Obj(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FObjectPropertyBase>(O->GetClass(),K):nullptr;return F?F->GetObjectPropertyValue_InContainer(O):nullptr;}
void Call(UObject* O,const TCHAR* K){if(auto* F=O?O->FindFunction(K):nullptr)O->ProcessEvent(F,nullptr);}
struct FState {
 TWeakObjectPtr<ACharacter> Player;TWeakObjectPtr<AParisBridgePlayerController> PC;
 TWeakObjectPtr<UCameraComponent> Camera;TWeakObjectPtr<UAnimSequence> Clip;
 FTransform BaseCamera;FVector StartEye,StartFeet;
 FString LastFeedback,Generation,Reason=TEXT("NotStarted");double Restore=-1,At=0,Duration=0,Age=0,OldPosture=0,StartHalf=0,GoalHalf=0,CameraAlpha=0;
 bool Running=false,Entering=false,Committing=false,Locks=false;int32 ClipIndex=0,Starts=0,Completions=0,Rejects=0,Cancels=0;
 double MaxEyeStep=0,MeshFeetOffset=0,MaxMeshFeetError=0;FVector LastEye;TArray<TSharedPtr<FJsonValue>> Events;
};
TMap<TWeakObjectPtr<UWorld>,FState> States;FDelegateHandle PreHandle,PostHandle,CleanupHandle;
void Event(UWorld* W,FState& S,const FString& Kind,const FString& Why){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("kind"),Kind);O->SetStringField(TEXT("reason"),Why);O->SetNumberField(TEXT("time"),W->GetTimeSeconds());O->SetNumberField(TEXT("clip_index"),S.ClipIndex);if(S.Events.Num()<256)S.Events.Add(MakeShared<FJsonValueObject>(O));UE_LOG(LogTemp,Display,TEXT("PARIS_PRONE_TRANSITION %s %s"),*Kind,*Why);}
bool Alive(const ACharacter* P){return P&&!Flag(P,TEXT("IsDead"))&&Num(P,TEXT("Health"))>0;}
void Unlock(FState& S){if(S.Locks&&S.PC.IsValid()){S.PC->SetIgnoreMoveInput(false);S.PC->SetIgnoreLookInput(false);}S.Locks=false;}
void RestoreCamera(FState& S){if(S.Camera.IsValid())S.Camera->SetRelativeTransform(S.BaseCamera);}
void Stop(UWorld* W,FState& S,bool Complete,const FString& Why){
 RestoreCamera(S);Unlock(S);S.Running=false;S.Reason=Why;S.Committing=false;
 if(Complete)++S.Completions;else ++S.Cancels;
 if(auto* P=S.Player.Get();Alive(P)&&Name(P,TEXT("ActionState"))==FName(S.Entering?TEXT("ProneEntering"):TEXT("ProneExiting"))){SetName(P,TEXT("ActionState"),TEXT("Ready"));SetName(P,TEXT("ActivePose"),NAME_None);Call(P,TEXT("PC_UpdateActionPose"));}
 Event(W,S,Complete?TEXT("complete"):TEXT("cancel"),Why);
}
FCollisionQueryParams Query(ACharacter* P){FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisProneNativeMotion),false,P);for(TActorIterator<AActor> I(P->GetWorld());I;++I)if(I->GetOwner()==P||I->ActorHasTag(TEXT("ParisEquipmentOwned")))Q.AddIgnoredActor(*I);return Q;}
bool MotionClear(ACharacter* P,int32 Index,FString& Why){
 const FTransform Frame=P->GetMesh()->GetComponentTransform();auto Q=Query(P);const double Feet=P->GetActorLocation().Z-P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
 for(int32 B=0;B<ProneMotionBoneCount;++B)for(int32 I=1;I<49;++I){FHitResult H;const FVector A=Frame.TransformPosition(ProneMotionBones[Index][I-1][B]),End=Frame.TransformPosition(ProneMotionBones[Index][I][B]);
  if(P->GetWorld()->SweepSingleByChannel(H,A,End,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(ProneMotionRadii[B]),Q)){
   // Native boot/palm/pelvis contact with the existing level support is permitted;
   // side/overhead hits still reject. This is a bone envelope, not skin certification.
   if(H.ImpactNormal.Z>.95&&H.ImpactPoint.Z<=Feet+5)continue;
   // Sphere envelopes overlap the support at palms/toes; an initial overlap
   // has a depenetration normal instead of a reliable triangle normal. Require
   // an actual flat support trace, the same collision component, and contact
   // at support height before treating that overlap as native floor contact.
   FHitResult Support;const FVector XY(End.X,End.Y,Feet);
   const bool Floor=P->GetWorld()->LineTraceSingleByChannel(Support,XY+FVector(0,0,40),XY-FVector(0,0,30),ECC_Visibility,Q);
   if(Floor&&Support.Component==H.Component&&Support.ImpactNormal.Z>=.97&&FMath::Abs(Support.ImpactPoint.Z-Feet)<=10&&H.ImpactPoint.Z<=Support.ImpactPoint.Z+5&&(A.Z-ProneMotionRadii[B]<=Support.ImpactPoint.Z+5||End.Z-ProneMotionRadii[B]<=Support.ImpactPoint.Z+5))continue;
   Why=FString::Printf(TEXT("Transition blocked near %s by %s normal=%s point=%s feet=%.3f start_overlap=%d support=%s"),ProneMotionBoneNames[B],H.GetActor()?*H.GetActor()->GetName():TEXT("world"),*H.ImpactNormal.ToString(),*H.ImpactPoint.ToString(),Feet,H.bStartPenetrating,*Support.ImpactPoint.ToString());return false;
  }
 }
 return true;
}
// Explain a native refusal without overriding its result or thresholds.
FString ClearanceReason(ACharacter* P){
 const FVector Feet=P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight());
 const FVector Pending=P->GetPendingMovementInputVector();const double Axis=Num(P,TEXT("ProneProbeAxis"));
 const FVector Direction=FMath::Abs(Axis)>.01?P->GetActorForwardVector()*Axis*60:Pending.SizeSquared()>.01?Pending.GetSafeNormal()*60:P->GetVelocity();
 const FVector Center=Feet+FVector(0,0,30),Future=Center+Direction*FMath::Max(.1,double(P->GetWorld()->GetDeltaSeconds()));
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisProneRefusal),false,P);FHitResult H;
 if(P->GetWorld()->SweepSingleByChannel(H,Center,Future,P->GetActorQuat(),ECC_Visibility,FCollisionShape::MakeBox(FVector(130,55,28)),Q)){
  UE_LOG(LogTemp,Display,TEXT("PARIS_PRONE_CLEARANCE obstacle=%s feet=%s yaw=%.3f point=%s"),H.GetActor()?*H.GetActor()->GetPathName():TEXT("world"),*Feet.ToString(),P->GetActorRotation().Yaw,*H.ImpactPoint.ToString());
  return TEXT("Prone space blocked. Step away from the obstacle or turn.");
 }
 for(double Offset:{-120.,0.,110.}){const FVector Point=Feet+P->GetActorForwardVector()*Offset;FHitResult Floor;
  const bool Hit=P->GetWorld()->LineTraceSingleByChannel(Floor,Point+FVector(0,0,40),Point-FVector(0,0,30),ECC_Visibility,Q);
  if(!Hit||Floor.ImpactNormal.Z<.97||FMath::Abs(Floor.ImpactPoint.Z-Feet.Z)>10){
   UE_LOG(LogTemp,Display,TEXT("PARIS_PRONE_CLEARANCE support_offset=%.0f feet=%s yaw=%.3f hit=%d normal=%s point=%s"),Offset,*Feet.ToString(),P->GetActorRotation().Yaw,Hit,*Floor.ImpactNormal.ToString(),*Floor.ImpactPoint.ToString());
   return TEXT("Prone needs flat ground under head and feet. Move to level ground.");
  }
 }
 return TEXT("Prone path blocked. Stop and move to open, level ground.");
}
double CurveAlpha(int32 Index,double T){const double X=FMath::Clamp(T*48.,0.,48.);const int32 A=FMath::FloorToInt(X),B=FMath::Min(A+1,48);return FMath::Lerp(ProneHeadProgress[Index][A],ProneHeadProgress[Index][B],X-A);}
bool Request(AParisBridgePlayerController* PC,FString& Why){
 auto* W=PC->GetWorld();auto* M=AParisBridgeMission::Find(W);auto* P=Cast<ACharacter>(PC->GetPawn());auto& S=States.FindOrAdd(W);
 if(!M||!P||(!M->AllowsPlay()&&M->Phase!=TEXT("Won"))||ParisCombatUI::IsOpen(PC)||M->CheckpointDialogVisible()||!Alive(P)||!P->GetCharacterMovement()->IsMovingOnGround()){Why=TEXT("Stand on supported ground before changing posture");return false;}
 if(S.Running){Why=TEXT("Finish the current posture change");return false;}
 auto& E=ParisTacticalEquipment::Session(W);
 if((Name(P,TEXT("ActionState"))!=TEXT("Ready")&&Name(P,TEXT("ActionState"))!=TEXT("Reloading"))||E.SelectedSlot!=0||!E.ThrowKind.IsEmpty()){Why=TEXT("Finish your action and select the rifle before changing posture");return false;}
 bool Ready=false;for(TActorIterator<AParisFirstPersonApprovedActor> I(W);I;++I)if(I->GetOwner()==P&&I->Initialized)Ready=true;if(!Ready){Why=TEXT("Player display preparing");return false;}
 P->GetMesh()->UpdateComponentToWorld();
 const double Half=P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();const bool Entering=Half>=40;const int32 Index=Entering?(P->bIsCrouched?2:0):1;
 auto* Clip=LoadObject<UAnimSequence>(nullptr,*FString::Printf(TEXT("/Game/RifleAnimsetPro/Animations/InPlace/%s.%s"),ProneClipNames[Index],ProneClipNames[Index]));
 if(!Clip||!Clip->GetSkeleton()->IsCompatibleMesh(P->GetMesh()->GetSkeletalMeshAsset())){Why=TEXT("Native posture clip missing or incompatible");return false;}
 if(Entering){Call(P,TEXT("PC_CheckProneClearance"));if(!Flag(P,TEXT("ProneClear"))){Why=ClearanceReason(P);return false;}}
 if(!MotionClear(P,Index,Why))return false;
 auto* Camera=Cast<UCameraComponent>(Obj(P,TEXT("ParisPlayerCamera")));if(!Camera){Why=TEXT("Player camera unavailable");return false;}
 const double Old=Num(P,TEXT("DesiredPosture"));const FTransform Base=Camera->GetRelativeTransform();const FVector Eye=Camera->GetComponentLocation(),Feet=P->GetActorLocation()-FVector(0,0,Half);const double MeshFeetOffset=P->GetMesh()->GetComponentLocation().Z-Feet.Z;
 Call(P,TEXT("PC_ActionProne"));
 if(Entering&&Num(P,TEXT("DesiredPosture"))!=2){Why=TEXT("Original posture request rejected");return false;}
 if(Entering){SetNum(P,TEXT("DesiredPosture"),Old);if(P->bIsCrouched){SetNum(P,TEXT("DesiredPosture"),0);Call(P,TEXT("PC_UpdateActions"));P->GetCharacterMovement()->UnCrouch(false);if(P->bIsCrouched){SetNum(P,TEXT("DesiredPosture"),Old);Call(P,TEXT("PC_UpdateActions"));Why=TEXT("Not enough headroom for the original crouch-to-prone posture change");return false;}}}else{Call(P,TEXT("PC_UpdateActions"));P->GetCharacterMovement()->UnCrouch(false);if(P->bIsCrouched){SetNum(P,TEXT("DesiredPosture"),2);Call(P,TEXT("PC_UpdateActions"));Why=TEXT("Not enough headroom to stand");return false;}}
 P->GetMesh()->UpdateComponentToWorld();
 S.Player=P;S.PC=PC;S.Camera=Camera;S.Clip=Clip;S.BaseCamera=Base;S.StartEye=Eye;S.LastEye=Eye;S.StartFeet=Feet;S.StartHalf=Half;S.MeshFeetOffset=MeshFeetOffset;S.OldPosture=Old;S.Entering=Entering;S.ClipIndex=Index;S.At=W->GetTimeSeconds();S.Age=0;S.Duration=Clip->GetPlayLength();S.CameraAlpha=0;S.Generation=M->RunGeneration;S.Restore=Num(P,TEXT("RestoreGeneration"));S.Running=true;S.Committing=false;++S.Starts;S.Reason=Entering?TEXT("Going prone"):TEXT("Standing up");
 const double Scale=P->GetCapsuleComponent()->GetShapeScale();S.GoalHalf=Entering?FMath::Max(34.f,P->GetCapsuleComponent()->GetUnscaledCapsuleRadius())*Scale:P->GetClass()->GetDefaultObject<ACharacter>()->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()*Scale;
 PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);S.Locks=true;P->StopJumping();P->ConsumeMovementInputVector();P->GetCharacterMovement()->StopMovementImmediately();
 SetName(P,TEXT("ActionState"),Entering?TEXT("ProneEntering"):TEXT("ProneExiting"));SetName(P,TEXT("ActivePose"),FName(ProneClipNames[Index]));P->GetMesh()->PlayAnimation(Clip,false);
 if(!S.LastFeedback.IsEmpty()&&M->Feedback==S.LastFeedback)M->Feedback.Reset();S.LastFeedback.Reset();
 Camera->SetWorldLocation(Eye);Event(W,S,TEXT("start"),FString::Printf(TEXT("native=%s duration=%.6f original_half=%.6f target_half=%.6f"),*Clip->GetPathName(),S.Duration,Half,S.GoalHalf));return true;
}
void Pre(UWorld* W,ELevelTick,float){
 if(!W||!W->IsGameWorld())return;auto* S=States.Find(W);if(!S||!S->Running)return;auto* P=S->Player.Get();auto* M=AParisBridgeMission::Find(W);
 if(!P||!M||S->Generation!=M->RunGeneration||S->Restore!=Num(P,TEXT("RestoreGeneration"))||!Alive(P)||M->Phase==TEXT("Lost")||M->Phase==TEXT("Ready")){Stop(W,*S,false,TEXT("Original lifecycle interrupted transition"));return;}
 if(W->IsPaused())return;
 P->ConsumeMovementInputVector();P->GetCharacterMovement()->StopMovementImmediately();
}
void Post(UWorld* W,ELevelTick,float){
 if(!W||!W->IsGameWorld()||W->IsPaused())return;auto* S=States.Find(W);if(!S||!S->Running)return;auto* P=S->Player.Get();if(!Alive(P)){Stop(W,*S,false,TEXT("Death takes priority"));return;}
 auto* Single=P->GetMesh()->GetSingleNodeInstance();if(!Single||Single->GetCurrentAsset()!=S->Clip.Get()){Stop(W,*S,false,TEXT("Original action replaced transition"));return;}
 // Native OnStart/OnEndCrouch changes MeshRelativeLocation through the direct
 // mutable accessor. Refresh that existing transform after movement; otherwise
 // a single-node pose can retain the old component world frame and float/sink.
 P->GetMesh()->UpdateComponentToWorld();
 const double MeshFeet=P->GetMesh()->GetComponentLocation().Z-(P->GetActorLocation().Z-P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
 S->MaxMeshFeetError=FMath::Max(S->MaxMeshFeetError,FMath::Abs(MeshFeet-S->MeshFeetOffset));
 S->Age=Single->GetCurrentTime();S->CameraAlpha=FMath::Max(S->CameraAlpha,CurveAlpha(S->ClipIndex,S->Age/S->Duration));
 if(S->Camera.IsValid()){
  auto* Parent=S->Camera->GetAttachParent();const FVector Natural=Parent->GetComponentTransform().TransformPosition(S->BaseCamera.GetLocation());
  const FVector End=Natural+FVector(0,0,S->GoalHalf-P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());const FVector Eye=FMath::Lerp(S->StartEye,End,S->CameraAlpha);
  S->Camera->SetWorldLocation(Eye);S->MaxEyeStep=FMath::Max(S->MaxEyeStep,FVector::Distance(Eye,S->LastEye));S->LastEye=Eye;
  if(S->PC.IsValid()&&S->PC->GetViewTarget()==P&&S->PC->PlayerCameraManager)S->PC->PlayerCameraManager->UpdateCamera(0);
 }
 if(S->Age>=S->Duration-.001){
  if(S->Entering){if(!S->Committing){SetNum(P,TEXT("DesiredPosture"),2);Call(P,TEXT("PC_UpdateActions"));S->Committing=true;Event(W,*S,TEXT("commit"),TEXT("Original Crouch endpoint after native motion"));}
   if(P->bIsCrouched&&P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()<40){Stop(W,*S,true,TEXT("Native enter complete; original prone loop"));return;}
  }else{Stop(W,*S,true,TEXT("Native exit complete; original standing stride"));return;}
 }
 if(W->GetTimeSeconds()-S->At>S->Duration+1){SetNum(P,TEXT("DesiredPosture"),S->OldPosture);Call(P,TEXT("PC_UpdateActions"));Stop(W,*S,false,TEXT("Bounded native posture commit rejected"));}
}
void Cleanup(UWorld* W,bool,bool){if(auto* S=States.Find(W)){RestoreCamera(*S);Unlock(*S);}States.Remove(W);}
}
bool Active(const ACharacter* P){const auto* S=P?States.Find(P->GetWorld()):nullptr;return S&&S->Running&&S->Player.Get()==P;}
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& K){
 auto* W=PC->GetWorld();auto& S=States.FindOrAdd(W);
 if(S.Running){if(K.Event==IE_Released)return false;return K.Key==EKeys::Z||K.Key==EKeys::SpaceBar||K.Key==EKeys::LeftControl||K.Key==EKeys::RightControl||K.Key==EKeys::LeftMouseButton||K.Key==EKeys::RightMouseButton||K.Key==EKeys::R||K.Key==EKeys::MouseScrollUp||K.Key==EKeys::MouseScrollDown;}
 if(K.Key!=EKeys::Z||K.Event!=IE_Pressed)return false;FString Why;if(!Request(PC,Why)){++S.Rejects;S.Reason=Why;Event(W,S,TEXT("reject"),Why);if(auto* M=AParisBridgeMission::Find(W)){S.LastFeedback=Why.StartsWith(TEXT("Transition blocked near"))?TEXT("Not enough room to change posture."):Why;M->Feedback=S.LastFeedback;}}return true;
}
TSharedPtr<FJsonObject> Inspect(UWorld* W){auto O=MakeShared<FJsonObject>();const auto* S=States.Find(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* I=P?P->GetMesh()->GetSingleNodeInstance():nullptr;O->SetBoolField(TEXT("active"),S&&S->Running);O->SetBoolField(TEXT("entering"),S&&S->Entering);O->SetBoolField(TEXT("committing"),S&&S->Committing);O->SetNumberField(TEXT("starts"),S?S->Starts:0);O->SetNumberField(TEXT("completions"),S?S->Completions:0);O->SetNumberField(TEXT("rejects"),S?S->Rejects:0);O->SetNumberField(TEXT("cancels"),S?S->Cancels:0);O->SetNumberField(TEXT("age"),S?S->Age:0);O->SetNumberField(TEXT("duration"),S?S->Duration:0);O->SetNumberField(TEXT("camera_alpha"),S?S->CameraAlpha:0);O->SetNumberField(TEXT("max_eye_step_cm"),S?S->MaxEyeStep:0);O->SetNumberField(TEXT("max_mesh_feet_error_cm"),S?S->MaxMeshFeetError:0);O->SetNumberField(TEXT("capsule_half"),P?P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight():0);O->SetNumberField(TEXT("desired_posture"),Num(P,TEXT("DesiredPosture")));O->SetStringField(TEXT("action"),Name(P,TEXT("ActionState")).ToString());O->SetStringField(TEXT("clip"),I&&I->GetCurrentAsset()?I->GetCurrentAsset()->GetName():TEXT("AnimBlueprint"));O->SetStringField(TEXT("reason"),S?S->Reason:TEXT("NotStarted"));if(S)O->SetArrayField(TEXT("events"),S->Events);return O;}
#include "ParisProneTransitionProbe.inl"
void Initialize(){PreHandle=FWorldDelegates::OnWorldTickStart.AddStatic(&Pre);PostHandle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Post);CleanupHandle=FWorldDelegates::OnWorldCleanup.AddStatic(&Cleanup);InitializeProbe();}
void Shutdown(){ShutdownProbe();FWorldDelegates::OnWorldTickStart.Remove(PreHandle);FWorldDelegates::OnWorldPostActorTick.Remove(PostHandle);FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);for(auto& S:States){RestoreCamera(S.Value);Unlock(S.Value);}States.Empty();}
}
