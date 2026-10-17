#pragma once
#include "CoreMinimal.h"
class AActor;
class AParisFirstPersonApprovedActor;
class USkinnedMeshComponent;
class UStaticMeshComponent;
class UPoseableMeshComponent;
struct FParisUnifiedPresentation {
 TWeakObjectPtr<AActor> Actor;
 TWeakObjectPtr<UPoseableMeshComponent> Body;
 TWeakObjectPtr<UStaticMeshComponent> Rifle;
 TMap<TWeakObjectPtr<AActor>,bool> HiddenLegacyRifles;
 bool Observer=false,RifleVisible=true,OriginalHidden=false,OriginalOwnerNoSee=true;
 FTransform Recoil=FTransform::Identity;
 double MaxLengthError=0,RecoilHandDelta=0;
 int64 Frame=0;
 uint8 OriginalAnimTick=0;
 FName PoseKey;double TransitionAt=0;TArray<FTransform> PreviousPose,TransitionFrom;
};

// One action/lifecycle authority. Views adapt its space, never own a second clock.
namespace ParisActionBindings {
PARISGRIPBINDINGV18_API AParisFirstPersonApprovedActor* Display(AActor* Player);
PARISGRIPBINDINGV18_API void SetObserver(AActor* Player,bool Observer);
PARISGRIPBINDINGV18_API void SetRifleVisible(AActor* Player,bool Visible);
PARISGRIPBINDINGV18_API USkinnedMeshComponent* VisibleBody(AActor* Player);
PARISGRIPBINDINGV18_API UStaticMeshComponent* VisibleRifle(AActor* Player);
PARISGRIPBINDINGV18_API const TCHAR* RecoilClip();
PARISGRIPBINDINGV18_API FString GrenadeClip(FName Stage,bool EquippedDisplay);
}
