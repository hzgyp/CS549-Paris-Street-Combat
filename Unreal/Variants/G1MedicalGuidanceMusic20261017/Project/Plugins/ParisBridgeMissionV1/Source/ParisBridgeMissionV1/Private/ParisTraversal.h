#pragma once
#include "CoreMinimal.h"
class AParisBridgePlayerController;
class ACharacter;
class AActor;
struct FInputKeyEventArgs;
namespace ParisTraversal {
void Initialize();
void Shutdown();
bool Input(AParisBridgePlayerController*,const FInputKeyEventArgs&);
void Tick(UWorld*,float);
bool Active(const ACharacter*);
bool Request(AParisBridgePlayerController*,FString&);
FString Inspect(UWorld*);
FString Hint(UWorld*);
AActor* Fixture(UWorld*);
void SetObserver(AParisBridgePlayerController*,bool);
// Refresh only the existing collision-aware observer after a finite pose sample.
void RefreshObserver(UWorld*);
}
