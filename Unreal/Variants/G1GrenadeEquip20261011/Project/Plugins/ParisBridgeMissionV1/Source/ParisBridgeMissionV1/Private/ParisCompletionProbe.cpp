// Finite read-only full-space survey. No actor/pose/resource/AI writes.
#include "ParisCompletionProbe.h"
#include "ParisBridgeMission.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Dom/JsonObject.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "NavigationSystem.h"
#include "NavigationData.h"
#include "NavigationPath.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"

namespace ParisCompletionProbe { namespace {
FString Out,CauseOut; FDelegateHandle Handle; double Begin=0; bool Finished=false,PathOnly=false,CauseSaved=false;
int32 Region=0,Point=0;TArray<TSharedPtr<FJsonValue>> Cells,Prone,Actors;
TSharedPtr<FJsonObject> Root=MakeShared<FJsonObject>();
struct FArea {const TCHAR* Id;double X,Y;};
const FArea Areas[]={{TEXT("Ally1"),1262.5,-21712.5},{TEXT("Ally2"),1012.5,-20462.5},{TEXT("German1"),6362.5,-20912.5},{TEXT("German2"),7137.5,-20187.5},{TEXT("German3"),7362.5,-21612.5}};
ACharacter* Find(UWorld* W,const TCHAR* Id) {for(TActorIterator<ACharacter> A(W);A;++A)if(A->ActorHasTag(FName(*(FString(TEXT("G1_"))+Id))))return *A;return nullptr;}
void Finish(const FString& Status) {
 if(Finished)return;Finished=true;Root->SetStringField(TEXT("status"),Status);Root->SetStringField(TEXT("scope"),TEXT("Read-only finite native full-space measurement, not spawn/traversal/human acceptance"));
 Root->SetArrayField(TEXT("npc_cells"),Cells);Root->SetArrayField(TEXT("prone_corridors"),Prone);Root->SetArrayField(TEXT("original_actors"),Actors);Root->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-Begin);
 FString S;auto Writer=TJsonWriterFactory<>::Create(&S);FJsonSerializer::Serialize(Root.ToSharedRef(),Writer);FFileHelper::SaveStringToFile(S,*(Out/TEXT("result.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);FPlatformMisc::RequestExit(false);
}
void IgnoreRoster(UWorld* W,FCollisionQueryParams& Q) {for(const TCHAR* Id:{TEXT("Player"),TEXT("Ally1"),TEXT("Ally2"),TEXT("German1"),TEXT("German2"),TEXT("German3")})if(auto* A=Find(W,Id))Q.AddIgnoredActor(A);}
bool CompletePath(UWorld* W,ACharacter* C,FVector A,FVector B) {auto* P=UNavigationSystemV1::FindPathToLocationSynchronously(W,A,B,C);return P&&P->IsValid()&&!P->IsPartial()&&P->PathPoints.Num()>=2;}
void PathWitness(UWorld* W,ACharacter* C,FVector B,const TCHAR* Label,TArray<TSharedPtr<FJsonValue>>& Rows) {
 auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);const auto& Agent=C->GetCharacterMovement()->GetNavAgentPropertiesRef();auto* Data=Nav->GetNavDataForProps(Agent,C->GetNavAgentLocation());
 const FVector Start=C->GetNavAgentLocation();FNavLocation AProj,BProj;const bool AP=Nav->ProjectPointToNavigation(Start,AProj,FVector(25,25,150),&Agent),BP=Nav->ProjectPointToNavigation(B,BProj,FVector(25,25,150),&Agent);
 auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("label"),Label);R->SetStringField(TEXT("start_feet"),Start.ToString());R->SetStringField(TEXT("end_feet"),B.ToString());R->SetStringField(TEXT("actor_center"),C->GetActorLocation().ToString());R->SetNumberField(TEXT("agent_radius"),Agent.AgentRadius);R->SetNumberField(TEXT("agent_height"),Agent.AgentHeight);R->SetStringField(TEXT("default_query_extent"),Data?Data->GetConfig().DefaultQueryExtent.ToString():TEXT("No nav data"));
 R->SetBoolField(TEXT("start_projected"),AP);R->SetBoolField(TEXT("end_projected"),BP);R->SetStringField(TEXT("start_nav"),AP?AProj.Location.ToString():TEXT("None"));R->SetStringField(TEXT("end_nav"),BP?BProj.Location.ToString():TEXT("None"));
 for(int32 Mode=0;Mode<2;++Mode) {
  auto* P=UNavigationSystemV1::FindPathToLocationSynchronously(W,Mode==0?Start:AProj.Location,Mode==0?B:BProj.Location,C);auto Q=MakeShared<FJsonObject>();Q->SetBoolField(TEXT("valid"),P&&P->IsValid());Q->SetBoolField(TEXT("partial"),P&&P->IsPartial());Q->SetNumberField(TEXT("points"),P?P->PathPoints.Num():0);TArray<TSharedPtr<FJsonValue>> Points;if(P)for(const FVector& PathPoint:P->PathPoints)Points.Add(MakeShared<FJsonValueString>(PathPoint.ToString()));Q->SetArrayField(TEXT("path"),Points);R->SetObjectField(Mode==0?TEXT("feet_query"):TEXT("projected_query"),Q);
 }Rows.Add(MakeShared<FJsonValueObject>(R));
}
bool Ground(UWorld* W,ACharacter* C,FVector Proposed,FVector& Feet,FHitResult& H) {
 auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);FNavLocation P;const auto& Agent=C->GetCharacterMovement()->GetNavAgentPropertiesRef();
 if(!Nav||!Nav->ProjectPointToNavigation(Proposed,P,FVector(25,25,150),&Agent)||FVector::Dist2D(P.Location,Proposed)>25)return false;
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisCompletionGround),false);IgnoreRoster(W,Q);
 if(!W->LineTraceSingleByChannel(H,P.Location+FVector(0,0,100),P.Location-FVector(0,0,100),ECC_Visibility,Q)||H.ImpactNormal.Z<.7||FMath::Abs(H.ImpactPoint.Z-P.Location.Z)>20)return false;
 Feet=FVector(P.Location.X,P.Location.Y,H.ImpactPoint.Z);return true;
}
bool Capsule(UWorld* W,ACharacter* C,FVector Feet,TArray<FOverlapResult>& Hits) {
 auto* Cap=C->GetCapsuleComponent();FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisCompletionCapsule),false);IgnoreRoster(W,Q);
 return !W->OverlapMultiByProfile(Hits,Feet+FVector(0,0,Cap->GetScaledCapsuleHalfHeight()+1),C->GetActorQuat(),Cap->GetCollisionProfileName(),FCollisionShape::MakeCapsule(Cap->GetScaledCapsuleRadius(),Cap->GetScaledCapsuleHalfHeight()),Q);
}
TSharedRef<FJsonObject> Cell(UWorld* W,AParisBridgeMission* M,const FArea& A,int32 I) {
 auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("id"),A.Id);auto* C=Find(W,A.Id);FVector Proposed(A.X+(I%21)*25,A.Y+(I/21)*25,C->GetNavAgentLocation().Z),Feet;FHitResult H;
 R->SetStringField(TEXT("proposed"),Proposed.ToString());const bool G=Ground(W,C,Proposed,Feet,H);R->SetBoolField(TEXT("ground"),G);if(!G)return R;
 R->SetStringField(TEXT("feet"),Feet.ToString());R->SetNumberField(TEXT("normal_z"),H.ImpactNormal.Z);R->SetStringField(TEXT("ground_actor"),H.GetActor()?H.GetActor()->GetPathName():TEXT("None"));
 TArray<FOverlapResult> Hits;const bool Clear=Capsule(W,C,Feet,Hits);R->SetBoolField(TEXT("capsule_clear"),Clear);TArray<TSharedPtr<FJsonValue>> Blocks;
 for(const auto& Hit:Hits)if(Hit.bBlockingHit){auto B=MakeShared<FJsonObject>();B->SetStringField(TEXT("actor"),Hit.GetActor()?Hit.GetActor()->GetPathName():TEXT("None"));B->SetStringField(TEXT("component"),Hit.GetComponent()?Hit.GetComponent()->GetName():TEXT("None"));Blocks.Add(MakeShared<FJsonValueObject>(B));}R->SetArrayField(TEXT("blocking"),Blocks);
 const bool OldPath=Clear&&CompletePath(W,C,C->GetNavAgentLocation(),Feet),GoalPath=Clear&&CompletePath(W,C,Feet,FString(A.Id).StartsWith(TEXT("Ally"))?M->FarBankFeet:M->BridgeheadFeet);
 R->SetBoolField(TEXT("old_to_new_complete"),OldPath);R->SetBoolField(TEXT("goal_complete"),GoalPath);R->SetBoolField(TEXT("admitted_static"),G&&Clear&&OldPath&&GoalPath);
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisCompletionSight),false);IgnoreRoster(W,Q);FHitResult Sight;FVector Eye;FRotator Rot;C->GetActorEyesViewPoint(Eye,Rot);
 const bool Block=W->LineTraceSingleByChannel(Sight,Feet+FVector(0,0,Eye.Z-C->GetNavAgentLocation().Z),M->FarBankFeet+FVector(0,0,150),ECC_Visibility,Q);
 R->SetBoolField(TEXT("sight_to_farbank"),!Block);R->SetStringField(TEXT("sight_blocker"),Sight.GetActor()?Sight.GetActor()->GetPathName():TEXT("None"));return R;
}
TSharedRef<FJsonObject> Corridor(UWorld* W,ACharacter* P,int32 I) {
 auto R=MakeShared<FJsonObject>();const FVector Proposed(1112.5+(I%17)*25,-20662.5+(I/17)*25,P->GetNavAgentLocation().Z);FVector GroundFeet;FHitResult H;
 R->SetStringField(TEXT("proposed"),Proposed.ToString());const bool G=Ground(W,P,Proposed,GroundFeet,H);R->SetBoolField(TEXT("ground"),G);if(!G)return R;
 // Keep the same floor tolerance; use the original walking floor separation.
 const FVector Feet=GroundFeet+FVector(0,0,2.15);R->SetStringField(TEXT("feet"),Feet.ToString());TArray<FOverlapResult> Hits;
 const bool Standing=Capsule(W,P,GroundFeet,Hits);R->SetBoolField(TEXT("standing_clear"),Standing);const bool Path=Standing&&CompletePath(W,P,P->GetNavAgentLocation(),Feet);R->SetBoolField(TEXT("complete_path"),Path);
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisCompletionProne),false);IgnoreRoster(W,Q);TArray<TSharedPtr<FJsonValue>> Stations;bool Clear=G&&Standing&&Path;
 for(int32 S=0;S<=16;++S) {
  auto V=MakeShared<FJsonObject>();const FVector At=Feet+FVector(S*25,0,0);FHitResult B;
  const bool Hit=W->SweepSingleByChannel(B,At+FVector(0,0,30),At+FVector(6,0,30),FQuat::Identity,ECC_Visibility,FCollisionShape::MakeBox(FVector(130,55,28)),Q);
  bool OK=!Hit;V->SetNumberField(TEXT("offset"),S*25);V->SetBoolField(TEXT("box_clear"),!Hit);V->SetStringField(TEXT("box_actor"),B.GetActor()?B.GetActor()->GetPathName():TEXT("None"));TArray<TSharedPtr<FJsonValue>> Floors;
  for(double Offset:{-120.,0.,110.}) {
   FHitResult F;const FVector Pt=At+FVector(Offset,0,0);const bool Found=W->LineTraceSingleByChannel(F,Pt+FVector(0,0,40),Pt-FVector(0,0,30),ECC_Visibility,Q);const bool Good=Found&&F.ImpactNormal.Z>=.97&&FMath::Abs(F.ImpactPoint.Z-At.Z)<=10;OK&=Good;
   auto Row=MakeShared<FJsonObject>();Row->SetNumberField(TEXT("offset"),Offset);Row->SetBoolField(TEXT("pass"),Good);Row->SetNumberField(TEXT("normal_z"),F.ImpactNormal.Z);Row->SetNumberField(TEXT("height_delta"),F.ImpactPoint.Z-At.Z);Row->SetStringField(TEXT("actor"),F.GetActor()?F.GetActor()->GetPathName():TEXT("None"));Floors.Add(MakeShared<FJsonValueObject>(Row));
  }V->SetArrayField(TEXT("floors"),Floors);V->SetBoolField(TEXT("pass"),OK);Clear&=OK;Stations.Add(MakeShared<FJsonValueObject>(V));
 }
 bool Dynamic=true;for(const TCHAR* Id:{TEXT("Ally1"),TEXT("Ally2")}) {auto* A=Find(W,Id);const FVector N=A->GetNavAgentLocation();const double Radius=A->GetCapsuleComponent()->GetScaledCapsuleRadius();if(N.X>=Feet.X-130-Radius&&N.X<=Feet.X+530+Radius&&FMath::Abs(N.Y-Feet.Y)<=55+Radius)Dynamic=false;}
 R->SetBoolField(TEXT("original_allies_outside_corridor"),Dynamic);R->SetArrayField(TEXT("stations"),Stations);R->SetBoolField(TEXT("admitted_static"),Clear&&Dynamic);return R;
}
void Tick(UWorld* W,ELevelTick,float) {
 if(Finished||!W||W->WorldType!=EWorldType::Game)return;if(FPlatformTime::Seconds()-Begin>180){Finish(TEXT("failed_finite_survey_deadline"));return;}
 auto* M=AParisBridgeMission::Find(W);if(!M)return;if(M->Phase==TEXT("Error")){Finish(TEXT("failed_preparation_")+M->Feedback);return;}if(M->Phase!=TEXT("Ready")||M->ReadySeconds<12)return;
 if(Actors.IsEmpty())for(const TCHAR* Id:{TEXT("Player"),TEXT("Ally1"),TEXT("Ally2"),TEXT("German1"),TEXT("German2"),TEXT("German3")}) {auto* C=Find(W,Id);if(!C){Finish(TEXT("failed_missing_roster"));return;}auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("id"),Id);A->SetStringField(TEXT("class"),C->GetClass()->GetPathName());A->SetStringField(TEXT("feet"),C->GetNavAgentLocation().ToString());A->SetNumberField(TEXT("radius"),C->GetCapsuleComponent()->GetScaledCapsuleRadius());A->SetNumberField(TEXT("half_height"),C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());Actors.Add(MakeShared<FJsonValueObject>(A));}
 if(PathOnly) {
  TArray<TSharedPtr<FJsonValue>> Paths;auto* A=Find(W,TEXT("Ally2"));auto* P=Find(W,TEXT("Player"));
  PathWitness(W,A,M->FarBankFeet,TEXT("original_ally2_to_farbank"),Paths);PathWitness(W,A,Find(W,TEXT("Ally1"))->GetNavAgentLocation(),TEXT("original_ally2_to_ally1"),Paths);PathWitness(W,A,FVector(1012.5,-20462.5,99.992),TEXT("ally2_to_measured_landscape_cell"),Paths);
  PathWitness(W,P,FVector(1762.5,-20662.5,114.402),TEXT("player_to_previously_physically_reached_prone_site"),Paths);PathWitness(W,P,FVector(1112.5,-20662.5,110.15),TEXT("player_to_first_measured_corridor"),Paths);
  Root->SetArrayField(TEXT("path_witnesses"),Paths);Finish(TEXT("pass_finite_read_only_path_witness"));return;
 }
 for(int32 Work=0;Work<12;++Work) {
  if(Region<5) {Cells.Add(MakeShared<FJsonValueObject>(Cell(W,M,Areas[Region],Point)));if(++Point==441){Point=0;++Region;}}
  else if(Region==5) {Prone.Add(MakeShared<FJsonValueObject>(Corridor(W,Find(W,TEXT("Player")),Point)));if(++Point==289){Point=0;++Region;}}
  else {Finish(TEXT("pass_finite_read_only_space_survey"));return;}
 }
}
}
void ObserveProneCause(ACharacter* P,bool NativeFuture) {
 if(CauseOut.IsEmpty()||CauseSaved||!P)return;const auto* Posture=FindFProperty<FNumericProperty>(P->GetClass(),TEXT("DesiredPosture"));const auto* Blocked=FindFProperty<FBoolProperty>(P->GetClass(),TEXT("ProneBlocked"));
 if(!Posture||Posture->GetSignedIntPropertyValue(Posture->ContainerPtrToValuePtr<void>(P))!=2||!Blocked||(!NativeFuture&&!Blocked->GetPropertyValue_InContainer(P)))return;
 CauseSaved=true;auto R=MakeShared<FJsonObject>();auto* W=P->GetWorld();const FVector Feet=P->GetNavAgentLocation(),Forward=P->GetActorForwardVector();const auto* Axis=FindFProperty<FNumericProperty>(P->GetClass(),TEXT("ProneProbeAxis"));const double AxisValue=Axis?Axis->GetFloatingPointPropertyValue(Axis->ContainerPtrToValuePtr<void>(P)):0;
 const FVector Future=Feet+(NativeFuture?P->GetPendingMovementInputVector().GetSafeNormal():Forward*AxisValue)*60*FMath::Max(.1,double(W->GetDeltaSeconds()));FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisProneCause),false,P);FHitResult H;
 const bool Hit=W->SweepSingleByChannel(H,Feet+FVector(0,0,30),Future+FVector(0,0,30),P->GetActorQuat(),ECC_Visibility,FCollisionShape::MakeBox(FVector(130,55,28)),Q);
 const auto* GunField=FindFProperty<FObjectPropertyBase>(P->GetClass(),TEXT("WeaponAppearance"));auto* Gun=GunField?Cast<AActor>(GunField->GetObjectPropertyValue_InContainer(P)):nullptr;
 R->SetStringField(TEXT("query_kind"),NativeFuture?TEXT("native_future"):TEXT("original_bp_current"));R->SetStringField(TEXT("feet"),Feet.ToString());R->SetStringField(TEXT("rotation"),P->GetActorRotation().ToString());R->SetStringField(TEXT("future"),Future.ToString());R->SetNumberField(TEXT("axis"),AxisValue);R->SetNumberField(TEXT("delta_seconds"),W->GetDeltaSeconds());R->SetBoolField(TEXT("box_hit"),Hit);R->SetStringField(TEXT("box_actor"),H.GetActor()?H.GetActor()->GetPathName():TEXT("None"));R->SetStringField(TEXT("box_component"),H.GetComponent()?H.GetComponent()->GetName():TEXT("None"));R->SetStringField(TEXT("box_point"),H.ImpactPoint.ToString());R->SetStringField(TEXT("box_normal"),H.ImpactNormal.ToString());R->SetStringField(TEXT("weapon"),Gun?Gun->GetPathName():TEXT("None"));R->SetBoolField(TEXT("box_hit_is_weapon"),Hit&&Gun&&H.GetActor()==Gun);R->SetStringField(TEXT("velocity"),P->GetVelocity().ToString());
 TArray<TSharedPtr<FJsonValue>> Floors;for(double Offset:{-120.,0.,110.}) {FHitResult F;const FVector Pt=(NativeFuture?Future:Feet)+Forward*Offset;const bool Found=W->LineTraceSingleByChannel(F,Pt+FVector(0,0,40),Pt-FVector(0,0,30),ECC_Visibility,Q);auto Row=MakeShared<FJsonObject>();Row->SetNumberField(TEXT("offset"),Offset);Row->SetStringField(TEXT("point"),Pt.ToString());Row->SetBoolField(TEXT("pass"),Found&&F.ImpactNormal.Z>=.97&&FMath::Abs(F.ImpactPoint.Z-(NativeFuture?Future.Z:Feet.Z))<=10);Row->SetNumberField(TEXT("normal_z"),F.ImpactNormal.Z);Row->SetNumberField(TEXT("height_delta"),F.ImpactPoint.Z-(NativeFuture?Future.Z:Feet.Z));Row->SetStringField(TEXT("actor"),F.GetActor()?F.GetActor()->GetPathName():TEXT("None"));Floors.Add(MakeShared<FJsonValueObject>(Row));}R->SetArrayField(TEXT("floors"),Floors);
 FString S;auto Writer=TJsonWriterFactory<>::Create(&S);FJsonSerializer::Serialize(R,Writer);IFileManager::Get().MakeDirectory(*CauseOut,true);const bool Saved=FFileHelper::SaveStringToFile(S,*(CauseOut/TEXT("CAUSE.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);UE_LOG(LogTemp,Display,TEXT("PARIS_PRONE_CAUSE saved=%d native_future=%d box_actor=%s"),Saved,NativeFuture,*GetPathNameSafe(H.GetActor()));
}
void Initialize(){FParse::Value(FCommandLine::Get(),TEXT("ParisProneCauseOut="),CauseOut);if(!FParse::Value(FCommandLine::Get(),TEXT("ParisSpaceSurveyOut="),Out)){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisPathWitnessOut="),Out))return;PathOnly=true;}IFileManager::Get().MakeDirectory(*Out,true);Begin=FPlatformTime::Seconds();Handle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);}
void Shutdown(){if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);}
}
