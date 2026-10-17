#include "ParisNPCGripV15Editor.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/MorphTarget.h"
#include "Rendering/SkeletalMeshModel.h"
#include "Rendering/SkeletalMeshLODModel.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "SkeletalMeshAttributes.h"
#include "MeshDescription.h"

FString UParisNPCGripAssetFactory::AddThumbCorrectives(USkeletalMesh* Mesh,const FString& Json)
{
 TSharedPtr<FJsonObject> Data;
 if(!Mesh||!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json),Data))return TEXT("invalid input");
 auto* Model=Mesh->GetImportedModel();
 if(!Model||Model->LODModels.Num()!=1||Mesh->GetMorphTargets().Num()!=0)return TEXT("expected unchanged single LOD mesh without morphs");
 auto& LOD=Model->LODModels[0];TArray<FSoftSkinVertex> V;LOD.GetVertices(V);
 const auto& Rest=Data->GetArrayField(TEXT("rest_cm"));
 auto Vec=[](const TSharedPtr<FJsonValue>& X){const auto& A=X->AsArray();return FVector3f(A[0]->AsNumber(),A[1]->AsNumber(),A[2]->AsNumber());};
 TArray<int32> Map;double MaxError=0;
 for(const auto& P:V){double Best=1e30;int32 N=-1;for(int32 J=0;J<Rest.Num();++J){double E=FVector3f::DistSquared(P.Position,Vec(Rest[J]));if(E<Best){Best=E;N=J;}}if(Best>FMath::Square(.002))return FString::Printf(TEXT("rest correspondence failed %.9f"),FMath::Sqrt(Best));Map.Add(N);MaxError=FMath::Max(MaxError,FMath::Sqrt(Best));}
 auto* MD=Mesh->GetMeshDescription(0);if(!MD)return TEXT("native mesh description absent");
 FSkeletalMeshAttributes Attr(*MD);const auto Positions=Attr.GetVertexPositions();TMap<FVertexID,int32> SourceMap;
 for(const FVertexID ID:MD->Vertices().GetElementIDs()){double Best=1e30;int32 N=-1;for(int32 J=0;J<Rest.Num();++J){double E=FVector3f::DistSquared(Positions[ID],Vec(Rest[J]));if(E<Best){Best=E;N=J;}}if(Best>FMath::Square(.002))return TEXT("mesh description correspondence failed");SourceMap.Add(ID,N);}
 {
 FScopedSkeletalMeshPostEditChange PostEdit(Mesh);
 for(const auto& R:Data->GetArrayField(TEXT("records"))){const auto O=R->AsObject();const auto& D=O->GetArrayField(TEXT("delta_cm"));if(D.Num()!=Rest.Num())return TEXT("delta count mismatch");const FName Name(*O->GetStringField(TEXT("key")));if(!Attr.RegisterMorphTargetAttribute(Name,false))return TEXT("source morph registration failed");auto Delta=Attr.GetVertexMorphPositionDelta(Name);for(const auto& X:SourceMap)Delta[X.Key]=Vec(D[X.Value]);
 }
 if(!Mesh->CommitMeshDescription(0))return TEXT("source morph commit failed");
 }
 Mesh->MarkPackageDirty();
 return FString::Printf(TEXT("pass vertices=%d max_error_cm=%.9f source_morphs=2 morphs=%d"),V.Num(),MaxError,Mesh->GetMorphTargets().Num());
}

FString UParisNPCGripAssetFactory::AuditThumbMesh(USkeletalMesh* Mesh,USkeletalMesh* Original)
{
 if(!Mesh||!Original)return TEXT("missing mesh");
 const auto& A=Mesh->GetRefSkeleton();const auto& B=Original->GetRefSkeleton();if(A.GetNum()!=B.GetNum())return TEXT("bone count changed");
 for(int32 I=0;I<A.GetNum();++I)if(A.GetBoneName(I)!=B.GetBoneName(I)||A.GetParentIndex(I)!=B.GetParentIndex(I)||!A.GetRefBonePose()[I].Equals(B.GetRefBonePose()[I],0.f))return TEXT("rest skeleton changed");
 auto* AM=Mesh->GetImportedModel();auto* BM=Original->GetImportedModel();if(AM->LODModels.Num()!=BM->LODModels.Num())return TEXT("LOD count changed");
 const auto& AL=AM->LODModels[0];const auto& BL=BM->LODModels[0];TArray<FSoftSkinVertex> AV,BV;AL.GetVertices(AV);BL.GetVertices(BV);
 if(AV.Num()!=BV.Num()||AL.IndexBuffer!=BL.IndexBuffer||AL.Sections.Num()!=BL.Sections.Num())return TEXT("topology changed");
 for(int32 I=0;I<AV.Num();++I){const auto& X=AV[I];const auto& Y=BV[I];if(X.Position!=Y.Position||X.Color!=Y.Color)return TEXT("basis position/color changed");for(int32 J=0;J<UE_ARRAY_COUNT(X.UVs);++J)if(X.UVs[J]!=Y.UVs[J])return TEXT("UV changed");for(int32 J=0;J<UE_ARRAY_COUNT(X.InfluenceBones);++J)if(X.InfluenceBones[J]!=Y.InfluenceBones[J]||X.InfluenceWeights[J]!=Y.InfluenceWeights[J])return TEXT("skin weights changed");}
 for(int32 I=0;I<AL.Sections.Num();++I)if(AL.Sections[I].BoneMap!=BL.Sections[I].BoneMap||AL.Sections[I].MaterialIndex!=BL.Sections[I].MaterialIndex)return TEXT("skin/material partition changed");
 if(Mesh->GetMorphTargets().Num()!=2)return TEXT("two morphs not persisted");
 for(const auto& M:Mesh->GetMorphTargets())if(!M||M->GetNumDeltasForLOD(0)<=0)return TEXT("empty persisted morph");
 return FString::Printf(TEXT("pass basis_positions_weights_uv_topology_rest_exact vertices=%d bones=%d morphs=2"),AV.Num(),A.GetNum());
}
