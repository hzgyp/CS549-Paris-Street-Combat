#pragma once
#include "CoreMinimal.h"
class AParisBridgePlayerController;
class UWorld;
struct FInputKeyEventArgs;
class FJsonObject;
namespace ParisMedicalKits {
struct FGuidance {
 FString Heading,Action,Detail;
 FVector PouchLocation=FVector::ZeroVector;
 bool HasPouch=false,PickupReady=false;
 float TreatmentProgress=0;
};
bool Guidance(UWorld* W,FGuidance& Out);
void Tick(UWorld* W,float Delta);
void Diagnostics(UWorld* W,float Delta);
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& Args);
void Cancel(UWorld* W);
bool Busy(UWorld* W);
int32 Count(UWorld* W);
FString Hint(UWorld* W);
FString PickupHint(UWorld* W);
float Progress(UWorld* W);
void Capture(UWorld* W,const TSharedPtr<FJsonObject>& Root);
bool Validate(const TSharedPtr<FJsonObject>& Root,FString& Error);
void Restore(UWorld* W,const TSharedPtr<FJsonObject>& Root);
void Shutdown();
}
