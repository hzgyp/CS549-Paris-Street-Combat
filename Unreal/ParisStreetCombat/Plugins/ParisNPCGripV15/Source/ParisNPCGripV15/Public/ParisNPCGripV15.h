#pragma once
#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimNodeBase.h"
#include "Engine/DataAsset.h"
#include "GameFramework/Actor.h"
#include "BoneContainer.h"
#include "ParisNPCGripV15.generated.h"

USTRUCT(BlueprintType)
struct PARISNPCGRIPV15_API FParisNPCGripRule
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere,Category="Grip") FBoneReference Bone;
    UPROPERTY(EditAnywhere,Category="Grip") FQuat Delta=FQuat::Identity;
    UPROPERTY(EditAnywhere,Category="Grip") FQuat Accepted=FQuat::Identity;
};

USTRUCT(BlueprintInternalUseOnly)
struct PARISNPCGRIPV15_API FAnimNode_ParisNPCGrip : public FAnimNode_Base
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere,Category="Links") FPoseLink InputPose;
    UPROPERTY(EditAnywhere,Category="Grip") TArray<FParisNPCGripRule> Rules;
    UPROPERTY(EditAnywhere,Category="Grip") bool AcceptedHolding=false;
    float HoldingAlpha=0;
    double TranslationError=0,ScaleError=0,ProtectedRotationError=0,AdapterError=0;
    double ProtectedQuatComponentError=0,SourceQuatNormError=0,RawProtectedAngle=0;
    bool HasValidInput=false;
    virtual void Initialize_AnyThread(const FAnimationInitializeContext& Context) override;
    virtual void CacheBones_AnyThread(const FAnimationCacheBonesContext& Context) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
};

UCLASS()
class PARISNPCGRIPV15_API UParisNPCGripAnimInstance : public UAnimInstance
{
    GENERATED_BODY()
public:
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") int64 Evaluations=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") double ProtectionError=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") double ProtectedQuatComponentError=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") double SourceQuatNormError=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") double RawProtectedAngle=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") bool ValidInput=false;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") float HoldingWeight=0;
    virtual void NativePostEvaluateAnimation() override;
protected:
    virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override;
    virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* InProxy) override;
};

UCLASS(BlueprintType)
class PARISNPCGRIPV15_API UParisNPCGripConfig : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere,Category="Grip") TSubclassOf<UAnimInstance> PostProcessClass;
    UPROPERTY(EditAnywhere,Category="Grip",meta=(MultiLine="true")) FString BindingJson;
};

UCLASS()
class PARISNPCGRIPV15_API AParisNPCGripActor : public AActor
{
    GENERATED_BODY()
public:
    AParisNPCGripActor();
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Grip") TObjectPtr<class ACharacter> Target;
    UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Grip") TObjectPtr<UParisNPCGripConfig> BindingConfig;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") bool Initialized=false;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") FString BindingError;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") int64 NativeUpdates=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") double GunErrorCm=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") double GunErrorDegrees=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") int32 PendingEvaluationFrames=0;
    UFUNCTION(BlueprintCallable,Category="Audit") FString ObservationJson() const;
    virtual void Tick(float DeltaSeconds) override;
private:
    bool Bind();
    UPROPERTY() TObjectPtr<class USkeletalMeshComponent> BoundMesh;
    UPROPERTY() TObjectPtr<AActor> BoundGun;
    UPROPERTY() TObjectPtr<class UStaticMeshComponent> GunMesh;
    FTransform GunHand=FTransform::Identity;
    double PendingEvaluationStart=-1;
    struct FObservation {double Time;float Dt,Alpha;FName Action;FTransform Gun,Right,Left;};
    TArray<FObservation> Observations;
};
