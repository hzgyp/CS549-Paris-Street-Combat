#include "ParisMissionInteraction.h"
#include "ParisBridgeMission.h"
#include "GameFramework/Character.h"
#include "Engine/World.h"
#include "GameFramework/PlayerInput.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/KismetSystemLibrary.h"
#include "UObject/UnrealType.h"

static double ParisInteractionPosture(const ACharacter* Player) {
    const auto* P=Player?FindFProperty<FNumericProperty>(Player->GetClass(),TEXT("DesiredPosture")):nullptr;
    if(!P)return -1;
    const void* V=P->ContainerPtrToValuePtr<void>(Player);
    return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));
}

bool AParisBridgeMission::CanLoadCheckpoint(FString& Reason) const {
    FString Payload;int32 Serial=0;return ReadLatest(Payload,Serial,Reason);
}

FString AParisBridgeMission::CheckpointSaveBlockReason() const {
    if(!CheckpointUnlocked())return TEXT("Defeat all three G1 guards before saving.");
    if(!InsideCheckpoint())return TEXT("Stand on the ground inside the gold checkpoint circle.");
    if(Phase!=TEXT("Won"))return TEXT("Finish securing G1 before saving.");
    if(!Roster.IsEmpty() && (Roster[0]->bIsCrouched || ParisInteractionPosture(Roster[0])!=0))
        return TEXT("Stand up before saving this checkpoint.");
    FString Reason;
    if(!IsSafeBoundary(Reason))return Reason;
    return FString();
}

bool AParisBridgeMission::InteractCheckpoint() {
    ++InteractionRevision;
    if(!RequestCheckpointPrompt())return false;
    return ConfirmCheckpoint();
}

bool AParisBridgePlayerController::InteractionMenuVisible() const {
    const auto* M=AParisBridgeMission::Find(this);
    return M && ParisMissionInteraction::MenuPhase(M->Phase);
}

void AParisBridgePlayerController::RefreshInteractionMenu() {
    auto* M=AParisBridgeMission::Find(this);if(!M)return;
    const bool Menu=InteractionMenuVisible();
    if(!bInteractionModeInitialized || Menu!=bInteractionMenuMode) {
        bInteractionModeInitialized=true;bInteractionMenuMode=Menu;
        bShowMouseCursor=Menu;
        if(Menu) {
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
    RefreshInteractionMenu();
    if(Params.Key==EKeys::LeftMouseButton && bSwallowMenuClick) {
        if(Params.Event==IE_Released)bSwallowMenuClick=false;
        return true;
    }
    auto* M=AParisBridgeMission::Find(this);if(!M)return false;
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
    if(Params.Event==IE_Pressed && Params.Key==EKeys::E) {M->InteractCheckpoint();return true;}
    return false;
}
