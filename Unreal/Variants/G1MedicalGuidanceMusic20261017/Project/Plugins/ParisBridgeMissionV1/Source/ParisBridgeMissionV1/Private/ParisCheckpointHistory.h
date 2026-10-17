#pragma once
#include "CoreMinimal.h"
class AParisBridgeMission;
class AParisBridgePlayerController;
namespace ParisCheckpointHistory {
struct FRecord {FString Id,Name,Utc,Payload,Slot;int32 Serial=0,Allies=0,Loaded=0,Reserve=0,Frag=0,Smoke=0;bool Latest=false,Active=false,Recovered=false;};
bool Enabled();
bool HasIndex(const AParisBridgeMission* M);
TArray<FRecord> List(const AParisBridgeMission* M,FString& Error);
int32 NextSerial(const AParisBridgeMission* M,FString& Error);
bool Save(AParisBridgeMission* M,const FString& Payload,FString& Error);
bool Read(const AParisBridgeMission* M,FString& Payload,int32& Serial,FString& Error);
bool PrepareLoad(AParisBridgeMission* M,const FString& Id,int32 Expected,FString& Error);
bool Delete(AParisBridgeMission* M,const FString& Id,int32 Expected,FString& Error);
void Loaded(AParisBridgeMission* M);
void Restart(AParisBridgeMission* M);
FString Active(const AParisBridgeMission* M);
bool ArmDiagnosticWriteFailure(const FString& Kind);
void Diagnostics(AParisBridgePlayerController* PC);
}
