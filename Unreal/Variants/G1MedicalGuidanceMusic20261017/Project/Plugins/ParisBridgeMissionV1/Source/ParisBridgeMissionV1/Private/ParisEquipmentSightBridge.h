#pragma once
#include "CoreMinimal.h"
#include "Perception/PawnSensingComponent.h"
#include "ParisEquipmentSightBridge.generated.h"

// Separate native object: no added reflected fields on the cooked mission/pawns.
UCLASS()
class UParisEquipmentSightBridge : public UObject
{
    GENERATED_BODY()
public:
    TWeakObjectPtr<UPawnSensingComponent> Sensor;
    UPawnSensingComponent::FSeePawnDelegate Original;
    UFUNCTION() void Seen(APawn* Pawn);
};
