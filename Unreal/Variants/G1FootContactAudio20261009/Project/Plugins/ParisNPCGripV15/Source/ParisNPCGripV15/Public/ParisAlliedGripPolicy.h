#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ParisNPCGripV15.h"
#include "ParisAlliedGripPolicy.generated.h"

// One map-level default: reuse the accepted adapter for current and future Allies.
UCLASS()
class PARISNPCGRIPV15_API AParisAlliedGripPolicy : public AActor
{
    GENERATED_BODY()
public:
    AParisAlliedGripPolicy();
    UPROPERTY(EditAnywhere,Category="Allied default") TSubclassOf<class ACharacter> AlliedNPCClass;
    UPROPERTY(EditAnywhere,Category="Allied default") TObjectPtr<UParisNPCGripConfig> BindingConfig;
    UPROPERTY(EditAnywhere,Category="Allied default") TSubclassOf<AActor> RifleAppearanceClass;
    UPROPERTY(EditAnywhere,Category="Allied default") TObjectPtr<class UStaticMesh> RifleMesh;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") int32 RegisteredNPCs=0;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Audit") FString SetupError;
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void Tick(float DeltaSeconds) override;
private:
    void RegisterActor(AActor* Actor);
    bool EnsureRifle(class ACharacter* Soldier);
    UFUNCTION() void OnNPCDestroyed(AActor* Actor);
    FDelegateHandle SpawnHandle;
    TMap<TWeakObjectPtr<class ACharacter>,TWeakObjectPtr<AParisNPCGripActor>> Adapters;
    TMap<TWeakObjectPtr<class ACharacter>,TWeakObjectPtr<AActor>> SpawnedRifles;
    TSet<TWeakObjectPtr<class ACharacter>> ReadyReported;
};
