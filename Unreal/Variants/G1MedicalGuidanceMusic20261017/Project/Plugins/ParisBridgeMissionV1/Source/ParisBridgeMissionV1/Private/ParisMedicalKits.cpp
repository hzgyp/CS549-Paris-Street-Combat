#include "ParisMedicalKits.h"
#include "ParisTutorialSoundscape.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundWaveProcedural.h"
#include "UObject/UObjectIterator.h"
#include "AudioMixerBlueprintLibrary.h"
#include "ParisMedicalPolicy.h"
#include "ParisMedicalAction.h"
#include "ParisFirstPersonApprovedActor.h"
#include "Components/PoseableMeshComponent.h"
#include "ParisBridgeMission.h"
#include "ParisTutorial.h"
#include "ParisCombatUI.h"
#include "ParisPlayerDeath.h"
#include "ParisEquipmentState.h"
#include "ParisTacticalEquipment.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonWriter.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonValue.h"
#include "UObject/StructOnScope.h"
#include "AIController.h"
#include "BrainComponent.h"
#include "Animation/AnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "CollisionShape.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "Engine/OverlapResult.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "Dom/JsonObject.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include "UnrealClient.h"

namespace ParisMedicalKits {
namespace {
using ParisMedicalPolicy::Claim;
const TCHAR* Ids[]={TEXT("German1"),TEXT("German2"),TEXT("German3"),TEXT("MedicalSupply2")};
constexpr const TCHAR* MeshPath=TEXT("/Game/ParisCombat/Props/MedicalPouch20261017V2/SM_MedicalPouch.SM_MedicalPouch");
struct FSource {
 Claim State=Claim::Waiting;bool HasKit=false,Located=false;
 FVector Position=FVector::ZeroVector;TWeakObjectPtr<AActor> Visual;
};
struct FState {
 uint32 Seed=1;bool Initialized=false,Legacy=false,HDown=false,Treating=false,RequireRelease=false;
 int32 Held=0,Used=0;FSource Sources[4];
 double Elapsed=0,StartedHP=0,RestoreGeneration=-1,NoticeUntil=0,NextSiteTry=0;
 TWeakObjectPtr<ACharacter> Player;FString Generation,Notice;
};
TMap<UWorld*,FState> States;FDelegateHandle Cleanup;
TStrongObjectPtr<UStaticMesh> Mesh;bool MeshAttempted=false;
double Num(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!F)return -1;auto* V=F->ContainerPtrToValuePtr<void>(O);return F->IsFloatingPoint()?F->GetFloatingPointPropertyValue(V):F->GetSignedIntPropertyValue(V);}
bool Flag(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FBoolProperty>(O->GetClass(),K):nullptr;return F&&F->GetPropertyValue_InContainer(O);}
FName Name(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr;return F?F->GetPropertyValue_InContainer(O):NAME_None;}
bool PutHealth(ACharacter* P,double HP){auto* F=P?FindFProperty<FNumericProperty>(P->GetClass(),TEXT("Health")):nullptr;if(!F)return false;auto* V=F->ContainerPtrToValuePtr<void>(P);if(F->IsFloatingPoint())F->SetFloatingPointPropertyValue(V,HP);else F->SetIntPropertyValue(V,int64(HP));return true;}
bool Alive(const ACharacter* P){return IsValid(P)&&!Flag(P,TEXT("IsDead"))&&Num(P,TEXT("Health"))>0;}
ACharacter* Actor(UWorld* W,const TCHAR* Id){const FName Tag(*(FString(TEXT("G1_"))+Id));for(TActorIterator<ACharacter>I(W);I;++I)if(I->ActorHasTag(Tag))return *I;return nullptr;}
uint32 Seed(const FString& Key){FTCHARToUTF8 Bytes(*Key);return ParisMedicalPolicy::Hash(Bytes.Get());}
void Notice(UWorld* W,FState& S,const TCHAR* Text){S.Notice=Text;S.NoticeUntil=W->GetTimeSeconds()+4;}
void End(UWorld* W,FState& S,const TCHAR* Why){if(S.Treating){ParisMedicalAction::End(S.Player.Get());UE_LOG(LogTemp,Display,TEXT("PARIS_MEDICAL cancel=%s held=%d used=%d"),Why,S.Held,S.Used);if(Why[0])Notice(W,S,Why);}S.Treating=false;S.Elapsed=0;S.RequireRelease=S.HDown;}
void RemoveVisuals(FState& S){for(auto& A:S.Sources)if(A.Visual.IsValid()){A.Visual->Destroy();A.Visual.Reset();}}
FState& State(UWorld* W){
 if(!Cleanup.IsValid())Cleanup=FWorldDelegates::OnWorldCleanup.AddLambda([](UWorld* World,bool,bool){if(auto* S=States.Find(World)){End(World,*S,TEXT(""));RemoveVisuals(*S);States.Remove(World);}});
 auto& S=States.FindOrAdd(W);
 if(!S.Initialized){auto* M=AParisBridgeMission::Find(W);S.Generation=M?M->RunGeneration:TEXT("medical-before-mission");S.Seed=Seed(S.Generation+TEXT("|medical-v1"));for(int I=0;I<4;++I)S.Sources[I].HasKit=ParisMedicalPolicy::Eligible(S.Seed,I);S.Initialized=true;}
 return S;
}
bool LivePlay(UWorld* W){auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));return M&&PC&&(M->AllowsPlay()||M->Phase==TEXT("Won"))&&!UGameplayStatics::IsGamePaused(W)&&!ParisCombatUI::IsOpen(PC)&&!ParisPlayerDeath::Presenting(PC)&&!M->CheckpointDialogVisible()&&!M->CheckpointPromptVisible&&!ParisTutorial::DialogVisible(M);}
bool Focused(UWorld* W){auto* V=W->GetGameViewport();return !V||(V->Viewport&&V->Viewport->HasFocus());}
bool ControlsIdle(ACharacter* P){auto* PC=P?Cast<APlayerController>(P->GetController()):nullptr;if(!PC)return false;for(const FKey K:{EKeys::W,EKeys::A,EKeys::S,EKeys::D,EKeys::SpaceBar,EKeys::LeftShift,EKeys::RightShift,EKeys::LeftMouseButton,EKeys::RightMouseButton,EKeys::R})if(PC->IsInputKeyDown(K))return false;return true;}
bool Ready(ACharacter* P,UWorld* W){auto& E=ParisTacticalEquipment::Session(W);return ControlsIdle(P)&&Name(P,TEXT("ActionState"))==TEXT("Ready")&&E.ThrowKind.IsEmpty()&&!E.EHeld&&E.SelectedSlot==0&&!E.PrimaryHeld;}
UStaticMesh* PouchMesh(){if(!MeshAttempted){MeshAttempted=true;Mesh.Reset(LoadObject<UStaticMesh>(nullptr,MeshPath));if(!Mesh.IsValid())UE_LOG(LogTemp,Error,TEXT("PARIS_MEDICAL_DEPENDENCY_MISSING %s; no invisible pickup/grant"),MeshPath);}return Mesh.Get();}
bool Ground(UWorld* W,FVector Near,FVector& Out,bool DeathDrop){
 auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);if(!Nav)return false;
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisMedicalDrop),false);
 for(TActorIterator<ACharacter>I(W);I;++I)Q.AddIgnoredActor(*I);
 for(const auto& Pair:States)if(Pair.Key==W)for(const auto& A:Pair.Value.Sources)if(A.Visual.IsValid())Q.AddIgnoredActor(A.Visual.Get());
 // Keep the intact pouch beside a casualty rather than hidden under its body.
 for(const FVector Offset:{FVector(140,0,0),FVector(-140,0,0),FVector(0,140,0),FVector(0,-140,0),FVector(100,100,0),FVector(-100,100,0),FVector(100,-100,0),FVector(-100,-100,0),FVector(0,0,0)}){
  FNavLocation N;if(!Nav->ProjectPointToNavigation(Near+Offset,N,FVector(55,55,240)))continue;
  if(DeathDrop&&FVector::DistSquared2D(N.Location,Near)<FMath::Square(100.))continue;
  FHitResult Hit;if(!W->LineTraceSingleByChannel(Hit,N.Location+FVector(0,0,90),N.Location-FVector(0,0,160),ECC_Visibility,Q)||Hit.ImpactNormal.Z<.7)continue;
  auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!P)continue;const auto* C=P->GetCapsuleComponent();
  if(W->OverlapBlockingTestByChannel(Hit.ImpactPoint+FVector(0,0,C->GetScaledCapsuleHalfHeight()+2),FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(C->GetScaledCapsuleRadius(),C->GetScaledCapsuleHalfHeight()),Q))continue;
  auto* Path=UNavigationSystemV1::FindPathToLocationSynchronously(W,P->GetActorLocation(),Hit.ImpactPoint,P);if(!Path||!Path->IsValid()||Path->IsPartial())continue;
  Out=Hit.ImpactPoint;return true;
 }return false;
}
void Visual(UWorld* W,FSource& A){
 if(A.State!=Claim::Available||!A.Located){if(A.Visual.IsValid()){A.Visual->Destroy();A.Visual.Reset();}return;}
 if(A.Visual.IsValid()||!PouchMesh())return;
 auto* V=W->SpawnActor<AActor>();if(!V)return;V->Tags.Add(TEXT("ParisMedicalPickup"));
 auto* C=NewObject<UStaticMeshComponent>(V);V->AddInstanceComponent(C);V->SetRootComponent(C);C->SetStaticMesh(PouchMesh());C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCanEverAffectNavigation(false);C->RegisterComponent();
 const auto Bounds=PouchMesh()->GetBounds();V->SetActorLocation(A.Position+FVector(0,0,Bounds.BoxExtent.Z-Bounds.Origin.Z+1));A.Visual=V;
}
void Sync(UWorld* W,FState& S){
 auto* M=AParisBridgeMission::Find(W);if(!M||!ParisTutorial::CombatStarted(M))return;
 const double Now=W->GetTimeSeconds();const bool TrySites=Now>=S.NextSiteTry;
 for(int I=0;I<4;++I){auto& A=S.Sources[I];
  if(A.State==Claim::Waiting){
   auto* Enemy=I<3?Actor(W,Ids[I]):nullptr;
   const bool AcceptedDeath=Enemy&&Num(Enemy,TEXT("TeamId"))==1&&Flag(Enemy,TEXT("IsDead"))&&Num(Enemy,TEXT("Health"))==0;
   if(I==3||AcceptedDeath){
    A.State=A.HasKit?Claim::Available:Claim::Miss;
    if(A.HasKit){if(I<3)A.Position=Enemy->GetActorLocation();else {const auto& E=ParisTacticalEquipment::Session(W);if(E.Supplies.Num()>1)A.Position=E.Supplies[1].Position+FVector(65,0,0);}}
    UE_LOG(LogTemp,Display,TEXT("PARIS_MEDICAL source=%s eligible=%d state=%d seed=%u"),Ids[I],A.HasKit,int(A.State),S.Seed);
   }
  }
  if(A.State==Claim::Available&&!A.Located&&TrySites){
   // Persist the death/site anchor before searching, so corpse removal cannot
   // erase an unlocated finite item or cause a reroll after restoration.
   A.Located=Ground(W,A.Position,A.Position,I<3);
  }
  const bool HadVisual=A.Visual.IsValid();Visual(W,A);
  if(I==0&&!HadVisual&&A.Visual.IsValid())Notice(W,S,TEXT("MEDICAL KIT DROPPED  |  APPROACH, AIM AT POUCH + E"));
 }
 if(TrySites)S.NextSiteTry=Now+1;
}
int Target(UWorld* W,FState& S){
 auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* PC=UGameplayStatics::GetPlayerController(W,0);if(!Alive(P)||!PC)return -1;
 // A visible checkpoint modal, a real mine target and active throw/disarm win.
 // After dismissing the checkpoint modal, pouches inside its circle stay usable.
 auto* M=AParisBridgeMission::Find(W);if(!M||M->CheckpointDialogVisible()||M->CheckpointPromptVisible)return -1;
 auto& E=ParisTacticalEquipment::Session(W);if(!E.ThrowKind.IsEmpty()||E.EHeld||ParisTacticalEquipment::HasArmedMineTarget(W))return -1;
 FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
 int Best=-1;double Score=-1;
 for(int I=0;I<4;++I){auto& A=S.Sources[I];if(A.State!=Claim::Available||!A.Located||!A.Visual.IsValid())continue;
  const FVector At=A.Position+FVector(0,0,8);if(FVector::Dist(P->GetActorLocation(),At)>200)continue;
  const double Dot=FVector::DotProduct(View.Vector(),(At-Eye).GetSafeNormal());if(Dot<.88||Dot<=Score)continue;
  FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisMedicalPickup),true,P);for(const auto& V:S.Sources)if(V.Visual.IsValid())Q.AddIgnoredActor(V.Visual.Get());
  // A corpse is the source, not an occluding wall. Other combatants stay physical.
  if(I<3)if(auto* Enemy=Actor(W,Ids[I]))Q.AddIgnoredActor(Enemy);
  FHitResult Hit;if(ParisTacticalEquipment::Occluded(W,Eye,At)||W->LineTraceSingleByChannel(Hit,Eye,At,ECC_Visibility,Q))continue;
  Best=I;Score=Dot;
 }return Best;
}
void Begin(UWorld* W,FState& S,ACharacter* P){
 const double HP=Num(P,TEXT("Health")),Max=Num(P,TEXT("MaxHealth"));
 if(!Alive(P))return;
 if(S.Held<=0){Notice(W,S,TEXT("NO MEDICAL KITS"));return;}
 if(HP>=Max){Notice(W,S,TEXT("HEALTH ALREADY FULL"));return;}
 if(ParisTacticalEquipment::Session(W).SelectedSlot!=0){Notice(W,S,TEXT("WHEEL TO RIFLE BEFORE TREATMENT"));return;}
 if(!ParisMedicalPolicy::CanStart(true,Ready(P,W),P->GetCharacterMovement()->IsMovingOnGround(),P->GetVelocity().Size()<=2,S.Held,HP,Max)){Notice(W,S,TEXT("STOP AND FINISH CURRENT ACTION TO TREAT"));return;}
 if(!ParisMedicalAction::Ready(P)){Notice(W,S,TEXT("TREATMENT ANIMATION NOT READY"));return;}
 if(!ParisMedicalAction::Begin(P,ParisMedicalPolicy::Seconds)){Notice(W,S,TEXT("TREATMENT ANIMATION NOT READY"));return;}
 S.Treating=true;S.Elapsed=0;S.StartedHP=HP;S.Player=P;S.RestoreGeneration=Num(P,TEXT("RestoreGeneration"));S.Notice.Empty();
 UE_LOG(LogTemp,Display,TEXT("PARIS_MEDICAL treatment_begin health=%.3f held=%d"),HP,S.Held);
}
}

void Tick(UWorld* W,float Delta){
 if(!ParisTutorial::Enabled())return;auto& S=State(W);auto* M=AParisBridgeMission::Find(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);
 if(!M)return;
 if(S.Generation!=M->RunGeneration){End(W,S,TEXT(""));RemoveVisuals(S);S=FState();S.Initialized=true;S.Generation=M->RunGeneration;S.Seed=Seed(S.Generation+TEXT("|medical-v1"));for(int I=0;I<4;++I)S.Sources[I].HasKit=ParisMedicalPolicy::Eligible(S.Seed,I);}
 Sync(W,S);
 if(!S.Treating)return;
 if(P!=S.Player.Get()||Num(P,TEXT("RestoreGeneration"))!=S.RestoreGeneration||!Alive(P)){End(W,S,TEXT("TREATMENT CANCELLED"));return;}
 if(Num(P,TEXT("Health"))!=S.StartedHP){End(W,S,TEXT("TREATMENT INTERRUPTED BY DAMAGE"));return;}
 if(!S.HDown||!LivePlay(W)||!Focused(W)||!ControlsIdle(P)||P->GetVelocity().Size()>2||!P->GetCharacterMovement()->IsMovingOnGround()||Name(P,TEXT("ActionState"))!=TEXT("Ready")){End(W,S,TEXT("TREATMENT CANCELLED"));return;}
 S.Elapsed+=FMath::Max(0.f,Delta);
 if(!ParisMedicalAction::Tick(P,S.Elapsed,ParisMedicalPolicy::Seconds)){End(W,S,TEXT("TREATMENT ANIMATION NOT READY"));return;}
 const double HP=Num(P,TEXT("Health"));
 if(ParisMedicalPolicy::CanCommit(S.Held>0&&Alive(P)&&LivePlay(W),S.Elapsed,HP,S.StartedHP)){
  const double New=ParisMedicalPolicy::Healed(HP,Num(P,TEXT("MaxHealth")));
  // No asynchronous notify owns health. This is one game-thread transaction.
  if(New>HP&&PutHealth(P,New)){--S.Held;++S.Used;End(W,S,TEXT(""));Notice(W,S,TEXT("TREATMENT COMPLETE"));UE_LOG(LogTemp,Display,TEXT("PARIS_MEDICAL committed before=%.3f after=%.3f held=%d used=%d"),HP,New,S.Held,S.Used);}
  else End(W,S,TEXT("TREATMENT CANCELLED"));
 }
}
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& A){
 if(!ParisTutorial::Enabled()||!PC)return false;auto* W=PC->GetWorld();auto& S=State(W);
 if(A.Key==EKeys::H){
  if(A.Event==IE_Released){S.HDown=false;End(W,S,TEXT("TREATMENT CANCELLED"));S.RequireRelease=false;return true;}
  if(A.Event!=IE_Pressed||S.HDown||S.RequireRelease)return true;S.HDown=true;
  if(LivePlay(W)&&Focused(W))Begin(W,S,UGameplayStatics::GetPlayerCharacter(W,0));return true;
 }
 if(S.Treating&&A.Event==IE_Pressed&&(A.Key==EKeys::W||A.Key==EKeys::A||A.Key==EKeys::S||A.Key==EKeys::D||A.Key==EKeys::SpaceBar||A.Key==EKeys::LeftShift||A.Key==EKeys::RightShift||A.Key==EKeys::LeftMouseButton||A.Key==EKeys::RightMouseButton||A.Key==EKeys::R||A.Key==EKeys::E||A.Key==EKeys::Z||A.Key==EKeys::LeftControl||A.Key==EKeys::RightControl||A.Key==EKeys::V||A.Key==EKeys::MouseScrollUp||A.Key==EKeys::MouseScrollDown||A.Key==EKeys::Escape||A.Key==EKeys::Tab||A.Key==EKeys::F5||A.Key==EKeys::F6||A.Key==EKeys::F9))End(W,S,TEXT("TREATMENT CANCELLED"));
 if(A.Key==EKeys::E&&A.Event==IE_Pressed&&LivePlay(W)&&!S.Treating){
  Sync(W,S);const int I=Target(W,S);if(I<0)return false;
  if(S.Held>=ParisMedicalPolicy::Capacity){Notice(W,S,TEXT("MEDICAL KITS FULL"));return true;}
  S.Sources[I].State=Claim::Claimed;++S.Held;Visual(W,S.Sources[I]);Notice(W,S,TEXT("MEDICAL KIT +1  |  HOLD H 3s: +50 HEALTH"));UE_LOG(LogTemp,Display,TEXT("PARIS_MEDICAL pickup=%s held=%d used=%d"),Ids[I],S.Held,S.Used);return true;
 }return false;
}
void Cancel(UWorld* W){if(auto* S=States.Find(W))End(W,*S,TEXT(""));}
bool Busy(UWorld* W){auto* S=States.Find(W);return S&&S->Treating;}
int32 Count(UWorld* W){return ParisTutorial::Enabled()?State(W).Held:0;}
FString PickupHint(UWorld* W){
 if(!ParisTutorial::Enabled())return FString();auto& S=State(W);
 if(Target(W,S)<0)return FString();return S.Held>=ParisMedicalPolicy::Capacity?TEXT("MEDICAL KITS FULL"):TEXT("E  PICK UP MEDICAL KIT");
}
FString Hint(UWorld* W){
 if(!ParisTutorial::Enabled())return FString();auto& S=State(W);
 if(S.Treating)return FString::Printf(TEXT("TREATING  %.1f / 3s  |  RELEASE H TO CANCEL"),FMath::Min(3.,S.Elapsed));
 const FString Pickup=PickupHint(W);if(!Pickup.IsEmpty())return Pickup;
 if(S.NoticeUntil>W->GetTimeSeconds())return S.Notice;
 auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(S.Held>0&&Alive(P)&&Num(P,TEXT("Health"))<Num(P,TEXT("MaxHealth")))return ParisTacticalEquipment::Session(W).SelectedSlot!=0?TEXT("WHEEL TO RIFLE BEFORE TREATMENT"):TEXT("STAND STILL + HOLD H 3s  |  HEAL UP TO 50");
 return FString();
}
float Progress(UWorld* W){auto* S=States.Find(W);return S&&S->Treating?float(FMath::Clamp(S->Elapsed/3.,0.,1.)):0.f;}
#include "ParisMedicalGuidance.inl"
#include "ParisMedicalSave.inl"
#include "ParisMedicalCheck.inl"
void Shutdown(){FWorldDelegates::OnWorldCleanup.Remove(Cleanup);Cleanup.Reset();for(auto& P:States){End(P.Key,P.Value,TEXT(""));RemoveVisuals(P.Value);}States.Empty();ParisMedicalAction::Shutdown();Mesh.Reset();MeshAttempted=false;}
}
