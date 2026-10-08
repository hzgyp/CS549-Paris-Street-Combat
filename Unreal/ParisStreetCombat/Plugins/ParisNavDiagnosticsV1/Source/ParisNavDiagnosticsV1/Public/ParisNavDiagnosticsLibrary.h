#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ParisNavDiagnosticsLibrary.generated.h"
class AAIController;

UCLASS()
class PARISNAVDIAGNOSTICSV1_API UParisNavDiagnosticsLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // Query only: budget0 preserves the original filter,65536 clones it; never submits movement.
    UFUNCTION(BlueprintCallable, Category="Navigation Diagnostics")
    static FString InspectStandardQuery(AAIController* Controller, FVector Goal, int32 Budget);
};
