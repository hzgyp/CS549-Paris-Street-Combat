#include "ParisTacticalEquipment.h"
#include "ParisBridgeMission.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/PackageName.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Components/SkeletalMeshComponent.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"

namespace ParisTacticalEquipment {
namespace {
FDelegateHandle TickHandle;
FString CheckMode,CheckOut;
bool Finished=false;
TSharedPtr<FJsonObject> Root;
void Inventory(UWorld* World,AParisBridgeMission* Mission) {
    if(Finished || Mission->Phase!=TEXT("Ready"))return;
    auto* Player=UGameplayStatics::GetPlayerCharacter(World,0);if(!Player)return;
    Root=MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("status"),TEXT("inventory_complete_not_feature_acceptance"));
    Root->SetStringField(TEXT("player_mesh"),Player->GetMesh()->GetSkeletalMeshAsset()->GetPathName());
    Root->SetStringField(TEXT("player_skeleton"),Player->GetMesh()->GetSkeletalMeshAsset()->GetSkeleton()->GetPathName());
    TArray<TSharedPtr<FJsonValue>> Assets,Functions;
    const TCHAR* Paths[]={
      TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Grenade_Throw_Start.Rifle_Grenade_Throw_Start"),
      TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Grenade_Throw_Single.Rifle_Grenade_Throw_Single"),
      TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Grenade_Throw_Far.Rifle_Grenade_Throw_Far"),
      TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Grenade_Throw_Cancel.Rifle_Grenade_Throw_Cancel"),
      TEXT("/Game/WW2City/Library_Meshingun/VFX_Meshingun/SmokeFog/Niagara/P_Smoke.P_Smoke"),
      TEXT("/Game/WW2City/Environment/Mesh/Props/SM_AmmoBox_01a.SM_AmmoBox_01a"),
      TEXT("/Game/WW2City/Environment/Mesh/Props/SM_AmmoBox_01b.SM_AmmoBox_01b"),
      TEXT("/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_equipment.SK_WWII_US_Paratrooper_equipment")};
    for(const TCHAR* Path:Paths) {
      auto R=MakeShared<FJsonObject>();const FString Package=FPackageName::ObjectPathToPackageName(FString(Path));
      const bool Exists=FPackageName::DoesPackageExist(Package);R->SetStringField(TEXT("path"),Path);R->SetBoolField(TEXT("cooked_exists"),Exists);
      UObject* Asset=Exists?StaticLoadObject(UObject::StaticClass(),nullptr,Path):nullptr;R->SetBoolField(TEXT("loaded"),Asset!=nullptr);
      if(Asset){R->SetStringField(TEXT("class"),Asset->GetClass()->GetPathName());
        if(auto* Clip=Cast<UAnimSequence>(Asset)){R->SetNumberField(TEXT("length"),Clip->GetPlayLength());R->SetStringField(TEXT("skeleton"),Clip->GetSkeleton()->GetPathName());}
        if(auto* Mesh=Cast<USkeletalMesh>(Asset)){TArray<TSharedPtr<FJsonValue>> Materials;for(const auto& Mat:Mesh->GetMaterials())Materials.Add(MakeShared<FJsonValueString>(Mat.MaterialSlotName.ToString()));R->SetArrayField(TEXT("materials"),Materials);}
      } Assets.Add(MakeShared<FJsonValueObject>(R));
    }
    for(TFieldIterator<UFunction> It(Player->GetClass());It;++It)if(It->GetName().StartsWith(TEXT("PC_"))) {
      auto F=MakeShared<FJsonObject>();F->SetStringField(TEXT("name"),It->GetName());TArray<TSharedPtr<FJsonValue>> Params;
      for(TFieldIterator<FProperty> P(*It);P;++P)if(P->HasAnyPropertyFlags(CPF_Parm)){auto V=MakeShared<FJsonObject>();V->SetStringField(TEXT("name"),P->GetName());V->SetStringField(TEXT("type"),P->GetCPPType());Params.Add(MakeShared<FJsonValueObject>(V));}
      F->SetArrayField(TEXT("params"),Params);Functions.Add(MakeShared<FJsonValueObject>(F));
    }
    Root->SetArrayField(TEXT("assets"),Assets);Root->SetArrayField(TEXT("functions"),Functions);
    FString Json;auto Writer=TJsonWriterFactory<>::Create(&Json);FJsonSerializer::Serialize(Root.ToSharedRef(),Writer);
    FFileHelper::SaveStringToFile(Json,*(CheckOut/TEXT("INVENTORY.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
    Finished=true;FPlatformMisc::RequestExit(false);
}
void Tick(UWorld* World,ELevelTick Type,float DeltaSeconds) {
    if(!World || !World->IsGameWorld() || CheckMode!=TEXT("inventory"))return;
    auto* Mission=AParisBridgeMission::Find(World);if(Mission)Inventory(World,Mission);
}
}
void Initialize() {
    if(!FParse::Value(FCommandLine::Get(),TEXT("ParisEquipmentCheck="),CheckMode))return;
    checkf(FParse::Value(FCommandLine::Get(),TEXT("ParisEquipmentOut="),CheckOut),TEXT("Equipment diagnostic requires explicit output"));
    TickHandle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);
}
void Shutdown() {FWorldDelegates::OnWorldPostActorTick.Remove(TickHandle);}
}
