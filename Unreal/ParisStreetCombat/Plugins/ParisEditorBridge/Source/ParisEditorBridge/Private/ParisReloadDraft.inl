// Editor-only generation and testing. All action logic becomes native Blueprint nodes.
namespace ParisReload
{
using namespace ParisDraft;
using FValue = TPair<UEdGraphNode*, FName>;
FEdGraphPinType IntType(){FEdGraphPinType P;P.PinCategory=UEdGraphSchema_K2::PC_Int;return P;}
FEdGraphPinType BoolType(){FEdGraphPinType P;P.PinCategory=UEdGraphSchema_K2::PC_Boolean;return P;}
FValue V(UEdGraph* G,FName Name){return {Get(G,Name),Name};}
FValue Math(UEdGraph* G,FName Fn,FValue A,FValue B)
{auto* N=Call(G,UKismetMathLibrary::StaticClass(),Fn,100,200);Wire(A.Key,A.Value,N,TEXT("A"));Wire(B.Key,B.Value,N,TEXT("B"));return {N,UEdGraphSchema_K2::PN_ReturnValue};}
FValue Const(UEdGraph* G,FName Fn,FValue A,const TCHAR* B)
{auto* N=Call(G,UKismetMathLibrary::StaticClass(),Fn,100,200);Wire(A.Key,A.Value,N,TEXT("A"));N->FindPin(TEXT("B"))->DefaultValue=B;return {N,UEdGraphSchema_K2::PN_ReturnValue};}
FValue And(UEdGraph* G,const TArray<FValue>& Values)
{check(Values.Num());FValue R=Values[0];for(int32 I=1;I<Values.Num();++I)R=Math(G,TEXT("BooleanAND"),R,Values[I]);return R;}
FValue Alive(UEdGraph* G)
{auto* N=Call(G,UKismetMathLibrary::StaticClass(),TEXT("Not_PreBool"),100,200);Wire(Get(G,TEXT("IsDead")),TEXT("IsDead"),N,TEXT("A"));return {N,UEdGraphSchema_K2::PN_ReturnValue};}
FValue State(UEdGraph* G,const TCHAR* Name){return Const(G,TEXT("EqualEqual_NameName"),V(G,TEXT("ActionState")),Name);}
UK2Node_IfThenElse* Branch(UEdGraph* G,UEdGraphNode* Previous,FValue Condition)
{auto* B=Node<UK2Node_IfThenElse>(G,500,0);Wire(Previous,UEdGraphSchema_K2::PN_Then,B,UEdGraphSchema_K2::PN_Execute);Wire(Condition.Key,Condition.Value,B,UEdGraphSchema_K2::PN_Condition);return B;}
void Put(UEdGraph* G,UEdGraphNode*& Previous,FName Name,FValue Value)
{auto* N=Set(G,Name);Wire(Value.Key,Value.Value,N,Name);Wire(Previous,UEdGraphSchema_K2::PN_Then,N,UEdGraphSchema_K2::PN_Execute);Previous=N;}
void PutConst(UEdGraph* G,UEdGraphNode*& Previous,FName Name,const TCHAR* Value)
{auto* N=Set(G,Name);N->FindPin(Name)->DefaultValue=Value;Wire(Previous,UEdGraphSchema_K2::PN_Then,N,UEdGraphSchema_K2::PN_Execute);Previous=N;}
void TokenInputs(UK2Node_FunctionEntry* E)
{E->CreateUserDefinedPin(TEXT("ExpectedActionID"),IntType(),EGPD_Output);E->CreateUserDefinedPin(TEXT("ExpectedGeneration"),IntType(),EGPD_Output);}
FValue TokenMatch(UEdGraph* G,UK2Node_FunctionEntry* E)
{return And(G,{Alive(G),State(G,TEXT("Reloading")),
 Math(G,TEXT("EqualEqual_IntInt"),{E,TEXT("ExpectedActionID")},V(G,TEXT("ActionID"))),
 Math(G,TEXT("EqualEqual_IntInt"),{E,TEXT("ExpectedGeneration")},V(G,TEXT("RestoreGeneration"))),
 Math(G,TEXT("EqualEqual_IntInt"),V(G,TEXT("ReloadActionID")),V(G,TEXT("ActionID"))),
 Math(G,TEXT("EqualEqual_IntInt"),V(G,TEXT("ReloadGeneration")),V(G,TEXT("RestoreGeneration")))});}
UK2Node_CallFunction* CurrentTokenCall(UEdGraph* G,UBlueprint* BP,FName Name,UEdGraphNode* Previous,FName Exec=UEdGraphSchema_K2::PN_Then)
{auto* N=Call(G,BP->GeneratedClass,Name,900,0);Wire(Previous,Exec,N,UEdGraphSchema_K2::PN_Execute);Wire(Get(G,TEXT("ReloadActionID")),TEXT("ReloadActionID"),N,TEXT("ExpectedActionID"));Wire(Get(G,TEXT("ReloadGeneration")),TEXT("ReloadGeneration"),N,TEXT("ExpectedGeneration"));return N;}
void Layout(UBlueprint* BP)
{for(UEdGraph* G:BP->FunctionGraphs){int32 I=0;for(UEdGraphNode* N:G->Nodes){N->NodePosX=(I%6)*380;N->NodePosY=(I/6)*230;++I;}}}
void Functions(UBlueprint* BP,UAnimSequence* Clip,TArray<TSharedPtr<FJsonValue>>& Diagnostics)
{
    UK2Node_FunctionEntry* E=nullptr;
    auto* G=Function(BP,TEXT("PC_CommitReload"),E);TokenInputs(E);
    auto* Position=Call(G,USkeletalMeshComponent::StaticClass(),TEXT("GetPosition"),250,0);
    Wire(Get(G,TEXT("Mesh")),TEXT("Mesh"),Position,UEdGraphSchema_K2::PN_Self);
    auto* NotCommitted=Call(G,UKismetMathLibrary::StaticClass(),TEXT("Not_PreBool"),0,200);Wire(Get(G,TEXT("ReloadCommitted")),TEXT("ReloadCommitted"),NotCommitted,TEXT("A"));
    auto Legal=And(G,{TokenMatch(G,E),{NotCommitted,UEdGraphSchema_K2::PN_ReturnValue},
        Math(G,TEXT("GreaterEqual_DoubleDouble"),{Position,UEdGraphSchema_K2::PN_ReturnValue},V(G,TEXT("ReloadCommitTime"))),
        Const(G,TEXT("Greater_IntInt"),V(G,TEXT("Capacity")),TEXT("0")),
        Const(G,TEXT("GreaterEqual_IntInt"),V(G,TEXT("LoadedAmmo")),TEXT("0")),
        Math(G,TEXT("Less_IntInt"),V(G,TEXT("LoadedAmmo")),V(G,TEXT("Capacity"))),
        Const(G,TEXT("GreaterEqual_IntInt"),V(G,TEXT("ReserveAmmo")),TEXT("0"))});
    auto* B=Branch(G,E,Legal);UEdGraphNode* P=B;
    auto* Transfer=Set(G,TEXT("ReloadTransfer"));Wire(B,UEdGraphSchema_K2::PN_Then,Transfer,UEdGraphSchema_K2::PN_Execute);
    auto Amount=Math(G,TEXT("Min"),Math(G,TEXT("Subtract_IntInt"),V(G,TEXT("Capacity")),V(G,TEXT("LoadedAmmo"))),V(G,TEXT("ReserveAmmo")));
    Wire(Amount.Key,Amount.Value,Transfer,TEXT("ReloadTransfer"));P=Transfer;
    Put(G,P,TEXT("LoadedAmmo"),Math(G,TEXT("Add_IntInt"),V(G,TEXT("LoadedAmmo")),V(G,TEXT("ReloadTransfer"))));
    Put(G,P,TEXT("ReserveAmmo"),Math(G,TEXT("Subtract_IntInt"),V(G,TEXT("ReserveAmmo")),V(G,TEXT("ReloadTransfer"))));
    PutConst(G,P,TEXT("ReloadCommitted"),TEXT("true"));Increment(G,TEXT("ReloadCommitCount"),P);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);check(Compile(BP,Diagnostics));

    G=Function(BP,TEXT("PC_EndReload"),E);TokenInputs(E);B=Branch(G,E,TokenMatch(G,E));P=B;
    PutConst(G,P,TEXT("ActionState"),TEXT("Ready"));Increment(G,TEXT("ActionID"),P);
    auto* Mode=Call(G,USkeletalMeshComponent::StaticClass(),TEXT("SetAnimationMode"),1200,0);Mode->FindPin(TEXT("InAnimationMode"))->DefaultValue=TEXT("AnimationBlueprint");
    Wire(Get(G,TEXT("Mesh")),TEXT("Mesh"),Mode,UEdGraphSchema_K2::PN_Self);Wire(P,UEdGraphSchema_K2::PN_Then,Mode,UEdGraphSchema_K2::PN_Execute);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);check(Compile(BP,Diagnostics));

    G=Function(BP,TEXT("PC_RequestReload"),E);
    auto RateDelta=Math(G,TEXT("Subtract_DoubleDouble"),V(G,TEXT("ReloadPlayRate")),V(G,TEXT("ReloadPlayRate")));
    Legal=And(G,{Alive(G),State(G,TEXT("Ready")),Const(G,TEXT("Greater_IntInt"),V(G,TEXT("Capacity")),TEXT("0")),
        Const(G,TEXT("GreaterEqual_IntInt"),V(G,TEXT("LoadedAmmo")),TEXT("0")),Math(G,TEXT("Less_IntInt"),V(G,TEXT("LoadedAmmo")),V(G,TEXT("Capacity"))),
        Const(G,TEXT("Greater_IntInt"),V(G,TEXT("ReserveAmmo")),TEXT("0")),
        Const(G,TEXT("Greater_DoubleDouble"),V(G,TEXT("ReloadPlayRate")),TEXT("0")),Const(G,TEXT("EqualEqual_DoubleDouble"),RateDelta,TEXT("0"))});
    B=Branch(G,E,Legal);P=B;Increment(G,TEXT("ActionID"),P);
    Put(G,P,TEXT("ReloadActionID"),V(G,TEXT("ActionID")));Put(G,P,TEXT("ReloadGeneration"),V(G,TEXT("RestoreGeneration")));
    PutConst(G,P,TEXT("ActionState"),TEXT("Reloading"));PutConst(G,P,TEXT("ReloadCommitted"),TEXT("false"));PutConst(G,P,TEXT("ReloadElapsed"),TEXT("0"));
    auto* Play=Call(G,USkeletalMeshComponent::StaticClass(),TEXT("PlayAnimation"),1200,0);Play->FindPin(TEXT("NewAnimToPlay"))->DefaultObject=Clip;Play->FindPin(TEXT("bLooping"))->DefaultValue=TEXT("false");
    Wire(Get(G,TEXT("Mesh")),TEXT("Mesh"),Play,UEdGraphSchema_K2::PN_Self);Wire(P,UEdGraphSchema_K2::PN_Then,Play,UEdGraphSchema_K2::PN_Execute);
    auto* Rate=Call(G,USkeletalMeshComponent::StaticClass(),TEXT("SetPlayRate"),1500,0);Wire(Get(G,TEXT("Mesh")),TEXT("Mesh"),Rate,UEdGraphSchema_K2::PN_Self);
    Wire(Get(G,TEXT("ReloadPlayRate")),TEXT("ReloadPlayRate"),Rate,TEXT("Rate"));Wire(Play,UEdGraphSchema_K2::PN_Then,Rate,UEdGraphSchema_K2::PN_Execute);
    auto* Start=Call(G,USkeletalMeshComponent::StaticClass(),TEXT("SetPosition"),1800,0);Start->FindPin(TEXT("InPos"))->DefaultValue=TEXT("0");Start->FindPin(TEXT("bFireNotifies"))->DefaultValue=TEXT("false");
    Wire(Get(G,TEXT("Mesh")),TEXT("Mesh"),Start,UEdGraphSchema_K2::PN_Self);Wire(Rate,UEdGraphSchema_K2::PN_Then,Start,UEdGraphSchema_K2::PN_Execute);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);check(Compile(BP,Diagnostics));

    G=Function(BP,TEXT("PC_ConsumeDiagnosticRound"),E);B=Branch(G,E,And(G,{Alive(G),State(G,TEXT("Ready")),Const(G,TEXT("Greater_IntInt"),V(G,TEXT("LoadedAmmo")),TEXT("0"))}));P=B;
    Put(G,P,TEXT("LoadedAmmo"),Const(G,TEXT("Subtract_IntInt"),V(G,TEXT("LoadedAmmo")),TEXT("1")));
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);check(Compile(BP,Diagnostics));

    G=Function(BP,TEXT("PC_PollReloadPhase"),E);E->CreateUserDefinedPin(TEXT("DeltaSeconds"),Number(),EGPD_Output);
    B=Branch(G,E,And(G,{Alive(G),State(G,TEXT("Reloading"))}));P=B;
    Put(G,P,TEXT("ReloadElapsed"),Math(G,TEXT("Add_DoubleDouble"),V(G,TEXT("ReloadElapsed")),{E,TEXT("DeltaSeconds")}));
    auto Deadline=Const(G,TEXT("Add_DoubleDouble"),Math(G,TEXT("Divide_DoubleDouble"),V(G,TEXT("ReloadDuration")),V(G,TEXT("ReloadPlayRate"))),TEXT("0.5"));
    B=Branch(G,P,Math(G,TEXT("Greater_DoubleDouble"),V(G,TEXT("ReloadElapsed")),Deadline));P=B;
    auto* Timeout=Set(G,TEXT("ReloadTimeoutCount"));Wire(B,UEdGraphSchema_K2::PN_Then,Timeout,UEdGraphSchema_K2::PN_Execute);
    auto Count=Const(G,TEXT("Add_IntInt"),V(G,TEXT("ReloadTimeoutCount")),TEXT("1"));Wire(Count.Key,Count.Value,Timeout,TEXT("ReloadTimeoutCount"));
    CurrentTokenCall(G,BP,TEXT("PC_EndReload"),Timeout);
    auto* Enabled=Node<UK2Node_IfThenElse>(G,800,300);Wire(B,UEdGraphSchema_K2::PN_Else,Enabled,UEdGraphSchema_K2::PN_Execute);Wire(Get(G,TEXT("ReloadPhaseDriverEnabled")),TEXT("ReloadPhaseDriverEnabled"),Enabled,UEdGraphSchema_K2::PN_Condition);
    auto* Commit=CurrentTokenCall(G,BP,TEXT("PC_CommitReload"),Enabled);
    Position=Call(G,USkeletalMeshComponent::StaticClass(),TEXT("GetPosition"),1400,300);Wire(Get(G,TEXT("Mesh")),TEXT("Mesh"),Position,UEdGraphSchema_K2::PN_Self);
    auto EndTime=Const(G,TEXT("Subtract_DoubleDouble"),V(G,TEXT("ReloadDuration")),TEXT("0.001"));
    B=Branch(G,Commit,Math(G,TEXT("GreaterEqual_DoubleDouble"),{Position,UEdGraphSchema_K2::PN_ReturnValue},EndTime));CurrentTokenCall(G,BP,TEXT("PC_EndReload"),B);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);check(Compile(BP,Diagnostics));
    auto* Events=FBlueprintEditorUtils::FindEventGraph(BP);FGraphNodeCreator<UK2Node_Event> Creator(*Events);auto* Tick=Creator.CreateNode();
    Tick->EventReference.SetExternalMember(TEXT("ReceiveTick"),AActor::StaticClass());Tick->bOverrideFunction=true;Creator.Finalize();
    auto* Poll=Call(Events,BP->GeneratedClass,TEXT("PC_PollReloadPhase"),500,0);Wire(Tick,UEdGraphSchema_K2::PN_Then,Poll,UEdGraphSchema_K2::PN_Execute);Wire(Tick,TEXT("DeltaSeconds"),Poll,TEXT("DeltaSeconds"));
    Layout(BP);FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);check(Compile(BP,Diagnostics));
}
}

FString UParisBlueprintAuthoring::CreateSimplifiedReloadDraft()
{
    using namespace ParisDraft;
    auto R=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Assets,Diagnostics;
    const FString Dir=BPDir/TEXT("SimplifiedReloadDraft");const TCHAR* Names[]={TEXT("BP_PCCombatantReloadV1"),TEXT("BP_PCPlayerReloadV1"),TEXT("BP_PCNPCReloadV1")};
    for(auto N:Names)if(FPackageName::DoesPackageExist(Dir/N)){R->SetStringField(TEXT("error"),TEXT("Refusing existing reload draft"));return Json(R);}
    auto* Parent=LoadClass<ACharacter>(nullptr,*(BPDir/TEXT("LifecycleDraft/BP_PCCombatantV2.BP_PCCombatantV2_C")));check(Parent);
    auto Make=[&](const TCHAR* N,UClass* P){return FKismetEditorUtilities::CreateBlueprint(P,CreatePackage(*(Dir/N)),FName(N),BPTYPE_Normal,UBlueprint::StaticClass(),UBlueprintGeneratedClass::StaticClass());};
    auto* Base=Make(Names[0],Parent);auto* Clip=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Reload_2"));check(Clip);
    for(auto Pair:{TPair<FName,FString>(TEXT("Capacity"),TEXT("8")),{TEXT("LoadedAmmo"),TEXT("2")},{TEXT("ReserveAmmo"),TEXT("16")},{TEXT("ReloadActionID"),TEXT("0")},{TEXT("ReloadGeneration"),TEXT("0")},{TEXT("ReloadTransfer"),TEXT("0")},{TEXT("ReloadCommitCount"),TEXT("0")},{TEXT("ReloadTimeoutCount"),TEXT("0")}})
        FBlueprintEditorUtils::AddMemberVariable(Base,Pair.Key,ParisReload::IntType(),Pair.Value);
    for(auto Pair:{TPair<FName,FString>(TEXT("ReloadElapsed"),TEXT("0")),{TEXT("ReloadPlayRate"),TEXT("1")},{TEXT("ReloadDuration"),FString::SanitizeFloat(Clip->GetPlayLength())},{TEXT("ReloadCommitTime"),FString::SanitizeFloat(Clip->GetPlayLength()*.5)}})
        FBlueprintEditorUtils::AddMemberVariable(Base,Pair.Key,Number(),Pair.Value);
    FBlueprintEditorUtils::AddMemberVariable(Base,TEXT("ReloadCommitted"),ParisReload::BoolType(),TEXT("false"));
    FBlueprintEditorUtils::AddMemberVariable(Base,TEXT("ReloadPhaseDriverEnabled"),ParisReload::BoolType(),TEXT("true"));
    ParisReload::Functions(Base,Clip,Diagnostics);
    auto* Allied=LoadObject<USkeletalMesh>(nullptr,*(MeshDir+TEXT("SK_WWII_US_Paratrooper_simple_UE582_v1")));
    auto* German=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1/SK_PC_German_A_Translation_v1"));
    auto* AA=LoadObject<UAnimBlueprint>(nullptr,TEXT("/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_Allied_Stride_v1"));
    auto* GA=LoadObject<UAnimBlueprint>(nullptr,TEXT("/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_German_Stride_v1"));check(Allied&&German&&AA&&GA);
    Defaults(Base,Allied,AA,false);
    auto* Player=Make(Names[1],Base->GeneratedClass);
    const TCHAR* Axes[]={TEXT("PC_MoveForward"),TEXT("PC_MoveRight"),TEXT("PC_LookYaw"),TEXT("PC_LookPitch")};
    const TCHAR* Fn[]={TEXT("PC_RequestMoveForward"),TEXT("PC_RequestMoveRight"),TEXT("PC_RequestLookYaw"),TEXT("PC_RequestLookPitch")};
    for(int32 I=0;I<4;++I)InputEvent(Player,Axes[I],Fn[I],I*300);
    auto* ArmNode=Player->SimpleConstructionScript->CreateNode(USpringArmComponent::StaticClass(),TEXT("DiagnosticCameraArm"));Player->SimpleConstructionScript->AddNode(ArmNode);
    auto* Arm=CastChecked<USpringArmComponent>(ArmNode->ComponentTemplate);Arm->TargetArmLength=300;Arm->bUsePawnControlRotation=true;Arm->SetRelativeLocation(FVector(0,0,55));
    auto* Cam=Player->SimpleConstructionScript->CreateNode(UCameraComponent::StaticClass(),TEXT("DiagnosticCamera"));ArmNode->AddChildNode(Cam);Cam->AttachToName=USpringArmComponent::SocketName;
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Player);check(Compile(Player,Diagnostics));Defaults(Player,Allied,AA,true);
    auto* NPC=Make(Names[2],Base->GeneratedClass);check(Compile(NPC,Diagnostics));Defaults(NPC,German,GA,false);
    for(auto N:Names)Assets.Add(MakeShared<FJsonValueString>(Dir/N));R->SetArrayField(TEXT("assets"),Assets);R->SetArrayField(TEXT("compiler_messages"),Diagnostics);
    R->SetStringField(TEXT("presentation"),TEXT("Generic third-person animation-phase placeholder, not M1/FP acceptance"));R->SetNumberField(TEXT("commit_time_seconds"),Clip->GetPlayLength()*.5);R->SetNumberField(TEXT("duration_seconds"),Clip->GetPlayLength());return Json(R);
}

FString UParisBlueprintAuthoring::ProbeSimplifiedReload(const FString& ClassPath,double PlaybackRate,int32 FramesPerSecond)
{
    using namespace ParisDraft;
    check(FramesPerSecond==30||FramesPerSecond==60||FramesPerSecond==120);
    auto R=MakeShared<FJsonObject>();R->SetStringField(TEXT("class"),ClassPath);R->SetNumberField(TEXT("rate"),PlaybackRate);R->SetNumberField(TEXT("fixed_steps_per_second"),FramesPerSecond);
    auto* Class=LoadClass<ACharacter>(nullptr,*ClassPath);check(Class);
    const auto IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(true).SetTransactional(false);
    auto* W=UWorld::CreateWorld(EWorldType::Game,false,TEXT("ParisReloadProbe"),nullptr,true,ERHIFeatureLevel::Num,&IV);GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    struct Guard{UWorld* Old;explicit Guard(UWorld* Current):Old(GWorld){GWorld=Current;}~Guard(){GWorld=Old;}}WorldGuard(W);
    auto* Floor=W->SpawnActor<AStaticMeshActor>(FVector(0,0,-5),FRotator::ZeroRotator);Floor->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube")));Floor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Floor->SetActorScale3D(FVector(100,100,.1));
    auto* C=W->SpawnActor<ACharacter>(Class,FVector(0,0,120),FRotator::ZeroRotator);W->InitializeActorsForPlay(FURL());W->BeginPlay();W->SetBegunPlay(true);if(!C->HasActorBegunPlay())C->DispatchBeginPlay();
    auto I=[&](FName N){return Property<FIntProperty>(Class,N)->GetPropertyValue_InContainer(C);};auto D=[&](FName N){return Property<FDoubleProperty>(Class,N)->GetPropertyValue_InContainer(C);};
    auto SI=[&](FName N,int32 V){Property<FIntProperty>(Class,N)->SetPropertyValue_InContainer(C,V);};auto SD=[&](FName N,double V){Property<FDoubleProperty>(Class,N)->SetPropertyValue_InContainer(C,V);};
    auto State=[&](){return Property<FNameProperty>(Class,TEXT("ActionState"))->GetPropertyValue_InContainer(C);};
    auto Invoke=[&](FName Name,int32 ID=-1,int32 Generation=-1){auto* F=C->FindFunction(Name);check(F);FStructOnScope P(F);if(ID>=0){Property<FIntProperty>(F,TEXT("ExpectedActionID"))->SetPropertyValue_InContainer(P.GetStructMemory(),ID);Property<FIntProperty>(F,TEXT("ExpectedGeneration"))->SetPropertyValue_InContainer(P.GetStructMemory(),Generation);}C->ProcessEvent(F,P.GetStructMemory());};
    auto Tick=[&](double Seconds){for(int32 K=0;K<FMath::CeilToInt(Seconds*FramesPerSecond);++K){++GFrameCounter;W->Tick(LEVELTICK_All,1.f/FramesPerSecond);}};
    auto Init=[&](int32 Loaded=2,int32 Reserve=16){Invoke(TEXT("PC_ResetLifecycle"));SI(TEXT("Capacity"),8);SI(TEXT("LoadedAmmo"),Loaded);SI(TEXT("ReserveAmmo"),Reserve);SI(TEXT("ReloadCommitCount"),0);SI(TEXT("ReloadTimeoutCount"),0);SD(TEXT("ReloadPlayRate"),PlaybackRate);Property<FBoolProperty>(Class,TEXT("ReloadPhaseDriverEnabled"))->SetPropertyValue_InContainer(C,true);C->SetActorLocation(FVector(0,0,120),false,nullptr,ETeleportType::TeleportPhysics);Tick(.1);};
    TArray<TSharedPtr<FJsonValue>> Cases;bool All=true;
    auto Expect=[&](const TCHAR* Name,bool Pass){auto P=MakeShared<FJsonObject>();P->SetStringField(TEXT("name"),Name);P->SetBoolField(TEXT("pass"),Pass);P->SetNumberField(TEXT("loaded"),I(TEXT("LoadedAmmo")));P->SetNumberField(TEXT("reserve"),I(TEXT("ReserveAmmo")));P->SetNumberField(TEXT("commits"),I(TEXT("ReloadCommitCount")));P->SetStringField(TEXT("state"),State().ToString());Cases.Add(MakeShared<FJsonValueObject>(P));All&=Pass;};
    const double Duration=D(TEXT("ReloadDuration")),Marker=D(TEXT("ReloadCommitTime"));
    Init();Invoke(TEXT("PC_RequestReload"));const int32 First=I(TEXT("ActionID")),Gen=I(TEXT("RestoreGeneration"));
    Invoke(TEXT("PC_RequestReload"));Invoke(TEXT("PC_ConsumeDiagnosticRound"));Expect(TEXT("busy_start_and_fire_rejected"),I(TEXT("ActionID"))==First&&I(TEXT("LoadedAmmo"))==2);
    Invoke(TEXT("PC_CommitReload"),First,Gen);Expect(TEXT("early_commit_rejected"),I(TEXT("LoadedAmmo"))==2&&I(TEXT("ReloadCommitCount"))==0);
    Tick((Marker+.1)/PlaybackRate);Expect(TEXT("animation_phase_commits_once"),I(TEXT("LoadedAmmo"))==8&&I(TEXT("ReserveAmmo"))==10&&I(TEXT("ReloadCommitCount"))==1);
    Invoke(TEXT("PC_CommitReload"),First,Gen);Expect(TEXT("duplicate_commit_ignored"),I(TEXT("ReserveAmmo"))==10&&I(TEXT("ReloadCommitCount"))==1);
    Tick(Duration/PlaybackRate);Expect(TEXT("normal_finish_ready"),State()==TEXT("Ready")&&C->GetMesh()->GetAnimInstance()&&C->GetMesh()->GetAnimationMode()==EAnimationMode::AnimationBlueprint);
    const int32 Finished=I(TEXT("ActionID"));Invoke(TEXT("PC_EndReload"),First,Gen);Expect(TEXT("duplicate_end_ignored"),I(TEXT("ActionID"))==Finished);
    Invoke(TEXT("PC_ConsumeDiagnosticRound"));Invoke(TEXT("PC_ConsumeDiagnosticRound"));Invoke(TEXT("PC_RequestReload"));Tick((Duration+.1)/PlaybackRate);Expect(TEXT("repeated_reload_conserves_ammo"),I(TEXT("LoadedAmmo"))==8&&I(TEXT("ReserveAmmo"))==8&&I(TEXT("ReloadCommitCount"))==2);
    Init(4,2);Invoke(TEXT("PC_RequestReload"));Tick((Duration+.1)/PlaybackRate);Expect(TEXT("partial_reserve"),I(TEXT("LoadedAmmo"))==6&&I(TEXT("ReserveAmmo"))==0&&I(TEXT("ReloadCommitCount"))==1);
    Init(0,3);Invoke(TEXT("PC_RequestReload"));Tick((Duration+.1)/PlaybackRate);Expect(TEXT("empty_loaded_partial_fill"),I(TEXT("LoadedAmmo"))==3&&I(TEXT("ReserveAmmo"))==0);
    Init();Invoke(TEXT("PC_RequestReload"));int32 Token=I(TEXT("ActionID")),G=I(TEXT("RestoreGeneration"));Tick(Marker*.25/PlaybackRate);Invoke(TEXT("PC_EndReload"),Token,G);Invoke(TEXT("PC_CommitReload"),Token,G);Expect(TEXT("cancel_before_no_transfer"),I(TEXT("LoadedAmmo"))==2&&I(TEXT("ReserveAmmo"))==16&&State()==TEXT("Ready"));
    Init();Invoke(TEXT("PC_RequestReload"));Token=I(TEXT("ActionID"));G=I(TEXT("RestoreGeneration"));Tick((Marker+.1)/PlaybackRate);Invoke(TEXT("PC_EndReload"),Token,G);Invoke(TEXT("PC_CommitReload"),Token,G);Expect(TEXT("cancel_after_keeps_transfer"),I(TEXT("LoadedAmmo"))==8&&I(TEXT("ReserveAmmo"))==10&&I(TEXT("ReloadCommitCount"))==1);
    Init();Invoke(TEXT("PC_RequestReload"));Token=I(TEXT("ActionID"));G=I(TEXT("RestoreGeneration"));Property<FBoolProperty>(Class,TEXT("ReloadPhaseDriverEnabled"))->SetPropertyValue_InContainer(C,false);Tick(Duration/PlaybackRate+.7);Invoke(TEXT("PC_CommitReload"),Token,G);Expect(TEXT("missing_marker_timeout_no_ammo"),I(TEXT("LoadedAmmo"))==2&&I(TEXT("ReserveAmmo"))==16&&State()==TEXT("Ready")&&I(TEXT("ReloadTimeoutCount"))==1);
    Init();Invoke(TEXT("PC_RequestReload"));Token=I(TEXT("ActionID"));G=I(TEXT("RestoreGeneration"));Property<FBoolProperty>(Class,TEXT("ReloadPhaseDriverEnabled"))->SetPropertyValue_InContainer(C,false);Tick((Marker+.1)/PlaybackRate);Invoke(TEXT("PC_CommitReload"),Token+100,G);Invoke(TEXT("PC_CommitReload"),Token,G+100);Expect(TEXT("wrong_id_generation_rejected"),I(TEXT("LoadedAmmo"))==2&&I(TEXT("ReloadCommitCount"))==0);
    Init();Invoke(TEXT("PC_RequestReload"));Token=I(TEXT("ActionID"));G=I(TEXT("RestoreGeneration"));Invoke(TEXT("PC_Die"));Tick(Duration/PlaybackRate+.1);Invoke(TEXT("PC_CommitReload"),Token,G);Expect(TEXT("death_before_no_transfer"),State()==TEXT("Dead")&&I(TEXT("LoadedAmmo"))==2&&I(TEXT("ReserveAmmo"))==16);
    Invoke(TEXT("PC_ResetLifecycle"));Invoke(TEXT("PC_CommitReload"),Token,G);Expect(TEXT("reset_rejects_old_event_preserves_ammo"),State()==TEXT("Ready")&&I(TEXT("LoadedAmmo"))==2&&I(TEXT("ReserveAmmo"))==16);
    Init();Invoke(TEXT("PC_RequestReload"));Tick((Marker+.1)/PlaybackRate);Token=I(TEXT("ActionID"));G=I(TEXT("RestoreGeneration"));Invoke(TEXT("PC_Die"));Invoke(TEXT("PC_CommitReload"),Token,G);Expect(TEXT("death_after_keeps_transfer"),State()==TEXT("Dead")&&I(TEXT("LoadedAmmo"))==8&&I(TEXT("ReserveAmmo"))==10&&I(TEXT("ReloadCommitCount"))==1);
    for(auto Pair:{TPair<int32,int32>(8,16),{2,0},{-1,16},{2,-1}}){Init(Pair.Key,Pair.Value);const int32 A=I(TEXT("ActionID"));Invoke(TEXT("PC_RequestReload"));Expect(TEXT("full_empty_or_invalid_request_rejected"),State()==TEXT("Ready")&&I(TEXT("ActionID"))==A);}
    Init();SI(TEXT("Capacity"),0);Token=I(TEXT("ActionID"));Invoke(TEXT("PC_RequestReload"));Expect(TEXT("invalid_capacity_rejected"),State()==TEXT("Ready")&&I(TEXT("ActionID"))==Token);
    for(double Rate:{0.,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){Init();SD(TEXT("ReloadPlayRate"),Rate);Token=I(TEXT("ActionID"));Invoke(TEXT("PC_RequestReload"));Expect(TEXT("invalid_play_rate_rejected"),State()==TEXT("Ready")&&I(TEXT("ActionID"))==Token);}
    R->SetArrayField(TEXT("cases"),Cases);R->SetBoolField(TEXT("all_pass"),All);R->SetNumberField(TEXT("duration_seconds"),Duration);R->SetNumberField(TEXT("placeholder_commit_seconds"),Marker);
    W->EndPlay(EEndPlayReason::Quit);GEngine->DestroyWorldContext(W);W->DestroyWorld(false);return Json(R);
}
