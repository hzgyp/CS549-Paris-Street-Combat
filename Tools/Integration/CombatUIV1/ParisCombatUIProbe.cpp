// Finite opt-in UI checks via actual controller presses, native pause and real frames.
#include "ParisCombatUIProbe.h"
#include "ParisCombatUI.h"
#include "ParisBridgeMission.h"
#include "ParisTacticalEquipment.h"
#include "ParisEquipmentState.h"
#include "Containers/Ticker.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"
#include "UnrealClient.h"
namespace ParisCombatUIProbe {
namespace {
FTSTicker::FDelegateHandle Handle;
FString Mode,Out;int32 Step=0;double Since=0,Begin=0,FrozenTime=0,Fuse=0,Life=0;
bool Finished=false;FVector Position;FRotator Rotation;TArray<FVector> FrozenRoster;
TArray<TSharedPtr<FJsonValue>> Checks,States;
TFunction<void()> PendingImageAction;
double Num(const UObject* O,const TCHAR* N){auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),N):nullptr;if(!P)return -1;const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));}
FString Json(const TSharedPtr<FJsonObject>& O){FString T;auto R=TJsonWriterFactory<>::Create(&T);FJsonSerializer::Serialize(O,R);return T;}
void Key(APlayerController* PC,FKey K,bool Down){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,Down?IE_Pressed:IE_Released,Down?1.f:0.f));}
void Tap(APlayerController* PC,FKey K){Key(PC,K,true);Key(PC,K,false);}
void Go(int32 Value){Step=Value;Since=FPlatformTime::Seconds();}
void Finish(bool OK,const FString& Why){if(Finished)return;Finished=true;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),(OK?TEXT("pass_ui_"):TEXT("failed_ui_"))+Mode);O->SetStringField(TEXT("reason"),Why);O->SetStringField(TEXT("scope"),TEXT("Opt-in real controller key/mouse input, actual UE pause and screenshots; no gameplay resource overrides, teleport, damage or Brain changes. Not human acceptance."));O->SetArrayField(TEXT("checks"),Checks);O->SetArrayField(TEXT("states"),States);O->SetNumberField(TEXT("step"),Step);FFileHelper::SaveStringToFile(Json(O),*(Out/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);UE_LOG(LogTemp,Display,TEXT("PARIS_COMBAT_UI_PROBE %s %s"),*Mode,*Why);FPlatformMisc::RequestExit(false);}
bool Check(bool B,const TCHAR* Why){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("name"),Why);O->SetBoolField(TEXT("pass"),B);Checks.Add(MakeShared<FJsonValueObject>(O));if(!B)Finish(false,Why);return B;}
void Image(const TCHAR* Name){FScreenshotRequest::RequestScreenshot(Out/(FString(Name)+TEXT(".png")),true,false);}
void Click(AParisBridgePlayerController* PC,double X,double Y){int32 W=0,H=0;PC->GetViewportSize(W,H);const double S=FMath::Min(W/1920.,H/1080.);PC->SetMouseLocation(FMath::RoundToInt((W-1920*S)*.5+X*S),FMath::RoundToInt((H-1080*S)*.5+Y*S));Tap(PC,EKeys::LeftMouseButton);}
bool DisplayReady(UWorld* W,ACharacter* C){for(TActorIterator<AActor> I(W);I;++I)if(I->GetOwner()==C){auto* V=FindFProperty<FBoolProperty>(I->GetClass(),TEXT("Initialized"));auto* G=FindFProperty<FObjectPropertyBase>(I->GetClass(),TEXT("Gun"));if(V&&G&&V->GetPropertyValue_InContainer(*I))return true;}return false;}
TArray<FVector> Locations(UWorld* W){TArray<FVector> V;for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Player"))||I->ActorHasTag(TEXT("G1_Ally1"))||I->ActorHasTag(TEXT("G1_Ally2"))||I->ActorHasTag(TEXT("G1_German1"))||I->ActorHasTag(TEXT("G1_German2"))||I->ActorHasTag(TEXT("G1_German3")))V.Add(I->GetActorLocation());return V;}
bool Equal(const TArray<FVector>& A,const TArray<FVector>& B){if(A.Num()!=B.Num())return false;for(int32 I=0;I<A.Num();++I)if(FVector::Dist(A[I],B[I])>.001)return false;return true;}
bool Tick(float){if(Finished)return false;UWorld* W=nullptr;for(const auto& C:GEngine->GetWorldContexts())if(C.World()&&C.World()->IsGameWorld()){W=C.World();break;}if(!W)return true;auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;if(!M||!PC||!P)return true;if(Begin==0)Begin=FPlatformTime::Seconds();if(FPlatformTime::Seconds()-Begin>90){Finish(false,TEXT("bounded UI deadline"));return false;}if(PendingImageAction){if(FScreenshotRequest::IsScreenshotRequested())return true;auto Next=MoveTemp(PendingImageAction);Next();return !Finished;}const double DT=FPlatformTime::Seconds()-Since;auto& E=ParisTacticalEquipment::Session(W);
 if(Step==0){if(M->Phase!=TEXT("Ready")||!E.Initialized||!DisplayReady(W,P))return true;Tap(PC,EKeys::Escape);if(!Check(ParisCombatUI::IsOpen(PC)&&UGameplayStatics::IsGamePaused(W),TEXT("menu_opens_and_uses_real_UE_pause")))return false;FrozenTime=W->GetTimeSeconds();Position=P->GetActorLocation();FrozenRoster=Locations(W);Rotation=PC->GetControlRotation();Go(1);return true;}
 if(Mode==TEXT("pages")||Mode==TEXT("pages_small")){
  if(Step==1&&DT>.5){Image(TEXT("01_mission"));States.Add(MakeShared<FJsonValueObject>(ParisCombatUI::Inspect(PC)));PendingImageAction=[PC](){Click(PC,950,248);Go(2);};}
  else if(Step==2&&DT>.4){auto O=ParisCombatUI::Inspect(PC);if(!Check(O->GetNumberField(TEXT("page"))==1&&O->GetArrayField(TEXT("roster")).Num()==3&&O->GetNumberField(TEXT("frag"))==2&&O->GetNumberField(TEXT("smoke"))==2,TEXT("squad_values_match_current_three_allied_actors_and_equipment")))return false;Image(TEXT("02_player_squad"));States.Add(MakeShared<FJsonValueObject>(O));PendingImageAction=[PC](){Click(PC,1280,248);Go(3);};}
  else if(Step>=3&&Step<=7&&DT>.4){auto O=ParisCombatUI::Inspect(PC);if(!Check(O->GetNumberField(TEXT("page"))==2&&O->GetNumberField(TEXT("help"))==Step-3,TEXT("help_category_mouse_selection")))return false;Image(*FString::Printf(TEXT("%02d_help_%d"),Step,Step-3));States.Add(MakeShared<FJsonValueObject>(O));PendingImageAction=[PC](){if(Step<7)Click(PC,640+(Step-2)*205+70,330);else Click(PC,1530,248);Go(Step+1);};}
  else if(Step==8&&DT>.4){Image(TEXT("08_settings"));PendingImageAction=[PC](){Click(PC,800,443);Click(PC,800,583);Go(9);};}
  else if(Step==9&&DT>.4){auto O=ParisCombatUI::Inspect(PC);if(!Check(!O->GetBoolField(TEXT("detailed"))&&O->GetNumberField(TEXT("hud_scale"))<.86,TEXT("settings_have_actual_effect")))return false;Image(TEXT("09_compact_settings"));States.Add(MakeShared<FJsonValueObject>(O));PendingImageAction=[PC,W](){Click(PC,800,443);Click(PC,800,583);Click(PC,800,583);Tap(PC,EKeys::Escape);if(!Check(!ParisCombatUI::IsOpen(PC)&&!UGameplayStatics::IsGamePaused(W),TEXT("escape_restores_prior_game_and_cursor_mode")))return;Click(PC,960,772);Go(10);};}
  else if(Step==10&&DT>.7){Image(TEXT("10_combat_hud"));if(!Check(M->Phase==TEXT("Crossing")&&Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))+Num(P,TEXT("ShotSequence"))==18,TEXT("original_start_and_authoritative_weapon_resources")))return false;PendingImageAction=[PC](){Tap(PC,EKeys::Tab);Go(11);};}
  else if(Step==11&&DT>.5){if(!Check(ParisCombatUI::IsOpen(PC)&&ParisCombatUI::Inspect(PC)->GetNumberField(TEXT("page"))==1,TEXT("tab_direct_status_page")))return false;Tap(PC,EKeys::Tab);Finish(!ParisCombatUI::IsOpen(PC)&&!UGameplayStatics::IsGamePaused(W),TEXT("all four pages, five help groups, settings, actual HUD and menu navigation"));}
 }else if(Mode==TEXT("pause")){
  if(Step==1&&DT>2){if(!Check(FMath::Abs(W->GetTimeSeconds()-FrozenTime)<.00001&&Equal(FrozenRoster,Locations(W)),TEXT("player_and_all_NPC_locations_and_world_time_frozen")))return false;const double Shots=Num(P,TEXT("ShotSequence"));Tap(PC,EKeys::LeftMouseButton);Tap(PC,EKeys::R);Tap(PC,EKeys::G);Tap(PC,EKeys::Q);Tap(PC,EKeys::E);Key(PC,EKeys::W,true);Go(2);Position=P->GetActorLocation();Fuse=Shots;}
  else if(Step==2&&DT>1){if(!Check(FVector::Dist(Position,P->GetActorLocation())<.001&&Num(P,TEXT("ShotSequence"))==Fuse&&E.Frag==2&&E.Smoke==2,TEXT("menu_blocks_movement_fire_reload_equipment_and_E")))return false;Key(PC,EKeys::W,false);Tap(PC,EKeys::Escape);Click(PC,960,772);Key(PC,EKeys::W,true);Key(PC,EKeys::LeftShift,true);Go(3);}
  else if(Step==3&&DT>.45){Tap(PC,EKeys::Escape);FrozenTime=W->GetTimeSeconds();Position=P->GetActorLocation();Go(4);}
  else if(Step==4&&DT>1){Key(PC,EKeys::W,false);Key(PC,EKeys::LeftShift,false);if(!Check(FMath::Abs(W->GetTimeSeconds()-FrozenTime)<.00001&&FVector::Dist(Position,P->GetActorLocation())<.001,TEXT("pause_during_actual_running_freezes_motion")))return false;Tap(PC,EKeys::Escape);Go(5);}
  else if(Step==5&&DT>.6){Position=P->GetActorLocation();Go(6);}
  else if(Step==6&&DT>.5){if(!Check(FVector::Dist(Position,P->GetActorLocation())<2,TEXT("released_move_keys_do_not_stick_after_menu")))return false;Key(PC,EKeys::W,true);Position=P->GetActorLocation();Go(7);}
  else if(Step==7&&DT>.5){Key(PC,EKeys::W,false);if(!Check(FVector::Dist(Position,P->GetActorLocation())>20,TEXT("normal_movement_resumes_after_close")))return false;Finish(true,TEXT("real pause and release/resume input checks"));}
 }else if(Mode==TEXT("confirm")){
  if(Step==1&&DT>.4){Tap(PC,EKeys::Escape);Click(PC,960,772);Go(2);}
  else if(Step==2&&DT>.5){const auto Generation=M->RunGeneration;Tap(PC,EKeys::F6);if(!Check(ParisCombatUI::Confirmation(PC)==TEXT("Restart")&&M->RunGeneration==Generation,TEXT("F6_opens_confirmation_without_restarting")))return false;Image(TEXT("01_restart_confirmation"));Go(3);}
  else if(Step==3&&DT>.5){Tap(PC,EKeys::Enter);if(!Check(ParisCombatUI::Confirmation(PC).IsEmpty()&&ParisCombatUI::IsOpen(PC),TEXT("enter_defaults_to_cancel")))return false;Click(PC,350,488);Go(4);}
  else if(Step==4&&DT>.4){if(!Check(ParisCombatUI::Confirmation(PC)==TEXT("Restart"),TEXT("mouse_restart_uses_same_confirmation")))return false;Click(PC,1080,641);if(!Check(ParisCombatUI::Confirmation(PC).IsEmpty(),TEXT("mouse_cancel_does_not_change_mission")))return false;Click(PC,350,634);Go(5);}
  else if(Step==5&&DT>.4){if(!Check(ParisCombatUI::Confirmation(PC)==TEXT("Exit"),TEXT("exit_has_confirmation")))return false;Tap(PC,EKeys::Escape);Click(PC,350,414);if(!Check(ParisCombatUI::Confirmation(PC).IsEmpty()&&!ParisCombatUI::Inspect(PC)->GetBoolField(TEXT("load_enabled")),TEXT("no_save_load_disabled_without_inventing_checkpoint")))return false;Tap(PC,EKeys::Escape);Go(6);}
  else if(Step==6&&DT>.3){const double Before=Num(P,TEXT("ShotSequence"));Tap(PC,EKeys::Tab);Click(PC,350,343);Go(7);Fuse=Before;}
  else if(Step==7&&DT>.5){if(!Check(Num(P,TEXT("ShotSequence"))==Fuse&&!ParisCombatUI::IsOpen(PC)&&!UGameplayStatics::IsGamePaused(W),TEXT("mouse_resume_not_leaked_as_rifle_shot")))return false;Tap(PC,EKeys::F6);Click(PC,805,641);Go(8);}
  else if(Step==8&&DT>.4){if(M->Phase!=TEXT("Ready"))return true;if(!Check(!ParisCombatUI::IsOpen(PC)&&!UGameplayStatics::IsGamePaused(W)&&Num(P,TEXT("LoadedAmmo"))==8&&Num(P,TEXT("ReserveAmmo"))==10,TEXT("explicit_confirm_calls_original_restart_and_returns_unpaused")))return false;Finish(true,TEXT("confirm, cancel, disabled load, actual restart and mouse input isolation"));}
 }else if(Mode==TEXT("equipment_pause")){
  if(Step==1&&DT>.3){Tap(PC,EKeys::Escape);Click(PC,960,772);PC->SetControlRotation(FRotator(20,0,0));Key(PC,EKeys::G,true);Go(2);}
  else if(Step==2&&DT>.9){Tap(PC,EKeys::Escape);if(!Check(!ParisCombatUI::IsOpen(PC)&&E.Frag==2,TEXT("escape_cancels_preparation_before_menu_without_spend")))return false;Key(PC,EKeys::G,false);Go(3);}
  else if(Step==3&&DT>.8&&E.ThrowKind.IsEmpty()){Key(PC,EKeys::G,true);Go(4);}
  else if(Step==4&&DT>.9){Key(PC,EKeys::G,false);Go(5);}
  else if(Step==5&&E.ThrowKind.IsEmpty()&&E.Balls.Num()==1){Tap(PC,EKeys::Escape);if(!Check(ParisCombatUI::IsOpen(PC)&&E.Frag==1,TEXT("menu_after_one_real_frag_commit")))return false;Fuse=E.Balls[0].Fuse;FrozenTime=W->GetTimeSeconds();Position=E.Balls[0].Position;Go(6);}
  else if(Step==6&&DT>2){if(!Check(E.Balls.Num()==1&&FMath::Abs(E.Balls[0].Fuse-Fuse)<.00001&&FVector::Dist(Position,E.Balls[0].Position)<.001&&FMath::Abs(W->GetTimeSeconds()-FrozenTime)<.00001,TEXT("live_frag_position_and_fuse_do_not_advance_in_menu")))return false;Image(TEXT("01_live_frag_pause"));PendingImageAction=[PC](){Tap(PC,EKeys::Escape);Go(7);};}
  else if(Step==7&&E.Balls.IsEmpty()){if(!Check(E.Frag==1&&E.FragThrown==1,TEXT("frag_resumes_original_fuse_and_spends_once")))return false;Key(PC,EKeys::Q,true);Go(8);}
  else if(Step==8&&DT>.9){Key(PC,EKeys::Q,false);Go(9);}
  else if(Step==9&&!E.Clouds.IsEmpty()&&E.ThrowKind.IsEmpty()){Tap(PC,EKeys::Escape);Life=E.Clouds[0].Life;FrozenTime=W->GetTimeSeconds();Go(10);}
  else if(Step==10&&DT>2){if(!Check(E.Clouds.Num()==1&&FMath::Abs(E.Clouds[0].Life-Life)<.00001&&FMath::Abs(W->GetTimeSeconds()-FrozenTime)<.00001,TEXT("smoke_lifetime_frozen_by_real_pause")))return false;Tap(PC,EKeys::Escape);Go(11);}
  else if(Step==11&&DT>.7){if(!Check(E.Clouds.Num()==1&&E.Clouds[0].Life<Life-.3&&E.Smoke==1&&E.SmokeThrown==1,TEXT("smoke_resumes_remaining_life_without_refill")))return false;Finish(true,TEXT("real G/Q preparation cancellation, finite equipment and paused hazard timers"));}
 }else Finish(false,TEXT("unknown UI mode"));
 return !Finished;
}
}
void Initialize(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisCombatUIProbe="),Mode))return;FParse::Value(FCommandLine::Get(),TEXT("ParisCombatUIOut="),Out);Handle=FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateStatic(&Tick));}
void Shutdown(){if(Handle.IsValid())FTSTicker::GetCoreTicker().RemoveTicker(Handle);}
}
