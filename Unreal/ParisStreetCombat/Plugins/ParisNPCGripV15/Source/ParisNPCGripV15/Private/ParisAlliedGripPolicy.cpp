#include "ParisAlliedGripPolicy.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "UObject/UnrealType.h"

AParisAlliedGripPolicy::AParisAlliedGripPolicy()
{
    PrimaryActorTick.bCanEverTick=true;
    PrimaryActorTick.TickInterval=1.f; // Lifecycle cleanup only; pose stays native.
}
void AParisAlliedGripPolicy::BeginPlay()
{
    Super::BeginPlay();
    if(!AlliedNPCClass || !BindingConfig || !RifleAppearanceClass || !RifleMesh)
    {SetupError=TEXT("Allied class/config/original rifle defaults required");SetActorTickEnabled(false);return;}
    SpawnHandle=GetWorld()->AddOnActorSpawnedHandler(
        FOnActorSpawned::FDelegate::CreateUObject(this,&AParisAlliedGripPolicy::RegisterActor));
    for(TActorIterator<ACharacter> It(GetWorld());It;++It)RegisterActor(*It);
}
void AParisAlliedGripPolicy::RegisterActor(AActor* Actor)
{
    auto* Soldier=Cast<ACharacter>(Actor);
    if(!Soldier || !Soldier->IsA(AlliedNPCClass) || Soldier->IsPlayerControlled() || Adapters.Contains(Soldier))return;
    const auto* Team=FindFProperty<FNumericProperty>(Soldier->GetClass(),TEXT("TeamId"));
    if(!Team || Team->GetSignedIntPropertyValue(Team->ContainerPtrToValuePtr<void>(Soldier))!=0)
    {SetupError=TEXT("Selected Allied class is not TeamId0");return;}
    for(TActorIterator<AParisNPCGripActor> It(GetWorld());It;++It)
        if(It->Target==Soldier)
        {SetupError=TEXT("Duplicate Allied grip adapter; preserve existing binding");return;}
    FActorSpawnParameters Params;
    Params.Owner=Soldier;
    auto* Adapter=GetWorld()->SpawnActor<AParisNPCGripActor>(FVector::ZeroVector,FRotator::ZeroRotator,Params);
    if(!Adapter){SetupError=TEXT("Could not create Allied grip adapter");return;}
    Adapter->Target=Soldier;
    Adapter->BindingConfig=BindingConfig;
    Soldier->OnDestroyed.AddUniqueDynamic(this,&AParisAlliedGripPolicy::OnNPCDestroyed);
    Adapters.Add(Soldier,Adapter);RegisteredNPCs=Adapters.Num();
}
void AParisAlliedGripPolicy::OnNPCDestroyed(AActor* Actor)
{
    const TWeakObjectPtr<ACharacter> Key(Cast<ACharacter>(Actor));
    if(auto* Adapter=Adapters.Find(Key))if(Adapter->IsValid())Adapter->Get()->Destroy();
    if(auto* Rifle=SpawnedRifles.Find(Key))if(Rifle->IsValid())Rifle->Get()->Destroy();
    SpawnedRifles.Remove(Key);
    Adapters.Remove(Key);ReadyReported.Remove(Key);RegisteredNPCs=Adapters.Num();
}
bool AParisAlliedGripPolicy::EnsureRifle(ACharacter* Soldier)
{
    // Level-placed equipment is authoritative and never replaced. A later same-
    // class spawn needs the original M1 appearance wiring supplied by the map.
    const auto* Weapon=FindFProperty<FObjectPropertyBase>(Soldier->GetClass(),TEXT("WeaponAppearance"));
    if(!Weapon){SetupError=TEXT("Allied weapon property absent");return false;}
    if(Weapon->GetObjectPropertyValue_InContainer(Soldier))return true;
    if(!Soldier->HasActorBegunPlay())return false;
    FActorSpawnParameters Params;Params.Owner=Soldier;
    auto* Rifle=GetWorld()->SpawnActor<AActor>(RifleAppearanceClass,FVector::ZeroVector,FRotator::ZeroRotator,Params);
    if(!Rifle){SetupError=TEXT("Default original M1 appearance spawn failed");return false;}
    auto* Mesh=Rifle->FindComponentByClass<UStaticMeshComponent>();
    const auto* Grip=FindFProperty<FObjectPropertyBase>(Rifle->GetClass(),TEXT("GripMesh"));
    const auto* Combatant=FindFProperty<FObjectPropertyBase>(Rifle->GetClass(),TEXT("Combatant"));
    if(!Mesh || !Grip || !Combatant)
    {SetupError=TEXT("Default original M1 interface mismatch");Rifle->Destroy();return false;}
    Mesh->SetStaticMesh(RifleMesh);
    Grip->SetObjectPropertyValue_InContainer(Rifle,Soldier->GetMesh());
    Combatant->SetObjectPropertyValue_InContainer(Rifle,Soldier);
    Weapon->SetObjectPropertyValue_InContainer(Soldier,Rifle);
    SpawnedRifles.Add(Soldier,Rifle);
    return true;
}
void AParisAlliedGripPolicy::Tick(float Dt)
{
    Super::Tick(Dt);
    for(auto It=Adapters.CreateIterator();It;++It)
        if(!It.Key().IsValid())
        {if(It.Value().IsValid())It.Value()->Destroy();It.RemoveCurrent();}
        else if(It.Value().IsValid())
        {
            EnsureRifle(It.Key().Get());
            if(!SetupError.IsEmpty())
            {UE_LOG(LogTemp,Error,TEXT("PARIS_ALLIED_GRIP_FAILURE equipment: %s"),*SetupError);SetActorTickEnabled(false);return;}
            auto* Adapter=It.Value().Get();
            if(!Adapter->BindingError.IsEmpty())
            {
                SetupError=Adapter->BindingError;
                UE_LOG(LogTemp,Error,TEXT("PARIS_ALLIED_GRIP_FAILURE %s: %s"),*It.Key()->GetName(),*SetupError);
                SetActorTickEnabled(false);return;
            }
            if(Adapter->Initialized && Adapter->NativeUpdates>0 && !ReadyReported.Contains(It.Key()))
            {
                UE_LOG(LogTemp,Display,TEXT("PARIS_ALLIED_GRIP_READY %s updates=%lld gun_cm=%.9f gun_deg=%.9f"),
                    *It.Key()->GetName(),Adapter->NativeUpdates,Adapter->GunErrorCm,Adapter->GunErrorDegrees);
                ReadyReported.Add(It.Key());
            }
        }
    RegisteredNPCs=Adapters.Num();
}
void AParisAlliedGripPolicy::EndPlay(const EEndPlayReason::Type Reason)
{
    if(GetWorld() && SpawnHandle.IsValid())GetWorld()->RemoveOnActorSpawnedHandler(SpawnHandle);
    SpawnHandle.Reset();Adapters.Empty();SpawnedRifles.Empty();
    Super::EndPlay(Reason);
}
