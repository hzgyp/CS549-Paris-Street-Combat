// Independent native-input human-flow regression. No normal launch activates this driver.
#include "ParisTutorial.h"
#include "ParisBridgeMission.h"
#include "ParisCheckpointHistory.h"
#include "ParisEquipmentState.h"
#include "ParisPlayerDeath.h"
#include "ParisCombatUI.h"
#include "Components/CapsuleComponent.h"
#include "Components/LineBatchComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"
#include "UnrealClient.h"

TArray<FVector> ParisCheckpointRingGeometry(const AParisBridgeMission* M);
namespace ParisTutorial {namespace {
FString FlowMode,FlowOut,WaitGeneration,Expected;bool FlowInit=false,FlowDone=false,HeldForward=false,HeldSprint=false;FString BeforeArchive;int StepNow=0;double Began=0,At=0,NextTrace=0;
TArray<TSharedPtr<FJsonValue>> Assertions;TSharedPtr<FJsonObject> RingReport;
TSharedPtr<FJsonObject> ParseFlow(const FString& S){TSharedPtr<FJsonObject> O;auto R=TJsonReaderFactory<>::Create(S);return FJsonSerializer::Deserialize(R,O)?O:nullptr;}
FString JsonFlow(const TSharedPtr<FJsonObject>& O){FString S;auto W=TJsonWriterFactory<TCHAR,TCondensedJsonPrintPolicy<TCHAR>>::Create(&S);FJsonSerializer::Serialize(O.ToSharedRef(),W);return S;}
double N(const UObject* O,const TCHAR* K){auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!P)return -1;const auto* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):P->GetSignedIntPropertyValue(V);}
bool DeadFlow(const ACharacter* P){return !P||N(P,TEXT("Health"))<=0;}
void KeyFlow(APlayerController* PC,FKey K,bool Down){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1:0));}
void TapFlow(APlayerController* PC,FKey K){KeyFlow(PC,K,true);KeyFlow(PC,K,false);}
void StopFlow(APlayerController* PC){if(HeldForward)KeyFlow(PC,EKeys::W,false);if(HeldSprint)KeyFlow(PC,EKeys::LeftShift,false);HeldForward=HeldSprint=false;}
void StageFlow(int S){StepNow=S;At=FPlatformTime::Seconds();}
void ShotFlow(const TCHAR* Name){FScreenshotRequest::RequestScreenshot(FlowOut/FString(Name)+TEXT(".png"),false,false);}
void FinishFlow(AParisBridgeMission* M,const FString& Status){if(FlowDone)return;FlowDone=true;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Status);O->SetStringField(TEXT("mode"),FlowMode);O->SetArrayField(TEXT("checks"),Assertions);O->SetStringField(TEXT("state"),M->ReadMissionState());O->SetNumberField(TEXT("wall_seconds"),FPlatformTime::Seconds()-Began);if(RingReport)O->SetObjectField(TEXT("ring"),RingReport);O->SetStringField(TEXT("scope"),TEXT("Native path movement, original actual mine/contact/blast/death, original death-menu Load, actual E saves. Original guard damage endpoints are declared clear fixtures; no pawn relocation, mine-state assignment, resource grants or AI isolation. Not human natural-combat/all-map acceptance."));FFileHelper::SaveStringToFile(JsonFlow(O),*(FlowOut/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);FPlatformMisc::RequestExit(false);}
bool ExpectFlow(AParisBridgeMission* M,bool Good,const TCHAR* Label){auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("name"),Label);A->SetBoolField(TEXT("pass"),Good);Assertions.Add(MakeShared<FJsonValueObject>(A));if(!Good)FinishFlow(M,TEXT("failed_")+FString(Label));return Good;}
TArray<ParisCheckpointHistory::FRecord> RecordsFlow(AParisBridgeMission* M){FString Error;return ParisCheckpointHistory::List(M,Error);}
FString ArchiveFlow(AParisBridgeMission* M){FString Signature;for(const auto& R:RecordsFlow(M))Signature+=R.Id+FString::FromInt(R.Serial)+R.Payload;return Signature;}
TSharedPtr<FJsonObject> LiveFlow(AParisBridgeMission* M){return ParseFlow(M->ReadMissionState())->GetObjectField(TEXT("snapshot"));}
bool RestoreExact(AParisBridgeMission* M){auto A=ParseFlow(Expected),B=LiveFlow(M);if(!A||!B)return false;if(JsonFlow(A->GetObjectField(TEXT("equipment")))!=JsonFlow(B->GetObjectField(TEXT("equipment")))||JsonFlow(A->GetObjectField(TEXT("tutorial")))!=JsonFlow(B->GetObjectField(TEXT("tutorial"))))return false;for(int I=0;I<6;++I){auto X=A->GetArrayField(TEXT("actors"))[I]->AsObject(),Y=B->GetArrayField(TEXT("actors"))[I]->AsObject();for(const TCHAR* K:{TEXT("health"),TEXT("loaded"),TEXT("reserve"),TEXT("shots")})if(X->GetNumberField(K)!=Y->GetNumberField(K))return false;if(X->GetBoolField(TEXT("dead"))!=Y->GetBoolField(TEXT("dead")))return false;}return true;}
ACharacter* FlowActor(AParisBridgeMission* M,int Index){const TCHAR* IDs[]={TEXT("G1_Player"),TEXT("G1_Ally1"),TEXT("G1_Ally2"),TEXT("G1_German1"),TEXT("G1_German2"),TEXT("G1_German3")};for(TActorIterator<ACharacter>I(M->GetWorld());I;++I)if(I->ActorHasTag(FName(IDs[Index])))return *I;return nullptr;}
void ClearGuard(AParisBridgeMission* M,int Index){auto* C=FlowActor(M,Index);auto* F=C->FindFunction(TEXT("PC_ApplyDamage"));FStructOnScope A(F);auto* V=CastField<FNumericProperty>(F->FindPropertyByName(TEXT("Amount")));V->SetFloatingPointPropertyValue(V->ContainerPtrToValuePtr<void>(A.GetStructMemory()),1000);C->ProcessEvent(F,A.GetStructMemory());}
bool GoFlow(AParisBridgePlayerController* PC,ACharacter* P,FVector Target,bool Sprint=true){const auto Feet=P->GetNavAgentLocation();if(FVector::Dist2D(Feet,Target)<40){StopFlow(PC);return true;}auto* Path=UNavigationSystemV1::FindPathToLocationSynchronously(PC->GetWorld(),Feet,Target,P);if(!Path||!Path->IsValid()||Path->IsPartial()){FinishFlow(AParisBridgeMission::Find(PC),TEXT("failed_native_path"));return false;}FVector Next=Target;for(auto V:Path->PathPoints)if(FVector::Dist2D(Feet,V)>60){Next=V;break;}PC->SetControlRotation(FRotator(0,(Next-Feet).Rotation().Yaw,0));if(!HeldForward){KeyFlow(PC,EKeys::W,true);HeldForward=true;}if(HeldSprint!=Sprint){KeyFlow(PC,EKeys::LeftShift,Sprint);HeldSprint=Sprint;}return false;}
bool LiveCombat(AParisBridgeMission* M){auto& E=ParisTacticalEquipment::Session(M->GetWorld());bool Good=CombatStarted(M)&&M->LivingDefenders==3&&!M->CheckpointUnlocked();for(int I=3;I<6;++I){auto* C=FlowActor(M,I);Good&=!DeadFlow(C)&&C&&!C->IsHidden()&&C->GetActorEnableCollision();}for(int I=0;I<2;++I)Good&=E.Traps[I].State==TEXT("Armed")&&E.Traps[I].Visual.IsValid()&&!E.Traps[I].Visual->IsHidden();return Good&&E.Traps[2].State==TEXT("Disarmed");}
int GreenRoutes(UWorld* W){int Num=0;for(auto Type:{UWorld::ELineBatcherType::World,UWorld::ELineBatcherType::WorldPersistent})if(auto* B=W->GetLineBatcher(Type))for(const auto& L:B->BatchedLines)if(FMath::IsNearlyEqual(L.Thickness,1.8f,.01f)&&L.Color.Equals(FLinearColor(FColor(175,205,151)),.001f))++Num;return Num;}
bool RingGround(AParisBridgeMission* M){auto P=ParisCheckpointRingGeometry(M);int Supported=0;double Low=DBL_MAX,High=-DBL_MAX,MinGap=DBL_MAX,MaxGap=-DBL_MAX;FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisFlowRingWitness),false);const FCollisionObjectQueryParams Static(FCollisionObjectQueryParams::InitType::AllStaticObjects);for(auto V:P){FHitResult Hit;Low=FMath::Min(Low,V.Z);High=FMath::Max(High,V.Z);if(M->GetWorld()->LineTraceSingleByObjectType(Hit,V+FVector(0,0,40),V-FVector(0,0,40),Static,Q)&&Hit.ImpactNormal.Z>=.6){++Supported;MinGap=FMath::Min(MinGap,V.Z-Hit.ImpactPoint.Z);MaxGap=FMath::Max(MaxGap,V.Z-Hit.ImpactPoint.Z);}}RingReport=MakeShared<FJsonObject>();RingReport->SetNumberField(TEXT("samples"),P.Num());RingReport->SetNumberField(TEXT("supported"),Supported);RingReport->SetNumberField(TEXT("minimum_z"),Low);RingReport->SetNumberField(TEXT("maximum_z"),High);RingReport->SetNumberField(TEXT("minimum_ground_gap_cm"),MinGap);RingReport->SetNumberField(TEXT("maximum_ground_gap_cm"),MaxGap);RingReport->SetNumberField(TEXT("previous_flat_circle_z"),M->BridgeheadFeet.Z+7);return P.Num()==96&&Supported==96&&MinGap>=7.9&&MaxGap<=8.1;}
} // private diagnostic helpers
void FlowDiagnostics(AParisBridgePlayerController* PC){
 if(!FlowInit){FlowInit=true;if(!FParse::Value(FCommandLine::Get(),TEXT("ParisFlowCheck="),FlowMode))return;FParse::Value(FCommandLine::Get(),TEXT("ParisFlowOut="),FlowOut);IFileManager::Get().MakeDirectory(*FlowOut,true);Began=FPlatformTime::Seconds();StageFlow(0);}
 if(FlowMode.IsEmpty()||FlowDone)return;auto* M=AParisBridgeMission::Find(PC);auto* P=Cast<ACharacter>(PC->GetPawn());if(!M||!P)return;const double Now=FPlatformTime::Seconds();if(Now-Began>210){FinishFlow(M,TEXT("failed_deadline"));return;}if(M->Phase==TEXT("Error")){FinishFlow(M,TEXT("failed_preparation_")+M->Feedback);return;}if(M->Phase==TEXT("Preparing"))return;
 if(Now>NextTrace){NextTrace=Now+.25;auto T=MakeShared<FJsonObject>();T->SetNumberField(TEXT("time"),Now-Began);T->SetNumberField(TEXT("step"),StepNow);T->SetStringField(TEXT("phase"),M->Phase);T->SetNumberField(TEXT("tutorial"),Step(M));T->SetNumberField(TEXT("living_guards"),M->LivingDefenders);T->SetBoolField(TEXT("checkpoint_unlocked"),M->CheckpointUnlocked());T->SetStringField(TEXT("dialog"),M->CheckpointDialogState());T->SetNumberField(TEXT("player_health"),N(P,TEXT("Health")));T->SetStringField(TEXT("feet"),P->GetNavAgentLocation().ToString());auto& E=ParisTacticalEquipment::Session(M->GetWorld());T->SetStringField(TEXT("trap2"),E.Traps[1].State);T->SetNumberField(TEXT("route_lines"),GreenRoutes(M->GetWorld()));FFileHelper::SaveStringToFile(JsonFlow(T)+TEXT("\n"),*(FlowOut/TEXT("trace.jsonl")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);}
 if(Now-At<.2)return;FString Error;
 switch(StepNow){
 case 0:{BeforeArchive=ArchiveFlow(M);auto Rows=RecordsFlow(M);const FString Id=FlowMode==TEXT("flow_cp1_restore")?TEXT("CP1"):TEXT("CP0");auto* R=Rows.FindByPredicate([&](const auto& X){return X.Id==Id;});if(!ExpectFlow(M,R!=nullptr,TEXT("requested_seed_point_valid")))return;Expected=R->Payload;if(!ExpectFlow(M,ParisCheckpointHistory::PrepareLoad(M,Id,R->Serial,Error),TEXT("select_seed_point_without_mutating_old_files")))return;WaitGeneration=M->RunGeneration;M->LoadCheckpoint();StageFlow(1);break;}
 case 1:if(M->RunGeneration==WaitGeneration||M->VerifiedRestoreState.IsEmpty())return;if(!ExpectFlow(M,RestoreExact(M),TEXT("live_restored_full_equipment_recruitment_and_six_actor_resources_match_snapshot")))return;
     if(FlowMode==TEXT("flow_copy_cp0")){
   if(!ExpectFlow(M,TrainingCheckpointSaved(M)&&M->LivingDefenders==3&&!CombatStarted(M)&&Goal(M).Equals(M->FarBankFeet,.01),TEXT("actual_earned_CP0_uses_training_state_and_bridge_C_goal")))return;
   M->DismissCheckpointPrompt();TapFlow(PC,EKeys::Escape);ShotFlow(TEXT("cp0_training_briefing"));StageFlow(50);return;
  }
  if(FlowMode==TEXT("flow_cp1_restore")){bool AllDead=M->Phase==TEXT("Won")&&M->LivingDefenders==0;for(int I=3;I<6;++I)AllDead&=DeadFlow(FlowActor(M,I));if(!ExpectFlow(M,AllDead&&RingGround(M),TEXT("fresh_CP1_keeps_saved_dead_guards_and_complete_trap_state_with_supported_ring")))return;ParisCombatUI::ShowCheckpointList(PC);ShotFlow(TEXT("cp1_fresh_archive"));StageFlow(40);return;}
  if(!ExpectFlow(M,M->Phase==TEXT("TrainingCheckpoint")&&M->LivingDefenders==3&&!CombatStarted(M)&&CheckpointFeet(M).Equals(FVector(1200,-21400,100.802),.01),TEXT("restored_CP0_is_current_marker_and_all_guards_live_before_combat")))return;
  if(!ExpectFlow(M,GreenRoutes(M->GetWorld())==0,TEXT("no_recruitment_or_checkpoint_green_route_after_movement_lessons")))return;M->DismissCheckpointPrompt();PC->SetControlRotation(FRotator(-25,0,0));ShotFlow(TEXT("cp0_correct_marker_restored"));StageFlow(2);break;
 case 2:if(CombatStarted(M)){StopFlow(PC);StageFlow(3);break;}GoFlow(PC,P,FVector(1600,-21350,100),false);break;
 case 3:if(!ExpectFlow(M,LiveCombat(M),TEXT("actual_forward_departure_activates_three_visible_collidable_guards_and_two_armed_visible_mines")))return;if(!ExpectFlow(M,ParisCheckpointRingGeometry(M).IsEmpty()&&GreenRoutes(M->GetWorld())==0,TEXT("before_kills_no_CP1_ring_or_green_navigation_route")))return;ShotFlow(TEXT("combat_reactivated"));if(FlowMode==TEXT("flow_restore_only")){StageFlow(40);return;}ClearGuard(M,3);ClearGuard(M,4);ExpectFlow(M,true,TEXT("declared_original_guard_damage_endpoints_for_first_two_guards"));StageFlow(4);break;
 case 4:if(M->LivingDefenders!=1)return;if(!ExpectFlow(M,!M->CheckpointUnlocked()&&ParisCheckpointRingGeometry(M).IsEmpty()&&!M->InteractCheckpoint()&&ArchiveFlow(M)==BeforeArchive,TEXT("two_of_three_guards_cannot_show_CP1_ring_or_create_save")))return;ShotFlow(TEXT("two_guards_no_checkpoint"));StageFlow(45);break;
 case 45:ClearGuard(M,5);StageFlow(5);break;
 case 5:if(M->Phase!=TEXT("Won")||Step(M)!=17)return;if(!ExpectFlow(M,M->CheckpointUnlocked()&&RingGround(M),TEXT("three_guard_clearance_unlocks_CP1_ring_supported_eight_cm_above_real_ground")))return;StageFlow(6);break;
 case 6:if(DeadFlow(P)){StopFlow(PC);if(!ExpectFlow(M,ParisTacticalEquipment::Session(M->GetWorld()).Traps[1].State==TEXT("Spent")&&ArchiveFlow(M)==BeforeArchive,TEXT("actual_Trap2_contact_blast_kills_player_after_clear_without_CP1_autosave")))return;ShotFlow(TEXT("actual_mine_death"));StageFlow(7);break;}GoFlow(PC,P,ParisTacticalEquipment::Session(M->GetWorld()).Traps[1].Position,true);break;
 case 7:if(M->Phase!=TEXT("Lost")||ParisPlayerDeath::Presenting(PC)||!PC->InteractionMenuVisible())return;for(int I=0;I<3&&PC->InteractionMenuSelection()!=1;++I)TapFlow(PC,EKeys::Down);if(!ExpectFlow(M,PC->InteractionMenuSelection()==1&&PC->MenuActionEnabled(1),TEXT("original_death_menu_load_action_selected")))return;WaitGeneration=M->RunGeneration;TapFlow(PC,EKeys::Enter);StageFlow(8);break;
 case 8:if(M->RunGeneration==WaitGeneration||M->VerifiedRestoreState.IsEmpty())return;if(!ExpectFlow(M,RestoreExact(M)&&M->LivingDefenders==3&&ParisCheckpointHistory::Active(M)==TEXT("CP0")&&ArchiveFlow(M)==BeforeArchive,TEXT("mine_death_menu_load_rewinds_complete_CP0_state_with_three_living_guards")))return;if(!ExpectFlow(M,ParisTacticalEquipment::Session(M->GetWorld()).Traps[1].State==TEXT("Dormant")&&ParisTacticalEquipment::Session(M->GetWorld()).Traps[2].State==TEXT("Disarmed"),TEXT("blast_spent_combat_mine_rewinds_while_previously_disarmed_teaching_mine_stays_disarmed")))return;M->DismissCheckpointPrompt();ShotFlow(TEXT("actual_death_menu_CP0_restored"));StageFlow(9);break;
 case 9:if(CombatStarted(M)){StopFlow(PC);StageFlow(10);break;}GoFlow(PC,P,FVector(1600,-21350,100),false);break;
 case 10:if(!ExpectFlow(M,LiveCombat(M)&&GreenRoutes(M->GetWorld())==0,TEXT("after_actual_mine_death_retry_forward_motion_refreshes_live_models_collision_and_rearmed_combat_mines")))return;ShotFlow(TEXT("retry_guards_and_mines_live"));for(int I=3;I<6;++I)ClearGuard(M,I);StageFlow(11);break;
 case 11:if(M->Phase!=TEXT("Won")||Step(M)!=17)return;if(GoFlow(PC,P,M->BridgeheadFeet,false)){PC->SetControlRotation(FRotator(-55,0,0));StageFlow(12);}break;
 case 12:if(!ExpectFlow(M,M->InsideCheckpoint()&&M->CheckpointSaveBlockReason().IsEmpty()&&RingGround(M)&&GreenRoutes(M->GetWorld())==0,TEXT("actual_grounded_CP1_arrival_has_visible_supported_ring_and_original_save_admission")))return;ShotFlow(TEXT("cp1_ground_ring_before_E"));StageFlow(13);break;
 case 13:TapFlow(PC,EKeys::E);StageFlow(14);break;
 case 14:if(M->CheckpointDialogState()!=TEXT("Succeeded"))return;{auto R=RecordsFlow(M);if(!ExpectFlow(M,R.Num()==2&&R[0].Id==TEXT("CP1")&&R[0].Latest,TEXT("native_E_creates_durable_CP1_only_after_all_guards_die")))return;Expected=R[0].Payload;ShotFlow(TEXT("cp1_native_E_saved"));StageFlow(15);break;}
 case 15:TapFlow(PC,EKeys::Escape);WaitGeneration=M->RunGeneration;TapFlow(PC,EKeys::F9);if(!ExpectFlow(M,ParisCombatUI::Confirmation(PC)==TEXT("Load"),TEXT("CP1_retry_default_cancel_confirmation_retained")))return;TapFlow(PC,EKeys::Left);TapFlow(PC,EKeys::Enter);StageFlow(16);break;
 case 16:if(M->RunGeneration==WaitGeneration||M->VerifiedRestoreState.IsEmpty())return;if(!ExpectFlow(M,RestoreExact(M)&&M->Phase==TEXT("Won")&&M->LivingDefenders==0&&RingGround(M),TEXT("actual_CP1_load_preserves_guard_deaths_all_saved_resources_and_mine_states")))return;ParisCombatUI::ShowCheckpointList(PC);ShotFlow(TEXT("cp0_cp1_final_records"));StageFlow(40);break;
   case 50:if(FScreenshotRequest::IsScreenshotRequested())return;TapFlow(PC,EKeys::Right);TapFlow(PC,EKeys::Right);TapFlow(PC,EKeys::Five);if(!ExpectFlow(M,ParisCombatUI::Inspect(PC)->GetNumberField(TEXT("page"))==2&&ParisCombatUI::Inspect(PC)->GetNumberField(TEXT("help"))==4,TEXT("actual_checkpoint_help_page")))return;ShotFlow(TEXT("cp0_checkpoint_help"));StageFlow(51);break;
 case 51:if(FScreenshotRequest::IsScreenshotRequested())return;TapFlow(PC,EKeys::Three);ShotFlow(TEXT("grenade_help"));StageFlow(52);break;
 case 52:if(FScreenshotRequest::IsScreenshotRequested())return;TapFlow(PC,EKeys::Left);ShotFlow(TEXT("grenade_equipment"));StageFlow(53);break;
 case 53:if(FScreenshotRequest::IsScreenshotRequested())return;if(!ExpectFlow(M,RestoreExact(M)&&ArchiveFlow(M)==BeforeArchive,TEXT("menu_copy_review_changes_no_snapshot_or_archive_values")))return;FinishFlow(M,TEXT("pass_copy_CP0_briefing_help_equipment"));break;
 case 40:FinishFlow(M,TEXT("pass_")+FlowMode);break;
 }
}
} // namespace ParisTutorial
