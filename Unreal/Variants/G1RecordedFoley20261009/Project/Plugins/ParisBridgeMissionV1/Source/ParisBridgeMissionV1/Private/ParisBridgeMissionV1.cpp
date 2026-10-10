#include "Modules/ModuleManager.h"
// Finite opt-in integration checks. No model/pose/resource/death writes.
#include "ParisBridgeMission.h"
#include "ParisGameplayAV.h"
#include "Blueprint/AIBlueprintHelperLibrary.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"

bool ParisProneFutureBlocked(const ACharacter* Player);

namespace ParisUXTest
{
double Number(const UObject* O,const TCHAR* N)
{
 auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),N):nullptr;
 if(!P)return -9999;const void* V=P->ContainerPtrToValuePtr<void>(O);
 return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));
}

bool Flag(const UObject* O,const TCHAR* N)
{auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),N):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
FString Name(const UObject* O,const TCHAR* N)
{if(auto* S=O?FindFProperty<FStrProperty>(O->GetClass(),N):nullptr)return S->GetPropertyValue_InContainer(O);auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),N):nullptr;return P?P->GetPropertyValue_InContainer(O).ToString():TEXT("Missing");}
void Key(APlayerController* PC,FKey K,bool Down)
{PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1.f:0.f));}
void Tap(APlayerController* PC,FKey K){Key(PC,K,true);Key(PC,K,false);}
}

class FParisUXRevisionModule : public FDefaultModuleImpl
{
 FString Mode,Out,Step=TEXT("ready"),Generation;FDelegateHandle Handle;
 double BeginWall=0,Since=0,LastSample=0,NextShot=0,Peak=0,MinSquad=1e9,MaxAllyTravel=0;
 FVector Start,Origin,ProneSite,AllyStarts[2];int32 LastDefenders=3,AmmoBefore=0;bool Finished=false,SawFalling=false,CombatHalted=false;
 double AimStarted=-1;
 double BlockSince=-1;FVector BlockFeet;double BlockDrift=0;
 TArray<TSharedPtr<FJsonValue>> Events,Samples;TSharedPtr<FJsonObject> Root=MakeShared<FJsonObject>();
 void Event(const FString& Text)
 {auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("event"),Text);E->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-BeginWall);Events.Add(MakeShared<FJsonValueObject>(E));UE_LOG(LogTemp,Display,TEXT("PARIS_UX_TEST %s"),*Text);}
 void Finish(const FString& Status)
 {
  if(Finished)return;Finished=true;Event(Status);Root->SetStringField(TEXT("status"),Status);
  Root->SetStringField(TEXT("mode"),Mode);Root->SetStringField(TEXT("step"),Step);
  Root->SetStringField(TEXT("scope"),TEXT("Opt-in simulated engine key presses/releases and native movement/visible aim; not human play, full contact, FPS or natural encounter acceptance"));
  Root->SetNumberField(TEXT("elapsed_wall_seconds"),FPlatformTime::Seconds()-BeginWall);
  Root->SetArrayField(TEXT("events"),Events);Root->SetArrayField(TEXT("samples"),Samples);
  FString S;auto W=TJsonWriterFactory<>::Create(&S);FJsonSerializer::Serialize(Root.ToSharedRef(),W);
  FFileHelper::SaveStringToFile(S,*(Out/TEXT("result.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
  FPlatformMisc::RequestExit(false);
 }
 bool Check(bool OK,const FString& What){if(!OK){Finish(TEXT("failed_")+What);return false;}Event(TEXT("pass_")+What);return true;}
 void Go(UWorld* W,ACharacter* P,const FString& Next)
 {Step=Next;Since=W->GetTimeSeconds();Start=P->GetNavAgentLocation();Peak=0;SawFalling=false;Event(TEXT("step_")+Next);}
 void Image(APlayerController* PC,const TCHAR* Name)
 {PC->ConsoleCommand(FString::Printf(TEXT("Shot SHOWUI -nosuffix filename=%s/%s.png"),*Out,Name),false);}
 void Move(APlayerController* PC,FVector Feet){PC->SetControlRotation((Feet-PC->GetPawn()->GetActorLocation()).Rotation());UAIBlueprintHelperLibrary::SimpleMoveToLocation(PC,Feet);}
 bool Probe(UWorld* W,ACharacter* P,FVector Feet,const FString& Label)
 {
  auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("label"),Label);R->SetStringField(TEXT("feet"),Feet.ToString());
  R->SetStringField(TEXT("actor_scale"),P->GetActorScale3D().ToString());
  const double Delta=P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-P->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight();
  R->SetNumberField(TEXT("authored_feet_delta_z"),Delta);
  FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisUXProneProbe),false,P);FHitResult H;
  const FVector F=P->GetActorForwardVector(),Center=Feet+FVector(0,0,30);
  const bool Box=W->SweepSingleByChannel(H,Center,Center,P->GetActorQuat(),ECC_Visibility,FCollisionShape::MakeBox(FVector(130,55,28)),Q);
  R->SetBoolField(TEXT("box_hit"),Box);R->SetStringField(TEXT("box_actor"),H.GetActor()?H.GetActor()->GetPathName():TEXT("None"));
  R->SetStringField(TEXT("box_normal"),H.ImpactNormal.ToString());R->SetStringField(TEXT("box_point"),H.ImpactPoint.ToString());
  bool Clear=!Box&&FMath::Abs(Delta)<.01;TArray<TSharedPtr<FJsonValue>> Supports;
  for(double Offset:{-120.,0.,110.})
  {
   const FVector Pt=Feet+F*Offset;FHitResult S;const bool Hit=W->LineTraceSingleByChannel(S,Pt+FVector(0,0,40),Pt-FVector(0,0,30),ECC_Visibility,Q);
   const bool OK=Hit&&S.ImpactNormal.Z>=.97&&FMath::Abs(S.ImpactPoint.Z-Feet.Z)<=10;Clear&=OK;
   auto Row=MakeShared<FJsonObject>();Row->SetNumberField(TEXT("offset"),Offset);Row->SetBoolField(TEXT("hit"),Hit);Row->SetBoolField(TEXT("pass"),OK);
   Row->SetNumberField(TEXT("normal_z"),S.ImpactNormal.Z);Row->SetNumberField(TEXT("height_delta"),S.ImpactPoint.Z-Feet.Z);
   Row->SetStringField(TEXT("actor"),S.GetActor()?S.GetActor()->GetPathName():TEXT("None"));Supports.Add(MakeShared<FJsonValueObject>(Row));
  }
  R->SetBoolField(TEXT("clear"),Clear);R->SetArrayField(TEXT("supports"),Supports);Probes.Add(MakeShared<FJsonValueObject>(R));return Clear;
 }
 TArray<TSharedPtr<FJsonValue>> Probes;
 bool SelectProneSite(UWorld* W,ACharacter* P)
 {
  // Fixed from actions_v2's measured footprint, no new coordinate search.
  const FVector Feet(1762.5,-20662.5,114.402);
  if(!Probe(W,P,Feet,TEXT("retained_measured_site"))||!Probe(W,P,Feet+FVector(60,0,0),TEXT("retained_forward60")))return false;
  if(Probe(W,P,Feet+FVector(120,0,0),TEXT("retained_obstruction120")))return false;
  auto* Path=UNavigationSystemV1::FindPathToLocationSynchronously(W,P->GetNavAgentLocation(),Feet,P);
  if(!Path||!Path->IsValid()||Path->IsPartial())return false;
  ProneSite=Feet;Root->SetStringField(TEXT("selected_prone_site"),Feet.ToString());return true;
 }
 void FireVisible(UWorld* W,ACharacter* P,APlayerController* PC,FVector RouteGoal)
 {
  if(W->GetTimeSeconds()<NextShot || ParisUXTest::Name(P,TEXT("ActionState"))!=TEXT("Ready"))return;
  NextShot=W->GetTimeSeconds()+.3;FVector Eye;FRotator R;PC->GetPlayerViewPoint(Eye,R);
  ACharacter* Target=nullptr;double Best=1e20;
  for(TActorIterator<ACharacter> I(W);I;++I)if((I->ActorHasTag(TEXT("G1_German1"))||I->ActorHasTag(TEXT("G1_German2"))||I->ActorHasTag(TEXT("G1_German3")))&&!ParisUXTest::Flag(*I,TEXT("IsDead")))
  {
   FHitResult H;FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisUXVisible),false,P);
   const double D=FVector::DistSquared(Eye,I->GetActorLocation());
   if(D<Best&&W->LineTraceSingleByChannel(H,Eye,I->GetActorLocation(),ECC_Visibility,Q)&&H.GetActor()==*I){Target=*I;Best=D;}
  }
  if(!Target){if(CombatHalted){CombatHalted=false;AimStarted=-1;Move(PC,RouteGoal);}return;}
  const FVector Direction=(Target->GetActorLocation()-Eye).GetSafeNormal();PC->SetControlRotation(Direction.Rotation());
  auto* GunProperty=FindFProperty<FObjectPropertyBase>(P->GetClass(),TEXT("WeaponAppearance"));
  auto* Gun=GunProperty?Cast<AActor>(GunProperty->GetObjectPropertyValue_InContainer(P)):nullptr;
  if(!Gun){Finish(TEXT("failed_authoritative_gun_missing"));return;}
  const FVector Muzzle=Gun->GetActorTransform().TransformPosition(FVector(0,83.23,0));FHitResult B;
  FCollisionQueryParams BulletQ(SCENE_QUERY_STAT(ParisUXBullet),false,P),BarrelQ(SCENE_QUERY_STAT(ParisUXBarrel),false,P);
  const bool ClearBullet=W->LineTraceSingleByChannel(B,Muzzle,Target->GetActorLocation(),ECC_Visibility,BulletQ)&&B.GetActor()==Target;
  const bool ClearBarrel=!W->SweepSingleByChannel(B,Gun->GetActorLocation(),Muzzle,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(2),BarrelQ);
  const bool ClearMuzzle=!W->SweepSingleByChannel(B,Muzzle-Direction*.1,Muzzle+Direction*.1,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(2),BarrelQ);
  if(!ClearBullet||!ClearBarrel||!ClearMuzzle)
  {if(CombatHalted){CombatHalted=false;UAIBlueprintHelperLibrary::SimpleMoveToLocation(PC,RouteGoal);}AimStarted=-1;return;}
  if(!CombatHalted){PC->StopMovement();CombatHalted=true;AimStarted=W->GetTimeSeconds();Event(TEXT("eye_and_muzzle_clear_stop_and_aim"));}
  auto* Camera=P->FindComponentByClass<UCameraComponent>();
  const double Error=Camera?FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(FVector::DotProduct(Camera->GetForwardVector(),Direction),-1.,1.))):180;
  Root->SetNumberField(TEXT("latest_camera_aim_error_degrees"),Error);
  if(Error>.3){if(W->GetTimeSeconds()-AimStarted>2){Image(PC,TEXT("aim_failure"));Finish(TEXT("failed_camera_aim_settle"));}return;}
  if(ParisUXTest::Number(P,TEXT("LoadedAmmo"))+ParisUXTest::Number(P,TEXT("ReserveAmmo"))<=0){Image(PC,TEXT("ammo_exhausted"));Finish(TEXT("failed_original_rounds_exhausted"));return;}
  ParisUXTest::Tap(PC,ParisUXTest::Number(P,TEXT("LoadedAmmo"))>0?EKeys::LeftMouseButton:EKeys::R);
 }
 void Tick(UWorld* W,ELevelTick,float)
 {
  using namespace ParisUXTest;
  if(Finished||!W||!W->IsGameWorld())return;
  if(!BeginWall)BeginWall=FPlatformTime::Seconds();
  if(FPlatformTime::Seconds()-BeginWall>240){Finish(TEXT("failed_finite_deadline"));return;}
  auto* M=AParisBridgeMission::Find(W);auto* PC=UGameplayStatics::GetPlayerController(W,0);auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
  if(!M||!PC||!P)return;const double Now=W->GetTimeSeconds(),Age=Now-Since;const FVector Feet=P->GetNavAgentLocation();
  if(Now-LastSample>=.1)
  {
   LastSample=Now;auto S=MakeShared<FJsonObject>();S->SetStringField(TEXT("step"),Step);S->SetNumberField(TEXT("time"),Now);
   S->SetStringField(TEXT("phase"),M->Phase);S->SetStringField(TEXT("feet"),Feet.ToString());S->SetNumberField(TEXT("speed"),P->GetVelocity().Size2D());
   S->SetNumberField(TEXT("posture"),Number(P,TEXT("DesiredPosture")));S->SetNumberField(TEXT("half_height"),P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
   S->SetBoolField(TEXT("prone_blocked"),Flag(P,TEXT("ProneBlocked")));S->SetBoolField(TEXT("prone_clear"),Flag(P,TEXT("ProneClear")));
   S->SetBoolField(TEXT("future_floor_blocked"),ParisProneFutureBlocked(P));
   S->SetStringField(TEXT("pose"),Name(P,TEXT("ActivePose")));S->SetBoolField(TEXT("run"),Flag(P,TEXT("RunHeld")));S->SetBoolField(TEXT("slow"),Flag(P,TEXT("SlowHeld")));
   S->SetNumberField(TEXT("loaded"),Number(P,TEXT("LoadedAmmo")));S->SetNumberField(TEXT("reserve"),Number(P,TEXT("ReserveAmmo")));
   S->SetNumberField(TEXT("health"),Number(P,TEXT("Health")));S->SetNumberField(TEXT("shots"),Number(P,TEXT("ShotSequence")));S->SetStringField(TEXT("shot_outcome"),Name(P,TEXT("ShotOutcome")));
   S->SetNumberField(TEXT("defenders"),M->LivingDefenders);S->SetNumberField(TEXT("serial"),M->SaveSerial);S->SetBoolField(TEXT("unlocked"),M->CheckpointUnlocked());S->SetBoolField(TEXT("prompt"),M->CheckpointPromptVisible);
   Samples.Add(MakeShared<FJsonValueObject>(S));
  }
  if(M->Phase==TEXT("Error")||M->Phase==TEXT("Lost")){Finish(TEXT("failed_mission_")+M->Phase+TEXT("_")+M->Feedback);return;}
  if(Step==TEXT("ready"))
  {
   if(M->Phase!=TEXT("Ready")||M->ReadySeconds<12)return;
   if(Mode==TEXT("legacy")){Generation=M->RunGeneration;Root->SetStringField(TEXT("legacy_journal"),M->InspectCheckpointJournal());Go(W,P,TEXT("load_wait"));Tap(PC,EKeys::F9);return;}
   if(!Check(P->GetClass()->GetPathName().Contains(TEXT("BP_PCParisPlayerActionsV6")),TEXT("action_class")))return;
   if(!Check(!M->CheckpointUnlocked()&&!M->CheckpointPromptVisible&&M->SaveSerial==0,TEXT("initial_no_checkpoint")))return;
   Image(PC,TEXT("ready"));Go(W,P,TEXT("ready_image"));return;
  }
  if(Step==TEXT("ready_image")&&Age>=1)
  {
   PC->SetControlRotation(FRotator::ZeroRotator);Origin=Feet;Tap(PC,EKeys::Enter);
   int32 I=0;for(TActorIterator<ACharacter> A(W);A;++A)if(A->ActorHasTag(TEXT("G1_Ally1"))||A->ActorHasTag(TEXT("G1_Ally2"))){if(I<2)AllyStarts[I++]=A->GetActorLocation();}
   Go(W,P,TEXT("stationary"));return;
  }
  if(Step==TEXT("stationary"))
  {
   int32 I=0;for(TActorIterator<ACharacter> A(W);A;++A)if(A->ActorHasTag(TEXT("G1_Ally1"))||A->ActorHasTag(TEXT("G1_Ally2")))
   {MinSquad=FMath::Min(MinSquad,FVector::Dist2D(P->GetActorLocation(),A->GetActorLocation()));if(I<2)MaxAllyTravel=FMath::Max(MaxAllyTravel,FVector::Dist2D(AllyStarts[I++],A->GetActorLocation()));}
   if(Age<8)return;
   Root->SetNumberField(TEXT("stationary_min_player_ally_cm"),MinSquad);Root->SetNumberField(TEXT("stationary_max_ally_travel_cm"),MaxAllyTravel);
   if(!Check(MinSquad>=250 && MaxAllyTravel<80,TEXT("stationary_squad_separation")))return;
   if(Mode==TEXT("checkpoint")){Tap(PC,EKeys::R);Go(W,P,TEXT("preload"));return;}
   Go(W,P,TEXT("walk"));Key(PC,EKeys::W,true);return;
  }
  Peak=FMath::Max(Peak,P->GetVelocity().Size2D());SawFalling|=P->GetCharacterMovement()->IsFalling();
  if(Mode==TEXT("actions"))
  {
   if(Step==TEXT("walk")&&Age>=2){if(!Check(Peak>140&&Peak<160&&FVector::Dist2D(Feet,Start)>180,TEXT("walk_physical")))return;Go(W,P,TEXT("run"));Key(PC,EKeys::LeftShift,true);return;}
   if(Step==TEXT("run")&&Age>=2){if(!Check(Peak>290&&Peak<310&&FVector::Dist2D(Feet,Start)>400&&Flag(P,TEXT("RunHeld")),TEXT("run_physical")))return;Key(PC,EKeys::LeftShift,false);Go(W,P,TEXT("slow"));Key(PC,EKeys::LeftAlt,true);return;}
   if(Step==TEXT("slow")&&Age>=2){if(!Check(P->GetVelocity().Size2D()>60&&P->GetVelocity().Size2D()<70&&!Flag(P,TEXT("RunHeld")),TEXT("slow_and_run_release")))return;Key(PC,EKeys::W,false);Key(PC,EKeys::LeftAlt,false);Go(W,P,TEXT("stop"));return;}
   if(Step==TEXT("stop")&&Age>=1){if(!Check(P->GetVelocity().Size2D()<2&&!Flag(P,TEXT("SlowHeld")),TEXT("movement_key_release")))return;Go(W,P,TEXT("jump"));Key(PC,EKeys::SpaceBar,true);return;}
   if(Step==TEXT("jump")){if(Age>.2)Key(PC,EKeys::SpaceBar,false);if(Age>=2){if(!Check(SawFalling&&P->GetCharacterMovement()->IsMovingOnGround(),TEXT("jump_land")))return;Go(W,P,TEXT("crouch"));Key(PC,EKeys::LeftControl,true);}return;}
   if(Step==TEXT("crouch")&&Age>=1){if(!Check(Number(P,TEXT("DesiredPosture"))==1&&P->bIsCrouched&&FMath::Abs(P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-60)<1,TEXT("crouch_capsule")))return;Image(PC,TEXT("crouch"));AmmoBefore=Number(P,TEXT("LoadedAmmo"));Generation=M->RunGeneration;Tap(PC,EKeys::R);Go(W,P,TEXT("crouch_reload"));return;}
   if(Step==TEXT("crouch_reload")&&Age>=1){if(!Check(M->RunGeneration==Generation&&M->Phase==TEXT("Crossing")&&Number(P,TEXT("LoadedAmmo"))==AmmoBefore,TEXT("held_control_reload_no_restart")))return;Key(PC,EKeys::LeftControl,false);Tap(PC,EKeys::LeftControl);Go(W,P,TEXT("stand"));return;}
   if(Step==TEXT("stand")&&Age>=1)
   {
    if(!Check(Number(P,TEXT("DesiredPosture"))==0&&!P->bIsCrouched,TEXT("stand_clearance")))return;
    const bool Clear=Probe(W,P,Feet,TEXT("previous_bridge_refusal"));
    Root->SetArrayField(TEXT("prone_probes"),Probes);
    if(!Check(FMath::Abs(P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-P->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight())<.01,TEXT("prone_feet_frame")))return;
    Tap(PC,EKeys::Z);
    if(Clear){Go(W,P,TEXT("prone"));return;}
    Go(W,P,TEXT("prone_denied"));return;
   }
   if(Step==TEXT("prone_denied")&&Age>=1)
   {
    if(!Check(Number(P,TEXT("DesiredPosture"))==0&&!Flag(P,TEXT("ProneClear")),TEXT("original_terrain_refusal")))return;
    const bool Found=SelectProneSite(W,P);Root->SetArrayField(TEXT("prone_probes"),Probes);
    if(!Check(Found,TEXT("retained_prone_site_obstruction_and_complete_path")))return;Go(W,P,TEXT("prone_move"));Move(PC,ProneSite);return;
   }
   if(Step==TEXT("prone_move"))
   {
    if(FVector::Dist2D(Feet,ProneSite)>45||P->GetVelocity().Size2D()>2){if(Age>25)Finish(TEXT("failed_prone_physical_arrival"));return;}
    PC->SetControlRotation(FRotator::ZeroRotator);Go(W,P,TEXT("prone_align"));return;
   }
   if(Step==TEXT("prone_align"))
   {
    if(FMath::Abs(Feet.Y-ProneSite.Y)>15||Feet.X<ProneSite.X-15||Age>2){Finish(TEXT("failed_measured_prone_anchor_alignment"));return;}
    if(Feet.X-ProneSite.X>15){Key(PC,EKeys::S,true);return;}
    Key(PC,EKeys::S,false);Go(W,P,TEXT("prone_arrived"));return;
   }
   if(Step==TEXT("prone_arrived")&&Age>=1)
   {
    const bool Clear=Probe(W,P,Feet,TEXT("actual_physical_arrival"));Root->SetArrayField(TEXT("prone_probes"),Probes);
    if(!Check(Clear&&FVector::Dist2D(Feet,ProneSite)<=20,TEXT("actual_flat_prone_clearance")))return;Tap(PC,EKeys::Z);Go(W,P,TEXT("prone"));return;
   }
   if(Step==TEXT("prone")&&Age>=1){if(!Check(Number(P,TEXT("DesiredPosture"))==2&&FMath::Abs(P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-34)<1,TEXT("prone_capsule")))return;Image(PC,TEXT("prone"));AmmoBefore=Number(P,TEXT("LoadedAmmo"));Tap(PC,EKeys::LeftMouseButton);Go(W,P,TEXT("prone_fire_denied"));return;}
   if(Step==TEXT("prone_fire_denied")&&Age>=.5){if(!Check(Number(P,TEXT("LoadedAmmo"))==AmmoBefore,TEXT("original_low_posture_fire_denial")))return;Go(W,P,TEXT("crawl"));Key(PC,EKeys::W,true);return;}
   if(Step==TEXT("crawl"))
   {
    if(Flag(P,TEXT("ProneBlocked"))||ParisProneFutureBlocked(P)){if(BlockSince<0){BlockSince=Now;BlockFeet=Feet;}BlockDrift=FMath::Max(BlockDrift,FVector::Dist2D(Feet,BlockFeet));}
    if(Age<4)return;
    Root->SetNumberField(TEXT("crawl_forward_cm"),FVector::Dist2D(Feet,Start));Root->SetNumberField(TEXT("blocked_drift_cm"),BlockDrift);
    if(!Check(Peak>55&&Peak<65&&FVector::Dist2D(Feet,Start)>10&&BlockSince>0&&Now-BlockSince>=.7&&BlockDrift<1,TEXT("crawl_physical_and_original_obstruction_stop")))return;
    Key(PC,EKeys::W,false);Go(W,P,TEXT("crawl_back"));Key(PC,EKeys::S,true);return;
   }
   if(Step==TEXT("crawl_back")&&Age>=.5)
   {if(!Check(Peak>55&&Peak<65&&FVector::Dist2D(Feet,Start)>10,TEXT("crawl_backward_physical")))return;Key(PC,EKeys::S,false);Go(W,P,TEXT("crawl_stop"));return;}
   if(Step==TEXT("crawl_stop")&&Age>=1)
   {if(!Check(P->GetVelocity().Size2D()<2,TEXT("crawl_key_release")))return;Tap(PC,EKeys::Z);Go(W,P,TEXT("reload_wait"));return;}
   if(Step==TEXT("reload_wait")&&Age>=1){AmmoBefore=Number(P,TEXT("LoadedAmmo"))+Number(P,TEXT("ReserveAmmo"));Tap(PC,EKeys::R);Go(W,P,TEXT("reload"));return;}
   if(Step==TEXT("reload")&&Age>=9){if(!Check(Name(P,TEXT("ActionState"))==TEXT("Ready")&&Number(P,TEXT("LoadedAmmo"))==8&&Number(P,TEXT("LoadedAmmo"))+Number(P,TEXT("ReserveAmmo"))==AmmoBefore,TEXT("original_reload_conserved")))return;AmmoBefore=Number(P,TEXT("LoadedAmmo"));Tap(PC,EKeys::LeftMouseButton);Go(W,P,TEXT("fire"));return;}
   if(Step==TEXT("fire")&&Age>=1){if(!Check(Number(P,TEXT("LoadedAmmo"))==AmmoBefore-1,TEXT("original_fire_consumes_one")))return;Image(PC,TEXT("actions_final"));Go(W,P,TEXT("image_settle"));return;}
   if(Step==TEXT("image_settle")&&Age>=2)Finish(TEXT("pass_scoped_input_numeric_visual_review_separate"));return;
  }
  if(M->LivingDefenders!=LastDefenders)
  {LastDefenders=M->LivingDefenders;Event(FString::Printf(TEXT("defenders_%d_unlocked_%d"),LastDefenders,M->CheckpointUnlocked()));if(LastDefenders>0&&M->CheckpointUnlocked()){Finish(TEXT("failed_premature_checkpoint"));return;}}
  if(Step==TEXT("preload")&&Age>=9)
  {if(!Check(Number(P,TEXT("LoadedAmmo"))==8&&Number(P,TEXT("LoadedAmmo"))+Number(P,TEXT("ReserveAmmo"))==18,TEXT("safe_start_reload_conserved")))return;Go(W,P,TEXT("bridge"));Move(PC,M->FarBankFeet);return;}
  if(Step==TEXT("bridge"))
  {FireVisible(W,P,PC,M->FarBankFeet);if(M->Phase==TEXT("Clearing")||M->Phase==TEXT("Occupying")){CombatHalted=false;Go(W,P,TEXT("g1"));Move(PC,M->BridgeheadFeet);}return;}
  if(Step==TEXT("g1"))
  {FireVisible(W,P,PC,M->BridgeheadFeet);if(M->Phase!=TEXT("Won")||!M->InsideCheckpoint())return;if(!Check(M->CheckpointPromptVisible&&M->SaveSerial==0,TEXT("clear_three_entry_prompt_no_autosave")))return;Image(PC,TEXT("checkpoint_prompt"));Go(W,P,TEXT("prompt_image"));return;}
  if(Step==TEXT("prompt_image")&&Age>=1){Tap(PC,EKeys::Escape);Go(W,P,TEXT("decline"));return;}
  if(Step==TEXT("decline")&&Age>=2)
  {if(!Check(!M->CheckpointPromptVisible&&M->SaveSerial==0,TEXT("decline_no_save")))return;Go(W,P,TEXT("leave"));Move(PC,M->BridgeheadFeet+FVector(-500,0,0));return;}
  if(Step==TEXT("leave"))
  {if(M->InsideCheckpoint()||P->GetVelocity().Size2D()>2)return;if(!Check(!M->CheckpointPromptVisible&&M->SaveSerial==0,TEXT("leave_no_save")))return;Go(W,P,TEXT("reenter"));Move(PC,M->BridgeheadFeet);return;}
  if(Step==TEXT("reenter"))
  {if(!M->InsideCheckpoint()||!M->CheckpointPromptVisible)return;Tap(PC,EKeys::E);if(!Check(M->SaveSerial==0,TEXT("moving_confirmation_denied")))return;Go(W,P,TEXT("settle"));return;}
  if(Step==TEXT("settle")&&Age>=4)
  {if(!Check(M->CheckpointPromptVisible&&M->SaveSerial==0,TEXT("reentry_no_autosave")))return;Tap(PC,EKeys::E);if(!Check(M->SaveSerial==1&&!M->CheckpointPromptVisible,TEXT("explicit_safe_confirmation_once")))return;Image(PC,TEXT("checkpoint_saved"));Go(W,P,TEXT("saved_image"));return;}
  if(Step==TEXT("saved_image")&&Age>=1){Generation=M->RunGeneration;Go(W,P,TEXT("load_wait"));Tap(PC,EKeys::F9);return;}
  if(Step==TEXT("load_wait"))
  {if(M->RunGeneration==Generation||M->Phase==TEXT("Preparing"))return;if(!Check(M->Phase==TEXT("Won")&&M->SaveSerial==1&&M->CheckpointUnlocked(),TEXT("fresh_saved_checkpoint_load")))return;FString Why;if(!Check(ParisGameplayAV::VerifyRestoredCorpses(W,Why),TEXT("first_loaded_frame_terminal_corpses")))return;Root->SetStringField(TEXT("first_loaded_audio"),ParisGameplayAV::Inspect(W));Go(W,P,TEXT("loaded_settle"));return;}
  if(Step==TEXT("loaded_settle")){FString Why;if(!ParisGameplayAV::VerifyRestoredCorpses(W,Why)){Finish(TEXT("failed_restored_corpse_replay"));return;}if(Age>=3){Root->SetStringField(TEXT("settled_loaded_audio"),ParisGameplayAV::Inspect(W));Event(TEXT("pass_restored_corpses_stopped_for_three_seconds"));Image(PC,TEXT("checkpoint_loaded"));Go(W,P,TEXT("loaded_image"));}return;}
  if(Step==TEXT("loaded_image")&&Age>=1){if(Mode==TEXT("legacy")){Finish(TEXT("pass_legacy_v5_terminal_corpse_compatibility"));return;}Generation=M->RunGeneration;Go(W,P,TEXT("restart_wait"));Tap(PC,EKeys::F6);return;}
  if(Step==TEXT("restart_wait"))
  {if(M->RunGeneration==Generation||M->Phase!=TEXT("Ready"))return;if(!Check(!M->CheckpointUnlocked()&&!M->CheckpointPromptVisible&&M->LivingDefenders==3,TEXT("full_restart_checkpoint_reset")))return;Finish(TEXT("pass_checkpoint_numeric_visual_review_separate"));}
 }
public:
 void StartupModule()override
 {
  ParisGameplayAV::Initialize();
  if(!FParse::Value(FCommandLine::Get(),TEXT("ParisUXTest="),Mode)||!FParse::Value(FCommandLine::Get(),TEXT("ParisUXTestOut="),Out))return;
  check(Mode==TEXT("actions")||Mode==TEXT("checkpoint")||Mode==TEXT("legacy"));IFileManager::Get().MakeDirectory(*Out,true);
  Handle=FWorldDelegates::OnWorldPostActorTick.AddRaw(this,&FParisUXRevisionModule::Tick);
 }
 void ShutdownModule()override{if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);ParisGameplayAV::Shutdown();}
};
IMPLEMENT_MODULE(FParisUXRevisionModule,ParisBridgeMissionV1)
