// Recording-only opt-in normal input. No transforms, health, ammo, AI or pose writes.
#include "ParisDemoInput.h"
#include "ParisBridgeMission.h"
#include "ParisGameplayAV.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/InputSettings.h"
#include "Components/CapsuleComponent.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"

namespace ParisDemoInput {
namespace {
FString Mode,Out,Step=TEXT("ready"),Generation;FDelegateHandle Handle;
TWeakObjectPtr<APlayerController> Controller;TSet<FKey> Held;
double BeginWall=0,InputBeginWall=0,Since=0,LastSample=0,NextShot=0,LastHealth=100;
double GoalSince=0,LastProgress=0,LastDistance=1e9,StartYaw=0;
bool Finished=false,Started=false,SawFalling=false,SquadViewed=false,WonInputSynced=false;int32 SavedLoaded=0,SavedReserve=0;double SavedHealth=0;
FVector Goal=FVector::ZeroVector;TArray<FVector> Path;int32 Corner=0;
TSharedPtr<FJsonObject> Root=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Events,Samples;
double Number(const UObject* O,const TCHAR* N) {
 auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),N):nullptr;
 if(!P)return -9999;const void* V=P->ContainerPtrToValuePtr<void>(O);
 return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));
}
bool Flag(const UObject* O,const TCHAR* N) {auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),N):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
FString Name(const UObject* O,const TCHAR* N) {auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),N):nullptr;return P?P->GetPropertyValue_InContainer(O).ToString():TEXT("Missing");}
void Event(const FString& E) {
 auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("event"),E);R->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-BeginWall);
 Events.Add(MakeShared<FJsonValueObject>(R));UE_LOG(LogTemp,Display,TEXT("PARIS_DEMO_INPUT %s"),*E);
}
void Key(APlayerController* PC,FKey K,bool Down) {
 if(!PC||Held.Contains(K)==Down)return;
 PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1.f:0.f));
 if(Down)Held.Add(K);else Held.Remove(K);
}
void Tap(APlayerController* PC,FKey K) {Key(PC,K,true);Key(PC,K,false);}
void Release() {if(Controller.IsValid()){const auto Copy=Held.Array();for(const FKey& K:Copy)Key(Controller.Get(),K,false);}Held.Empty();}
void Finish(const FString& Status) {
 if(Finished)return;Release();Finished=true;Event(Status);Root->SetStringField(TEXT("status"),Status);
 Root->SetStringField(TEXT("mode"),Mode);Root->SetStringField(TEXT("step"),Step);Root->SetArrayField(TEXT("events"),Events);Root->SetArrayField(TEXT("samples"),Samples);
 Root->SetStringField(TEXT("scope"),TEXT("Disclosed automated normal engine input, bounded continuous look, physical key movement; no state cheats; not manual play or FPS acceptance"));
 FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Root.ToSharedRef(),Writer);
 FFileHelper::SaveStringToFile(Text,*(Out/TEXT("result.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
 // Remain visible so OBS can retain the ending; the owning launcher closes later.
}
void Go(UWorld* W,const FString& Next) {Release();Step=Next;Since=W->GetTimeSeconds();Goal=FVector::ZeroVector;Path.Reset();Corner=0;SawFalling=false;Event(TEXT("step_")+Next);}
bool Check(bool OK,const FString& E) {if(!OK){Finish(TEXT("failed_")+E);return false;}Event(TEXT("pass_")+E);return true;}
double Look(APlayerController* PC,FRotator Desired,double Dt,double Rate=55) {
 const FRotator Current=PC->GetControlRotation();const double Y=FMath::FindDeltaAngleDegrees(Current.Yaw,Desired.Yaw),P=FMath::FindDeltaAngleDegrees(Current.Pitch,Desired.Pitch);
 double YScale=1,PScale=1;
 PRAGMA_DISABLE_DEPRECATION_WARNINGS
 if(GetDefault<UInputSettings>()->bEnableLegacyInputScales){YScale=PC->GetDeprecatedInputYawScale();PScale=PC->GetDeprecatedInputPitchScale();}
 PRAGMA_ENABLE_DEPRECATION_WARNINGS
 if(FMath::Abs(YScale)<.001||FMath::Abs(PScale)<.001){Finish(TEXT("failed_input_scale"));return 180;}
 PC->AddYawInput(FMath::Clamp(Y,-Rate*FMath::Min(Dt,.05),Rate*FMath::Min(Dt,.05))/YScale);
 PC->AddPitchInput(FMath::Clamp(P,-35*FMath::Min(Dt,.05),35*FMath::Min(Dt,.05))/PScale);
 return FMath::Max(FMath::Abs(Y),FMath::Abs(P));
}
bool Drive(UWorld* W,ACharacter* P,APlayerController* PC,FVector Target,double Dt,bool Run=true) {
 const FVector Feet=P->GetNavAgentLocation();
 if(Goal!=Target){
  Goal=Target;auto* N=UNavigationSystemV1::FindPathToLocationSynchronously(W,Feet,Target,P);
  if(!N||!N->IsValid()||N->IsPartial()){Finish(TEXT("failed_complete_nav_path"));return false;}
  Path=N->PathPoints;Corner=Path.Num()>1?1:0;GoalSince=W->GetTimeSeconds();LastProgress=GoalSince;LastDistance=FVector::Dist2D(Feet,Target);Event(TEXT("physical_route_started"));
  TArray<TSharedPtr<FJsonValue>> Points;for(const FVector& V:Path)Points.Add(MakeShared<FJsonValueString>(V.ToString()));Root->SetArrayField(TEXT("route_")+Step,Points);
 }
 if(FVector::Dist2D(Feet,Target)<30){Key(PC,EKeys::W,false);Key(PC,EKeys::LeftShift,false);return P->GetVelocity().Size2D()<2;}
 while(Corner<Path.Num()-1&&FVector::Dist2D(Feet,Path[Corner])<15)++Corner;
 FVector Dir=Path[Corner]-Feet;Dir.Z=0;const double Error=Look(PC,Dir.Rotation(),Dt);
 Key(PC,EKeys::LeftShift,Run);Key(PC,EKeys::W,Error<7);
 const double D=FVector::Dist2D(Feet,Target);
 if(D<LastDistance-20){LastDistance=D;LastProgress=W->GetTimeSeconds();}
 if(W->GetTimeSeconds()-LastProgress>14||W->GetTimeSeconds()-GoalSince>90)Finish(TEXT("failed_physical_route_stall"));
 return false;
}
ACharacter* VisibleGuard(UWorld* W,ACharacter* P,APlayerController* PC) {
 FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);ACharacter* Best=nullptr;double Dist=1e30;
 for(TActorIterator<ACharacter> I(W);I;++I)if((I->ActorHasTag(TEXT("G1_German1"))||I->ActorHasTag(TEXT("G1_German2"))||I->ActorHasTag(TEXT("G1_German3")))&&!Flag(*I,TEXT("IsDead"))) {
  FHitResult H;FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisDemoSight),false,P);
  const double D=FVector::DistSquared(Eye,I->GetActorLocation());
  if(D<Dist&&W->LineTraceSingleByChannel(H,Eye,I->GetActorLocation(),ECC_Visibility,Q)&&H.GetActor()==*I){Best=*I;Dist=D;}
 }
 return Best;
}
bool Combat(UWorld* W,ACharacter* P,APlayerController* PC,double Dt) {
 auto* Target=VisibleGuard(W,P,PC);if(!Target||FVector::Dist2D(P->GetActorLocation(),Target->GetActorLocation())>1800)return false;
 Key(PC,EKeys::W,false);Key(PC,EKeys::LeftShift,false);
 FVector Eye;FRotator R;PC->GetPlayerViewPoint(Eye,R);const double Error=Look(PC,(Target->GetActorLocation()-Eye).Rotation(),Dt);
 if(Error>=.3)return true;
 auto* GP=FindFProperty<FObjectPropertyBase>(P->GetClass(),TEXT("WeaponAppearance"));auto* Gun=GP?Cast<AActor>(GP->GetObjectPropertyValue_InContainer(P)):nullptr;
 if(!Gun){Finish(TEXT("failed_original_gun_missing"));return true;}
 const FVector Muzzle=Gun->GetActorTransform().TransformPosition(FVector(0,83.23,0));FHitResult H;
 FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisDemoGunClear),false,P);const FVector Direction=(Target->GetActorLocation()-Muzzle).GetSafeNormal();
 const bool Bullet=W->LineTraceSingleByChannel(H,Muzzle,Target->GetActorLocation(),ECC_Visibility,Q)&&H.GetActor()==Target;
 const bool Barrel=!W->SweepSingleByChannel(H,Gun->GetActorLocation(),Muzzle,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(2),Q);
 const bool Clear=!W->SweepSingleByChannel(H,Muzzle-Direction*.1,Muzzle+Direction*.1,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(2),Q);
 if(!Bullet||!Barrel||!Clear)return false;
 if(Error<.3&&W->GetTimeSeconds()>=NextShot&&Name(P,TEXT("ActionState"))==TEXT("Ready")) {
  if(Number(P,TEXT("LoadedAmmo"))+Number(P,TEXT("ReserveAmmo"))<=0){Finish(TEXT("failed_original_ammo_exhausted"));return true;}
  Tap(PC,Number(P,TEXT("LoadedAmmo"))>0?EKeys::LeftMouseButton:EKeys::R);NextShot=W->GetTimeSeconds()+.45;Event(TEXT("normal_combat_input"));
 }
 return true;
}
void Sample(UWorld* W,ACharacter* P,APlayerController* PC,AParisBridgeMission* M) {
 if(W->GetTimeSeconds()-LastSample<.05)return;LastSample=W->GetTimeSeconds();
 auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("step"),Step);R->SetNumberField(TEXT("time"),W->GetTimeSeconds());R->SetNumberField(TEXT("wall"),FPlatformTime::Seconds()-BeginWall);
 R->SetStringField(TEXT("generation"),M->RunGeneration);R->SetStringField(TEXT("phase"),M->Phase);R->SetStringField(TEXT("feet"),P->GetNavAgentLocation().ToString());
 R->SetNumberField(TEXT("yaw"),PC->GetControlRotation().Yaw);R->SetNumberField(TEXT("pitch"),PC->GetControlRotation().Pitch);R->SetNumberField(TEXT("speed"),P->GetVelocity().Size2D());
 R->SetNumberField(TEXT("posture"),Number(P,TEXT("DesiredPosture")));R->SetStringField(TEXT("action"),Name(P,TEXT("ActionState")));
 R->SetNumberField(TEXT("health"),Number(P,TEXT("Health")));R->SetNumberField(TEXT("loaded"),Number(P,TEXT("LoadedAmmo")));R->SetNumberField(TEXT("reserve"),Number(P,TEXT("ReserveAmmo")));
 R->SetNumberField(TEXT("shots"),Number(P,TEXT("ShotSequence")));R->SetStringField(TEXT("outcome"),Name(P,TEXT("ShotOutcome")));
 R->SetNumberField(TEXT("defenders"),M->LivingDefenders);R->SetNumberField(TEXT("allies"),M->LivingAllies);R->SetNumberField(TEXT("serial"),M->SaveSerial);
 R->SetBoolField(TEXT("unlocked"),M->CheckpointUnlocked());R->SetBoolField(TEXT("prompt"),M->CheckpointPromptVisible);R->SetBoolField(TEXT("blocked"),Flag(P,TEXT("ProneBlocked")));
 TArray<TSharedPtr<FJsonValue>> Agents;
 for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Ally1"))||I->ActorHasTag(TEXT("G1_Ally2"))||I->ActorHasTag(TEXT("G1_German1"))||I->ActorHasTag(TEXT("G1_German2"))||I->ActorHasTag(TEXT("G1_German3"))) {
  auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("actor"),I->GetName());A->SetStringField(TEXT("position"),I->GetActorLocation().ToString());A->SetNumberField(TEXT("health"),Number(*I,TEXT("Health")));A->SetNumberField(TEXT("shots"),Number(*I,TEXT("ShotSequence")));Agents.Add(MakeShared<FJsonValueObject>(A));
 }
 R->SetArrayField(TEXT("agents"),Agents);Samples.Add(MakeShared<FJsonValueObject>(R));
 R->SetNumberField(TEXT("route_corner"),Corner);if(Path.IsValidIndex(Corner))R->SetStringField(TEXT("route_waypoint"),Path[Corner].ToString());
 if(Number(P,TEXT("Health"))<LastHealth){Event(FString::Printf(TEXT("actual_player_damage_%.1f_to_%.1f"),LastHealth,Number(P,TEXT("Health"))));LastHealth=Number(P,TEXT("Health"));}
}
void Tick(UWorld* W,ELevelTick,float Dt) {
 if(Finished||!W||!W->IsGameWorld())return;
 if(!BeginWall)BeginWall=FPlatformTime::Seconds();if(Started&&FPlatformTime::Seconds()-InputBeginWall>400){Finish(TEXT("failed_finite_deadline"));return;}
 auto* M=AParisBridgeMission::Find(W);auto* PC=UGameplayStatics::GetPlayerController(W,0);auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;if(!M||!PC||!P)return;
 if(Controller.Get()!=PC){Release();Controller=PC;LastSample=-1;}
 Sample(W,P,PC,M);const double Age=W->GetTimeSeconds()-Since;
 if(M->Phase==TEXT("Error")){Finish(TEXT("failed_mission_")+M->Feedback);return;}
 if(M->Phase==TEXT("Lost")&&Mode!=TEXT("defeat")){Finish(TEXT("failed_unplanned_defeat"));return;}
 if(Step==TEXT("ready")) {
  if(M->Phase!=TEXT("Ready")||!IFileManager::Get().FileExists(*(Out/TEXT("GO"))))return;
  if(!Started){Started=true;InputBeginWall=FPlatformTime::Seconds();Go(W,TEXT("intro"));return;}
 }
 if(Step==TEXT("intro")&&Age>=5){StartYaw=PC->GetControlRotation().Yaw;Tap(PC,EKeys::Enter);Go(W,Mode==TEXT("victory")?TEXT("reload_start"):Mode==TEXT("defeat")?TEXT("defeat_approach"):TEXT("back_to_flat"));return;}
 if(Mode==TEXT("actions")||Mode==TEXT("probe")) {
  if(Step==TEXT("back_to_flat")){Key(PC,EKeys::S,true);if(Age>=1){Go(W,TEXT("flat_settle"));}return;}
  if(Step==TEXT("flat_settle")&&Age>=1){Tap(PC,EKeys::Z);Go(W,TEXT("prone"));return;}
  if(Step==TEXT("prone")&&Age>=1){if(!Check(Number(P,TEXT("DesiredPosture"))==2,TEXT("normal_prone")))return;Go(W,TEXT("crawl"));Key(PC,EKeys::W,true);return;}
  if(Step==TEXT("crawl")&&Age>=4){Go(W,TEXT("rise"));Tap(PC,EKeys::Z);return;}
  if(Step==TEXT("rise")&&Age>=1){Go(W,TEXT("walk"));Key(PC,EKeys::W,true);return;}
  if(Step==TEXT("walk")&&Age>=2){Go(W,TEXT("run"));Key(PC,EKeys::W,true);Key(PC,EKeys::LeftShift,true);return;}
  if(Step==TEXT("run")&&Age>=2){Go(W,TEXT("slow"));Key(PC,EKeys::W,true);Key(PC,EKeys::LeftAlt,true);return;}
  if(Step==TEXT("slow")&&Age>=2){Go(W,TEXT("jump"));Key(PC,EKeys::SpaceBar,true);return;}
  if(Step==TEXT("jump")){SawFalling|=P->GetCharacterMovement()->IsFalling();if(Age>.2)Key(PC,EKeys::SpaceBar,false);if(Age>=2){if(!Check(SawFalling&&P->GetCharacterMovement()->IsMovingOnGround(),TEXT("jump_land")))return;Go(W,TEXT("crouch"));Key(PC,EKeys::LeftControl,true);}return;}
  if(Step==TEXT("crouch")&&Age>=2){if(!Check(Number(P,TEXT("DesiredPosture"))==1,TEXT("crouch")))return;Go(W,TEXT("stand"));Tap(PC,EKeys::LeftControl);return;}
  if(Step==TEXT("stand")&&Age>=1){Go(W,TEXT("continuous_turn"));return;}
  if(Step==TEXT("continuous_turn")){Look(PC,FRotator(0,StartYaw+55,0),Dt,28);if(Age>=2.5){Go(W,TEXT("turn_back"));}return;}
  if(Step==TEXT("turn_back")){Look(PC,FRotator(0,StartYaw,0),Dt,28);if(Age>=2.5){Tap(PC,EKeys::R);Go(W,TEXT("reload"));}return;}
  if(Step==TEXT("reload")&&Age>=9){if(!Check(Number(P,TEXT("LoadedAmmo"))==8&&Number(P,TEXT("ReserveAmmo"))==10,TEXT("conserved_original_reload")))return;Tap(PC,EKeys::LeftMouseButton);Go(W,TEXT("shot"));return;}
  if(Step==TEXT("shot")&&Age>=2){Check(Number(P,TEXT("LoadedAmmo"))==7,TEXT("original_shot_consumption"));if(!Finished)Finish(TEXT("pass_actions_pending_media_review"));return;}
  return;
 }
 if(Mode==TEXT("victory")) {
  if(Step==TEXT("reload_start")&&Age>=1){Tap(PC,EKeys::R);Go(W,TEXT("reload"));return;}
  if(Step==TEXT("reload")&&Age>=9){if(!Check(Number(P,TEXT("LoadedAmmo"))==8&&Number(P,TEXT("ReserveAmmo"))==10,TEXT("conserved_original_reload")))return;Go(W,TEXT("bridge"));return;}
  if(Step==TEXT("bridge")||Step==TEXT("g1")) {
   // Original Won gates flush PlayerInput; resynchronize our key ledger only.
   if(M->Phase==TEXT("Won")&&!WonInputSynced){Release();WonInputSynced=true;Event(TEXT("resync_after_original_won_key_flush"));}
   if(Step==TEXT("bridge")&&!SquadViewed&&P->GetNavAgentLocation().X>=3350){StartYaw=PC->GetControlRotation().Yaw;Go(W,TEXT("squad_turn_back"));return;}
   const FVector Target=Step==TEXT("bridge")?M->FarBankFeet:M->BridgeheadFeet;
   if(M->LivingDefenders>0&&Combat(W,P,PC,Dt))return;
   const bool Arrived=Drive(W,P,PC,Target,Dt);
   if(Step==TEXT("bridge")&&Arrived){Go(W,TEXT("g1"));return;}
   if(Step==TEXT("g1")&&M->Phase==TEXT("Won")&&M->InsideCheckpoint()&&P->GetVelocity().Size2D()<2){Go(W,TEXT("corpse_framing"));double Best=-1;for(TActorIterator<ACharacter> I(W);I;++I)if((I->ActorHasTag(TEXT("G1_German1"))||I->ActorHasTag(TEXT("G1_German2"))||I->ActorHasTag(TEXT("G1_German3")))&&Flag(*I,TEXT("IsDead"))){double D=FVector::Dist2D(P->GetActorLocation(),I->GetActorLocation());if(D>120&&D<800&&D>Best){Best=D;Goal=I->GetActorLocation()-FVector(0,0,75);}}if(Best<0)Finish(TEXT("failed_visible_corpse_target"));return;}
   return;
  }
  if(Step==TEXT("squad_turn_back")){Look(PC,FRotator(0,StartYaw+180,0),Dt,28);if(Age>=7)Go(W,TEXT("squad_observe"));return;}
  if(Step==TEXT("squad_observe")&&Age>=3){Go(W,TEXT("squad_turn_forward"));return;}
  if(Step==TEXT("squad_turn_forward")){Look(PC,FRotator(0,StartYaw,0),Dt,28);if(Age>=7){SquadViewed=true;Go(W,TEXT("bridge"));}return;}
  if(Step==TEXT("corpse_framing")){FVector Eye;FRotator R;PC->GetPlayerViewPoint(Eye,R);double Error=Look(PC,(Goal-Eye).Rotation(),Dt,28);if(Age>=8&&Error<.5){Go(W,TEXT("prompt"));return;}if(Age>12)Finish(TEXT("failed_corpse_framing"));return;}
  if(Step==TEXT("prompt")&&Age>=3){if(!Check(M->CheckpointPromptVisible&&M->SaveSerial==0,TEXT("explicit_prompt_no_autosave")))return;Tap(PC,EKeys::E);Go(W,TEXT("saved"));return;}
  if(Step==TEXT("saved")&&Age>=3){if(!Check(M->SaveSerial==1,TEXT("explicit_save")))return;SavedLoaded=Number(P,TEXT("LoadedAmmo"));SavedReserve=Number(P,TEXT("ReserveAmmo"));SavedHealth=Number(P,TEXT("Health"));StartYaw=PC->GetControlRotation().Yaw;Go(W,TEXT("safe_look"));return;}
  if(Step==TEXT("safe_look")){Look(PC,FRotator(12,StartYaw+50,0),Dt,28);if(Age>=2.5){Tap(PC,EKeys::LeftMouseButton);Go(W,TEXT("changed_ammo"));}return;}
  if(Step==TEXT("changed_ammo")&&Age>=2){if(!Check(Number(P,TEXT("LoadedAmmo"))==SavedLoaded-1,TEXT("postsave_shot")))return;Generation=M->RunGeneration;Tap(PC,EKeys::F9);Go(W,TEXT("load_wait"));return;}
  if(Step==TEXT("load_wait")){if(M->RunGeneration==Generation||M->Phase==TEXT("Preparing"))return;if(!Check(M->Phase==TEXT("Won")&&Number(P,TEXT("LoadedAmmo"))==SavedLoaded&&Number(P,TEXT("ReserveAmmo"))==SavedReserve&&Number(P,TEXT("Health"))==SavedHealth,TEXT("f9_saved_resources_restored")))return;Go(W,TEXT("corpse_observe"));return;}
  if(Step==TEXT("corpse_observe")){FString Why;if(!ParisGameplayAV::VerifyRestoredCorpses(W,Why)){Finish(TEXT("failed_terminal_corpses"));return;}if(Age>=5)Finish(TEXT("pass_victory_save_restore_pending_media_review"));return;}
 }
 if(Mode==TEXT("defeat")) {
  if(Step==TEXT("defeat_approach")) {
   if(M->Phase==TEXT("Lost")){Go(W,TEXT("lost_hold"));return;}
   auto* Target=VisibleGuard(W,P,PC);
   if(Target&&FVector::Dist2D(P->GetActorLocation(),Target->GetActorLocation())<1800){Release();FVector Eye;FRotator R;PC->GetPlayerViewPoint(Eye,R);Look(PC,(Target->GetActorLocation()-Eye).Rotation(),Dt);if(Age>15&&Number(P,TEXT("Health"))<100){Go(W,TEXT("await_enemy_defeat"));}return;}
   Drive(W,P,PC,M->BridgeheadFeet,Dt,true);if(Age>100)Finish(TEXT("failed_natural_enemy_damage_not_admitted"));return;
  }
  if(Step==TEXT("await_enemy_defeat")){if(M->Phase==TEXT("Lost")){Go(W,TEXT("lost_hold"));return;}if(Age>90||M->LivingDefenders==0){Finish(TEXT("failed_natural_defeat_not_observed"));return;}return;}
  if(Step==TEXT("lost_hold")&&Age>=4){if(!Check(Number(P,TEXT("Health"))<=0&&Flag(P,TEXT("IsDead")),TEXT("genuine_player_death")))return;Generation=M->RunGeneration;Tap(PC,EKeys::F6);Go(W,TEXT("restart_wait"));return;}
  if(Step==TEXT("restart_wait")){if(M->RunGeneration==Generation||M->Phase!=TEXT("Ready"))return;if(!Check(Number(P,TEXT("Health"))==100&&Number(P,TEXT("LoadedAmmo"))==2&&Number(P,TEXT("ReserveAmmo"))==16&&M->LivingDefenders==3&&M->LivingAllies==2&&!M->CheckpointUnlocked()&&!M->CheckpointPromptVisible&&M->SaveSerial==0,TEXT("fresh_f6_reset")))return;Go(W,TEXT("fresh_ready"));return;}
  if(Step==TEXT("fresh_ready")&&Age>=5)Finish(TEXT("pass_genuine_enemy_defeat_restart_pending_media_review"));
 }
}
}
void Initialize() {
 if(!FParse::Value(FCommandLine::Get(),TEXT("ParisDemoMode="),Mode)||!FParse::Value(FCommandLine::Get(),TEXT("ParisDemoOut="),Out))return;
 if(Mode!=TEXT("probe")&&Mode!=TEXT("actions")&&Mode!=TEXT("victory")&&Mode!=TEXT("defeat"))return;
 IFileManager::Get().MakeDirectory(*Out,true);Handle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);
}
void Shutdown() {Release();if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);}
}
