#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ParisFormalSurveyLibrary.generated.h"
class ACharacter;
class AController;
UCLASS()
class PARISFORMALSURVEYV1_API UParisFormalSurveyLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="Formal Map Test")
    static FString ReadFormalCharacter(ACharacter* Character);
    UFUNCTION(BlueprintCallable, Category="Formal Map Test")
    static FString ReadFormalController(AController* Controller);
    UFUNCTION(BlueprintCallable, Category="Formal Map Test")
    static FString BeginFormalMove(AController* Controller, FVector Goal);
};
