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
    // Transient display source only; no reflected/save fields or rifle constants.
    void SetEquipmentPoseSource(USkeletalMeshComponent* Source, FName Label, double ExteriorHeightCm);
    void SetSmokeGripContact(bool Active) { SmokeGripContactActive=Active; }
    void SetFragGripContact(bool Active) { FragGripContactActive=Active; }
    bool HasEquipmentPoseSource() const { return EquipmentPoseSource.IsValid(); }
    // A separate presentation source: never enters grenade framing/contact code.
    void SetMedicalPoseSource(USkeletalMeshComponent* MedicalSource);
    bool HasMedicalPoseSource() const { return MedicalPoseSource.IsValid(); }
    bool MedicalPoseUses(const USkeletalMeshComponent* MedicalSource) const { return MedicalSource && MedicalPoseSource.Get()==MedicalSource; }
    bool CanPresentMedicalPose() const { return Initialized&&SourceFrameCached&&!ReadyWorkspace.IsEmpty()&&!EquipmentPoseSource.IsValid()&&!MedicalPoseSource.IsValid(); }
protected:
    USkeletalMeshComponent* UnifiedMedicalSource() const { return MedicalPoseSource.Get(); }
    void ApplySmokeGripContact(const FReferenceSkeleton& Ref,TArray<FTransform>& Local) const;
    void ApplyFragGripContact(const FReferenceSkeleton& Ref,TArray<FTransform>& Local) const;
    USkeletalMeshComponent* UnifiedEquipmentSource() const { return EquipmentPoseSource.Get(); }
    FName UnifiedEquipmentLabel() const { return EquipmentPoseLabel; }
    virtual bool AdaptSourceLocalPose(const FReferenceSkeleton& DisplayRef,
        TArray<FTransform>& InOutLocal, FName Action, float DeltaSeconds) override;
    virtual float GetGripWeight(bool Holding) const override { return ExistingGripWeight; }
private:
    bool AdaptMedicalSourcePose(const FReferenceSkeleton& Ref,TArray<FTransform>& Local,float DeltaSeconds);
    TWeakObjectPtr<USkeletalMeshComponent> MedicalPoseSource;
    FTransform MedicalViewFrame=FTransform::Identity;
    bool MedicalFrameCached=false;
    bool AdaptReloadWorkspace(const FReferenceSkeleton& Ref,TArray<FTransform>& Target);
    TArray<FTransform> ReadyWorkspace;
    TArray<FTransform> PreviousSourcePose;
    TArray<FTransform> TransitionFrom;
    FName PreviousAction;
    float TransitionElapsed = .25f;
    float TransitionFromGrip = 1;
    bool SourceFrameCached = false;
    TWeakObjectPtr<USkeletalMeshComponent> EquipmentPoseSource;
    FName EquipmentPoseLabel;
    int32 ThumbProbeMask=-1;
    bool SmokeGripContactActive=false;
    bool FragGripContactActive=false;
    FVector EquipmentRootOffset=FVector::ZeroVector;
    FTransform EquipmentPresentationFrame=FTransform::Identity;
    FTransform EquipmentReleasePresentationFrame=FTransform::Identity;
    bool EquipmentReleaseFrameCached=false;
    FVector EquipmentEntryHandCamera=FVector::ZeroVector;
    float EquipmentEntryElapsed=0;
    bool EquipmentFrameCached=false;
    double EquipmentExteriorHeightCm=0;
};
