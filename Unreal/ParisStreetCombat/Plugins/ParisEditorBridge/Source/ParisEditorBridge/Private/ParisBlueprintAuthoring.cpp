#include "ParisBlueprintAuthoring.h"
#include <limits>

#include "Modules/ModuleManager.h"
#include "Misc/PackageName.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/FileManager.h"
#include "AssetToolsModule.h"
#include "Animation/AnimBlueprint.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/BlendSpace1D.h"
#include "AnimGraphNode_BlendSpacePlayer.h"
#include "AnimGraphNode_Root.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Blueprint.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SceneCapture2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Engine/Engine.h"
#include "Engine/SCS_Node.h"
#include "Engine/SimpleConstructionScript.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Animation/SkeletalMeshActor.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Factories/AnimBlueprintFactory.h"
#include "Factories/BlendSpaceFactory1D.h"
#include "Factories/BlendSpaceFactoryNew.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "K2Node_CallFunction.h"
#include "K2Node_Event.h"
#include "K2Node_FunctionEntry.h"
#include "K2Node_InputAxisEvent.h"
#include "K2Node_IfThenElse.h"
#include "K2Node_VariableGet.h"
#include "K2Node_VariableSet.h"
#include "Kismet/KismetMathLibrary.h"
#include "Kismet/KismetRenderingLibrary.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "KismetCompiler.h"
#include "Serialization/JsonSerializer.h"
#include "SkeletalRenderPublic.h"
#include "RenderingThread.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, ParisEditorBridge)

bool UParisBlueprintAuthoring::ClearSkeletonPreviewAttachments(const FString& SkeletonPath)
{
    // Python does not expose FPreviewAssetAttachContainer; editor data only.
    if (!SkeletonPath.StartsWith(TEXT("/Game/Rifle_01/"))) return false;
    auto* Skeleton = LoadObject<USkeleton>(nullptr, *SkeletonPath);
    if (!Skeleton) return false;
    Skeleton->Modify();
    Skeleton->PreviewAttachedAssetContainer.ClearAllAttachedObjects();
    Skeleton->MarkPackageDirty();
    return true;
}

namespace ParisDraft
{
const FString BPDir = TEXT("/Game/ParisCombat/Blueprints/Characters");
const FString AnimDir = TEXT("/Game/ParisCombat/Animation/LocomotionDraft");
const FString MeshDir = TEXT("/Game/ParisCombat/Characters/Adaptation/Meshes/");

FString Json(const TSharedRef<FJsonObject>& Value)
{
    FString Out;
    FJsonSerializer::Serialize(Value, TJsonWriterFactory<>::Create(&Out));
    return Out;
}

FEdGraphPinType Number()
{
    FEdGraphPinType Type;
    Type.PinCategory = UEdGraphSchema_K2::PC_Real;
    Type.PinSubCategory = UEdGraphSchema_K2::PC_Double;
    return Type;
}

template<class T> T* Node(UEdGraph* Graph, int32 X, int32 Y)
{
    FGraphNodeCreator<T> Creator(*Graph);
    T* Result = Creator.CreateNode();
    Result->NodePosX = X;
    Result->NodePosY = Y;
    Creator.Finalize();
    return Result;
}

template<class T> T* Property(UStruct* Owner,FName Name)
{ auto* P=FindFProperty<T>(Owner,Name); check(P); return P; }

UK2Node_CallFunction* Call(UEdGraph* Graph, UClass* Owner, FName Name, int32 X, int32 Y)
{
    UFunction* Function = Owner->FindFunctionByName(Name);
    checkf(Function, TEXT("Required engine function missing: %s"), *Name.ToString());
    FGraphNodeCreator<UK2Node_CallFunction> Creator(*Graph);
    auto* Result = Creator.CreateNode();
    Result->SetFromFunction(Function);
    Result->NodePosX = X;
    Result->NodePosY = Y;
    Creator.Finalize();
    return Result;
}

void Wire(UEdGraphNode* A, FName APin, UEdGraphNode* B, FName BPin)
{
    auto* Out = A->FindPin(APin);
    auto* In = B->FindPin(BPin);
    checkf(Out && In, TEXT("Pin missing: %s.%s -> %s.%s"), *A->GetName(), *APin.ToString(), *B->GetName(), *BPin.ToString());
    checkf(A->GetGraph()->GetSchema()->TryCreateConnection(Out, In), TEXT("Cannot wire %s -> %s"), *APin.ToString(), *BPin.ToString());
}

bool Compile(UBlueprint* BP, TArray<TSharedPtr<FJsonValue>>& Diagnostics)
{
    FCompilerResultsLog Log;
    FKismetEditorUtilities::CompileBlueprint(BP, EBlueprintCompileOptions::None, &Log);
    for (const auto& Message : Log.Messages)
        Diagnostics.Add(MakeShared<FJsonValueString>(Message->ToText().ToString()));
    return Log.NumErrors == 0 && BP->Status != BS_Error && BP->GeneratedClass;
}

void MoveFunction(UBlueprint* BP, FName Name, FName EngineFunction, FName Direction)
{
    UEdGraph* Graph = FBlueprintEditorUtils::CreateNewGraph(BP, Name, UEdGraph::StaticClass(), UEdGraphSchema_K2::StaticClass());
    FBlueprintEditorUtils::AddFunctionGraph(BP, Graph, true, static_cast<UFunction*>(nullptr));
    TArray<UK2Node_FunctionEntry*> Entries;
    Graph->GetNodesOfClass(Entries);
    check(Entries.Num() == 1);
    auto* Entry = Entries[0];
    Entry->SetExtraFlags(FUNC_Public | FUNC_BlueprintCallable);
    Entry->CreateUserDefinedPin(TEXT("AxisValue"), Number(), EGPD_Output);
    auto* Request = Call(Graph, APawn::StaticClass(), EngineFunction, 450, 0);
    Wire(Entry, UEdGraphSchema_K2::PN_Then, Request, UEdGraphSchema_K2::PN_Execute);
    if (!Direction.IsNone())
    {
        auto* Vector = Call(Graph, AActor::StaticClass(), Direction, 200, 180);
        Wire(Vector, UEdGraphSchema_K2::PN_ReturnValue, Request, TEXT("WorldDirection"));
        Wire(Entry, TEXT("AxisValue"), Request, TEXT("ScaleValue"));
    }
    else Wire(Entry, TEXT("AxisValue"), Request, TEXT("Val"));
}

void InputEvent(UBlueprint* BP, FName Axis, FName Function, int32 Y)
{
    auto* Graph = FBlueprintEditorUtils::FindEventGraph(BP);
    FGraphNodeCreator<UK2Node_InputAxisEvent> Creator(*Graph);
    auto* Event = Creator.CreateNode();
    Event->Initialize(Axis);
    Event->NodePosY = Y;
    Creator.Finalize();
    auto* Request = Call(Graph, BP->GeneratedClass, Function, 350, Y);
    Wire(Event, UEdGraphSchema_K2::PN_Then, Request, UEdGraphSchema_K2::PN_Execute);
    Wire(Event, TEXT("AxisValue"), Request, TEXT("AxisValue"));
}

UK2Node_VariableGet* Get(UEdGraph* Graph,FName Name,int32 X=0,int32 Y=200)
{
    FGraphNodeCreator<UK2Node_VariableGet> C(*Graph); auto* N=C.CreateNode();
    N->VariableReference.SetSelfMember(Name); N->NodePosX=X; N->NodePosY=Y; C.Finalize(); return N;
}
UK2Node_VariableSet* Set(UEdGraph* Graph,FName Name,int32 X=300,int32 Y=0)
{
    FGraphNodeCreator<UK2Node_VariableSet> C(*Graph); auto* N=C.CreateNode();
    N->VariableReference.SetSelfMember(Name); N->NodePosX=X; N->NodePosY=Y; C.Finalize(); return N;
}
UEdGraph* Function(UBlueprint* BP,FName Name,UK2Node_FunctionEntry*& Entry)
{
    auto* G=FBlueprintEditorUtils::CreateNewGraph(BP,Name,UEdGraph::StaticClass(),UEdGraphSchema_K2::StaticClass());
    FBlueprintEditorUtils::AddFunctionGraph(BP,G,true,static_cast<UFunction*>(nullptr));
    TArray<UK2Node_FunctionEntry*> E; G->GetNodesOfClass(E); check(E.Num()==1); Entry=E[0];
    Entry->SetExtraFlags(FUNC_Public|FUNC_BlueprintCallable); return G;
}
void Increment(UEdGraph* G,FName Variable,UEdGraphNode*& Previous)
{
    auto* Add=Call(G,UKismetMathLibrary::StaticClass(),TEXT("Add_IntInt"),0,200);
    Wire(Get(G,Variable),Variable,Add,TEXT("A")); Add->FindPin(TEXT("B"))->DefaultValue=TEXT("1");
    auto* Next=Set(G,Variable); Wire(Add,UEdGraphSchema_K2::PN_ReturnValue,Next,Variable);
    Wire(Previous,UEdGraphSchema_K2::PN_Then,Next,UEdGraphSchema_K2::PN_Execute); Previous=Next;
}
void LifecycleFunctions(UBlueprint* BP,TArray<TSharedPtr<FJsonValue>>& Diagnostics)
{
    UK2Node_FunctionEntry* Entry=nullptr;
    auto* G=Function(BP,TEXT("PC_Die"),Entry);
    auto* Branch=Node<UK2Node_IfThenElse>(G,300,0);
    Wire(Get(G,TEXT("IsDead")),TEXT("IsDead"),Branch,UEdGraphSchema_K2::PN_Condition);
    Wire(Entry,UEdGraphSchema_K2::PN_Then,Branch,UEdGraphSchema_K2::PN_Execute);
    auto* Dead=Set(G,TEXT("IsDead"),600); Dead->FindPin(TEXT("IsDead"))->DefaultValue=TEXT("true");
    Wire(Branch,UEdGraphSchema_K2::PN_Else,Dead,UEdGraphSchema_K2::PN_Execute);
    UEdGraphNode* Previous=Dead;
    for(auto Pair : {TPair<FName,FString>(TEXT("Health"),TEXT("0")),TPair<FName,FString>(TEXT("ActionState"),TEXT("Dead"))})
    { auto* Next=Set(G,Pair.Key); Next->FindPin(Pair.Key)->DefaultValue=Pair.Value;
      Wire(Previous,UEdGraphSchema_K2::PN_Then,Next,UEdGraphSchema_K2::PN_Execute); Previous=Next; }
    Increment(G,TEXT("ActionID"),Previous);
    auto* Stop=Call(G,UCharacterMovementComponent::StaticClass(),TEXT("StopMovementImmediately"),900,0);
    Wire(Get(G,TEXT("CharacterMovement")),TEXT("CharacterMovement"),Stop,UEdGraphSchema_K2::PN_Self);
    Wire(Previous,UEdGraphSchema_K2::PN_Then,Stop,UEdGraphSchema_K2::PN_Execute);
    auto* Disable=Call(G,UCharacterMovementComponent::StaticClass(),TEXT("DisableMovement"),1200,0);
    Wire(Get(G,TEXT("CharacterMovement")),TEXT("CharacterMovement"),Disable,UEdGraphSchema_K2::PN_Self);
    Wire(Stop,UEdGraphSchema_K2::PN_Then,Disable,UEdGraphSchema_K2::PN_Execute);
    auto* Collision=Call(G,UPrimitiveComponent::StaticClass(),TEXT("SetCollisionEnabled"),1500,0);
    Collision->FindPin(TEXT("NewType"))->DefaultValue=TEXT("NoCollision");
    Wire(Get(G,TEXT("CapsuleComponent")),TEXT("CapsuleComponent"),Collision,UEdGraphSchema_K2::PN_Self);
    Wire(Disable,UEdGraphSchema_K2::PN_Then,Collision,UEdGraphSchema_K2::PN_Execute);
    auto* Play=Call(G,USkeletalMeshComponent::StaticClass(),TEXT("PlayAnimation"),1800,0);
    Play->FindPin(TEXT("NewAnimToPlay"))->DefaultObject=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Death_3"));
    Play->FindPin(TEXT("bLooping"))->DefaultValue=TEXT("false");
    Wire(Get(G,TEXT("Mesh")),TEXT("Mesh"),Play,UEdGraphSchema_K2::PN_Self);
    Wire(Collision,UEdGraphSchema_K2::PN_Then,Play,UEdGraphSchema_K2::PN_Execute);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP); check(Compile(BP,Diagnostics));

    G=Function(BP,TEXT("PC_ApplyDamage"),Entry); Entry->CreateUserDefinedPin(TEXT("Amount"),Number(),EGPD_Output);
    auto* Positive=Call(G,UKismetMathLibrary::StaticClass(),TEXT("Greater_DoubleDouble"),200,180);
    Wire(Entry,TEXT("Amount"),Positive,TEXT("A")); Positive->FindPin(TEXT("B"))->DefaultValue=TEXT("0");
    auto* Alive=Call(G,UKismetMathLibrary::StaticClass(),TEXT("Not_PreBool"),200,350);
    Wire(Get(G,TEXT("IsDead")),TEXT("IsDead"),Alive,TEXT("A"));
    auto* Legal=Call(G,UKismetMathLibrary::StaticClass(),TEXT("BooleanAND"),400,180);
    Wire(Positive,UEdGraphSchema_K2::PN_ReturnValue,Legal,TEXT("A")); Wire(Alive,UEdGraphSchema_K2::PN_ReturnValue,Legal,TEXT("B"));
    auto* Delta=Call(G,UKismetMathLibrary::StaticClass(),TEXT("Subtract_DoubleDouble"),400,450);
    Wire(Entry,TEXT("Amount"),Delta,TEXT("A")); Wire(Entry,TEXT("Amount"),Delta,TEXT("B"));
    auto* Finite=Call(G,UKismetMathLibrary::StaticClass(),TEXT("EqualEqual_DoubleDouble"),600,450);
    Wire(Delta,UEdGraphSchema_K2::PN_ReturnValue,Finite,TEXT("A")); Finite->FindPin(TEXT("B"))->DefaultValue=TEXT("0");
    auto* Valid=Call(G,UKismetMathLibrary::StaticClass(),TEXT("BooleanAND"),600,180);
    Wire(Legal,UEdGraphSchema_K2::PN_ReturnValue,Valid,TEXT("A")); Wire(Finite,UEdGraphSchema_K2::PN_ReturnValue,Valid,TEXT("B"));
    Branch=Node<UK2Node_IfThenElse>(G,800,0); Wire(Valid,UEdGraphSchema_K2::PN_ReturnValue,Branch,UEdGraphSchema_K2::PN_Condition);
    Wire(Entry,UEdGraphSchema_K2::PN_Then,Branch,UEdGraphSchema_K2::PN_Execute);
    auto* Subtract=Call(G,UKismetMathLibrary::StaticClass(),TEXT("Subtract_DoubleDouble"),600,200);
    Wire(Get(G,TEXT("Health")),TEXT("Health"),Subtract,TEXT("A")); Wire(Entry,TEXT("Amount"),Subtract,TEXT("B"));
    auto* Clamp=Call(G,UKismetMathLibrary::StaticClass(),TEXT("FClamp"),800,200);
    Wire(Subtract,UEdGraphSchema_K2::PN_ReturnValue,Clamp,TEXT("Value"));
    Clamp->FindPin(TEXT("Min"))->DefaultValue=TEXT("0"); Wire(Get(G,TEXT("MaxHealth")),TEXT("MaxHealth"),Clamp,TEXT("Max"));
    auto* Health=Set(G,TEXT("Health"),1000); Wire(Clamp,UEdGraphSchema_K2::PN_ReturnValue,Health,TEXT("Health"));
    Wire(Branch,UEdGraphSchema_K2::PN_Then,Health,UEdGraphSchema_K2::PN_Execute);
    auto* Empty=Call(G,UKismetMathLibrary::StaticClass(),TEXT("LessEqual_DoubleDouble"),1200,200);
    Wire(Get(G,TEXT("Health")),TEXT("Health"),Empty,TEXT("A")); Empty->FindPin(TEXT("B"))->DefaultValue=TEXT("0");
    Branch=Node<UK2Node_IfThenElse>(G,1400,0); Wire(Empty,UEdGraphSchema_K2::PN_ReturnValue,Branch,UEdGraphSchema_K2::PN_Condition);
    Wire(Health,UEdGraphSchema_K2::PN_Then,Branch,UEdGraphSchema_K2::PN_Execute);
    auto* Die=Call(G,BP->GeneratedClass,TEXT("PC_Die"),1600,0); Wire(Branch,UEdGraphSchema_K2::PN_Then,Die,UEdGraphSchema_K2::PN_Execute);

    G=Function(BP,TEXT("PC_ResetLifecycle"),Entry); Previous=Entry;
    Increment(G,TEXT("RestoreGeneration"),Previous); Increment(G,TEXT("ActionID"),Previous);
    Health=Set(G,TEXT("Health")); Wire(Get(G,TEXT("MaxHealth")),TEXT("MaxHealth"),Health,TEXT("Health"));
    Wire(Previous,UEdGraphSchema_K2::PN_Then,Health,UEdGraphSchema_K2::PN_Execute); Previous=Health;
    for(auto Pair : {TPair<FName,FString>(TEXT("IsDead"),TEXT("false")),TPair<FName,FString>(TEXT("ActionState"),TEXT("Ready"))})
    { auto* Next=Set(G,Pair.Key); Next->FindPin(Pair.Key)->DefaultValue=Pair.Value;
      Wire(Previous,UEdGraphSchema_K2::PN_Then,Next,UEdGraphSchema_K2::PN_Execute); Previous=Next; }
    auto* Mode=Call(G,USkeletalMeshComponent::StaticClass(),TEXT("SetAnimationMode"),900,0);
    Mode->FindPin(TEXT("InAnimationMode"))->DefaultValue=TEXT("AnimationBlueprint");
    Wire(Get(G,TEXT("Mesh")),TEXT("Mesh"),Mode,UEdGraphSchema_K2::PN_Self); Wire(Previous,UEdGraphSchema_K2::PN_Then,Mode,UEdGraphSchema_K2::PN_Execute);
    Collision=Call(G,UPrimitiveComponent::StaticClass(),TEXT("SetCollisionEnabled"),1200,0);
    Collision->FindPin(TEXT("NewType"))->DefaultValue=TEXT("QueryAndPhysics");
    Wire(Get(G,TEXT("CapsuleComponent")),TEXT("CapsuleComponent"),Collision,UEdGraphSchema_K2::PN_Self); Wire(Mode,UEdGraphSchema_K2::PN_Then,Collision,UEdGraphSchema_K2::PN_Execute);
    auto* Walk=Call(G,UCharacterMovementComponent::StaticClass(),TEXT("SetMovementMode"),1500,0);
    Walk->FindPin(TEXT("NewMovementMode"))->DefaultValue=TEXT("MOVE_Walking");
    Wire(Get(G,TEXT("CharacterMovement")),TEXT("CharacterMovement"),Walk,UEdGraphSchema_K2::PN_Self); Wire(Collision,UEdGraphSchema_K2::PN_Then,Walk,UEdGraphSchema_K2::PN_Execute);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP); check(Compile(BP,Diagnostics));
}

UAnimBlueprint* Animation(USkeleton* Skeleton, const FString& Label, TArray<TSharedPtr<FJsonValue>>& Diagnostics, bool Directional=false)
{
    auto& Tools = FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools")).Get();
    const FString Directory = Directional ? TEXT("/Game/ParisCombat/Animation/DirectionalDraft") : AnimDir;
    UFactory* BSFactory;
    if(Directional) { auto* F=NewObject<UBlendSpaceFactoryNew>(); F->TargetSkeleton=Skeleton; BSFactory=F; }
    else { auto* F=NewObject<UBlendSpaceFactory1D>(); F->TargetSkeleton=Skeleton; BSFactory=F; }
    auto* BS = CastChecked<UBlendSpace>(Tools.CreateAsset(TEXT("BS_PC_") + Label, Directory, Directional ? UBlendSpace::StaticClass() : UBlendSpace1D::StaticClass(), BSFactory));
    auto& Axis = const_cast<FBlendParameter&>(BS->GetBlendParameter(0));
    Axis.DisplayName = TEXT("GroundSpeed"); Axis.Min = 0; Axis.Max = 300; Axis.GridNum = 2;
    const TCHAR* Names[] = { TEXT("Rifle_Idle"), TEXT("Rifle_WalkFwdLoop"), TEXT("Rifle_RunFwdLoop") };
    for (int32 I=0; !Directional && I<3; ++I)
    {
        auto* Clip = LoadObject<UAnimSequence>(nullptr, *(FString(TEXT("/Game/RifleAnimsetPro/Animations/InPlace/")) + Names[I]));
        check(Clip && !Clip->bEnableRootMotion);
        check(BS->AddSample(Clip, FVector(I * 150., 0, 0)) != INDEX_NONE);
    }
    if (Directional)
    {
        Axis.DisplayName = TEXT("VelocityForward"); Axis.Min=-300; Axis.Max=300; Axis.GridNum=4;
        auto& Side = const_cast<FBlendParameter&>(BS->GetBlendParameter(1));
        Side.DisplayName=TEXT("VelocityRight"); Side.Min=-300; Side.Max=300; Side.GridNum=4;
        auto Sample = [&](const TCHAR* Name, FVector Point)
        {
            auto* Clip=LoadObject<UAnimSequence>(nullptr, *(FString(TEXT("/Game/RifleAnimsetPro/Animations/InPlace/"))+Name));
            check(Clip && !Clip->bEnableRootMotion); check(BS->AddSample(Clip,Point)!=INDEX_NONE);
        };
        Sample(TEXT("Rifle_Idle"),FVector::ZeroVector);
        const TCHAR* Walk[] = {TEXT("Rifle_WalkFwdLoop"),TEXT("Rifle_StrafeRight45Loop"),TEXT("Rifle_StrafeRightLoop"),TEXT("Rifle_StrafeRight135Loop"),TEXT("Rifle_WalkBwdLoop"),TEXT("Rifle_StrafeLeft135Loop"),TEXT("Rifle_StrafeLeftLoop"),TEXT("Rifle_StrafeLeft45Loop")};
        const TCHAR* Run[] = {TEXT("Rifle_RunFwdLoop"),TEXT("Rifle_StrafeRun45RightLoop"),TEXT("Rifle_StrafeRunRightLoop"),TEXT("Rifle_StrafeRun135RightLoop"),TEXT("Rifle_RunBwdLoop"),TEXT("Rifle_StrafeRun135LeftLoop"),TEXT("Rifle_StrafeRunLeftLoop"),TEXT("Rifle_StrafeRun45LeftLoop")};
        for(int32 I=0; I<8; ++I)
        {
            const double Angle=I*PI/4.;
            for(int32 Ring=0; Ring<2; ++Ring)
            { const double Speed=Ring?300:150; Sample(Ring?Run[I]:Walk[I],FVector(Speed*FMath::Cos(Angle),Speed*FMath::Sin(Angle),0)); }
        }
    }
    BS->ValidateSampleData(); BS->ResampleData(); BS->PostEditChange(); BS->MarkPackageDirty();
    auto* Factory = NewObject<UAnimBlueprintFactory>();
    Factory->ParentClass = UAnimInstance::StaticClass(); Factory->TargetSkeleton = Skeleton;
    auto* BP = CastChecked<UAnimBlueprint>(Tools.CreateAsset(TEXT("ABP_PC_") + Label, Directory, UAnimBlueprint::StaticClass(), Factory));
    check(FBlueprintEditorUtils::AddMemberVariable(BP, TEXT("GroundSpeed"), Number(), TEXT("0")));
    auto* EventGraph = FBlueprintEditorUtils::FindEventGraph(BP);
    UK2Node_Event* Update = nullptr;
    for (UEdGraphNode* Existing : EventGraph->Nodes)
        if (auto* E = Cast<UK2Node_Event>(Existing); E && E->EventReference.GetMemberName() == TEXT("BlueprintUpdateAnimation")) Update = E;
    if (!Update)
    {
        FGraphNodeCreator<UK2Node_Event> Creator(*EventGraph);
        Update = Creator.CreateNode();
        Update->EventReference.SetExternalMember(TEXT("BlueprintUpdateAnimation"), UAnimInstance::StaticClass());
        Update->bOverrideFunction = true; Creator.Finalize();
    }
    auto* Pawn = Call(EventGraph, UAnimInstance::StaticClass(), TEXT("TryGetPawnOwner"), 150, 180);
    auto* Velocity = Call(EventGraph, AActor::StaticClass(), TEXT("GetVelocity"), 400, 180);
    auto* Length = Call(EventGraph, UKismetMathLibrary::StaticClass(), TEXT("VSizeXY"), 650, 180);
    FGraphNodeCreator<UK2Node_VariableSet> SetCreator(*EventGraph);
    auto* Set = SetCreator.CreateNode(); Set->VariableReference.SetSelfMember(TEXT("GroundSpeed"));
    Set->NodePosX = 900; SetCreator.Finalize();
    Wire(Pawn, UEdGraphSchema_K2::PN_ReturnValue, Velocity, UEdGraphSchema_K2::PN_Self);
    Wire(Velocity, UEdGraphSchema_K2::PN_ReturnValue, Length, TEXT("A"));
    Wire(Length, UEdGraphSchema_K2::PN_ReturnValue, Set, TEXT("GroundSpeed"));
    Wire(Update, UEdGraphSchema_K2::PN_Then, Set, UEdGraphSchema_K2::PN_Execute);
    if(Directional)
    {
        UK2Node_VariableSet* Previous=Set;
        const TCHAR* Vars[] = {TEXT("VelocityForward"),TEXT("VelocityRight")};
        const TCHAR* Functions[] = {TEXT("GetActorForwardVector"),TEXT("GetActorRightVector")};
        for(int32 I=0; I<2; ++I)
        {
            check(FBlueprintEditorUtils::AddMemberVariable(BP,Vars[I],Number(),TEXT("0")));
            auto* Vector=Call(EventGraph,AActor::StaticClass(),Functions[I],400,400+I*220);
            auto* Dot=Call(EventGraph,UKismetMathLibrary::StaticClass(),TEXT("Dot_VectorVector"),650,400+I*220);
            Wire(Pawn,UEdGraphSchema_K2::PN_ReturnValue,Vector,UEdGraphSchema_K2::PN_Self);
            Wire(Velocity,UEdGraphSchema_K2::PN_ReturnValue,Dot,TEXT("A"));
            Wire(Vector,UEdGraphSchema_K2::PN_ReturnValue,Dot,TEXT("B"));
            FGraphNodeCreator<UK2Node_VariableSet> Creator(*EventGraph);
            auto* Next=Creator.CreateNode(); Next->VariableReference.SetSelfMember(Vars[I]); Next->NodePosX=1200+I*300; Creator.Finalize();
            Wire(Dot,UEdGraphSchema_K2::PN_ReturnValue,Next,Vars[I]);
            Wire(Previous,UEdGraphSchema_K2::PN_Then,Next,UEdGraphSchema_K2::PN_Execute); Previous=Next;
        }
    }
    UEdGraph* AnimGraph = nullptr;
    for (UEdGraph* G : BP->FunctionGraphs) if (G->GetFName() == TEXT("AnimGraph")) AnimGraph = G;
    check(AnimGraph);
    TArray<UAnimGraphNode_Root*> Roots; AnimGraph->GetNodesOfClass(Roots); check(Roots.Num() == 1);
    FGraphNodeCreator<UAnimGraphNode_BlendSpacePlayer> PlayerCreator(*AnimGraph);
    auto* Player = PlayerCreator.CreateNode(); static_cast<FAnimNode_BlendSpacePlayerBase*>(&Player->Node)->SetBlendSpace(BS);
    Player->NodePosX = -300; PlayerCreator.Finalize();
    FGraphNodeCreator<UK2Node_VariableGet> GetCreator(*AnimGraph);
    const FName XVariable = Directional ? TEXT("VelocityForward") : TEXT("GroundSpeed");
    auto* Speed = GetCreator.CreateNode(); Speed->VariableReference.SetSelfMember(XVariable);
    Speed->NodePosX = -600; GetCreator.Finalize();
    Wire(Speed, XVariable, Player, TEXT("X"));
    if(Directional)
    {
        FGraphNodeCreator<UK2Node_VariableGet> Creator(*AnimGraph);
        auto* Side=Creator.CreateNode(); Side->VariableReference.SetSelfMember(TEXT("VelocityRight")); Side->NodePosX=-600; Side->NodePosY=160; Creator.Finalize();
        Wire(Side,TEXT("VelocityRight"),Player,TEXT("Y"));
    }
    Wire(Player, TEXT("Pose"), Roots[0], TEXT("Result"));
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
    check(Compile(BP, Diagnostics));
    return BP;
}

void CharacterDefaults(ACharacter* CDO, USkeletalMesh* Mesh, UAnimBlueprint* Anim)
{
    const auto Bounds = Mesh->GetImportedBounds();
    const double MinZ = Bounds.Origin.Z - Bounds.BoxExtent.Z;
    const double Half = FMath::Max(88., double(Bounds.BoxExtent.Z) + 2.);
    CDO->GetCapsuleComponent()->SetCapsuleSize(34, Half);
    CDO->GetMesh()->SetSkeletalMesh(Mesh);
    CDO->GetMesh()->SetAnimInstanceClass(Anim->GeneratedClass);
    CDO->GetMesh()->SetRelativeLocation(FVector(0, 0, -Half - MinZ));
    CDO->GetMesh()->SetRelativeRotation(FRotator(0, -90, 0));
    CDO->GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    CDO->GetMesh()->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    CDO->GetCharacterMovement()->MaxWalkSpeed = 300;
    CDO->GetCharacterMovement()->BrakingDecelerationWalking = 2048;
    CDO->bUseControllerRotationYaw = true;
    CDO->MarkPackageDirty();
}

void Defaults(UBlueprint* BP, USkeletalMesh* Mesh, UAnimBlueprint* Anim, bool Player)
{
    auto* CDO = CastChecked<ACharacter>(BP->GeneratedClass->GetDefaultObject());
    CharacterDefaults(CDO, Mesh, Anim);
    CDO->AutoPossessPlayer = Player ? EAutoReceiveInput::Player0 : EAutoReceiveInput::Disabled;
}
}

FString UParisBlueprintAuthoring::DescribeReferenceSkeleton(const FString& MeshPath)
{
    auto R = MakeShared<FJsonObject>();
    auto* Mesh = LoadObject<USkeletalMesh>(nullptr, *MeshPath);
    if (!Mesh) { R->SetStringField(TEXT("error"), TEXT("Mesh missing")); return ParisDraft::Json(R); }
    R->SetStringField(TEXT("mesh"), Mesh->GetPathName());
    R->SetStringField(TEXT("skeleton"), Mesh->GetSkeleton()->GetPathName());
    const auto& Ref = Mesh->GetRefSkeleton();
    const auto& Pose = Ref.GetRefBonePose();
    TArray<FTransform> Component;
    TArray<TSharedPtr<FJsonValue>> Bones;
    for (int32 I=0; I<Ref.GetNum(); ++I)
    {
        const int32 Parent = Ref.GetParentIndex(I);
        Component.Add(Parent == INDEX_NONE ? Pose[I] : Pose[I] * Component[Parent]);
        auto B = MakeShared<FJsonObject>();
        B->SetStringField(TEXT("name"), Ref.GetBoneName(I).ToString());
        B->SetNumberField(TEXT("parent"), Parent);
        auto Vector = [](const FVector& V) { TArray<TSharedPtr<FJsonValue>> A;
            for (double Value : {V.X,V.Y,V.Z}) A.Add(MakeShared<FJsonValueNumber>(Value)); return A; };
        B->SetArrayField(TEXT("local_translation_cm"), Vector(Pose[I].GetTranslation()));
        B->SetArrayField(TEXT("component_translation_cm"), Vector(Component[I].GetTranslation()));
        const int32 Index = Mesh->GetSkeleton()->GetReferenceSkeleton().FindBoneIndex(Ref.GetBoneName(I));
        B->SetNumberField(TEXT("translation_retarget_mode"), Mesh->GetSkeleton()->GetBoneTranslationRetargetingMode(Index));
        Bones.Add(MakeShared<FJsonValueObject>(B));
    }
    R->SetArrayField(TEXT("bones"), Bones);
    R->SetNumberField(TEXT("imported_bounds_min_z_cm"), Mesh->GetImportedBounds().Origin.Z - Mesh->GetImportedBounds().BoxExtent.Z);
    return ParisDraft::Json(R);
}

FString UParisBlueprintAuthoring::CompareTranslationModes(const FString& MeshPath, const FString& ClipPath)
{
    auto R = MakeShared<FJsonObject>();
    auto* Mesh = LoadObject<USkeletalMesh>(nullptr, *MeshPath);
    auto* Clip = LoadObject<UAnimSequence>(nullptr, *ClipPath);
    check(Mesh && Clip && GWorld);
    auto* Skeleton = Mesh->GetSkeleton();
    const int32 Root = Skeleton->GetReferenceSkeleton().FindBoneIndex(TEXT("root"));
    const int32 Pelvis = Skeleton->GetReferenceSkeleton().FindBoneIndex(TEXT("pelvis"));
    const auto RootMode = Skeleton->GetBoneTranslationRetargetingMode(Root);
    const auto PelvisMode = Skeleton->GetBoneTranslationRetargetingMode(Pelvis);
    auto* Actor = GWorld->SpawnActor<ASkeletalMeshActor>();
    auto* Component = Actor->GetSkeletalMeshComponent();
    Component->SetSkeletalMesh(Mesh);
    Component->SetAnimationMode(EAnimationMode::AnimationSingleNode);
    Component->SetAnimation(Clip);
    TArray<TSharedPtr<FJsonValue>> Cases;
    for (int32 Override=0; Override<2; ++Override)
    {
        Skeleton->SetBoneTranslationRetargetingMode(Root, Override ? EBoneTranslationRetargetingMode::Animation : RootMode, false);
        Skeleton->SetBoneTranslationRetargetingMode(Pelvis, Override ? EBoneTranslationRetargetingMode::Animation : PelvisMode, false);
        auto Case = MakeShared<FJsonObject>();
        Case->SetBoolField(TEXT("animation_translation_override"), Override != 0);
        TArray<TSharedPtr<FJsonValue>> Samples;
        const int32 Frames = FMath::CeilToInt(Clip->GetPlayLength()*60);
        for (int32 I=0; I<=Frames; ++I)
        {
            const float Time = FMath::Min(I/60.f, Clip->GetPlayLength()-.0001f);
            ++GFrameCounter;
            Component->SetPosition(Time, false); Component->TickAnimation(0,false); Component->RefreshBoneTransforms();
            TArray<FFinalSkinVertex> Vertices; Component->GetCPUSkinnedVertices(Vertices,0);
            double MinZ = DBL_MAX;
            for (const auto& V : Vertices) MinZ = FMath::Min(MinZ,double(V.Position.Z));
            auto S = MakeShared<FJsonObject>(); S->SetNumberField(TEXT("time_s"), Time);
            S->SetNumberField(TEXT("mesh_min_z_cm"), MinZ);
            S->SetNumberField(TEXT("pelvis_z_cm"), Component->GetBoneLocation(TEXT("pelvis")).Z);
            for (auto Bone : {FName(TEXT("foot_l")),FName(TEXT("foot_r"))})
            { const FVector P = Component->GetBoneLocation(Bone);
              TArray<TSharedPtr<FJsonValue>> V; for(double Value : {P.X,P.Y,P.Z}) V.Add(MakeShared<FJsonValueNumber>(Value));
              S->SetArrayField(Bone.ToString(),V); }
            Samples.Add(MakeShared<FJsonValueObject>(S));
        }
        Case->SetArrayField(TEXT("samples"),Samples); Cases.Add(MakeShared<FJsonValueObject>(Case));
    }
    Skeleton->SetBoneTranslationRetargetingMode(Root,RootMode,false);
    Skeleton->SetBoneTranslationRetargetingMode(Pelvis,PelvisMode,false);
    Actor->Destroy();
    R->SetStringField(TEXT("mesh"),MeshPath); R->SetStringField(TEXT("clip"),ClipPath);
    R->SetArrayField(TEXT("cases"),Cases); R->SetBoolField(TEXT("original_modes_restored"),true);
    return ParisDraft::Json(R);
}

FString UParisBlueprintAuthoring::CreateGermanTranslationDraft()
{
    const FString Dir = TEXT("/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1");
    auto R = MakeShared<FJsonObject>();
    const TCHAR* Names[] = {TEXT("SKEL_PC_German_Translation_v1"), TEXT("SK_PC_German_A_Translation_v1"),TEXT("SK_PC_German_B_Translation_v1")};
    for(auto Name : Names) if(FPackageName::DoesPackageExist(Dir/Name))
    { R->SetStringField(TEXT("error"),TEXT("Refusing existing adaptation")); return ParisDraft::Json(R); }
    auto& Tools = FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools")).Get();
    auto* Source = LoadObject<USkeletalMesh>(nullptr, *(ParisDraft::MeshDir+TEXT("SK_WWII_GermanSoldier_varA_UE582_v1")));
    check(Source);
    auto* Skeleton = CastChecked<USkeleton>(Tools.DuplicateAsset(Names[0],Dir,Source->GetSkeleton()));
    for(auto Bone : {FName(TEXT("root")),FName(TEXT("pelvis"))})
        Skeleton->SetBoneTranslationRetargetingMode(Skeleton->GetReferenceSkeleton().FindBoneIndex(Bone),EBoneTranslationRetargetingMode::Animation,false);
    Skeleton->MarkPackageDirty();
    TArray<TSharedPtr<FJsonValue>> Assets; Assets.Add(MakeShared<FJsonValueString>(Skeleton->GetPathName()));
    for(int32 I=0; I<2; ++I)
    {
        auto* Original = LoadObject<USkeletalMesh>(nullptr, *(ParisDraft::MeshDir+(I==0?TEXT("SK_WWII_GermanSoldier_varA_UE582_v1"):TEXT("SK_WWII_GermanSoldier_varB_UE582_v1"))));
        auto* Mesh = CastChecked<USkeletalMesh>(Tools.DuplicateAsset(Names[I+1],Dir,Original));
        Mesh->SetSkeleton(Skeleton); Mesh->MarkPackageDirty();
        Assets.Add(MakeShared<FJsonValueString>(Mesh->GetPathName()));
    }
    R->SetArrayField(TEXT("assets"),Assets); R->SetStringField(TEXT("result"),TEXT("created_unsaved_translation_adaptation"));
    return ParisDraft::Json(R);
}

FString UParisBlueprintAuthoring::CreateDirectionalDraft()
{
    auto R=MakeShared<FJsonObject>(); TArray<TSharedPtr<FJsonValue>> Diagnostics,Assets;
    const FString Dir=TEXT("/Game/ParisCombat/Animation/DirectionalDraft");
    for(auto Name : {TEXT("BS_PC_Allied"),TEXT("BS_PC_German"),TEXT("ABP_PC_Allied"),TEXT("ABP_PC_German")})
        if(FPackageName::DoesPackageExist(Dir/Name)) { R->SetStringField(TEXT("error"),TEXT("Refusing existing directional draft")); return ParisDraft::Json(R); }
    auto* Allied=LoadObject<USkeletalMesh>(nullptr,*(ParisDraft::MeshDir+TEXT("SK_WWII_US_Paratrooper_simple_UE582_v1")));
    auto* German=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1/SK_PC_German_A_Translation_v1"));
    check(Allied && German);
    for(int32 I=0; I<2; ++I)
    {
        const FString Label=I?TEXT("German"):TEXT("Allied");
        auto* BP=ParisDraft::Animation((I?German:Allied)->GetSkeleton(),Label,Diagnostics,true);
        Assets.Add(MakeShared<FJsonValueString>(BP->GetPathName())); Assets.Add(MakeShared<FJsonValueString>(Dir/TEXT("BS_PC_")+Label));
    }
    R->SetArrayField(TEXT("assets"),Assets); R->SetArrayField(TEXT("compiler_messages"),Diagnostics); return ParisDraft::Json(R);
}

FString UParisBlueprintAuthoring::CreateLifecycleDraft()
{
    using namespace ParisDraft;
    auto R=MakeShared<FJsonObject>(); TArray<TSharedPtr<FJsonValue>> Diagnostics,Assets;
    const FString Dir=BPDir/TEXT("LifecycleDraft");
    const TCHAR* Names[]={TEXT("BP_PCCombatantV2"),TEXT("BP_PCPlayerV2"),TEXT("BP_PCNPCV2")};
    for(auto Name:Names) if(FPackageName::DoesPackageExist(Dir/Name))
    {R->SetStringField(TEXT("error"),TEXT("Refusing existing lifecycle draft")); return Json(R);}
    auto Create=[&](FName Name,UClass* Parent)
    {return FKismetEditorUtilities::CreateBlueprint(Parent,CreatePackage(*(Dir/Name.ToString())),Name,BPTYPE_Normal,UBlueprint::StaticClass(),UBlueprintGeneratedClass::StaticClass());};
    auto* Parent=LoadClass<ACharacter>(nullptr,*(BPDir/TEXT("BP_PCCombatantBase.BP_PCCombatantBase_C"))); check(Parent);
    auto* Base=Create(Names[0],Parent);
    FEdGraphPinType Boolean; Boolean.PinCategory=UEdGraphSchema_K2::PC_Boolean;
    FEdGraphPinType Integer; Integer.PinCategory=UEdGraphSchema_K2::PC_Int;
    FEdGraphPinType Name; Name.PinCategory=UEdGraphSchema_K2::PC_Name;
    FBlueprintEditorUtils::AddMemberVariable(Base,TEXT("MaxHealth"),Number(),TEXT("100"));
    FBlueprintEditorUtils::AddMemberVariable(Base,TEXT("Health"),Number(),TEXT("100"));
    FBlueprintEditorUtils::AddMemberVariable(Base,TEXT("IsDead"),Boolean,TEXT("false"));
    FBlueprintEditorUtils::AddMemberVariable(Base,TEXT("RestoreGeneration"),Integer,TEXT("0"));
    FBlueprintEditorUtils::AddMemberVariable(Base,TEXT("ActionID"),Integer,TEXT("0"));
    FBlueprintEditorUtils::AddMemberVariable(Base,TEXT("ActionState"),Name,TEXT("Ready"));
    LifecycleFunctions(Base,Diagnostics);
    auto* Allied=LoadObject<USkeletalMesh>(nullptr,*(MeshDir+TEXT("SK_WWII_US_Paratrooper_simple_UE582_v1")));
    auto* German=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/ParisCombat/Animation/RetargetDraft/GermanTranslationV1/SK_PC_German_A_Translation_v1"));
    auto* AlliedAnim=LoadObject<UAnimBlueprint>(nullptr,TEXT("/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_Allied"));
    auto* GermanAnim=LoadObject<UAnimBlueprint>(nullptr,TEXT("/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_German"));
    check(Allied && German && AlliedAnim && GermanAnim); Defaults(Base,Allied,AlliedAnim,false);
    auto* Player=Create(Names[1],Base->GeneratedClass);
    const TCHAR* Axes[]={TEXT("PC_MoveForward"),TEXT("PC_MoveRight"),TEXT("PC_LookYaw"),TEXT("PC_LookPitch")};
    const TCHAR* Funcs[]={TEXT("PC_RequestMoveForward"),TEXT("PC_RequestMoveRight"),TEXT("PC_RequestLookYaw"),TEXT("PC_RequestLookPitch")};
    for(int32 I=0;I<4;++I) InputEvent(Player,Axes[I],Funcs[I],I*300);
    auto* ArmNode=Player->SimpleConstructionScript->CreateNode(USpringArmComponent::StaticClass(),TEXT("DiagnosticCameraArm"));
    Player->SimpleConstructionScript->AddNode(ArmNode);
    auto* Arm=CastChecked<USpringArmComponent>(ArmNode->ComponentTemplate);
    Arm->TargetArmLength=300; Arm->bUsePawnControlRotation=true; Arm->SetRelativeLocation(FVector(0,0,55));
    auto* Cam=Player->SimpleConstructionScript->CreateNode(UCameraComponent::StaticClass(),TEXT("DiagnosticCamera"));
    ArmNode->AddChildNode(Cam); Cam->AttachToName=USpringArmComponent::SocketName;
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Player); check(Compile(Player,Diagnostics)); Defaults(Player,Allied,AlliedAnim,true);
    auto* NPC=Create(Names[2],Base->GeneratedClass); check(Compile(NPC,Diagnostics)); Defaults(NPC,German,GermanAnim,false);
    for(auto NameValue:Names) Assets.Add(MakeShared<FJsonValueString>(Dir/NameValue));
    R->SetArrayField(TEXT("assets"),Assets); R->SetArrayField(TEXT("compiler_messages"),Diagnostics); return Json(R);
}

FString UParisBlueprintAuthoring::CreateStrideDraft()
{
    auto R=MakeShared<FJsonObject>(); TArray<TSharedPtr<FJsonValue>> Assets,Settings,Diagnostics;
    const FString Dir=TEXT("/Game/ParisCombat/Animation/DirectionalDraft");
    for(auto Label : {TEXT("Allied"),TEXT("German")})
        for(auto Prefix : {TEXT("BS_PC_"),TEXT("ABP_PC_")})
            if(FPackageName::DoesPackageExist(Dir/(FString(Prefix)+Label+TEXT("_Stride_v1"))))
            {R->SetStringField(TEXT("error"),TEXT("Refusing existing stride draft"));return ParisDraft::Json(R);}
    auto& Tools=FModuleManager::LoadModuleChecked<FAssetToolsModule>(TEXT("AssetTools")).Get();
    for(auto Label : {TEXT("Allied"),TEXT("German")})
    {
        auto* Original=LoadObject<UBlendSpace>(nullptr,*(Dir/(FString(TEXT("BS_PC_"))+Label))); check(Original);
        auto* BS=CastChecked<UBlendSpace>(Tools.DuplicateAsset(FString(TEXT("BS_PC_"))+Label+TEXT("_Stride_v1"),Dir,Original));
        for(int32 I=0;I<BS->GetNumberOfBlendSamples();++I)
        {
            auto& Sample=const_cast<FBlendSample&>(BS->GetBlendSample(I));
            const double Speed=Sample.SampleValue.Size2D(); if(Speed<1)continue;
            auto* Native=LoadObject<UAnimSequence>(nullptr,*(FString(TEXT("/Game/RifleAnimsetPro/Animations/RootMotion/"))+Sample.Animation->GetName()));
            check(Native && !Sample.Animation->bEnableRootMotion && Sample.Animation->AdditiveAnimType==AAT_None);
            check(FMath::IsNearlyEqual(Native->GetPlayLength(),Sample.Animation->GetPlayLength(),.001f));
            const FVector Delta=Native->ExtractRootMotionFromRange(0,Native->GetPlayLength(),FAnimExtractContext(0.,true)).GetTranslation();
            const double NativeSpeed=Delta.Size2D()/Native->GetPlayLength()*Sample.Animation->RateScale; check(NativeSpeed>50);
            Sample.RateScale=Speed/NativeSpeed; check(Sample.RateScale>.25 && Sample.RateScale<2);
            auto S=MakeShared<FJsonObject>(); S->SetStringField(TEXT("faction"),Label);
            S->SetStringField(TEXT("clip"),Sample.Animation->GetPathName()); S->SetNumberField(TEXT("source_speed_cm_s"),NativeSpeed);
            S->SetNumberField(TEXT("sample_speed_cm_s"),Speed); S->SetNumberField(TEXT("sample_rate_scale"),Sample.RateScale);
            Settings.Add(MakeShared<FJsonValueObject>(S));
        }
        BS->ValidateSampleData();BS->ResampleData();BS->PostEditChange();BS->MarkPackageDirty();
        auto* Previous=LoadObject<UAnimBlueprint>(nullptr,*(Dir/(FString(TEXT("ABP_PC_"))+Label)));check(Previous);
        auto* BP=CastChecked<UAnimBlueprint>(Tools.DuplicateAsset(FString(TEXT("ABP_PC_"))+Label+TEXT("_Stride_v1"),Dir,Previous));
        int32 Changed=0;
        for(UEdGraph* G:BP->FunctionGraphs)for(UEdGraphNode* N:G->Nodes)
            if(auto* Player=Cast<UAnimGraphNode_BlendSpacePlayer>(N))
            {static_cast<FAnimNode_BlendSpacePlayerBase*>(&Player->Node)->SetBlendSpace(BS);++Changed;}
        check(Changed==1);FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);check(ParisDraft::Compile(BP,Diagnostics));
        Assets.Add(MakeShared<FJsonValueString>(BS->GetPathName()));Assets.Add(MakeShared<FJsonValueString>(BP->GetPathName()));
    }
    R->SetArrayField(TEXT("assets"),Assets);R->SetArrayField(TEXT("sample_settings"),Settings);R->SetArrayField(TEXT("compiler_messages"),Diagnostics);
    return ParisDraft::Json(R);
}

FString UParisBlueprintAuthoring::ProbeLifecycle(const FString& ClassPath,const FString& AnimationPath)
{
    auto R=MakeShared<FJsonObject>(); R->SetStringField(TEXT("class"),ClassPath);
    auto* Class=LoadClass<ACharacter>(nullptr,*ClassPath); check(Class);
    const auto IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(true).SetTransactional(false);
    auto* W=UWorld::CreateWorld(EWorldType::Game,false,TEXT("ParisLifecycleProbe"),nullptr,true,ERHIFeatureLevel::Num,&IV);
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
    struct Guard {UWorld* Old; explicit Guard(UWorld* Current):Old(GWorld){GWorld=Current;} ~Guard(){GWorld=Old;}} WorldGuard(W);
    auto* Floor=W->SpawnActor<AStaticMeshActor>(FVector(0,0,-5),FRotator::ZeroRotator);
    Floor->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube")));
    Floor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll")); Floor->SetActorScale3D(FVector(100,100,.1));
    auto* C=W->SpawnActor<ACharacter>(Class,FVector(0,0,120),FRotator::ZeroRotator);
    if(!AnimationPath.IsEmpty())
    {auto* BP=LoadObject<UAnimBlueprint>(nullptr,*AnimationPath);check(BP && BP->GeneratedClass);C->GetMesh()->SetAnimInstanceClass(BP->GeneratedClass);R->SetStringField(TEXT("override_animation"),AnimationPath);}
    auto* PC=W->SpawnActor<APlayerController>(); PC->SetAsLocalPlayerController(); PC->Possess(C);
    W->InitializeActorsForPlay(FURL()); W->BeginPlay(); W->SetBegunPlay(true);
    for(TActorIterator<AActor> I(W);I;++I) if(!I->HasActorBegunPlay()) I->DispatchBeginPlay();
    auto Invoke=[&](FName Name,const TCHAR* Parameter=nullptr,double Amount=0)
    {auto* F=C->FindFunction(Name);check(F);FStructOnScope P(F);if(Parameter)ParisDraft::Property<FDoubleProperty>(F,Parameter)->SetPropertyValue_InContainer(P.GetStructMemory(),Amount);C->ProcessEvent(F,P.GetStructMemory());};
    auto Tick=[&](int32 Frames,bool Move=false){for(int32 I=0;I<Frames;++I){if(Move)Invoke(TEXT("PC_RequestMoveForward"),TEXT("AxisValue"),1);++GFrameCounter;W->Tick(LEVELTICK_All,1.f/60);}};
    auto Health=[&](){return ParisDraft::Property<FDoubleProperty>(Class,TEXT("Health"))->GetPropertyValue_InContainer(C);};
    auto Dead=[&](){return ParisDraft::Property<FBoolProperty>(Class,TEXT("IsDead"))->GetPropertyValue_InContainer(C);};
    auto Int=[&](FName Name){return ParisDraft::Property<FIntProperty>(Class,Name)->GetPropertyValue_InContainer(C);};
    TArray<TSharedPtr<FJsonValue>> Cases;
    Tick(60);
    for(int32 Cycle=0;Cycle<3;++Cycle)
    {
        auto P=MakeShared<FJsonObject>(); P->SetNumberField(TEXT("cycle"),Cycle+1);
        Invoke(TEXT("PC_ApplyDamage"),TEXT("Amount"),25); P->SetBoolField(TEXT("damage_25_leaves_75"),Health()==75 && !Dead());
        Invoke(TEXT("PC_ApplyDamage"),TEXT("Amount"),-50); Invoke(TEXT("PC_ApplyDamage"),TEXT("Amount"),0);
        P->SetBoolField(TEXT("nonpositive_damage_ignored"),Health()==75 && !Dead());
        Invoke(TEXT("PC_ApplyDamage"),TEXT("Amount"),std::numeric_limits<double>::infinity());
        Invoke(TEXT("PC_ApplyDamage"),TEXT("Amount"),std::numeric_limits<double>::quiet_NaN());
        P->SetBoolField(TEXT("nonfinite_damage_ignored"),Health()==75 && !Dead());
        Invoke(TEXT("PC_ApplyDamage"),TEXT("Amount"),200); const int32 DeathAction=Int(TEXT("ActionID"));
        P->SetBoolField(TEXT("death_clamped_once"),Health()==0 && Dead() && DeathAction==Cycle*2+1);
        Invoke(TEXT("PC_ApplyDamage"),TEXT("Amount"),100); Invoke(TEXT("PC_Die"));
        P->SetBoolField(TEXT("repeat_death_ignored"),Int(TEXT("ActionID"))==DeathAction && Health()==0);
        const FVector Before=C->GetActorLocation(); Tick(180,true);
        P->SetBoolField(TEXT("dead_movement_disabled"),C->GetActorLocation().Equals(Before,.01) && C->GetCharacterMovement()->MovementMode==MOVE_None);
        auto* Single=C->GetMesh()->GetSingleNodeInstance();
        P->SetNumberField(TEXT("death_clip_time_s"),Single?Single->GetCurrentTime():-1);
        P->SetBoolField(TEXT("death_clip_advances"),Single && Single->GetCurrentTime()>2.9);
        P->SetBoolField(TEXT("dead_capsule_not_obstructing"),C->GetCapsuleComponent()->GetCollisionEnabled()==ECollisionEnabled::NoCollision);
        Invoke(TEXT("PC_ResetLifecycle")); C->SetActorLocation(FVector(0,0,120),false,nullptr,ETeleportType::TeleportPhysics);
        Tick(60); const FVector Start=C->GetActorLocation(); Tick(60,true);
        P->SetBoolField(TEXT("reset_health_generation"),Health()==100 && !Dead() && Int(TEXT("RestoreGeneration"))==Cycle+1 && Int(TEXT("ActionID"))==DeathAction+1);
        P->SetNumberField(TEXT("restored_move_dx_cm"),C->GetActorLocation().X-Start.X);
        P->SetBoolField(TEXT("restored_movement"),C->GetActorLocation().X-Start.X>250 && C->GetCharacterMovement()->IsMovingOnGround());
        auto* Anim=C->GetMesh()->GetAnimInstance();
        P->SetStringField(TEXT("restored_anim_class"),Anim?Anim->GetClass()->GetPathName():TEXT("None"));
        P->SetBoolField(TEXT("restored_anim_blueprint"),Anim && Anim->GetClass()->GetPathName().Contains(TEXT("/DirectionalDraft/ABP_PC_")));
        P->SetBoolField(TEXT("restored_capsule_collision"),C->GetCapsuleComponent()->GetCollisionEnabled()==ECollisionEnabled::QueryAndPhysics);
        Cases.Add(MakeShared<FJsonValueObject>(P));
    }
    R->SetArrayField(TEXT("cycles"),Cases);
    W->EndPlay(EEndPlayReason::Quit);GEngine->DestroyWorldContext(W);W->DestroyWorld(false);
    return ParisDraft::Json(R);
}

FString UParisBlueprintAuthoring::CreateMovementDraft()
{
    using namespace ParisDraft;
    auto Report = MakeShared<FJsonObject>();
    TArray<TSharedPtr<FJsonValue>> Diagnostics;
    const FString Paths[] = { BPDir / TEXT("BP_PCCombatantBase"), BPDir / TEXT("BP_PCPlayer"), BPDir / TEXT("BP_PCNPC"),
        AnimDir / TEXT("BS_PC_Allied"), AnimDir / TEXT("BS_PC_German"), AnimDir / TEXT("ABP_PC_Allied"), AnimDir / TEXT("ABP_PC_German") };
    for (const auto& P : Paths) if (FPackageName::DoesPackageExist(P))
    { Report->SetStringField(TEXT("error"), TEXT("Refusing existing package: ") + P); return Json(Report); }
    auto* Allied = LoadObject<USkeletalMesh>(nullptr, *(MeshDir + TEXT("SK_WWII_US_Paratrooper_simple_UE582_v1")));
    auto* German = LoadObject<USkeletalMesh>(nullptr, *(MeshDir + TEXT("SK_WWII_GermanSoldier_varA_UE582_v1")));
    check(Allied && German);
    auto* AlliedAnim = Animation(Allied->GetSkeleton(), TEXT("Allied"), Diagnostics);
    auto* GermanAnim = Animation(German->GetSkeleton(), TEXT("German"), Diagnostics);
    auto NewBP = [](const FString& Path, UClass* Parent)
    {
        auto* Package = CreatePackage(*Path);
        return FKismetEditorUtilities::CreateBlueprint(Parent, Package, FName(*FPackageName::GetLongPackageAssetName(Path)), BPTYPE_Normal,
            UBlueprint::StaticClass(), UBlueprintGeneratedClass::StaticClass());
    };
    auto* Base = NewBP(Paths[0], ACharacter::StaticClass());
    FEdGraphPinType Integer; Integer.PinCategory = UEdGraphSchema_K2::PC_Int;
    FEdGraphPinType Name; Name.PinCategory = UEdGraphSchema_K2::PC_Name;
    FBlueprintEditorUtils::AddMemberVariable(Base, TEXT("TeamId"), Integer, TEXT("0"));
    FBlueprintEditorUtils::AddMemberVariable(Base, TEXT("RoleId"), Name, TEXT("Diagnostic"));
    FBlueprintEditorUtils::SetBlueprintOnlyEditableFlag(Base, TEXT("TeamId"), false);
    FBlueprintEditorUtils::SetBlueprintOnlyEditableFlag(Base, TEXT("RoleId"), false);
    MoveFunction(Base, TEXT("PC_RequestMoveForward"), TEXT("AddMovementInput"), TEXT("GetActorForwardVector"));
    MoveFunction(Base, TEXT("PC_RequestMoveRight"), TEXT("AddMovementInput"), TEXT("GetActorRightVector"));
    MoveFunction(Base, TEXT("PC_RequestLookYaw"), TEXT("AddControllerYawInput"), NAME_None);
    MoveFunction(Base, TEXT("PC_RequestLookPitch"), TEXT("AddControllerPitchInput"), NAME_None);
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Base); check(Compile(Base, Diagnostics));
    const TCHAR* Axes[] = { TEXT("PC_MoveForward"), TEXT("PC_MoveRight"), TEXT("PC_LookYaw"), TEXT("PC_LookPitch") };
    const TCHAR* Functions[] = { TEXT("PC_RequestMoveForward"), TEXT("PC_RequestMoveRight"), TEXT("PC_RequestLookYaw"), TEXT("PC_RequestLookPitch") };
    auto* Player = NewBP(Paths[1], Base->GeneratedClass);
    for (int32 I=0; I<4; ++I) InputEvent(Player, Axes[I], Functions[I], I*300);
    auto* ArmNode = Player->SimpleConstructionScript->CreateNode(USpringArmComponent::StaticClass(), TEXT("DiagnosticCameraArm"));
    Player->SimpleConstructionScript->AddNode(ArmNode);
    auto* Arm = CastChecked<USpringArmComponent>(ArmNode->ComponentTemplate);
    Arm->TargetArmLength = 300; Arm->bUsePawnControlRotation = true; Arm->SetRelativeLocation(FVector(0,0,55));
    auto* CamNode = Player->SimpleConstructionScript->CreateNode(UCameraComponent::StaticClass(), TEXT("DiagnosticCamera"));
    ArmNode->AddChildNode(CamNode); CamNode->AttachToName = USpringArmComponent::SocketName;
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Player); check(Compile(Player, Diagnostics));
    Defaults(Player, Allied, AlliedAnim, true);
    auto* NPC = NewBP(Paths[2], Base->GeneratedClass); check(Compile(NPC, Diagnostics)); Defaults(NPC, German, GermanAnim, false);
    TArray<TSharedPtr<FJsonValue>> Assets;
    for (const auto& P : Paths) Assets.Add(MakeShared<FJsonValueString>(P));
    Report->SetArrayField(TEXT("assets"), Assets); Report->SetArrayField(TEXT("compiler_messages"), Diagnostics);
    Report->SetStringField(TEXT("result"), TEXT("created_unsaved_drafts")); return Json(Report);
}

FString UParisBlueprintAuthoring::ConfigureDraftCharacter(ACharacter* Character, USkeletalMesh* Mesh, UAnimBlueprint* Animation)
{
    auto R = MakeShared<FJsonObject>();
    if (!Character || !Mesh || !Animation || !Animation->GeneratedClass)
    { R->SetStringField(TEXT("error"), TEXT("Invalid draft character configuration")); return ParisDraft::Json(R); }
    ParisDraft::CharacterDefaults(Character, Mesh, Animation);
    R->SetNumberField(TEXT("capsule_half_height_cm"), Character->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight());
    R->SetNumberField(TEXT("mesh_z_offset_cm"), Character->GetMesh()->GetRelativeLocation().Z);
    return ParisDraft::Json(R);
}

FString UParisBlueprintAuthoring::ProbeMovement(const FString& ClassPath, int32 FPS, const FString& MeshPath, const FString& AnimPath)
{
    auto Report = MakeShared<FJsonObject>();
    Report->SetStringField(TEXT("class"), ClassPath); Report->SetNumberField(TEXT("fps"), FPS);
    auto* Class = LoadClass<ACharacter>(nullptr, *ClassPath);
    if (!Class || (FPS != 30 && FPS != 60 && FPS != 120))
    { Report->SetStringField(TEXT("error"), TEXT("Invalid Character class or diagnostic step")); return ParisDraft::Json(Report); }
    const auto IVS = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true)
        .RequiresHitProxies(false).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(true).SetTransactional(false);
    UWorld* World = UWorld::CreateWorld(EWorldType::Game, false, TEXT("ParisMovementProbe"), nullptr, true, ERHIFeatureLevel::Num, &IVS);
    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
    struct FWorldGuard
    {
        UWorld* Previous;
        explicit FWorldGuard(UWorld* Current) : Previous(GWorld) { GWorld = Current; }
        ~FWorldGuard() { GWorld = Previous; }
    } Guard(World);
    auto* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube"));
    auto Block = [&](FVector Pos, FVector Scale)
    {
        auto* A = World->SpawnActor<AStaticMeshActor>(Pos, FRotator::ZeroRotator);
        A->GetStaticMeshComponent()->SetStaticMesh(Cube);
        A->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
        A->SetActorScale3D(Scale); return A;
    };
    Block(FVector(0,0,-5), FVector(100,100,.1));
    Block(FVector(1100,0,150), FVector(1,20,3));
    auto* Character = World->SpawnActor<ACharacter>(Class, FVector(0,0,120), FRotator::ZeroRotator);
    if (!MeshPath.IsEmpty())
    {
        auto* Mesh = LoadObject<USkeletalMesh>(nullptr, *MeshPath);
        auto* Anim = LoadObject<UAnimBlueprint>(nullptr, *AnimPath);
        check(Mesh && Anim); ParisDraft::CharacterDefaults(Character, Mesh, Anim);
        Report->SetStringField(TEXT("mesh"), MeshPath); Report->SetStringField(TEXT("animation_blueprint"), AnimPath);
    }
    auto* Controller = World->SpawnActor<APlayerController>();
    // No GameMode/ULocalPlayer exists in this bounded harness. Mirror the local
    // controller designation normally performed by GameMode; do not bypass
    // collision or CharacterMovement and do not claim device-input validation.
    Controller->SetAsLocalPlayerController(); Controller->Possess(Character);
    Report->SetBoolField(TEXT("diagnostic_local_controller"), Controller->IsLocalController());
    ASceneCapture2D* Camera = nullptr;
    UTextureRenderTarget2D* Target = nullptr;
    TArray<TSharedPtr<FJsonValue>> Captures;
    const bool Extended = AnimPath.Contains(TEXT("/DirectionalDraft/"));
    FString Identity=Extended?TEXT("v4"):TEXT("v3");
    FParse::Value(FCommandLine::Get(),TEXT("ParisProbeIdentity="),Identity);
    for(TCHAR C:Identity) checkf(FChar::IsAlnum(C)||C==TEXT('_'),TEXT("Invalid evidence identity"));
    const FString Evidence = FPaths::ConvertRelativePathToFull(FPaths::ProjectDir() / (TEXT("../../Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/Movement/Captures_")+Identity));
    if(Extended)
    {
        // Keep this DIAGNOSTIC component in CPU-skinning mode. Toggling
        // GetCPUSkinnedVertices from GPU->CPU->GPU every sample recreates render
        // resources thousands of times in one outer commandlet frame.
        Character->GetMesh()->SetForcedLOD(1);
        Character->GetMesh()->SetCPUSkinningEnabled(true,true);
        Report->SetStringField(TEXT("geometry_sampler"),TEXT("CPU skinning diagnostic, refreshed end-of-frame data; not runtime rendering performance"));
    }
    if (FPS == 60 && !GUsingNullRHI)
    {
        IFileManager::Get().MakeDirectory(*Evidence, true);
        for (auto Rotation : {FRotator(-35,-135,0), FRotator(-20,45,0)})
        {
            auto* Light = World->SpawnActor<ADirectionalLight>(FVector(0,0,400), Rotation);
            auto* Component = CastChecked<UDirectionalLightComponent>(Light->GetLightComponent());
            Component->SetIntensity(10); Component->SetCastShadows(false);
        }
        Camera = World->SpawnActor<ASceneCapture2D>();
        Target = NewObject<UTextureRenderTarget2D>(); Target->RenderTargetFormat = RTF_RGBA8; Target->InitAutoFormat(1000, 1000);
        auto* Capture = Camera->GetCaptureComponent2D(); Capture->TextureTarget = Target;
        Capture->CaptureSource = SCS_FinalColorLDR; Capture->bCaptureEveryFrame = false; Capture->bCaptureOnMovement = false; Capture->FOVAngle = 30;
    }
    World->InitializeActorsForPlay(FURL()); World->BeginPlay();
    // This explicit bounded world has no GameMode. Dispatch normal actor BeginPlay,
    // but do not call it PIE, input-device or packaged-runtime acceptance.
    World->SetBegunPlay(true);
    for (TActorIterator<AActor> It(World); It; ++It) if (!It->HasActorBegunPlay()) It->DispatchBeginPlay();
    UFunction* Forward = Character->FindFunction(TEXT("PC_RequestMoveForward"));
    UFunction* Right = Character->FindFunction(TEXT("PC_RequestMoveRight"));
    check(Forward && Right);
    auto Request = [&](UFunction* Function, double Value)
    {
        FStructOnScope Parameters(Function);
        auto* Property = FindFProperty<FDoubleProperty>(Function, TEXT("AxisValue")); check(Property);
        Property->SetPropertyValue_InContainer(Parameters.GetStructMemory(), Value);
        Character->ProcessEvent(Function, Parameters.GetStructMemory());
    };
    TArray<TSharedPtr<FJsonValue>> Phases;
    auto Phase = [&](const TCHAR* Name, double Seconds, double Fwd, double Side)
    {
        auto P = MakeShared<FJsonObject>(); const FVector Start = Character->GetActorLocation();
        double MinGap = DBL_MAX, MaxGap = -DBL_MAX, MaxPending = 0;
        TArray<TSharedPtr<FJsonValue>> PoseSamples;
        for (int32 I=0; I<FMath::RoundToInt(Seconds * FPS); ++I)
        {
            Request(Forward, Fwd); Request(Right, Side);
            MaxPending = FMath::Max(MaxPending, Character->GetPendingMovementInputVector().Size());
            // A Python commandlet loop is one outer engine frame. The normal
            // engine loop advances this counter; TickTaskManager and skeletal
            // pose ticks suppress repeated work if we leave it unchanged.
            ++GFrameCounter;
            World->Tick(LEVELTICK_All, 1.f/FPS);
            const double Gap = Character->GetActorLocation().Z - Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
            MinGap = FMath::Min(MinGap, Gap); MaxGap = FMath::Max(MaxGap, Gap);
            if (Extended)
            {
                auto S=MakeShared<FJsonObject>(); auto* M=Character->GetMesh(); M->RefreshBoneTransforms();
                M->MarkRenderDynamicDataDirty(); World->SendAllEndOfFrameUpdates(); FlushRenderingCommands();
                TArray<FFinalSkinVertex> Vertices; M->GetCPUSkinnedCachedFinalVertices(Vertices); check(Vertices.Num()>0); double MinZ=DBL_MAX;
                for(const auto& V : Vertices) MinZ=FMath::Min(MinZ,M->GetComponentTransform().TransformPosition(FVector(V.Position)).Z);
                S->SetNumberField(TEXT("t"),(I+1.)/FPS); S->SetNumberField(TEXT("min_z_cm"),MinZ);
                S->SetNumberField(TEXT("speed_cm_s"),Character->GetVelocity().Size2D());
                for(auto Bone : {FName(TEXT("foot_l")),FName(TEXT("foot_r")),FName(TEXT("ball_l")),FName(TEXT("ball_r"))})
                { const FVector V=M->GetBoneLocation(Bone); TArray<TSharedPtr<FJsonValue>> A;
                  for(double Value : {V.X,V.Y,V.Z}) A.Add(MakeShared<FJsonValueNumber>(Value)); S->SetArrayField(Bone.ToString(),A); }
                PoseSamples.Add(MakeShared<FJsonValueObject>(S));
            }
        }
        const FVector End = Character->GetActorLocation();
        P->SetStringField(TEXT("phase"), Name); P->SetNumberField(TEXT("dx_cm"), End.X-Start.X); P->SetNumberField(TEXT("dy_cm"), End.Y-Start.Y);
        P->SetNumberField(TEXT("end_x_cm"), End.X); P->SetNumberField(TEXT("end_y_cm"), End.Y);
        P->SetNumberField(TEXT("end_speed_cm_s"), Character->GetVelocity().Size2D());
        P->SetNumberField(TEXT("capsule_floor_gap_min_cm"), MinGap); P->SetNumberField(TEXT("capsule_floor_gap_max_cm"), MaxGap);
        P->SetBoolField(TEXT("moving_on_ground"), Character->GetCharacterMovement()->IsMovingOnGround());
        P->SetNumberField(TEXT("max_pending_input_magnitude"), MaxPending);
        auto* Mesh = Character->GetMesh(); Mesh->RefreshBoneTransforms();
        P->SetNumberField(TEXT("foot_l_world_z_cm"), Mesh->GetBoneLocation(TEXT("foot_l")).Z);
        P->SetNumberField(TEXT("foot_r_world_z_cm"), Mesh->GetBoneLocation(TEXT("foot_r")).Z);
        TArray<FFinalSkinVertex> Vertices; Mesh->GetCPUSkinnedVertices(Vertices, 0);
        double MinVertex = DBL_MAX;
        for (const auto& V : Vertices) MinVertex = FMath::Min(MinVertex, Mesh->GetComponentTransform().TransformPosition(FVector(V.Position)).Z);
        P->SetNumberField(TEXT("geometry_min_world_z_cm"), MinVertex); P->SetNumberField(TEXT("skinned_vertices"), Vertices.Num());
        if (auto* Anim = Mesh->GetAnimInstance())
        {
            if (auto* Speed = FindFProperty<FDoubleProperty>(Anim->GetClass(), TEXT("GroundSpeed"))) P->SetNumberField(TEXT("anim_ground_speed_cm_s"), Speed->GetPropertyValue_InContainer(Anim));
            for(auto Variable : {FName(TEXT("VelocityForward")),FName(TEXT("VelocityRight"))})
                if(auto* Value=FindFProperty<FDoubleProperty>(Anim->GetClass(),Variable)) P->SetNumberField(Variable.ToString(),Value->GetPropertyValue_InContainer(Anim));
        }
        P->SetArrayField(TEXT("pose_samples"),PoseSamples);
        if (Camera && ((Extended && FString(Name)!=TEXT("run_to_wall") && FString(Name)!=TEXT("wall_stop")) || FString(Name) == TEXT("settle") || FString(Name) == TEXT("walk_forward") || FString(Name) == TEXT("walk_right")))
        {
            const FVector Aim(End.X, End.Y, 88);
            for (int32 View=0; View<2; ++View)
            {
                const FVector At = Aim + (View == 0 ? FVector(420,0,20) : FVector(0,420,20));
                Camera->SetActorLocation(At); Camera->SetActorRotation((Aim-At).Rotation());
                Camera->GetCaptureComponent2D()->CaptureScene(); FlushRenderingCommands();
                const FString Filename = Mesh->GetSkinnedAsset()->GetName() + TEXT("_") + Name + (View == 0 ? TEXT("_front.png") : TEXT("_side.png"));
                checkf(!IFileManager::Get().FileExists(*(Evidence / Filename)), TEXT("Refusing existing capture; use a new probe identity"));
                UKismetRenderingLibrary::ExportRenderTarget(World, Target, Evidence, Filename);
                auto Image = MakeShared<FJsonObject>(); Image->SetStringField(TEXT("file"), Filename);
                Image->SetStringField(TEXT("directory"), Evidence);
                Image->SetBoolField(TEXT("exists"), IFileManager::Get().FileExists(*(Evidence / Filename)));
                Captures.Add(MakeShared<FJsonValueObject>(Image));
            }
        }
        Phases.Add(MakeShared<FJsonValueObject>(P));
    };
    Phase(TEXT("settle"), 1, 0, 0);
    Character->GetCharacterMovement()->MaxWalkSpeed = 150;
    Phase(TEXT("walk_forward"), 3, 1, 0); Phase(TEXT("walk_right"), 2, 0, 1); Phase(TEXT("brake"), 1, 0, 0);
    if(Extended)
    {
        Phase(TEXT("walk_backward"),2,-1,0); Phase(TEXT("walk_left"),2,0,-1);
        Phase(TEXT("walk_diagonal"),2,1,1); Phase(TEXT("transition_stop"),1,0,0);
        Character->GetCharacterMovement()->MaxWalkSpeed=300;
        Phase(TEXT("run_left"),2,0,-1); Phase(TEXT("run_backward"),2,-1,0); Phase(TEXT("run_brake"),1,0,0);
    }
    Character->GetCharacterMovement()->MaxWalkSpeed = 300;
    Phase(TEXT("run_to_wall"), 5, 1, 0); Phase(TEXT("wall_stop"), 1, 0, 0);
    const double Edge = Character->GetActorLocation().X + Character->GetCapsuleComponent()->GetScaledCapsuleRadius();
    Report->SetNumberField(TEXT("wall_penetration_cm"), FMath::Max(0., Edge - 1050.));
    Report->SetNumberField(TEXT("capsule_half_height_cm"), Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
    Report->SetNumberField(TEXT("capsule_radius_cm"), Character->GetCapsuleComponent()->GetScaledCapsuleRadius());
    Report->SetNumberField(TEXT("mesh_z_offset_cm"), Character->GetMesh()->GetRelativeLocation().Z);
    Report->SetArrayField(TEXT("phases"), Phases); Report->SetStringField(TEXT("result"), TEXT("measured_not_accepted"));
    Report->SetArrayField(TEXT("captures"), Captures);
    World->EndPlay(EEndPlayReason::Quit); GEngine->DestroyWorldContext(World); World->DestroyWorld(false);
    return ParisDraft::Json(Report);
}

#include "ParisReloadDraft.inl"
