#include "ParisMissionInteraction.h"
#include "ParisCombatUI.h"
#include "ParisTacticalEquipment.h"
#include "ParisBridgeMission.h"
#include "GameFramework/Character.h"
#include "Engine/World.h"
#include "GameFramework/PlayerInput.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/KismetSystemLibrary.h"
#include "UObject/UnrealType.h"

bool AParisBridgeMission::CanLoadCheckpoint(FString& Reason) const {
    FString Payload;int32 Serial=0;return ReadLatest(Payload,Serial,Reason);
}

FString AParisBridgeMission::CheckpointSaveBlockReason() const {
    if(!CheckpointUnlocked())return TEXT("Defeat all three G1 guards before saving.");
    if(!InsideCheckpoint())return TEXT("Stand on the ground inside the gold checkpoint circle.");
    if(bTravelPending)return TEXT("Wait for the mission to finish loading.");
    return FString();
}

bool AParisBridgeMission::InteractCheckpoint() {
    if(CheckpointDialogVisible())return false;
    ++InteractionRevision;
    if(!RequestCheckpointPrompt())return false;
    return ConfirmCheckpoint();
}

bool AParisBridgePlayerController::InteractionMenuVisible() const {
    const auto* M=AParisBridgeMission::Find(this);
    return M && ParisMissionInteraction::MenuPhase(M->Phase);
}

void AParisBridgePlayerController::RefreshInteractionMenu() {
    if(ParisCombatUI::IsOpen(this)){ParisCombatUI::Refresh(this);return;}
    auto* M=AParisBridgeMission::Find(this);if(!M)return;
    const bool Menu=InteractionMenuVisible(),Dialog=M->CheckpointDialogVisible();
    const bool Lock=M->CheckpointDialogLocksGameplay();
    if(Lock!=bCheckpointInputHeld){SetIgnoreMoveInput(Lock);SetIgnoreLookInput(Lock);bCheckpointInputHeld=Lock;}
    if(!bInteractionModeInitialized || Menu!=bInteractionMenuMode || Dialog!=bInteractionDialogMode) {
        bInteractionModeInitialized=true;bInteractionMenuMode=Menu;bInteractionDialogMode=Dialog;
        bShowMouseCursor=Menu || Dialog;
        if(Menu || Dialog) {
            FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);
            Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);SetInputMode(Mode);
            MenuSelection=0;NextMenuCheck=0;
        } else {
            FInputModeGameOnly Mode;Mode.SetConsumeCaptureMouseDown(true);SetInputMode(Mode);
        }
        UE_LOG(LogTemp,Display,TEXT("PARIS_INTERACTION_INPUT_MODE menu=%d phase=%s"),Menu,*M->Phase);
    }
    if(Menu && GetWorld()->GetTimeSeconds()>=NextMenuCheck) {
        bMenuLoadEnabled=M->CanLoadCheckpoint(MenuLoadReason);
        NextMenuCheck=GetWorld()->GetTimeSeconds()+1;
    }
}

void AParisBridgePlayerController::PlayerTick(float DeltaTime) {
    Super::PlayerTick(DeltaTime);RefreshInteractionMenu();
    if(InteractionMenuVisible()) {
        float X=0,Y=0;int32 W=0,H=0;GetViewportSize(W,H);
        if(GetMousePosition(X,Y)) {
            const FVector2D Mouse(X,Y);
            if(!bMenuMouseObserved || FVector2D::Distance(Mouse,LastMenuMouse)>1) {
                const int32 Hit=ParisMissionInteraction::MenuHit(Mouse,FIntPoint(W,H));
                if(Hit!=INDEX_NONE)MenuSelection=Hit;
            }
            LastMenuMouse=Mouse;bMenuMouseObserved=true;
        }
    }
}

bool AParisBridgePlayerController::SelectMenuAtScreen(FVector2D Mouse,FIntPoint Size) {
    if(!InteractionMenuVisible())return false;
    const int32 Hit=ParisMissionInteraction::MenuHit(Mouse,Size);
    if(Hit==INDEX_NONE)return false;
    MenuSelection=Hit;return ActivateInteractionMenu();
}

bool AParisBridgePlayerController::ActivateInteractionMenu() {
    auto* M=AParisBridgeMission::Find(this);if(!M || !InteractionMenuVisible())return false;
    ++M->InteractionRevision;
    UE_LOG(LogTemp,Display,TEXT("PARIS_INTERACTION_MENU action=%d phase=%s enabled=%d"),MenuSelection,*M->Phase,MenuActionEnabled(MenuSelection));
    if(MenuSelection==1) {
        if(!bMenuLoadEnabled){M->Feedback=MenuLoadReason;return false;}
        return M->LoadCheckpoint();
    }
    if(MenuSelection==2){UKismetSystemLibrary::QuitGame(this,this,EQuitPreference::Quit,false);return true;}
    if(MenuSelection==0) {
        bool Started=true;
        if(M->Phase==TEXT("Ready"))Started=M->StartMission();else M->RestartMission();
        RefreshInteractionMenu();return Started;
    }
    return false;
}

bool AParisBridgePlayerController::HandleInteractionInput(const FInputKeyEventArgs& Params) {
    if(ParisCombatUI::Input(this,Params))return true;
    RefreshInteractionMenu();
    if(Params.Key==EKeys::LeftMouseButton && bSwallowMenuClick) {
        if(Params.Event==IE_Released)bSwallowMenuClick=false;
        return true;
    }
    auto* M=AParisBridgeMission::Find(this);if(!M)return false;
    if(M->CheckpointDialogVisible()) {
        if(Params.Key==EKeys::LeftMouseButton) {
            if(Params.Event==IE_Pressed){bSwallowMenuClick=true;float X=0,Y=0;int32 W=0,H=0;GetViewportSize(W,H);
                if(GetMousePosition(X,Y)){const int32 Button=ParisMissionInteraction::CheckpointHit(FVector2D(X,Y),FIntPoint(W,H),M->CheckpointDialogState()==TEXT("Failed"));
                    if(Button!=INDEX_NONE)M->ActivateCheckpointDialog(Button);}}
            return true;
        }
        if(Params.Event==IE_Pressed){
            if(Params.Key==EKeys::Escape){M->ActivateCheckpointDialog(M->CheckpointDialogState()==TEXT("Failed")?1:0);return true;}
            if(Params.Key==EKeys::E || Params.Key==EKeys::Enter){if(M->CheckpointDialogState()==TEXT("Succeeded") || M->CheckpointDialogState()==TEXT("Failed"))M->ActivateCheckpointDialog(0);return true;}
        }
        // Always deliver releases to original bindings. Waiting permits standing/stopping.
        if(M->CheckpointDialogLocksGameplay() && Params.Event!=IE_Released)return true;
    }
    if(InteractionMenuVisible()) {
        if(Params.Key==EKeys::LeftMouseButton) {
            if(Params.Event==IE_Pressed) {
                bSwallowMenuClick=true;float X=0,Y=0;int32 W=0,H=0;GetViewportSize(W,H);
                if(GetMousePosition(X,Y))SelectMenuAtScreen(FVector2D(X,Y),FIntPoint(W,H));
            }
            return true;
        }
        if(Params.Event==IE_Pressed) {
            if(Params.Key==EKeys::Up || Params.Key==EKeys::Down || Params.Key==EKeys::Tab) {
                const int32 D=Params.Key==EKeys::Up?-1:1;
                for(int32 I=0;I<3;++I){MenuSelection=(MenuSelection+D+3)%3;if(MenuActionEnabled(MenuSelection))break;}
                return true;
            }
            if(Params.Key==EKeys::Enter){ActivateInteractionMenu();return true;}
        }
    }
    if(!InteractionMenuVisible() && !M->CheckpointDialogVisible() && ParisTacticalEquipment::Input(this,Params))return true;
    if(Params.Event==IE_Pressed && Params.Key==EKeys::E) {M->InteractCheckpoint();return true;}
    return false;
}

void AParisBridgeMission::SetCheckpointDialog(const FString& State,const FString& Detail) {
    SaveDialogState=State;SaveDialogDetail=Detail;bSaveDialogDrawn=false;SaveDialogDrawnFrame=0;++InteractionRevision;
    UE_LOG(LogTemp,Display,TEXT("PARIS_CHECKPOINT_DIALOG state=%s serial=%d reason=%s"),*State,SaveSerial,*Detail);
}
void AParisBridgeMission::MarkCheckpointDialogDrawn() {
    if(!bSaveDialogDrawn){bSaveDialogDrawn=true;SaveDialogDrawnFrame=GFrameCounter;
        UE_LOG(LogTemp,Display,TEXT("PARIS_CHECKPOINT_DIALOG_DRAW state=%s frame=%llu"),*SaveDialogState,SaveDialogDrawnFrame);}
}
void AParisBridgeMission::UpdateCheckpointDialog() {
    if(SaveDialogState!=TEXT("Waiting") && SaveDialogState!=TEXT("Saving"))return;
    if(!InsideCheckpoint()){
        SetCheckpointDialog(TEXT("None"),FString());Feedback=TEXT("Save cancelled: you left the checkpoint circle.");return;
    }
    const FString Reason=CheckpointSaveBlockReason();
    if(!Reason.IsEmpty()){
        if(GetWorld()->GetTimeSeconds()-SaveDialogRequestedAt>30){SetCheckpointDialog(TEXT("Failed"),TEXT("Save request timed out. ")+Reason);return;}
        if(SaveDialogState!=TEXT("Waiting") || SaveDialogDetail!=Reason)SetCheckpointDialog(TEXT("Waiting"),Reason);
        return;
    }
    if(SaveDialogState==TEXT("Waiting")){SetCheckpointDialog(TEXT("Saving"),FString());return;}
    if(!bSaveDialogDrawn || GFrameCounter<=SaveDialogDrawnFrame+1)return;
    UE_LOG(LogTemp,Display,TEXT("PARIS_CHECKPOINT_DIALOG_WRITE frame=%llu after_draw=%llu"),GFrameCounter,SaveDialogDrawnFrame);
    TGuardValue<bool> Permit(bConfirmedSaveRequest,true);
    if(SaveCheckpoint()){
        CheckpointPromptVisible=false;bCheckpointDismissed=true;bCheckpointSavedThisVisit=true;
        SetCheckpointDialog(TEXT("Succeeded"),FString());
    } else SetCheckpointDialog(TEXT("Failed"),Feedback);
}
bool AParisBridgeMission::ActivateCheckpointDialog(int32 Button) {
    if(SaveDialogState==TEXT("Saving") || !CheckpointDialogVisible())return false;
    if(SaveDialogState==TEXT("Failed") && Button==0){
        SetCheckpointDialog(TEXT("None"),FString());CheckpointPromptVisible=InsideCheckpoint();return ConfirmCheckpoint();
    }
    if(Button<0 || Button>(SaveDialogState==TEXT("Failed")?1:0))return false;
    const bool Saved=SaveDialogState==TEXT("Succeeded");
    SetCheckpointDialog(TEXT("None"),FString());CheckpointPromptVisible=false;bCheckpointDismissed=true;
    if(!Saved)Feedback=TEXT("Checkpoint not saved. Press E inside the circle when ready.");
    return true;
}
