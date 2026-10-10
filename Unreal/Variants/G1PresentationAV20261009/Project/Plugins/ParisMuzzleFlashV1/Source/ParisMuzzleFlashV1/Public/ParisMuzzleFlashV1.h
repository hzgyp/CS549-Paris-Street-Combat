#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Engine/EngineBaseTypes.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Subsystems/WorldSubsystem.h"
#include "TimerManager.h"
#include "ParisMuzzleFlashV1.generated.h"

class UNiagaraSystem;
class UNiagaraComponent;
class UStaticMesh;
class UStaticMeshComponent;
class UTextureRenderTarget2D;

USTRUCT(BlueprintType)
struct PARISMUZZLEFLASHV1_API FParisMuzzleCaptureFrame
{
    GENERATED_BODY()
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") int64 Frame = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") double WorldTime = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") int64 ShotSequence = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") int32 Started = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") int32 LiveCount = 0;
};

// Diagnostic capture preserves owner-only presentation instead of disabling it.
UCLASS()
class PARISMUZZLEFLASHV1_API UParisMuzzleReviewCapture : public USceneCaptureComponent2D
{
    GENERATED_BODY()
public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") TObjectPtr<AActor> ReviewViewOwner;
    virtual const AActor* GetViewOwner() const override { return ReviewViewOwner; }
    UFUNCTION(BlueprintCallable, Category="Muzzle Review") bool ArmDeferredReview(AActor* Target, const TArray<UTextureRenderTarget2D*>& Targets);
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") TArray<FParisMuzzleCaptureFrame> CaptureRecords;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") FString CaptureError;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") bool ReviewArmed = false;
    virtual void OnUnregister() override;
    virtual void BeginDestroy() override;
private:
    UPROPERTY() TArray<TObjectPtr<UTextureRenderTarget2D>> ReviewTargets;
    TWeakObjectPtr<AActor> ReviewTarget;
    FDelegateHandle CaptureDelegate;
    void DeferredWorldFrame(UWorld* World, ELevelTick TickType, float DeltaSeconds);
    void StopDeferredReview();
};

// Measured supplier-mesh coordinates belong in a private native profile, not
// public source, accepted grip constants, or authoritative combat logic.
USTRUCT(BlueprintType)
struct PARISMUZZLEFLASHV1_API FParisRifleMuzzleProfile
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Muzzle Profile") TObjectPtr<UStaticMesh> RifleMesh;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Muzzle Profile") FTransform MuzzleLocal;
};

UCLASS(BlueprintType)
class PARISMUZZLEFLASHV1_API UParisMuzzleFlashProfile : public UDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Muzzle Profile") TObjectPtr<UNiagaraSystem> Effect;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Muzzle Profile") TArray<FParisRifleMuzzleProfile> Rifles;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Muzzle Profile") float MaximumLifetimeSeconds = 8;
};

USTRUCT(BlueprintType)
struct PARISMUZZLEFLASHV1_API FParisMuzzleTargetObservation
{
    GENERATED_BODY()
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") TObjectPtr<AActor> Target;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") TObjectPtr<UStaticMeshComponent> VisibleRifle;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") int64 LastSequence = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") int64 Generation = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") int32 Started = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") int32 Completed = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") int32 Cancelled = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") int32 TimedOut = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") int32 MissedSequences = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") int32 LiveCount = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") FString Error;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") FTransform VisualMuzzle;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") FVector LegacyShotMuzzle = FVector::ZeroVector;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") double LatestShotTime = -1;
};

// No input/AI/action/mesh/pose writer. Game-world lifetime owns only its effects.
UCLASS(BlueprintType)
class PARISMUZZLEFLASHV1_API UParisMuzzleFlashSubsystem : public UTickableWorldSubsystem
{
    GENERATED_BODY()
public:
    virtual bool DoesSupportWorldType(EWorldType::Type WorldType) const override;
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    virtual void Tick(float DeltaTime) override;
    virtual TStatId GetStatId() const override;
    UFUNCTION(BlueprintCallable, Category="Muzzle Candidate") bool ConfigurePrivateCandidate(UParisMuzzleFlashProfile* InProfile);
    UFUNCTION(BlueprintPure, Category="Muzzle Observation") TArray<UNiagaraComponent*> GetOwnedComponents() const;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") TObjectPtr<UParisMuzzleFlashProfile> Profile;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") TArray<FParisMuzzleTargetObservation> Observations;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Observation") FString State = TEXT("WaitingForVerifiedPrivateProfile");
private:
    struct FOwnedEffect
    {
        TWeakObjectPtr<UNiagaraComponent> Component;
        TWeakObjectPtr<AActor> Target;
        double Born = 0;
        FTimerHandle StopTimer;
    };
    TArray<FOwnedEffect> Effects;
    double NextDiscovery = 0;
    void DiscoverTargets();
    void Cancel(AActor* Target);
};

// Diagnostic object is outside the dying world; only weak references are kept.
UCLASS(BlueprintType)
class PARISMUZZLEFLASHV1_API UParisMuzzleLifetimeProbe : public UObject
{
    GENERATED_BODY()
public:
    TWeakObjectPtr<UParisMuzzleFlashSubsystem> TrackedSubsystem;
    TArray<TWeakObjectPtr<UNiagaraComponent>> TrackedComponents;
    UFUNCTION(BlueprintCallable, Category="Muzzle Observation") int32 TrackOwnedEffects();
    UFUNCTION(BlueprintPure, Category="Muzzle Observation") FString InspectLifetime() const;
};

// Diagnostic-only original transaction request, not a runtime input/AI driver.
// No strong world/target refs, state writes, effect spawning or recurring tick.
UCLASS(BlueprintType)
class PARISMUZZLEFLASHV1_API UParisMuzzleReviewFireBatch : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") bool Executed = false;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") FString Error;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") TArray<int64> SequenceDeltas;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") int64 SequenceBefore = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") int64 SequenceAfter = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") int64 DispatchFrame = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") double QueuedWorldTime = -1;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Muzzle Review") double DispatchWorldTime = -1;
    bool Queue(AActor* InTarget, int32 InRequests);
    virtual void BeginDestroy() override;
private:
    TWeakObjectPtr<AActor> Target;
    TWeakObjectPtr<UWorld> ReviewWorld;
    int32 Requests = 0;
    FDelegateHandle PreActorHandle;
    void Dispatch(UWorld* World, ELevelTick TickType, float DeltaSeconds);
};

UCLASS()
class PARISMUZZLEFLASHV1_API UParisMuzzleFlashLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintPure, Category="Muzzle Observation") static UParisMuzzleFlashSubsystem* GetPresentationSubsystem(UObject* WorldContext);
    UFUNCTION(BlueprintCallable, Category="Muzzle Observation") static UParisMuzzleLifetimeProbe* CreateLifetimeProbe(UObject* WorldContext);
    UFUNCTION(BlueprintCallable, Category="Muzzle Review") static UParisMuzzleReviewFireBatch* QueueReviewFire(AActor* Target, int32 Requests);
    UFUNCTION(BlueprintCallable, Category="Purchased Muzzle Diagnostics") static UParisMuzzleReviewCapture* CreateReviewCapture(AActor* ViewOwner);
    UFUNCTION(BlueprintCallable, Category="Purchased Muzzle Diagnostics") static FString InspectPurchasedSystem(UNiagaraSystem* System);
    UFUNCTION(BlueprintCallable, Category="Purchased Muzzle Diagnostics") static bool RequestPurchasedCompile(UNiagaraSystem* System);
    UFUNCTION(BlueprintCallable, Category="Purchased Muzzle Diagnostics") static FString InspectPurchasedComponent(UNiagaraComponent* Component);
    UFUNCTION(BlueprintCallable, Category="Purchased Muzzle Diagnostics") static FString InspectRifleGeometry(UStaticMesh* Mesh);
    UFUNCTION(BlueprintCallable, Category="Purchased Muzzle Candidate") static UNiagaraComponent* SpawnMeasuredPulse(UNiagaraSystem* System, UStaticMeshComponent* Rifle, FTransform Local);
};
