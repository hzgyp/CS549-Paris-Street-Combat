#include "ParisFirstPersonApprovedActor.h"
#include "Camera/CameraComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "UObject/UnrealType.h"
#include "ParisExistingRecoil.h"

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
AParisFirstPersonApprovedActor::~AParisFirstPersonApprovedActor() = default;

FString AParisFirstPersonApprovedActor::InspectExistingRecoilSource() const
{
    FParisExistingRecoil Probe;
    const bool Valid=Probe.Prepare(LoadObject<UAnimSequence>(nullptr,TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_ShootOnce.Rifle_ShootOnce")));
    FString Result=FString::Printf(TEXT("{\"valid\":%s,\"maximum\":%.12f,\"duration\":%.12f,\"error\":\"%s\",\"samples\":["),Valid?TEXT("true"):TEXT("false"),Probe.SourceMaximumCm,Probe.Duration,*Probe.Error);
    for(int32 I=0;I<Probe.Samples.Num();++I)
    {
        const auto& T=Probe.Samples[I];const auto V=T.GetTranslation();const auto Q=T.GetRotation();
        Result+=FString::Printf(TEXT("%s{\"t\":[%.12f,%.12f,%.12f],\"q\":[%.12f,%.12f,%.12f,%.12f]}"),I?TEXT(","):TEXT(""),V.X,V.Y,V.Z,Q.X,Q.Y,Q.Z,Q.W);
    }
    return Result+TEXT("]}");
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
    if (Initialized)
    {
        if (!ExistingRecoil)
        {
            ExistingRecoil = MakeUnique<FParisExistingRecoil>();
            auto* Clip = LoadObject<UAnimSequence>(nullptr, TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_ShootOnce.Rifle_ShootOnce"));
            if (!ExistingRecoil->Prepare(Clip)) { RecoilSourceMaximumCm=ExistingRecoil->SourceMaximumCm; RecoilError = ExistingRecoil->Error; Initialized=false; StopSetup(RecoilError); return; }
            RecoilSourceMaximumCm = ExistingRecoil->SourceMaximumCm;
        }
        const FTransform Delta = ExistingRecoil->Update(GetOwner(), GetWorld()->GetTimeSeconds());
        const FTransform Hand = Pose->GetSocketTransform(TEXT("hand_r"), RTS_Component);
        // Move the entire accepted display about its current hand frame.
        // Both hands and the attached rifle retain all relative geometry.
        Pose->SetRelativeTransform(Hand.Inverse() * Delta * Hand * CachedAssemblyFrame);
        RecoilActive = ExistingRecoil->Active;
        RecoilStarts = ExistingRecoil->Starts;
        RecoilAge = ExistingRecoil->Age;
        RecoilError = ExistingRecoil->Error;
    }
}
