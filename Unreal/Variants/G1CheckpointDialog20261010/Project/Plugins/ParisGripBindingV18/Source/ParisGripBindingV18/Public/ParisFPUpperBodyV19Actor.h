#pragma once

#include "ParisGripV18Actor.h"
#include "ParisFPUpperBodyV19Actor.generated.h"

class UAnimSequence;

// First-person display only. Original body locomotion and actions are untouched.
UCLASS(BlueprintType)
class PARISGRIPBINDINGV18_API AParisFPUpperBodyV19Actor : public AParisGripV18Actor
{
    GENERATED_BODY()
public:
    AParisFPUpperBodyV19Actor();
    UFUNCTION(BlueprintCallable, Category="Existing Motion")
    bool PrepareHoldingSource(USkeletalMesh* SourceMesh, UAnimSequence* ExistingHoldingClip);
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Existing Motion") TObjectPtr<USkeletalMeshComponent> HoldingSource;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Existing Motion") float SourceTransitionAlpha = 1;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Existing Motion") float ExistingGripWeight = 1;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Existing Motion") FString ExistingClipPath;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Existing Motion") FTransform BodySourceToHolding;
protected:
    virtual bool AdaptSourceLocalPose(const FReferenceSkeleton& DisplayRef,
        TArray<FTransform>& InOutLocal, FName Action, float DeltaSeconds) override;
    virtual float GetGripWeight(bool Holding) const override { return ExistingGripWeight; }
private:
    TArray<FTransform> PreviousSourcePose;
    TArray<FTransform> TransitionFrom;
    FName PreviousAction;
    float TransitionElapsed = .25f;
    float TransitionFromGrip = 1;
    bool SourceFrameCached = false;
};
