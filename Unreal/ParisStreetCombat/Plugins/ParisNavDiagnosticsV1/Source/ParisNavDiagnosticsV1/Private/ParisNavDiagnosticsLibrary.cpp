#include "ParisNavDiagnosticsLibrary.h"
#include "AIController.h"
#include "AI/Navigation/NavQueryFilter.h"
#include "Dom/JsonObject.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Modules/ModuleManager.h"
#include "NavigationSystem.h"
#include "NavFilters/NavigationQueryFilter.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonWriter.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, ParisNavDiagnosticsV1)
namespace
{
TArray<TSharedPtr<FJsonValue>> V(const FVector& P)
{return {MakeShared<FJsonValueNumber>(P.X),MakeShared<FJsonValueNumber>(P.Y),MakeShared<FJsonValueNumber>(P.Z)};}
FString Encode(const TSharedRef<FJsonObject>& O)
{FString S;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&S));return S;}
}
FString UParisNavDiagnosticsLibrary::InspectStandardQuery(AAIController* C,FVector Goal,int32 Budget)
{
    const auto O=MakeShared<FJsonObject>();
    const auto* Character=IsValid(C)?Cast<ACharacter>(C->GetPawn()):nullptr;
    if(!Character||C->GetWorld()->WorldType!=EWorldType::PIE||!Character->GetClass()->GetPathName().StartsWith(TEXT("/Game/ParisCombat/"))||(Budget!=0&&Budget!=65536))
    {O->SetStringField(TEXT("error"),TEXT("Original formal PIE controller and bounded budget required"));return Encode(O);}
    auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(C->GetWorld());
    if(!Nav){O->SetStringField(TEXT("error"),TEXT("Missing native navigation"));return Encode(O);}
    const auto& Agent=C->GetNavAgentPropertiesRef();FNavLocation Projected;
    O->SetArrayField(TEXT("source_cm"),V(C->GetNavAgentLocation()));
    O->SetNumberField(TEXT("agent_radius_cm"),Agent.AgentRadius);O->SetNumberField(TEXT("agent_height_cm"),Agent.AgentHeight);
    O->SetStringField(TEXT("original_filter_class"),GetPathNameSafe(C->GetDefaultNavigationFilterClass().Get()));
    const bool GoalProjected=Nav->ProjectPointToNavigation(Goal,Projected,INVALID_NAVEXTENT,&Agent);
    O->SetBoolField(TEXT("goal_projected"),GoalProjected);O->SetNumberField(TEXT("budget_override"),Budget);
    if(!GoalProjected)return Encode(O);
    O->SetArrayField(TEXT("goal_projected_cm"),V(Projected.Location));
    FAIMoveRequest Request(Projected.Location);Request.SetUsePathfinding(true);Request.SetAllowPartialPath(true);
    Request.SetNavigationFilter(C->GetDefaultNavigationFilterClass());
    FPathFindingQuery Query;
    if(!C->BuildPathfindingQuery(Request,Query)||!Query.QueryFilter.IsValid())
    {O->SetStringField(TEXT("error"),TEXT("Original standard query construction unavailable"));return Encode(O);}
    O->SetNumberField(TEXT("original_max_search_nodes"),Query.QueryFilter->GetMaxSearchNodes());
    if(Budget)
    {const auto Copy=Query.QueryFilter->GetCopy();Copy->SetMaxSearchNodes(Budget);Query.QueryFilter=Copy;}
    O->SetNumberField(TEXT("effective_max_search_nodes"),Query.QueryFilter->GetMaxSearchNodes());
    O->SetStringField(TEXT("nav_data"),GetPathNameSafe(Query.NavData.Get()));
    const auto Found=Nav->FindPathSync(Query);
    O->SetNumberField(TEXT("result_code"),static_cast<int32>(Found.Result));
    O->SetBoolField(TEXT("success"),Found.IsSuccessful());O->SetBoolField(TEXT("path_valid"),Found.Path.IsValid()&&Found.Path->IsValid());
    if(Found.Path.IsValid())
    {
        O->SetBoolField(TEXT("partial"),Found.Path->IsPartial());O->SetBoolField(TEXT("search_reached_limit"),Found.Path->DidSearchReachedLimit());
        O->SetNumberField(TEXT("length_cm"),Found.Path->GetLength());
        TArray<TSharedPtr<FJsonValue>> Points;
        for(const auto& P:Found.Path->GetPathPoints())Points.Add(MakeShared<FJsonValueArray>(V(P.Location)));
        O->SetArrayField(TEXT("points_cm"),Points);
    }
    O->SetBoolField(TEXT("movement_submitted"),false);return Encode(O);
}
