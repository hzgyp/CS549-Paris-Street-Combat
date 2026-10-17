#pragma once
#include "CoreMinimal.h"
class UWorld;
class AParisBridgeHUD;
class AParisBridgeMission;
class FJsonObject;
namespace ParisPlayerDamageFeedback {
void Initialize();
void Shutdown();
void DrawEdges(AParisBridgeHUD* HUD,AParisBridgeMission* Mission,float Width,float Height);
double TrailFraction(UWorld* World);
bool CriticalVisible(UWorld* World);
TSharedPtr<FJsonObject> Inspect(UWorld* World);
}
