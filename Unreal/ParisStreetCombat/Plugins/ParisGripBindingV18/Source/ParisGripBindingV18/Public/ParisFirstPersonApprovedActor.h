#pragma once

#include "ParisFPUpperBodyV19Actor.h"
#include "ParisFirstPersonApprovedActor.generated.h"

// Persistent selection wrapper only: the accepted grip/motion algorithms stay unchanged.
UCLASS(BlueprintType)
class PARISGRIPBINDINGV18_API AParisFirstPersonApprovedActor : public AParisFPUpperBodyV19Actor
{
    GENERATED_BODY()
public:
    AParisFirstPersonApprovedActor();
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Approved Display") TObjectPtr<UParisGripV18Config> BindingConfig;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Approved Display") TObjectPtr<USkeletalMesh> DisplayMesh;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Approved Display") TObjectPtr<UStaticMesh> RifleMesh;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Approved Display") TObjectPtr<UAnimSequence> HoldingClip;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Approved Display") FString SetupState = TEXT("WaitingForOriginalOwner");

private:
    float WaitingSeconds = 0;
    float PreparedSeconds = 0;
    bool HoldingPrepared = false;
    bool SetupStopped = false;
    void TryInitialize(float DeltaSeconds);
    void StopSetup(const FString& Reason);
};
