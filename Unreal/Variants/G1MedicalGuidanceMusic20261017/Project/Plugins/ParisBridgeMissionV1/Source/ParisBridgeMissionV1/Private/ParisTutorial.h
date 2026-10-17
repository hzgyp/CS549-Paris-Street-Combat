#pragma once
#include "CoreMinimal.h"
class AParisBridgeMission;
class ACharacter;
class AParisBridgePlayerController;
struct FInputKeyEventArgs;
class FJsonObject;
namespace ParisTacticalEquipment {struct FEquipmentSession;}
namespace ParisTutorial {
bool Enabled();
FVector PlayerStartFeet();
bool InitialPlayerTransform(ACharacter* Original,FTransform& Transform,FString& Error);
bool HasGuidanceGoal(const AParisBridgeMission* M);
void StartupDiagnostics(AParisBridgeMission* M);
void StartupHUD(AParisBridgeMission* M,bool Covered);
bool PrepareNavigation(AParisBridgeMission* M,FString& Error);
bool ApplyLayout(AParisBridgeMission* M,const TArray<TObjectPtr<ACharacter>>& Roster,FString& Error);
void Ready(AParisBridgeMission* M);
void ConfigureReady(AParisBridgeMission* M);
void ClearWorld(UWorld* W);
void SetInitialBudget(ACharacter* Player);
bool StartTraining(AParisBridgeMission* M);
bool TickTraining(AParisBridgeMission* M,float Delta);
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& Input);
bool CombatStarted(const AParisBridgeMission* M);
void OpenCombat(AParisBridgeMission* M);
bool BrainAllowed(const ACharacter* C);
bool CombatantActive(const ACharacter* C);
bool TrainingCheckpoint(const AParisBridgeMission* M);
bool TrainingCheckpointSaved(const AParisBridgeMission* M);
bool TrainingCheckpointUnlocked(const AParisBridgeMission* M);
bool ForwardDeparture(const AParisBridgeMission* M);
void FlowDiagnostics(AParisBridgePlayerController* PC);
bool DialogVisible(const AParisBridgeMission* M);
FVector CheckpointFeet(const AParisBridgeMission* M);
FVector Goal(const AParisBridgeMission* M);
FString Heading(const AParisBridgeMission* M);
FString Guidance(const AParisBridgeMission* M);
FString KeyHint(const AParisBridgeMission* M);
FString HudStatus(const AParisBridgeMission* M);
FString HudInstruction(const AParisBridgeMission* M);
FString DialogName(const AParisBridgeMission* M);
int DialogChoice(const AParisBridgeMission* M);
bool LargePrompt(const AParisBridgeMission* M);
int Step(const AParisBridgeMission* M);
int JoinedCount(const AParisBridgeMission* M);
bool SupplyAllowed(UWorld* W,const FString& Id);
void InitializeEquipment(UWorld* W,ParisTacticalEquipment::FEquipmentSession& S);
FVector SiteXY(bool Trap,int Index);
void Capture(const AParisBridgeMission* M,const TSharedPtr<FJsonObject>& Root);
void PrepareSavedState(const AParisBridgeMission* M,const TSharedPtr<FJsonObject>& Root);
bool Validate(const AParisBridgeMission* M,const TSharedPtr<FJsonObject>& Root,const TArray<TObjectPtr<ACharacter>>& Roster,const TArray<FVector>& Initial,const TArray<int64>& Shots,FString& Error);
bool ValidateEquipment(const TSharedPtr<FJsonObject>& Root,FString& Error);
void Restore(AParisBridgeMission* M,const TSharedPtr<FJsonObject>& Root);
void Saved(AParisBridgeMission* M);
void Diagnostics(AParisBridgeMission* M,float Delta);
}
