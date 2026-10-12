// Fixed fresh-task configuration from survey_v1 and paths_v1. No saved-state override.
#include "ParisFreshLayout.h"
#include "ParisBridgeMission.h"
#include "AIController.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"

namespace ParisFreshLayout {
namespace {
bool Complete(UWorld* W,ACharacter* C,FVector Start,FVector End) {
 auto* P=UNavigationSystemV1::FindPathToLocationSynchronously(W,Start,End,C);
 return P&&P->IsValid()&&!P->IsPartial()&&P->PathPoints.Num()>=2;
}
bool Captured(const UObject* O,const TCHAR* Name) {
 auto* P=FindFProperty<FBoolProperty>(O->GetClass(),Name);return P&&P->GetPropertyValue_InContainer(O);
}
}
bool Apply(AParisBridgeMission* M,const TArray<TObjectPtr<ACharacter>>& Roster,FString& Error) {
 auto* W=M->GetWorld();auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);
 if(!Nav||Roster.Num()!=6){Error=TEXT("Measured layout requires original six actors and native navigation");return false;}
 const FVector Measured[]={FVector(1512.5,-21462.5,94.399),FVector(1487.5,-20837.5,96.835),FVector(6612.5,-20662.5,108.228),FVector(7387.5,-19937.5,264.324),FVector(7738.631,-21337.367,165.227)};
 const TCHAR* Names[]={TEXT("Ally1"),TEXT("Ally2"),TEXT("German1"),TEXT("German2"),TEXT("German3")};
 FVector Targets[5],Feet[5];UFunction* Role[5]={};AAIController* Controllers[5]={};
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisMeasuredLayout),false);
 for(ACharacter* C:Roster){if(!IsValid(C)){Error=TEXT("Measured layout roster missing");return false;}Q.AddIgnoredActor(C);}
 // Admit all static volumes, route/spacing and original configuration contracts before writes.
 for(int32 K=0;K<5;++K) {
  auto* C=Roster[K+1].Get();const FVector Old=C->GetNavAgentLocation();
  if(!C->ActorHasTag(FName(*(FString(TEXT("G1_"))+Names[K])))){Error=TEXT("Measured layout identity mismatch");return false;}
  const auto& Agent=C->GetCharacterMovement()->GetNavAgentPropertiesRef();FNavLocation P;
  const FVector Proposed=K==1?Old:Measured[K];
  if(!Nav->ProjectPointToNavigation(Proposed,P,FVector(25,25,150),&Agent)||FVector::Dist2D(P.Location,Proposed)>25){Error=FString::Printf(TEXT("Measured %s projection rejected"),Names[K]);return false;}
  FHitResult H;
  if(!W->LineTraceSingleByChannel(H,P.Location+FVector(0,0,100),P.Location-FVector(0,0,100),ECC_Visibility,Q)||H.ImpactNormal.Z<.7||FMath::Abs(H.ImpactPoint.Z-P.Location.Z)>20){Error=FString::Printf(TEXT("Measured %s ground rejected"),Names[K]);return false;}
  const double HH=C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),Radius=C->GetCapsuleComponent()->GetScaledCapsuleRadius();
  Targets[K]=K==1?C->GetActorLocation():FVector(P.Location.X,P.Location.Y,H.ImpactPoint.Z+HH+1);
  Feet[K]=Targets[K]-FVector(0,0,HH);
  if(K!=1&&FVector::Dist2D(Feet[K],Measured[K])>25){Error=TEXT("Measured target no longer matches its survey cell");return false;}
  if(W->OverlapBlockingTestByProfile(Targets[K],C->GetActorQuat(),C->GetCapsuleComponent()->GetCollisionProfileName(),FCollisionShape::MakeCapsule(Radius,HH),Q)){Error=FString::Printf(TEXT("Measured %s capsule blocked"),Names[K]);return false;}
  if((K!=1&&!Complete(W,C,Old,Feet[K]))||!Complete(W,C,Feet[K],K<2?M->FarBankFeet:M->BridgeheadFeet)){Error=FString::Printf(TEXT("Measured %s complete path rejected"),Names[K]);return false;}
  if(K<2&&FVector::Dist2D(Feet[K],Roster[0]->GetNavAgentLocation())<350){Error=TEXT("Measured ally too close to player");return false;}
  for(int32 J=0;J<K;++J)if(FVector::Dist2D(Feet[K],Feet[J])<((K<2&&J<2)?500:350)){Error=TEXT("Measured actor pair spacing rejected");return false;}
  Controllers[K]=Cast<AAIController>(C->GetController());Role[K]=Controllers[K]?Controllers[K]->FindFunction(TEXT("PC_SetSearchRole")):nullptr;
  if(!Role[K]||!FindFProperty<FBoolProperty>(Role[K],TEXT("Patrol"))||!FindFProperty<FDoubleProperty>(Role[K],TEXT("Radius"))){Error=TEXT("Original role configuration signature missing");return false;}
  auto* RP=FindFProperty<FStructProperty>(Role[K],TEXT("PatrolPoint"));
  if(!RP||RP->Struct!=TBaseStructure<FVector>::Get()){Error=TEXT("Original role vector signature missing");return false;}
  for(const TCHAR* Field:{TEXT("GuardAnchor"),TEXT("HomePoint")}){auto* V=FindFProperty<FStructProperty>(Controllers[K]->GetClass(),Field);if(!V||V->Struct!=TBaseStructure<FVector>::Get()){Error=TEXT("Original anchor configuration signature missing");return false;}}
  UE_LOG(LogTemp,Display,TEXT("PARIS_MEASURED_LAYOUT_ADMIT id=%s feet=%s ground=%s normal=%.6f retained=%d paths=complete capsule=clear"),Names[K],*Feet[K].ToString(),*GetPathNameSafe(H.GetActor()),H.ImpactNormal.Z,K==1);
 }
 // Ally2 keeps its exact current actor transform. Native equipment continues to follow hands.
 for(int32 K=0;K<5;++K)if(K!=1) {
  auto* C=Roster[K+1].Get();C->SetActorLocation(Targets[K],false);C->GetCharacterMovement()->StopMovementImmediately();
  FStructOnScope Args(Role[K]);auto* BP=FindFProperty<FBoolProperty>(Role[K],TEXT("Patrol"));BP->SetPropertyValue_InContainer(Args.GetStructMemory(),false);
  *FindFProperty<FStructProperty>(Role[K],TEXT("PatrolPoint"))->ContainerPtrToValuePtr<FVector>(Args.GetStructMemory())=Targets[K];FindFProperty<FDoubleProperty>(Role[K],TEXT("Radius"))->SetPropertyValue_InContainer(Args.GetStructMemory(),500);
  Controllers[K]->ProcessEvent(Role[K],Args.GetStructMemory());
  for(const auto& Pair:{TPair<const TCHAR*,const TCHAR*>(TEXT("AnchorCaptured"),TEXT("GuardAnchor")),TPair<const TCHAR*,const TCHAR*>(TEXT("HomeCaptured"),TEXT("HomePoint"))})if(Captured(Controllers[K],Pair.Key))*FindFProperty<FStructProperty>(Controllers[K]->GetClass(),Pair.Value)->ContainerPtrToValuePtr<FVector>(Controllers[K])=Targets[K];
 }
 UE_LOG(LogTemp,Display,TEXT("PARIS_MEASURED_LAYOUT_APPLIED moved=4 retained_ally2=1 original_roster=6"));return true;
}
}
