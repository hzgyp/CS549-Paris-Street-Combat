#pragma once
#include "CoreMinimal.h"
#include "AnimGraphNode_Base.h"
#include "ParisNPCGripV15.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ParisNPCGripV15Editor.generated.h"

UCLASS()
class PARISNPCGRIPV15EDITOR_API UAnimGraphNode_ParisNPCGrip : public UAnimGraphNode_Base
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere,Category="Grip") FAnimNode_ParisNPCGrip Node;
    virtual FText GetNodeTitle(ENodeTitleType::Type T) const override{return FText::FromString(TEXT("Existing NPC grip rotation adapter"));}
    virtual FText GetTooltipText() const override{return GetNodeTitle(ENodeTitleType::FullTitle);}
    virtual FText GetMenuCategory() const override{return FText::FromString(TEXT("Paris"));}
};
UCLASS()
class PARISNPCGRIPV15EDITOR_API UParisNPCGripAssetFactory : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable,Category="Paris|Editor")
    static class UAnimBlueprint* CreateAdapter(class USkeletalMesh* Mesh,const FString& PackagePath,const FString& Json);
};
