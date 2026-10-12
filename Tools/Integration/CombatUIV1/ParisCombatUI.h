#pragma once
#include "CoreMinimal.h"
class AParisBridgePlayerController;
class AParisBridgeHUD;
class AParisBridgeMission;
class APlayerController;
class FJsonObject;
struct FInputKeyEventArgs;
namespace ParisCombatUI {
void Initialize();
void Shutdown();
bool Input(AParisBridgePlayerController* Controller,const FInputKeyEventArgs& Params);
bool IsOpen(const AParisBridgePlayerController* Controller);
void Refresh(AParisBridgePlayerController* Controller);
bool DrawMenu(AParisBridgeHUD* HUD,AParisBridgeMission* Mission);
void DrawExtras(AParisBridgeHUD* HUD,AParisBridgeMission* Mission);
float HudScale();
FString Confirmation(const APlayerController* Controller);
TSharedPtr<FJsonObject> Inspect(AParisBridgePlayerController* Controller);
}
