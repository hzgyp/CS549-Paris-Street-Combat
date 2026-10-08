#include "ParisBridgeMission.h"
#include "AIController.h"
#include "BehaviorTree/BehaviorTree.h"
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
#include "Perception/PawnSensingComponent.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/StructOnScope.h"
#include "UObject/UnrealType.h"
#include <limits>

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

bool AParisBridgeMission::BuildBridgePath(FString& Error)
{
    if(BridgePath.Num()>1) return true;
    const FVector Ends[] = {FVector(-3162.5,-25937.5,110.116898),FVector(1950,-20650,114.262990),FarBankFeet};
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
    double Wanted=FMath::Max(0.0,Progress-(Index==1?450:700)); FVector Goal=BridgePath[0];
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
    if(!AllowsPlay()) return;
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
    if(DeathLedger.Contains(TEXT("Player"))) { SetPhase(TEXT("Lost")); Feedback=TEXT("Player lost. F9 loads a save; Ctrl+R restarts."); GateBrains(false); return; }
    ACharacter* P=Roster[0];
    FVector Feet=P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());
    if(Phase==TEXT("Crossing") && FVector::Dist2D(Feet,FarBankFeet)<=ReachRadius && FMath::Abs(Feet.Z-FarBankFeet.Z)<=100) SetPhase(TEXT("Clearing"));
    if(Phase==TEXT("Clearing") && LivingDefenders==0 && DeathLedger.Contains(TEXT("German1")) && DeathLedger.Contains(TEXT("German2")) && DeathLedger.Contains(TEXT("German3"))) SetPhase(TEXT("Occupying"));
    if(Phase==TEXT("Occupying") && FVector::Dist2D(Feet,BridgeheadFeet)<=OccupyRadius && FMath::Abs(Feet.Z-BridgeheadFeet.Z)<=100 && P->GetCharacterMovement()->IsMovingOnGround())
    { SetPhase(TEXT("Won")); Feedback=TEXT("G1 bridgehead captured. F5 saves the result; Ctrl+R restarts."); GateBrains(false); }
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
            if(Params.Key==EKeys::F5) { M->SaveCheckpoint(); return true; }
            if(Params.Key==EKeys::F9) { M->LoadCheckpoint(); return true; }
            if(Params.Key==EKeys::R && bMissionControlHeld) { M->RestartMission(); return true; }
        }
        if(!M->AllowsPlay() && Params.Key!=EKeys::Tilde && Params.Key!=EKeys::Escape) return true;
    }
    return Super::InputKey(Params);
}
void AParisBridgePlayerController::MissionStart() { if(auto* M=AParisBridgeMission::Find(this)) M->StartMission(); }
void AParisBridgePlayerController::MissionSave() { if(auto* M=AParisBridgeMission::Find(this)) M->SaveCheckpoint(); }
void AParisBridgePlayerController::MissionLoad() { if(auto* M=AParisBridgeMission::Find(this)) M->LoadCheckpoint(); }
void AParisBridgePlayerController::MissionRestart() { if(auto* M=AParisBridgeMission::Find(this)) M->RestartMission(); }

AParisBridgeGameMode::AParisBridgeGameMode()
{
    DefaultPawnClass=nullptr; PlayerControllerClass=AParisBridgePlayerController::StaticClass(); HUDClass=AParisBridgeHUD::StaticClass();
}

void AParisBridgeHUD::DrawHUD()
{
    Super::DrawHUD(); if(!Canvas) return;
    auto* M=AParisBridgeMission::Find(this); if(!M) return;
    FString Objective=TEXT("Preparing selected equipment...");
    if(M->Phase==TEXT("Ready")) Objective=TEXT("G1 BRIDGEHEAD | Press Enter to start");
    else if(M->Phase==TEXT("Crossing")) Objective=TEXT("OBJECTIVE: Cross bridge C and reach the far bank");
    else if(M->Phase==TEXT("Clearing")) Objective=FString::Printf(TEXT("OBJECTIVE: Clear G1 | %d defenders remaining"),M->LivingDefenders);
    else if(M->Phase==TEXT("Occupying")) Objective=TEXT("OBJECTIVE: Occupy the G1 bridgehead");
    else if(M->Phase==TEXT("Won")) Objective=TEXT("MISSION COMPLETE | G1 bridgehead captured");
    else if(M->Phase==TEXT("Lost")) Objective=TEXT("MISSION LOST | Load a save or restart");
    else if(M->Phase==TEXT("Error")) Objective=TEXT("MISSION STOPPED | Configuration / acceptance error");
    DrawRect(FLinearColor(0,0,0,.72f),18,18,FMath::Min(Canvas->SizeX-36,900),116);
    DrawText(Objective,FLinearColor::White,32,28,GEngine->GetMediumFont(),1.1f);
    DrawText(TEXT("Enter Start   F5 Safe save   F9 Load   Ctrl+R Full restart   R Reload"),FLinearColor(.7f,.85f,1),32,61,GEngine->GetSmallFont());
    DrawText(M->Feedback,FLinearColor(1,.85f,.45f),32,86,GEngine->GetSmallFont());
    if(APawn* P=PlayerOwner ? PlayerOwner->GetPawn() : nullptr)
        DrawText(FString::Printf(TEXT("HP %.0f   Ammo %.0f / %.0f   Allies %d / 2"),Number(P,TEXT("Health")),Number(P,TEXT("LoadedAmmo")),Number(P,TEXT("ReserveAmmo")),M->LivingAllies),FLinearColor::White,32,110,GEngine->GetSmallFont());
    if(M->AllowsPlay())
    {
        FVector Goal=M->Phase==TEXT("Crossing")?M->FarBankFeet:M->BridgeheadFeet;
        FVector2D Screen;
        if(PlayerOwner && PlayerOwner->ProjectWorldLocationToScreen(Goal+FVector(0,0,150),Screen) && Screen.X>0 && Screen.X<Canvas->SizeX && Screen.Y>140 && Screen.Y<Canvas->SizeY)
            DrawText(M->Phase==TEXT("Crossing")?TEXT("T1"):TEXT("G1"),FLinearColor(1,.8f,.15f),Screen.X,Screen.Y,GEngine->GetMediumFont());
    }
}
