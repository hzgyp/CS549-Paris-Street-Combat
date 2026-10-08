#include "ParisMapSurveyLibrary.h"
#include "NavMesh/RecastNavMesh.h"
#include "NavigationSystem.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"
#include "Modules/ModuleManager.h"
#include "EngineUtils.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/PrimitiveComponent.h"
#include "AIController.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, ParisMapSurveyV1)

int64 UParisMapSurveyLibrary::DecodeRequestId(FAIRequestID RequestId)
{
    return RequestId.IsValid() ? static_cast<int64>(RequestId.GetID()) : -1;
}

int64 UParisMapSurveyLibrary::CurrentRequestId(AAIController* Controller)
{
    if (!IsValid(Controller) || Controller->GetClass() != AAIController::StaticClass() || Controller->GetWorld()->WorldType != EWorldType::PIE) return -1;
    return DecodeRequestId(Controller->GetCurrentMoveRequestID());
}

bool UParisMapSurveyLibrary::DestroySurveyProbe(ACharacter* Probe, AAIController* Controller)
{
    if (!IsValid(Probe) || Probe->GetClass() != ACharacter::StaticClass() ||
        !IsValid(Controller) || Controller->GetClass() != AAIController::StaticClass() ||
        Probe->GetWorld() != Controller->GetWorld() || Probe->GetWorld()->WorldType != EWorldType::PIE ||
        Controller->GetPawn() != Probe) return false;
    Controller->StopMovement();
    Controller->UnPossess();
    const bool ControllerDestroyed = Controller->Destroy();
    const bool ProbeDestroyed = Probe->Destroy();
    return ControllerDestroyed && ProbeDestroyed;
}

FString UParisMapSurveyLibrary::InspectSurveyWorld(UWorld* World)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    if (!IsValid(World) || World->WorldType != EWorldType::PIE)
    {
        Result->SetStringField(TEXT("error"), TEXT("Explicit PIE world required"));
    }
    else
    {
        int32 Characters = 0, AIControllers = 0;
        TMap<const UClass*, bool> ClassIsProduction;
        TArray<TSharedPtr<FJsonValue>> Contaminants;
        for (TActorIterator<AActor> It(World); It; ++It)
        {
            if (It->IsA<ACharacter>()) ++Characters;
            if (It->IsA<AAIController>()) ++AIControllers;
            const UClass* ActorClass = It->GetClass();
            if (!ClassIsProduction.Contains(ActorClass))
            {
                bool bProduction = false;
                for (const UClass* Class = ActorClass; Class; Class = Class->GetSuperClass())
                {
                    const FString Path = Class->GetPathName();
                    bProduction |= Path.StartsWith(TEXT("/Game/ParisCombat/")) || Path.StartsWith(TEXT("/Script/Paris")) || Path.Contains(TEXT("GripPolicy"));
                }
                ClassIsProduction.Add(ActorClass, bProduction);
            }
            if (ClassIsProduction[ActorClass])
                Contaminants.Add(MakeShared<FJsonValueString>(ActorClass->GetPathName()));
        }
        Result->SetNumberField(TEXT("characters"), Characters);
        Result->SetNumberField(TEXT("ai_controllers"), AIControllers);
        Result->SetArrayField(TEXT("production_contaminants"), Contaminants);
    }
    FString Text;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Text);
    FJsonSerializer::Serialize(Result, Writer);
    return Text;
}

namespace
{
TArray<TSharedPtr<FJsonValue>> Coordinates(const FVector& V)
{
    return {MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z)};
}
}

FString UParisMapSurveyLibrary::ExportNavmesh(ARecastNavMesh* NavMesh)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    if (!IsValid(NavMesh))
    {
        Result->SetStringField(TEXT("error"), TEXT("Invalid explicit Recast instance"));
    }
    else
    {
        TArray<FNavTileRef> Tiles;
        NavMesh->GetAllNavMeshTiles(Tiles);
        TArray<TSharedPtr<FJsonValue>> Polygons;
        TSet<NavNodeRef> Seen;
        int32 Invalid = 0;
        int32 VacantSlots = 0, ActiveExported = 0, EmptyGroundTiles = 0;
        for (const FNavTileRef Tile : Tiles)
        {
            int32 TileX = 0, TileY = 0, TileLayer = 0;
            if (!NavMesh->GetNavMeshTileXY(Tile, TileX, TileY, TileLayer)) { ++VacantSlots; continue; }
            ++ActiveExported;
            TArray<FNavPoly> TilePolys;
            if (!NavMesh->GetPolysInTile(Tile, TilePolys)) { ++EmptyGroundTiles; continue; }
            for (const FNavPoly& Poly : TilePolys)
            {
                if (Seen.Contains(Poly.Ref)) { ++Invalid; continue; }
                Seen.Add(Poly.Ref);
                FVector Center;
                TArray<FVector> Vertices;
                TArray<FNavigationPortalEdge> Neighbors;
                if (!NavMesh->GetPolyCenter(Poly.Ref, Center) || !NavMesh->GetPolyVerts(Poly.Ref, Vertices))
                { ++Invalid; continue; }
                FVector Surface;
                if (!NavMesh->GetClosestPointOnPoly(Poly.Ref, Center, Surface) || Surface.ContainsNaN() ||
                    FVector::Dist2D(Center, Surface) > 0.01)
                { ++Invalid; continue; }
                NavMesh->GetPolyNeighbors(Poly.Ref, Neighbors);
                TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
                Row->SetStringField(TEXT("id"), FString::Printf(TEXT("%llu"), static_cast<uint64>(Poly.Ref)));
                Row->SetArrayField(TEXT("center_cm"), Coordinates(Center));
                Row->SetArrayField(TEXT("surface_cm"), Coordinates(Surface));
                Row->SetNumberField(TEXT("surface_xy_drift_cm"), FVector::Dist2D(Center, Surface));
                Row->SetNumberField(TEXT("surface_minus_center_z_cm"), Surface.Z - Center.Z);
                Row->SetNumberField(TEXT("tile_x"), TileX);
                Row->SetNumberField(TEXT("tile_y"), TileY);
                Row->SetNumberField(TEXT("tile_layer"), TileLayer);
                TArray<TSharedPtr<FJsonValue>> Verts;
                for (const FVector& V : Vertices) { Verts.Add(MakeShared<FJsonValueArray>(Coordinates(V))); }
                Row->SetArrayField(TEXT("vertices_cm"), Verts);
                TArray<TSharedPtr<FJsonValue>> Portals;
                for (const FNavigationPortalEdge& N : Neighbors)
                {
                    TSharedRef<FJsonObject> Portal = MakeShared<FJsonObject>();
                    Portal->SetStringField(TEXT("to"), FString::Printf(TEXT("%llu"), static_cast<uint64>(N.ToRef)));
                    Portal->SetArrayField(TEXT("left_cm"), Coordinates(N.Left));
                    Portal->SetArrayField(TEXT("right_cm"), Coordinates(N.Right));
                    Portal->SetNumberField(TEXT("width_cm"), FVector::Dist(N.Left, N.Right));
                    Portals.Add(MakeShared<FJsonValueObject>(Portal));
                }
                Row->SetArrayField(TEXT("neighbors"), Portals);
                Polygons.Add(MakeShared<FJsonValueObject>(Row));
            }
        }
        Result->SetNumberField(TEXT("active_tiles"), NavMesh->GetNumActiveTiles());
        Result->SetNumberField(TEXT("exported_tiles"), ActiveExported);
        Result->SetNumberField(TEXT("capacity_slots"), Tiles.Num());
        Result->SetNumberField(TEXT("vacant_slots"), VacantSlots);
        Result->SetNumberField(TEXT("empty_ground_tiles"), EmptyGroundTiles);
        Result->SetNumberField(TEXT("invalid_records"), Invalid);
        Result->SetStringField(TEXT("sampling_version"), TEXT("native_specific_polygon_surface_v2"));
        Result->SetArrayField(TEXT("polygons"), Polygons);
    }
    FString Text;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Text);
    FJsonSerializer::Serialize(Result, Writer);
    return Text;
}

FString UParisMapSurveyLibrary::NavigationBuildState(UNavigationSystemV1* NavigationSystem)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    if (!IsValid(NavigationSystem))
    {
        Result->SetStringField(TEXT("error"), TEXT("Invalid explicit navigation system"));
    }
    else
    {
        // Manual editor build ignores only the editor auto-update preference,
        // exactly like UNavigationSystemV1::Build. Never clear an async/custom lock.
        const uint8 RelevantLocks = static_cast<uint8>(~ENavigationBuildLock::NoUpdateInEditor);
        Result->SetBoolField(TEXT("manual_build_locked"), NavigationSystem->IsNavigationBuildingLocked(RelevantLocks));
        TArray<TSharedPtr<FJsonValue>> Bounds;
        for (const FNavigationBounds& B : NavigationSystem->GetNavigationBounds())
        {
            TSharedRef<FJsonObject> Row = MakeShared<FJsonObject>();
            Row->SetArrayField(TEXT("min_cm"), Coordinates(B.AreaBox.Min));
            Row->SetArrayField(TEXT("max_cm"), Coordinates(B.AreaBox.Max));
            Bounds.Add(MakeShared<FJsonValueObject>(Row));
        }
        Result->SetArrayField(TEXT("registered_bounds"), Bounds);
    }
    FString Text;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Text);
    FJsonSerializer::Serialize(Result, Writer);
    return Text;
}

FString UParisMapSurveyLibrary::SurveyFloorState(ACharacter* Probe)
{
    TSharedRef<FJsonObject> Result = MakeShared<FJsonObject>();
    if (!IsValid(Probe) || Probe->GetClass() != ACharacter::StaticClass() || Probe->GetWorld()->WorldType != EWorldType::PIE)
        Result->SetStringField(TEXT("error"), TEXT("Exact native PIE probe required"));
    else
    {
        const UCharacterMovementComponent* Movement = Probe->GetCharacterMovement();
        const FFindFloorResult& Floor = Movement->CurrentFloor;
        Result->SetBoolField(TEXT("walkable_floor"), Floor.IsWalkableFloor());
        Result->SetBoolField(TEXT("blocking_hit"), Floor.bBlockingHit);
        Result->SetNumberField(TEXT("floor_distance_cm"), Floor.FloorDist);
        Result->SetArrayField(TEXT("impact_cm"), Coordinates(Floor.HitResult.ImpactPoint));
        Result->SetArrayField(TEXT("normal"), Coordinates(Floor.HitResult.ImpactNormal));
        if (const AActor* Actor = Floor.HitResult.GetActor())
        {
            Result->SetStringField(TEXT("actor"), Actor->GetPathName());
            Result->SetStringField(TEXT("actor_class"), Actor->GetClass()->GetPathName());
        }
        if (const UPrimitiveComponent* Component = Floor.HitResult.GetComponent())
            Result->SetStringField(TEXT("component"), Component->GetPathName());
        Result->SetNumberField(TEXT("max_simulation_time_step"), Movement->MaxSimulationTimeStep);
        Result->SetNumberField(TEXT("max_simulation_iterations"), Movement->MaxSimulationIterations);
    }
    FString Text;
    const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Text);
    FJsonSerializer::Serialize(Result, Writer);
    return Text;
}
