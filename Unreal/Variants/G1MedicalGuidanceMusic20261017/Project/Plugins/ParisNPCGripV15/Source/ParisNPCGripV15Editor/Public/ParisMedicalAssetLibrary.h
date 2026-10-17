#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ParisMedicalAssetLibrary.generated.h"

UCLASS()
class PARISNPCGRIPV15EDITOR_API UParisMedicalAssetLibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable,Category="Paris|Editor")
 static FString LinkAndAuditMedical(class UAnimSequence* Motion,class USkeleton* Skeleton,class UAnimSequence* Original);
 UFUNCTION(BlueprintCallable,Category="Paris|Editor")
 static FString RestoreMedicalFunctionInputs(class UMaterialExpressionMaterialFunctionCall* Destination,class UMaterialExpressionMaterialFunctionCall* Original,class UMaterialFunctionInterface* NewFunction);
 UFUNCTION(BlueprintCallable,Category="Paris|Editor")
 static FString RebuildMedicalUVDensity(class UStaticMesh* Mesh);
};
