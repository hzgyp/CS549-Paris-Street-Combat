#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "AITypes.h"
#include "ParisMapSurveyLibrary.generated.h"
class ARecastNavMesh;
class UNavigationSystemV1;
class ACharacter;
class AAIController;
class UWorld;

UCLASS()
class PARISMAPSURVEYV1_API UParisMapSurveyLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // Navigation queries never rebuild, alter collision or save assets.
    UFUNCTION(BlueprintCallable, Category="Map Survey")
    static FString ExportNavmesh(ARecastNavMesh* NavMesh);
    UFUNCTION(BlueprintCallable, Category="Map Survey")
    static FString NavigationBuildState(UNavigationSystemV1* NavigationSystem);
    UFUNCTION(BlueprintCallable, Category="Map Survey")
    static FString InspectSurveyWorld(UWorld* World);
    UFUNCTION(BlueprintCallable, Category="Map Survey")
    static FString SurveyFloorState(ACharacter* Probe);
    UFUNCTION(BlueprintCallable, Category="Map Survey")
    static int64 DecodeRequestId(FAIRequestID RequestId);
    UFUNCTION(BlueprintCallable, Category="Map Survey")
    static int64 CurrentRequestId(AAIController* Controller);
    // Only exact native disposable classes in a PIE world may be destroyed.
    UFUNCTION(BlueprintCallable, Category="Map Survey")
    static bool DestroySurveyProbe(ACharacter* Probe, AAIController* Controller);
};
