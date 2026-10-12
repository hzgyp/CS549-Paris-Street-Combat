#include "ParisTeamP1.h"
#include "ParisBridgeMission.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "UObject/UnrealType.h"

namespace ParisTeamP1 {
namespace {
double Num(const UObject* O,const TCHAR* N) {
 const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),N):nullptr;
 if(!P)return -9999;const void* V=P->ContainerPtrToValuePtr<void>(O);
 return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));
}
bool Flag(const UObject* O,const TCHAR* N) {const auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),N):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
FString State(const UObject* O) {const auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),TEXT("ActionState")):nullptr;return P?P->GetPropertyValue_InContainer(O).ToString():FString();}
bool Put(UObject* O,const TCHAR* N,double V) {
 auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),N):nullptr;if(!P)return false;
 void* D=P->ContainerPtrToValuePtr<void>(O);if(P->IsFloatingPoint())P->SetFloatingPointPropertyValue(D,V);else P->SetIntPropertyValue(D,int64(V));return true;
}
}
bool ConfigureFreshLoadout(ACharacter* P) {
 const double L=Num(P,TEXT("LoadedAmmo")),R=Num(P,TEXT("ReserveAmmo"));
 if(Num(P,TEXT("Capacity"))!=8||L!=2||R!=16)return false;
 // Initial distribution only; original fire/reload transactions remain authoritative.
 return Put(P,TEXT("LoadedAmmo"),8)&&Put(P,TEXT("ReserveAmmo"),10)&&Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))==L+R;
}
void UpdatePlayerMovement(ACharacter* P,bool Paused) {
 if(!P||!P->ActorHasTag(TEXT("G1_Player")))return;
 auto* Move=P->GetCharacterMovement();auto* Body=P->GetMesh();if(!Move||!Body)return;
 const bool Running=Flag(P,TEXT("RunHeld")),Slow=Flag(P,TEXT("SlowHeld"));
 const double Posture=Num(P,TEXT("DesiredPosture"));
 if(!Paused&&Posture==0&&!Flag(P,TEXT("IsDead")))Move->MaxWalkSpeed=Slow?65.f:Running?450.f:220.f;
 // Only the existing grounded standing locomotion graph changes cadence.
 const bool Cadence=!Paused&&Posture==0&&!P->bIsCrouched&&Move->IsMovingOnGround()&&P->GetVelocity().Size2D()>12&&State(P)==TEXT("Ready")&&Body->GetAnimationMode()==EAnimationMode::AnimationBlueprint&&!Flag(P,TEXT("IsDead"))&&!Slow;
 // Retained Stride_v1 already calibrates 0..300cm/s samples. Do not double-scale
 // the interpolated 220cm/s walk. Compensate only above its outer 300cm/s ring.
 Body->GlobalAnimRateScale=Cadence?float(FMath::Max(1.0,P->GetVelocity().Size2D()/300.0)):1.f;
}
bool ConfigureFreshLayout(AParisBridgeMission* M,FString& Error) {
 auto* W=M->GetWorld();auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);
 if(!Nav){Error=TEXT("P1 initial layout: native navigation missing");return false;}
 // Fixed 25cm measured candidates from full_filters; native cooked-map admission follows.
 const TCHAR* Tags[]={TEXT("G1_Ally1"),TEXT("G1_Ally2"),TEXT("G1_German1"),TEXT("G1_German2"),TEXT("G1_German3")};
 const FVector2D XY[]={ {1562.5,-21212.5},{1312.5,-20787.5},{6737.5,-20437.5},{7437.5,-19962.5},{7362.5,-20812.5} };
 ACharacter* Actors[5]={};FVector Targets[5];
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisP1InitialLayout),false);
 for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Player")))Q.AddIgnoredActor(*I);
 for(int32 K=0;K<5;++K) {
  for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(Tags[K])){if(Actors[K]){Error=TEXT("P1 duplicate initial identity");return false;}Actors[K]=*I;}
  if(!Actors[K]){Error=TEXT("P1 missing initial identity");return false;}Q.AddIgnoredActor(Actors[K]);
 }
 // Admit every target before moving any actor; no search/retry or collision exception.
 for(int32 K=0;K<5;++K) {
  auto* C=Actors[K];const FVector Old=C->GetNavAgentLocation();FNavLocation Projected;
  const FVector Proposed(XY[K].X,XY[K].Y,Old.Z);
  const auto& Agent=C->GetCharacterMovement()->GetNavAgentPropertiesRef();
  if(!Nav->ProjectPointToNavigation(Proposed,Projected,FVector(25,25,150),&Agent)||FVector::Dist2D(Projected.Location,Proposed)>25) {Error=FString::Printf(TEXT("P1 %s initial nav projection rejected"),Tags[K]);return false;}
  FHitResult Ground;
  if(!W->LineTraceSingleByChannel(Ground,Projected.Location+FVector(0,0,100),Projected.Location-FVector(0,0,100),ECC_Visibility,Q)||Ground.ImpactNormal.Z<.7||FMath::Abs(Ground.ImpactPoint.Z-Projected.Location.Z)>20) {Error=FString::Printf(TEXT("P1 %s initial ground rejected"),Tags[K]);return false;}
  const double HH=C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),RR=C->GetCapsuleComponent()->GetScaledCapsuleRadius();
  Targets[K]=FVector(Projected.Location.X,Projected.Location.Y,Ground.ImpactPoint.Z+HH+1.0);
  if(W->OverlapBlockingTestByProfile(Targets[K],C->GetActorQuat(),C->GetCapsuleComponent()->GetCollisionProfileName(),FCollisionShape::MakeCapsule(RR,HH),Q)) {Error=FString::Printf(TEXT("P1 %s initial capsule blocked"),Tags[K]);return false;}
  const FVector Goal=K<2?M->FarBankFeet:M->BridgeheadFeet;
  for(const FVector End:{Projected.Location,Goal}) {
   const FVector Start=End==Goal?Projected.Location:Old;
   auto* Path=UNavigationSystemV1::FindPathToLocationSynchronously(W,Start,End,C);
   if(!Path||!Path->IsValid()||Path->IsPartial()||Path->PathPoints.Num()<2) {Error=FString::Printf(TEXT("P1 %s initial complete path rejected"),Tags[K]);return false;}
  }
  for(int32 J=0;J<K;++J)if(FVector::Dist2D(Targets[K],Targets[J])<2*RR+20){Error=TEXT("P1 initial actor spacing rejected");return false;}
  UE_LOG(LogTemp,Display,TEXT("PARIS_P1_LAYOUT_ADMIT id=%s feet=%s capsule=clear paths=complete ground_normal=%.6f"),Tags[K],*(Targets[K]-FVector(0,0,HH)).ToString(),Ground.ImpactNormal.Z);
 }
 for(int32 K=0;K<5;++K) {Actors[K]->SetActorLocation(Targets[K],false);Actors[K]->GetCharacterMovement()->StopMovementImmediately();}
 return true;
}
FVector2D RadarPoint(FVector V,FVector P,double CX,double CY,double R) {return FVector2D(CX+(V.X-P.X)*R/RadarRadiusCm,CY-(V.Y-P.Y)*R/RadarRadiusCm);}
FVector2D SurveyUV(FVector V) {return FVector2D(V.X/10000,(-15000-V.Y)/10000);}
TArray<FVector2D> ClipSurvey(const TArray<FVector2D>& Polygon) {
 TArray<FVector2D> A=Polygon;
 for(int32 Edge=0;Edge<4;++Edge) {
  TArray<FVector2D> B;if(A.IsEmpty())return B;
  auto D=[&](FVector2D P){return Edge==0?P.X:Edge==1?10000-P.X:Edge==2?P.Y+25000:-15000-P.Y;};
  FVector2D Prev=A.Last();double DP=D(Prev);
  for(FVector2D P:A) {const double DV=D(P);if((DP>=0)!=(DV>=0))B.Add(Prev+(P-Prev)*(DP/(DP-DV)));if(DV>=0)B.Add(P);Prev=P;DP=DV;}A=MoveTemp(B);
 }
 return A;
}
}
