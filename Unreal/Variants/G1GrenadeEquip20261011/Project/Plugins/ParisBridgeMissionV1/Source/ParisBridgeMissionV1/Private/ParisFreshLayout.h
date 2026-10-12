#pragma once
#include "CoreMinimal.h"
class AParisBridgeMission;
class ACharacter;
namespace ParisFreshLayout {
bool Apply(AParisBridgeMission* Mission,const TArray<TObjectPtr<ACharacter>>& Roster,FString& Error);
}
