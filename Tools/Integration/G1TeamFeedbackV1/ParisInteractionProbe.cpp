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
void Tick(UWorld* W,ELevelTick,float){
 if(Finished || !W || !W->IsGameWorld())return;
 if(FPlatformTime::Seconds()-Begin>100){Finish(TEXT("failed_deadline"));return;}
 auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;
 if(!M || !PC || !P || M->Phase==TEXT("Preparing"))return;
 if(M->Phase==TEXT("Error")){Result->SetStringField(TEXT("mission_error"),M->Feedback);Finish(TEXT("failed_mission_error"));return;}
 const double Age=FPlatformTime::Seconds()-Since;
 if(Step==TEXT("ready")){
  if(M->Phase!=TEXT("Ready") || M->ReadySeconds<1.2)return;
  PC->RefreshInteractionMenu();Result->SetStringField(TEXT("initial"),M->ReadMissionState());
  if(!Check(PC->InteractionMenuVisible() && PC->bShowMouseCursor,TEXT("ready_cursor_menu")))return;
  for(const FIntPoint Size:{FIntPoint(1920,1080),FIntPoint(1280,720),FIntPoint(2560,1080),FIntPoint(1080,1920)}){
   for(int32 I=0;I<3;++I)if(!Check(ParisMissionInteraction::MenuHit(ParisMissionInteraction::ScreenPoint(FVector2D(960,772+I*58),Size),Size)==I,TEXT("scaled_hit_")+Size.ToString()+FString::FromInt(I)))return;
   if(!Check(ParisMissionInteraction::MenuHit(FVector2D::ZeroVector,Size)==INDEX_NONE,TEXT("outside_hit_")+Size.ToString()))return;
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
  if(!Check(Number(P,TEXT("ShotSequence"))==0 && Number(P,TEXT("LoadedAmmo"))==2,TEXT("menu_click_no_shot")))return;
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
  Tap(PC,EKeys::E);Revision=M->InteractionRevision;
  if(!Check(M->SaveSerial==Serial && M->CheckpointPromptVisible && M->Feedback.Contains(TEXT("Player")),TEXT("moving_e_reopens_explains")))return;
  Result->SetStringField(TEXT("moving_reason"),M->Feedback);Tap(PC,EKeys::E);
  if(!Check(M->InteractionRevision>Revision && M->SaveSerial==Serial,TEXT("repeated_e_refreshes")))return;
  Key(PC,EKeys::W,false);Stage(TEXT("crouch_start"));return;
 }
 if(Step==TEXT("crouch_start") && Age>.8){Tap(PC,EKeys::LeftControl);Stage(TEXT("crouched"));return;}
 if(Step==TEXT("crouched") && Age>1){
  if(Number(P,TEXT("DesiredPosture"))!=1 || !P->bIsCrouched)return;
  Tap(PC,EKeys::E);if(!Check(M->SaveSerial==Serial && M->Feedback.Contains(TEXT("Stand up")),TEXT("crouched_e_stand_reason")))return;
  Image(TEXT("save_reason"));Tap(PC,EKeys::LeftControl);Stage(TEXT("stand"));return;
 }
 if(Step==TEXT("stand") && Age>1.5){
  if(!M->CheckpointSaveBlockReason().IsEmpty())return;
  BlockFile=FPaths::ProjectSavedDir()/TEXT("SaveGames")/(M->SlotPrefix+((Serial+1)%2?TEXT("_A.sav"):TEXT("_B.sav")));
  const FString PreviousFile=FPaths::ProjectSavedDir()/TEXT("SaveGames")/(M->SlotPrefix+(Serial%2?TEXT("_A.sav"):TEXT("_B.sav")));
  if(!Check(IFileManager::Get().Copy(*BlockFile,*PreviousFile)==COPY_OK && FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*BlockFile,true),TEXT("isolated_readonly_valid_slot")))return;
  Tap(PC,EKeys::E);if(!Check(M->SaveSerial==Serial && M->Feedback.Contains(TEXT("write failed")),TEXT("write_failure_retains_serial")))return;
  Result->SetStringField(TEXT("write_failure_reason"),M->Feedback);FPlatformFileManager::Get().GetPlatformFile().SetReadOnly(*BlockFile,false);BlockFile.Empty();
  Tap(PC,EKeys::Escape);Tap(PC,EKeys::E);
  if(!Check(M->SaveSerial==Serial+1 && !M->CheckpointPromptVisible && M->Feedback.StartsWith(TEXT("Mission saved")),TEXT("single_e_after_dismiss_writes_readbacks")))return;
  Result->SetStringField(TEXT("saved"),M->ReadMissionState());Result->SetStringField(TEXT("journal"),M->InspectCheckpointJournal());Image(TEXT("saved"));Generation=M->RunGeneration;Stage(TEXT("before_reload"));return;
 }
 if(Step==TEXT("before_reload") && Age>.5){Tap(PC,EKeys::F9);Stage(TEXT("new_world"));return;}
 if(Step==TEXT("new_world")){
  if(M->RunGeneration==Generation || M->Phase!=TEXT("Won"))return;
  FString Why;if(!ParisGameplayAV::VerifyRestoredCorpses(W,Why)){Finish(TEXT("failed_reloaded_corpse_replay"));return;}if(Age<3)return;
  if(!Check(M->SaveSerial==Serial+1,TEXT("new_save_reloads")))return;
  Result->SetStringField(TEXT("reloaded"),M->ReadMissionState());Image(TEXT("reloaded"));Generation=M->RunGeneration;Stage(TEXT("before_restart"));return;
 }
 if(Step==TEXT("before_restart") && Age>.5){Tap(PC,EKeys::F6);Stage(TEXT("restarted"));return;}
 if(Step==TEXT("restarted")){
  if(M->RunGeneration==Generation || M->Phase!=TEXT("Ready") || M->ReadySeconds<1)return;
  PC->RefreshInteractionMenu();if(!Check(PC->InteractionMenuVisible() && PC->MenuActionEnabled(1) && PC->bShowMouseCursor && Number(P,TEXT("LoadedAmmo"))==2 && M->LivingDefenders==3,TEXT("restart_menu_original_resources")))return;
  Result->SetStringField(TEXT("restart"),M->ReadMissionState());Stage(TEXT("restore_finish"));return;
 }
 if(Step==TEXT("restore_finish") && Age>.5)Finish(Mode==TEXT("restore")?TEXT("pass_fresh_process_restore"):TEXT("pass_checkpoint_interaction"));
}
}
void Initialize(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisInteractionProbe="),Mode))return;check(Mode==TEXT("menu") || Mode==TEXT("checkpoint") || Mode==TEXT("restore"));check(FParse::Value(FCommandLine::Get(),TEXT("ParisInteractionOut="),Out));IFileManager::Get().MakeDirectory(*Out,true);Begin=FPlatformTime::Seconds();Handle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);}
void Shutdown(){if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);}
}
