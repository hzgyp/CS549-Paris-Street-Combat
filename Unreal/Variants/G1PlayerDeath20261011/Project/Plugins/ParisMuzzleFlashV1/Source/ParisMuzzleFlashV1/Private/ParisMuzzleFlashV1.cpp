#include "ParisMuzzleFlashV1.h"
#include "CoreGlobals.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshSocket.h"
#include "Engine/World.h"
#include "Engine/TextureRenderTarget2D.h"
#include "EngineUtils.h"
#include "GameFramework/Pawn.h"
#include "NiagaraComponent.h"
#include "NiagaraEmitter.h"
#include "NiagaraEmitterHandle.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraParameterStore.h"
#include "NiagaraSystem.h"
#include "NiagaraTypes.h"
#include "Modules/ModuleManager.h"
#include "Misc/PackageName.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"
#include "UObject/Package.h"
#include "UObject/StructOnScope.h"
#if WITH_EDITOR
#include "StaticMeshAttributes.h"
#endif

namespace
{
constexpr float VerifiedRate = 20.f;
constexpr float VerifiedEmissionSeconds = .10f;
const FName RateName(TEXT("User.MuzzleFlash_SpawnRate"));
UNiagaraComponent* SpawnPulse(UNiagaraSystem* System, UStaticMeshComponent* Rifle, const FTransform& Local, FTimerHandle& Handle)
{
    if (!IsValid(System) || !System->IsReadyToRun() || !IsValid(Rifle) || !Local.IsValid()
        || System->GetPathName() != TEXT("/Game/MsvFx_MuzzleFlash_Pack/Prefabs/Niagara_Riffle_MuzzleFlash_01.Niagara_Riffle_MuzzleFlash_01")) return nullptr;
    auto* C = UNiagaraFunctionLibrary::SpawnSystemAttached(System, Rifle, NAME_None, Local.GetLocation(),
        Local.Rotator(), Local.GetScale3D(), EAttachLocation::KeepRelativeOffset, false, ENCPoolMethod::None, false, false);
    if (!C) return nullptr;
    C->SetOnlyOwnerSee(Rifle->bOnlyOwnerSee);
    C->SetOwnerNoSee(Rifle->bOwnerNoSee);
    C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    C->SetVariableFloat(RateName, VerifiedRate);
    bool Valid = false;
    if (C->GetVariableFloat(RateName, Valid) != VerifiedRate || !Valid) { C->DestroyComponent(); return nullptr; }
    C->Activate(true);
    FTimerDelegate Stop;
    Stop.BindUFunction(C, TEXT("Deactivate"));
    Rifle->GetWorld()->GetTimerManager().SetTimer(Handle, Stop, VerifiedEmissionSeconds, false);
    return C;
}
int64 Integer(UObject* Object, const TCHAR* Name)
{
    const auto* P = Object ? FindFProperty<FNumericProperty>(Object->GetClass(), Name) : nullptr;
    return P ? P->GetSignedIntPropertyValue(P->ContainerPtrToValuePtr<void>(Object)) : 0;
}
double Real(UObject* Object, const TCHAR* Name)
{
    const auto* P = Object ? FindFProperty<FNumericProperty>(Object->GetClass(), Name) : nullptr;
    return P ? P->GetFloatingPointPropertyValue(P->ContainerPtrToValuePtr<void>(Object)) : 0;
}
UObject* ObjectProperty(UObject* Object, const TCHAR* Name)
{
    const auto* P = Object ? FindFProperty<FObjectPropertyBase>(Object->GetClass(), Name) : nullptr;
    return P ? P->GetObjectPropertyValue_InContainer(Object) : nullptr;
}
bool Boolean(UObject* Object, const TCHAR* Name)
{
    const auto* P = Object ? FindFProperty<FBoolProperty>(Object->GetClass(), Name) : nullptr;
    return P && P->GetPropertyValue_InContainer(Object);
}
FName Name(UObject* Object, const TCHAR* Property)
{
    const auto* P = Object ? FindFProperty<FNameProperty>(Object->GetClass(), Property) : nullptr;
    return P ? P->GetPropertyValue_InContainer(Object) : NAME_None;
}
UStaticMeshComponent* PresentedRifle(UStaticMeshComponent* Gun)
{
    // Hidden equipment must not leave an independently visible owned effect.
    // Observe presentation only; never change the accepted rifle/grip itself.
    return IsValid(Gun) && Gun->IsRegistered() && Gun->IsVisible() && !Gun->bHiddenInGame
        && IsValid(Gun->GetOwner()) && !Gun->GetOwner()->IsHidden() ? Gun : nullptr;
}
UStaticMeshComponent* VisibleRifleFor(AActor* Target)
{
    if (const auto* Pawn = Cast<APawn>(Target); Pawn && Pawn->IsPlayerControlled())
    {
        for (TActorIterator<AActor> It(Target->GetWorld()); It; ++It)
            if (It->GetOwner() == Target && It->GetClass()->GetPathName() == TEXT("/Script/ParisGripBindingV18.ParisFirstPersonApprovedActor")
                && Boolean(*It, TEXT("Initialized")))
                return PresentedRifle(Cast<UStaticMeshComponent>(ObjectProperty(*It, TEXT("Gun"))));
        return nullptr;
    }
    // Only bind a current supported NPC after its accepted native policy is ready.
    for (TActorIterator<AActor> It(Target->GetWorld()); It; ++It)
        if (It->GetClass()->GetPathName() == TEXT("/Script/ParisNPCGripV15.ParisNPCGripActor")
            && ObjectProperty(*It, TEXT("Target")) == Target && Boolean(*It, TEXT("Initialized")))
            if (auto* Gun = Cast<AStaticMeshActor>(ObjectProperty(Target, TEXT("WeaponAppearance"))))
                return PresentedRifle(Gun->GetStaticMeshComponent());
    return nullptr;
}
}

bool UParisMuzzleReviewCapture::ArmDeferredReview(AActor* Target, const TArray<UTextureRenderTarget2D*>& Targets)
{
    if (CaptureDelegate.IsValid() || ReviewArmed || !CaptureRecords.IsEmpty() || !CaptureError.IsEmpty()
        || !IsRegistered() || bCaptureEveryFrame || !IsValid(Target) || Target->GetWorld() != GetWorld()
        || Integer(Target, TEXT("ShotSequence")) != 0 || Targets.Num() != 12) return false;
    TSet<UTextureRenderTarget2D*> Unique;
    for (auto* RT : Targets)
        if (!IsValid(RT) || RT == TextureTarget || Unique.Contains(RT)) return false;
        else Unique.Add(RT);
    ReviewTargets = Targets;
    ReviewTarget = Target;
    ReviewArmed = true;
    CaptureDelegate = FWorldDelegates::OnWorldPostActorTick.AddUObject(this, &UParisMuzzleReviewCapture::DeferredWorldFrame);
    return true;
}
void UParisMuzzleReviewCapture::StopDeferredReview()
{
    if (CaptureDelegate.IsValid()) FWorldDelegates::OnWorldPostActorTick.Remove(CaptureDelegate);
    CaptureDelegate.Reset();
    ReviewArmed = false;
}
void UParisMuzzleReviewCapture::OnUnregister()
{
    StopDeferredReview();
    Super::OnUnregister();
}
void UParisMuzzleReviewCapture::BeginDestroy()
{
    StopDeferredReview();
    Super::BeginDestroy();
}
void UParisMuzzleReviewCapture::DeferredWorldFrame(UWorld* World, ELevelTick TickType, float DeltaSeconds)
{
    if (World != GetWorld() || !ReviewArmed) return;
    auto Fail = [this](const TCHAR* Message) { CaptureError = Message; StopDeferredReview(); };
    AActor* Target = ReviewTarget.Get();
    auto* Subsystem = World->GetSubsystem<UParisMuzzleFlashSubsystem>();
    if (!IsValid(Target) || Target->GetWorld() != World || !Subsystem || World->IsPaused())
    { Fail(TEXT("Deferred review lost original world/target")); return; }
    const auto* O = Subsystem->Observations.FindByPredicate([Target](const auto& Row) { return Row.Target == Target; });
    if (!O) { Fail(TEXT("Deferred review lost original binding")); return; }
    if (O->Started == 0) return;
    if (Integer(Target, TEXT("ShotSequence")) != 1 || O->Started != 1 || O->LiveCount != 1
        || O->Completed || O->Cancelled || O->TimedOut || O->MissedSequences || !O->Error.IsEmpty())
    { Fail(TEXT("First actual pulse ended before twelve deferred frames")); return; }
    const int64 Frame = static_cast<int64>(GFrameCounter);
    const double Now = World->GetTimeSeconds();
    if (!CaptureRecords.IsEmpty() && (CaptureRecords.Last().Frame == Frame || CaptureRecords.Last().WorldTime == Now)) return;
    if (!CaptureRecords.IsEmpty() && (CaptureRecords.Last().Frame > Frame || CaptureRecords.Last().WorldTime > Now))
    { Fail(TEXT("Deferred review frame/time reversed")); return; }
    const int32 Index = CaptureRecords.Num();
    if (!ReviewTargets.IsValidIndex(Index) || !IsValid(ReviewTargets[Index]))
    { Fail(TEXT("Deferred review target unavailable")); return; }
    TextureTarget = ReviewTargets[Index];
    // Normal rendering path only. No manual Niagara simulation or world step.
    CaptureSceneDeferred();
    auto& Record = CaptureRecords.AddDefaulted_GetRef();
    Record.Frame = Frame; Record.WorldTime = Now; Record.ShotSequence = 1;
    Record.Started = O->Started; Record.LiveCount = O->LiveCount;
    if (CaptureRecords.Num() == 12) StopDeferredReview();
}

bool UParisMuzzleFlashSubsystem::DoesSupportWorldType(EWorldType::Type Type) const
{
    return Type == EWorldType::Game || Type == EWorldType::PIE;
}
void UParisMuzzleFlashSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // A hard native profile keeps selected effect/mesh identity explicit. It
    // remains absent during Entry inventory and unselected source development.
    if (FPackageName::DoesPackageExist(TEXT("/Game/ParisCombat/VFX/MuzzleFlashV1/DA_PC_MuzzleFlashV1")))
        Profile = LoadObject<UParisMuzzleFlashProfile>(nullptr, TEXT("/Game/ParisCombat/VFX/MuzzleFlashV1/DA_PC_MuzzleFlashV1.DA_PC_MuzzleFlashV1"), nullptr, LOAD_NoWarn);
    if (Profile) ConfigurePrivateCandidate(Profile);
}
bool UParisMuzzleFlashSubsystem::ConfigurePrivateCandidate(UParisMuzzleFlashProfile* InProfile)
{
    if (!InProfile || !InProfile->Effect || !InProfile->Effect->IsReadyToRun()
        || InProfile->Rifles.IsEmpty() || InProfile->MaximumLifetimeSeconds <= 0 || InProfile->MaximumLifetimeSeconds > 8
        || !Observations.IsEmpty() || !Effects.IsEmpty()) return false;
    for (const auto& Rifle : InProfile->Rifles)
        if (!Rifle.RifleMesh || !Rifle.MuzzleLocal.IsValid() || Rifle.MuzzleLocal.GetScale3D().GetMin() <= 0) return false;
    Profile = InProfile;
    State = TEXT("NativeCommittedShotPresentationReady");
    return true;
}
TArray<UNiagaraComponent*> UParisMuzzleFlashSubsystem::GetOwnedComponents() const
{
    TArray<UNiagaraComponent*> Result;
    for (const auto& E : Effects) if (E.Component.IsValid()) Result.Add(E.Component.Get());
    return Result;
}
TStatId UParisMuzzleFlashSubsystem::GetStatId() const
{
    RETURN_QUICK_DECLARE_CYCLE_STAT(ParisPurchasedMuzzleFlash, STATGROUP_Tickables);
}
void UParisMuzzleFlashSubsystem::DiscoverTargets()
{
    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        AActor* Target = *It;
        if (!FindFProperty<FNumericProperty>(Target->GetClass(), TEXT("ShotSequence"))
            || Boolean(Target, TEXT("IsDead")) || Observations.ContainsByPredicate([Target](const auto& O) { return O.Target == Target; })) continue;
        auto* Gun = VisibleRifleFor(Target);
        if (!IsValid(Gun) || !Profile->Rifles.ContainsByPredicate([Gun](const auto& P) { return P.RifleMesh == Gun->GetStaticMesh(); })) continue;
        auto& O = Observations.AddDefaulted_GetRef();
        O.Target = Target; O.VisibleRifle = Gun;
        O.LastSequence = Integer(Target, TEXT("ShotSequence"));
        O.Generation = Integer(Target, TEXT("RestoreGeneration"));
    }
}
void UParisMuzzleFlashSubsystem::Cancel(AActor* Target)
{
    for (int32 I = Effects.Num() - 1; I >= 0; --I)
        if (!Target || Effects[I].Target == Target)
        {
            GetWorld()->GetTimerManager().ClearTimer(Effects[I].StopTimer);
            if (auto* C = Effects[I].Component.Get()) { C->DeactivateImmediate(); C->DestroyComponent(); }
            if (auto* O = Observations.FindByPredicate([&](const auto& Row) { return Row.Target == Effects[I].Target.Get(); })) ++O->Cancelled;
            Effects.RemoveAt(I);
        }
}
void UParisMuzzleFlashSubsystem::Tick(float DeltaTime)
{
    // An editor/game load may finish Niagara compilation after Initialize.
    // An absent profile stays dormant; only the same explicit profile may arm.
    if (State == TEXT("WaitingForVerifiedPrivateProfile") && Profile && Profile->Effect
        && Profile->Effect->IsReadyToRun()) ConfigurePrivateCandidate(Profile);
    if (State != TEXT("NativeCommittedShotPresentationReady") || !Profile || GetWorld()->GetNetMode() == NM_DedicatedServer) return;
    const double Now = GetWorld()->GetTimeSeconds();
    if (Now >= NextDiscovery) { DiscoverTargets(); NextDiscovery = Now + .25; }
    for (auto& O : Observations)
    {
        if (!IsValid(O.Target)) { Cancel(O.Target); continue; }
        const int64 Shot = Integer(O.Target, TEXT("ShotSequence"));
        const int64 Generation = Integer(O.Target, TEXT("RestoreGeneration"));
        if (Generation != O.Generation || Shot < O.LastSequence || Boolean(O.Target, TEXT("IsDead")))
        { Cancel(O.Target); O.LastSequence = Shot; O.Generation = Generation; continue; }
        if (Name(O.Target, TEXT("ActionState")) == TEXT("Reloading"))
        { Cancel(O.Target); O.LastSequence = Shot; continue; }
        auto* CurrentGun = VisibleRifleFor(O.Target);
        if (CurrentGun != O.VisibleRifle)
        { Cancel(O.Target); O.VisibleRifle = CurrentGun; O.LastSequence = Shot; continue; }
        if (!IsValid(CurrentGun)) { Cancel(O.Target); O.LastSequence = Shot; continue; }
        const auto* Rifle = Profile->Rifles.FindByPredicate([&](const auto& P) { return P.RifleMesh == O.VisibleRifle->GetStaticMesh(); });
        if (!Rifle) { Cancel(O.Target); O.Error = TEXT("Equipment no longer matches verified muzzle profile"); continue; }
        O.VisualMuzzle = Rifle->MuzzleLocal * O.VisibleRifle->GetComponentTransform();
        if (auto* Original = Cast<AActor>(ObjectProperty(O.Target, TEXT("WeaponAppearance"))))
            O.LegacyShotMuzzle = Original->GetActorTransform().TransformPosition(FVector(0, 83.23, 0));
        if (Shot > O.LastSequence)
        {
            const double Commit = Real(O.Target, TEXT("NextShotTime")) - .25;
            if (Shot - O.LastSequence != 1 || Now - Commit > .25 || Now < Commit)
            { O.MissedSequences += static_cast<int32>(Shot - O.LastSequence); O.Error = TEXT("Unobserved/stale shot identity; no invented effect"); }
            else
            {
                FTimerHandle StopTimer;
                auto* C = SpawnPulse(Profile->Effect, O.VisibleRifle, Rifle->MuzzleLocal, StopTimer);
                if (!C) O.Error = TEXT("Purchased system failed to spawn");
                else
                {
                    Effects.Add({C, O.Target, Now, StopTimer}); ++O.Started; O.LatestShotTime = Commit;
                }
            }
            O.LastSequence = Shot;
        }
    }
    for (int32 I = Effects.Num() - 1; I >= 0; --I)
    {
        auto* C = Effects[I].Component.Get();
        const bool Lost = !IsValid(C);
        const bool Finished = !Lost && C->IsComplete();
        const bool TimedOut = Now - Effects[I].Born > Profile->MaximumLifetimeSeconds;
        if (Lost || Finished || TimedOut)
        {
            GetWorld()->GetTimerManager().ClearTimer(Effects[I].StopTimer);
            if (auto* O = Observations.FindByPredicate([&](const auto& Row) { return Row.Target == Effects[I].Target.Get(); }))
            {
                if (Lost) { ++O->Cancelled; O->Error = TEXT("Owned component lost before true completion"); }
                else if (TimedOut && !Finished) { ++O->TimedOut; O->Error = TEXT("Purchased emission exceeded finite lifetime"); }
                else ++O->Completed;
            }
            if (IsValid(C)) { if (!Finished) C->DeactivateImmediate(); C->DestroyComponent(); }
            Effects.RemoveAt(I);
        }
    }
    for (auto& O : Observations)
    {
        O.LiveCount = 0;
        for (const auto& E : Effects) if (E.Target.Get() == O.Target.Get()) ++O.LiveCount;
    }
}
void UParisMuzzleFlashSubsystem::Deinitialize()
{
    Cancel(nullptr); Observations.Empty(); Profile = nullptr;
    Super::Deinitialize();
}

FString UParisMuzzleFlashLibrary::InspectPurchasedSystem(UNiagaraSystem* System)
{
    if (!System) return TEXT("{\"loaded\":false}");
    auto Root = MakeShared<FJsonObject>();
    Root->SetStringField(TEXT("path"), System->GetPathName());
    Root->SetBoolField(TEXT("loaded"), true);
    Root->SetBoolField(TEXT("valid"), System->IsValid());
    Root->SetBoolField(TEXT("ready"), System->IsReadyToRun());
#if WITH_EDITOR
    Root->SetBoolField(TEXT("compiling"), System->HasOutstandingCompilationRequests(true));
#endif
    TArray<TSharedPtr<FJsonValue>> Emitters;
    for (const auto& Handle : System->GetEmitterHandles())
    {
        auto E = MakeShared<FJsonObject>();
        E->SetStringField(TEXT("name"), Handle.GetName().ToString());
        E->SetBoolField(TEXT("enabled"), Handle.GetIsEnabled());
        if (const auto* Data = Handle.GetEmitterData())
        {
            E->SetBoolField(TEXT("local_space"), Data->bLocalSpace);
            E->SetStringField(TEXT("simulation"), Data->SimTarget == ENiagaraSimTarget::CPUSim ? TEXT("CPU") : TEXT("GPU"));
            E->SetNumberField(TEXT("renderer_count"), Data->GetRenderers().Num());
        }
        Emitters.Add(MakeShared<FJsonValueObject>(E));
    }
    Root->SetArrayField(TEXT("emitters"), Emitters);
    TArray<FNiagaraVariable> Parameters;
    System->GetExposedParameters().GetParameters(Parameters);
    TArray<TSharedPtr<FJsonValue>> Names;
    for (const auto& P : Parameters) Names.Add(MakeShared<FJsonValueString>(P.GetName().ToString()));
    Root->SetArrayField(TEXT("user_parameters"), Names);
    // Asset-owned typed defaults only. No overrides or live instance buffers.
    TArray<TSharedPtr<FJsonValue>> Defaults;
    for (const auto& P : Parameters)
    {
        auto D = MakeShared<FJsonObject>();
        D->SetStringField(TEXT("name"), P.GetName().ToString());
        D->SetStringField(TEXT("type"), P.GetType().GetName());
        D->SetNumberField(TEXT("size_bytes"), P.GetSizeInBytes());
        if (P.GetType() == FNiagaraTypeDefinition::GetFloatDef() && P.GetSizeInBytes() == sizeof(float))
        {
            const auto Value = System->GetExposedParameters().GetParameterOptionalValue<float>(P);
            D->SetBoolField(TEXT("available"), Value.IsSet());
            if (Value.IsSet()) D->SetNumberField(TEXT("float_value"), Value.GetValue());
        }
        Defaults.Add(MakeShared<FJsonValueObject>(D));
    }
    Root->SetArrayField(TEXT("exposed_asset_defaults"), Defaults);
    FString Result; FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result)); return Result;
}
UParisMuzzleFlashSubsystem* UParisMuzzleFlashLibrary::GetPresentationSubsystem(UObject* WorldContext)
{
    UWorld* World = IsValid(WorldContext) ? WorldContext->GetWorld() : nullptr;
    return World ? World->GetSubsystem<UParisMuzzleFlashSubsystem>() : nullptr;
}
UParisMuzzleLifetimeProbe* UParisMuzzleFlashLibrary::CreateLifetimeProbe(UObject* WorldContext)
{
    auto* Subsystem = GetPresentationSubsystem(WorldContext);
    if (!Subsystem) return nullptr;
    auto* Probe = NewObject<UParisMuzzleLifetimeProbe>(GetTransientPackage());
    Probe->TrackedSubsystem = Subsystem;
    return Probe;
}
bool UParisMuzzleReviewFireBatch::Queue(AActor* InTarget, int32 InRequests)
{
    if (!IsValid(InTarget) || !InTarget->GetWorld() || (InRequests != 1 && InRequests != 2)
        || PreActorHandle.IsValid() || Executed) return false;
    UFunction* Function = InTarget->FindFunction(TEXT("PC_RequestFire"));
    const auto* Origin = Function ? FindFProperty<FStructProperty>(Function, TEXT("AimOrigin")) : nullptr;
    const auto* Direction = Function ? FindFProperty<FStructProperty>(Function, TEXT("AimDirection")) : nullptr;
    const auto* Sequence = FindFProperty<FNumericProperty>(InTarget->GetClass(), TEXT("ShotSequence"));
    if (!Function || Function->NumParms != 2 || !Origin || !Direction
        || !Origin->HasAnyPropertyFlags(CPF_Parm) || !Direction->HasAnyPropertyFlags(CPF_Parm)
        || Origin->HasAnyPropertyFlags(CPF_OutParm | CPF_ReturnParm)
        || Direction->HasAnyPropertyFlags(CPF_OutParm | CPF_ReturnParm)
        || Origin->Struct != TBaseStructure<FVector>::Get() || Direction->Struct != TBaseStructure<FVector>::Get()
        || !Sequence || !Sequence->IsInteger()) return false;
    Target = InTarget;
    ReviewWorld = InTarget->GetWorld();
    Requests = InRequests;
    QueuedWorldTime = InTarget->GetWorld()->GetTimeSeconds();
    PreActorHandle = FWorldDelegates::OnWorldPreActorTick.AddUObject(this, &UParisMuzzleReviewFireBatch::Dispatch);
    return true;
}
void UParisMuzzleReviewFireBatch::Dispatch(UWorld* World, ELevelTick, float)
{
    if (World != ReviewWorld.Get()) return;
    FWorldDelegates::OnWorldPreActorTick.Remove(PreActorHandle);
    PreActorHandle.Reset(); // One shot, removed BEFORE any original transaction.
    Executed = true;
    AActor* Actor = Target.Get();
    if (!IsValid(Actor) || Actor->GetWorld() != World)
    {
        Error = TEXT("Original fire target unavailable at native dispatch");
        return;
    }
    UFunction* Function = Actor->FindFunction(TEXT("PC_RequestFire"));
    const auto* Origin = Function ? FindFProperty<FStructProperty>(Function, TEXT("AimOrigin")) : nullptr;
    const auto* Direction = Function ? FindFProperty<FStructProperty>(Function, TEXT("AimDirection")) : nullptr;
    if (!Function || Function->NumParms != 2 || !Origin || !Direction
        || Origin->Struct != TBaseStructure<FVector>::Get() || Direction->Struct != TBaseStructure<FVector>::Get())
    {
        Error = TEXT("Original fire function signature changed after queue");
        return;
    }
    DispatchWorldTime = World->GetTimeSeconds();
    DispatchFrame = static_cast<int64>(GFrameCounter);
    SequenceBefore = Integer(Actor, TEXT("ShotSequence"));
    for (int32 Index = 0; Index < Requests; ++Index)
    {
        FStructOnScope Parameters(Function);
        *Origin->ContainerPtrToValuePtr<FVector>(Parameters.GetStructMemory()) = Actor->GetActorLocation() + FVector(0, 0, 70);
        *Direction->ContainerPtrToValuePtr<FVector>(Parameters.GetStructMemory()) = FVector(0, 0, 1);
        const int64 Before = Integer(Actor, TEXT("ShotSequence"));
        Actor->ProcessEvent(Function, Parameters.GetStructMemory());
        SequenceDeltas.Add(Integer(Actor, TEXT("ShotSequence")) - Before);
    }
    SequenceAfter = Integer(Actor, TEXT("ShotSequence"));
}
void UParisMuzzleReviewFireBatch::BeginDestroy()
{
    if (PreActorHandle.IsValid()) FWorldDelegates::OnWorldPreActorTick.Remove(PreActorHandle);
    PreActorHandle.Reset();
    Super::BeginDestroy();
}
UParisMuzzleReviewFireBatch* UParisMuzzleFlashLibrary::QueueReviewFire(AActor* Target, int32 Requests)
{
    auto* Batch = NewObject<UParisMuzzleReviewFireBatch>(GetTransientPackage());
    return Batch->Queue(Target, Requests) ? Batch : nullptr;
}
int32 UParisMuzzleLifetimeProbe::TrackOwnedEffects()
{
    TrackedComponents.Reset();
    if (auto* Subsystem = TrackedSubsystem.Get())
        for (auto* Component : Subsystem->GetOwnedComponents()) TrackedComponents.Add(Component);
    return TrackedComponents.Num();
}
FString UParisMuzzleLifetimeProbe::InspectLifetime() const
{
    auto Root = MakeShared<FJsonObject>();
    Root->SetBoolField(TEXT("subsystem_valid"), TrackedSubsystem.IsValid());
    Root->SetNumberField(TEXT("tracked_components"), TrackedComponents.Num());
    int32 Valid = 0;
    for (const auto& Component : TrackedComponents) if (Component.IsValid()) ++Valid;
    Root->SetNumberField(TEXT("valid_components"), Valid);
    FString Result; FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result)); return Result;
}
UParisMuzzleReviewCapture* UParisMuzzleFlashLibrary::CreateReviewCapture(AActor* ViewOwner)
{
    if (!IsValid(ViewOwner) || !ViewOwner->GetWorld()) return nullptr;
    auto* Holder = ViewOwner->GetWorld()->SpawnActor<AActor>();
    if (!Holder) return nullptr;
    auto* Capture = NewObject<UParisMuzzleReviewCapture>(Holder);
    Capture->ReviewViewOwner = ViewOwner;
    Holder->SetRootComponent(Capture);
    Holder->AddInstanceComponent(Capture);
    Capture->RegisterComponent();
    return Capture;
}
bool UParisMuzzleFlashLibrary::RequestPurchasedCompile(UNiagaraSystem* System)
{
#if WITH_EDITOR
    return System && System->RequestCompile(false);
#else
    return false;
#endif
}

FString UParisMuzzleFlashLibrary::InspectPurchasedComponent(UNiagaraComponent* Component)
{
    if (!IsValid(Component)) return TEXT("{\"component_valid\":false}");
    auto Root = MakeShared<FJsonObject>();
    Root->SetBoolField(TEXT("component_valid"), true);
    Root->SetBoolField(TEXT("active"), Component->IsActive());
    Root->SetBoolField(TEXT("complete"), Component->IsComplete());
    bool RateValid = false;
    Root->SetNumberField(TEXT("instance_rate"), Component->GetVariableFloat(RateName, RateValid));
    Root->SetBoolField(TEXT("instance_rate_valid"), RateValid);
    Root->SetStringField(TEXT("system"), Component->GetAsset() ? Component->GetAsset()->GetPathName() : TEXT(""));
    auto VectorArray = [](const FVector& V)
    {
        return TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(V.X),
            MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)};
    };
    Root->SetArrayField(TEXT("location"), VectorArray(Component->GetComponentLocation()));
    Root->SetArrayField(TEXT("forward"), VectorArray(Component->GetForwardVector()));
    Root->SetArrayField(TEXT("bounds_origin"), VectorArray(Component->Bounds.Origin));
    Root->SetArrayField(TEXT("bounds_extent"), VectorArray(Component->Bounds.BoxExtent));
    FString Result; FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result)); return Result;
}

UNiagaraComponent* UParisMuzzleFlashLibrary::SpawnMeasuredPulse(UNiagaraSystem* System, UStaticMeshComponent* Rifle, FTransform Local)
{
    FTimerHandle Timer;
    return SpawnPulse(System, Rifle, Local, Timer);
}
FString UParisMuzzleFlashLibrary::InspectRifleGeometry(UStaticMesh* Mesh)
{
    auto Root = MakeShared<FJsonObject>();
    Root->SetBoolField(TEXT("valid"), IsValid(Mesh));
    if (IsValid(Mesh))
    {
        Root->SetStringField(TEXT("path"), Mesh->GetPathName());
        TArray<TSharedPtr<FJsonValue>> Sockets;
        for (const TObjectPtr<UStaticMeshSocket>& Socket : Mesh->Sockets) if (Socket)
        {
            auto S = MakeShared<FJsonObject>();
            S->SetStringField(TEXT("name"), Socket->SocketName.ToString());
            const auto V = Socket->RelativeLocation;
            S->SetArrayField(TEXT("location"), {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)});
            Sockets.Add(MakeShared<FJsonValueObject>(S));
        }
        Root->SetArrayField(TEXT("sockets"), Sockets);
#if WITH_EDITOR
        if (const auto* Description = Mesh->GetMeshDescription(0))
        {
            const FStaticMeshConstAttributes Attributes(*Description);
            const auto Positions = Attributes.GetVertexPositions();
            TArray<TSharedPtr<FJsonValue>> Vertices;
            for (const auto ID : Description->Vertices().GetElementIDs())
            {
                const auto V = Positions[ID];
                Vertices.Add(MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(ID.GetValue()),
                    MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)}));
            }
            Root->SetArrayField(TEXT("vertices"), Vertices);
        }
#endif
    }
    FString Result; FJsonSerializer::Serialize(Root, TJsonWriterFactory<>::Create(&Result)); return Result;
}

IMPLEMENT_MODULE(FDefaultModuleImpl, ParisMuzzleFlashV1)
