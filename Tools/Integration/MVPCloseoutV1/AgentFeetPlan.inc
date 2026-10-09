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
