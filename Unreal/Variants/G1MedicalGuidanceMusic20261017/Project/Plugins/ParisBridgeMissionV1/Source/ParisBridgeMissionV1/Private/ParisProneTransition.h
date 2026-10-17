#pragma once
#include "CoreMinimal.h"
class AParisBridgePlayerController;
class ACharacter;
class UWorld;
class FJsonObject;
struct FInputKeyEventArgs;
namespace ParisProneTransition {
void Initialize();
void Shutdown();
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& Key);
bool Active(const ACharacter* Player);
TSharedPtr<FJsonObject> Inspect(UWorld* World);
}
