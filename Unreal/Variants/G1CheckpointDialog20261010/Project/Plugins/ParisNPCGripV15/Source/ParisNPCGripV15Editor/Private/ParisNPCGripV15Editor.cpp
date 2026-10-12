#include "ParisNPCGripV15Editor.h"
#include "Animation/AnimBlueprint.h"
#include "Engine/SkeletalMesh.h"
#include "AnimGraphNode_LinkedInputPose.h"
#include "AnimGraphNode_Root.h"
#include "Factories/AnimBlueprintFactory.h"
#include "AssetToolsModule.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphNode.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonReader.h"
#include "Misc/PackageName.h"
#include "Modules/ModuleManager.h"

UAnimBlueprint* UParisNPCGripAssetFactory::CreateAdapter(USkeletalMesh* Mesh,const FString& Path,const FString& Json)
{
    if(!Mesh || FindObject<UObject>(nullptr,*(Path+TEXT(".")+FPackageName::GetLongPackageAssetName(Path))))return nullptr;
    TSharedPtr<FJsonObject> J;
    if(!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json),J))return nullptr;
    auto* Factory=NewObject<UAnimBlueprintFactory>();
    Factory->TargetSkeleton=Mesh->GetSkeleton();Factory->PreviewSkeletalMesh=Mesh;
    Factory->ParentClass=UParisNPCGripAnimInstance::StaticClass();
    auto& Tools=FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools")).Get();
    auto* BP=Cast<UAnimBlueprint>(Tools.CreateAsset(FPackageName::GetLongPackageAssetName(Path),FPackageName::GetLongPackagePath(Path),UAnimBlueprint::StaticClass(),Factory));
    if(!BP)return nullptr;
    UEdGraph* Graph=nullptr;
    for(UEdGraph* G:BP->FunctionGraphs)if(G->GetFName()==TEXT("AnimGraph"))Graph=G;
    if(!Graph)return nullptr;
    TArray<UAnimGraphNode_Root*> Roots;Graph->GetNodesOfClass(Roots);
    if(Roots.Num()!=1)return nullptr;
    FGraphNodeCreator<UAnimGraphNode_LinkedInputPose> InputCreator(*Graph);
    auto* Input=InputCreator.CreateNode();Input->NodePosX=-600;InputCreator.Finalize();
    FGraphNodeCreator<UAnimGraphNode_ParisNPCGrip> AdapterCreator(*Graph);
    auto* Adapter=AdapterCreator.CreateNode();Adapter->NodePosX=-300;
    Adapter->Node.AcceptedHolding=J->GetBoolField(TEXT("accepted_holding"));
    for(const auto& Value:J->GetArrayField(TEXT("rules")))
    {
        auto R=Value->AsObject();const auto Q=R->GetArrayField(TEXT("delta"));
        FParisNPCGripRule Rule;Rule.Bone.BoneName=FName(R->GetStringField(TEXT("bone")));
        Rule.Delta=FQuat(Q[0]->AsNumber(),Q[1]->AsNumber(),Q[2]->AsNumber(),Q[3]->AsNumber()).GetNormalized();
        const auto A=R->GetArrayField(TEXT("accepted_q"));
        Rule.Accepted=FQuat(A[0]->AsNumber(),A[1]->AsNumber(),A[2]->AsNumber(),A[3]->AsNumber()).GetNormalized();
        Adapter->Node.Rules.Add(Rule);
    }
    AdapterCreator.Finalize();
    auto OutputPin=[](UEdGraphNode* N){for(auto* P:N->Pins)if(P->Direction==EGPD_Output)return P;return (UEdGraphPin*)nullptr;};
    auto InputPin=[](UEdGraphNode* N){for(auto* P:N->Pins)if(P->Direction==EGPD_Input && P->PinType.PinCategory==TEXT("struct"))return P;return (UEdGraphPin*)nullptr;};
    auto* RootPin=InputPin(Roots[0]);if(!RootPin)return nullptr;RootPin->BreakAllPinLinks();
    if(!Graph->GetSchema()->TryCreateConnection(OutputPin(Input),InputPin(Adapter)))return nullptr;
    if(!Graph->GetSchema()->TryCreateConnection(OutputPin(Adapter),RootPin))return nullptr;
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
    FKismetEditorUtilities::CompileBlueprint(BP);
    return BP->Status==BS_Error ? nullptr:BP;
}
IMPLEMENT_MODULE(FDefaultModuleImpl,ParisNPCGripV15Editor)
