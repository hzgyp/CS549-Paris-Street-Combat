#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ParisGridSurveyLibrary.generated.h"
class ACharacter;
class ARecastNavMesh;
class UWorld;

UCLASS()
class PARISGRIDSURVEYV1_API UParisGridSurveyLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Map Grid")
    static ACharacter* CreateGridProbe(UWorld* World);
    UFUNCTION(BlueprintCallable, Category="Map Grid")
    static bool DestroyGridProbe(ACharacter* Probe);
    UFUNCTION(BlueprintCallable, Category="Map Grid")
    static FString InspectGridWorld(UWorld* World);
    UFUNCTION(BlueprintCallable, Category="Map Grid")
    static FString SampleGridCells(ARecastNavMesh* NavMesh, ACharacter* Probe, const FString& RequestsJson);
    UFUNCTION(BlueprintCallable, Category="Map Grid")
    static FString SampleGridLinks(ARecastNavMesh* NavMesh, ACharacter* Probe, const FString& RequestsJson);
};
