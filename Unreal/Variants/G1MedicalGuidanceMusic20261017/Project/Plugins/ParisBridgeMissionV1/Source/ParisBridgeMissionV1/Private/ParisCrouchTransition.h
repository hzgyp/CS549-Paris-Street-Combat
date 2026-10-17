#pragma once
#include "CoreMinimal.h"
class AParisBridgePlayerController;
class ACharacter;
class FJsonObject;
struct FInputKeyEventArgs;

namespace ParisCrouchTransition {
void Initialize();
void Shutdown();
bool Input(AParisBridgePlayerController* Controller,const FInputKeyEventArgs& Key);
bool Active(const ACharacter* Player);
TSharedPtr<FJsonObject> Inspect(UWorld* World);
}
