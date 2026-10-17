#include "ParisMedicalAssetLibrary.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Animation/AnimData/IAnimationDataModel.h"
#include "Materials/MaterialExpressionMaterialFunctionCall.h"
#include "Materials/MaterialFunctionInterface.h"
#include "Engine/StaticMesh.h"

FString UParisMedicalAssetLibrary::RebuildMedicalUVDensity(UStaticMesh* Mesh){
 if(!Mesh||Mesh->GetPathName()!=TEXT("/Game/ParisCombat/Props/MedicalPouch20261017V2/SM_MedicalPouch.SM_MedicalPouch"))return TEXT("fail mesh identity");
 Mesh->UpdateUVChannelData(true);
 for(const auto& Slot:Mesh->GetStaticMaterials())if(!Slot.UVChannelData.bInitialized)return TEXT("fail UV density uninitialized");
 Mesh->MarkPackageDirty();return FString::Printf(TEXT("pass rebuilt UV streaming density slots=%d"),Mesh->GetStaticMaterials().Num());
}

FString UParisMedicalAssetLibrary::RestoreMedicalFunctionInputs(UMaterialExpressionMaterialFunctionCall* Destination,UMaterialExpressionMaterialFunctionCall* Original,UMaterialFunctionInterface* NewFunction){
 if(!Destination||!Original||!NewFunction||!Destination->GetPathName().StartsWith(TEXT("/Game/ParisCombat/Props/MedicalPouch20261017V2/RuntimeMaterialsV2/"))||!Original->GetPathName().StartsWith(TEXT("/InterchangeAssets/")))return TEXT("fail private repair identity");
 TMap<FName,FExpressionInput> Inputs;
 for(int32 I=0;I<Original->FunctionInputs.Num();++I)Inputs.Add(Original->GetInputNameWithType(I,false),Original->FunctionInputs[I].Input);
 if(!Destination->SetMaterialFunction(NewFunction))return TEXT("fail function setter");
 int32 Connected=0;
 for(int32 I=0;I<Destination->FunctionInputs.Num();++I){
  const auto* Saved=Inputs.Find(Destination->GetInputNameWithType(I,false));if(!Saved){FString Names;for(const auto& Pair:Inputs)Names+=Pair.Key.ToString()+TEXT(";");return FString::Printf(TEXT("fail input name mismatch original=%s new=%s original_count=%d new_count=%d expression=%s"),*Names,*Destination->GetInputNameWithType(I,false).ToString(),Original->FunctionInputs.Num(),Destination->FunctionInputs.Num(),*Original->GetPathName());}
  FExpressionInput Value=*Saved;
  if(Value.Expression){
   auto* Peer=FindObject<UMaterialExpression>(Destination->GetOuter(),*Value.Expression->GetName());
   if(!Peer||Peer->GetClass()!=Value.Expression->GetClass())return TEXT("fail cloned expression identity");
   Value.Expression=Peer;++Connected;
  }
  Destination->FunctionInputs[I].Input=Value;
 }
 Destination->MarkPackageDirty();
 return FString::Printf(TEXT("pass restored named inputs=%d connected=%d"),Destination->FunctionInputs.Num(),Connected);
}

FString UParisMedicalAssetLibrary::LinkAndAuditMedical(UAnimSequence* Motion,USkeleton* Skeleton,UAnimSequence* Original){
 if(!Motion||!Skeleton||!Original||!Original->GetSkeleton())return TEXT("fail missing object");
 if(Motion->GetPathName()!=TEXT("/Game/ParisCombat/Animations/Medical20261017/AS_PC_HealBandages.AS_PC_HealBandages")||
    Skeleton->GetPathName()!=TEXT("/Game/ParisCombat/Animations/Medical20261017/SKEL_PC_Medical.SKEL_PC_Medical"))return TEXT("fail target identity");
 if(!Original->GetPathName().EndsWith(TEXT("/UE4M_Heal_bandages_Anim.UE4M_Heal_bandages_Anim")))return TEXT("fail original identity");
 const auto& A=Original->GetSkeleton()->GetReferenceSkeleton();const auto& B=Skeleton->GetReferenceSkeleton();
 if(A.GetNum()!=B.GetNum())return TEXT("fail hierarchy size");
 for(int I=0;I<A.GetNum();++I)if(A.GetBoneName(I)!=B.GetBoneName(I)||A.GetParentIndex(I)!=B.GetParentIndex(I)||!A.GetRefBonePose()[I].Equals(B.GetRefBonePose()[I],0))return TEXT("fail skeleton identity");
 Motion->Modify();Skeleton->Modify();Motion->SetSkeleton(Skeleton);Motion->SetPreviewMesh(nullptr);Skeleton->SetPreviewMesh(nullptr);Skeleton->SetAdditionalPreviewSkeletalMeshes(nullptr);
 // Named retarget reference poses keep their transforms; editor source-mesh hints are not runtime dependencies.
 for(auto& Pair:Skeleton->AnimRetargetSources)Pair.Value.SourceReferenceMesh.Reset();
 auto* O=Original->GetDataModel();auto* M=Motion->GetDataModel();
 if(!O||!M||O->GetNumberOfKeys()!=M->GetNumberOfKeys()||O->GetNumberOfFrames()!=M->GetNumberOfFrames()||Original->GetPlayLength()!=Motion->GetPlayLength()||Motion->HasRootMotion())return TEXT("fail duration/model/root motion");
 TArray<FName> ON,MN;O->GetBoneTrackNames(ON);M->GetBoneTrackNames(MN);if(ON!=MN||ON.IsEmpty())return TEXT("fail track names");
 int32 Samples=0;
 for(const FName Name:ON){TArray<FTransform> X,Y;O->GetBoneTrackTransforms(Name,X);M->GetBoneTrackTransforms(Name,Y);if(X.Num()!=Y.Num())return TEXT("fail track size");for(int I=0;I<X.Num();++I){if(!X[I].Equals(Y[I],0))return TEXT("fail original motion changed");++Samples;}}
 Motion->PostEditChange();Skeleton->PostEditChange();Motion->MarkPackageDirty();Skeleton->MarkPackageDirty();
 return FString::Printf(TEXT("pass original_motion_exact bones=%d tracks=%d samples=%d duration=%.9f keys=%d root_motion=0"),B.GetNum(),ON.Num(),Samples,Motion->GetPlayLength(),M->GetNumberOfKeys());
}
