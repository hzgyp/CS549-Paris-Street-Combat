#include "ParisGridSurveyLibrary.h"
#include "NavMesh/RecastNavMesh.h"
#include "NavigationSystem.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Policies/CondensedJsonPrintPolicy.h"
#include "Modules/ModuleManager.h"
#include "EngineUtils.h"
#include "GameFramework/Controller.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, ParisGridSurveyV1)

namespace
{
constexpr float Radius = 34.0f;
constexpr float HalfHeight = 96.23316f;
constexpr double FloorGap = 2.15;

TArray<TSharedPtr<FJsonValue>> Coords(const FVector& V)
{
    return {MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)};
}
FVector Vec(const TSharedPtr<FJsonObject>& Row, const FString& Key)
{
    const auto& A = Row->GetArrayField(Key);
    return FVector(A[0]->AsNumber(), A[1]->AsNumber(), A[2]->AsNumber());
}
FString Text(const TSharedRef<FJsonObject>& Object)
{
    FString Out;
    FJsonSerializer::Serialize(Object, TJsonWriterFactory<TCHAR,TCondensedJsonPrintPolicy<TCHAR>>::Create(&Out));
    return Out;
}
bool Valid(ARecastNavMesh* Nav, ACharacter* Probe)
{
    return IsValid(Nav) && IsValid(Probe) && Probe->GetClass() == ACharacter::StaticClass() &&
        Nav->GetWorld() == Probe->GetWorld() && Nav->GetWorld()->WorldType == EWorldType::Editor &&
        IsValid(Probe->GetCharacterMovement()) && Probe->GetCharacterMovement()->GetCharacterOwner() == Probe &&
        Probe->GetCharacterMovement()->UpdatedComponent == Probe->GetCapsuleComponent() &&
        FMath::Abs(Probe->GetCapsuleComponent()->GetScaledCapsuleRadius()-Radius) < 0.001 &&
        FMath::Abs(Probe->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()-HalfHeight) < 0.001;
}
TArray<TSharedPtr<FJsonValue>> Overlaps(ACharacter* Probe, const FVector& Center)
{
    TArray<FOverlapResult> Hits;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(ParisGridOverlap), false, Probe);
    Probe->GetWorld()->OverlapMultiByChannel(Hits, Center, FQuat::Identity, ECC_Pawn,
        FCollisionShape::MakeCapsule(Radius, HalfHeight), Params);
    TArray<TSharedPtr<FJsonValue>> Result;
    for (const auto& Hit : Hits)
        if (Hit.bBlockingHit && Hit.Component.IsValid())
            Result.Add(MakeShared<FJsonValueString>(Hit.Component->GetPathName()));
    return Result;
}
FString MeshPath(const UPrimitiveComponent* Component)
{
    if (const auto* Static = Cast<UStaticMeshComponent>(Component))
        if (Static->GetStaticMesh()) return Static->GetStaticMesh()->GetPathName();
    if (const auto* Skeletal = Cast<USkeletalMeshComponent>(Component))
        if (Skeletal->GetSkeletalMeshAsset()) return Skeletal->GetSkeletalMeshAsset()->GetPathName();
    return TEXT("");
}
}

ACharacter* UParisGridSurveyLibrary::CreateGridProbe(UWorld* World)
{
    if (!IsValid(World) || World->WorldType != EWorldType::Editor) return nullptr;
    FActorSpawnParameters Params;
    Params.ObjectFlags |= RF_Transient;
    Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    ACharacter* Probe = World->SpawnActor<ACharacter>(ACharacter::StaticClass(), FVector(0,0,-100000), FRotator::ZeroRotator, Params);
    if (!Probe) return nullptr;
    Probe->SetActorTickEnabled(false);
    Probe->GetCapsuleComponent()->SetCapsuleSize(Radius,HalfHeight);
    Probe->GetCapsuleComponent()->SetCanEverAffectNavigation(false);
    // Editor-world SpawnActor does not run the game-world movement initialization.
    Probe->GetCharacterMovement()->SetUpdatedComponent(Probe->GetCapsuleComponent());
    if (Probe->GetCharacterMovement()->GetCharacterOwner() != Probe ||
        Probe->GetCharacterMovement()->UpdatedComponent != Probe->GetCapsuleComponent())
    {
        Probe->Destroy();
        return nullptr;
    }
    Probe->GetCharacterMovement()->SetComponentTickEnabled(false);
    Probe->GetCharacterMovement()->MaxStepHeight = 45.0f;
    Probe->GetCharacterMovement()->SetWalkableFloorAngle(44.7651f);
    return Probe;
}

bool UParisGridSurveyLibrary::DestroyGridProbe(ACharacter* Probe)
{
    return IsValid(Probe) && Probe->GetClass() == ACharacter::StaticClass() &&
        Probe->GetWorld()->WorldType == EWorldType::Editor && Probe->HasAnyFlags(RF_Transient) && Probe->Destroy();
}

FString UParisGridSurveyLibrary::InspectGridWorld(UWorld* World)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    if (!IsValid(World) || World->WorldType != EWorldType::Editor)
    {
        Result->SetStringField(TEXT("error"), TEXT("Explicit disposable Editor world required"));
        return Text(Result);
    }
    int32 Characters = 0, Controllers = 0;
    TArray<TSharedPtr<FJsonValue>> Contaminants;
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        if (It->IsA<ACharacter>()) ++Characters;
        if (It->IsA<AController>()) ++Controllers;
        bool Production = false;
        for (const UClass* C = It->GetClass(); C; C = C->GetSuperClass())
        {
            const FString P = C->GetPathName();
            Production |= P.StartsWith(TEXT("/Game/ParisCombat/")) || P.StartsWith(TEXT("/Script/Paris")) || P.Contains(TEXT("GripPolicy"));
        }
        if (Production) Contaminants.Add(MakeShared<FJsonValueString>(It->GetPathName()));
    }
    Result->SetNumberField(TEXT("characters"), Characters);
    Result->SetNumberField(TEXT("controllers"), Controllers);
    Result->SetArrayField(TEXT("production_contaminants"), Contaminants);
    return Text(Result);
}

FString UParisGridSurveyLibrary::SampleGridCells(ARecastNavMesh* NavMesh, ACharacter* Probe, const FString& RequestsJson)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> Requests;
    if (!Valid(NavMesh, Probe) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(RequestsJson), Requests))
    {
        Result->SetStringField(TEXT("error"), TEXT("Exact Editor-world native probe/navigation and JSON array required"));
        return Text(Result);
    }
    TArray<TSharedPtr<FJsonValue>> Samples;
    for (const auto& Request : Requests)
    {
        const auto In = Request->AsObject();
        if (In->HasField(TEXT("sight")) && In->GetBoolField(TEXT("sight")))
        {
            const double EyeHeight = In->GetNumberField(TEXT("eye_height_cm"));
            const FVector A = Vec(In,TEXT("start_feet_cm"))+FVector(0,0,EyeHeight);
            const FVector B = Vec(In,TEXT("end_feet_cm"))+FVector(0,0,EyeHeight);
            FCollisionQueryParams Params(SCENE_QUERY_STAT(ParisGridSight), false, Probe);
            FHitResult HitAB, HitBA;
            const bool BlockAB = Probe->GetWorld()->LineTraceSingleByChannel(HitAB,A,B,ECC_Visibility,Params);
            const bool BlockBA = Probe->GetWorld()->LineTraceSingleByChannel(HitBA,B,A,ECC_Visibility,Params);
            TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
            Row->SetNumberField(TEXT("id"),In->GetNumberField(TEXT("id")));
            Row->SetBoolField(TEXT("admitted"),!BlockAB && !BlockBA);
            Row->SetBoolField(TEXT("visible_ab"),!BlockAB);
            Row->SetBoolField(TEXT("visible_ba"),!BlockBA);
            Row->SetStringField(TEXT("blocker_ab"),HitAB.GetComponent() ? HitAB.GetComponent()->GetPathName() : TEXT(""));
            Row->SetStringField(TEXT("blocker_ba"),HitBA.GetComponent() ? HitBA.GetComponent()->GetPathName() : TEXT(""));
            Row->SetStringField(TEXT("reason"),!BlockAB && !BlockBA ? TEXT("visibility_pair_clear") : TEXT("visibility_blocked"));
            Samples.Add(MakeShared<FJsonValueObject>(Row));
            continue;
        }
        const NavNodeRef Ref = FCString::Strtoui64(*In->GetStringField(TEXT("p")), nullptr, 10);
        TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("id"), In->GetNumberField(TEXT("id")));
        Row->SetBoolField(TEXT("admitted"), false);
        const FVector Requested = Vec(In, TEXT("xyz"));
        FVector Surface = Requested;
        const bool ExactSurface = Ref && NavMesh->GetClosestPointOnPoly(Ref, Requested, Surface);
        Row->SetBoolField(TEXT("exact_surface"), ExactSurface);
        Row->SetArrayField(TEXT("nav_cm"), Coords(Surface));
        Row->SetNumberField(TEXT("xy_drift_cm"), FVector::Dist2D(Requested,Surface));
        // A non-nav diagnostic remains excluded even if its geometry is clear.
        if (Ref && (!ExactSurface || Surface.ContainsNaN() || FVector::Dist2D(Requested,Surface) > 0.01))
        {
            Result->SetStringField(TEXT("error"), TEXT("Required exact polygon surface/XY identity failed"));
            return Text(Result);
        }
        Row->SetArrayField(TEXT("requested_blockers"), Overlaps(Probe, Surface+FVector(0,0,HalfHeight+FloorGap)));
        FFindFloorResult Floor;
        const FVector QueryCenter = Surface+FVector(0,0,HalfHeight+30.0);
        Probe->GetCharacterMovement()->ComputeFloorDist(QueryCenter, 100.0, 100.0, Floor, Radius);
        Row->SetBoolField(TEXT("floor_walkable"), Floor.IsWalkableFloor());
        Row->SetBoolField(TEXT("floor_penetrating"), Floor.HitResult.bStartPenetrating);
        Row->SetNumberField(TEXT("floor_distance_cm"), Floor.GetDistanceToFloor());
        Row->SetArrayField(TEXT("floor_normal"), Coords(Floor.HitResult.ImpactNormal));
        Row->SetArrayField(TEXT("impact_cm"), Coords(Floor.HitResult.ImpactPoint));
        const UPrimitiveComponent* Component = Floor.HitResult.GetComponent();
        const AActor* Support = Floor.HitResult.GetActor();
        Row->SetStringField(TEXT("component"), Component ? Component->GetPathName() : TEXT(""));
        Row->SetStringField(TEXT("mesh"), MeshPath(Component));
        Row->SetStringField(TEXT("actor_class"), Support ? Support->GetClass()->GetPathName() : TEXT(""));
        const double FeetZ = QueryCenter.Z-Floor.GetDistanceToFloor()-HalfHeight+FloorGap;
        const FVector Feet(Surface.X, Surface.Y, FeetZ);
        Row->SetArrayField(TEXT("feet_cm"), Coords(Feet));
        const double HeightError = FMath::Abs(FeetZ-Surface.Z);
        Row->SetNumberField(TEXT("height_delta_cm"), HeightError);
        const auto Blockers = Overlaps(Probe, Feet+FVector(0,0,HalfHeight));
        Row->SetArrayField(TEXT("blockers"), Blockers);
        FString Reason;
        if (!ExactSurface) Reason = TEXT("outside_navigation");
        else if (!Floor.IsWalkableFloor() || Floor.HitResult.bStartPenetrating) Reason = TEXT("unsupported_or_nonwalkable_floor");
        else if (HeightError > 35.0) Reason = TEXT("surface_floor_height_mismatch");
        else if (Blockers.Num()) Reason = TEXT("capsule_blocked");
        else Reason = TEXT("geometry_clear");
        Row->SetStringField(TEXT("reason"), Reason);
        Row->SetBoolField(TEXT("admitted"), Reason == TEXT("geometry_clear"));
        Samples.Add(MakeShared<FJsonValueObject>(Row));
    }
    Result->SetArrayField(TEXT("samples"), Samples);
    return Text(Result);
}

FString UParisGridSurveyLibrary::SampleGridLinks(ARecastNavMesh* NavMesh, ACharacter* Probe, const FString& RequestsJson)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> Requests;
    if (!Valid(NavMesh, Probe) || !FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(RequestsJson), Requests))
    {
        Result->SetStringField(TEXT("error"), TEXT("Exact Editor probe/navigation and link JSON required"));
        return Text(Result);
    }
    TArray<TSharedPtr<FJsonValue>> Samples;
    for (const auto& Request : Requests)
    {
        const auto In = Request->AsObject();
        const NavNodeRef Ref = FCString::Strtoui64(*In->GetStringField(TEXT("p")), nullptr, 10);
        const FVector StartNav = Vec(In,TEXT("start_nav_cm")), EndNav = Vec(In,TEXT("end_nav_cm"));
        const FVector Start = Vec(In,TEXT("start_feet_cm"))+FVector(0,0,HalfHeight);
        const FVector End = Vec(In,TEXT("end_feet_cm"))+FVector(0,0,HalfHeight);
        TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
        Row->SetNumberField(TEXT("id"), In->GetNumberField(TEXT("id")));
        FNavLocation Reached;
        const bool MovedOnSurface = NavMesh->FindMoveAlongSurface(FNavLocation(StartNav,Ref), EndNav, Reached);
        Row->SetArrayField(TEXT("reached_nav_cm"), Coords(Reached.Location));
        Row->SetStringField(TEXT("reached_poly"), FString::Printf(TEXT("%llu"),static_cast<uint64>(Reached.NodeRef)));
        const bool SurfaceConnected = MovedOnSurface && FVector::Dist2D(Reached.Location,EndNav) <= 0.01 &&
            FMath::Abs(Reached.Location.Z-EndNav.Z) <= 1.0;
        FCollisionQueryParams Params(SCENE_QUERY_STAT(ParisGridLink), false, Probe);
        FHitResult Hit;
        const bool Blocked = Probe->GetWorld()->SweepSingleByChannel(Hit, Start, End, FQuat::Identity, ECC_Pawn,
            FCollisionShape::MakeCapsule(Radius,HalfHeight), Params);
        Row->SetBoolField(TEXT("surface_connected"), SurfaceConnected);
        Row->SetBoolField(TEXT("capsule_blocked"), Blocked);
        Row->SetStringField(TEXT("blocker"), Hit.GetComponent() ? Hit.GetComponent()->GetPathName() : TEXT(""));
        const bool HeightOK = FMath::Abs(End.Z-Start.Z) <= 45.0;
        Row->SetBoolField(TEXT("admitted"), SurfaceConnected && !Blocked && HeightOK);
        Row->SetStringField(TEXT("reason"), !SurfaceConnected ? TEXT("surface_connection_missing") :
            Blocked ? TEXT("capsule_sweep_blocked") : !HeightOK ? TEXT("height_step_exceeded") : TEXT("geometry_link_clear"));
        Samples.Add(MakeShared<FJsonValueObject>(Row));
    }
    Result->SetArrayField(TEXT("samples"), Samples);
    return Text(Result);
}
