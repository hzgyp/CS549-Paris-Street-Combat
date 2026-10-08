#include "ParisFormalSurveyLibrary.h"
#include "AIController.h"
#include "Components/CapsuleComponent.h"
#include "Dom/JsonObject.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Modules/ModuleManager.h"
#include "Navigation/PathFollowingComponent.h"
#include "NavigationSystem.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, ParisFormalSurveyV1)
namespace
{
TWeakObjectPtr<UWorld> ObservedWorld;
TSet<TWeakObjectPtr<AController>> ObservedControllers;
TArray<TSharedPtr<FJsonValue>> Events;
TArray<TSharedPtr<FJsonValue>> VectorArray(const FVector& V)
{ return {MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)}; }
FString Encode(const TSharedRef<FJsonObject>& O)
{ FString S; FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&S)); return S; }
bool Admitted(const ACharacter* C)
{ return IsValid(C) && C->GetWorld()->WorldType==EWorldType::PIE && C->GetClass()->GetPathName().StartsWith(TEXT("/Game/ParisCombat/")); }
void Observe(AController* C,UPathFollowingComponent* P)
{
    if(ObservedWorld.Get()!=C->GetWorld()){ObservedWorld=C->GetWorld();ObservedControllers.Empty();Events.Empty();}
    if(ObservedControllers.Contains(C)) return;
    ObservedControllers.Add(C);
    const TWeakObjectPtr<AController> Weak(C);
    P->OnRequestFinished.AddLambda([Weak](FAIRequestID ID,const FPathFollowingResult& Result)
    {
        if(!Weak.IsValid()) return;
        const auto O=MakeShared<FJsonObject>();
        O->SetStringField(TEXT("controller"),Weak->GetPathName());
        O->SetNumberField(TEXT("request_id"),ID.GetID());
        O->SetNumberField(TEXT("result_code"),static_cast<int32>(Result.Code));
        O->SetStringField(TEXT("result"),UEnum::GetValueAsString(Result.Code));
        O->SetNumberField(TEXT("game_seconds"),Weak->GetWorld()->GetTimeSeconds());
        Events.Add(MakeShared<FJsonValueObject>(O));
    });
}
}
FString UParisFormalSurveyLibrary::ReadFormalCharacter(ACharacter* C)
{
    const auto O=MakeShared<FJsonObject>();
    if(!Admitted(C)){O->SetStringField(TEXT("error"),TEXT("Formal Paris PIE Character required"));return Encode(O);}
    const auto* M=C->GetCharacterMovement();const auto& F=M->CurrentFloor;
    O->SetStringField(TEXT("class"),C->GetClass()->GetPathName());
    O->SetArrayField(TEXT("body_cm"),VectorArray(C->GetActorLocation()));
    FVector Feet=C->GetActorLocation();Feet.Z-=C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    O->SetArrayField(TEXT("feet_cm"),VectorArray(Feet));
    O->SetNumberField(TEXT("radius_cm"),C->GetCapsuleComponent()->GetScaledCapsuleRadius());
    O->SetNumberField(TEXT("half_height_cm"),C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
    O->SetBoolField(TEXT("walkable_floor"),F.IsWalkableFloor());
    O->SetBoolField(TEXT("blocking_floor"),F.bBlockingHit);
    O->SetNumberField(TEXT("floor_distance_cm"),F.FloorDist);
    O->SetArrayField(TEXT("impact_cm"),VectorArray(F.HitResult.ImpactPoint));
    O->SetArrayField(TEXT("normal"),VectorArray(F.HitResult.ImpactNormal));
    O->SetStringField(TEXT("floor_actor"),GetPathNameSafe(F.HitResult.GetActor()));
    O->SetStringField(TEXT("floor_component"),GetPathNameSafe(F.HitResult.GetComponent()));
    O->SetNumberField(TEXT("movement_mode"),static_cast<int32>(M->MovementMode));
    O->SetNumberField(TEXT("max_speed_cm_s"),M->MaxWalkSpeed);
    O->SetNumberField(TEXT("max_step_cm"),M->MaxStepHeight);
    O->SetNumberField(TEXT("slope_degrees"),M->GetWalkableFloorAngle());
    O->SetNumberField(TEXT("gravity_scale"),M->GravityScale);
    O->SetBoolField(TEXT("rvo"),M->bUseRVOAvoidance);
    return Encode(O);
}
FString UParisFormalSurveyLibrary::ReadFormalController(AController* C)
{
    const auto O=MakeShared<FJsonObject>();
    if(!IsValid(C)||!Admitted(Cast<ACharacter>(C->GetPawn()))){O->SetStringField(TEXT("error"),TEXT("Possessed formal PIE Character required"));return Encode(O);}
    auto* P=C->FindComponentByClass<UPathFollowingComponent>();
    if(P) Observe(C,P);
    O->SetStringField(TEXT("controller"),C->GetPathName());
    O->SetStringField(TEXT("pawn"),C->GetPawn()->GetPathName());
    O->SetNumberField(TEXT("status_code"),P?static_cast<int32>(P->GetStatus()):0);
    O->SetNumberField(TEXT("request_id"),P&&P->GetCurrentRequestId().IsValid()?P->GetCurrentRequestId().GetID():-1);
    O->SetArrayField(TEXT("events"),Events);
    return Encode(O);
}
FString UParisFormalSurveyLibrary::BeginFormalMove(AController* C,FVector Goal)
{
    const auto O=MakeShared<FJsonObject>();auto* Character=IsValid(C)?Cast<ACharacter>(C->GetPawn()):nullptr;
    if(!Admitted(Character)){O->SetStringField(TEXT("error"),TEXT("Possessed formal PIE Character required"));return Encode(O);}
    auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(C->GetWorld());
    FVector Feet=Character->GetActorLocation();Feet.Z-=Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
    const auto* Data=Nav?Nav->GetNavDataForProps(Character->GetNavAgentPropertiesRef(),Feet):nullptr;
    if(!Data){O->SetStringField(TEXT("rejection"),TEXT("missing_saved_navigation_data"));return Encode(O);}
    const FPathFindingQuery Query(C,*Data,Feet,Goal);
    const auto Found=Nav->FindPathSync(Query);
    if(!Found.IsSuccessful()||!Found.Path.IsValid()||Found.Path->IsPartial()){O->SetStringField(TEXT("rejection"),TEXT("missing_or_partial_saved_path"));return Encode(O);}
    auto* P=C->FindComponentByClass<UPathFollowingComponent>();
    if(!P && Cast<APlayerController>(C))
    { P=NewObject<UPathFollowingComponent>(C);C->AddInstanceComponent(P);P->RegisterComponentWithWorld(C->GetWorld());P->Initialize(); }
    if(!P||!P->IsPathFollowingAllowed()){O->SetStringField(TEXT("error"),TEXT("Original native path following unavailable"));return Encode(O);}
    Observe(C,P);
    if(P->GetStatus()!=EPathFollowingStatus::Idle){O->SetStringField(TEXT("error"),TEXT("Do not override active policy request"));return Encode(O);}
    FAIMoveRequest Request(Goal);Request.SetAcceptanceRadius(30.f);Request.SetAllowPartialPath(false);
    Request.SetProjectGoalLocation(false);Request.SetReachTestIncludesAgentRadius(false);Request.SetReachTestIncludesGoalRadius(false);
    const auto ID=P->RequestMove(Request,Found.Path);
    O->SetBoolField(TEXT("started"),ID.IsValid());O->SetNumberField(TEXT("request_id"),ID.GetID());O->SetStringField(TEXT("controller"),C->GetPathName());
    O->SetArrayField(TEXT("goal_cm"),VectorArray(Goal));
    TArray<TSharedPtr<FJsonValue>> Points;for(const auto& Point:Found.Path->GetPathPoints())Points.Add(MakeShared<FJsonValueArray>(VectorArray(Point.Location)));
    O->SetArrayField(TEXT("path_cm"),Points);O->SetNumberField(TEXT("path_length_cm"),Found.Path->GetLength());
    return Encode(O);
}
