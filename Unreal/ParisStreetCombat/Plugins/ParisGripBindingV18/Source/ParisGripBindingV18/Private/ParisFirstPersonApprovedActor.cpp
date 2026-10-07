#include "ParisFirstPersonApprovedActor.h"
#include "Camera/CameraComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "UObject/UnrealType.h"

namespace
{
UObject* ReadObject(UObject* Object, const TCHAR* Name)
{
    if (!Object) return nullptr;
    const auto* Property = FindFProperty<FObjectPropertyBase>(Object->GetClass(), Name);
    return Property ? Property->GetObjectPropertyValue_InContainer(Object) : nullptr;
}
bool ReadBool(UObject* Object, const TCHAR* Name)
{
    const auto* Property = FindFProperty<FBoolProperty>(Object->GetClass(), Name);
    return Property && Property->GetPropertyValue_InContainer(Object);
}
}

AParisFirstPersonApprovedActor::AParisFirstPersonApprovedActor()
{
    Pose->SetVisibility(false, true);
}

void AParisFirstPersonApprovedActor::StopSetup(const FString& Reason)
{
    SetupStopped = true;
    BindingError = Reason;
    SetupState = TEXT("Stopped");
    Pose->SetVisibility(false, true);
    UE_LOG(LogTemp, Error, TEXT("Paris approved first-person setup stopped: %s"), *Reason);
}

void AParisFirstPersonApprovedActor::TryInitialize(float DeltaSeconds)
{
    WaitingSeconds += DeltaSeconds;
    if (WaitingSeconds > 60.f) { StopSetup(TEXT("Original Ready source did not become available within 60 game seconds")); return; }
    ACharacter* Player = UGameplayStatics::GetPlayerCharacter(this, 0);
    if (!IsValid(Player) || !Player->IsLocallyControlled()) return;
    if (!BindingConfig || !DisplayMesh || !RifleMesh || !HoldingClip)
    { StopSetup(TEXT("Persistent approved display references incomplete")); return; }
    const auto* Action = FindFProperty<FNameProperty>(Player->GetClass(), TEXT("ActionState"));
    if (!Action) { StopSetup(TEXT("Authoritative ActionState absent")); return; }
    if (Action->GetPropertyValue_InContainer(Player) != TEXT("Ready") || ReadBool(Player, TEXT("IsDead"))) return;
    AActor* OriginalGun = Cast<AActor>(ReadObject(Player, TEXT("WeaponAppearance")));
    if (!IsValid(OriginalGun)) return;
    AActor* OriginalOwner = nullptr;
    // Property identity works in packaged builds; editor actor labels are not a runtime contract.
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
        if (*It != this && ReadObject(*It, TEXT("DisplayGun")) == OriginalGun
            && ReadBool(*It, TEXT("Initialized")) && ReadBool(*It, TEXT("HasFraming")))
        { OriginalOwner = *It; break; }
    if (!OriginalOwner) return;
    UCameraComponent* Camera = Cast<UCameraComponent>(ReadObject(Player, TEXT("ParisPlayerCamera")));
    USkeletalMeshComponent* BodySource = Player->GetMesh();
    if (!IsValid(Camera) || !IsValid(BodySource) || !BodySource->GetSkeletalMeshAsset()) return;
    if (!HoldingPrepared)
    {
        if (!PrepareHoldingSource(BodySource->GetSkeletalMeshAsset(), HoldingClip))
        { StopSetup(TEXT("Could not prepare existing holding source")); return; }
        AddTickPrerequisiteActor(OriginalOwner);
        HoldingPrepared = true;
        SetupState = TEXT("EvaluatingExistingHoldingSource");
        return;
    }
    PreparedSeconds += DeltaSeconds;
    // Same one-time source evaluation window as the accepted preview, not a transition repair.
    if (PreparedSeconds < 2.f) return;
    if (!BindExistingPose(Player, BodySource, Camera, OriginalGun, DisplayMesh, RifleMesh, BindingConfig))
    { StopSetup(BindingError); return; }
    OriginalOwner->SetActorHiddenInGame(true);
    OriginalGun->SetActorHiddenInGame(true);
    SetupState = TEXT("NativeApprovedDisplayReady");
    UE_LOG(LogTemp, Display, TEXT("Paris approved first-person native binding ready; original gameplay retained"));
}

void AParisFirstPersonApprovedActor::Tick(float DeltaSeconds)
{
    if (!Initialized && !SetupStopped) TryInitialize(DeltaSeconds);
    Super::Tick(DeltaSeconds);
    if (!Initialized && SetupState == TEXT("NativeApprovedDisplayReady")) StopSetup(BindingError);
}
