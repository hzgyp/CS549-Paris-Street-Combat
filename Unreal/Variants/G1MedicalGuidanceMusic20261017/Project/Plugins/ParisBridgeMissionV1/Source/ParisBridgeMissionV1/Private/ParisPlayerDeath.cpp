// Render-only death sequence. Original damage, PC_Die and journals own state.
#include "ParisPlayerDeath.h"
#include "ParisActionBindings.h"
#include "ParisFirstPersonApprovedActor.h"
#include "ParisBridgeMission.h"
#include "ParisTacticalEquipment.h"
#include "ParisEquipmentState.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "Engine/SkeletalMesh.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerInput.h"
#include "GameFramework/PlayerController.h"
#include "Camera/PlayerCameraManager.h"
#include "AIController.h"
#include "BrainComponent.h"
#include "InputCoreTypes.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Dom/JsonObject.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"
#include "UnrealClient.h"

namespace ParisPlayerDeath {
namespace {
bool Dead(const ACharacter* P){auto* F=P?FindFProperty<FBoolProperty>(P->GetClass(),TEXT("IsDead")):nullptr;return F&&F->GetPropertyValue_InContainer(P);}
UObject* Object(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FObjectPropertyBase>(O->GetClass(),K):nullptr;return F?F->GetObjectPropertyValue_InContainer(O):nullptr;}
struct FDeath {
 TWeakObjectPtr<ACharacter> Player;
 TWeakObjectPtr<ACameraActor> Camera;
 TWeakObjectPtr<AActor> Previous;
 TArray<TWeakObjectPtr<AActor>> HiddenDisplays;
 FVector Feet=FVector::ZeroVector,CameraAt=FVector::ZeroVector;
 bool Started=false,Finished=false,MeshHidden=false,MeshVisible=false,OwnerNoSee=false;
 EVisibilityBasedAnimTickOption TickPolicy=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
 double At=0,Remaining=0,FinishedAt=0;
};
TMap<TWeakObjectPtr<UWorld>,FDeath> States;
FDelegateHandle TickHandle,CleanupHandle;
void Reset(UWorld* W,FDeath& S){
 if(auto* PC=UGameplayStatics::GetPlayerController(W,0))if(S.Started){PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);if(PC->GetViewTarget()==S.Camera.Get()&&S.Previous.IsValid())PC->SetViewTarget(S.Previous.Get());}
 if(auto* P=S.Player.Get())if(!Dead(P)){auto* Mesh=P->GetMesh();Mesh->SetHiddenInGame(S.MeshHidden);Mesh->SetVisibility(S.MeshVisible);Mesh->SetOwnerNoSee(S.OwnerNoSee);Mesh->VisibilityBasedAnimTickOption=S.TickPolicy;for(auto A:S.HiddenDisplays)if(A.IsValid())A->SetActorHiddenInGame(false);}
 if(S.Camera.IsValid())S.Camera->Destroy();S=FDeath();
}
FVector CameraPosition(UWorld* W,ACharacter* P,FVector Feet){
 const FVector Focus=Feet+FVector(0,0,100);FVector Best=Focus+FVector(0,0,120);double Score=-1;
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisDeathCamera),true,P);
 for(TActorIterator<AActor> I(W);I;++I)if(I->GetOwner()==P||I->ActorHasTag(TEXT("ParisEquipmentOwned")))Q.AddIgnoredActor(*I);
 for(double Offset:{135.,-135.,90.,-90.,180.,45.,-45.,0.}){
  const FVector Out=FRotator(0,P->GetActorRotation().Yaw+Offset,0).Vector();const FVector Want=Feet+Out*420+FVector(0,0,210);FHitResult Hit;
  const bool Blocked=W->SweepSingleByChannel(Hit,Focus,Want,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(14),Q);
  const FVector At=Blocked?Hit.Location+Hit.Normal*4:Want;const double Distance=FVector::Distance(At,Focus);
  if(Distance>Score){Score=Distance;Best=At;}
 }
 return Best;
}
void Start(UWorld* W,ACharacter* P,FDeath& S){
 auto* PC=UGameplayStatics::GetPlayerController(W,0);auto* Mesh=P->GetMesh();if(!PC||!Mesh)return;
 S.Player=P;S.Started=true;S.At=W->GetTimeSeconds();S.Previous=PC->GetViewTarget();S.Feet=P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
 S.MeshHidden=Mesh->bHiddenInGame;S.MeshVisible=Mesh->IsVisible();S.OwnerNoSee=Mesh->bOwnerNoSee;S.TickPolicy=Mesh->VisibilityBasedAnimTickOption;
 if(auto* D=ParisActionBindings::Display(P)){uint8 Tick=uint8(S.TickPolicy);if(D->UnifiedNativeBodyDefaults(S.MeshHidden,S.OwnerNoSee,Tick)){S.TickPolicy=EVisibilityBasedAnimTickOption(Tick);S.Previous=P;}}
 Mesh->SetHiddenInGame(false);Mesh->SetVisibility(true);Mesh->SetOwnerNoSee(false);Mesh->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
 for(TActorIterator<AActor> I(W);I;++I)if(I->GetOwner()==P&&Object(*I,TEXT("Pose"))&&Object(*I,TEXT("Gun"))&&!I->IsHidden()){S.HiddenDisplays.Add(*I);I->SetActorHiddenInGame(true);}
 auto* Single=Mesh->GetSingleNodeInstance();S.Remaining=Single?FMath::Max(0.f,Single->GetLength()-Single->GetCurrentTime()):4.;
 S.Camera=W->SpawnActor<ACameraActor>();check(S.Camera.IsValid());S.Camera->Tags.Add(TEXT("ParisDeathCameraOwned"));S.CameraAt=CameraPosition(W,P,S.Feet);
 S.Camera->SetActorLocation(S.CameraAt);S.Camera->SetActorRotation((S.Feet+FVector(0,0,115)-S.CameraAt).Rotation());S.Camera->GetCameraComponent()->SetFieldOfView(70);
 PC->FlushPressedKeys();PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);PC->SetViewTarget(S.Camera.Get());if(PC->PlayerCameraManager)PC->PlayerCameraManager->SetGameCameraCutThisFrame();
 UE_LOG(LogTemp,Display,TEXT("PARIS_PLAYER_DEATH started clip=%s time=%.6f remaining=%.6f camera=%s mesh=%s"),Single&&Single->GetCurrentAsset()?*Single->GetCurrentAsset()->GetName():TEXT("None"),Single?Single->GetCurrentTime():-1.,S.Remaining,*S.CameraAt.ToString(),*Mesh->GetSkeletalMeshAsset()->GetPathName());
}
void Tick(UWorld* W,ELevelTick,float DT){
 if(!W||!W->IsGameWorld()||UGameplayStatics::IsGamePaused(W))return;auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!P)return;auto& S=States.FindOrAdd(W);
 if(S.Started&&(S.Player.Get()!=P||!Dead(P)))Reset(W,S);
 if(Dead(P)&&!S.Started)Start(W,P,S);
 if(S.Started&&!S.Finished){
  const double Age=W->GetTimeSeconds()-S.At;auto* Single=P->GetMesh()->GetSingleNodeInstance();
  const double T=FMath::Clamp(Age/FMath::Max(.1,S.Remaining),0.,1.);if(S.Camera.IsValid())S.Camera->SetActorRotation((S.Feet+FVector(0,0,115-70*T)-S.CameraAt).Rotation());
  const bool Terminal=Single&&Single->GetLength()>0&&Single->GetCurrentTime()>=Single->GetLength()-.025;
  if(Terminal&&Age>=S.Remaining+.25){Single->SetPlaying(false);S.Finished=true;S.FinishedAt=W->GetTimeSeconds();if(auto* PC=UGameplayStatics::GetPlayerController(W,0)){PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);PC->FlushPressedKeys();}UE_LOG(LogTemp,Display,TEXT("PARIS_PLAYER_DEATH complete elapsed=%.6f clip_time=%.6f"),Age,Single->GetCurrentTime());}
  else if(Age>S.Remaining+2){UE_LOG(LogTemp,Error,TEXT("PARIS_PLAYER_DEATH original clip did not reach terminal; presentation watchdog"));S.Finished=true;S.FinishedAt=W->GetTimeSeconds();if(auto* PC=UGameplayStatics::GetPlayerController(W,0)){PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);}}
 }
}
}
bool Presenting(const UObject* O){auto* W=O?O->GetWorld():nullptr;if(!W||!Dead(UGameplayStatics::GetPlayerCharacter(W,0)))return false;const auto* S=States.Find(W);return !S||!S->Finished;}
bool Complete(const UObject* O){const auto* S=O?States.Find(O->GetWorld()):nullptr;return S&&S->Started&&S->Finished;}
TSharedPtr<FJsonObject> Inspect(UWorld* W){auto O=MakeShared<FJsonObject>();const auto* S=States.Find(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* Single=P?P->GetMesh()->GetSingleNodeInstance():nullptr;O->SetBoolField(TEXT("started"),S&&S->Started);O->SetBoolField(TEXT("complete"),S&&S->Finished);O->SetBoolField(TEXT("presenting"),Presenting(W));O->SetNumberField(TEXT("age"),S&&S->Started?W->GetTimeSeconds()-S->At:0);O->SetNumberField(TEXT("clip_time"),Single?Single->GetCurrentTime():-1);O->SetNumberField(TEXT("clip_length"),Single?Single->GetLength():-1);O->SetBoolField(TEXT("playing"),Single&&Single->IsPlaying());O->SetStringField(TEXT("clip"),Single&&Single->GetCurrentAsset()?Single->GetCurrentAsset()->GetName():TEXT("None"));O->SetBoolField(TEXT("body_visible"),P&&P->GetMesh()->IsVisible()&&!P->GetMesh()->bHiddenInGame&&!P->GetMesh()->bOwnerNoSee);auto* PC=UGameplayStatics::GetPlayerController(W,0);O->SetBoolField(TEXT("camera_owned"),PC&&S&&S->Camera.IsValid()&&PC->GetViewTarget()==S->Camera.Get());return O;}
#include "ParisPlayerDeathProbe.inl"
void Initialize(){TickHandle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);CleanupHandle=FWorldDelegates::OnWorldCleanup.AddLambda([](UWorld* W,bool,bool){States.Remove(W);});InitializeProbe();}
void Shutdown(){ShutdownProbe();FWorldDelegates::OnWorldPostActorTick.Remove(TickHandle);FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);States.Empty();}
}
