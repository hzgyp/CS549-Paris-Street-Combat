// Opt-in diagnostic input/observer for the private packaged closeout variant.
// No position, health, ammunition, pose or NPC brain writes. Not human play.
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"
#include "ParisBridgeMission.h"
#include "AIController.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "Blueprint/AIBlueprintHelperLibrary.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/GameViewportClient.h"
#include "Engine/Engine.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/SecureHash.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"
#include "NavMesh/RecastNavMesh.h"
#include "NavAreas/NavArea_Null.h"
#include "NavCollision.h"
#include "PhysicsEngine/BodySetup.h"
#include "Navigation/PathFollowingComponent.h"
#include "ProfilingDebugging/CsvProfiler.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"
#include "UnrealClient.h"
#include "Engine/GameEngine.h"
#include "FrameGrabber.h"
#include "ImageUtils.h"
#include "Async/Async.h"

namespace Closeout
{
double Number(const UObject* O,const TCHAR* N)
{
 const auto* P=O?CastField<FNumericProperty>(O->GetClass()->FindPropertyByName(N)):nullptr;
 if(!P)return -1;const void* V=P->ContainerPtrToValuePtr<void>(O);
 return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));
}
bool Dead(const UObject* O)
{
 const auto* P=O?CastField<FBoolProperty>(O->GetClass()->FindPropertyByName(TEXT("IsDead"))):nullptr;
 return !P||P->GetPropertyValue_InContainer(O);
}
bool Flag(const UObject* O,const TCHAR* N)
{const auto* P=O?CastField<FBoolProperty>(O->GetClass()->FindPropertyByName(N)):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
FString NameProperty(const UObject* O,const TCHAR* N)
{const auto* P=O?CastField<FNameProperty>(O->GetClass()->FindPropertyByName(N)):nullptr;return P?P->GetPropertyValue_InContainer(O).ToString():TEXT("Missing");}
FVector VectorProperty(const UObject* O,const TCHAR* N)
{const auto* P=O?CastField<FStructProperty>(O->GetClass()->FindPropertyByName(N)):nullptr;return P&&P->Struct==TBaseStructure<FVector>::Get()?*P->ContainerPtrToValuePtr<FVector>(O):FVector::ZeroVector;}
TSharedPtr<FJsonObject> ControllerState(AAIController* Ctrl)
{
 auto E=MakeShared<FJsonObject>();
 for(auto N:{TEXT("SquadMode"),TEXT("PolicyState"),TEXT("CombatPhase")})E->SetStringField(N,NameProperty(Ctrl,N));
 for(auto N:{TEXT("SquadDesiredGoal"),TEXT("PolicyGoal"),TEXT("HeldGoal")})E->SetStringField(N,VectorProperty(Ctrl,N).ToString());
 E->SetNumberField(TEXT("SquadReservationID"),Number(Ctrl,TEXT("SquadReservationID")));
 E->SetBoolField(TEXT("PatrolEnabled"),Flag(Ctrl,TEXT("PatrolEnabled")));
 E->SetBoolField(TEXT("CombatHold"),Flag(Ctrl,TEXT("CombatHold")));
 if(auto* B=Ctrl?Ctrl->GetBlackboardComponent():nullptr)
 {
  E->SetStringField(TEXT("WaitingReason"),B->GetValueAsName(TEXT("WaitingReason")).ToString());
  E->SetBoolField(TEXT("HasMoveGoal"),B->GetValueAsBool(TEXT("HasMoveGoal")));
  E->SetBoolField(TEXT("HasVisibleTarget"),B->GetValueAsBool(TEXT("HasVisibleTarget")));
  E->SetNumberField(TEXT("RetryCount"),B->GetValueAsInt(TEXT("RetryCount")));
  E->SetNumberField(TEXT("ReservationID"),B->GetValueAsInt(TEXT("ReservationID")));
  E->SetStringField(TEXT("DesiredPosition"),B->GetValueAsVector(TEXT("DesiredPosition")).ToString());
 }
 return E;
}
FString Action(const UObject* O)
{
 const auto* P=O?CastField<FNameProperty>(O->GetClass()->FindPropertyByName(TEXT("ActionState"))):nullptr;
 return P?P->GetPropertyValue_InContainer(O).ToString():TEXT("Missing");
}
bool Invoke(UObject* O,const TCHAR* N,const FVector* Origin=nullptr,const FVector* Direction=nullptr)
{
 UFunction* F=O?O->FindFunction(N):nullptr;if(!F)return false;FStructOnScope Params(F);
 if(Origin)
 {
  auto* A=CastField<FStructProperty>(F->FindPropertyByName(TEXT("AimOrigin")));
  auto* B=CastField<FStructProperty>(F->FindPropertyByName(TEXT("AimDirection")));
  if(!A||!B||A->Struct!=TBaseStructure<FVector>::Get()||B->Struct!=A->Struct)return false;
  *A->ContainerPtrToValuePtr<FVector>(Params.GetStructMemory())=*Origin;
  *B->ContainerPtrToValuePtr<FVector>(Params.GetStructMemory())=*Direction;
 }
 O->ProcessEvent(F,Params.GetStructMemory());return true;
}
TSharedPtr<FJsonObject> Parse(const FString& Text)
{TSharedPtr<FJsonObject> O;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Text),O);return O;}
FString Json(const TSharedPtr<FJsonObject>& O)
{FString S;FJsonSerializer::Serialize(O.ToSharedRef(),TJsonWriterFactory<>::Create(&S));return S;}
}

using namespace Closeout;
struct FCloseoutFrame : IFramePayload
{
 double Wall;explicit FCloseoutFrame(double Value):Wall(Value){}
};
class FCloseoutGame : public FDefaultModuleImpl
{
 FDelegateHandle Handle,CaptureDelegate;FString Mode,Out,Step=TEXT("await_ready"),Generation,CaptureProblem;
 TWeakObjectPtr<AParisBridgeMission> Current;
 TArray<TSharedPtr<FJsonValue>> Samples,Events,Rounds;
 TSharedPtr<FJsonObject> Saved,Root=MakeShared<FJsonObject>();
 double BeginWall=0,RoundWall=0,LastSample=-1,LastInput=-1,StepTime=0;
 int32 Round=0,GoalIndex=-1,RequiredRounds=3;bool Finished=false;FVector Goal;
 double StillSince=-1;
 bool WantCapture=false,VerifyOldConfig=false;double LastCapture=-1,CaptureStarted=-1;int32 CaptureIndex=0;
 TUniquePtr<FFrameGrabber> Grabber;TArray<TFuture<void>> ImageTasks;
 TArray<TSharedPtr<FJsonValue>> Captures;
 TMap<TWeakObjectPtr<UPathFollowingComponent>,FDelegateHandle> RequestObservers;
 TMap<TWeakObjectPtr<ACharacter>,double> NpcStillSince;

 bool CohortMode() const {return Mode==TEXT("cohort")||Mode==TEXT("squad_diagnose")||Mode==TEXT("candidate");}
 void ObserveRequests(UWorld* W)
 {
  if(!CohortMode())return;
  for(TActorIterator<ACharacter> I(W);I;++I)
  {
   if(!I->ActorHasTag(TEXT("G1_Ally1"))&&!I->ActorHasTag(TEXT("G1_Ally2")))continue;
   auto* Ctrl=Cast<AAIController>(I->GetController());auto* PF=Ctrl?Ctrl->GetPathFollowingComponent():nullptr;
   if(!PF||RequestObservers.Contains(PF))continue;
   FString Name=I->GetName();TWeakObjectPtr<UWorld> World(W);TWeakObjectPtr<AAIController> Controller(Ctrl);
   RequestObservers.Add(PF,PF->OnRequestFinished.AddLambda([this,Name,World,Controller](FAIRequestID Id,const FPathFollowingResult& Result)
   {auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("event"),TEXT("observed_original_npc_move_finished"));E->SetStringField(TEXT("actor"),Name);E->SetNumberField(TEXT("request_id"),Id.GetID());E->SetNumberField(TEXT("result_code"),int32(Result.Code));E->SetNumberField(TEXT("result_flags"),Result.Flags);E->SetNumberField(TEXT("world_seconds"),World.IsValid()?World->GetTimeSeconds():-1);E->SetObjectField(TEXT("controller"),ControllerState(Controller.Get()));Events.Add(MakeShared<FJsonValueObject>(E));}));
  }
 }
 TSharedPtr<FJsonObject> NpcMotion(UWorld* W,ACharacter* A)
 {
  auto E=MakeShared<FJsonObject>();auto* Ctrl=A->GetController();auto* C=A->GetCapsuleComponent();auto* M=A->GetCharacterMovement();auto* PF=Ctrl?Ctrl->FindComponentByClass<UPathFollowingComponent>():nullptr;
  E->SetStringField(TEXT("actor"),A->GetName());E->SetNumberField(TEXT("speed_cm_s"),A->GetVelocity().Size());E->SetStringField(TEXT("held_goal_cm"),VectorProperty(Ctrl,TEXT("HeldGoal")).ToString());E->SetNumberField(TEXT("goal_error_cm"),FVector::Dist(A->GetActorLocation(),VectorProperty(Ctrl,TEXT("HeldGoal"))));E->SetBoolField(TEXT("squad_failed"),Flag(Ctrl,TEXT("SquadFailed")));E->SetBoolField(TEXT("squad_enabled"),Flag(Ctrl,TEXT("SquadEnabled")));
  E->SetStringField(TEXT("action"),Action(A));E->SetNumberField(TEXT("movement_mode"),int32(M->MovementMode));E->SetBoolField(TEXT("root_motion"),A->IsPlayingRootMotion());E->SetNumberField(TEXT("radius_cm"),C->GetScaledCapsuleRadius());E->SetNumberField(TEXT("half_height_cm"),C->GetScaledCapsuleHalfHeight());E->SetNumberField(TEXT("max_step_cm"),M->MaxStepHeight);E->SetNumberField(TEXT("nav_radius_cm"),M->GetNavAgentPropertiesRef().AgentRadius);E->SetNumberField(TEXT("nav_height_cm"),M->GetNavAgentPropertiesRef().AgentHeight);
  E->SetObjectField(TEXT("controller"),ControllerState(Cast<AAIController>(Ctrl)));
  if(PF)
  {
   E->SetNumberField(TEXT("path_status"),int32(PF->GetStatus()));E->SetNumberField(TEXT("next_index"),PF->GetNextPathIndex());
   if(PF->GetStatus()==EPathFollowingStatus::Moving)
   {
    const FVector Target=PF->GetCurrentTargetLocation();E->SetStringField(TEXT("next_target_cm"),Target.ToString());
    if(Mode==TEXT("squad_diagnose"))
    {
     FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(CloseoutNpcBlocker),false,A);for(auto Actor:C->GetMoveIgnoreActors())Q.AddIgnoredActor(Actor);
     bool Blocked=W->SweepSingleByChannel(Hit,A->GetActorLocation(),A->GetActorLocation()+(Target-A->GetActorLocation()).GetSafeNormal2D()*60,A->GetActorQuat(),C->GetCollisionObjectType(),FCollisionShape::MakeCapsule(C->GetScaledCapsuleRadius(),C->GetScaledCapsuleHalfHeight()),Q,FCollisionResponseParams(C->GetCollisionResponseToChannels()));
     E->SetBoolField(TEXT("forward_capsule_blocked"),Blocked);
     if(Blocked)
     {
      E->SetStringField(TEXT("blocker"),GetPathNameSafe(Hit.GetActor()));E->SetStringField(TEXT("blocker_component"),GetPathNameSafe(Hit.GetComponent()));E->SetNumberField(TEXT("hit_distance_cm"),Hit.Distance);E->SetStringField(TEXT("impact_normal"),Hit.ImpactNormal.ToString());E->SetNumberField(TEXT("impact_above_feet_cm"),Hit.ImpactPoint.Z-(A->GetActorLocation().Z-C->GetScaledCapsuleHalfHeight()));E->SetBoolField(TEXT("walkable_hit"),M->IsWalkable(Hit));
      if(auto* S=Cast<UStaticMeshComponent>(Hit.GetComponent()))
      {
       E->SetStringField(TEXT("blocker_mesh"),GetPathNameSafe(S->GetStaticMesh()));E->SetBoolField(TEXT("navigation_relevant"),S->IsNavigationRelevant());
       if(auto* Body=S->GetBodySetup()){E->SetNumberField(TEXT("resolved_collision_trace_flag"),int32(Body->GetCollisionTraceFlag()));E->SetNumberField(TEXT("physics_convex_shapes"),Body->AggGeom.ConvexElems.Num());int Count=0;for(auto& V:Body->AggGeom.ConvexElems)Count+=V.VertexData.Num();E->SetNumberField(TEXT("physics_convex_vertices"),Count);}
       if(S->GetStaticMesh())if(auto* N=S->GetStaticMesh()->GetNavCollision()){E->SetBoolField(TEXT("nav_dynamic_obstacle"),N->IsDynamicObstacle());E->SetBoolField(TEXT("nav_has_convex"),N->HasConvexGeometry());E->SetNumberField(TEXT("nav_convex_vertices"),N->GetConvexCollision().VertexBuffer.Num());E->SetNumberField(TEXT("nav_trimesh_vertices"),N->GetTriMeshCollision().VertexBuffer.Num());}
      }
     }
    }
   }
  }
  return E;
 }

 void DrainFrames()
 {
  if(!Grabber)return;
  ImageTasks.RemoveAll([](TFuture<void>& T){return T.IsReady();});
  for(auto& Frame:Grabber->GetCapturedFrames())
  {
   auto E=MakeShared<FJsonObject>();const double Wall=Frame.GetPayload<FCloseoutFrame>()->Wall;
   E->SetNumberField(TEXT("wall_seconds"),Wall);const FString Name=FString::Printf(TEXT("frames/%06d.png"),CaptureIndex++);
   E->SetStringField(TEXT("file"),Name);E->SetNumberField(TEXT("width"),Frame.BufferSize.X);E->SetNumberField(TEXT("height"),Frame.BufferSize.Y);
   Captures.Add(MakeShared<FJsonValueObject>(E));
   ImageTasks.Add(Async(EAsyncExecution::ThreadPool,[Colors=MoveTemp(Frame.ColorBuffer),Size=Frame.BufferSize,Path=Out/Name]()
   {TArray64<uint8> Data;FImageUtils::PNGCompressImageArray(Size.X,Size.Y,Colors,Data);FFileHelper::SaveArrayToFile(Data,*Path);}));
  }
 }
 void CaptureFrame(UWorld* W)
 {
  if(!WantCapture)return;
  if(!CaptureProblem.IsEmpty()){Finish(W,CaptureProblem);return;}
  ImageTasks.RemoveAll([](TFuture<void>& Task){return Task.IsReady();});
  const double Wall=FPlatformTime::Seconds()-BeginWall;
  if(CaptureStarted>=0 && Wall-CaptureStarted>=12 && CaptureIndex<30)
  {Finish(W,TEXT("failed_viewport_capture_early_frame_admission"));return;}
  if(Wall<=165&&(LastCapture<0||Wall-LastCapture>=.1)&&ImageTasks.Num()<8&&!FScreenshotRequest::IsScreenshotRequested())
  {
   LastCapture=Wall;FScreenshotRequest::RequestScreenshot(TEXT("CloseoutViewport"),true,false,false);
  }
 }
 void CapturePixels(int32 Width,int32 Height,const TArray<FColor>& Pixels)
 {
  if(!WantCapture||Finished)return;
  if(Width!=1920||Height!=1080||Pixels.Num()!=Width*Height||ImageTasks.Num()>=8)
  {CaptureProblem=TEXT("failed_native_screenshot_size_or_queue");return;}
  bool Nonblank=false;for(int32 I=0;I<Pixels.Num();I+=97)if(Pixels[I].R||Pixels[I].G||Pixels[I].B){Nonblank=true;break;}
  if(!Nonblank){CaptureProblem=TEXT("failed_native_screenshot_blank");return;}
  const double Wall=FPlatformTime::Seconds()-BeginWall;if(CaptureStarted<0)CaptureStarted=Wall;
  IFileManager::Get().MakeDirectory(*(Out/TEXT("frames")),true);
  auto E=MakeShared<FJsonObject>();E->SetNumberField(TEXT("wall_seconds"),Wall);
  const FString Name=FString::Printf(TEXT("frames/%06d.png"),CaptureIndex++);E->SetStringField(TEXT("file"),Name);
  E->SetNumberField(TEXT("width"),Width);E->SetNumberField(TEXT("height"),Height);Captures.Add(MakeShared<FJsonValueObject>(E));
  ImageTasks.Add(Async(EAsyncExecution::ThreadPool,[Colors=Pixels,Width,Height,Path=Out/Name]()
  {TArray64<uint8> Data;FImageUtils::PNGCompressImageArray(Width,Height,Colors,Data);FFileHelper::SaveArrayToFile(Data,*Path);}));
 }

 void Event(const FString& What)
 {auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("event"),What);E->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-BeginWall);E->SetNumberField(TEXT("round"),Round);Events.Add(MakeShared<FJsonValueObject>(E));UE_LOG(LogTemp,Display,TEXT("CLOSEOUT %s"),*What);}
 void Write(const FString& Status)
 {
  Root->SetStringField(TEXT("status"),Status);Root->SetStringField(TEXT("mode"),Mode);
  Root->SetStringField(TEXT("input"),TEXT("Opt-in native scripted player movement/visible-target aim/original fire/reload/mission interfaces; NOT unassisted human play"));
  Root->SetStringField(TEXT("step"),Step);Root->SetArrayField(TEXT("samples"),Samples);Root->SetArrayField(TEXT("events"),Events);Root->SetArrayField(TEXT("rounds"),Rounds);
  Root->SetNumberField(TEXT("elapsed_wall_seconds"),FPlatformTime::Seconds()-BeginWall);
  Root->SetNumberField(TEXT("requested_rounds"),RequiredRounds);
  Root->SetArrayField(TEXT("realtime_viewport_frames"),Captures);
  FFileHelper::SaveStringToFile(Json(Root),*(Out/TEXT("result.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
 }
 void Finish(UWorld* W,const FString& Status)
 {if(Finished)return;Finished=true;if(Grabber){Grabber->StopCapturingFrames();Grabber->Shutdown();DrainFrames();Grabber.Reset();}for(auto& T:ImageTasks)T.Wait();Event(Status);Write(Status);if(FCsvProfiler::IsCapturing())FCsvProfiler::Get()->EndCapture();FPlatformMisc::RequestExit(false);}
 bool Move(UWorld* W,ACharacter* P,APlayerController* PC,const FVector& Feet,int32 Index)
 {
  UNavigationPath* Path=UNavigationSystemV1::FindPathToLocationSynchronously(W,P->GetActorLocation(),Feet,P);
  if(!Path||!Path->IsValid()||Path->IsPartial()){Finish(W,TEXT("failed_complete_native_player_path"));return false;}
  auto E=MakeShared<FJsonObject>();E->SetNumberField(TEXT("goal_index"),Index);E->SetNumberField(TEXT("path_length_cm"),Path->GetPathLength());
  TArray<TSharedPtr<FJsonValue>> Points;for(auto V:Path->PathPoints)Points.Add(MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)}));
  E->SetArrayField(TEXT("native_path_cm"),Points);Events.Add(MakeShared<FJsonValueObject>(E));
  Goal=Feet;GoalIndex=Index;PC->SetControlRotation((Feet-P->GetActorLocation()).Rotation());UAIBlueprintHelperLibrary::SimpleMoveToLocation(PC,Feet);return true;
 }
 void Shot(UWorld* W,ACharacter* P,APlayerController* PC)
 {
  FVector Eye;FRotator Rotation;PC->GetPlayerViewPoint(Eye,Rotation);
  ACharacter* Target=nullptr;double Best=DBL_MAX;
  for(TActorIterator<ACharacter> I(W);I;++I)
  {
   if(!I->ActorHasTag(TEXT("G1_German1"))&&!I->ActorHasTag(TEXT("G1_German2"))&&!I->ActorHasTag(TEXT("G1_German3")))continue;
   if(Dead(*I))continue;double D=FVector::DistSquared(Eye,I->GetActorLocation());
   FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(CloseoutVisible),true,P);
   if(D<Best&&W->LineTraceSingleByChannel(Hit,Eye,I->GetActorLocation(),ECC_Visibility,Q)&&Hit.GetActor()==*I){Target=*I;Best=D;}
  }
  if(!Target)return;
  FVector Direction=(Target->GetActorLocation()-Eye).GetSafeNormal();PC->SetControlRotation(Direction.Rotation());
  if(Action(P)!=TEXT("Ready"))return;
  if(Number(P,TEXT("LoadedAmmo"))==0){if(Number(P,TEXT("ReserveAmmo"))>0)Invoke(P,TEXT("PC_RequestReload"));return;}
  Invoke(P,TEXT("PC_RequestFire"),&Eye,&Direction);
 }
 bool CheckOldConfiguration(UWorld* W,AParisBridgeMission* M)
 {
  if(Mode!=TEXT("candidate")){Finish(W,TEXT("failed_old_configuration_test_wrong_mode"));return false;}
  const FString Before=M->ReadMissionState();const int GoodSerial=int(Saved->GetNumberField(TEXT("serial")));
  auto Bad=Parse(Json(Saved));Bad->SetStringField(TEXT("config"),TEXT("G1V2_20261008_nearbank703_roster6_v1"));Bad->SetNumberField(TEXT("serial"),GoodSerial+1);
  auto* File=Cast<UParisBridgeSave>(UGameplayStatics::CreateSaveGameObject(UParisBridgeSave::StaticClass()));File->Payload=Json(Bad);
  FTCHARToUTF8 Bytes(*File->Payload);File->Checksum=FMD5::HashBytes(reinterpret_cast<const uint8*>(Bytes.Get()),Bytes.Length());
  TArray<uint8> Raw;
  const FString Retained=Out/FString::Printf(TEXT("rejected_old_configuration_round%d.sav"),Round);
  if(!UGameplayStatics::SaveGameToMemory(File,Raw)||!FFileHelper::SaveArrayToFile(Raw,*Retained)||
     !UGameplayStatics::SaveGameToSlot(File,M->SlotPrefix+((GoodSerial+1)%2?TEXT("_A"):TEXT("_B")),0))
  {Finish(W,TEXT("failed_isolated_old_configuration_fixture"));return false;}
  auto Journal=Parse(M->InspectCheckpointJournal());
  if(!Journal||!Journal->GetBoolField(TEXT("valid"))||int(Journal->GetNumberField(TEXT("serial")))!=GoodSerial||
     Journal->GetStringField(TEXT("feedback")).IsEmpty()||Json(Journal->GetObjectField(TEXT("snapshot")))!=Json(Saved)||M->ReadMissionState()!=Before)
  {Finish(W,TEXT("failed_old_configuration_rejection_or_state_mutation"));return false;}
  auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("event"),TEXT("newer_old_config_correct_checksum_rejected_good_fallback_live_state_exact"));
  E->SetNumberField(TEXT("round"),Round);E->SetStringField(TEXT("retained_file"),Retained);E->SetObjectField(TEXT("journal"),Journal);Events.Add(MakeShared<FJsonValueObject>(E));return true;
 }
 void InspectGeometry(UWorld* W,ACharacter* P)
 {
  auto G=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Entries;
  for(TActorIterator<AActor> I(W);I;++I)
  {
   if(I->GetName()!=TEXT("StaticMeshActor_1600"))continue;
   TInlineComponentArray<UStaticMeshComponent*> Components(*I);
   for(auto* C:Components)
   {
    auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("actor"),I->GetPathName());E->SetStringField(TEXT("component"),C->GetPathName());
    E->SetStringField(TEXT("mesh"),GetPathNameSafe(C->GetStaticMesh()));E->SetStringField(TEXT("transform"),C->GetComponentTransform().ToString());
    E->SetStringField(TEXT("bounds_origin_cm"),C->Bounds.Origin.ToString());E->SetStringField(TEXT("bounds_extent_cm"),C->Bounds.BoxExtent.ToString());
    E->SetStringField(TEXT("collision_profile"),C->GetCollisionProfileName().ToString());E->SetNumberField(TEXT("collision_enabled"),int32(C->GetCollisionEnabled()));
    E->SetBoolField(TEXT("can_ever_affect_navigation"),C->CanEverAffectNavigation());E->SetBoolField(TEXT("navigation_relevant"),C->IsNavigationRelevant());
    E->SetNumberField(TEXT("pawn_response"),int32(C->GetCollisionResponseToChannel(ECC_Pawn)));E->SetNumberField(TEXT("can_step_up"),int32(C->CanCharacterStepUpOn));
    if(auto* Body=C->GetBodySetup()){E->SetNumberField(TEXT("collision_trace_flag"),int32(Body->CollisionTraceFlag));E->SetNumberField(TEXT("convex_count"),Body->AggGeom.ConvexElems.Num());E->SetNumberField(TEXT("box_count"),Body->AggGeom.BoxElems.Num());}
    Entries.Add(MakeShared<FJsonValueObject>(E));
   }
  }
  G->SetArrayField(TEXT("blocker_components"),Entries);G->SetNumberField(TEXT("player_max_step_cm"),P->GetCharacterMovement()->MaxStepHeight);
  const auto& A=P->GetCharacterMovement()->GetNavAgentPropertiesRef();G->SetNumberField(TEXT("player_nav_radius_cm"),A.AgentRadius);G->SetNumberField(TEXT("player_nav_height_cm"),A.AgentHeight);
  for(TActorIterator<ARecastNavMesh> I(W);I;++I){const auto& N=I->GetConfig();G->SetNumberField(TEXT("nav_radius_cm"),N.AgentRadius);G->SetNumberField(TEXT("nav_height_cm"),N.AgentHeight);G->SetNumberField(TEXT("nav_step_cm"),I->GetAgentMaxStepHeight(ENavigationDataResolution::Default));}
  Root->SetObjectField(TEXT("geometry_diagnostic"),G);Event(TEXT("read_only_blocker_geometry_inspected"));
 }
 bool ExcludeWitnessedPolygon(UWorld* W,ACharacter* P)
 {
  const FVector Feet(5192.972650,-20735.731259,128.136620);auto* C=P->GetCapsuleComponent();
  const FVector Center=Feet+FVector(0,0,C->GetScaledCapsuleHalfHeight());
  const FVector Direction=(FVector(5225.223529,-20748,135.176471)-Feet).GetSafeNormal2D();
  FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(CloseoutWitness),false,P);
  const bool Blocked=W->SweepSingleByChannel(Hit,Center,Center+Direction*60,FQuat::Identity,C->GetCollisionObjectType(),FCollisionShape::MakeCapsule(C->GetScaledCapsuleRadius(),C->GetScaledCapsuleHalfHeight()),Q,FCollisionResponseParams(C->GetCollisionResponseToChannels()));
  if(!Blocked||!Hit.GetActor()||Hit.GetActor()->GetName()!=TEXT("StaticMeshActor_1600")){Finish(W,TEXT("failed_witness_no_original_blocker"));return false;}
  ARecastNavMesh* Recast=nullptr;for(TActorIterator<ARecastNavMesh> I(W);I;++I){if(Recast){Finish(W,TEXT("failed_ambiguous_navmesh"));return false;}Recast=*I;}
  auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);FNavLocation Point;
  if(!Nav||!Recast||!Nav->ProjectPointToNavigation(Feet,Point,FVector(50,50,100),Recast)||FVector::Dist(Point.Location,Feet)>50){Finish(W,TEXT("failed_witness_polygon_projection"));return false;}
  TArray<FVector> Verts;if(!Recast->GetPolyVerts(Point.NodeRef,Verts)||Verts.Num()<3||Recast->GetPolyAreaID(Point.NodeRef)==Recast->GetAreaID(UNavArea_Null::StaticClass())){Finish(W,TEXT("failed_witness_polygon_metadata"));return false;}
  auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("event"),TEXT("single_collision_witness_polygon_exclusion"));E->SetNumberField(TEXT("round"),Round);E->SetStringField(TEXT("node_ref"),LexToString(Point.NodeRef));E->SetNumberField(TEXT("area_before"),Recast->GetPolyAreaID(Point.NodeRef));
  E->SetNumberField(TEXT("witness_hit_cm"),Hit.Distance);E->SetNumberField(TEXT("projection_error_cm"),FVector::Dist(Point.Location,Feet));
  TArray<TSharedPtr<FJsonValue>> Points;for(auto V:Verts)Points.Add(MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)}));E->SetArrayField(TEXT("polygon_vertices_cm"),Points);
  if(!Recast->SetPolyArea(Point.NodeRef,UNavArea_Null::StaticClass())||Recast->GetPolyAreaID(Point.NodeRef)!=Recast->GetAreaID(UNavArea_Null::StaticClass())){Finish(W,TEXT("failed_single_polygon_exclusion"));return false;}
  E->SetNumberField(TEXT("area_after"),Recast->GetPolyAreaID(Point.NodeRef));Events.Add(MakeShared<FJsonValueObject>(E));return true;
 }
 void RecordedQueries(UWorld* W)
 {
  ACharacter* Subject=nullptr;for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Ally1")))Subject=*I;
  ARecastNavMesh* Recast=nullptr;for(TActorIterator<ARecastNavMesh> I(W);I;++I)Recast=*I;
  if(!Subject||!Recast){Finish(W,TEXT("failed_recorded_query_agent"));return;}
  const FVector Body(2533.6603195578004,-20872.277299739802,253.260784642413);
  const double Height=Subject->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
  const FVector Goals[]={FVector(4011.161,-20750.837,206.233),FVector(4165.093,-20817.540,206.233),FVector(5833.884,-20739.338,205.727)};
  TArray<TSharedPtr<FJsonValue>> Results;auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);
  for(int GoalId=0;GoalId<3;++GoalId)for(int StartFeet=0;StartFeet<2;++StartFeet)for(int EndFeet=0;EndFeet<2;++EndFeet)
  {
   const FVector Start=Body-FVector(0,0,StartFeet?Height:0),End=Goals[GoalId]-FVector(0,0,EndFeet?Height:0);
   auto E=MakeShared<FJsonObject>();E->SetNumberField(TEXT("goal_id"),GoalId);E->SetBoolField(TEXT("agent_feet_start"),StartFeet!=0);E->SetBoolField(TEXT("projected_feet_goal"),EndFeet!=0);
   E->SetStringField(TEXT("start_cm"),Start.ToString());E->SetStringField(TEXT("end_cm"),End.ToString());E->SetStringField(TEXT("default_query_extent_cm"),Recast->GetDefaultQueryExtent().ToString());
   FNavLocation Projected;bool Project=Nav&&Nav->ProjectPointToNavigation(Start,Projected,Recast->GetDefaultQueryExtent(),Recast);
   E->SetBoolField(TEXT("start_projects_default_extent"),Project);if(Project)E->SetStringField(TEXT("projected_start_cm"),Projected.Location.ToString());
   UNavigationPath* Path=UNavigationSystemV1::FindPathToLocationSynchronously(W,Start,End,Subject);
   E->SetBoolField(TEXT("path_object"),Path!=nullptr);E->SetBoolField(TEXT("valid"),Path&&Path->IsValid());E->SetBoolField(TEXT("partial"),Path&&Path->IsPartial());
   if(Path){TArray<TSharedPtr<FJsonValue>> Points;for(auto V:Path->PathPoints)Points.Add(MakeShared<FJsonValueString>(V.ToString()));E->SetArrayField(TEXT("path_points_cm"),Points);}
   Results.Add(MakeShared<FJsonValueObject>(E));
  }
  Root->SetArrayField(TEXT("recorded_coordinate_queries"),Results);Event(TEXT("twelve_read_only_recorded_coordinate_queries_complete"));
 }
 void Tick(UWorld* W,ELevelTick Type,float Delta)
 {
  using namespace Closeout;
  if(Finished||!W||!W->IsGameWorld()||W->GetMapName().Contains(TEXT("Entry")))return;
  if(BeginWall==0){BeginWall=FPlatformTime::Seconds();RoundWall=BeginWall;Event(TEXT("observer_started"));}
  if(FPlatformTime::Seconds()-BeginWall>700){Finish(W,TEXT("failed_total_wall_bound"));return;}
  AParisBridgeMission* M=AParisBridgeMission::Find(W);if(!M){if(FPlatformTime::Seconds()-BeginWall>30)Finish(W,TEXT("failed_missing_mission"));return;}
  auto S=Parse(M->ReadMissionState());if(!S){Finish(W,TEXT("failed_state_json"));return;}
  const double T=W->GetTimeSeconds();APlayerController* PC=UGameplayStatics::GetPlayerController(W,0);auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
  if(!PC||!P)return;
  if(M->Phase!=TEXT("Preparing"))CaptureFrame(W);if(Finished)return;
  ObserveRequests(W);
  if(Current.Get()!=M){Current=M;LastSample=-1;LastInput=-1;StepTime=T;}
  if(LastSample<0||T-LastSample>=1)
  {
   LastSample=T;S->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-BeginWall);S->SetNumberField(TEXT("world_seconds"),T);S->SetNumberField(TEXT("round"),Round);
   const FIntPoint Size=GEngine->GameViewport->Viewport->GetSizeXY();S->SetNumberField(TEXT("viewport_width"),Size.X);S->SetNumberField(TEXT("viewport_height"),Size.Y);Samples.Add(MakeShared<FJsonValueObject>(S));
   auto D=MakeShared<FJsonObject>();auto* C=P->GetCapsuleComponent();auto* Move=P->GetCharacterMovement();auto* PF=PC->FindComponentByClass<UPathFollowingComponent>();
   D->SetStringField(TEXT("action"),Action(P));D->SetNumberField(TEXT("velocity_cm_s"),P->GetVelocity().Size());D->SetNumberField(TEXT("max_speed_cm_s"),Move->GetMaxSpeed());D->SetNumberField(TEXT("movement_mode"),int32(Move->MovementMode));
   D->SetNumberField(TEXT("capsule_radius_cm"),C->GetScaledCapsuleRadius());D->SetNumberField(TEXT("capsule_half_height_cm"),C->GetScaledCapsuleHalfHeight());D->SetBoolField(TEXT("root_motion"),P->IsPlayingRootMotion());D->SetBoolField(TEXT("csv_capturing"),FCsvProfiler::IsCapturing());
   if(PF){D->SetNumberField(TEXT("path_status"),int32(PF->GetStatus()));D->SetNumberField(TEXT("current_path_index"),PF->GetCurrentPathIndex());D->SetNumberField(TEXT("next_path_index"),PF->GetNextPathIndex());}
   if(PF&&PF->GetStatus()==EPathFollowingStatus::Moving)
   {
    FVector Target=PF->GetCurrentTargetLocation();D->SetArrayField(TEXT("next_target_cm"),{MakeShared<FJsonValueNumber>(Target.X),MakeShared<FJsonValueNumber>(Target.Y),MakeShared<FJsonValueNumber>(Target.Z)});
    if(Mode==TEXT("diagnose")||Mode==TEXT("navrepair")||Mode==TEXT("cohort"))
    {
     FVector Dir=(Target-P->GetActorLocation()).GetSafeNormal2D();FHitResult Hit;FCollisionQueryParams Q(SCENE_QUERY_STAT(CloseoutBlocker),false,P);
     for(auto Actor:C->GetMoveIgnoreActors())Q.AddIgnoredActor(Actor);
     const bool Blocked=W->SweepSingleByChannel(Hit,P->GetActorLocation(),P->GetActorLocation()+Dir*60,P->GetActorQuat(),C->GetCollisionObjectType(),FCollisionShape::MakeCapsule(C->GetScaledCapsuleRadius(),C->GetScaledCapsuleHalfHeight()),Q,FCollisionResponseParams(C->GetCollisionResponseToChannels()));
     D->SetBoolField(TEXT("forward60cm_capsule_blocked"),Blocked);
     if(Blocked){D->SetStringField(TEXT("blocker"),GetPathNameSafe(Hit.GetActor()));D->SetStringField(TEXT("blocker_component"),GetPathNameSafe(Hit.GetComponent()));D->SetNumberField(TEXT("hit_distance_cm"),Hit.Distance);D->SetBoolField(TEXT("start_penetrating"),Hit.bStartPenetrating);}
    }
   }
   S->SetObjectField(TEXT("movement_diagnostic"),D);
   TArray<TSharedPtr<FJsonValue>> Allies;
   for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Ally1"))||I->ActorHasTag(TEXT("G1_Ally2")))
   {Allies.Add(MakeShared<FJsonValueObject>(NpcMotion(W,*I)));}
   S->SetArrayField(TEXT("allied_navigation_diagnostic"),Allies);
   FFileHelper::SaveStringToFile(Json(S)+TEXT("\n"),*(Out/TEXT("samples.jsonl")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);
  }
  if(M->Phase==TEXT("Error")||M->Phase==TEXT("Lost")){Finish(W,TEXT("failed_live_mission_")+M->Phase);return;}
  if(Step==TEXT("await_ready"))
  {
   if(T>45&&M->Phase!=TEXT("Ready")){Finish(W,TEXT("failed_native_ready_bound"));return;}
   if(M->Phase!=TEXT("Ready")||M->ReadySeconds<10)return;
   if(GEngine->GameViewport->Viewport->GetSizeXY()!=FIntPoint(1920,1080)){Finish(W,TEXT("failed_actual_resolution"));return;}
   Event(TEXT("native_ready_six_member_roster"));PC->ConsoleCommand(FString::Printf(TEXT("Shot SHOWUI -nosuffix filename=\"%s\""),*(Out/FString::Printf(TEXT("round%d_ready.png"),Round))));
   if(Mode==TEXT("geometry")){InspectGeometry(W,P);Step=TEXT("geometry_capture");StepTime=T;return;}
   if(Mode==TEXT("queries")){RecordedQueries(W);Step=TEXT("query_capture");StepTime=T;return;}
   if(Mode==TEXT("startup")){Step=TEXT("startup_capture");StepTime=T;return;}
   if((Mode==TEXT("navrepair")||Mode==TEXT("cohort")||Mode==TEXT("squad_diagnose"))&&!ExcludeWitnessedPolygon(W,P))return;
   if(!M->SaveCheckpoint()){Finish(W,TEXT("failed_ready_checkpoint"));return;}
   Saved=Parse(M->InspectCheckpointJournal())->GetObjectField(TEXT("snapshot"));Event(TEXT("ready_checkpoint_saved"));if(VerifyOldConfig&&!CheckOldConfiguration(W,M))return;Step=TEXT("warmup");StepTime=T;return;
  }
  if(Step==TEXT("startup_capture")){if(T-StepTime>=2)Finish(W,TEXT("pass_packaged_native_ready_only"));return;}
  if(Step==TEXT("geometry_capture")){if(T-StepTime>=2)Finish(W,TEXT("read_only_geometry_observation_complete"));return;}
  if(Step==TEXT("query_capture")){if(T-StepTime>=2)Finish(W,TEXT("read_only_recorded_coordinate_queries_complete"));return;}
  if(Step==TEXT("warmup"))
  {
   if(T-StepTime<20)return;
   IFileManager::Get().MakeDirectory(*(Out/TEXT("CSV")),true);FCsvProfiler::Get()->BeginCapture(-1,Out/TEXT("CSV"),FString::Printf(TEXT("round%d.csv"),Round));
   if(!M->StartMission()){Finish(W,TEXT("failed_start"));return;}
   RoundWall=FPlatformTime::Seconds();Step=TEXT("playing");Event(TEXT("original_mission_started"));Move(W,P,PC,M->FarBankFeet,0);return;
  }
  if(Step==TEXT("playing"))
  {
   if(FPlatformTime::Seconds()-RoundWall>180){Finish(W,TEXT("failed_round_180sec_bound"));return;}
   if(M->Phase==TEXT("Won"))
   {
    PC->StopMovement();if(FCsvProfiler::IsCapturing())FCsvProfiler::Get()->EndCapture();Event(TEXT("native_won"));Step=TEXT("save_won");StepTime=T;return;
   }
   if(LastInput<0||T-LastInput>=.35){LastInput=T;Shot(W,P,PC);}
   if(Mode==TEXT("squad_diagnose"))for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Ally1"))||I->ActorHasTag(TEXT("G1_Ally2")))
   {
    const bool Still=Action(*I)==TEXT("Ready")&&I->GetVelocity().Size()<1&&FVector::Dist(I->GetActorLocation(),VectorProperty(I->GetController(),TEXT("HeldGoal")))>100;
    if(!Still)NpcStillSince.Remove(*I);else if(!NpcStillSince.Contains(*I))NpcStillSince.Add(*I,T);
    else if(T-NpcStillSince[*I]>=4){Event(TEXT("npc_four_seconds_ready_stationary_cause_capture"));if(FCsvProfiler::IsCapturing())FCsvProfiler::Get()->EndCapture();PC->StopMovement();Step=TEXT("npc_diagnostic_capture");StepTime=T;return;}
   }
   if((Mode==TEXT("diagnose")||Mode==TEXT("navrepair")||Mode==TEXT("cohort"))&&FVector::Dist2D(P->GetActorLocation(),Goal)>120)
   {
    if(P->GetVelocity().Size()<1&&Action(P)==TEXT("Ready")){if(StillSince<0)StillSince=T;}else StillSince=-1;
    if(StillSince>=0&&T-StillSince>=6){Event(TEXT("diagnostic_six_seconds_ready_still"));if(FCsvProfiler::IsCapturing())FCsvProfiler::Get()->EndCapture();PC->ConsoleCommand(FString::Printf(TEXT("Shot SHOWUI -nosuffix filename=\"%s\""),*(Out/TEXT("stalled.png"))));Step=TEXT("diagnostic_capture");StepTime=T;return;}
   }
   const FVector Feet=P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
   if(GoalIndex==0&&FVector::Dist2D(Feet,M->FarBankFeet)<(CohortMode()?55:120))
   {Event(TEXT("player_physically_crossed_bridge"));if(CohortMode()){Step=TEXT("regroup");StepTime=T;}else Move(W,P,PC,M->BridgeheadFeet,1);}
   return;
  }
  if(Step==TEXT("regroup"))
  {
   if(WantCapture)
   {
    ACharacter* Subject=nullptr;double Furthest=-1;
    for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Ally1"))||I->ActorHasTag(TEXT("G1_Ally2")))
    {double D=FVector::Dist(I->GetActorLocation(),VectorProperty(I->GetController(),TEXT("HeldGoal")));if(D>Furthest){Furthest=D;Subject=*I;}}
    if(Subject){FVector Eye;FRotator R;PC->GetPlayerViewPoint(Eye,R);PC->SetControlRotation((Subject->GetActorLocation()+FVector(0,0,40)-Eye).Rotation());}
   }
   int Count=0;bool Arrived=true;
   for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Ally1"))||I->ActorHasTag(TEXT("G1_Ally2")))
   {++Count;auto* Ctrl=I->GetController();Arrived&=!Dead(*I)&&I->GetActorLocation().X>=5600&&!Flag(Ctrl,TEXT("SquadFailed"))&&FVector::Dist(I->GetActorLocation(),VectorProperty(Ctrl,TEXT("HeldGoal")))<=55;}
   if(Count!=2){Finish(W,TEXT("failed_cohort_original_roster"));return;}
   if(Arrived){Event(TEXT("both_allies_original_55cm_25sec_far_bank_gate_pass"));Step=TEXT("playing");StillSince=-1;Move(W,P,PC,M->BridgeheadFeet,1);return;}
   if(T-StepTime>25){Finish(W,TEXT("failed_original_cohort_25sec_bound"));return;}
   return;
  }
  if(Step==TEXT("diagnostic_capture")){if(T-StepTime>=2)Finish(W,TEXT("stop_cause_observation_no_gameplay_acceptance"));return;}
  if(Step==TEXT("npc_diagnostic_capture")){if(T-StepTime>=2)Finish(W,TEXT("stop_companion_cause_observation_no_cohort_acceptance"));return;}
  if(Step==TEXT("save_won"))
  {
   if(T-StepTime>10){Finish(W,TEXT("failed_won_save_safe_bound"));return;}
   if(!M->SaveCheckpoint())return;
   Saved=Parse(M->InspectCheckpointJournal())->GetObjectField(TEXT("snapshot"));Rounds.Add(MakeShared<FJsonValueObject>(Saved));
   PC->ConsoleCommand(FString::Printf(TEXT("Shot SHOWUI -nosuffix filename=\"%s\""),*(Out/FString::Printf(TEXT("round%d_won.png"),Round))));
   Event(TEXT("won_checkpoint_saved_original_resources"));Step=TEXT("load_won");StepTime=T;return;
  }
  if(Step==TEXT("load_won"))
  {
   if(T-StepTime<2)return;Generation=M->RunGeneration;Step=TEXT("restore_wait");if(!M->LoadCheckpoint())Finish(W,TEXT("failed_load_won_request"));return;
  }
  if(Step==TEXT("restore_wait"))
  {
   if(M->RunGeneration==Generation||M->Phase==TEXT("Preparing"))return;
   if(M->Phase!=TEXT("Won")){Finish(W,TEXT("failed_restored_phase"));return;}
   auto Actual=Parse(M->ReadMissionState())->GetObjectField(TEXT("snapshot"));
   if(Json(Saved)!=Json(Actual))
   {
    // Source generation and controller motion are not gameplay resources; compare all six authoritative resources.
    const auto& A=Saved->GetArrayField(TEXT("actors"));const auto& B=Actual->GetArrayField(TEXT("actors"));
    if(A.Num()!=6||B.Num()!=6){Finish(W,TEXT("failed_restore_roster"));return;}
    for(int I=0;I<6;++I)for(auto N:{TEXT("health"),TEXT("loaded"),TEXT("reserve"),TEXT("shots")})
     if(A[I]->AsObject()->GetNumberField(N)!=B[I]->AsObject()->GetNumberField(N)){Finish(W,TEXT("failed_restore_resource"));return;}
    for(int I=0;I<6;++I)if(A[I]->AsObject()->GetBoolField(TEXT("dead"))!=B[I]->AsObject()->GetBoolField(TEXT("dead"))){Finish(W,TEXT("failed_restore_death"));return;}
   }
   Event(TEXT("fresh_world_won_resource_restore_verified"));++Round;
   if(Round==RequiredRounds){Finish(W,RequiredRounds==3?TEXT("pass_three_scripted_integrated_rounds_human_gate_pending"):TEXT("pass_one_scripted_integrated_round_human_gate_pending"));return;}
   Step=TEXT("restart_wait");Generation=M->RunGeneration;M->RestartMission();return;
  }
  if(Step==TEXT("restart_wait"))
  {
   if(M->RunGeneration==Generation||M->Phase!=TEXT("Ready"))return;
   auto A=Parse(M->ReadMissionState())->GetObjectField(TEXT("snapshot"))->GetArrayField(TEXT("actors"));
   if(A.Num()!=6){Finish(W,TEXT("failed_fresh_restart_roster"));return;}
   for(auto V:A){auto O=V->AsObject();if(O->GetNumberField(TEXT("health"))!=100||O->GetNumberField(TEXT("loaded"))!=2||O->GetNumberField(TEXT("reserve"))!=16||O->GetNumberField(TEXT("shots"))!=0||O->GetBoolField(TEXT("dead"))){Finish(W,TEXT("failed_fresh_restart_resources"));return;}}
   Event(TEXT("original_fresh_roster_resources_verified"));Step=TEXT("await_ready");return;
  }
 }
public:
 virtual void StartupModule() override
 {
  using namespace Closeout;
  if(!FParse::Value(FCommandLine::Get(),TEXT("ParisCloseout="),Mode)||!FParse::Value(FCommandLine::Get(),TEXT("ParisCloseoutOut="),Out))return;
  if(Mode!=TEXT("startup")&&Mode!=TEXT("integrated")&&Mode!=TEXT("diagnose")&&Mode!=TEXT("geometry")&&Mode!=TEXT("navrepair")&&Mode!=TEXT("cohort")&&Mode!=TEXT("squad_diagnose")&&Mode!=TEXT("candidate")&&Mode!=TEXT("queries"))return;
  WantCapture=FParse::Param(FCommandLine::Get(),TEXT("ParisCapture"));
  VerifyOldConfig=FParse::Param(FCommandLine::Get(),TEXT("ParisVerifyOldCheckpoint"));
  FParse::Value(FCommandLine::Get(),TEXT("ParisRounds="),RequiredRounds);if(RequiredRounds!=1&&RequiredRounds!=3)return;
  if(!FPaths::DirectoryExists(Out)||FPaths::FileExists(Out/TEXT("result.json")))return;
  if(WantCapture)CaptureDelegate=UGameViewportClient::OnScreenshotCaptured().AddRaw(this,&FCloseoutGame::CapturePixels);
  UE_LOG(LogTemp,Display,TEXT("CLOSEOUT_MODULE_ACTIVATED mode=%s"),*Mode);
  Handle=FWorldDelegates::OnWorldPostActorTick.AddRaw(this,&FCloseoutGame::Tick);
 }
 virtual void ShutdownModule() override {if(CaptureDelegate.IsValid())UGameViewportClient::OnScreenshotCaptured().Remove(CaptureDelegate);if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);for(auto& E:RequestObservers)if(E.Key.IsValid())E.Key->OnRequestFinished.Remove(E.Value);}
};
IMPLEMENT_MODULE(FCloseoutGame,ParisBridgeMissionV1);
