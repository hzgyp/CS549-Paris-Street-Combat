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
bool HasArmedMineTarget(UWorld* World);
FString HudInventory(UWorld* World);
FString HudInteraction(UWorld* World);
float HudProgress(UWorld* World);
TArray<TPair<FVector,float>> MineHints(UWorld* World);
}
