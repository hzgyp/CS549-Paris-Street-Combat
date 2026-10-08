#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SaveGame.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ParisBridgeMission.generated.h"

class ACharacter;
class UBehaviorTree;
class AAIController;

UCLASS()
class PARISBRIDGEMISSIONV1_API UParisBridgeMissionLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="G1 Mission") static bool UpdateBridgeSquad(AAIController* Controller);
};

UCLASS()
class PARISBRIDGEMISSIONV1_API UParisBridgeSave : public USaveGame
{
    GENERATED_BODY()
public:
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="G1 Save") FString Payload;
    UPROPERTY(SaveGame, EditAnywhere, BlueprintReadWrite, Category="G1 Save") FString Checksum;
};

UCLASS()
class PARISBRIDGEMISSIONV1_API AParisBridgeMission : public AActor
{
    GENERATED_BODY()
public:
    AParisBridgeMission();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    UFUNCTION(BlueprintCallable, Category="G1 Mission") bool StartMission();
    UFUNCTION(BlueprintCallable, Category="G1 Mission") bool SaveCheckpoint();
    UFUNCTION(BlueprintCallable, Category="G1 Mission") bool LoadCheckpoint();
    UFUNCTION(BlueprintCallable, Category="G1 Mission") void RestartMission();
    UFUNCTION(BlueprintPure, Category="G1 Mission") bool AllowsPlay() const;
    UFUNCTION(BlueprintPure, Category="G1 Mission") FString ReadMissionState() const;
    UFUNCTION(BlueprintPure, Category="G1 Mission") FString InspectCheckpointJournal() const;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Mission") FVector FarBankFeet = FVector(5837.5, -20237.5, 110.150006);
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Mission") FVector BridgeheadFeet = FVector(7087.5, -20287.5, 132.783997);
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Mission") double ReachRadius = 250;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Mission") double OccupyRadius = 350;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Mission") FString MissionMap = TEXT("/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Mission") FString ConfigFingerprint = TEXT("G1V1_20261008_original703_roster6_v1");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Mission") FString SlotPrefix = TEXT("ParisG1V1");
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="G1 Mission") TObjectPtr<UBehaviorTree> RetainedTree;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Mission") FString Phase = TEXT("Preparing");
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Mission") FString Feedback;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Mission") FString RunGeneration;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Mission") int32 LivingDefenders = 3;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Mission") int32 LivingAllies = 2;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Mission") double ReadySeconds = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Mission") int32 SaveSerial = 0;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="G1 Mission") FString VerifiedRestoreState;
    static AParisBridgeMission* Find(const UObject* Context);
    bool UpdateBridgeSquad(AAIController* Controller);
private:
    UPROPERTY() TArray<TObjectPtr<ACharacter>> Roster;
    TArray<FString> StableIds;
    TSet<FString> DeathLedger;
    double PreparationSeconds = 0;
    double BootstrapClock = 0;
    double SafeSeconds = 0;
    bool bRegistrySealed = false;
    bool bLoadRequested = false;
    bool bTravelPending = false;
    bool bReleased = false;
    TArray<int64> InitialShots;
    TArray<FVector> InitialResources;
    TArray<FVector> InitialLocations;
    TArray<FVector> BridgePath;
    TArray<double> BridgeArcs;
    bool bBridgeTransitArmed = false;
    bool bBridgeTransitComplete = false;
    bool BuildBridgePath(FString& Error);
    bool SealRegistry(FString& Error);
    bool EquipmentReady(FString& Error);
    void GateBrains(bool bEnable);
    void SetPhase(const FString& Value);
    void Fail(const FString& Reason);
    bool IsSafeBoundary(FString& Reason) const;
    bool ValidateSnapshot(const FString& Payload, FString& Error) const;
    bool ReadLatest(FString& Payload, int32& Serial, FString& Error) const;
    bool ApplySnapshot(const FString& Payload, FString& Error);
    FString CaptureSnapshot(int32 Serial) const;
};

UCLASS()
class PARISBRIDGEMISSIONV1_API AParisBridgePlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    virtual bool InputKey(const FInputKeyEventArgs& Params) override;
    UFUNCTION(Exec) void MissionStart();
    UFUNCTION(Exec) void MissionSave();
    UFUNCTION(Exec) void MissionLoad();
    UFUNCTION(Exec) void MissionRestart();
private:
    bool bMissionControlHeld = false;
};

UCLASS()
class PARISBRIDGEMISSIONV1_API AParisBridgeHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
};

UCLASS()
class PARISBRIDGEMISSIONV1_API AParisBridgeGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    AParisBridgeGameMode();
};
