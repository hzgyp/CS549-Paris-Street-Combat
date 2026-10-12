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
