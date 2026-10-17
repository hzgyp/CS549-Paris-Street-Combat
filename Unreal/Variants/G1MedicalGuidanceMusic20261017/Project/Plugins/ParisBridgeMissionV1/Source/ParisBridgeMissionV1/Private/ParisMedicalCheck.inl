// Explicit opt-in runtime driver. Normal launch has neither option.
namespace {
bool ProbeRecording=false;bool ProbeInitialized=false,ProbeDone=false;FString ProbeMode,ProbeOut,ProbeBaseline;int ProbeStep=0;double ProbeAt=0,ProbeBegin=0,ProbeHP=0,ProbeRestoredAt=0;uint32 ProbeSeed=0;TArray<TSharedPtr<FJsonValue>> ProbeChecks;
TSharedPtr<FJsonObject> ProbeParse(const FString& Text){TSharedPtr<FJsonObject> O;auto R=TJsonReaderFactory<>::Create(Text);FJsonSerializer::Deserialize(R,O);return O;}
FString ProbeJson(const TSharedPtr<FJsonObject>& O){FString T;auto J=TJsonWriterFactory<>::Create(&T);FJsonSerializer::Serialize(O.ToSharedRef(),J);return T;}
void ProbeKey(APlayerController* PC,FKey K,bool Down){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1:0));}
void ProbeTap(APlayerController* PC,FKey K){ProbeKey(PC,K,true);ProbeKey(PC,K,false);}
void ProbeFinish(UWorld* W,const FString& Status){if(ProbeDone)return;ProbeDone=true;if(ProbeRecording){UAudioMixerBlueprintLibrary::StopRecordingOutput(W,EAudioRecordingExportType::WavFile,TEXT("actual_context_mix"),ProbeOut);ProbeRecording=false;}auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Status);O->SetStringField(TEXT("mode"),ProbeMode);O->SetStringField(TEXT("scope"),TEXT("Opt-in separate UserDir; actual earned CP0 load, original damage endpoints and real E/H/posture/V/save/load inputs. Original PC_EnableCombat(false), AI brain holds and pawn placement are declared fixtures; no health, inventory, claim or mine assignment. No natural-combat/travel or human appearance acceptance."));O->SetArrayField(TEXT("checks"),ProbeChecks);O->SetStringField(TEXT("state"),AParisBridgeMission::Find(W)->ReadMissionState());FFileHelper::SaveStringToFile(ProbeJson(O),*(ProbeOut/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);FPlatformMisc::RequestExit(false);}
bool ProbeCheck(UWorld* W,bool Value,const TCHAR* Label){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("name"),Label);O->SetBoolField(TEXT("pass"),Value);ProbeChecks.Add(MakeShared<FJsonValueObject>(O));if(!Value)ProbeFinish(W,FString(TEXT("failed_"))+Label);return Value;}
void ProbeNext(UWorld* W,int Step){ProbeStep=Step;ProbeAt=FPlatformTime::Seconds();UE_LOG(LogTemp,Display,TEXT("PARIS_MEDICAL_CHECK step=%d"),Step);}
void ProbeDamage(ACharacter* P,double Amount){auto* F=P->FindFunction(TEXT("PC_ApplyDamage"));check(F);FStructOnScope Params(F);auto* N=CastField<FNumericProperty>(F->FindPropertyByName(TEXT("Amount")));check(N);N->SetFloatingPointPropertyValue(N->ContainerPtrToValuePtr<void>(Params.GetStructMemory()),Amount);P->ProcessEvent(F,Params.GetStructMemory());}
void ProbePicture(UWorld* W,const TCHAR* Name){
 FScreenshotRequest::RequestScreenshot(ProbeOut/(FString(Name)+TEXT(".png")),false,false);
 auto* PC=UGameplayStatics::GetPlayerController(W,0);if(!PC)return;FVector Eye;FRotator Rotation;PC->GetPlayerViewPoint(Eye,Rotation);FTransform View(Rotation,Eye);
 for(TActorIterator<AParisFirstPersonApprovedActor> It(W);It;++It)if(It->GetOwner()==PC->GetPawn()&&It->Pose){
  auto O=MakeShared<FJsonObject>();O->SetBoolField(TEXT("actor_hidden"),It->IsHidden());O->SetBoolField(TEXT("pose_visible"),It->Pose->IsVisible());O->SetBoolField(TEXT("pose_hidden"),It->Pose->bHiddenInGame);O->SetBoolField(TEXT("medical_source"),It->HasMedicalPoseSource());O->SetNumberField(TEXT("actual_posture"),Num(PC->GetPawn(),TEXT("DesiredPosture")));
  for(const TCHAR* Bone:{TEXT("spine_03"),TEXT("upperarm_l"),TEXT("upperarm_r"),TEXT("hand_l"),TEXT("hand_r")}){const FVector At=It->Pose->GetSocketLocation(Bone),V=View.InverseTransformPosition(At);FVector2D Screen;const bool Projected=PC->ProjectWorldLocationToScreen(At,Screen);auto B=MakeShared<FJsonObject>();B->SetArrayField(TEXT("camera_cm"),{MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)});B->SetBoolField(TEXT("projected"),Projected);B->SetArrayField(TEXT("screen_px"),{MakeShared<FJsonValueNumber>(Screen.X),MakeShared<FJsonValueNumber>(Screen.Y)});O->SetObjectField(Bone,B);}
  FFileHelper::SaveStringToFile(ProbeJson(O),*(ProbeOut/(FString(Name)+TEXT("_bones.json"))),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);break;
 }
}
void ProbeHoldAI(UWorld* W){for(TActorIterator<ACharacter>I(W);I;++I)if(!I->IsPlayerControlled())if(auto* AI=Cast<AAIController>(I->GetController())){if(auto* F=AI->FindFunction(TEXT("PC_EnableCombat"))){FStructOnScope Args(F);if(auto* B=FindFProperty<FBoolProperty>(F,TEXT("Enabled"))){B->SetPropertyValue_InContainer(Args.GetStructMemory(),false);AI->ProcessEvent(F,Args.GetStructMemory());}}AI->StopMovement();if(AI->GetBrainComponent())AI->GetBrainComponent()->PauseLogic(TEXT("Opt-in medical check isolation"));}}
bool ProbeMusic(UWorld* W,float Expected,const TCHAR* Label){int32 Count=0;float Gain=-1;for(TObjectIterator<UAudioComponent> I;I;++I)if(I->GetWorld()==W&&I->IsPlaying())if(auto* Wave=Cast<USoundWaveProcedural>(I->Sound))if(Wave->NumChannels==2){++Count;Gain=I->VolumeMultiplier;}static FString WaitingContext;static double WaitingSince=0;const double Now=FPlatformTime::Seconds();if(WaitingContext!=Label){WaitingContext=Label;WaitingSince=Now;}if((Count!=1||!FMath::IsNearlyEqual(Gain,Expected,.035f))&&Now-WaitingSince<12)return false;auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("settle_wait_seconds"),Now-WaitingSince);O->SetStringField(TEXT("music_context"),Label);O->SetNumberField(TEXT("component_gain"),Gain);O->SetNumberField(TEXT("expected"),Expected);O->SetNumberField(TEXT("streams"),Count);ProbeChecks.Add(MakeShared<FJsonValueObject>(O));return ProbeCheck(W,Count==1&&FMath::IsNearlyEqual(Gain,Expected,.035f),Label);}
void ProbeNear(ACharacter* P,FVector Feet){P->SetActorLocation(Feet+FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()+4),false,nullptr,ETeleportType::TeleportPhysics);P->GetCharacterMovement()->StopMovementImmediately();}
void ProbeAim(APlayerController* PC,FVector At){FVector Eye;FRotator R;PC->GetPlayerViewPoint(Eye,R);PC->SetControlRotation((At-Eye).Rotation());}
}
void Diagnostics(UWorld* W,float){
 if(!ProbeInitialized){ProbeInitialized=true;if(!FParse::Value(FCommandLine::Get(),TEXT("ParisMedicalCheck="),ProbeMode))return;FParse::Value(FCommandLine::Get(),TEXT("ParisMedicalOut="),ProbeOut);IFileManager::Get().MakeDirectory(*ProbeOut,true);ProbeBegin=FPlatformTime::Seconds();}
 if(ProbeMode.IsEmpty()||ProbeDone)return;
 auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;if(!M||!P)return;
 if(FPlatformTime::Seconds()-ProbeBegin>160){ProbeFinish(W,FString::Printf(TEXT("failed_deadline_step_%d"),ProbeStep));return;}
 if(M->Phase==TEXT("Error")){ProbeFinish(W,TEXT("failed_mission_preparation"));return;}
 if(M->Phase==TEXT("Preparing"))return;
 auto& S=State(W);auto& E=ParisTacticalEquipment::Session(W);const double Age=FPlatformTime::Seconds()-ProbeAt;
 ProbeHoldAI(W);
 if(FScreenshotRequest::IsScreenshotRequested())return;
 if(ProbeStep==0){if(M->Phase==TEXT("Ready")){if(!ProbeCheck(W,M->LoadCheckpoint(),TEXT("request_actual_earned_CP0_load")))return;ProbeNext(W,1);}return;}
 if(ProbeStep==1){
  if(M->VerifiedRestoreState.IsEmpty())return;if(ProbeRestoredAt==0)ProbeRestoredAt=FPlatformTime::Seconds();if(FPlatformTime::Seconds()-ProbeRestoredAt<3.2)return;
  if(!ProbeCheck(W,M->Phase==TEXT("TrainingCheckpoint")&&!ParisTutorial::CombatStarted(M)&&M->LivingDefenders==3,TEXT("actual_CP0_with_three_live_guards")))return;
  if(!ProbeMusic(W,.55f,TEXT("actual_training_music_gain")))return;UAudioMixerBlueprintLibrary::StartRecordingOutput(W,160);ProbeRecording=true;
  ProbeBaseline=ProbeJson(ProbeParse(M->ReadMissionState())->GetObjectField(TEXT("snapshot"))->GetObjectField(TEXT("medical")));ProbeSeed=S.Seed;
  if(M->CheckpointDialogVisible()){M->ActivateCheckpointDialog(0);return;}M->DismissCheckpointPrompt();
  if(!ProbeCheck(W,M->StartTutorialCombat(),TEXT("normal_combat_transition_from_earned_CP0")))return;ProbeHoldAI(W);ProbeNext(W,2);return;
 }
 if(ProbeStep==2){
  if(Age<3)return;
  if(!ProbeMusic(W,.80f,TEXT("actual_approach_music_gain")))return;
  int InvalidUV=0;for(const auto& Slot:PouchMesh()->GetStaticMaterials())InvalidUV+=!Slot.UVChannelData.bInitialized;
  for(TActorIterator<AActor> It(W);It;++It)if(It->ActorHasTag(TEXT("ParisEquipmentOwned"))){TInlineComponentArray<UStaticMeshComponent*> Parts;It->GetComponents(Parts);for(auto* Part:Parts)if(UStaticMesh* MeshPart=Part->GetStaticMesh())for(const auto& Slot:MeshPart->GetStaticMaterials())if(!Slot.UVChannelData.bInitialized){++InvalidUV;UE_LOG(LogTemp,Error,TEXT("PARIS_MEDICAL_UV_UNINITIALIZED mesh=%s actor=%s"),*MeshPart->GetPathName(),*It->GetName());}}
  if(!ProbeCheck(W,InvalidUV==0,TEXT("native_pouch_and_live_equipment_UV_streaming_metadata_initialized")))return;
  if(!ProbeCheck(W,S.Held==0&&S.Used==0&&S.Sources[0].State==Claim::Waiting&&E.Supplies[2].Retired&&!E.Supplies[2].Visual.IsValid(),TEXT("zero_medicine_before_death_and_duplicate_box_absent")))return;
  ParisTutorialSoundscape::Greeting(M,0);ProbeNext(W,201);return;
 }
 if(ProbeStep==201){if(Age<.35)return;if(!ProbeCheck(W,!ParisTutorialSoundscape::Subtitle(M).IsEmpty(),TEXT("actual_ally_speech_active"))||!ProbeMusic(W,.80f*.22f,TEXT("actual_speech_ducks_music")))return;ProbeNext(W,202);return;}
 if(ProbeStep==202){if(Age<5)return;if(!ProbeMusic(W,.80f,TEXT("actual_music_recovers_after_speech")))return;ProbeNear(P,M->FarBankFeet);ProbeNext(W,203);return;}
 if(ProbeStep==203){if(Age<3)return;if(!ProbeCheck(W,M->Phase==TEXT("Clearing"),TEXT("actual_far_bank_triggers_combat_context"))||!ProbeMusic(W,1.15f,TEXT("actual_combat_music_gain")))return;ProbeDamage(Actor(W,TEXT("German1")),1000);ProbeNext(W,3);return;}
 if(ProbeStep==3){if(!S.Sources[0].Visual.IsValid())return;if(!ProbeCheck(W,S.Sources[0].State==Claim::Available&&S.Sources[0].HasKit,TEXT("actual_registered_death_spawns_approved_native_pouch")))return;ProbeNear(P,S.Sources[0].Position+FVector(120,0,0));ProbeNext(W,4);return;}
 if(ProbeStep==4){
  if(Age<1)return;ProbeAim(PC,S.Sources[0].Position+FVector(0,0,8));if(Age<5.2||S.NoticeUntil>W->GetTimeSeconds())return;FGuidance G;if(!ProbeCheck(W,Guidance(W,G)&&G.Heading==TEXT("MEDICAL KIT DROPPED")&&G.HasPouch&&G.PickupReady,TEXT("persistent_first_drop_panel_and_visible_marker_after_old_four_second_timeout")))return;ProbePicture(W,TEXT("pickup_target_audit"));
  if(!ProbeCheck(W,!PickupHint(W).IsEmpty(),TEXT("visible_reachable_actual_E_target")))return;ProbePicture(W,TEXT("pouch_before_pickup"));ProbeNext(W,401);return;
 }
 if(ProbeStep==401){if(Age<.35)return;PC->SetControlRotation(FRotator(0,PC->GetControlRotation().Yaw+180,0));ProbeNext(W,402);return;}
 if(ProbeStep==402){if(Age<.6)return;FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);FGuidance Away;const bool Present=Guidance(W,Away);const bool Behind=FVector::DotProduct(View.Vector(),(S.Sources[0].Position+FVector(0,0,12)-Eye).GetSafeNormal())<.10;auto CameraAudit=MakeShared<FJsonObject>();CameraAudit->SetStringField(TEXT("fixture"),TEXT("rear_camera"));CameraAudit->SetStringField(TEXT("view"),View.ToString());CameraAudit->SetBoolField(TEXT("behind"),Behind);CameraAudit->SetBoolField(TEXT("guidance_present"),Present);CameraAudit->SetBoolField(TEXT("has_marker"),Away.HasPouch);ProbeChecks.Add(MakeShared<FJsonValueObject>(CameraAudit));if(!ProbeCheck(W,Behind&&Present&&(!Away.HasPouch||!Away.PouchLocation.Equals(S.Sources[0].Position+FVector(0,0,65),1)),TEXT("actual_rendered_view_hides_rear_first_pouch_but_preserves_lesson")))return;ProbeAim(PC,S.Sources[0].Position+FVector(0,0,8));ProbeNext(W,403);return;}
 if(ProbeStep==403){if(Age<.6)return;FGuidance G;if(!ProbeCheck(W,Guidance(W,G)&&G.PickupReady,TEXT("real_camera_return_restores_pickup_marker")))return;ProbeTap(PC,EKeys::Escape);FGuidance Modal;const bool Hidden=!Guidance(W,Modal);ProbeTap(PC,EKeys::Escape);if(!ProbeCheck(W,Hidden,TEXT("medical_guidance_hidden_during_pause_menu")))return;ProbeNext(W,40);return;}
 if(ProbeStep==40){if(Age<.25)return;ProbeTap(PC,EKeys::E);ProbeNext(W,5);return;}
 if(ProbeStep==5){
  if(!ProbeCheck(W,S.Held==1&&S.Sources[0].State==Claim::Claimed&&!S.Sources[0].Visual.IsValid(),TEXT("E_credits_once_and_removes_world_item")))return;
  if(E.SelectedSlot!=0){ProbeTap(PC,EKeys::MouseScrollDown);return;}
  FGuidance G;if(!ProbeCheck(W,Guidance(W,G)&&G.Action==TEXT("KIT STORED  |  HOLD H 3s WHEN INJURED")&&(!G.HasPouch||!G.PouchLocation.Equals(S.Sources[0].Position+FVector(0,0,65),1)),TEXT("pickup_shows_full_health_lesson_and_removes_only_claimed_pouch_marker")))return;ProbePicture(W,TEXT("kit_stored_full_health"));ProbeNext(W,51);return;
 }
 if(ProbeStep==51){if(Age<.5)return;ProbeTap(PC,EKeys::H);if(!ProbeCheck(W,!S.Treating&&S.Held==1&&Num(P,TEXT("Health"))==Num(P,TEXT("MaxHealth")),TEXT("full_health_refuses_without_spending")))return;
  ProbeDamage(P,45);ProbeNext(W,6);return;
 }
 if(ProbeStep==6){
  if(Age<5||S.NoticeUntil>W->GetTimeSeconds())return;
  if(ProbeMode.Contains(TEXT("observer")))ProbeTap(PC,EKeys::V);
  if(ProbeMode.Contains(TEXT("crouch"))||ProbeMode.Contains(TEXT("prone"))){ProbeNear(P,FVector(-152.397309,-22340.170222,97.169));P->SetActorRotation(FRotator(0,30.6,0));PC->SetControlRotation(FRotator(0,30.6,0));}
  else PC->SetControlRotation(FRotator(0,PC->GetControlRotation().Yaw,0));ProbeNext(W,60);return;
 }
 if(ProbeStep==60){if(Age<1.2)return;if(ProbeMode.Contains(TEXT("crouch")))ProbeKey(PC,EKeys::LeftControl,true);if(ProbeMode.Contains(TEXT("prone")))ProbeTap(PC,EKeys::Z);ProbeNext(W,7);return;}
 if(ProbeStep==7){if(Age<3.4)return;const int Wanted=ProbeMode.Contains(TEXT("prone"))?2:ProbeMode.Contains(TEXT("crouch"))?1:0;if(!ProbeCheck(W,Num(P,TEXT("DesiredPosture"))==Wanted,TEXT("real_requested_posture_entered_at_verified_clear_ground")))return;if(!ProbeCheck(W,ParisMedicalAction::Ready(P),TEXT("matching_cooked_native_bandage_and_visible_display_ready")))return;FGuidance G;if(!ProbeCheck(W,Guidance(W,G)&&G.Action==TEXT("STOP MOVING + HOLD H FOR 3 SECONDS"),TEXT("injured_first_use_instructs_real_H_controls")))return;ProbePicture(W,TEXT("injured_hold_H_guidance"));ProbeNext(W,70);return;}
 if(ProbeStep==70){if(Age<.35)return;ProbeHP=Num(P,TEXT("Health"));ProbeKey(PC,EKeys::H,true);ProbeNext(W,8);return;}
 if(ProbeStep==8){if(Age<.65)return;FGuidance G;if(!ProbeCheck(W,Guidance(W,G)&&G.Heading==TEXT("FIELD TREATMENT")&&G.TreatmentProgress>0,TEXT("real_treatment_panel_has_live_progress")))return;ProbePicture(W,TEXT("release_cancel_pose"));ProbeKey(PC,EKeys::H,false);if(!ProbeCheck(W,!S.Treating&&S.Held==1&&Num(P,TEXT("Health"))==ProbeHP,TEXT("release_cancels_without_health_or_inventory_change")))return;ProbeKey(PC,EKeys::H,true);ProbeNext(W,9);return;}
 if(ProbeStep==9){if(Age<.65)return;ProbeKey(PC,EKeys::W,true);ProbeNext(W,10);return;}
 if(ProbeStep==10){ProbeKey(PC,EKeys::W,false);ProbeKey(PC,EKeys::H,false);if(!ProbeCheck(W,!S.Treating&&S.Held==1&&Num(P,TEXT("Health"))==ProbeHP,TEXT("movement_cancels_without_spending")))return;ProbeNext(W,11);return;}
 if(ProbeStep==11){if(Age<.8)return;ProbeKey(PC,EKeys::H,true);ProbeNext(W,12);return;}
 if(ProbeStep==12){if(Age<.65)return;ProbeDamage(P,5);ProbeNext(W,13);return;}
 if(ProbeStep==13){if(Age<.1)return;ProbeKey(PC,EKeys::H,false);if(!ProbeCheck(W,!S.Treating&&S.Held==1&&Num(P,TEXT("Health"))==ProbeHP-5,TEXT("original_damage_interrupts_without_medical_debit")))return;ProbeNext(W,14);return;}
 if(ProbeStep==14){if(Age<1.4)return;ProbeHP=Num(P,TEXT("Health"));ProbeKey(PC,EKeys::H,true);ProbeNext(W,15);return;}
 if(ProbeStep==15){if(Age<.12)return;const int Wanted=ProbeMode.Contains(TEXT("prone"))?2:ProbeMode.Contains(TEXT("crouch"))?1:0;if(!ProbeCheck(W,Num(P,TEXT("DesiredPosture"))==Wanted,TEXT("actual_requested_posture_retained_during_native_treatment")))return;if(!ProbeCheck(W,S.Treating&&S.Elapsed>0&&S.Held==1&&Num(P,TEXT("Health"))==ProbeHP,TEXT("actual_H_starts_without_early_heal_or_consumption")))return;ProbePicture(W,TEXT("treatment_early_entry"));ProbeNext(W,151);return;}
 if(ProbeStep==151){if(Age<.28)return;ProbePicture(W,TEXT("treatment_start"));ProbeNext(W,16);return;}
 if(ProbeStep==16){if(Age<1.1)return;ProbePicture(W,TEXT("treatment_middle"));ProbeNext(W,17);return;}
 if(ProbeStep==17){if(Age<1.1)return;ProbePicture(W,TEXT("treatment_late"));ProbeNext(W,18);return;}
 if(ProbeStep==18){if(S.Treating)return;ProbeKey(PC,EKeys::H,false);if(!ProbeCheck(W,S.Held==0&&S.Used==1&&Num(P,TEXT("Health"))==FMath::Min(Num(P,TEXT("MaxHealth")),ProbeHP+50),TEXT("three_second_completion_grants_fifty_and_spends_exactly_one")))return;FString Error;auto Snap=ProbeParse(M->ReadMissionState())->GetObjectField(TEXT("snapshot"));if(!ProbeCheck(W,ParisMedicalKits::Validate(Snap,Error),TEXT("actual_live_medical_receipt_validates")))return;ProbeNext(W,181);return;}
 if(ProbeStep==181){if(Age<.6)return;const int Wanted=ProbeMode.Contains(TEXT("prone"))?2:ProbeMode.Contains(TEXT("crouch"))?1:0;if(!ProbeCheck(W,Num(P,TEXT("DesiredPosture"))==Wanted,TEXT("actual_requested_posture_retained_after_weapon_return")))return;bool Restored=false;for(TActorIterator<AParisFirstPersonApprovedActor> It(W);It;++It)if(It->GetOwner()==P){Restored=!It->HasMedicalPoseSource()&&(ProbeMode.Contains(TEXT("observer"))||(It->Gun&&It->Gun->IsVisible()&&!It->Gun->bHiddenInGame&&!It->IsHidden()));break;}if(!ProbeCheck(W,Restored,TEXT("medical_pose_cleared_and_normal_view_weapon_owner_restored")))return;ProbePicture(W,TEXT("treatment_complete_weapon_restored"));ProbeNext(W,182);return;}
 if(ProbeStep==182){if(Age<4.5||S.NoticeUntil>W->GetTimeSeconds())return;FGuidance G;Guidance(W,G);if(!ProbeCheck(W,G.Action.IsEmpty(),TEXT("successful_first_treatment_retires_unfinished_teaching_after_result_notice")))return;ProbePicture(W,TEXT("first_teaching_retired"));M->LoadCheckpoint();ProbeNext(W,19);return;}
 if(ProbeStep==19){
  if(Age<.7||M->Phase!=TEXT("TrainingCheckpoint"))return;
  const auto Med=ProbeParse(M->ReadMissionState())->GetObjectField(TEXT("snapshot"))->GetObjectField(TEXT("medical"));
  if(!ProbeCheck(W,ProbeJson(Med)==ProbeBaseline&&S.Seed==ProbeSeed&&S.Held==0&&S.Used==0&&M->LivingDefenders==3&&Num(P,TEXT("Health"))==100,TEXT("actual_CP0_retry_restores_medicine_seed_counts_health_and_guards")))return;
  FGuidance G;if(!ProbeCheck(W,!Guidance(W,G),TEXT("restored_CP0_has_no_stale_combat_medical_teaching")))return;
  if(M->CheckpointDialogVisible()){M->ActivateCheckpointDialog(0);return;}M->DismissCheckpointPrompt();
  if(!ProbeCheck(W,M->StartTutorialCombat(),TEXT("second_normal_combat_transition")))return;ProbeHoldAI(W);ProbeDamage(Actor(W,TEXT("German1")),1000);ProbeNext(W,20);return;
 }
 if(ProbeStep==20){if(!S.Sources[0].Visual.IsValid())return;ProbeNear(P,S.Sources[0].Position+FVector(120,0,0));ProbeNext(W,21);return;}
 if(ProbeStep==21){if(Age<1)return;ProbeAim(PC,S.Sources[0].Position+FVector(0,0,8));if(Age<1.5)return;ProbeTap(PC,EKeys::E);if(!ProbeCheck(W,S.Held==1&&S.Used==0&&S.Seed==ProbeSeed,TEXT("retry_same_earned_drop_without_reroll_or_duplication")))return;ProbeDamage(P,45);ProbeNext(W,22);return;}
 if(ProbeStep==22){if(Age<1.4)return;ProbeKey(PC,EKeys::H,true);ProbeNext(W,23);return;}
 if(ProbeStep==23){if(Age<3.5||S.Treating)return;ProbeKey(PC,EKeys::H,false);if(!ProbeCheck(W,S.Held==0&&S.Used==1&&Num(P,TEXT("Health"))==100,TEXT("second_finite_treatment_after_rollback")))return;for(const TCHAR* Id:{TEXT("German2"),TEXT("German3")})ProbeDamage(Actor(W,Id),1000);if(Num(P,TEXT("DesiredPosture"))==2)ProbeTap(PC,EKeys::Z);ProbeKey(PC,EKeys::LeftControl,false);ProbeNear(P,M->BridgeheadFeet);ProbeNext(W,24);return;}
 if(ProbeStep==24){if(Age<4||M->Phase!=TEXT("Won"))return;if(!ProbeMusic(W,.45f,TEXT("actual_secured_music_gain")))return;if(M->CheckpointDialogVisible()){if(M->CheckpointDialogState()==TEXT("Succeeded")){auto Snap=ProbeParse(M->InspectCheckpointJournal())->GetObjectField(TEXT("snapshot"));ProbeBaseline=ProbeJson(Snap->GetObjectField(TEXT("medical")));if(!ProbeCheck(W,Snap->GetObjectField(TEXT("medical"))->GetNumberField(TEXT("used"))==1,TEXT("actual_CP1_durable_save_contains_medical_receipt")))return;M->ActivateCheckpointDialog(0);ProbeDamage(P,1000);ProbeNext(W,25);}return;}ProbeTap(PC,EKeys::E);return;}
 if(ProbeStep==25){if(Age<.6)return;FGuidance G;if(!ProbeCheck(W,!Guidance(W,G),TEXT("death_suppresses_medical_guidance")))return;if(!ProbeCheck(W,!Alive(P)&&!S.Treating&&S.Held==0,TEXT("fatal_original_damage_does_not_heal_or_reconsume")))return;if(!ProbeCheck(W,M->LoadCheckpoint(),TEXT("actual_load_after_death")))return;ProbeNext(W,26);return;}
 if(ProbeStep==26){if(Age<.7||!Alive(P))return;auto Med=ProbeParse(M->ReadMissionState())->GetObjectField(TEXT("snapshot"))->GetObjectField(TEXT("medical"));if(!ProbeCheck(W,ProbeJson(Med)==ProbeBaseline&&S.Held==0&&S.Used==1&&Num(P,TEXT("Health"))==100&&M->LivingDefenders==0,TEXT("actual_saved_CP1_restores_medical_receipt_after_death")))return;ProbePicture(W,TEXT("CP1_after_death_restore"));ProbeNext(W,27);return;}
 if(ProbeStep==27)ProbeFinish(W,TEXT("pass_medical_native_input_damage_and_snapshot_roundtrip"));
}
