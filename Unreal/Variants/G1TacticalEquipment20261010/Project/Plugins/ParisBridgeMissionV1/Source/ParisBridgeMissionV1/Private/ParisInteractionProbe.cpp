// Opt-in native input/journal checks. Ordinary play never installs this delegate.
#include "ParisMissionInteraction.h"
#include "ParisBridgeMission.h"
#include "ParisGameplayAV.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformFileManager.h"
#include "HAL/PlatformTime.h"
#include "UnrealClient.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"
#include "EngineUtils.h"
#include "Components/CapsuleComponent.h"
#include "AIController.h"
#include "BrainComponent.h"

namespace ParisInteractionProbe {
namespace {
FString Mode,Out,Step=TEXT("ready"),Generation,BlockFile;
FDelegateHandle Handle;double Begin=0,Since=0;int32 Serial=0,Revision=0;bool Finished=false;
TArray<TSharedPtr<FJsonValue>> Checks;TSharedPtr<FJsonObject> Result=MakeShared<FJsonObject>();
double Number(const UObject* O,const TCHAR* N){const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),N):nullptr;if(!P)return -9999;const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));}
void Key(APlayerController* P,FKey K,bool Down){P->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1.f:0.f));}
void Tap(APlayerController* P,FKey K){Key(P,K,true);Key(P,K,false);}
void Stage(const FString& S){Step=S;Since=FPlatformTime::Seconds();}
void Finish(const FString& S){
 if(Finished)return;Finished=true;if(!BlockFile.IsEmpty())FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*BlockFile,false);
 Result->SetStringField(TEXT("status"),S);Result->SetStringField(TEXT("mode"),Mode);Result->SetArrayField(TEXT("checks"),Checks);Result->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-Begin);
 Result->SetStringField(TEXT("scope"),TEXT("UE simulated input/isolated journal, not physical OS mouse or human review; readonly negative only affects this diagnostic UserDir."));
 FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(Result.ToSharedRef(),Writer);
 FFileHelper::SaveStringToFile(Text,*(Out/TEXT("RESULT.json")));UE_LOG(LogTemp,Display,TEXT("PARIS_INTERACTION_PROBE %s"),*S);FPlatformMisc::RequestExit(false);
}
bool Check(bool B,const FString& S){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("name"),S);O->SetBoolField(TEXT("pass"),B);Checks.Add(MakeShared<FJsonValueObject>(O));if(!B)Finish(TEXT("failed_")+S);return B;}
void Image(const FString& S){FScreenshotRequest::RequestScreenshot(Out/(S+TEXT(".png")),false,false);}
void Click(AParisBridgePlayerController* P,int32 Row){int32 W=0,H=0;P->GetViewportSize(W,H);auto V=ParisMissionInteraction::ScreenPoint(FVector2D(960,772+58*Row),FIntPoint(W,H));P->SetMouseLocation(FMath::RoundToInt(V.X),FMath::RoundToInt(V.Y));Tap(P,EKeys::LeftMouseButton);}
void DialogClick(AParisBridgePlayerController* P,bool Failure,int32 Button){
 int32 W=0,H=0;P->GetViewportSize(W,H);const FVector2D Ref(Failure?(Button==0?800:1120):960,644);
 auto V=ParisMissionInteraction::ScreenPoint(Ref,FIntPoint(W,H));P->SetMouseLocation(FMath::RoundToInt(V.X),FMath::RoundToInt(V.Y));Tap(P,EKeys::LeftMouseButton);
}
TSharedPtr<FJsonObject> ParseFixture(const FString& Text){TSharedPtr<FJsonObject> Object;auto Reader=TJsonReaderFactory<>::Create(Text);FJsonSerializer::Deserialize(Reader,Object);return Object;}
// Finite, isolated admission fixture: explicit diagnostic relocation and original PC_Die.
// It is not a natural combat or squad transit recording. No ordinary-play installation.
ACharacter* FixtureActor(UWorld* World,const TCHAR* Id){
 for(TActorIterator<ACharacter> It(World);It;++It)if(It->ActorHasTag(FName(*(FString(TEXT("G1_"))+Id))))return *It;
 return nullptr;
}
bool FixtureFlag(const UObject* Actor,const TCHAR* Field){
 const auto* Value=Actor?FindFProperty<FBoolProperty>(Actor->GetClass(),Field):nullptr;
 return Value && Value->GetPropertyValue_InContainer(Actor);
}
bool FixtureDeath(UWorld* World,const TCHAR* Id){
 auto* Actor=FixtureActor(World,Id);auto* Health=Actor?FindFProperty<FNumericProperty>(Actor->GetClass(),TEXT("Health")):nullptr;
 auto* Die=Actor?Actor->FindFunction(TEXT("PC_Die")):nullptr;
 if(!Health || !Die)return false;
 void* Address=Health->ContainerPtrToValuePtr<void>(Actor);
 if(Health->IsFloatingPoint())Health->SetFloatingPointPropertyValue(Address,0);else Health->SetIntPropertyValue(Address,int64(0));
 Actor->ProcessEvent(Die,nullptr);return FixtureFlag(Actor,TEXT("IsDead"));
}
void FixtureHold(UWorld* World){
 for(TActorIterator<ACharacter> It(World);It;++It){
  auto* AI=Cast<AAIController>(It->GetController());if(!AI)continue;
  if(auto* Fn=AI->FindFunction(TEXT("PC_EnableCombat"))){
   FStructOnScope Parameters(Fn);if(auto* Enabled=FindFProperty<FBoolProperty>(Fn,TEXT("Enabled")))Enabled->SetPropertyValue_InContainer(Parameters.GetStructMemory(),false);
   AI->ProcessEvent(Fn,Parameters.GetStructMemory());
  }
  AI->StopMovement();if(AI->GetBrainComponent())AI->GetBrainComponent()->StopLogic(TEXT("Isolated checkpoint admission fixture"));
  It->GetCharacterMovement()->StopMovementImmediately();
 }
}
void ClearanceTick(UWorld* World,AParisBridgeMission* Mission,AParisBridgePlayerController* Controller,ACharacter* Player,double Age){
 if(Step==TEXT("ready")){
  if(Mission->Phase!=TEXT("Ready") || Mission->ReadySeconds<1.2)return;
  Result->SetStringField(TEXT("fixture_scope"),TEXT("Fresh original roster; diagnostic player relocation to G1, AI hold and original PC_Die endpoints. No far-bank visit or manufactured save payload; not natural gunfire."));
  Result->SetStringField(TEXT("initial"),Mission->ReadMissionState());
  if(!Check(Mission->LivingDefenders==3 && !Mission->CheckpointUnlocked() && Mission->SaveSerial==0,TEXT("fresh_three_alive_locked")))return;
  Click(Controller,0);FixtureHold(World);
  const FVector Centre=Mission->BridgeheadFeet+FVector(0,0,Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
  if(!Check(Player->SetActorLocation(Centre,false,nullptr,ETeleportType::TeleportPhysics),TEXT("isolated_player_relocation")))return;
  Player->GetCharacterMovement()->StopMovementImmediately();Stage(TEXT("zero_dead"));return;
 }
 if(Step==TEXT("zero_dead") && Age>.4){
  FixtureHold(World);
  Tap(Controller,EKeys::E);Tap(Controller,EKeys::F5);
  if(!Check(Mission->Phase==TEXT("Crossing") && !Mission->CheckpointUnlocked() && Mission->SaveSerial==0 && !Mission->CheckpointDialogVisible(),TEXT("zero_dead_e_f5_denied_even_at_g1")))return;
  if(!Check(FixtureDeath(World,TEXT("German1")),TEXT("original_death_endpoint_one")))return;
  Stage(TEXT("one_dead"));return;
 }
 if(Step==TEXT("one_dead") && Age>.15){
  FixtureHold(World);Tap(Controller,EKeys::E);
  if(!Check(Mission->LivingDefenders==2 && !Mission->CheckpointUnlocked() && Mission->Phase==TEXT("Crossing") && Mission->SaveSerial==0,TEXT("one_dead_still_locked")))return;
  if(!Check(FixtureDeath(World,TEXT("German2")),TEXT("original_death_endpoint_two")))return;
  Stage(TEXT("two_dead"));return;
 }
 if(Step==TEXT("two_dead") && Age>.15){
  FixtureHold(World);Tap(Controller,EKeys::E);
  if(!Check(Mission->LivingDefenders==1 && !Mission->CheckpointUnlocked() && Mission->SaveSerial==0,TEXT("two_dead_still_locked")))return;
  Tap(Controller,EKeys::LeftControl);Stage(TEXT("last_death"));return;
 }
 if(Step==TEXT("last_death") && Age>.7){
  FixtureHold(World);
  if(!Check(Number(Player,TEXT("DesiredPosture"))==1,TEXT("original_crouch_before_clearance")))return;
  if(!Check(FixtureDeath(World,TEXT("German3")),TEXT("original_death_endpoint_three")))return;
  Stage(TEXT("clearance"));return;
 }
 if(Step==TEXT("clearance") && Age>.15){
  auto State=ParseFixture(Mission->ReadMissionState());
  if(!Check(Mission->Phase==TEXT("Won") && Mission->LivingDefenders==0 && Mission->CheckpointUnlocked(),TEXT("last_death_wins_without_far_bank_or_occupation")))return;
  if(!Check(State && !State->GetBoolField(TEXT("bridge_transit_complete")) && FixtureActor(World,TEXT("Ally1"))->GetActorLocation().X<5600 && FixtureActor(World,TEXT("Ally2"))->GetActorLocation().X<5600,TEXT("both_living_allies_unfinished_transit_not_a_gate")))return;
  if(!Check(Mission->InsideCheckpoint() && Mission->CheckpointSaveBlockReason().IsEmpty(),TEXT("crouched_clearance_admitted")))return;
  Result->SetStringField(TEXT("cleared"),Mission->ReadMissionState());
  Result->SetNumberField(TEXT("saved_posture"),Number(Player,TEXT("DesiredPosture")));
  Result->SetNumberField(TEXT("saved_capsule_half"),Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
  Key(Controller,EKeys::W,true);Stage(TEXT("move_save"));return;
 }
 if(Step==TEXT("move_save") && Age>.15){
  if(Player->GetVelocity().Size2D()<20)return;
  if(!Check(Mission->InsideCheckpoint() && Mission->CheckpointSaveBlockReason().IsEmpty(),TEXT("moving_crouched_player_has_no_save_blocker")))return;
  Tap(Controller,EKeys::E);Controller->RefreshInteractionMenu();
  if(!Check(Mission->CheckpointDialogState()==TEXT("Saving") && Mission->SaveSerial==0,TEXT("e_queues_save_without_movement_wait")))return;
  Tap(Controller,EKeys::E);Image(TEXT("saving"));Stage(TEXT("saved_one"));return;
 }
 if(Step==TEXT("saved_one")){
  if(Mission->CheckpointDialogState()==TEXT("Failed")){Result->SetStringField(TEXT("unexpected_failure"),Mission->CheckpointDialogDetail());Finish(TEXT("failed_clearance_save"));return;}
  if(Mission->CheckpointDialogState()!=TEXT("Succeeded"))return;
  Key(Controller,EKeys::W,false);
  if(!Check(Mission->SaveSerial==1 && !Mission->CheckpointPromptVisible,TEXT("moving_crouched_save_readback_success")))return;
  Result->SetStringField(TEXT("first_journal"),Mission->InspectCheckpointJournal());Image(TEXT("saved_window"));Stage(TEXT("ack_one"));return;
 }
 if(Step==TEXT("ack_one") && Age>.5){
  DialogClick(Controller,false,0);Controller->RefreshInteractionMenu();Tap(Controller,EKeys::E);Tap(Controller,EKeys::F5);
  if(!Check(Mission->SaveSerial==1 && !Mission->CheckpointDialogVisible() && !Mission->CheckpointPromptVisible && !Controller->IsMoveInputIgnored() && !Controller->IsLookInputIgnored(),TEXT("ack_hides_prompt_and_repeats_do_not_write")))return;
  Image(TEXT("clean_hud"));Key(Controller,EKeys::W,true);Stage(TEXT("leave"));return;
 }
 if(Step==TEXT("leave")){
  if(Mission->InsideCheckpoint())return;Key(Controller,EKeys::W,false);Tap(Controller,EKeys::E);
  if(!Check(Mission->SaveSerial==1 && !Mission->CheckpointDialogVisible(),TEXT("outside_circle_not_an_interaction")))return;
  Key(Controller,EKeys::S,true);Stage(TEXT("reenter"));return;
 }
 if(Step==TEXT("reenter")){
  if(!Mission->InsideCheckpoint())return;Key(Controller,EKeys::S,false);Stage(TEXT("disk_failure"));return;
 }
 if(Step==TEXT("disk_failure") && Age>.3){
  const FString First=FPaths::ProjectSavedDir()/TEXT("SaveGames")/(Mission->SlotPrefix+TEXT("_A.sav"));
  BlockFile=FPaths::ProjectSavedDir()/TEXT("SaveGames")/(Mission->SlotPrefix+TEXT("_B.sav"));
  if(!Check(IFileManager::Get().Copy(*BlockFile,*First,true,true)==COPY_OK && FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*BlockFile,true),TEXT("isolated_second_slot_readonly_fixture")))return;
  Tap(Controller,EKeys::E);Stage(TEXT("disk_failed"));return;
 }
 if(Step==TEXT("disk_failed")){
  if(Mission->CheckpointDialogState()!=TEXT("Failed"))return;
  if(!Check(Mission->SaveSerial==1 && Mission->CheckpointDialogDetail().Contains(TEXT("write failed")),TEXT("real_disk_failure_retains_previous_save")))return;
  Result->SetStringField(TEXT("failure_reason"),Mission->CheckpointDialogDetail());Image(TEXT("write_failed"));Stage(TEXT("retry_clear"));return;
 }
 if(Step==TEXT("retry_clear") && Age>.5){
  if(!Check(FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*BlockFile,false),TEXT("remove_only_fixture_readonly")))return;BlockFile.Empty();
  DialogClick(Controller,true,0);
  if(!Check(Mission->CheckpointDialogState()==TEXT("Saving") && Mission->SaveSerial==1,TEXT("retry_uses_same_clearance_admission")))return;
  Stage(TEXT("saved_two"));return;
 }
 if(Step==TEXT("saved_two")){
  if(Mission->CheckpointDialogState()!=TEXT("Succeeded"))return;
  if(!Check(Mission->SaveSerial==2 && !Mission->CheckpointPromptVisible,TEXT("retry_real_write_readback_success_once")))return;
  Result->SetStringField(TEXT("journal"),Mission->InspectCheckpointJournal());Tap(Controller,EKeys::Enter);Controller->RefreshInteractionMenu();
  Generation=Mission->RunGeneration;Stage(TEXT("load_new"));return;
 }
 if(Step==TEXT("load_new") && Age>.4){Tap(Controller,EKeys::F9);Stage(TEXT("loaded_new"));return;}
 if(Step==TEXT("loaded_new")){
  if(Mission->RunGeneration==Generation || Mission->Phase==TEXT("Preparing"))return;
  if(!Check(Mission->Phase==TEXT("Won") && Mission->SaveSerial==2 && Mission->CheckpointUnlocked(),TEXT("f9_completed_clearance_checkpoint_restored")))return;
  FString Why;if(!Check(ParisGameplayAV::VerifyRestoredCorpses(World,Why),TEXT("restored_corpses_terminal_first_frame")))return;
  Result->SetStringField(TEXT("reloaded"),Mission->ReadMissionState());Result->SetNumberField(TEXT("restored_capsule_half"),Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
  Stage(TEXT("restored_settle"));return;
 }
 if(Step==TEXT("restored_settle") && Age>3){
  FString Why;if(!Check(ParisGameplayAV::VerifyRestoredCorpses(World,Why) && Player->GetCharacterMovement()->IsMovingOnGround(),TEXT("restored_dead_stopped_player_grounded_three_seconds")))return;
  Result->SetStringField(TEXT("settled_restored"),Mission->ReadMissionState());Image(TEXT("restored"));Generation=Mission->RunGeneration;Tap(Controller,EKeys::F6);Stage(TEXT("fresh_restart"));return;
 }
 if(Step==TEXT("fresh_restart")){
  if(Mission->RunGeneration==Generation || Mission->Phase!=TEXT("Ready") || Mission->ReadySeconds<1)return;
  if(!Check(Mission->LivingDefenders==3 && !Mission->CheckpointUnlocked() && !Mission->CheckpointDialogVisible() && Number(Player,TEXT("LoadedAmmo"))==8 && Number(Player,TEXT("ReserveAmmo"))==10,TEXT("f6_three_alive_relocks_original_fresh_resources")))return;
  Result->SetStringField(TEXT("restart"),Mission->ReadMissionState());Stage(TEXT("clearance_finish"));return;
 }
 if(Step==TEXT("clearance_finish") && Age>.5)Finish(TEXT("pass_enemy_clear_checkpoint"));
}

void Tick(UWorld* W,ELevelTick,float){
 if(Finished || !W || !W->IsGameWorld())return;
 if(FPlatformTime::Seconds()-Begin>125){Finish(TEXT("failed_deadline"));return;}
 auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
 if(!M || !PC || !P || M->Phase==TEXT("Preparing"))return;
 if(M->Phase==TEXT("Error")){Result->SetStringField(TEXT("mission_error"),M->Feedback);Finish(TEXT("failed_mission_error"));return;}
 const double Age=FPlatformTime::Seconds()-Since;
 if(Mode==TEXT("enemy_clear")){ClearanceTick(W,M,PC,P,Age);return;}
 if(Step==TEXT("ready")){
  if(M->Phase!=TEXT("Ready") || M->ReadySeconds<1.2)return;
  PC->RefreshInteractionMenu();Result->SetStringField(TEXT("initial"),M->ReadMissionState());
  if(!Check(PC->InteractionMenuVisible() && PC->bShowMouseCursor,TEXT("ready_cursor_menu")))return;
  for(const FIntPoint Size:{FIntPoint(1920,1080),FIntPoint(1280,720),FIntPoint(2560,1080),FIntPoint(1080,1920)}){
   for(int32 I=0;I<3;++I)if(!Check(ParisMissionInteraction::MenuHit(ParisMissionInteraction::ScreenPoint(FVector2D(960,772+I*58),Size),Size)==I,TEXT("scaled_hit_")+Size.ToString()+FString::FromInt(I)))return;
   if(!Check(ParisMissionInteraction::MenuHit(FVector2D::ZeroVector,Size)==INDEX_NONE,TEXT("outside_hit_")+Size.ToString()))return;
  }
  for(const FIntPoint Size:{FIntPoint(1920,1080),FIntPoint(1280,720),FIntPoint(2560,1080),FIntPoint(1080,1920)}){
   for(int32 I=0;I<2;++I)if(!Check(ParisMissionInteraction::CheckpointHit(ParisMissionInteraction::ScreenPoint(FVector2D(I==0?800:1120,644),Size),Size,true)==I,TEXT("modal_failure_scaled_hit_")+Size.ToString()+FString::FromInt(I)))return;
   if(!Check(ParisMissionInteraction::CheckpointHit(ParisMissionInteraction::ScreenPoint(FVector2D(960,644),Size),Size,false)==0 && ParisMissionInteraction::CheckpointHit(FVector2D::ZeroVector,Size,false)==INDEX_NONE,TEXT("modal_ok_scaled_hit_")+Size.ToString()))return;
  }
  if(Mode==TEXT("menu")){
   if(!Check(!PC->MenuActionEnabled(1),TEXT("no_save_load_disabled")))return;
   Click(PC,1);
   if(!Check(M->Phase==TEXT("Ready") && PC->InteractionMenuSelection()==1 && M->Feedback.Contains(TEXT("No compatible")),TEXT("disabled_mouse_load_reason")))return;
   Tap(PC,EKeys::Down);Tap(PC,EKeys::Up);
   if(!Check(PC->InteractionMenuSelection()==0,TEXT("keyboard_skips_disabled")))return;
   Tap(PC,EKeys::Tab);if(!Check(PC->InteractionMenuSelection()==2,TEXT("tab_focus")))return;
   Tap(PC,EKeys::Down);Tap(PC,EKeys::E);
   if(!Check(M->SaveSerial==0 && M->Feedback.Contains(TEXT("three")),TEXT("locked_e_reason")))return;
   Image(TEXT("menu"));Stage(TEXT("start_click"));return;
  }
  if(!Check(PC->MenuActionEnabled(1),TEXT("old_journal_load_enabled")))return;
  Generation=M->RunGeneration;Click(PC,1);Stage(TEXT("loaded"));return;
 }
 if(Step==TEXT("start_click") && Age>.5){Click(PC,0);Stage(TEXT("started"));return;}
 if(Step==TEXT("started") && Age>.4){
  if(!Check(M->Phase==TEXT("Crossing") && !PC->bShowMouseCursor && !PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored(),TEXT("mouse_start_game_input")))return;
  if(!Check(Number(P,TEXT("ShotSequence"))==0 && Number(P,TEXT("LoadedAmmo"))==8,TEXT("menu_click_no_shot")))return;
  Key(PC,EKeys::W,true);Stage(TEXT("move"));return;
 }
 if(Step==TEXT("move") && Age>.3){double V=P->GetVelocity().Size2D();Key(PC,EKeys::W,false);if(!Check(V>20,TEXT("ordinary_move_after_menu")))return;Image(TEXT("gameplay"));Stage(TEXT("menu_finish"));return;}
 if(Step==TEXT("menu_finish") && Age>.4){Result->SetStringField(TEXT("final"),M->ReadMissionState());Finish(TEXT("pass_menu_input"));return;}
 if(Step==TEXT("loaded")){
  if(M->RunGeneration==Generation || M->Phase!=TEXT("Won"))return;
  FString Why;if(!ParisGameplayAV::VerifyRestoredCorpses(W,Why)){Finish(TEXT("failed_initial_restored_corpses"));return;}
  if(Age<3)return;
  if(!Check(M->InsideCheckpoint(),TEXT("old_journal_circle_and_terminal_corpses")))return;
  Result->SetStringField(TEXT("restored"),M->ReadMissionState());Result->SetStringField(TEXT("restored_audio"),ParisGameplayAV::Inspect(W));
  if(Mode==TEXT("restore")){Image(TEXT("fresh_restored"));Stage(TEXT("restore_finish"));return;}
  Serial=M->SaveSerial;Tap(PC,EKeys::Escape);if(!Check(!M->CheckpointPromptVisible,TEXT("dismiss_prompt")))return;
  Key(PC,EKeys::W,true);Stage(TEXT("moving"));return;
 }
 if(Step==TEXT("moving") && Age>.15){
  if(P->GetVelocity().Size()<20)return;
  Tap(PC,EKeys::E);PC->RefreshInteractionMenu();
  if(!Check(M->SaveSerial==Serial && !M->CheckpointPromptVisible && M->CheckpointDialogState()==TEXT("Waiting") && M->CheckpointDialogDetail().Contains(TEXT("Player")),TEXT("moving_e_queues_visible_wait_without_write")))return;
  Revision=M->InteractionRevision;Tap(PC,EKeys::E);Tap(PC,EKeys::E);
  if(!Check(M->SaveSerial==Serial && M->InteractionRevision==Revision,TEXT("pending_e_no_duplicate_request")))return;
  if(!Check(!PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored(),TEXT("waiting_keeps_stand_stop_controls")))return;
  Result->SetStringField(TEXT("moving_reason"),M->CheckpointDialogDetail());Image(TEXT("waiting"));Stage(TEXT("cancel_wait"));return;
 }
 if(Step==TEXT("cancel_wait") && Age>.2){
  Tap(PC,EKeys::Escape);Key(PC,EKeys::W,false);PC->RefreshInteractionMenu();
  if(!Check(!M->CheckpointDialogVisible() && !M->CheckpointPromptVisible && M->SaveSerial==Serial,TEXT("escape_cancels_pending_no_write")))return;
  Stage(TEXT("crouch_start"));return;
 }
 if(Step==TEXT("crouch_start") && Age>.8){Tap(PC,EKeys::LeftControl);Stage(TEXT("crouched"));return;}
 if(Step==TEXT("crouched") && Age>1){
  if(Number(P,TEXT("DesiredPosture"))!=1 || !P->bIsCrouched)return;
  Tap(PC,EKeys::E);
  if(!Check(M->SaveSerial==Serial && M->CheckpointDialogState()==TEXT("Waiting") && M->CheckpointDialogDetail().Contains(TEXT("Stand up")),TEXT("crouched_wait_reason")))return;
  Image(TEXT("crouched_wait"));Stage(TEXT("timeout"));return;
 }
 if(Step==TEXT("timeout") && Age>30){
  if(M->CheckpointDialogState()!=TEXT("Failed"))return;
  if(!Check(M->SaveSerial==Serial && M->CheckpointDialogDetail().Contains(TEXT("timed out")),TEXT("unsafe_timeout_not_success")))return;
  Image(TEXT("timed_out"));Stage(TEXT("cancel_timeout"));return;
 }
 if(Step==TEXT("cancel_timeout") && Age>.4){
  DialogClick(PC,true,1);PC->RefreshInteractionMenu();
  if(!Check(!M->CheckpointDialogVisible() && !PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored(),TEXT("mouse_cancel_restores_input")))return;
  Tap(PC,EKeys::LeftControl);Stage(TEXT("stand"));return;
 }
 if(Step==TEXT("stand") && Age>1.5){
  if(!M->CheckpointSaveBlockReason().IsEmpty())return;
  BlockFile=FPaths::ProjectSavedDir()/TEXT("SaveGames")/(M->SlotPrefix+((Serial+1)%2?TEXT("_A.sav"):TEXT("_B.sav")));
  const FString PreviousFile=FPaths::ProjectSavedDir()/TEXT("SaveGames")/(M->SlotPrefix+(Serial%2?TEXT("_A.sav"):TEXT("_B.sav")));
  if(!Check(IFileManager::Get().Copy(*BlockFile,*PreviousFile)==COPY_OK && FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*BlockFile,true),TEXT("isolated_readonly_valid_slot")))return;
  Tap(PC,EKeys::E);PC->RefreshInteractionMenu();
  if(!Check(M->SaveSerial==Serial && M->CheckpointDialogState()==TEXT("Saving") && !M->CheckpointPromptVisible,TEXT("saving_visible_before_any_write")))return;
  const double Shots=Number(P,TEXT("ShotSequence"));Tap(PC,EKeys::LeftMouseButton);Tap(PC,EKeys::E);Tap(PC,EKeys::F6);Tap(PC,EKeys::F9);
  if(!Check(Number(P,TEXT("ShotSequence"))==Shots && M->RunGeneration!=TEXT("") && M->SaveSerial==Serial,TEXT("saving_blocks_shot_repeat_restart_load")))return;
  if(!Check(PC->IsMoveInputIgnored() && PC->IsLookInputIgnored(),TEXT("saving_modal_locks_input")))return;
  Image(TEXT("saving"));Stage(TEXT("write_failure"));return;
 }
 if(Step==TEXT("write_failure")){
  if(M->CheckpointDialogState()!=TEXT("Failed"))return;
  if(!Check(M->SaveSerial==Serial && M->CheckpointDialogDetail().Contains(TEXT("write failed")),TEXT("write_failure_window_retains_serial")))return;
  Result->SetStringField(TEXT("write_failure_reason"),M->CheckpointDialogDetail());Image(TEXT("write_failed"));Stage(TEXT("retry"));return;
 }
 if(Step==TEXT("retry") && Age>.4){
  FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*BlockFile,false);BlockFile.Empty();
  DialogClick(PC,true,0);
  if(!Check(M->CheckpointDialogState()==TEXT("Saving") && M->SaveSerial==Serial,TEXT("mouse_retry_only_queues")))return;
  Stage(TEXT("success"));return;
 }
 if(Step==TEXT("success")){
  if(M->CheckpointDialogState()!=TEXT("Succeeded"))return;
  if(!Check(M->SaveSerial==Serial+1 && !M->CheckpointPromptVisible && M->Feedback.StartsWith(TEXT("Mission saved")),TEXT("readback_success_window_prompt_hidden")))return;
  Result->SetStringField(TEXT("saved"),M->ReadMissionState());Result->SetStringField(TEXT("journal"),M->InspectCheckpointJournal());
  Image(TEXT("saved_window"));Stage(TEXT("acknowledge"));return;
 }
 if(Step==TEXT("acknowledge") && Age>.5){
  DialogClick(PC,false,0);PC->RefreshInteractionMenu();
  if(!Check(!M->CheckpointDialogVisible() && !M->CheckpointPromptVisible && !PC->bShowMouseCursor && !PC->IsMoveInputIgnored() && !PC->IsLookInputIgnored(),TEXT("mouse_ok_closes_dialog_and_prompt")))return;
  Tap(PC,EKeys::E);Tap(PC,EKeys::E);Tap(PC,EKeys::F5);
  if(!Check(M->SaveSerial==Serial+1 && !M->CheckpointPromptVisible && !M->CheckpointDialogVisible(),TEXT("same_visit_e_f5_do_not_reopen_or_resave")))return;
  Image(TEXT("saved_clean_hud"));Stage(TEXT("leave_circle"));Key(PC,EKeys::W,true);return;
 }
 if(Step==TEXT("leave_circle")){
  if(M->InsideCheckpoint())return;Key(PC,EKeys::W,false);Tap(PC,EKeys::E);
  if(!Check(M->SaveSerial==Serial+1 && !M->CheckpointDialogVisible(),TEXT("outside_e_no_save")))return;
  Key(PC,EKeys::S,true);Stage(TEXT("reenter"));return;
 }
 if(Step==TEXT("reenter")){
  if(!M->InsideCheckpoint())return;
  Tap(PC,EKeys::E);
  if(!Check(M->CheckpointDialogState()==TEXT("Waiting") && M->SaveSerial==Serial+1,TEXT("moving_new_visit_explicit_pending_request")))return;
  Stage(TEXT("leave_pending"));return;
 }
 if(Step==TEXT("leave_pending")){
  if(M->InsideCheckpoint())return;Key(PC,EKeys::S,false);PC->RefreshInteractionMenu();
  if(!Check(!M->CheckpointDialogVisible() && !M->CheckpointPromptVisible && M->SaveSerial==Serial+1 && M->Feedback.Contains(TEXT("left")),TEXT("leaving_cancels_pending_no_write")))return;
  Key(PC,EKeys::W,true);Stage(TEXT("reenter_after_cancel"));return;
 }
 if(Step==TEXT("reenter_after_cancel")){
  if(!M->InsideCheckpoint())return;Key(PC,EKeys::W,false);Stage(TEXT("settle_second"));return;
 }
 if(Step==TEXT("settle_second") && Age>.8){
  if(!M->CheckpointSaveBlockReason().IsEmpty())return;
  if(!Check(M->CheckpointPromptVisible && M->SaveSerial==Serial+1,TEXT("new_visit_prompt_without_autosave")))return;
  Tap(PC,EKeys::E);Stage(TEXT("second_success"));return;
 }
 if(Step==TEXT("second_success")){
  if(M->CheckpointDialogState()!=TEXT("Succeeded"))return;
  if(!Check(M->SaveSerial==Serial+2 && !M->CheckpointPromptVisible,TEXT("new_visit_explicit_save_once")))return;
  Result->SetStringField(TEXT("journal"),M->InspectCheckpointJournal());Tap(PC,EKeys::Enter);PC->RefreshInteractionMenu();
  if(!Check(!M->CheckpointDialogVisible() && !M->CheckpointPromptVisible,TEXT("enter_acknowledges_success")))return;
  Generation=M->RunGeneration;Stage(TEXT("before_reload"));return;
 }
 if(Step==TEXT("before_reload") && Age>.5){Tap(PC,EKeys::F9);Stage(TEXT("new_world"));return;}
 if(Step==TEXT("new_world")){
  if(M->RunGeneration==Generation || M->Phase!=TEXT("Won"))return;
  FString Why;if(!ParisGameplayAV::VerifyRestoredCorpses(W,Why)){Finish(TEXT("failed_reloaded_corpse_replay"));return;}if(Age<3)return;
  if(!Check(M->SaveSerial==Serial+2,TEXT("new_save_reloads")))return;
  Result->SetStringField(TEXT("reloaded"),M->ReadMissionState());Image(TEXT("reloaded"));Generation=M->RunGeneration;Stage(TEXT("before_restart"));return;
 }
 if(Step==TEXT("before_restart") && Age>.5){Tap(PC,EKeys::F6);Stage(TEXT("restarted"));return;}
 if(Step==TEXT("restarted")){
  if(M->RunGeneration==Generation || M->Phase!=TEXT("Ready") || M->ReadySeconds<1)return;
  PC->RefreshInteractionMenu();if(!Check(PC->InteractionMenuVisible() && PC->MenuActionEnabled(1) && PC->bShowMouseCursor && Number(P,TEXT("LoadedAmmo"))==8 && M->LivingDefenders==3,TEXT("restart_menu_original_resources")))return;
  Result->SetStringField(TEXT("restart"),M->ReadMissionState());Stage(TEXT("restore_finish"));return;
 }
 if(Step==TEXT("restore_finish") && Age>.5)Finish(Mode==TEXT("restore")?TEXT("pass_fresh_process_restore"):TEXT("pass_checkpoint_interaction"));
}
}
void Initialize(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisInteractionProbe="),Mode))return;check(Mode==TEXT("menu") || Mode==TEXT("enemy_clear") || Mode==TEXT("restore")); /* Old synchronous/waiting checkpoint expectations are retired for this child. */check(FParse::Value(FCommandLine::Get(),TEXT("ParisInteractionOut="),Out));IFileManager::Get().MakeDirectory(*Out,true);Begin=FPlatformTime::Seconds();Handle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);}
void Shutdown(){if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);}
}
