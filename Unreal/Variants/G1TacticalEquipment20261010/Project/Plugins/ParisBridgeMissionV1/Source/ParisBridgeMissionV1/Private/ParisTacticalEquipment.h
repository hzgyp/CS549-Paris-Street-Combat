#pragma once
#include "CoreMinimal.h"
class AAIController;
class AParisBridgeMission;
class AParisBridgePlayerController;
class AParisBridgeHUD;
struct FInputKeyEventArgs;
namespace ParisTacticalEquipment {
bool OwnsNavigation(const AAIController* Controller);
void Initialize();
void Shutdown();
bool Input(AParisBridgePlayerController* Controller,const FInputKeyEventArgs& Params);
bool Occluded(UWorld* World,const FVector& From,const FVector& To);
FString HudInventory(UWorld* World);
FString HudInteraction(UWorld* World);
float HudProgress(UWorld* World);
}
