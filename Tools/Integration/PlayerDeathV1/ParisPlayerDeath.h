#pragma once
#include "CoreMinimal.h"
class UObject;
class UWorld;
class FJsonObject;
namespace ParisPlayerDeath {
void Initialize();
void Shutdown();
bool Presenting(const UObject* Context);
bool Complete(const UObject* Context);
TSharedPtr<FJsonObject> Inspect(UWorld* World);
}
