#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ParisBlueprintAuthoring.generated.h"

class ACharacter;
class USkeletalMesh;
class UAnimBlueprint;
class UBlueprint;

/** Authoring/testing only. Generated graphs never call this class. */
UCLASS()
class PARISEDITORBRIDGE_API UParisBlueprintAuthoring : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    /** New unselected player upper-spine aim AnimBP only; standard node, no save/runtime use. */
    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString AddPlayerAimLayer(UAnimBlueprint* Blueprint, FVector LocalAimAxis);

    /** Bounded trial: common rigid upper-body rotation, no local finger pose edits. */
    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString AddPlayerRigidAimLayer(UAnimBlueprint* Blueprint, FVector LocalAimAxis);

    /** New owner-view copy only. Standard node; never changes a source pose or saves. */
    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString BuildFirstPersonCopyPose(UAnimBlueprint* Blueprint);

    /** Exact unselected AlliedGripV1 AnimBP only. Standard nodes; no save/runtime use. */
    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString AddAlliedGripLayer(UAnimBlueprint* Blueprint);

    /** New, unsaved CityGameplayV1 widget template only; no runtime use/save. */
    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static bool CreateStatusWidgetTemplate(UBlueprint* Blueprint);

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static bool ClearSkeletonPreviewAttachments(const FString& SkeletonPath);

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString CreateSimplifiedReloadDraft();

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString ProbeSimplifiedReload(const FString& ClassPath, double PlaybackRate, int32 FramesPerSecond);

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString DescribeReferenceSkeleton(const FString& MeshPath);

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString CompareTranslationModes(const FString& MeshPath, const FString& ClipPath);

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString CreateGermanTranslationDraft();

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString CreateDirectionalDraft();

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString CreateLifecycleDraft();

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString CreateStrideDraft();

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString ProbeLifecycle(const FString& ClassPath, const FString& AnimationPath = "");

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString CreateMovementDraft();

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString ConfigureDraftCharacter(ACharacter* Character, USkeletalMesh* Mesh, UAnimBlueprint* Animation);

    UFUNCTION(BlueprintCallable, Category="Paris|Editor")
    static FString ProbeMovement(const FString& CharacterClassPath, int32 FramesPerSecond,
        const FString& MeshPath, const FString& AnimationBlueprintPath);
};
