#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameFramework/Actor.h"
#include "ParisGripV18Actor.generated.h"

class UCameraComponent;
class USkeletalMeshComponent;
class UPoseableMeshComponent;
class UStaticMeshComponent;
class USkeletalMesh;
class UStaticMesh;
struct FReferenceSkeleton;

// Private asset payload, never commercial pose constants embedded in public code.
UCLASS(BlueprintType)
class PARISGRIPBINDINGV18_API UParisGripV18Config : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Grip") FString BindingJson;
};

// Display-only: does not own input, animation selection or weapon transactions.
UCLASS(BlueprintType)
class PARISGRIPBINDINGV18_API AParisGripV18Actor : public AActor
{
    GENERATED_BODY()
public:
    AParisGripV18Actor();
    virtual void Tick(float DeltaSeconds) override;

    UFUNCTION(BlueprintCallable, Category="Grip")
    bool BindExistingPose(AActor* InCombatant, USkeletalMeshComponent* InSource,
        UCameraComponent* InCamera, AActor* OriginalVisibleGun,
        USkeletalMesh* DisplayMesh, UStaticMesh* GunMesh, UParisGripV18Config* Config);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") TObjectPtr<UPoseableMeshComponent> Pose;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") TObjectPtr<UStaticMeshComponent> Gun;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") bool Initialized = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") FString BindingError;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") FName ObservedAction;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") int32 NativePoseUpdates = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") double SupportErrorCm = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") double LimbLengthErrorCm = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") double FingerRotationErrorDegrees = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") FTransform CachedAssemblyFrame;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Grip") float HoldingAppliedAlpha = 0;

protected:
    // Default is exact V18 behavior. New source adapters have separate identities.
    virtual bool AdaptSourceLocalPose(const FReferenceSkeleton& DisplayRef,
        TArray<FTransform>& InOutLocal, FName Action, float DeltaSeconds) { return true; }
    virtual float GetGripWeight(bool Holding) const { return Holding ? 1.f : 0.f; }

private:
    UPROPERTY() TObjectPtr<AActor> Combatant;
    UPROPERTY() TObjectPtr<USkeletalMeshComponent> Source;
    TArray<int32> SourceIndices;
    TArray<int32> Parents;
    TArray<FTransform> Local;
    TArray<FTransform> Component;
    TMap<int32, FQuat> HoldingRotations;
    FTransform GunInHand;
    FTransform SupportInRight;
    FVector PoleInRight = FVector::ZeroVector;
    int32 HandR = INDEX_NONE, HandL = INDEX_NONE, UpperL = INDEX_NONE, LowerL = INDEX_NONE;
    int32 PinkyDistal = INDEX_NONE;
    double PinkyScale = 1;
    float NativeDeltaSeconds = 0;
    bool UpdateNativePose();
    void RebuildComponents();
};
