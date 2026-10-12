#pragma once
#include "CoreMinimal.h"
#include "UObject/StrongObjectPtr.h"
#include "Dom/JsonObject.h"
class ACharacter;
class AActor;
class AParisBridgeMission;
class USkeletalMeshComponent;
class UAnimSequence;
class UAnimInstance;
class UParisEquipmentSightBridge;
class UAudioComponent;
class USoundWaveProcedural;
class UParticleSystemComponent;
namespace ParisTacticalEquipment {
struct FBall {
    FString Id,Kind;
    FVector Position,Velocity;
    double Fuse=3.5,Age=0;
    TWeakObjectPtr<AActor> Visual;
};
struct FSmoke {
    FString Id;
    FVector Position;
    double Life=18;
    TWeakObjectPtr<AActor> Visual;
    TWeakObjectPtr<UParticleSystemComponent> Effect;
};
struct FTrap {
    FString Id,State=TEXT("Armed");
    FVector Position;
    bool Discovered=false;
    TWeakObjectPtr<AActor> Visual;
};
struct FSupply {
    FString Id;
    FVector Position;
    int32 Remaining=16;
    TWeakObjectPtr<AActor> Visual;
};
struct FEvade {
    TWeakObjectPtr<ACharacter> Pawn;
    double Until=0;
    bool Paused=false,PreviousHold=false;
    double PreviousGeneration=-1;
};
struct FEquipmentSession {
    FString Generation;
    bool Initialized=false,Restored=false;
    int32 Frag=2,Smoke=2,FragThrown=0,SmokeThrown=0,Grant=0;
    TArray<FBall> Balls;
    TArray<FSmoke> Clouds;
    TArray<FTrap> Traps;
    TArray<FSupply> Supplies;
    TArray<TStrongObjectPtr<UParisEquipmentSightBridge>> Bridges;
    TArray<FEvade> Evades;
    FString ThrowKind,ThrowStage,InteractId,Notice;
    double ActionClock=0,DisarmClock=0,NoticeUntil=0;
    bool ReleaseQueued=false,ThrowCommitted=false,EHeld=false;
    int32 SelectedSlot=0; // 0 rifle, 1 frag, 2 smoke; transient, never serialized
    bool PrimaryHeld=false,SuppressPrimary=false,HadWindowFocus=false;
    FString SelectedVisualKind;
    TWeakObjectPtr<AActor> SelectedVisual;
    TWeakObjectPtr<USkeletalMeshComponent> EquipmentPoseSource;
    FString EquipmentPoseTag;
    int32 OriginalAnimMode=0;
    TWeakObjectPtr<UClass> OriginalAnimClass;
    TWeakObjectPtr<AActor> Held;
    TWeakObjectPtr<AActor> Rifle;
    TStrongObjectPtr<UAnimSequence> ThrowClip;
    TArray<TStrongObjectPtr<USoundWaveProcedural>> Waves;
    TArray<TWeakObjectPtr<UAudioComponent>> Voices;
    TArray<TSharedPtr<FJsonValue>> Events;
};
FEquipmentSession& Session(UWorld* World);
bool ValidateEquipment(const TSharedPtr<FJsonObject>& Root,FString& Error);
void CaptureEquipment(UWorld* World,const TSharedPtr<FJsonObject>& Root);
void RestoreEquipment(UWorld* World,const TSharedPtr<FJsonObject>& Root);
double ValidatedGrant(const TSharedPtr<FJsonObject>& Root,int32 ActorIndex);
void ClearVisuals(FEquipmentSession& State);
void CreateVisuals(UWorld* World,FEquipmentSession& State);
}
