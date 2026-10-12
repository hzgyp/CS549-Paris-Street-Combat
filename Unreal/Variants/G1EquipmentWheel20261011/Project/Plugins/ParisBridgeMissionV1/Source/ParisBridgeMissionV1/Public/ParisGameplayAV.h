#pragma once
#include "CoreMinimal.h"
class ACharacter;
class AParisBridgeMission;
namespace ParisGameplayAV
{
void Initialize();
void Shutdown();
void Prime(AParisBridgeMission* Mission,const TArray<TObjectPtr<ACharacter>>& Roster);
void Tick(AParisBridgeMission* Mission,const TArray<TObjectPtr<ACharacter>>& Roster);
bool RestoreTerminalDeath(ACharacter* Character,FString& Error);
FString Inspect(UWorld* World);
bool VerifyRestoredCorpses(UWorld* World,FString& Error);
}
