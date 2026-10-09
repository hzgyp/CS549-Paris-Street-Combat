#include "ParisBridgeMission.h"
#include "AIController.h"
#include "BehaviorTree/BehaviorTree.h"
#include "BehaviorTree/BehaviorTreeComponent.h"
#include "BehaviorTree/BTCompositeNode.h"
#include "BehaviorTree/BTDecorator.h"
#include "BehaviorTree/BTService.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "BrainComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SceneComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Dom/JsonObject.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/SecureHash.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"
#include "NavMesh/RecastNavMesh.h"
#include "NavAreas/NavArea_Null.h"
#include "Perception/PawnSensingComponent.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"
#include <limits>
#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetBlueprintLibrary.h"
#include "Camera/CameraComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/Texture2D.h"
#include "ImageUtils.h"
#include "HAL/PlatformProcess.h"
#include "Misc/Paths.h"
#include "CanvasItem.h"
#include "Fonts/CompositeFont.h"
#include "Fonts/SlateFontInfo.h"
#include "GlobalRenderResources.h"
#include "Engine/Font.h"
#include "UObject/StrongObjectPtr.h"

namespace ParisG1
{
const TCHAR* Ids[] = { TEXT("Player"), TEXT("Ally1"), TEXT("Ally2"), TEXT("German1"), TEXT("German2"), TEXT("German3") };
FProperty* Property(const UObject* O, const TCHAR* N) { return O ? O->GetClass()->FindPropertyByName(N) : nullptr; }
double Number(const UObject* O, const TCHAR* N)
{
    const auto* P = CastField<FNumericProperty>(Property(O,N));
    if (!P) return std::numeric_limits<double>::quiet_NaN();
    const void* V = P->ContainerPtrToValuePtr<void>(O);
    return P->IsFloatingPoint() ? P->GetFloatingPointPropertyValue(V) : double(P->GetSignedIntPropertyValue(V));
}
bool SetNumber(UObject* O, const TCHAR* N, double V)
{
    auto* P = CastField<FNumericProperty>(Property(O,N));
    if (!P || !FMath::IsFinite(V)) return false;
    void* D = P->ContainerPtrToValuePtr<void>(O);
    if (P->IsFloatingPoint()) P->SetFloatingPointPropertyValue(D,V); else P->SetIntPropertyValue(D,int64(V));
    return true;
}
bool Flag(const UObject* O, const TCHAR* N)
{
    const auto* P = CastField<FBoolProperty>(Property(O,N)); return P && P->GetPropertyValue_InContainer(O);
}
FString Name(const UObject* O, const TCHAR* N)
{
    const auto* P = CastField<FNameProperty>(Property(O,N)); return P ? P->GetPropertyValue_InContainer(O).ToString() : FString();
}
UObject* Object(const UObject* O, const TCHAR* N)
{
    const auto* P = CastField<FObjectPropertyBase>(Property(O,N)); return P ? P->GetObjectPropertyValue_InContainer(O) : nullptr;
}
bool Invoke(UObject* O, const TCHAR* N, const TCHAR* Arg=nullptr, double V=0)
{
    UFunction* F = O ? O->FindFunction(N) : nullptr;
    if (!F) return false;
    FStructOnScope Parameters(F);
    if (Arg)
    {
        FProperty* P = F->FindPropertyByName(Arg);
        if (auto* B = CastField<FBoolProperty>(P)) B->SetPropertyValue_InContainer(Parameters.GetStructMemory(), V != 0);
        else if (auto* D = CastField<FDoubleProperty>(P)) D->SetPropertyValue_InContainer(Parameters.GetStructMemory(),V);
        else return false;
    }
    O->ProcessEvent(F,Parameters.GetStructMemory()); return true;
}
void CancelOriginalReload(UObject* O)
{
    if(Name(O,TEXT("ActionState"))!=TEXT("Reloading")) return;
    UFunction* F=O->FindFunction(TEXT("PC_EndReload")); if(!F) return;
    FStructOnScope Parameters(F);
    for(const auto& P : {TPair<const TCHAR*,const TCHAR*>(TEXT("ExpectedActionID"),TEXT("ReloadActionID")),TPair<const TCHAR*,const TCHAR*>(TEXT("ExpectedGeneration"),TEXT("ReloadGeneration"))})
    {
        auto* Field=CastField<FIntProperty>(F->FindPropertyByName(P.Key));
        if(!Field || !FMath::IsFinite(Number(O,P.Value))) return;
        Field->SetPropertyValue_InContainer(Parameters.GetStructMemory(),int32(Number(O,P.Value)));
    }
    O->ProcessEvent(F,Parameters.GetStructMemory());
}
TSharedPtr<FJsonObject> Parse(const FString& Text)
{
    TSharedPtr<FJsonObject> O; auto R = TJsonReaderFactory<>::Create(Text);
    return FJsonSerializer::Deserialize(R,O) ? O : nullptr;
}
FString Json(const TSharedPtr<FJsonObject>& O)
{
    FString S; auto W = TJsonWriterFactory<>::Create(&S); FJsonSerializer::Serialize(O.ToSharedRef(),W); return S;
}
TArray<TSharedPtr<FJsonValue>> Vector(const FVector& V)
{
    return { MakeShared<FJsonValueNumber>(V.X), MakeShared<FJsonValueNumber>(V.Y), MakeShared<FJsonValueNumber>(V.Z) };
}
bool GetVector(const TSharedPtr<FJsonObject>& O, const TCHAR* N, FVector& V)
{
    const TArray<TSharedPtr<FJsonValue>>* A=nullptr;
    if (!O->TryGetArrayField(N,A) || A->Num()!=3) return false;
    double X,Y,Z;
    if (!(*A)[0]->TryGetNumber(X) || !(*A)[1]->TryGetNumber(Y) || !(*A)[2]->TryGetNumber(Z) || !FMath::IsFinite(X) || !FMath::IsFinite(Y) || !FMath::IsFinite(Z)) return false;
    V=FVector(X,Y,Z); return true;
}
bool InRange(const TSharedPtr<FJsonObject>& O, const TCHAR* N, double Min, double Max, bool Integer=false)
{
    double V;
    return O->TryGetNumberField(N,V) && FMath::IsFinite(V) && V>=Min && V<=Max && (!Integer || FMath::FloorToDouble(V)==V);
}
FString Hash(const FString& S)
{
    FTCHARToUTF8 B(*S); return FMD5::HashBytes(reinterpret_cast<const uint8*>(B.Get()),B.Length());
}
}

using namespace ParisG1;

AParisBridgeMission::AParisBridgeMission()
{
    PrimaryActorTick.bCanEverTick=true;
    PrimaryActorTick.TickGroup=TG_PostUpdateWork;
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("MissionRoot")));
}

AParisBridgeMission* AParisBridgeMission::Find(const UObject* Context)
{
    UWorld* W=Context ? Context->GetWorld() : nullptr;
    if (W) for (TActorIterator<AParisBridgeMission> I(W);I;++I) return *I;
    return nullptr;
}

void AParisBridgeMission::BeginPlay()
{
    Super::BeginPlay();
    RunGeneration=FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
    ConfigFingerprint+=TEXT("_BridgeConstraintV2FeetPlan_HumanPlaytestUXV5");
    SlotPrefix=TEXT("ParisG1V5");
    FString Prefix;
    if (FParse::Value(FCommandLine::Get(),TEXT("ParisSavePrefix="),Prefix) && Prefix.Len()<=64)
    {
        bool Valid=!Prefix.IsEmpty(); for(TCHAR C : Prefix) Valid &= FChar::IsAlnum(C) || C==TEXT('_');
        if(Valid) SlotPrefix=Prefix;
    }
    bLoadRequested=GetWorld()->URL.HasOption(TEXT("ParisLoad"));
    UE_LOG(LogTemp,Display,TEXT("PARIS_G1_BEGIN generation=%s load=%d"),*RunGeneration,bLoadRequested);
}

bool AParisBridgeMission::AllowsPlay() const
{
    return !bTravelPending && (Phase==TEXT("Crossing") || Phase==TEXT("Clearing") || Phase==TEXT("Occupying"));
}

void AParisBridgeMission::SetPhase(const FString& Value)
{
    if (Phase==Value) return;
    Phase=Value;
    UE_LOG(LogTemp,Display,TEXT("PARIS_G1_PHASE %s generation=%s"),*Phase,*RunGeneration);
}

void AParisBridgeMission::Fail(const FString& Reason)
{
    Feedback=Reason; SetPhase(TEXT("Error")); GateBrains(false);
    UE_LOG(LogTemp,Warning,TEXT("PARIS_G1_STOP %s"),*Reason);
}

bool AParisBridgeMission::SealRegistry(FString& Error)
{
    Roster.Reset(); StableIds.Reset(); InitialShots.Reset(); InitialResources.Reset(); InitialLocations.Reset();
    for (const TCHAR* Id : Ids)
    {
        ACharacter* Found=nullptr; FName Tag(*(FString(TEXT("G1_"))+Id));
        for (TActorIterator<ACharacter> I(GetWorld());I;++I) if (I->ActorHasTag(Tag))
        {
            if (Found) { Error=TEXT("Duplicate roster identity ")+FString(Id); return false; }
            Found=*I;
        }
        if (!Found) { Error=TEXT("Missing roster identity ")+FString(Id); return false; }
        for (const TCHAR* Field : {TEXT("Health"),TEXT("LoadedAmmo"),TEXT("ReserveAmmo"),TEXT("ShotSequence")})
            if (!FMath::IsFinite(Number(Found,Field))) { Error=TEXT("Incompatible roster resource field"); return false; }
        if (!Property(Found,TEXT("IsDead")) || !Found->FindFunction(TEXT("PC_ResetLifecycle")) || !Found->FindFunction(TEXT("PC_Die")))
        { Error=TEXT("Incompatible roster lifecycle"); return false; }
        Roster.Add(Found); StableIds.Add(Id);
        InitialShots.Add(int64(Number(Found,TEXT("ShotSequence"))));
        InitialResources.Add(FVector(Number(Found,TEXT("Health")),Number(Found,TEXT("LoadedAmmo")),Number(Found,TEXT("ReserveAmmo"))));
        InitialLocations.Add(Found->GetActorLocation());
    }
    bRegistrySealed=true; return true;
}

bool AParisBridgeMission::EquipmentReady(FString& Error)
{
    for (int32 I=0;I<Roster.Num();++I)
    {
        ACharacter* C=Roster[I];
        if (!IsValid(C)) { Error=TEXT("Required actor disappeared"); return false; }
        if (Flag(C,TEXT("IsDead")) || Number(C,TEXT("ShotSequence"))!=InitialShots[I] ||
            FVector(Number(C,TEXT("Health")),Number(C,TEXT("LoadedAmmo")),Number(C,TEXT("ReserveAmmo")))!=InitialResources[I])
        { Error=TEXT("Resources changed before mission admission"); return false; }
        if (FVector::Dist2D(C->GetActorLocation(),InitialLocations[I])>35)
        { Error=TEXT("Body moved before mission admission"); return false; }
        if (!C->GetCharacterMovement()->IsMovingOnGround()) return false;
        if (I==0)
        {
            if (!C->IsPlayerControlled()) return false;
            continue;
        }
        AAIController* A=Cast<AAIController>(C->GetController()); if (!A) return false;
        if (Flag(A,TEXT("BootstrapFailed"))) { Error=TEXT("Original equipment bootstrap failed"); return false; }
        // Mission children have no tree during preparation; bootstrap cannot admit a task.
        if (!Invoke(A,TEXT("PC_BootstrapCombat")) || !Invoke(A,TEXT("PC_EnableCombat"),TEXT("Enabled"),0))
        { Error=TEXT("Missing original bootstrap/admission endpoint"); return false; }
        if (!Flag(A,TEXT("BootstrapReady"))) return false;
        if (A->GetBrainComponent() && A->GetBrainComponent()->IsRunning())
        { Error=TEXT("Behavior tree ran before Start"); return false; }
        UObject* Gun=Object(C,TEXT("WeaponAppearance"));
        if (!IsValid(Gun) || Object(Gun,TEXT("Combatant"))!=C || Object(Gun,TEXT("GripMesh"))!=C->GetMesh()) return false;
    }
    return true;
}

void AParisBridgeMission::GateBrains(bool bEnable)
{
    if(!bEnable) for(ACharacter* C : Roster) if(IsValid(C)) CancelOriginalReload(C);
    for (int32 I=1;I<Roster.Num();++I) if (IsValid(Roster[I]))
    {
        AAIController* A=Cast<AAIController>(Roster[I]->GetController()); if(!A) continue;
        Invoke(A,TEXT("PC_EnableCombat"),TEXT("Enabled"),bEnable && !Flag(Roster[I],TEXT("IsDead")));
        if (!bEnable || Flag(Roster[I],TEXT("IsDead")))
        {
            A->StopMovement();
            if(A->GetBrainComponent()) A->GetBrainComponent()->StopLogic(TEXT("G1 mission admission closed"));
            Roster[I]->GetCharacterMovement()->StopMovementImmediately();
        }
        else if (RetainedTree) A->RunBehaviorTree(RetainedTree);
    }
    if(APlayerController* P=UGameplayStatics::GetPlayerController(this,0))
    {
        P->SetIgnoreMoveInput(!bEnable); P->SetIgnoreLookInput(!bEnable);
        if(P->PlayerInput && !bEnable) P->PlayerInput->FlushPressedKeys();
        if(!bEnable && P->GetPawn()) P->GetPawn()->ConsumeMovementInputVector();
    }
    bReleased=bEnable;
}

bool AParisBridgeMission::StartMission()
{
    if (Phase!=TEXT("Ready") || !bRegistrySealed || !RetainedTree || bTravelPending) return false;
    FString Error;
    if(!BuildBridgePath(Error)) { Fail(Error); return false; }
    SetPhase(TEXT("Crossing")); Feedback=TEXT("Cross bridge C with your squad.");
    // Clear stacked preparation locks exactly once, then let original controls run.
    if(APlayerController* P=UGameplayStatics::GetPlayerController(this,0)) { P->ResetIgnoreMoveInput(); P->ResetIgnoreLookInput(); }
    GateBrains(true); return true;
}

// G1-only conservative constraint. Original collision and AI remain authoritative.
bool AParisBridgeMission::ApplyBridgeNavigationConstraint(FString& Error)
{
    if(bBridgeNavigationValidated) return true;
    if(Roster.Num()!=6 || !IsValid(Roster[0])) { Error=TEXT("Bridge constraint requires the original roster."); return false; }
    const FVector Feet(5192.972650,-20735.731259,128.136620);
    auto* C=Roster[0]->GetCapsuleComponent();
    const FVector Center=Feet+FVector(0,0,C->GetScaledCapsuleHalfHeight());
    const FVector Direction=(FVector(5225.223529,-20748,135.176471)-Feet).GetSafeNormal2D();
    FHitResult Hit; FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisG1BridgeWitness),false,Roster[0]);
    const bool Blocked=GetWorld()->SweepSingleByChannel(Hit,Center,Center+Direction*60,FQuat::Identity,
        C->GetCollisionObjectType(),FCollisionShape::MakeCapsule(C->GetScaledCapsuleRadius(),C->GetScaledCapsuleHalfHeight()),
        Q,FCollisionResponseParams(C->GetCollisionResponseToChannels()));
    if(!Blocked || !Hit.GetActor() || Hit.GetActor()->GetName()!=TEXT("StaticMeshActor_1600"))
    { Error=TEXT("Bridge collision witness differs from the validated route."); return false; }
    ARecastNavMesh* Recast=nullptr;
    for(TActorIterator<ARecastNavMesh> I(GetWorld());I;++I)
    { if(Recast) { Error=TEXT("Bridge navigation data is ambiguous."); return false; } Recast=*I; }
    auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld()); FNavLocation Point;
    if(!Nav || !Recast || !Nav->ProjectPointToNavigation(Feet,Point,FVector(50,50,100),Recast) || FVector::Dist(Point.Location,Feet)>50)
    { Error=TEXT("Bridge constraint projection differs from the validated route."); return false; }
    const TArray<FVector> Expected={FVector(5263,-20596,140),FVector(5491,-20691,120),FVector(5491,-20748,140),FVector(4940,-20748,130),FVector(5035,-20520,150)};
    TArray<FVector> Verts;
    if(!Recast->GetPolyVerts(Point.NodeRef,Verts) || Verts.Num()!=Expected.Num())
    { Error=TEXT("Bridge constraint topology differs from the validated route."); return false; }
    for(const FVector& V:Expected) if(!Verts.ContainsByPredicate([&V](const FVector& P){return FVector::Dist(V,P)<=0.1;}))
    { Error=TEXT("Bridge constraint geometry differs from the validated route."); return false; }
    const uint8 Before=Recast->GetPolyAreaID(Point.NodeRef);
    if(Before==Recast->GetAreaID(UNavArea_Null::StaticClass()) || !Recast->SetPolyArea(Point.NodeRef,UNavArea_Null::StaticClass()) ||
        Recast->GetPolyAreaID(Point.NodeRef)!=Recast->GetAreaID(UNavArea_Null::StaticClass()))
    { Error=TEXT("Bridge navigation constraint could not be applied."); return false; }
    bBridgeNavigationValidated=true;
    UE_LOG(LogTemp,Display,TEXT("PARIS_G1_NATIVE_BRIDGE_CONSTRAINT node=%llu vertices=%d area_before=%d area_after=%d hit_cm=%.6f projection_cm=%.6f"),
        uint64(Point.NodeRef),Verts.Num(),Before,Recast->GetPolyAreaID(Point.NodeRef),Hit.Distance,FVector::Dist(Point.Location,Feet));
    return true;
}

// Original G1 plan contract, with the witnessed preflight START frame corrected.
UParisG1AgentPlan::UParisG1AgentPlan(const FObjectInitializer& Init):Super(Init)
{ NodeName=TEXT("G1 plan from native agent position"); }

EBTNodeResult::Type UParisG1AgentPlan::ExecuteTask(UBehaviorTreeComponent& OwnerComp,uint8* NodeMemory)
{
    auto* Ctrl=OwnerComp.GetAIOwner(); auto* Pawn=Ctrl?Cast<ACharacter>(Ctrl->GetPawn()):nullptr;
    auto* BB=OwnerComp.GetBlackboardComponent();
    if(!Ctrl || !Pawn || !BB || ParisG1::Number(Pawn,TEXT("Health"))<=0 || !ParisG1::Flag(Ctrl,TEXT("PatrolEnabled")) ||
        BB->GetValueAsName(TEXT("WaitingReason"))==TEXT("PathExhausted")) return EBTNodeResult::Failed;
    auto* Home=CastField<FStructProperty>(ParisG1::Property(Ctrl,TEXT("HomePoint")));
    auto* Patrol=CastField<FStructProperty>(ParisG1::Property(Ctrl,TEXT("PatrolPoint")));
    auto* Captured=CastField<FBoolProperty>(ParisG1::Property(Ctrl,TEXT("HomeCaptured")));
    if(!Home || !Patrol || !Captured || Home->Struct!=TBaseStructure<FVector>::Get() || Patrol->Struct!=Home->Struct)
    { UE_LOG(LogTemp,Error,TEXT("PARIS_G1_AGENT_PLAN original property contract missing")); return EBTNodeResult::Failed; }
    if(!Captured->GetPropertyValue_InContainer(Ctrl)) *Home->ContainerPtrToValuePtr<FVector>(Ctrl)=Pawn->GetActorLocation();
    Captured->SetPropertyValue_InContainer(Ctrl,true);
    const FVector Goal=ParisG1::Flag(Ctrl,TEXT("PatrolLeg"))?*Home->ContainerPtrToValuePtr<FVector>(Ctrl):*Patrol->ContainerPtrToValuePtr<FVector>(Ctrl);
    UNavigationPath* Path=UNavigationSystemV1::FindPathToLocationSynchronously(Pawn,Pawn->GetNavAgentLocation(),Goal,Pawn);
    if(!Path || !Path->IsValid() || Path->IsPartial())
    { BB->SetValueAsName(TEXT("WaitingReason"),TEXT("PathInvalid")); UE_LOG(LogTemp,Display,TEXT("PARIS_G1_AGENT_PLAN_QUERY_FAILURE start=%s goal=%s"),*Pawn->GetNavAgentLocation().ToString(),*Goal.ToString()); return EBTNodeResult::Failed; }
    for(auto Key:{TEXT("TaskID"),TEXT("RequestID")}) BB->SetValueAsInt(Key,BB->GetValueAsInt(Key)+1);
    BB->SetValueAsInt(TEXT("RestoreGeneration"),int32(ParisG1::Number(Pawn,TEXT("RestoreGeneration"))));
    BB->SetValueAsVector(TEXT("DesiredPosition"),Goal); BB->SetValueAsBool(TEXT("HasMoveGoal"),true);
    BB->SetValueAsName(TEXT("WaitingReason"),TEXT("MoveStarted")); return EBTNodeResult::Succeeded;
}

bool AParisBridgeMission::InstallAgentFeetPlan(FString& Error)
{
    if(bAgentFeetPlanInstalled) return true;
    if(!RetainedTree || !RetainedTree->RootNode || !RetainedTree->BlackboardAsset)
    { Error=TEXT("Original G1 behavior tree is unavailable."); return false; }
    UBehaviorTree* Original=RetainedTree;
    UBehaviorTree* Copy=DuplicateObject<UBehaviorTree>(Original,this);
    int32 Replacements=0,Nodes=0,OriginalNodes=0,Services=0,OriginalServices=0;
    TArray<FString> OtherClasses,OriginalOtherClasses;
    const FString Expected=TEXT("/Game/ParisCombat/AI/NPCInteractionV1/BTT_PC_NPCPlanV3.BTT_PC_NPCPlanV3_C");
    TFunction<void(UBTCompositeNode*,bool)> Visit;
    Visit=[&](UBTCompositeNode* Node,bool Replace)
    {
        if(!Node) return;
        int32& Count=Replace?Nodes:OriginalNodes; int32& ServiceCount=Replace?Services:OriginalServices;
        auto& Classes=Replace?OtherClasses:OriginalOtherClasses;
        ++Count; Classes.Add(Node->GetClass()->GetPathName()); ServiceCount+=Node->Services.Num();
        for(const auto& S:Node->Services) Classes.Add(GetPathNameSafe(S->GetClass()));
        for(auto& Child:Node->Children)
        {
            for(const auto& D:Child.Decorators) Classes.Add(GetPathNameSafe(D->GetClass()));
            if(Child.ChildComposite) Visit(Child.ChildComposite,Replace);
            if(Child.ChildTask)
            {
                ++Count;
                if(Child.ChildTask->GetClass()->GetPathName()==Expected)
                { if(Replace){Child.ChildTask=NewObject<UParisG1AgentPlan>(Copy);++Replacements;} }
                else Classes.Add(Child.ChildTask->GetClass()->GetPathName());
            }
        }
    };
    Visit(Original->RootNode,false); Visit(Copy->RootNode,true);
    if(Replacements!=1 || Nodes!=OriginalNodes || Services!=OriginalServices || OtherClasses!=OriginalOtherClasses || Copy->BlackboardAsset!=Original->BlackboardAsset)
    { Error=TEXT("G1 behavior-tree topology differs from the validated plan."); return false; }
    RetainedTree=Copy; bAgentFeetPlanInstalled=true;
    UE_LOG(LogTemp,Display,TEXT("PARIS_G1_AGENT_PLAN_BIND replacements=%d nodes=%d services=%d other_classes_exact=1 blackboard_exact=1"),Replacements,Nodes,Services);
    return true;
}

bool AParisBridgeMission::BuildBridgePath(FString& Error)
{
    if(BridgePath.Num()>1) return true;
    if(InitialLocations.Num()!=6 || !IsValid(Roster[0])) { Error=TEXT("Original near-bank roster absent."); return false; }
    const FVector InitialFeet=InitialLocations[0]-FVector(0,0,Roster[0]->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
    const FVector Ends[] = {InitialFeet,FVector(1950,-20650,114.262990),FarBankFeet};
    BridgePath.Reset(); BridgeArcs.Reset();
    for(int32 I=0;I<2;++I)
    {
        UNavigationPath* P=UNavigationSystemV1::FindPathToLocationSynchronously(this,Ends[I],Ends[I+1],Roster[0]);
        if(!P || !P->IsValid() || P->IsPartial() || P->PathPoints.Num()<2 || FVector::Dist2D(P->PathPoints[0],Ends[I])>55 || FVector::Dist2D(P->PathPoints.Last(),Ends[I+1])>55)
        { Error=TEXT("Incomplete saved-map bridge centreline."); BridgePath.Reset(); return false; }
        for(const FVector& V : P->PathPoints) if(BridgePath.IsEmpty() || FVector::Dist(BridgePath.Last(),V)>1) BridgePath.Add(V);
    }
    double Arc=0; BridgeArcs.Add(0);
    for(int32 I=1;I<BridgePath.Num();++I) { Arc+=FVector::Dist(BridgePath[I-1],BridgePath[I]); BridgeArcs.Add(Arc); }
    UE_LOG(LogTemp,Display,TEXT("PARIS_G1_CENTRELINE points=%d length_cm=%.6f"),BridgePath.Num(),Arc);
    return true;
}

bool UParisBridgeMissionLibrary::UpdateBridgeSquad(AAIController* Controller)
{
    AParisBridgeMission* Mission=AParisBridgeMission::Find(Controller);
    return Mission && Mission->UpdateBridgeSquad(Controller);
}

bool AParisBridgeMission::UpdateBridgeSquad(AAIController* Controller)
{
    if(!AllowsPlay() || !Controller || bBridgeTransitComplete || Roster.Num()!=6) return false;
    int32 Index=Controller->GetPawn()==Roster[1]?1:(Controller->GetPawn()==Roster[2]?2:0);
    if(Index==0 || !IsValid(Roster[Index]) || Flag(Roster[Index],TEXT("IsDead"))) return false;
    ACharacter* Player=Roster[0]; if(!IsValid(Player)) return false;
    bool AllFar=true,AllArrived=true;
    for(int32 I=1;I<3;++I) if(IsValid(Roster[I]) && !Flag(Roster[I],TEXT("IsDead")))
    {
        AllFar &= Roster[I]->GetActorLocation().X>=5600;
        AAIController* C=Cast<AAIController>(Roster[I]->GetController());
        const auto* V=CastField<FStructProperty>(Property(C,TEXT("HeldGoal")));
        const FVector* Goal=V && V->Struct==TBaseStructure<FVector>::Get()?V->ContainerPtrToValuePtr<FVector>(C):nullptr;
        AllArrived &= Goal && FVector::Dist(Roster[I]->GetActorLocation(),*Goal)<=55 && !Flag(C,TEXT("SquadFailed"));
    }
    if((!bBridgeTransitArmed && Player->GetActorLocation().X>=5600 && AllFar) ||
        (bBridgeTransitArmed && Player->GetActorLocation().X>6500 && AllFar && AllArrived))
    { bBridgeTransitComplete=true; return false; }
    if(!bBridgeTransitArmed && Player->GetActorLocation().X>=1800) bBridgeTransitArmed=true;
    if(!bBridgeTransitArmed) return false;
    FString Error; if(!BuildBridgePath(Error)) { Fail(Error); return true; }
    if(Name(Roster[Index],TEXT("ActionState"))!=TEXT("Ready") || Flag(Controller,TEXT("CombatHold")))
    { Invoke(Controller,TEXT("PC_PolicyHold")); return true; }
    FVector Feet=Player->GetActorLocation()-FVector(0,0,Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
    double Best=std::numeric_limits<double>::max(),Progress=0;
    for(int32 I=1;I<BridgePath.Num();++I)
    {
        FVector A=BridgePath[I-1],B=BridgePath[I],D=B-A; D.Z=0;
        FVector Delta=Feet-A; Delta.Z=0;
        double T=D.SizeSquared()>0?FMath::Clamp(FVector::DotProduct(Delta,D)/D.SizeSquared(),0.0,1.0):0;
        double Distance=FVector::DistSquared2D(Feet,FMath::Lerp(A,B,T));
        if(Distance<Best) { Best=Distance; Progress=FMath::Lerp(BridgeArcs[I-1],BridgeArcs[I],T); }
    }
    if(FVector::Dist2D(Feet,FarBankFeet)<=55 && Player->GetVelocity().Size()<2) bBridgeFarBankSettling=true;
    const double Gap=700-450;
    if(bBridgeFarBankSettling && (BridgePath.Num()<2 || BridgePath.Last().X<5655 || BridgePath[BridgePath.Num()-2].X<5655 || BridgeArcs.Last()-BridgeArcs[BridgeArcs.Num()-2]<2*Gap+55))
    { Fail(TEXT("Far-bank staging lane differs from the validated route.")); return true; }
    const double Lag=Index==1?450.0:700.0;
    if(!bBridgeFarBankSettling && Progress<Lag) { Invoke(Controller,TEXT("PC_PolicyHold")); return true; }
    const double Wanted=bBridgeFarBankSettling?BridgeArcs.Last()-Index*Gap:FMath::Max(0.0,Progress-Lag);
    FVector Goal=BridgePath[0];
    for(int32 I=1;I<BridgePath.Num();++I) if(Wanted<=BridgeArcs[I])
    { Goal=FMath::Lerp(BridgePath[I-1],BridgePath[I],(Wanted-BridgeArcs[I-1])/(BridgeArcs[I]-BridgeArcs[I-1])); break; }
    UFunction* F=Controller->FindFunction(TEXT("PC_SquadRequestGoal"));
    if(!F) { Fail(TEXT("Original squad goal endpoint absent.")); return true; }
    FStructOnScope Parameters(F);
    auto* VectorField=CastField<FStructProperty>(F->FindPropertyByName(TEXT("Goal")));
    auto* ModeField=CastField<FNameProperty>(F->FindPropertyByName(TEXT("Mode")));
    if(!VectorField || VectorField->Struct!=TBaseStructure<FVector>::Get() || !ModeField)
    { Fail(TEXT("Original squad goal signature mismatch.")); return true; }
    *VectorField->ContainerPtrToValuePtr<FVector>(Parameters.GetStructMemory())=Goal;
    ModeField->SetPropertyValue_InContainer(Parameters.GetStructMemory(),TEXT("Follow"));
    Controller->ProcessEvent(F,Parameters.GetStructMemory());
    return true;
}

void AParisBridgeMission::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds); if(bTravelPending || Phase==TEXT("Error")) return;
    if(Phase==TEXT("Preparing"))
    {
        PreparationSeconds+=DeltaSeconds; BootstrapClock+=DeltaSeconds;
        if (BootstrapClock<.25) return; BootstrapClock=0;
        FString Error;
        if(!bRegistrySealed && !SealRegistry(Error)) { Fail(Error); return; }
        bool Ready=EquipmentReady(Error);
        if(!Error.IsEmpty()) { Fail(Error); return; }
        if(!Ready) { if(PreparationSeconds>15) Fail(TEXT("Bounded equipment/standing readiness timeout")); return; }
        if(!ApplyBridgeNavigationConstraint(Error) || !InstallAgentFeetPlan(Error)) { Fail(Error); return; }
        GateBrains(false);
        if(bLoadRequested)
        {
            FString Payload; int32 Serial=0;
            if(!ReadLatest(Payload,Serial,Error) || !ApplySnapshot(Payload,Error)) { Fail(TEXT("Load rejected: ")+Error); return; }
            SaveSerial=Serial; bLoadRequested=false; Feedback=TEXT("Saved mission restored.");
            UE_LOG(LogTemp,Display,TEXT("PARIS_G1_LOADED serial=%d state=%s"),Serial,*ReadMissionState());
        }
        else { SetPhase(TEXT("Ready")); Feedback=TEXT("Press Enter to begin the bridgehead mission."); }
        return;
    }
    if(Phase==TEXT("Ready"))
    {
        ReadySeconds+=DeltaSeconds;
        FString Error;
        if(!EquipmentReady(Error) && !Error.IsEmpty()) Fail(Error);
        return;
    }
    if(!AllowsPlay())
    {
        if(Phase==TEXT("Won")) { UpdateCheckpointUI(); FString Reason; SafeSeconds=IsSafeBoundary(Reason)?SafeSeconds+DeltaSeconds:0; }
        return;
    }
    LivingDefenders=0; LivingAllies=0;
    for(int32 I=0;I<Roster.Num();++I)
    {
        if(!IsValid(Roster[I]))
        {
            if(!DeathLedger.Contains(StableIds[I])) { Fail(TEXT("Required actor removed without recorded death")); return; }
            continue;
        }
        bool Dead=Flag(Roster[I],TEXT("IsDead"));
        if(Dead) DeathLedger.Add(StableIds[I]);
        else if(DeathLedger.Contains(StableIds[I])) { Fail(TEXT("Dead roster member resurrected in current run")); return; }
        if(I>=3 && !Dead) ++LivingDefenders;
        if(I>0 && I<3 && !Dead) ++LivingAllies;
    }
    if(DeathLedger.Contains(TEXT("Player"))) { SetPhase(TEXT("Lost")); Feedback=TEXT("Player lost. F9 loads a save; F6 restarts."); GateBrains(false); return; }
    ACharacter* P=Roster[0];
    FVector Feet=P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
    if(Phase==TEXT("Crossing") && FVector::Dist2D(Feet,FarBankFeet)<=ReachRadius && FMath::Abs(Feet.Z-FarBankFeet.Z)<=100) SetPhase(TEXT("Clearing"));
    if(Phase==TEXT("Clearing") && LivingDefenders==0 && DeathLedger.Contains(TEXT("German1")) && DeathLedger.Contains(TEXT("German2")) && DeathLedger.Contains(TEXT("German3"))) SetPhase(TEXT("Occupying"));
    if(Phase==TEXT("Occupying") && FVector::Dist2D(Feet,BridgeheadFeet)<=OccupyRadius && FMath::Abs(Feet.Z-BridgeheadFeet.Z)<=100 && P->GetCharacterMovement()->IsMovingOnGround())
    { SetPhase(TEXT("Won")); Feedback=TEXT("G1 secured. Enter the gold checkpoint circle to save."); GateBrains(false);
      if(auto* PC=UGameplayStatics::GetPlayerController(this,0)) { PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); } }
    UpdateCheckpointUI();
    FString Reason; SafeSeconds=IsSafeBoundary(Reason) ? SafeSeconds+DeltaSeconds : 0;
}

bool AParisBridgeMission::IsSafeBoundary(FString& Reason) const
{
    if(!bRegistrySealed || bTravelPending || (!AllowsPlay() && Phase!=TEXT("Ready") && Phase!=TEXT("Won"))) { Reason=TEXT("No stable playable state to save."); return false; }
    for(int32 I=0;I<Roster.Num();++I)
    {
        ACharacter* C=Roster[I];
        if(!IsValid(C)) { Reason=TEXT("The six-member roster is incomplete."); return false; }
        if(Flag(C,TEXT("IsDead"))) continue;
        if(Name(C,TEXT("ActionState"))!=TEXT("Ready") || !C->GetCharacterMovement()->IsMovingOnGround() || C->GetVelocity().Size()>2)
        { Reason=TEXT("Wait until everyone is grounded, still, and finished acting."); return false; }
        AAIController* A=Cast<AAIController>(C->GetController());
        if(A && (Flag(A,TEXT("CombatHold")) || Name(A,TEXT("CombatPhase"))==TEXT("Reload")))
        { Reason=TEXT("An NPC combat transaction is active."); return false; }
        if(A && Phase!=TEXT("Won") && Phase!=TEXT("Ready")) for(int32 J=0;J<Roster.Num();++J)
            if((I>=3)!=(J>=3) && IsValid(Roster[J]) && !Flag(Roster[J],TEXT("IsDead")) && A->LineOfSightTo(Roster[J]))
            { Reason=TEXT("Hostile line of sight: save after reaching safety."); return false; }
    }
    return true;
}

FString AParisBridgeMission::CaptureSnapshot(int32 Serial) const
{
    auto O=MakeShared<FJsonObject>(); O->SetNumberField(TEXT("schema"),1); O->SetStringField(TEXT("mission"),MissionMap);
    O->SetStringField(TEXT("config"),ConfigFingerprint); O->SetNumberField(TEXT("serial"),Serial); O->SetStringField(TEXT("phase"),Phase);
    O->SetStringField(TEXT("source_generation"),RunGeneration);
    TArray<TSharedPtr<FJsonValue>> Actors;
    for(int32 I=0;I<Roster.Num();++I)
    {
        ACharacter* C=Roster[I]; auto A=MakeShared<FJsonObject>();
        A->SetStringField(TEXT("id"),StableIds[I]); A->SetStringField(TEXT("class"),C->GetClass()->GetPathName());
        A->SetArrayField(TEXT("location"),Vector(C->GetActorLocation())); A->SetArrayField(TEXT("rotation"),Vector(C->GetActorRotation().Euler()));
        A->SetNumberField(TEXT("health"),Number(C,TEXT("Health"))); A->SetBoolField(TEXT("dead"),Flag(C,TEXT("IsDead")));
        A->SetNumberField(TEXT("loaded"),Number(C,TEXT("LoadedAmmo"))); A->SetNumberField(TEXT("reserve"),Number(C,TEXT("ReserveAmmo")));
        A->SetNumberField(TEXT("shots"),Number(C,TEXT("ShotSequence"))); Actors.Add(MakeShared<FJsonValueObject>(A));
    }
    O->SetArrayField(TEXT("actors"),Actors);
    auto* PC=UGameplayStatics::GetPlayerController(this,0);
    O->SetArrayField(TEXT("control"),Vector(PC ? PC->GetControlRotation().Euler() : FVector::ZeroVector));
    return Json(O);
}

bool AParisBridgeMission::ValidateSnapshot(const FString& Payload,FString& Error) const
{
    auto O=Parse(Payload); FString Map,Config,State; FVector Control;
    if(!O || !InRange(O,TEXT("schema"),1,1,true) || !O->TryGetStringField(TEXT("mission"),Map) || Map!=MissionMap || !O->TryGetStringField(TEXT("config"),Config) || Config!=ConfigFingerprint || !InRange(O,TEXT("serial"),1,2147483646,true))
    { Error=TEXT("Unsupported schema, mission, configuration or serial."); return false; }
    if(!O->TryGetStringField(TEXT("phase"),State) || !(State==TEXT("Ready") || State==TEXT("Crossing") || State==TEXT("Clearing") || State==TEXT("Occupying") || State==TEXT("Won")) || !GetVector(O,TEXT("control"),Control) || Control.GetAbsMax()>360)
    { Error=TEXT("Invalid phase or control rotation."); return false; }
    const TArray<TSharedPtr<FJsonValue>>* Actors=nullptr;
    if(!O->TryGetArrayField(TEXT("actors"),Actors) || Actors->Num()!=6 || Roster.Num()!=6) { Error=TEXT("Incomplete snapshot roster."); return false; }
    int32 Germans=0;
    for(int32 I=0;I<6;++I)
    {
        const TSharedPtr<FJsonObject>* A=nullptr; FString Id,Class; FVector Location,Rotation; bool Dead;
        if(!(*Actors)[I]->TryGetObject(A) || !(*A)->TryGetStringField(TEXT("id"),Id) || Id!=Ids[I] || !(*A)->TryGetStringField(TEXT("class"),Class) || !IsValid(Roster[I]) || Class!=Roster[I]->GetClass()->GetPathName() || !GetVector(*A,TEXT("location"),Location) || !GetVector(*A,TEXT("rotation"),Rotation) || !(*A)->TryGetBoolField(TEXT("dead"),Dead))
        { Error=TEXT("Roster identity/class/transform mismatch."); return false; }
        if(Location.GetAbsMax()>1000000 || Rotation.GetAbsMax()>360 || !InRange(*A,TEXT("health"),0,Number(Roster[I],TEXT("MaxHealth"))) || !InRange(*A,TEXT("loaded"),0,8,true) || !InRange(*A,TEXT("reserve"),0,10000,true) || !InRange(*A,TEXT("shots"),0,2147483646,true) || (Dead!=((*A)->GetNumberField(TEXT("health"))==0)) || (I==0 && Dead))
        { Error=TEXT("Illegal resource or death state."); return false; }
        if(I>=3 && !Dead) ++Germans;
        if(State==TEXT("Ready") && Dead) { Error=TEXT("Ready snapshot contains a casualty."); return false; }
        double Total=(*A)->GetNumberField(TEXT("loaded"))+(*A)->GetNumberField(TEXT("reserve"))+(*A)->GetNumberField(TEXT("shots"));
        if(InitialResources.Num()!=6 || InitialShots.Num()!=6 || Total!=InitialResources[I].Y+InitialResources[I].Z+InitialShots[I])
        { Error=TEXT("Snapshot creates or loses finite ammunition."); return false; }
        if(State==TEXT("Ready") && ((*A)->GetNumberField(TEXT("health"))!=InitialResources[I].X || (*A)->GetNumberField(TEXT("shots"))!=InitialShots[I]))
        { Error=TEXT("Ready snapshot is not an unstarted roster."); return false; }
    }
    if((State==TEXT("Occupying") || State==TEXT("Won")) && Germans!=0) { Error=TEXT("Uncleared bridgehead cannot be completed."); return false; }
    return true;
}

bool AParisBridgeMission::ReadLatest(FString& Payload,int32& Serial,FString& Error) const
{
    Serial=0; TArray<FString> Rejections;
    for(const TCHAR* Suffix : {TEXT("_A"),TEXT("_B")})
    {
        FString Slot=SlotPrefix+Suffix;
        if(!UGameplayStatics::DoesSaveGameExist(Slot,0)) continue;
        auto* S=Cast<UParisBridgeSave>(UGameplayStatics::LoadGameFromSlot(Slot,0)); FString Why;
        if(!S || S->Payload.Len()>65536 || Hash(S->Payload)!=S->Checksum || !ValidateSnapshot(S->Payload,Why))
        { Rejections.Add(Slot+TEXT(": ")+(Why.IsEmpty()?TEXT("checksum/type rejected"):Why)); continue; }
        int32 N=int32(Parse(S->Payload)->GetNumberField(TEXT("serial")));
        if(N>Serial) { Payload=S->Payload; Serial=N; }
    }
    if(Serial>0) { Error=FString::Join(Rejections,TEXT("; ")); return true; }
    Error=Rejections.IsEmpty()?TEXT("No compatible local save exists."):FString::Join(Rejections,TEXT("; ")); return false;
}

bool AParisBridgeMission::SaveCheckpoint()
{
    if(!bConfirmedSaveRequest || !CheckpointUnlocked() || !InsideCheckpoint() || Phase!=TEXT("Won"))
    { Feedback=TEXT("Enter the secured checkpoint circle and confirm with E."); return false; }
    if(!Roster.IsEmpty() && (Roster[0]->bIsCrouched || Number(Roster[0],TEXT("DesiredPosture"))!=0))
    { Feedback=TEXT("Stand up before saving this checkpoint."); return false; }
    FString Error;
    if(!IsSafeBoundary(Error) || (AllowsPlay() && SafeSeconds<2)) { Feedback=Error.IsEmpty()?TEXT("Wait two seconds at a safe settled boundary."):Error; return false; }
    FString Old; int32 Previous=0; ReadLatest(Old,Previous,Error);
    int32 Serial=Previous+1;
    if(Serial>=2147483646) { Feedback=TEXT("Save serial exhausted."); return false; }
    FString Payload=CaptureSnapshot(Serial);
    if(!ValidateSnapshot(Payload,Error)) { Feedback=TEXT("Save validation failed: ")+Error; return false; }
    auto* S=Cast<UParisBridgeSave>(UGameplayStatics::CreateSaveGameObject(UParisBridgeSave::StaticClass()));
    S->Payload=Payload; S->Checksum=Hash(Payload); FString Slot=SlotPrefix+(Serial%2?TEXT("_A"):TEXT("_B"));
    if(!UGameplayStatics::SaveGameToSlot(S,Slot,0)) { Feedback=TEXT("Save write failed; previous slot retained."); return false; }
    auto* Verify=Cast<UParisBridgeSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));
    if(!Verify || Verify->Payload!=Payload || Verify->Checksum!=Hash(Payload)) { Feedback=TEXT("Save readback failed; previous slot retained."); return false; }
    SaveSerial=Serial; Feedback=FString::Printf(TEXT("Mission saved (revision %d)."),Serial);
    UE_LOG(LogTemp,Display,TEXT("PARIS_G1_SAVED serial=%d slot=%s state=%s"),Serial,*Slot,*Payload); return true;
}

bool AParisBridgeMission::ApplySnapshot(const FString& Payload,FString& Error)
{
    if(!ValidateSnapshot(Payload,Error)) return false;
    auto O=Parse(Payload); const auto& Actors=O->GetArrayField(TEXT("actors"));
    // Validation above is complete before any actor is mutated. No old-world action is resumed.
    DeathLedger.Reset(); LivingAllies=0; LivingDefenders=0;
    for(int32 I=0;I<6;++I)
    {
        ACharacter* C=Roster[I]; auto A=Actors[I]->AsObject(); FVector Location,Rotation;
        GetVector(A,TEXT("location"),Location); GetVector(A,TEXT("rotation"),Rotation);
        if(!Invoke(C,TEXT("PC_ResetLifecycle"))) { Error=TEXT("Missing lifecycle restore endpoint."); return false; }
        C->GetCharacterMovement()->StopMovementImmediately();
        if(!C->SetActorLocationAndRotation(Location,FRotator::MakeFromEuler(Rotation),false,nullptr,ETeleportType::TeleportPhysics)) { Error=TEXT("Snapshot transform restore failed."); return false; }
        for(const auto& Pair : {TPair<const TCHAR*,const TCHAR*>(TEXT("Health"),TEXT("health")),TPair<const TCHAR*,const TCHAR*>(TEXT("LoadedAmmo"),TEXT("loaded")),TPair<const TCHAR*,const TCHAR*>(TEXT("ReserveAmmo"),TEXT("reserve")),TPair<const TCHAR*,const TCHAR*>(TEXT("ShotSequence"),TEXT("shots"))})
            if(!SetNumber(C,Pair.Key,A->GetNumberField(Pair.Value))) { Error=TEXT("Snapshot resource restore failed."); return false; }
        if(A->GetBoolField(TEXT("dead"))) { Invoke(C,TEXT("PC_Die")); DeathLedger.Add(StableIds[I]); }
        else { if(I>0 && I<3) ++LivingAllies; if(I>=3) ++LivingDefenders; }
    }
    FVector Control; GetVector(O,TEXT("control"),Control);
    if(auto* PC=UGameplayStatics::GetPlayerController(this,0)) { PC->SetControlRotation(FRotator::MakeFromEuler(Control)); PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); }
    SetPhase(O->GetStringField(TEXT("phase")));
    // Read actual restored actors before admitting any behavior that can move them.
    VerifiedRestoreState=CaptureSnapshot(int32(O->GetNumberField(TEXT("serial"))));
    auto Verified=Parse(VerifiedRestoreState);
    const auto& Restored=Verified->GetArrayField(TEXT("actors"));
    for(int32 I=0;I<6;++I)
    {
        auto Expected=Actors[I]->AsObject(); auto Actual=Restored[I]->AsObject(); FVector Want,Got;
        GetVector(Expected,TEXT("location"),Want); GetVector(Actual,TEXT("location"),Got);
        if(FVector::Dist(Want,Got)>.001 || Actual->GetBoolField(TEXT("dead"))!=Expected->GetBoolField(TEXT("dead")))
        { Error=TEXT("Restored actor transform/death verification failed."); return false; }
        for(const TCHAR* N : {TEXT("health"),TEXT("loaded"),TEXT("reserve"),TEXT("shots")})
            if(Actual->GetNumberField(N)!=Expected->GetNumberField(N)) { Error=TEXT("Restored resource verification failed."); return false; }
    }
    if(!BuildBridgePath(Error)) return false;
    GateBrains(AllowsPlay());
    if(Phase==TEXT("Won")) if(auto* PC=UGameplayStatics::GetPlayerController(this,0))
    { PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); }
    return true;
}

bool AParisBridgeMission::LoadCheckpoint()
{
    FString Payload,Error; int32 Serial;
    if(!ReadLatest(Payload,Serial,Error)) { Feedback=Error; return false; }
    Feedback=Error.IsEmpty()?TEXT("Loading saved mission..."):TEXT("Loading valid fallback; ")+Error;
    bTravelPending=true; GateBrains(false);
    UGameplayStatics::OpenLevel(this,FName(*MissionMap),true,TEXT("ParisLoad")); return true;
}

FString AParisBridgeMission::InspectCheckpointJournal() const
{
    FString Payload,Error; int32 Serial=0; bool Valid=ReadLatest(Payload,Serial,Error);
    auto O=MakeShared<FJsonObject>(); O->SetBoolField(TEXT("valid"),Valid); O->SetNumberField(TEXT("serial"),Serial);
    O->SetStringField(TEXT("feedback"),Error);
    if(Valid) O->SetObjectField(TEXT("snapshot"),Parse(Payload));
    return Json(O);
}

void AParisBridgeMission::RestartMission()
{
    if(bTravelPending) return;
    bTravelPending=true; GateBrains(false); UGameplayStatics::OpenLevel(this,FName(*MissionMap),true);
}

FString AParisBridgeMission::ReadMissionState() const
{
    auto O=MakeShared<FJsonObject>(); O->SetStringField(TEXT("phase"),Phase); O->SetStringField(TEXT("generation"),RunGeneration);
    O->SetStringField(TEXT("feedback"),Feedback); O->SetNumberField(TEXT("ready_seconds"),ReadySeconds); O->SetNumberField(TEXT("save_serial"),SaveSerial);
    O->SetNumberField(TEXT("living_defenders"),LivingDefenders); O->SetNumberField(TEXT("living_allies"),LivingAllies);
    O->SetBoolField(TEXT("registry_sealed"),bRegistrySealed); O->SetBoolField(TEXT("allows_play"),AllowsPlay());
    O->SetBoolField(TEXT("bridge_transit_active"),bBridgeTransitArmed && !bBridgeTransitComplete);
    O->SetBoolField(TEXT("bridge_transit_complete"),bBridgeTransitComplete);
    TArray<TSharedPtr<FJsonValue>> Centreline;
    for(const FVector& P : BridgePath) Centreline.Add(MakeShared<FJsonValueArray>(Vector(P)));
    O->SetArrayField(TEXT("bridge_centreline"),Centreline);
    if(bRegistrySealed && Roster.Num()==6 && !Roster.ContainsByPredicate([](const TObjectPtr<ACharacter>& A){return !IsValid(A);}))
        O->SetObjectField(TEXT("snapshot"),Parse(CaptureSnapshot(FMath::Max(SaveSerial,1))));
    return Json(O);
}

bool AParisBridgePlayerController::InputKey(const FInputKeyEventArgs& Params)
{
    AParisBridgeMission* M=AParisBridgeMission::Find(this);
    if(M)
    {
        if(Params.Key==EKeys::LeftControl || Params.Key==EKeys::RightControl)
            bMissionControlHeld=Params.Event!=IE_Released;
        if(Params.Event==IE_Pressed)
        {
            if(Params.Key==EKeys::Enter) { M->StartMission(); return true; }
            if(Params.Key==EKeys::F5) { M->RequestCheckpointPrompt(); return true; }
            if(Params.Key==EKeys::E && M->CheckpointPromptVisible) { M->ConfirmCheckpoint(); return true; }
            if(Params.Key==EKeys::Escape && M->CheckpointPromptVisible) { M->DismissCheckpointPrompt(); return true; }
            if(Params.Key==EKeys::F6) { M->RestartMission(); return true; }
            if(Params.Key==EKeys::F9) { M->LoadCheckpoint(); return true; }
        }
        if(!M->AllowsPlay() && M->Phase!=TEXT("Won") && Params.Key!=EKeys::Tilde && Params.Key!=EKeys::Escape) return true;
    }
    return Super::InputKey(Params);
}
void AParisBridgePlayerController::MissionStart() { if(auto* M=AParisBridgeMission::Find(this)) M->StartMission(); }
void AParisBridgePlayerController::MissionSave() { if(auto* M=AParisBridgeMission::Find(this)) M->RequestCheckpointPrompt(); }
void AParisBridgePlayerController::MissionLoad() { if(auto* M=AParisBridgeMission::Find(this)) M->LoadCheckpoint(); }
void AParisBridgePlayerController::MissionRestart() { if(auto* M=AParisBridgeMission::Find(this)) M->RestartMission(); }

AParisBridgeGameMode::AParisBridgeGameMode()
{
    DefaultPawnClass=nullptr; PlayerControllerClass=AParisBridgePlayerController::StaticClass(); HUDClass=AParisBridgeHUD::StaticClass();
}

namespace ParisPlaytestUX
{
bool PutObject(UObject* Target,const TCHAR* Field,UObject* Value)
{
    auto* P=Target?FindFProperty<FObjectPropertyBase>(Target->GetClass(),Field):nullptr;
    if(!P || (Value && !Value->IsA(P->PropertyClass))) return false;
    P->SetObjectPropertyValue_InContainer(Target,Value); return true;
}
}

void AParisBridgeGameMode::StartPlay()
{
    ACharacter* Original=nullptr;
    for(TActorIterator<ACharacter> I(GetWorld());I;++I) if(I->ActorHasTag(TEXT("G1_Player")))
    { checkf(!Original,TEXT("Duplicate G1 player before action integration")); Original=*I; }
    UClass* Actions=LoadClass<ACharacter>(nullptr,TEXT("/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6.BP_PCParisPlayerActionsV6_C"));
    checkf(Original && Actions && Actions->IsChildOf(Original->GetClass()),TEXT("Exact compatible existing action player is required"));
    checkf(!Original->HasActorBegunPlay(),TEXT("Action integration must precede original BeginPlay"));
    ACharacter* Player=GetWorld()->SpawnActorDeferred<ACharacter>(Actions,Original->GetActorTransform(),nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
    check(Player); Player->Tags=Original->Tags; Player->AutoPossessPlayer=EAutoReceiveInput::Player0;
    Player->SetActorEnableCollision(false);
    UGameplayStatics::FinishSpawningActor(Player,Original->GetActorTransform());
    checkf(Player->GetMesh()->GetSkeletalMeshAsset()==Original->GetMesh()->GetSkeletalMeshAsset(),TEXT("Source character mesh changed"));
    checkf(Player->GetMesh()->GetNumMaterials()==Original->GetMesh()->GetNumMaterials(),TEXT("Material count changed"));
    for(int32 I=0;I<Original->GetMesh()->GetNumMaterials();++I)
        checkf(Player->GetMesh()->GetMaterial(I)==Original->GetMesh()->GetMaterial(I),TEXT("Source material changed"));
    Player->GetMesh()->SetRelativeTransform(Original->GetMesh()->GetRelativeTransform());
    checkf(FMath::Abs(Player->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()-Original->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight())<.01 &&
           FMath::Abs(Player->GetCapsuleComponent()->GetUnscaledCapsuleRadius()-Original->GetCapsuleComponent()->GetUnscaledCapsuleRadius())<.01,TEXT("Initial action capsule changed"));
    for(const TCHAR* Field:{TEXT("Health"),TEXT("LoadedAmmo"),TEXT("ReserveAmmo"),TEXT("Capacity"),TEXT("TeamId"),TEXT("ShotSequence"),TEXT("ActionID"),TEXT("RestoreGeneration")})
    { const double V=Number(Original,Field); checkf(FMath::IsFinite(V) && SetNumber(Player,Field,V),TEXT("Original resource interface changed")); }
    AActor* Gun=Cast<AActor>(Object(Original,TEXT("WeaponAppearance")));
    checkf(Gun && ParisPlaytestUX::PutObject(Player,TEXT("WeaponAppearance"),Gun),TEXT("Original weapon handoff failed"));
    for(TActorIterator<AActor> I(GetWorld());I;++I) if(*I!=Original && *I!=Player)
    {
        if(Object(*I,TEXT("Combatant"))==Original) check(ParisPlaytestUX::PutObject(*I,TEXT("Combatant"),Player));
        if(Object(*I,TEXT("GripMesh"))==Original->GetMesh()) check(ParisPlaytestUX::PutObject(*I,TEXT("GripMesh"),Player->GetMesh()));
        if(Object(*I,TEXT("SourceMesh"))==Original->GetMesh()) check(ParisPlaytestUX::PutObject(*I,TEXT("SourceMesh"),Player->GetMesh()));
        if(I->GetOwner()==Original) I->SetOwner(Player);
    }
    Gun->AttachToComponent(Player->GetMesh(),FAttachmentTransformRules::KeepRelativeTransform,TEXT("hand_r"));
    if(auto* PC=Cast<APlayerController>(Original->GetController())) PC->Possess(Player);
    Original->Tags.Remove(TEXT("G1_Player")); const FString OldClass=Original->GetClass()->GetPathName();
    Original->Destroy(); Player->SetActorEnableCollision(true);
    UE_LOG(LogTemp,Display,TEXT("PARIS_UX_ACTION_PLAYER old=%s new=%s original_gun=%s mesh_material_resources_exact=1"),*OldClass,*Player->GetClass()->GetPathName(),*Gun->GetPathName());
    Super::StartPlay();
}

bool AParisBridgeMission::CheckpointUnlocked() const
{
    return bRegistrySealed && LivingDefenders==0 && DeathLedger.Contains(TEXT("German1")) &&
        DeathLedger.Contains(TEXT("German2")) && DeathLedger.Contains(TEXT("German3"));
}
bool AParisBridgeMission::InsideCheckpoint() const
{
    if(!CheckpointUnlocked() || Roster.IsEmpty() || !IsValid(Roster[0]) || Flag(Roster[0],TEXT("IsDead"))) return false;
    auto* P=Roster[0].Get(); const FVector Feet=P->GetNavAgentLocation();
    return FVector::Dist2D(Feet,BridgeheadFeet)<=CheckpointRadius && FMath::Abs(Feet.Z-BridgeheadFeet.Z)<=100 && P->GetCharacterMovement()->IsMovingOnGround();
}
void AParisBridgeMission::UpdateCheckpointUI()
{
    if(!CheckpointUnlocked()) { CheckpointPromptVisible=false; return; }
    // Development candidate: a world-space ring at the surveyed G1 ground anchor.
    DrawDebugCircle(GetWorld(),BridgeheadFeet+FVector(0,0,7),CheckpointRadius,128,FColor(202,171,105),false,-1,0,1.25,FVector(1,0,0),FVector(0,1,0),false);
    const bool Inside=InsideCheckpoint();
    if(!Inside) { CheckpointPromptVisible=false; bCheckpointDismissed=false; }
    else if(!bCheckpointWasInside && !bCheckpointDismissed)
    { CheckpointPromptVisible=true; UE_LOG(LogTemp,Display,TEXT("PARIS_UX_CHECKPOINT_ENTER prompt=1 serial=%d autosave=0"),SaveSerial); }
    bCheckpointWasInside=Inside;
}
bool AParisBridgeMission::RequestCheckpointPrompt()
{
    if(!InsideCheckpoint()) { Feedback=TEXT("Clear all three guards, then enter the gold checkpoint circle."); return false; }
    CheckpointPromptVisible=true; bCheckpointDismissed=false; return true;
}
void AParisBridgeMission::DismissCheckpointPrompt()
{
    CheckpointPromptVisible=false; bCheckpointDismissed=true;
    Feedback=TEXT("Checkpoint not saved. Leave and re-enter when ready.");
    UE_LOG(LogTemp,Display,TEXT("PARIS_UX_CHECKPOINT_DECLINED serial=%d"),SaveSerial);
}
bool AParisBridgeMission::ConfirmCheckpoint()
{
    if(!CheckpointPromptVisible || !InsideCheckpoint()) return false;
    TGuardValue<bool> Permit(bConfirmedSaveRequest,true);
    if(!SaveCheckpoint()) return false;
    CheckpointPromptVisible=false; bCheckpointDismissed=true;
    UE_LOG(LogTemp,Display,TEXT("PARIS_UX_CHECKPOINT_CONFIRMED serial=%d"),SaveSerial); return true;
}

void AParisBridgeHUD::DrawHUD()
{
    Super::DrawHUD(); if(!Canvas || !PlayerOwner) return;
    auto* M=AParisBridgeMission::Find(this);auto* Player=Cast<ACharacter>(PlayerOwner->GetPawn());
    if(!M) return;
    if(!bLegacyWidgetRemoved)
    {
        TArray<UUserWidget*> Widgets;
        UWidgetBlueprintLibrary::GetAllWidgetsOfClass(this,Widgets,UUserWidget::StaticClass(),false);
        for(auto* W:Widgets) if(W && W->GetClass()->GetPathName().StartsWith(TEXT("/Game/ParisCombat/UI/CityGameplayV1/WBP_PCParisStatusV1"))) W->RemoveFromParent();
        bLegacyWidgetRemoved=true;
    }
    const FString UIDir=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../UI")));
    if(!bMapLoadAttempted)
    {
        bMapLoadAttempted=true;
        MinimapTexture=FImageUtils::ImportFileAsTexture2D(FPaths::Combine(UIDir,TEXT("g1_minimap.png")));
        if(!MinimapTexture) { UE_LOG(LogTemp,Error,TEXT("PARIS_UX_MINIMAP_MISSING")); }
        else { UE_LOG(LogTemp,Display,TEXT("PARIS_UX_HUD_READY minimap=%dx%d metric_bounds=0,-25000,10000,-15000 legacy_widget_removed=1"),MinimapTexture->GetSizeX(),MinimapTexture->GetSizeY()); }
        checkf(FPaths::FileExists(FPaths::Combine(UIDir,TEXT("Cinzel.ttf"))),TEXT("Packaged Cinzel font required"));
        UE_LOG(LogTemp,Display,TEXT("PARIS_HUD_CONCEPT_READY style=ivory_brass_float_v1 font=Cinzel circular_map=1 authoritative_resources=1"));
    }
    // Canvas requires a UFont even when Slate provides the composite; hold it across GC.
    static TStrongObjectPtr<UFont> Typeface([&]()
    {
        UFont* Font=NewObject<UFont>();Font->FontCacheType=EFontCacheType::Runtime;
        Font->GetMutableInternalCompositeFont()=FCompositeFont(FName(TEXT("Regular")),
            FPaths::Combine(UIDir,TEXT("Cinzel.ttf")),EFontHinting::Default,EFontLoadingPolicy::LazyLoad);
        return Font;
    }());
    const float S=FMath::Min(Canvas->SizeX/1920.f,Canvas->SizeY/1080.f);
    const float OX=(Canvas->SizeX-1920*S)*.5f,OY=(Canvas->SizeY-1080*S)*.5f;
    const FLinearColor Ivory(.95f,.91f,.75f,1),Brass(.77f,.60f,.30f,1),Quiet(.67f,.66f,.52f,1),
        Ally(.56f,.65f,.40f,1),Danger(.92f,.24f,.16f,1),Ink(.004f,.006f,.006f,.80f);
    auto Pt=[&](double X,double Y){return FVector2D(OX+X*S,OY+Y*S);};
    auto Rect=[&](double X,double Y,double W,double H,FLinearColor C){DrawRect(C,OX+X*S,OY+Y*S,W*S,H*S);};
    auto Line=[&](double X,double Y,double XX,double YY,FLinearColor C,float T=1.f)
    {
        DrawLine(OX+X*S,OY+Y*S,OX+XX*S,OY+YY*S,FLinearColor(0,0,0,.65),T*S+1.5*S);
        DrawLine(OX+X*S,OY+Y*S,OX+XX*S,OY+YY*S,C,T*S);
    };
    auto Text=[&](const FString& V,float X,float Y,float Size,FLinearColor C,bool Center=false,int32 Tracking=0)
    {
        FSlateFontInfo Info(Typeface.Get(),Size);Info.LetterSpacing=Tracking;
        FCanvasTextItem Item(Pt(X,Y),FText::FromString(V),Info,C);
        Item.Scale=FVector2D(S,S);Item.bCentreX=Center;
        Item.EnableShadow(FLinearColor(0,0,0,.95),FVector2D(1.2*S,1.8*S));
        Canvas->DrawItem(Item);
        checkf(Item.DrawnSize.X>0 && Item.DrawnSize.Y>0,TEXT("HUD glyph draw required"));
        static bool FirstDrawLogged=false;
        if(!FirstDrawLogged)
        {FirstDrawLogged=true;UE_LOG(LogTemp,Display,TEXT("PARIS_HUD_CINZEL_DRAW runtime_ufont=1 width=%.3f height=%.3f"),Item.DrawnSize.X,Item.DrawnSize.Y);}
    };
    auto Tri=[&](FVector2D A,FVector2D B,FVector2D C,FLinearColor Color)
    {
        FCanvasTriangleItem Item(Pt(A.X,A.Y),Pt(B.X,B.Y),Pt(C.X,C.Y),GWhiteTexture);
        Item.SetColor(Color);Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
    };
    auto Halo=[&](double X,double Y,double RX,double RY,float Alpha)
    {
        TArray<FCanvasUVTri> Fan;Fan.Reserve(48);
        for(int32 I=0;I<48;++I)
        {
            const double A=2*PI*I/48,B=2*PI*(I+1)/48;FCanvasUVTri T;
            T.V0_Pos=Pt(X,Y);T.V1_Pos=Pt(X+RX*FMath::Cos(A),Y+RY*FMath::Sin(A));T.V2_Pos=Pt(X+RX*FMath::Cos(B),Y+RY*FMath::Sin(B));
            T.V0_UV=T.V1_UV=T.V2_UV=FVector2D::ZeroVector;
            T.V0_Color=FLinearColor(0,0,0,Alpha);T.V1_Color=T.V2_Color=FLinearColor(0,0,0,0);Fan.Add(T);
        }
        FCanvasTriangleItem Item(Fan,GWhiteTexture);Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
    };
    auto Circle=[&](double X,double Y,double R,FLinearColor C,float Width=1.f)
    {
        const int32 Segments=FMath::Clamp(FMath::CeilToInt(R*1.6),24,160);
        const double Inner=FMath::Max(0.,R-Width*.5),Outer=R+Width*.5;
        TArray<FCanvasUVTri> Mesh;Mesh.Reserve(Segments*6);
        auto Band=[&](double R1,double R2,float Alpha1,float Alpha2)
        {
            for(int32 I=0;I<Segments;++I)
            {
                const double A=2*PI*I/Segments,B=2*PI*(I+1)/Segments;
                const auto P1=Pt(X+R1*FMath::Cos(A),Y+R1*FMath::Sin(A)),P2=Pt(X+R2*FMath::Cos(A),Y+R2*FMath::Sin(A));
                const auto P3=Pt(X+R2*FMath::Cos(B),Y+R2*FMath::Sin(B)),P4=Pt(X+R1*FMath::Cos(B),Y+R1*FMath::Sin(B));
                FLinearColor C1=C,C2=C;C1.A*=Alpha1;C2.A*=Alpha2;
                FCanvasUVTri T;T.V0_UV=T.V1_UV=T.V2_UV=FVector2D::ZeroVector;
                T.V0_Pos=P1;T.V1_Pos=P2;T.V2_Pos=P3;T.V0_Color=C1;T.V1_Color=T.V2_Color=C2;Mesh.Add(T);
                T.V0_Pos=P1;T.V1_Pos=P3;T.V2_Pos=P4;T.V0_Color=T.V2_Color=C1;T.V1_Color=C2;Mesh.Add(T);
            }
        };
        Band(FMath::Max(0.,Inner-.85),Inner,0,1);Band(Inner,Outer,1,1);Band(Outer,Outer+.85,1,0);
        FCanvasTriangleItem Item(Mesh,GWhiteTexture);Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
    };
    auto Diamond=[&](double X,double Y,double R,FLinearColor C)
    {Line(X,Y-R,X+R,Y,C,1.3);Line(X+R,Y,X,Y+R,C,1.3);Line(X,Y+R,X-R,Y,C,1.3);Line(X-R,Y,X,Y-R,C,1.3);};
    auto Key=[&](const FString& Name,float X,float Y,float W)
    {
        Rect(X,Y,W,33,FLinearColor(0,0,0,.28));
        Line(X,Y,X+W,Y,Ivory);Line(X+W,Y,X+W,Y+33,Ivory);Line(X+W,Y+33,X,Y+33,Ivory);Line(X,Y+33,X,Y,Ivory);
        Text(Name,X+W*.5f,Y+4,16,Ivory,true);
    };

    // The approved composition floats over the real world; no generated scene or cards.
    Halo(250,89,270,76,.36);
    Diamond(76,84,30,Brass);
    if(M->Phase==TEXT("Won")) {Line(64,85,74,94,Ivory,4);Line(74,94,90,73,Ivory,4);}
    else {Line(76,72,76,87,Ivory,2);Rect(74.5,94,3,3,Ivory);}
    Text(TEXT("PARIS  /  G1"),130,41,13,Brass,false,190);
    FString Title=TEXT("ASSEMBLING SQUAD"),Detail=TEXT("PREPARING EQUIPMENT");
    if(M->Phase==TEXT("Ready")){Title=TEXT("CROSS THE RIVER");Detail=TEXT("CROSS BRIDGE C WITH YOUR SQUAD");}
    else if(M->Phase==TEXT("Crossing")){Title=TEXT("CROSS THE RIVER");Detail=TEXT("REACH THE FAR BANK");}
    else if(M->Phase==TEXT("Clearing")){Title=TEXT("SECURE THE BRIDGEHEAD");Detail=FString::Printf(TEXT("%d / 3 GUARDS ELIMINATED"),3-M->LivingDefenders);}
    else if(M->Phase==TEXT("Occupying")){Title=TEXT("OCCUPY THE BRIDGEHEAD");Detail=TEXT("3 / 3 GUARDS ELIMINATED");}
    else if(M->Phase==TEXT("Won")){Title=TEXT("BRIDGEHEAD SECURED");Detail=TEXT("3 / 3 GUARDS ELIMINATED");}
    else if(M->Phase==TEXT("Lost")){Title=TEXT("MISSION LOST");Detail=TEXT("F9 LOAD  /  F6 RESTART");}
    else if(M->Phase==TEXT("Error")){Title=TEXT("MISSION STOPPED");Detail=TEXT("SEE RUN LOG");}
    Text(Title,130,67,21,M->Phase==TEXT("Lost")?Danger:Ivory,false,45);
    Text(Detail,130,102,12,Quiet,false,130);

    // Native triangle fan is the circular clip of the unchanged metric survey.
    const double CX=1742,CY=182,R=136;
    Halo(CX,CY,R+16,R+16,.42);
    if(MinimapTexture && MinimapTexture->GetResource())
    {
        TArray<FCanvasUVTri> Fan;Fan.Reserve(128);
        for(int32 I=0;I<128;++I)
        {
            const double A=2*PI*I/128,B=2*PI*(I+1)/128;FCanvasUVTri T;
            T.V0_Pos=Pt(CX,CY);T.V1_Pos=Pt(CX+R*FMath::Cos(A),CY+R*FMath::Sin(A));T.V2_Pos=Pt(CX+R*FMath::Cos(B),CY+R*FMath::Sin(B));
            T.V0_UV=FVector2D(.5,.5);T.V1_UV=FVector2D(.5+.5*FMath::Cos(A),.5+.5*FMath::Sin(A));T.V2_UV=FVector2D(.5+.5*FMath::Cos(B),.5+.5*FMath::Sin(B));
            T.V0_Color=T.V1_Color=T.V2_Color=FLinearColor(.58f,.54f,.39f,.94f);Fan.Add(T);
        }
        FCanvasTriangleItem Item(Fan,MinimapTexture->GetResource());Item.BlendMode=SE_BLEND_Translucent;Canvas->DrawItem(Item);
    }
    Circle(CX,CY,R+2,Brass,1.5);Circle(CX,CY,R-2,FLinearColor(.8f,.75f,.56f,.50f),.65);
    Line(CX,CY-R-8,CX,CY-R+7,Ivory);Text(TEXT("N"),CX,CY-R+9,13,Ivory,true);
    Text(TEXT("G1"),CX,CY+R+13,15,Ivory,true,60);
    Line(CX-91,CY+R+26,CX-28,CY+R+26,Brass);Line(CX+28,CY+R+26,CX+91,CY+R+26,Brass);
    auto MapPoint=[&](FVector V){return FVector2D(CX-R+V.X/10000*(2*R),CY-R+(-15000-V.Y)/10000*(2*R));};
    auto InMap=[&](FVector2D P,double Margin=8.0){return FVector2D::DistSquared(P,FVector2D(CX,CY))<=FMath::Square(R-Margin);};
    auto Dot=[&](FVector V,FLinearColor C,float Size){const auto P=MapPoint(V);if(InMap(P)) {Rect(P.X-Size-1,P.Y-Size-1,2*Size+2,2*Size+2,Ink);Rect(P.X-Size,P.Y-Size,2*Size,2*Size,C);}};
    for(TActorIterator<ACharacter> I(GetWorld());I;++I)
        if((I->ActorHasTag(TEXT("G1_Ally1")) || I->ActorHasTag(TEXT("G1_Ally2"))) && !Flag(*I,TEXT("IsDead"))) Dot(I->GetActorLocation(),Ally,3);
    if(Player)
    {
        const auto P=MapPoint(Player->GetActorLocation());const double Angle=FMath::DegreesToRadians(PlayerOwner->GetControlRotation().Yaw);
        if(InMap(P,14))
        {
            const FVector2D F(FMath::Cos(Angle),-FMath::Sin(Angle)),Side(-F.Y,F.X);
            const auto A=P+F*10,B=P-F*6+Side*6,C=P-F*6-Side*6;
            Tri(A,B,C,Ivory);Line(B.X,B.Y,C.X,C.Y,Ink,1);
        }
        if(GetWorld()->GetTimeSeconds()>=NextMarkerRefresh)
        {
            NextMarkerRefresh=GetWorld()->GetTimeSeconds()+.2;CachedEnemyLocations.Reset();
            FVector Eye;FRotator View;PlayerOwner->GetPlayerViewPoint(Eye,View);const FVector Forward=View.Vector();
            for(TActorIterator<ACharacter> I(GetWorld());I;++I)
                if((I->ActorHasTag(TEXT("G1_German1")) || I->ActorHasTag(TEXT("G1_German2")) || I->ActorHasTag(TEXT("G1_German3"))) && !Flag(*I,TEXT("IsDead")))
                {
                    const FVector Delta=I->GetActorLocation()-Eye;
                    if(Delta.SizeSquared()<FMath::Square(10000.0) && FVector::DotProduct(Forward,Delta.GetSafeNormal())>=.70710678 && PlayerOwner->LineOfSightTo(*I)) CachedEnemyLocations.Add(I->GetActorLocation());
                }
        }
    }
    for(const auto& V:CachedEnemyLocations) Dot(V,Danger,2.5);
    const auto Goal=MapPoint(M->Phase==TEXT("Crossing")?M->FarBankFeet:M->BridgeheadFeet);
    if(InMap(Goal,12)){Circle(Goal.X,Goal.Y,8,Brass,1.5);Diamond(Goal.X,Goal.Y,4,Brass);}

    if(Player)
    {
        const double HP=Number(Player,TEXT("Health")),Loaded=Number(Player,TEXT("LoadedAmmo")),Reserve=Number(Player,TEXT("ReserveAmmo")),Capacity=Number(Player,TEXT("Capacity"));
        Halo(218,989,226,89,.34);Halo(1743,977,180,107,.36);
        const auto HealthColor=HP<=25?Danger:Ivory;
        Rect(55,946,10,31,HealthColor);Rect(44.5,956.5,31,10,HealthColor);
        Text(FString::Printf(TEXT("%.0f"),HP),92,931,31,HealthColor);
        const double Fraction=FMath::Clamp(HP/100.0,0.0,1.0);
        for(int32 I=0;I<6;++I)
        {
            const double X=191+I*34;Rect(X,956,28,9,FLinearColor(.20f,.20f,.16f,.75));
            Rect(X,956,28*FMath::Clamp(Fraction*6-I,0.0,1.0),9,HealthColor);
        }
        auto Soldier=[&](float X,bool Alive)
        {
            const auto C=Alive?Ally:FLinearColor(.28f,.29f,.25f,.8f);
            for(int32 I=0;I<12;++I){const double A=2*PI*I/12,B=2*PI*(I+1)/12;Tri(FVector2D(X,1007),FVector2D(X+3*FMath::Cos(A),1007+3*FMath::Sin(A)),FVector2D(X+3*FMath::Cos(B),1007+3*FMath::Sin(B)),C);}
            Tri(FVector2D(X-5,1014),FVector2D(X+5,1014),FVector2D(X+3,1027),C);
            Tri(FVector2D(X-5,1014),FVector2D(X+3,1027),FVector2D(X-3,1027),C);
            Tri(FVector2D(X-5,1014),FVector2D(X-7,1025),FVector2D(X-4,1025),C);
            Tri(FVector2D(X+5,1014),FVector2D(X+4,1025),FVector2D(X+7,1025),C);
            Tri(FVector2D(X-3,1026),FVector2D(X,1026),FVector2D(X-4,1038),C);Rect(X-5,1036,3,2,C);
            Tri(FVector2D(X,1026),FVector2D(X+3,1026),FVector2D(X+4,1038),C);Rect(X+2,1036,3,2,C);
        };
        Soldier(55,M->LivingAllies>=1);Soldier(82,M->LivingAllies>=2);
        Text(FString::Printf(TEXT("SQUAD %d / 2"),M->LivingAllies),115,1015,14,Ivory,false,85);

        Text(TEXT("M1 GARAND"),1623,888,13,Ivory,false,60);
        // Original vector silhouette, aligned with the actual rifle identity.
        const FVector2D A(1751,906),B(1784,896),C(1813,896),D(1816,902),E(1788,902),F(1765,914);
        Tri(A,B,F,Quiet);Tri(B,E,F,Quiet);Tri(B,C,E,Quiet);Tri(C,D,E,Quiet);
        Rect(1810,897,57,3,Quiet);Rect(1860,893,3,5,Quiet);Line(1800,903,1798,909,Quiet,1.3);Line(1798,909,1806,909,Quiet,1.3);
        Text(FString::Printf(TEXT("%02.0f"),Loaded),1623,922,50,Loaded<=2?Brass:Ivory);
        Line(1731,943,1721,982,Quiet,1.2);Text(FString::Printf(TEXT("%02.0f"),Reserve),1756,948,27,Quiet);
        Text(TEXT("LOADED"),1626,997,10,Quiet,false,90);Text(TEXT("RESERVE"),1755,997,10,Quiet,false,90);
        const int32 Cap=FMath::Clamp(int32(Capacity),1,16);const double Slot=224.0/Cap;
        for(int32 I=0;I<Cap;++I) Rect(1626+I*Slot,1024,FMath::Min(14.,Slot-5),17,I<Loaded?Ivory:FLinearColor(.26f,.26f,.22f,.8f));
        if(Name(Player,TEXT("ActionState"))==TEXT("Reloading")) Text(TEXT("RELOADING"),1742,852,13,Brass,true,100);
        else if(Loaded<=0) Text(TEXT("R  RELOAD"),1742,852,13,Brass,true,100);
        if(M->AllowsPlay())
        {Line(953,540,957,540,FLinearColor(.95,.91,.75,.6));Line(963,540,967,540,FLinearColor(.95,.91,.75,.6));}
    }

    if(M->CheckpointPromptVisible)
    {
        Halo(960,822,251,105,.48);
        Circle(960,766,25,Brass,1.5);Line(867,766,927,766,Brass);Line(993,766,1053,766,Brass);
        Line(950,755,967,755,Ivory,1.8);Line(967,755,971,759,Ivory,1.8);Line(971,759,971,778,Ivory,1.8);
        Line(971,778,950,778,Ivory,1.8);Line(950,778,950,755,Ivory,1.8);
        Rect(956,756,9,7,Ivory);Line(955,768,967,768,Ivory);Line(955,768,955,776,Ivory);Line(967,768,967,776,Ivory);
        Text(TEXT("SAVE CHECKPOINT?"),960,804,20,Ivory,true,40);
        Key(TEXT("E"),805,851,32);Text(TEXT("SAVE"),853,856,15,Ivory,false,60);
        Key(TEXT("ESC"),986,851,49);Text(TEXT("LATER"),1052,856,15,Ivory,false,60);
    }
    if(M->Phase==TEXT("Ready"))
    {
        Halo(960,774,240,80,.34);
        Text(TEXT("G1 BRIDGEHEAD"),960,740,19,Ivory,true,100);
        Key(TEXT("ENTER"),811,792,80);Text(TEXT("BEGIN MISSION"),910,797,15,Ivory,false,50);
    }
    // Feedback is ephemeral and belongs to the current world; no stale tutorial bar.
    static TWeakObjectPtr<AParisBridgeMission> FeedbackWorld;
    static FString LastFeedback;static double FeedbackAt=0;
    const double Now=GetWorld()->GetTimeSeconds();
    if(FeedbackWorld.Get()!=M){FeedbackWorld=M;LastFeedback.Empty();FeedbackAt=Now;}
    if(LastFeedback!=M->Feedback){LastFeedback=M->Feedback;FeedbackAt=Now;}
    const bool ProneNotice=Player && Number(Player,TEXT("DesiredPosture"))==2 && LastFeedback.Contains(TEXT("Prone"));
    if(!LastFeedback.IsEmpty() && M->Phase!=TEXT("Ready") && (Now-FeedbackAt<5 || ProneNotice || M->Phase==TEXT("Error") || M->Phase==TEXT("Lost")))
    {
        const bool Routine=LastFeedback.StartsWith(TEXT("G1 secured")) || LastFeedback.StartsWith(TEXT("Cross"));
        if(!Routine) {Halo(960,916,370,29,.30);Text(LastFeedback.Left(90),960,906,12,M->Phase==TEXT("Error")?Danger:Quiet,true);}
    }
    if(M->CheckpointUnlocked() && !M->InsideCheckpoint())
    {
        FVector2D Screen;
        if(PlayerOwner->ProjectWorldLocationToScreen(M->BridgeheadFeet+FVector(0,0,100),Screen) && Screen.X>100*S && Screen.X<Canvas->SizeX-100*S && Screen.Y>80*S && Screen.Y<Canvas->SizeY-130*S)
        {const float X=(Screen.X-OX)/S,Y=(Screen.Y-OY)/S;Diamond(X,Y,7,Brass);Text(TEXT("CHECKPOINT"),X,Y+12,12,Brass,true,60);}
    }
}

namespace ParisPronePrediction
{
TWeakObjectPtr<ACharacter> Player;
bool Blocked=false;
}
// Read-only witness for the finite integration observer, not a pose override.
bool ParisProneFutureBlocked(const ACharacter* Player)
{ return ParisPronePrediction::Player.Get()==Player && ParisPronePrediction::Blocked; }

void AParisBridgePlayerController::PostProcessInput(const float DeltaTime,const bool bGamePaused)
{
    Super::PostProcessInput(DeltaTime,bGamePaused);
    auto* P=Cast<ACharacter>(GetPawn());
    ParisPronePrediction::Player=P;ParisPronePrediction::Blocked=false;
    if(!P || bGamePaused || !P->ActorHasTag(TEXT("G1_Player")) || Number(P,TEXT("DesiredPosture"))!=2 ||
       !P->bIsCrouched || !P->GetCharacterMovement()->IsMovingOnGround()) return;
    const FVector Input=P->GetPendingMovementInputVector();
    if(Input.SizeSquared()<=.01) return;
    const FVector Feet=P->GetNavAgentLocation(),Forward=P->GetActorForwardVector();
    const FVector Future=Feet+Input.GetSafeNormal()*60*FMath::Max(.1,double(DeltaTime));
    FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisProneFuture),false,P);FHitResult H;
    bool Clear=!GetWorld()->SweepSingleByChannel(H,Feet+FVector(0,0,30),Future+FVector(0,0,30),P->GetActorQuat(),
        ECC_Visibility,FCollisionShape::MakeBox(FVector(130,55,28)),Q);
    for(double Offset:{-120.,0.,110.})
    {
        const FVector Point=Future+Forward*Offset;FHitResult Floor;
        const bool Hit=GetWorld()->LineTraceSingleByChannel(Floor,Point+FVector(0,0,40),Point-FVector(0,0,30),ECC_Visibility,Q);
        Clear&=Hit && Floor.ImpactNormal.Z>=.97 && FMath::Abs(Floor.ImpactPoint.Z-Future.Z)<=10;
    }
    if(!Clear)
    {
        ParisPronePrediction::Blocked=true;
        P->ConsumeMovementInputVector();P->GetCharacterMovement()->StopMovementImmediately();
        if(auto* M=AParisBridgeMission::Find(this)) M->Feedback=TEXT("Prone path blocked. S backs away; Z stands up.");
    }
}
