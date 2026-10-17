#include "ParisCombatUI.h"
#include "ParisAudioPreferences.h"
#include "ParisTutorialSoundscape.h"
#include "Framework/Application/SlateApplication.h"
#include "ParisMedicalKits.h"
#include "ParisLanguage.h"
// Presentation and input only. The original mission/equipment/journal own gameplay.
#include "ParisPlayerDeath.h"
#include "ParisBridgeMission.h"
#include "ParisTutorial.h"
#include "ParisCheckpointHistory.h"
#include "ParisMissionInteraction.h"
#include "ParisTacticalEquipment.h"
#include "ParisEquipmentState.h"
#include "Engine/Canvas.h"
#include "Engine/Font.h"
#include "CanvasItem.h"
#include "Fonts/CompositeFont.h"
#include "Fonts/SlateFontInfo.h"
#include "UObject/StrongObjectPtr.h"
#include "Misc/Paths.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerInput.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Dom/JsonObject.h"
#include "UObject/UnrealType.h"

namespace ParisCombatUI {
namespace {
struct FState {
 bool Open=false,OwnPause=false,OldFullTick=false,SwallowClick=false;
 int32 Page=0,Action=0,Help=0,ModalChoice=1,Record=0,HistoryAction=0,TargetSerial=0;
 int32 SettingsTab=0,AudioRow=0,AudioDrag=-1;FString LastHover;
 bool TargetActive=false;FString TargetId,TargetName;TArray<ParisCheckpointHistory::FRecord> HistoryRows;
 FString Confirm,LoadReason,Toast,Tutorial,TutorialCategory;
 bool CanLoad=false;
 double TutorialUntil=0;
 TSet<FString> Seen;
 FVector2D LastMouse=FVector2D(-1,-1);
};
TMap<TWeakObjectPtr<UWorld>,FState> States;
FDelegateHandle CleanupHandle;
bool Detailed=true;
int32 ScaleIndex=2;
const FLinearColor Ivory(.94,.93,.85,1),Brass(.80,.67,.40,1),Muted(.62,.68,.64,1),
 Green(.46,.78,.50,1),Red(.95,.35,.30,1),Panel(.018,.030,.025,.97),Fill(.055,.079,.065,1);
FState& State(const UObject* O){return States.FindOrAdd(O->GetWorld());}
double Num(const UObject* O,const TCHAR* Field){auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),Field):nullptr;if(!P)return -1;const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));}
bool Dead(const UObject* O){auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),TEXT("IsDead")):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
FString ActionLabel(const FString& A){return A==TEXT("ProneEntering")?TEXT("Going prone"):A==TEXT("ProneExiting")?TEXT("Standing up"):A;}
FString ActionState(const UObject* O){auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),TEXT("ActionState")):nullptr;if(P)return ActionLabel(P->GetPropertyValue_InContainer(O).ToString());auto* V=O?FindFProperty<FStrProperty>(O->GetClass(),TEXT("ActionState")):nullptr;return V?ActionLabel(V->GetPropertyValue_InContainer(O)):TEXT("Unavailable");}
FString Posture(const UObject* O){const int32 V=int32(Num(O,TEXT("DesiredPosture")));return V==2?TEXT("PRONE"):V==1?TEXT("CROUCHED"):V==0?TEXT("STANDING"):TEXT("UNAVAILABLE");}
ACharacter* Actor(UWorld* W,const TCHAR* Id){for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(FName(*(FString(TEXT("G1_"))+Id))))return *I;return nullptr;}
FVector2D Ref(AParisBridgePlayerController* PC){float X=0,Y=0;int32 W=0,H=0;PC->GetViewportSize(W,H);if(!PC->GetMousePosition(X,Y))return FVector2D(-1,-1);const double S=FMath::Min(W/1920.,H/1080.);return FVector2D((X-(W-1920*S)*.5)/S,(Y-(H-1080*S)*.5)/S);}
bool Hit(FVector2D P,double X,double Y,double W,double H){return P.X>=X&&P.X<=X+W&&P.Y>=Y&&P.Y<=Y+H;}
void FinishAudioDrag(AParisBridgePlayerController* PC);
void MenuCue(AParisBridgePlayerController* PC,ParisTutorialSoundscape::EMenuCue Cue){ParisTutorialSoundscape::Menu(AParisBridgeMission::Find(PC),Cue);}
void Cursor(AParisBridgePlayerController* PC,bool Menu){PC->bShowMouseCursor=Menu;if(Menu){FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);PC->SetInputMode(Mode);}else {FInputModeGameOnly Mode;Mode.SetConsumeCaptureMouseDown(true);PC->SetInputMode(Mode);}}
void Close(AParisBridgePlayerController* PC,bool Sound=true){auto& U=State(PC);if(!U.Open)return;FinishAudioDrag(PC);if(Sound)MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Back);const bool Unpause=U.OwnPause;U.Open=false;U.Confirm.Empty();U.Toast.Empty();U.OwnPause=false;PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);PC->SetCombatUIFullTick(U.OldFullTick);PC->FlushPressedKeys();if(Unpause)PC->SetPause(false);auto* M=AParisBridgeMission::Find(PC);Cursor(PC,M&&(ParisMissionInteraction::MenuPhase(M->Phase)||M->CheckpointDialogVisible()));UE_LOG(LogTemp,Display,TEXT("PARIS_COMBAT_UI closed owned_pause=%d"),Unpause);}
bool Open(AParisBridgePlayerController* PC,int32 Page){if(ParisPlayerDeath::Presenting(PC))return false;auto* M=AParisBridgeMission::Find(PC);if(!M||M->Phase==TEXT("Preparing")||M->CheckpointDialogVisible()||M->CheckpointPromptVisible)return false;auto& U=State(PC);if(U.Open){U.Page=Page;return true;}auto& E=ParisTacticalEquipment::Session(PC->GetWorld());if(E.EHeld||!E.ThrowKind.IsEmpty()){M->Feedback=TEXT("Finish or cancel your current interaction before opening the menu.");return false;}ParisMedicalKits::Cancel(PC->GetWorld());U.OldFullTick=PC->SetCombatUIFullTick(true);const bool WasPaused=UGameplayStatics::IsGamePaused(PC);U.OwnPause=!WasPaused&&PC->SetPause(true);if(!WasPaused&&!U.OwnPause){PC->SetCombatUIFullTick(U.OldFullTick);M->Feedback=TEXT("Pause unavailable. Continue playing.");return false;}PC->FlushPressedKeys();PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);U.Open=true;U.LastHover.Empty();MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);U.Page=Page;U.Action=0;U.Confirm.Empty();U.Toast.Empty();U.CanLoad=M->CanLoadCheckpoint(U.LoadReason);Cursor(PC,true);U.LastMouse=Ref(PC);UE_LOG(LogTemp,Display,TEXT("PARIS_COMBAT_UI opened page=%d paused=%d"),Page,UGameplayStatics::IsGamePaused(PC));return true;}
void Ask(AParisBridgePlayerController* PC,const FString& Action){if(!Open(PC,0))return;auto& U=State(PC);if(Action==TEXT("Load")&&!U.CanLoad){U.Toast=TEXT("No valid checkpoint is available.");return;}MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);U.Confirm=Action;U.ModalChoice=1;U.LastMouse=Ref(PC);UE_LOG(LogTemp,Display,TEXT("PARIS_COMBAT_UI confirm=%s"),*Action);}
bool HistoryCommit(AParisBridgePlayerController* PC);
void HistoryRefresh(AParisBridgePlayerController* PC);
void Commit(AParisBridgePlayerController* PC){if(HistoryCommit(PC))return;auto& U=State(PC);auto* M=AParisBridgeMission::Find(PC);if(!M)return;const FString Act=U.Confirm;if(Act==TEXT("Load")){FString Reason;if(!M->CanLoadCheckpoint(Reason)){U.Confirm.Empty();U.Toast=TEXT("Checkpoint unavailable. Your game has not changed.");return;}}MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);Close(PC,false);if(Act==TEXT("Load"))M->LoadCheckpoint();else if(Act==TEXT("Restart"))M->RestartMission();else if(Act==TEXT("Exit"))UKismetSystemLibrary::QuitGame(PC,PC,EQuitPreference::Quit,false);}
void Activate(AParisBridgePlayerController* PC,int32 Index){auto* M=AParisBridgeMission::Find(PC);if(!M)return;if(Index==1&&!State(PC).CanLoad)return;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);State(PC).Action=Index;if(Index==0){Close(PC,false);if(M->Phase==TEXT("Ready"))M->StartMission();}else if(Index==1){if(ParisCheckpointHistory::Enabled()){auto& U=State(PC);U.Page=4;U.Record=0;U.HistoryAction=0;HistoryRefresh(PC);}else Ask(PC,TEXT("Load"));}else if(Index==2)Ask(PC,TEXT("Restart"));else if(Index==3)State(PC).Page=2;else if(Index==4)Ask(PC,TEXT("Exit"));}
#include "ParisFieldManualPaint.inl"
#include "ParisEquipmentPanel.inl"
#include "ParisHistoryMenu.inl"
#include "ParisAudioSettingsMenu.inl"
const TCHAR* Tabs[]={TEXT("MISSION"),TEXT("PLAYER & SQUAD"),TEXT("CONTROLS"),TEXT("SETTINGS")};
const TCHAR* Groups[]={TEXT("MOVEMENT"),TEXT("WEAPONS"),TEXT("EQUIPMENT"),TEXT("INTERACTION"),TEXT("CHECKPOINTS")};
struct FHelp {const TCHAR* Key;const TCHAR* Name;const TCHAR* Detail;};
const TArray<TArray<FHelp>> Help={
 {{TEXT("W A S D"),TEXT("Move"),TEXT("Forward, left, back and right")},{TEXT("MOUSE"),TEXT("Look"),TEXT("Turn and aim with the centre reticle")},{TEXT("SHIFT"),TEXT("Run"),TEXT("Hold to run at 4.5 m/s")},{TEXT("ALT"),TEXT("Quiet walk"),TEXT("Hold to move slowly")},{TEXT("SPACE"),TEXT("Jump"),TEXT("Jump when grounded")},{TEXT("CTRL"),TEXT("Crouch"),TEXT("Use the current crouch control")},{TEXT("Z"),TEXT("Prone / stand"),TEXT("Crawling requires a supported, clear surface")}},
 {{TEXT("LEFT MOUSE"),TEXT("Fire"),TEXT("One shot uses one loaded round")},{TEXT("R"),TEXT("Reload"),TEXT("Transfers existing reserve rounds into the rifle")}},
 {{TEXT("HOLD H"),TEXT("Use medical kit"),TEXT("Rifle selected; hold H still for 3s; heals up to 50")},{TEXT("WHEEL"),TEXT("Select equipment"),TEXT("Cycle available equipment; empty types are skipped")},{TEXT("LEFT MOUSE"),TEXT("Prepare / throw"),TEXT("Hold to pull pin; release to throw selected grenade")},{TEXT("ESC / WHEEL"),TEXT("Cancel preparation"),TEXT("Before release: cancel without spending; press again to use")}},
 {{TEXT("E"),TEXT("Pick up medical kit"),TEXT("Aim at a nearby pouch; carry at most 2; full inventory leaves it")},{TEXT("E"),TEXT("Ammo supply"),TEXT("Aim at a nearby box; press to take reserve rounds")},{TEXT("HOLD E"),TEXT("Disarm mine"),TEXT("Stand still; aim within 2 m; hold 2s; release or move cancels")},{TEXT("ESC"),TEXT("Cancel interaction"),TEXT("Cancels disarming or the current checkpoint window")}},
 {{TEXT("E"),TEXT("Save checkpoint"),TEXT("Kill all 3 guards; enter the gold circle; confirm")},{TEXT("F9"),TEXT("Load checkpoint"),TEXT("Opens a confirmation before loading")},{TEXT("F6"),TEXT("Restart mission"),TEXT("Opens a confirmation before restarting")},{TEXT("ESC"),TEXT("Combat menu"),TEXT("Pause and open mission, squad, help and settings")},{TEXT("TAB"),TEXT("Player / squad"),TEXT("Open status; press again to return")}}
};
}
float HudScale(){const float Values[]={.85f,.925f,1.f};return Values[ScaleIndex];}
bool ShowCheckpointList(AParisBridgePlayerController* PC){if(!Open(PC,4))return false;auto& U=State(PC);U.Record=0;U.HistoryAction=0;HistoryRefresh(PC);return true;}
bool IsOpen(const AParisBridgePlayerController* PC){if(!PC)return false;const auto* U=States.Find(PC->GetWorld());return U&&U->Open;}
FString Confirmation(const APlayerController* PC){const auto* U=PC?States.Find(PC->GetWorld()):nullptr;return U&&U->Open?U->Confirm:FString();}
void Refresh(AParisBridgePlayerController* PC){if(!IsOpen(PC))return;PC->bShowMouseCursor=true;auto& U=State(PC);if(U.AudioDrag>=0&&FSlateApplication::IsInitialized()&&!FSlateApplication::Get().GetPressedMouseButtons().Contains(EKeys::LeftMouseButton))FinishAudioDrag(PC);else UpdateAudioDrag(PC);const auto P=Ref(PC);if(FVector2D::Distance(P,U.LastMouse)>1){if(U.Confirm.IsEmpty()){for(int32 I=0;I<5;++I)if((I!=1||U.CanLoad)&&Hit(P,SideX,SideY+I*SideStep,SideW,SideH))U.Action=I;}else {if(Hit(P,705,617,240,52))U.ModalChoice=0;else if(Hit(P,975,617,240,52))U.ModalChoice=1;}if(U.AudioDrag<0){const FString Target=HoverTarget(PC,P);if(Target!=U.LastHover){if(!Target.IsEmpty())MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Navigate);U.LastHover=Target;}}U.LastMouse=P;}}
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& Args){auto* M=AParisBridgeMission::Find(PC);if(!M)return false;auto& U=State(PC);if(Args.Key==EKeys::LeftMouseButton&&Args.Event==IE_Released)FinishAudioDrag(PC);if(Args.Key==EKeys::LeftMouseButton&&U.SwallowClick){if(Args.Event==IE_Released)U.SwallowClick=false;return true;}if(M->CheckpointDialogVisible()||M->CheckpointPromptVisible)return false;
 if(U.Open){
  if(Args.Event==IE_Released){PC->APlayerController::InputKey(Args);return true;}
  if(Args.Event!=IE_Pressed)return true;
  if(Args.Key==EKeys::Escape){FinishAudioDrag(PC);if(!U.Confirm.IsEmpty()){MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Back);U.Confirm.Empty();}else if(U.Page==4){MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Back);U.Page=0;}else Close(PC);return true;}
  if(Args.Key==EKeys::Tab){if(U.Confirm.IsEmpty())Close(PC);return true;}
  if(!U.Confirm.IsEmpty()){
   if(Args.Key==EKeys::Left||Args.Key==EKeys::Right){U.ModalChoice=1-U.ModalChoice;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Navigate);}
   else if(Args.Key==EKeys::Enter){if(U.ModalChoice==0)Commit(PC);else {MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Back);U.Confirm.Empty();}}
   else if(Args.Key==EKeys::LeftMouseButton){U.SwallowClick=true;const auto P=Ref(PC);if(Hit(P,705,617,240,52))Commit(PC);else if(Hit(P,975,617,240,52)){MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Back);U.Confirm.Empty();}}
   return true;
  }
  if(Args.Key==EKeys::PageUp||Args.Key==EKeys::PageDown){FinishAudioDrag(PC);U.Page=(FMath::Min(U.Page,3)+(Args.Key==EKeys::PageUp?3:1))%4;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Navigate);return true;}
  if(AudioSettingsInput(PC,Args))return true;
  if(U.Page==3&&Args.Key==EKeys::L){ParisLanguage::SetChinese(!ParisLanguage::Chinese());MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);return true;}
  if(HistoryInput(PC,Args))return true;
  if(Args.Key==EKeys::Left||Args.Key==EKeys::Right){U.Page=(U.Page+(Args.Key==EKeys::Left?3:1))%4;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Navigate);}
  else if(Args.Key==EKeys::Up||Args.Key==EKeys::Down){const int32 D=Args.Key==EKeys::Up?-1:1;for(int32 I=0;I<5;++I){U.Action=(U.Action+D+5)%5;if(U.Action!=1||U.CanLoad)break;}MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Navigate);}
  else if(Args.Key==EKeys::Enter)Activate(PC,U.Action);
  else if(Args.Key==EKeys::LeftMouseButton){U.SwallowClick=true;const auto P=Ref(PC);for(int32 I=0;I<4;++I)if(Hit(P,NavX[I],NavY,NavW[I],NavH)){FinishAudioDrag(PC);if(U.Page!=I)MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);U.Page=I;return true;}for(int32 I=0;I<5;++I)if(Hit(P,SideX,SideY+I*SideStep,SideW,SideH)){Activate(PC,I);return true;}if(U.Page==2)for(int32 I=0;I<5;++I)if(Hit(P,GroupX+I*GroupStep,GroupY,GroupW,GroupH)){if(U.Help!=I)MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);U.Help=I;return true;}if(U.Page==3&&U.SettingsTab==0){if(Hit(P,660,465,300,52)){Detailed=!Detailed;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);}if(Hit(P,660,580,300,52)){ScaleIndex=(ScaleIndex+1)%3;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);}if(Hit(P,660,750,300,52)){ParisLanguage::SetChinese(!ParisLanguage::Chinese());MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);}}}
  else if(U.Page==2){const FKey Keys[]={EKeys::One,EKeys::Two,EKeys::Three,EKeys::Four,EKeys::Five};for(int32 I=0;I<5;++I)if(Args.Key==Keys[I]){if(U.Help!=I)MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Navigate);U.Help=I;}}
  return true;
 }
 if(Args.Event!=IE_Pressed)return false;
 auto& E=ParisTacticalEquipment::Session(PC->GetWorld());
 if(Args.Key==EKeys::Escape){if(E.EHeld||!E.ThrowKind.IsEmpty())return false;Open(PC,0);return true;}
 if(Args.Key==EKeys::Tab&&!ParisMissionInteraction::MenuPhase(M->Phase)){Open(PC,1);return true;}
 if(Args.Key==EKeys::F6||Args.Key==EKeys::F9){Ask(PC,Args.Key==EKeys::F6?TEXT("Restart"):TEXT("Load"));return true;}
 return false;
}
#include "ParisFieldManualMenu.inl"
void DrawExtras(AParisBridgeHUD* H,AParisBridgeMission* M){if(M->CheckpointDialogVisible()||ParisMissionInteraction::MenuPhase(M->Phase))return;auto* PC=Cast<AParisBridgePlayerController>(H->PlayerOwner);if(!PC||!PC->GetPawn())return;auto& U=State(PC);auto& E=ParisTacticalEquipment::Session(PC->GetWorld());FPaint P(H,true);P.Key(TEXT("ESC"),48,1044,54);P.Text(TEXT("MENU"),111,1050,17,Muted);P.Key(TEXT("TAB"),230,1044,54);P.Text(TEXT("STATUS"),293,1050,17,Muted);P.Text(Posture(PC->GetPawn()),427,1018,18,Muted);

 DrawEquipmentPanel(H,PC,E);
  // The tutorial HUD owns its one live instruction; do not add timed legacy copy.
  if(ParisTutorial::Enabled()){U.Tutorial.Empty();U.TutorialUntil=0;return;}
 FString Category,Copy;const FString Hint=ParisTacticalEquipment::HudInteraction(PC->GetWorld());if(!E.ThrowKind.IsEmpty()&&(E.ThrowStage==TEXT("Start")||E.ThrowStage==TEXT("Hold"))){Category=TEXT("throw");Copy=TEXT("Hold left mouse to prepare. Release to throw; ESC cancels before release.");}else if(E.EHeld||(ParisTutorial::Enabled()?(Hint.StartsWith(TEXT("HOLD E 2s"))||Hint.StartsWith(TEXT("DISARMING"))):Hint.Contains(TEXT("DISARM")))){Category=TEXT("mine");Copy=TEXT("Aim within 2 m. Hold E for 2 seconds; release or move to cancel.");}else if(Hint.Contains(TEXT("AMMO SUPPLY"))||(ParisTutorial::Enabled()&&Hint.StartsWith(TEXT("E SUPPLY")))){Category=TEXT("supply");Copy=ParisTutorial::Enabled()?TEXT("E transfers finite rounds, frags and smoke. Reload your rifle with R."):TEXT("E takes finite reserve rounds. It does not reload your rifle.");}else if(M->CheckpointPromptVisible){Category=TEXT("save");Copy=TEXT("Press E to confirm saving. Wait for the success window.");}
 if(!M->CheckpointPromptVisible&&E.ThrowKind.IsEmpty()&&!E.EHeld&&(Hint.IsEmpty()||Hint.Contains(TEXT("MINE NEARBY")))){for(const auto& Mine:ParisTacticalEquipment::MineHints(PC->GetWorld()))if(Mine.Value>2&&Mine.Value<4.5){P.Box(640,790,640,42,FLinearColor(.009,.015,.012,.82));P.Text(TEXT("VISIBLE MINE: APPROACH WITHIN 2 m TO DISARM"),660,800,20,Brass);break;}}
 if((ParisTutorial::Enabled()&&((U.TutorialCategory==TEXT("mine")&&Category!=TEXT("mine"))||ParisTutorial::DialogVisible(M)))||(U.TutorialCategory==TEXT("save")&&!M->CheckpointPromptVisible)||(U.TutorialCategory==TEXT("throw")&&(E.ThrowKind.IsEmpty()||E.ThrowStage==TEXT("Cancel")||E.ThrowStage==TEXT("Release")))){U.Tutorial.Empty();U.TutorialUntil=0;}
 if(Detailed&&!Category.IsEmpty()&&!U.Seen.Contains(Category)){U.Seen.Add(Category);U.Tutorial=Copy;U.TutorialCategory=Category;U.TutorialUntil=PC->GetWorld()->GetTimeSeconds()+7;UE_LOG(LogTemp,Display,TEXT("PARIS_COMBAT_UI guidance=%s"),*Category);}
 if(Detailed&&PC->GetWorld()->GetTimeSeconds()<U.TutorialUntil){const double GuideY=M->CheckpointPromptVisible?650:864;P.Box(545,GuideY,870,47,FLinearColor(.009,.015,.012,.82));P.Text(U.Tutorial,563,GuideY+12,20,Brass);}
}
TSharedPtr<FJsonObject> Inspect(AParisBridgePlayerController* PC){auto O=MakeShared<FJsonObject>();auto& U=State(PC);auto* M=AParisBridgeMission::Find(PC);O->SetBoolField(TEXT("open"),U.Open);O->SetBoolField(TEXT("paused"),UGameplayStatics::IsGamePaused(PC));O->SetNumberField(TEXT("page"),U.Page);O->SetNumberField(TEXT("history_selected"),U.Record);O->SetNumberField(TEXT("history_action"),U.HistoryAction);O->SetNumberField(TEXT("history_count"),U.HistoryRows.Num());O->SetNumberField(TEXT("modal_choice"),U.ModalChoice);O->SetStringField(TEXT("toast"),U.Toast);O->SetNumberField(TEXT("help"),U.Help);O->SetStringField(TEXT("confirm"),U.Confirm);O->SetBoolField(TEXT("load_enabled"),U.CanLoad);O->SetNumberField(TEXT("hud_scale"),HudScale());O->SetBoolField(TEXT("detailed"),Detailed);O->SetNumberField(TEXT("settings_tab"),U.SettingsTab);O->SetNumberField(TEXT("audio_row"),U.AudioRow);O->SetNumberField(TEXT("audio_drag"),U.AudioDrag);for(int32 I=0;I<5;++I)O->SetNumberField(FString(TEXT("audio_"))+FString::FromInt(I),ParisAudioPreferences::Volume(ParisAudioPreferences::EBus(I)));O->SetStringField(TEXT("language"),ParisLanguage::Chinese()?TEXT("zh-Hans"):TEXT("en"));O->SetStringField(TEXT("tutorial"),U.Tutorial);O->SetNumberField(TEXT("tutorial_seen"),U.Seen.Num());if(M){O->SetStringField(TEXT("phase"),M->Phase);O->SetNumberField(TEXT("cleared"),3-M->LivingDefenders);O->SetBoolField(TEXT("checkpoint_unlocked"),M->CheckpointUnlocked());}auto& E=ParisTacticalEquipment::Session(PC->GetWorld());O->SetNumberField(TEXT("frag"),E.Frag);O->SetNumberField(TEXT("smoke"),E.Smoke);TArray<TSharedPtr<FJsonValue>> Roster;for(const TCHAR* Id:{TEXT("Player"),TEXT("Ally1"),TEXT("Ally2")}){auto* C=Actor(PC->GetWorld(),Id);auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("id"),Id);Row->SetNumberField(TEXT("health"),Num(C,TEXT("Health")));Row->SetNumberField(TEXT("loaded"),Num(C,TEXT("LoadedAmmo")));Row->SetNumberField(TEXT("reserve"),Num(C,TEXT("ReserveAmmo")));Row->SetBoolField(TEXT("dead"),Dead(C));Row->SetStringField(TEXT("posture"),Posture(C));Row->SetStringField(TEXT("action"),ActionState(C));Roster.Add(MakeShared<FJsonValueObject>(Row));}O->SetArrayField(TEXT("roster"),Roster);return O;}
void Initialize(){CleanupHandle=FWorldDelegates::OnWorldCleanup.AddLambda([](UWorld* W,bool,bool){States.Remove(W);});}
void Shutdown(){FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);States.Empty();}
}
