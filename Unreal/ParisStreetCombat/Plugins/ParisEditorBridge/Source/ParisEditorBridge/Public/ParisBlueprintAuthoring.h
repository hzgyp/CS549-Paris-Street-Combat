#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ParisBlueprintAuthoring.generated.h"

class ACharacter;
class USkeletalMesh;
class UAnimBlueprint;

/** Authoring/testing only. Generated graphs never call this class. */
UCLASS()
class PARISEDITORBRIDGE_API UParisBlueprintAuthoring : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
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
