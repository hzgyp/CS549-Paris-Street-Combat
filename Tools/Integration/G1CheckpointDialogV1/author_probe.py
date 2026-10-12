"""Native input/readback/visible-dialog regression; isolated UserDir only."""
from prepare import SOURCE
B=SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1'
p=B/'Private/ParisInteractionProbe.cpp';s=p.read_text(encoding='utf-8-sig')
s=s.replace('void Tick(UWorld* W,ELevelTick,float){','''void DialogClick(AParisBridgePlayerController* P,bool Failure,int32 Button){
 int32 W=0,H=0;P->GetViewportSize(W,H);const FVector2D Ref(Failure?(Button==0?800:1120):960,644);
 auto V=ParisMissionInteraction::ScreenPoint(Ref,FIntPoint(W,H));P->SetMouseLocation(FMath::RoundToInt(V.X),FMath::RoundToInt(V.Y));Tap(P,EKeys::LeftMouseButton);
}
void Tick(UWorld* W,ELevelTick,float){''')
s=s.replace('FPlatformTime::Seconds()-Begin>100','FPlatformTime::Seconds()-Begin>125')
start=s.index(' if(Step==TEXT("moving") && Age>.15)')
end=s.index(' if(Step==TEXT("before_reload")',start)
s=s[:start]+''' if(Step==TEXT("moving") && Age>.15){
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
  if(!M->InsideCheckpoint())return;Key(PC,EKeys::S,false);
  Stage(TEXT("settle_second"));return;
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
''' +s[end:]
s=s.replace('M->SaveSerial==Serial+1,TEXT("new_save_reloads")','M->SaveSerial==Serial+2,TEXT("new_save_reloads")')
# Keep restored/new-world tests and add exact modal button hit assertions.
needle='  if(Mode==TEXT("menu")){'
s=s.replace(needle,'''  for(const FIntPoint Size:{FIntPoint(1920,1080),FIntPoint(1280,720),FIntPoint(2560,1080),FIntPoint(1080,1920)}){
   for(int32 I=0;I<2;++I)if(!Check(ParisMissionInteraction::CheckpointHit(ParisMissionInteraction::ScreenPoint(FVector2D(I==0?800:1120,644),Size),Size,true)==I,TEXT("modal_failure_scaled_hit_")+Size.ToString()+FString::FromInt(I)))return;
   if(!Check(ParisMissionInteraction::CheckpointHit(ParisMissionInteraction::ScreenPoint(FVector2D(960,644),Size),Size,false)==0 && ParisMissionInteraction::CheckpointHit(FVector2D::ZeroVector,Size,false)==INDEX_NONE,TEXT("modal_ok_scaled_hit_")+Size.ToString()))return;
  }
''' +needle)
p.write_text(s,encoding='utf-8')
print('Dedicated checkpoint dialog native probe authored')
