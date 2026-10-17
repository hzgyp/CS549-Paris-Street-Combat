#pragma once
#include "CoreMinimal.h"
#include "UObject/StrongObjectPtr.h"
#include "Dom/JsonObject.h"
class ACharacter;
class AActor;
class AParisBridgeMission;
class USkeletalMeshComponent;
class USkinnedMeshComponent;
class UAnimSequence;
class UAnimInstance;
class UParisEquipmentSightBridge;
class UAudioComponent;
class USoundWaveProcedural;
class UParticleSystemComponent;
class UBoxComponent;
class UMaterialInstanceDynamic;
namespace ParisTacticalEquipment {
// Optional presentation state; Position in FSmoke remains the concealment anchor.
struct FSmokePose {
    FVector Position=FVector::ZeroVector,Scale=FVector::OneVector;
    FVector Linear=FVector::ZeroVector,Angular=FVector::ZeroVector;
    FQuat Rotation=FQuat::Identity;
    bool Sleeping=false,Valid=false;
};
struct FBall {
    FString Id,Kind;
    FVector Position,Velocity;
    double Fuse=3.5,Age=0;
    FSmokePose SmokePose;
    TWeakObjectPtr<UBoxComponent> SmokeBody;
    TWeakObjectPtr<AActor> Visual;
};
struct FSmoke {
    FString Id;
    FVector Position;
    double Life=18;
    FSmokePose Pose;
    TWeakObjectPtr<UBoxComponent> Body;
    TWeakObjectPtr<UMaterialInstanceDynamic> Material;
    bool EmissionStopped=false;
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
    FVector Position=FVector::ZeroVector;
    int32 Remaining=16,FragRemaining=2,SmokeRemaining=2;
    bool Retired=false; // retained save identity, no world prop or target
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
    bool ConsolidatedSupply=false,SupplyTutorialConfirmed=false;
    int32 Frag=2,Smoke=2,FragThrown=0,SmokeThrown=0,Grant=0,FragGrant=0,SmokeGrant=0;
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
    // Transient observer accessory only; never serialized.
    TWeakObjectPtr<AActor> StowedFrag;
    TWeakObjectPtr<USkinnedMeshComponent> StowBody;
    bool StowSectionWasShown=true;
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
