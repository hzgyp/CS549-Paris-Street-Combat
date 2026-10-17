#include "ParisActionBindings.h"
#include "ParisFirstPersonApprovedActor.h"
#include "EngineUtils.h"
namespace ParisActionBindings {
AParisFirstPersonApprovedActor* Display(AActor* P){if(!P||!P->GetWorld())return nullptr;for(TActorIterator<AParisFirstPersonApprovedActor> I(P->GetWorld());I;++I)if(I->GetOwner()==P&&I->Initialized)return *I;return nullptr;}
void SetObserver(AActor* P,bool B){if(auto* D=Display(P))D->SetUnifiedObserver(B);}
void SetRifleVisible(AActor* P,bool B){if(auto* D=Display(P))D->SetUnifiedRifleVisible(B);}
USkinnedMeshComponent* VisibleBody(AActor* P){auto* D=Display(P);return D?D->UnifiedVisibleBody():nullptr;}
UStaticMeshComponent* VisibleRifle(AActor* P){auto* D=Display(P);return D?D->UnifiedVisibleRifle():nullptr;}
const TCHAR* RecoilClip(){return TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_ShootOnce.Rifle_ShootOnce");}
FString GrenadeClip(FName Stage,bool EquippedDisplay){
 const FString Suffix=EquippedDisplay?(Stage==TEXT("Release")?TEXT("Far"):TEXT("Loop")):(Stage==TEXT("Start")?TEXT("Start"):Stage==TEXT("Cancel")?TEXT("Cancel"):TEXT("Far"));
 return TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Grenade_Throw_")+Suffix+TEXT(".Rifle_Grenade_Throw_")+Suffix;
}
}
