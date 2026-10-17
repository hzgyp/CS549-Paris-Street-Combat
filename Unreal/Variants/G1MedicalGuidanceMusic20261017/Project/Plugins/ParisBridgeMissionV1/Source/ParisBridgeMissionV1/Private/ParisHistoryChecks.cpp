// Opt-in isolated archive/UI/failure checks, never enabled by a normal launcher.
#include "ParisCheckpointHistory.h"
#include "ParisBridgeMission.h"
#include "ParisCombatUI.h"
#include "ParisPlayerDeath.h"
#include "ParisTutorial.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/SecureHash.h"
#include "HAL/FileManager.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"
#include "UnrealClient.h"

namespace ParisCheckpointHistory {namespace {
FString Mode,Out;bool Init=false,Done=false,HeldW=false;int Phase=0;double Begin=0,At=0,LastTrace=0;int OldSerial=0;FString Expected,LatestPayload,OldPayload,WaitGeneration;
TArray<TSharedPtr<FJsonValue>> Checks;
TSharedPtr<FJsonObject> JP(const FString& S){TSharedPtr<FJsonObject> O;auto R=TJsonReaderFactory<>::Create(S);return FJsonSerializer::Deserialize(R,O)?O:nullptr;}
FString JS(const TSharedPtr<FJsonObject>& O){FString S;auto W=TJsonWriterFactory<>::Create(&S);FJsonSerializer::Serialize(O.ToSharedRef(),W);return S;}
FString DH(const FString& S){FTCHARToUTF8 U(*S);uint8 B[20];FSHA1::HashBuffer(U.Get(),U.Length(),B);return BytesToHex(B,20);}
void Finish(AParisBridgeMission* M,const FString& Status){if(Done)return;Done=true;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Status);O->SetStringField(TEXT("mode"),Mode);O->SetArrayField(TEXT("checks"),Checks);O->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-Begin);O->SetStringField(TEXT("state"),M->ReadMissionState());O->SetStringField(TEXT("scope"),TEXT("Original native UI/input and archive methods; declared direct player-damage, archive write failures and file-corruption fixtures; not human natural combat/whole-map acceptance."));FFileHelper::SaveStringToFile(JS(O),*(Out/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);FPlatformMisc::RequestExit(false);}
bool Check(AParisBridgeMission* M,bool Good,const TCHAR* Name){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("name"),Name);O->SetBoolField(TEXT("pass"),Good);Checks.Add(MakeShared<FJsonValueObject>(O));if(!Good)Finish(M,TEXT("failed_")+FString(Name));return Good;}
void Key(APlayerController* PC,FKey K,bool Down){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1:0));}
void Tap(APlayerController* PC,FKey K){Key(PC,K,true);Key(PC,K,false);}
void Step(int Value){Phase=Value;At=FPlatformTime::Seconds();}
void Shot(const TCHAR* Name){FScreenshotRequest::RequestScreenshot(Out/FString(Name)+TEXT(".png"),false,false);}
TArray<FRecord> Rows(AParisBridgeMission* M){FString E;return List(M,E);}
void Damage(ACharacter* P){auto* F=P->FindFunction(TEXT("PC_ApplyDamage"));FStructOnScope A(F);auto* V=CastField<FNumericProperty>(F->FindPropertyByName(TEXT("Amount")));V->SetFloatingPointPropertyValue(V->ContainerPtrToValuePtr<void>(A.GetStructMemory()),1000);P->ProcessEvent(F,A.GetStructMemory());}
bool Resources(const FString& ExpectedText,const FString& ActualText){auto A=JP(ExpectedText),B=JP(ActualText);if(!A||!B)return false;auto EA=A->GetObjectField(TEXT("equipment")),EB=B->GetObjectField(TEXT("equipment"));if(JS(EA)!=JS(EB))return false;auto TA=A->GetObjectField(TEXT("tutorial")),TB=B->GetObjectField(TEXT("tutorial"));if(JS(TA)!=JS(TB))return false;for(int I=0;I<6;++I){auto X=A->GetArrayField(TEXT("actors"))[I]->AsObject(),Y=B->GetArrayField(TEXT("actors"))[I]->AsObject();for(const TCHAR* K:{TEXT("health"),TEXT("loaded"),TEXT("reserve"),TEXT("shots")})if(X->GetNumberField(K)!=Y->GetNumberField(K))return false;if(X->GetBoolField(TEXT("dead"))!=Y->GetBoolField(TEXT("dead")))return false;}return true;}
bool Move(APlayerController* PC,ACharacter* P,FVector Target){const FVector Feet=P->GetNavAgentLocation();if(FVector::Dist2D(Feet,Target)<45){if(HeldW){Key(PC,EKeys::W,false);HeldW=false;}return true;}PC->SetControlRotation(FRotator(0,(Target-Feet).Rotation().Yaw,0));if(!HeldW){Key(PC,EKeys::W,true);HeldW=true;}return false;}
void Corrupt(const FString& Slot){auto* S=Cast<UParisBridgeSave>(UGameplayStatics::CreateSaveGameObject(UParisBridgeSave::StaticClass()));S->Payload=TEXT("declared invalid archive fixture");S->Checksum=TEXT("invalid");UGameplayStatics::SaveGameToSlot(S,Slot,0);}
FString SavedText(const FString& Slot){auto* S=Cast<UParisBridgeSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));return S?S->Payload:FString();}
bool RawWrite(const FString& Slot,const FString& Text){auto* S=Cast<UParisBridgeSave>(UGameplayStatics::CreateSaveGameObject(UParisBridgeSave::StaticClass()));S->Payload=Text;S->Checksum=DH(Text);return UGameplayStatics::SaveGameToSlot(S,Slot,0);}
} // checks internals
void Diagnostics(AParisBridgePlayerController* PC){
 if(!Init){Init=true;if(!FParse::Value(FCommandLine::Get(),TEXT("ParisHistoryCheck="),Mode))return;FParse::Value(FCommandLine::Get(),TEXT("ParisHistoryOut="),Out);IFileManager::Get().MakeDirectory(*Out,true);Begin=FPlatformTime::Seconds();Step(0);}
 if(Mode.IsEmpty()||Done)return;auto* M=AParisBridgeMission::Find(PC);auto* P=Cast<ACharacter>(PC->GetPawn());if(!M||!P)return;if(M->Phase==TEXT("Error")){Finish(M,TEXT("failed_preparation_")+M->Feedback);return;}if(FPlatformTime::Seconds()-Begin>210){Finish(M,TEXT("failed_deadline"));return;}if(M->Phase==TEXT("Preparing"))return;
 const double Now=FPlatformTime::Seconds();FString E;
 if(Now-LastTrace>.5){LastTrace=Now;auto Trace=MakeShared<FJsonObject>();Trace->SetNumberField(TEXT("time"),Now-Begin);Trace->SetNumberField(TEXT("step"),Phase);Trace->SetStringField(TEXT("mission"),M->Phase);Trace->SetStringField(TEXT("generation"),M->RunGeneration);Trace->SetStringField(TEXT("dialog"),M->CheckpointDialogState());Trace->SetStringField(TEXT("active"),Active(M));Trace->SetStringField(TEXT("confirmation"),ParisCombatUI::Confirmation(PC));Trace->SetObjectField(TEXT("menu"),ParisCombatUI::Inspect(PC));FFileHelper::SaveStringToFile(JS(Trace)+TEXT("\n"),*(Out/TEXT("trace.jsonl")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);}

 if(Phase==0){auto R=Rows(M);if(R.IsEmpty()){Finish(M,TEXT("failed_no_seed_records"));return;}if(Mode==TEXT("history_persist")){
   if(!Check(M,R.Num()==1&&R[0].Id==TEXT("CP0")&&R[0].Latest&&R[0].Serial>=4,TEXT("new_process_deleted_records_stay_absent_and_latest_remains")))return;
   if(!Check(M,!Delete(M,R[0].Id,R[0].Serial,E),TEXT("new_process_cannot_delete_only_valid_checkpoint")))return;ParisCombatUI::ShowCheckpointList(PC);Shot(TEXT("history_fresh_process"));Step(40);return;
 }Expected=R[0].Payload;LatestPayload=R[0].Payload;OldSerial=R[0].Serial;WaitGeneration=M->RunGeneration;if(!M->LoadCheckpoint()){Finish(M,TEXT("failed_initial_load"));return;}Step(1);return;}
 if(Phase==1){if(M->RunGeneration==WaitGeneration||M->VerifiedRestoreState.IsEmpty())return;if(!Check(M,Resources(Expected,M->VerifiedRestoreState),TEXT("initial_actual_restore_resources_and_npc_state")))return;M->DismissCheckpointPrompt();if(Mode==TEXT("storage_faults")){Step(60);return;}if(Mode==TEXT("history_legacy")){if(!Check(M,!HasIndex(M)&&M->Phase==TEXT("TrainingCheckpoint"),TEXT("legacy_MD5_AB_snapshot_loads_without_modification")))return;OldPayload=SavedText(M->SlotPrefix+TEXT("_A"));M->InteractCheckpoint();Step(70);return;}auto R=Rows(M);if(!Check(M,R.Num()==2&&R[0].Id==TEXT("CP1")&&R[1].Id==TEXT("CP0"),TEXT("independent_CP0_CP1_records_survive_new_process")))return;OldPayload=R[1].Payload;ParisCombatUI::ShowCheckpointList(PC);Shot(TEXT("history_list"));Step(Mode==TEXT("history_stale")?80:2);return;}
 if(Now-At<.3)return;
 switch(Phase){
 case 80:{Tap(PC,EKeys::Down);auto R=Rows(M);auto Root=JP(R[1].Payload);Root->SetNumberField(TEXT("serial"),NextSerial(M,E));if(!Check(M,Save(M,JS(Root),E),TEXT("declared_store_only_republication_changes_cached_row_order")))return;Tap(PC,EKeys::Right);Tap(PC,EKeys::Enter);if(!Check(M,Rows(M).Num()==2&&Rows(M)[0].Id==TEXT("CP0")&&ParisCombatUI::Confirmation(PC).IsEmpty()&&ParisCombatUI::Inspect(PC)->GetStringField(TEXT("toast")).Contains(TEXT("changed")),TEXT("stale_selection_cannot_silently_retarget_delete_to_other_checkpoint")))return;Shot(TEXT("stale_selection_rejected"));Step(40);break;}
 case 2:{auto R=Rows(M);if(!Check(M,PC->GetWorld()->IsPaused()&&ParisCombatUI::Inspect(PC)->GetNumberField(TEXT("history_count"))==2,TEXT("browser_pauses_world_and_lists_two_points")))return;Tap(PC,EKeys::Right);Tap(PC,EKeys::Enter);if(!Check(M,ParisCombatUI::Confirmation(PC).IsEmpty()&&!Delete(M,R[0].Id,R[0].Serial,E)&&Rows(M).Num()==2,TEXT("latest_delete_disabled_in_UI_and_rejected_by_backend")))return;Shot(TEXT("latest_protected"));Step(3);break;}
 case 3:Tap(PC,EKeys::Down);Tap(PC,EKeys::Right);Tap(PC,EKeys::Enter);if(!Check(M,ParisCombatUI::Confirmation(PC)==TEXT("HistoryDelete")&&ParisCombatUI::Inspect(PC)->GetNumberField(TEXT("modal_choice"))==1,TEXT("old_delete_requires_default_cancel_confirmation")))return;Shot(TEXT("delete_default_cancel"));Step(4);break;
 case 4:Tap(PC,EKeys::Enter);if(!Check(M,Rows(M).Num()==2,TEXT("delete_cancel_preserves_both_records")))return;Tap(PC,EKeys::Left);Tap(PC,EKeys::Enter);if(!Check(M,ParisCombatUI::Confirmation(PC)==TEXT("HistoryLoad"),TEXT("old_selected_load_requires_confirmation")))return;Shot(TEXT("load_old_confirmation"));Step(5);break;
 case 5:WaitGeneration=M->RunGeneration;Tap(PC,EKeys::Left);Tap(PC,EKeys::Enter);Step(6);break;
 case 6:if(M->RunGeneration==WaitGeneration||M->VerifiedRestoreState.IsEmpty()||M->Phase!=TEXT("TrainingCheckpoint"))return;if(!Check(M,Active(M)==TEXT("CP0")&&M->LivingDefenders==3&&Resources(OldPayload,M->VerifiedRestoreState)&&Rows(M).Num()==2&&Rows(M)[0].Id==TEXT("CP1"),TEXT("old_CP0_actual_load_restores_precombat_state_without_removing_CP1")))return;M->DismissCheckpointPrompt();WaitGeneration=M->RunGeneration;Tap(PC,EKeys::F9);if(!Check(M,ParisCombatUI::Confirmation(PC)==TEXT("Load"),TEXT("F9_retry_still_has_confirmation")))return;Tap(PC,EKeys::Left);Tap(PC,EKeys::Enter);Step(7);break;
 case 7:if(M->RunGeneration==WaitGeneration||M->VerifiedRestoreState.IsEmpty()||M->Phase!=TEXT("TrainingCheckpoint"))return;if(!Check(M,Active(M)==TEXT("CP0")&&M->SaveSerial<Rows(M)[0].Serial,TEXT("F9_returns_current_selected_CP0_not_global_latest_CP1")))return;Damage(P);Check(M,true,TEXT("declared_player_damage_endpoint_for_death_retry"));Step(8);break;
 case 8:if(M->Phase!=TEXT("Lost")||ParisPlayerDeath::Presenting(PC))return;M->DismissCheckpointPrompt();WaitGeneration=M->RunGeneration;Tap(PC,EKeys::F9);Tap(PC,EKeys::Left);Tap(PC,EKeys::Enter);Step(9);break;
 case 9:if(M->RunGeneration==WaitGeneration||M->VerifiedRestoreState.IsEmpty()||M->Phase!=TEXT("TrainingCheckpoint"))return;if(!Check(M,Active(M)==TEXT("CP0")&&M->LivingDefenders==3&&Resources(OldPayload,M->VerifiedRestoreState),TEXT("actual_death_retry_restores_current_CP0_resources_and_living_guards")))return;M->DismissCheckpointPrompt();ParisCombatUI::ShowCheckpointList(PC);Tap(PC,EKeys::Down);Tap(PC,EKeys::Right);Tap(PC,EKeys::Enter);Shot(TEXT("delete_current_retry_warning"));Step(10);break;
 case 10:Tap(PC,EKeys::Left);Tap(PC,EKeys::Enter);if(!Check(M,Rows(M).Num()==1&&Rows(M)[0].Id==TEXT("CP1")&&Active(M)==TEXT("CP1"),TEXT("confirmed_old_current_record_delete_keeps_latest_and_retargets_retry")))return;Shot(TEXT("old_deleted"));Tap(PC,EKeys::Escape);Tap(PC,EKeys::Escape);M->DismissCheckpointPrompt();M->InteractCheckpoint();Step(11);break;
 case 11:if(M->CheckpointDialogState()!=TEXT("Succeeded"))return;if(!Check(M,Rows(M).Num()==2&&Rows(M)[0].Id==TEXT("CP0")&&Rows(M)[0].Serial==OldSerial+1,TEXT("new_CP0_save_after_old_load_uses_global_high_water_and_becomes_latest")))return;M->ActivateCheckpointDialog(0);Step(12);break;
 case 12:if(Move(PC,P,FVector(900,-21400,100)))Step(13);break;
 case 13:if(Move(PC,P,FVector(1200,-21400,100))){M->DismissCheckpointPrompt();M->InteractCheckpoint();Step(14);}break;
 case 14:if(M->CheckpointDialogState()!=TEXT("Succeeded"))return;if(!Check(M,Rows(M).Num()==2&&Rows(M)[0].Id==TEXT("CP0")&&Rows(M)[0].Serial==OldSerial+2,TEXT("same_checkpoint_revisit_save_updates_one_record")))return;M->ActivateCheckpointDialog(0);M->DismissCheckpointPrompt();ParisCombatUI::ShowCheckpointList(PC);Tap(PC,EKeys::Down);Tap(PC,EKeys::Right);Tap(PC,EKeys::Enter);Shot(TEXT("delete_old_CP1_confirmation"));Step(15);break;
 case 15:Tap(PC,EKeys::Left);Tap(PC,EKeys::Enter);if(!Check(M,Rows(M).Num()==1&&Rows(M)[0].Id==TEXT("CP0")&&Rows(M)[0].Latest,TEXT("old_CP1_deleted_while_latest_CP0_protected")))return;Shot(TEXT("history_final_latest"));Step(40);break;
 case 40:Finish(M,TEXT("pass_")+Mode);break;
 case 70:if(M->CheckpointDialogState()==TEXT("Succeeded")){if(Check(M,HasIndex(M)&&Rows(M).Num()==1&&Rows(M)[0].Serial==OldSerial+1&&SavedText(M->SlotPrefix+TEXT("_A"))==OldPayload,TEXT("first_history_save_imports_legacy_readonly_and_preserves_original_AB_bytes")))Finish(M,TEXT("pass_history_legacy"));}break;
 case 60:{auto R=Rows(M);const FRecord Current=R[0];auto Root=JP(Current.Payload);const int32 Next=NextSerial(M,E);Root->SetNumberField(TEXT("serial"),Next);Expected=JS(Root);LatestPayload=Current.Payload;OldSerial=Current.Serial;
  if(!Check(M,ArmDiagnosticWriteFailure(TEXT("record"))&&!Save(M,Expected,E)&&Rows(M)[0].Payload==LatestPayload,TEXT("declared_record_write_failure_keeps_committed_snapshot")))return;
  if(!Check(M,ArmDiagnosticWriteFailure(TEXT("index"))&&!Save(M,Expected,E)&&Rows(M)[0].Payload==LatestPayload,TEXT("declared_index_write_failure_does_not_publish_orphan_record")))return;
  auto Bad=JP(Expected);auto Eq=Bad->GetObjectField(TEXT("equipment"));Eq->SetNumberField(TEXT("frag"),Eq->GetNumberField(TEXT("frag"))+1);if(!Check(M,!Save(M,JS(Bad),E),TEXT("archive_reuses_strict_resource_validation")))return;
  if(!Check(M,Save(M,Expected,E)&&Rows(M)[0].Serial==Next,TEXT("valid_transaction_after_failed_writes_commits_once")))return;
  const FString Primary=Rows(M)[0].Slot;Corrupt(Primary);auto Recovered=Rows(M);if(!Check(M,Recovered.Num()==1&&Recovered[0].Recovered&&Recovered[0].Serial==OldSerial,TEXT("declared_primary_corruption_recovers_same_point_older_committed_copy")))return;
  Corrupt(M->SlotPrefix+TEXT("_HI_A"));if(!Check(M,Rows(M).Num()==1,TEXT("declared_one_index_corruption_recovers_mirrored_directory")))return;
  const auto Back=Rows(M)[0];auto Env=JP(SavedText(Back.Slot));auto Snapshot=JP(Back.Payload);Snapshot->SetNumberField(TEXT("serial"),Next+100);Env->SetNumberField(TEXT("serial"),Next+100);Env->SetStringField(TEXT("snapshot"),JS(Snapshot));RawWrite(Back.Slot,JS(Env));if(!Check(M,Rows(M).Num()==0,TEXT("valid_but_uncommitted_higher_sequence_is_not_a_recovery_candidate")))return;
  Corrupt(M->SlotPrefix+TEXT("_HI_B"));if(!Check(M,NextSerial(M,E)==0&&!Save(M,Expected,E),TEXT("both_invalid_directories_reject_save_without_resetting_history")))return;
  Check(M,true,TEXT("all_faults_are_declared_and_limited_to_independent_diagnostic_UserDir"));Finish(M,TEXT("pass_storage_faults"));break;}
 }
}
} // namespace
