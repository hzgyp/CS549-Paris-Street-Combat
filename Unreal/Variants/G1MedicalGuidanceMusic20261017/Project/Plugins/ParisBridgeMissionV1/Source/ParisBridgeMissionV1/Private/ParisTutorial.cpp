#include "ParisTutorial.h"
#include "ParisBridgeMission.h"
#include "AIController.h"
#include "Components/BrushComponent.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Engine/OverlapResult.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "NavMesh/NavMeshBoundsVolume.h"
#include "NavMesh/RecastNavMesh.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"

namespace ParisTutorial {
namespace {
TMap<UWorld*,double> NavStarted;
TSet<UWorld*> NavReady;
TMap<UWorld*,TSharedPtr<FJsonObject>> Proofs;
TArray<TSharedPtr<FJsonValue>> V(FVector P){return {MakeShared<FJsonValueNumber>(P.X),MakeShared<FJsonValueNumber>(P.Y),MakeShared<FJsonValueNumber>(P.Z)};}
TSharedPtr<FJsonObject> Proof(UWorld* W){if(!Proofs.Contains(W))Proofs.Add(W,MakeShared<FJsonObject>());return Proofs[W];}
bool Complete(UWorld* W,ACharacter* C,FVector A,FVector B){auto* P=UNavigationSystemV1::FindPathToLocationSynchronously(W,A,B,C);return P&&P->IsValid()&&!P->IsPartial()&&P->PathPoints.Num()>=2;}
}
bool Enabled(){return FParse::Param(FCommandLine::Get(),TEXT("ParisTutorial"));}
bool InitialPlayerTransform(ACharacter* Original,FTransform& Transform,FString& Error){
    if(!Enabled()||Original->GetWorld()->URL.HasOption(TEXT("ParisLoad")))return true;
    UWorld* W=Original->GetWorld();const FVector Want=PlayerStartFeet();
    FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisTutorialInitialSpawn),false);
    for(TActorIterator<ACharacter>I(W);I;++I)Q.AddIgnoredActor(*I);
    FHitResult H;
    if(!W->LineTraceSingleByChannel(H,Want+FVector(0,0,100),Want-FVector(0,0,100),ECC_Visibility,Q)||H.ImpactNormal.Z<.7||FMath::Abs(H.ImpactPoint.Z-Want.Z)>20){Error=TEXT("Tutorial initial spawn ground rejected");return false;}
    const auto* Cap=Original->GetCapsuleComponent();const double HH=Cap->GetScaledCapsuleHalfHeight();
    const FVector At(Want.X,Want.Y,H.ImpactPoint.Z+HH+1);
    if(W->OverlapBlockingTestByChannel(At,Original->GetActorQuat(),Cap->GetCollisionObjectType(),FCollisionShape::MakeCapsule(Cap->GetScaledCapsuleRadius(),HH),Q,FCollisionResponseParams(Cap->GetCollisionResponseToChannels()))){Error=TEXT("Tutorial initial spawn capsule rejected");return false;}
    UE_LOG(LogTemp,Display,TEXT("PARIS_TUTORIAL_INITIAL_SPAWN old=%s new=%s before_begin_play=1 support=%s"),*Transform.GetLocation().ToString(),*At.ToString(),*GetPathNameSafe(H.GetComponent()));
    Transform.SetLocation(At);return true;
}
bool PrepareNavigation(AParisBridgeMission* M,FString& Error){
    UWorld* W=M->GetWorld();if(NavReady.Contains(W))return true;
    auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);if(!Nav){Error=TEXT("Tutorial navigation system missing");return false;}
    ARecastNavMesh* R=nullptr;ANavMeshBoundsVolume* B=nullptr;
    for(TActorIterator<ARecastNavMesh>I(W);I;++I){if(R){Error=TEXT("Tutorial navigation identity ambiguous");return false;}R=*I;}
    for(TActorIterator<ANavMeshBoundsVolume>I(W);I;++I){if(B){Error=TEXT("Tutorial bounds identity ambiguous");return false;}B=*I;}
    if(!R||!B){Error=TEXT("Tutorial navigation data/bounds missing");return false;}
    if(!NavStarted.Contains(W)){
        FVector OldOrigin,OldExtent;B->GetActorBounds(false,OldOrigin,OldExtent);
        const FVector OldScale=B->GetActorScale3D(),Unit=OldExtent/OldScale;
        if(Unit.GetAbsMin()<1){Error=TEXT("Tutorial bounds shape invalid");return false;}
        auto* P=FindFProperty<FEnumProperty>(R->GetClass(),TEXT("RuntimeGeneration"));
        if(!P){Error=TEXT("Tutorial runtime generation interface missing");return false;}
        P->GetUnderlyingProperty()->SetIntPropertyValue(P->ContainerPtrToValuePtr<void>(R),int64(ERuntimeGenerationType::Dynamic));
        B->GetRootComponent()->SetMobility(EComponentMobility::Movable);
        B->SetActorLocation(FVector(4000,-21500,600));B->SetActorScale3D(FVector(6000,2500,1000)/Unit);
        Nav->OnNavigationBoundsUpdated(B);R->MarkRequiresInitialRebuild();R->ConditionalConstructGenerator();R->RebuildAll();
        NavStarted.Add(W,FPlatformTime::Seconds());
        auto O=Proof(W);O->SetArrayField(TEXT("old_bounds_origin_cm"),V(OldOrigin));O->SetArrayField(TEXT("old_bounds_extent_cm"),V(OldExtent));
        O->SetStringField(TEXT("navigation_scope"),TEXT("runtime_only_tutorial_bounds_default_agent_and_query_budget"));
        UE_LOG(LogTemp,Display,TEXT("PARIS_TUTORIAL_NAV_START supports=%d old=%s extent=%s"),Nav->SupportsNavigationGeneration(),*OldOrigin.ToString(),*OldExtent.ToString());return false;
    }
    const double Age=FPlatformTime::Seconds()-NavStarted[W];
    if(Age>45){Error=TEXT("Tutorial bounded navigation rebuild timed out");return false;}
    if(Age<2||UNavigationSystemV1::IsNavigationBeingBuilt(W))return false;
    const FVector Start=PlayerStartFeet();FNavLocation N;
    if(!Nav->ProjectPointToNavigation(Start,N,FVector(25,25,150))){Error=TEXT("Tutorial new spawn outside generated native navigation");return false;}
    if(FVector::Dist2D(N.Location,Start)>25){Error=TEXT("Tutorial new spawn projection drift");return false;}
    R->SetRebuildingSuspended(true);NavReady.Add(W);Proof(W)->SetNumberField(TEXT("navigation_seconds"),Age);
    UE_LOG(LogTemp,Display,TEXT("PARIS_TUTORIAL_NAV_READY seconds=%.3f projected=%s"),Age,*N.Location.ToString());return true;
}
bool ApplyLayout(AParisBridgeMission* M,const TArray<TObjectPtr<ACharacter>>& Roster,FString& Error){
    UWorld* W=M->GetWorld();auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(W);if(!Nav||Roster.Num()!=6){Error=TEXT("Tutorial roster missing");return false;}
    FString SurveyOut;
    if(FParse::Value(FCommandLine::Get(),TEXT("ParisTutorialSurveyOut="),SurveyOut)){
        const FVector XY[]={FVector(91.186979,-22140.678907,99),FVector(-152.397309,-22340.170222,99),FVector(153.216635,-22159.461553,100),FVector(250,-22175,100),FVector(500,-22025,100),FVector(500,-21875,100),FVector(800,-21675,100),FVector(1200,-21400,100),FVector(-500,-22350,100),FVector(-1200,-22700,100),FVector(250,-22000,100),FVector(500,-21950,100),FVector(850,-22100,100),FVector(1150,-22000,100),FVector(1200,-21700,100),FVector(1500,-21650,100),FVector(900,-21200,100),FVector(600,-22500,100),FVector(-300,-22650,100),FVector(1000,-22300,100),FVector(1100,-22050,100),FVector(1600,-21800,100),FVector(1600,-22000,100),FVector(1000,-22200,100),FVector(700,-21625,100),FVector(850,-21475,100)};
        TArray<TSharedPtr<FJsonValue>> Rows;auto* C=Roster[1].Get();const auto* Cap=C->GetCapsuleComponent();
        FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisTutorialFixedSurvey),false);for(auto R:Roster)Q.AddIgnoredActor(R);
        for(int K=0;K<UE_ARRAY_COUNT(XY);++K){auto A=MakeShared<FJsonObject>();A->SetNumberField(TEXT("candidate"),K);A->SetArrayField(TEXT("requested_cm"),V(XY[K]));FNavLocation N;FHitResult H;
            bool Projected=Nav->ProjectPointToNavigation(XY[K],N,FVector(25,25,150))&&FVector::Dist2D(N.Location,XY[K])<=25;
            bool Ground=Projected&&W->LineTraceSingleByChannel(H,N.Location+FVector(0,0,100),N.Location-FVector(0,0,100),ECC_Visibility,Q)&&H.ImpactNormal.Z>=.7&&FMath::Abs(H.ImpactPoint.Z-N.Location.Z)<=20;
            A->SetBoolField(TEXT("projected"),Projected);A->SetBoolField(TEXT("ground"),Ground);
            if(Ground){FVector Feet(XY[K].X,XY[K].Y,H.ImpactPoint.Z+1),Center=Feet+FVector(0,0,Cap->GetScaledCapsuleHalfHeight());
                TArray<FOverlapResult> Hits;W->OverlapMultiByChannel(Hits,Center,C->GetActorQuat(),Cap->GetCollisionObjectType(),FCollisionShape::MakeCapsule(Cap->GetScaledCapsuleRadius(),Cap->GetScaledCapsuleHalfHeight()),Q,FCollisionResponseParams(Cap->GetCollisionResponseToChannels()));
                bool Clear=true;TArray<TSharedPtr<FJsonValue>> Blockers;for(const auto& Hit:Hits)if(Hit.bBlockingHit){Clear=false;Blockers.Add(MakeShared<FJsonValueString>(GetPathNameSafe(Hit.GetComponent())));}
                bool Path=Complete(W,C,Feet,M->FarBankFeet);A->SetArrayField(TEXT("feet_cm"),V(Feet));A->SetStringField(TEXT("support"),GetPathNameSafe(H.GetComponent()));A->SetNumberField(TEXT("normal_z"),H.ImpactNormal.Z);A->SetBoolField(TEXT("standing_capsule_clear"),Clear);A->SetArrayField(TEXT("blockers"),Blockers);A->SetBoolField(TEXT("complete_c_path"),Path);
            }Rows.Add(MakeShared<FJsonValueObject>(A));}
        auto O=Proof(W);O->SetStringField(TEXT("status"),TEXT("fixed_tutorial_candidates_measured"));O->SetArrayField(TEXT("candidates"),Rows);FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(O.ToSharedRef(),Writer);IFileManager::Get().MakeDirectory(*SurveyOut,true);FFileHelper::SaveStringToFile(Text,*(SurveyOut/TEXT("RESULT.json")));FPlatformMisc::RequestExit(false);return true;
    }
    const FVector Wants[]={PlayerStartFeet(),FVector(850,-21475,100),FVector(900,-21200,100)};
    const TCHAR* Names[]={TEXT("Player"),TEXT("Ally1"),TEXT("Ally2")};
    FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisTutorialLayout),false);for(auto C:Roster)Q.AddIgnoredActor(C);
    FVector Targets[3];TArray<TSharedPtr<FJsonValue>> Rows;
    for(int K=0;K<3;++K){
        auto* C=Roster[K].Get();const auto& Agent=C->GetCharacterMovement()->GetNavAgentPropertiesRef();FNavLocation N;
        if(!Nav->ProjectPointToNavigation(Wants[K],N,FVector(25,25,150),&Agent)||FVector::Dist2D(Wants[K],N.Location)>25){Error=FString::Printf(TEXT("Tutorial %s native projection rejected"),Names[K]);return false;}
        FHitResult H;if(!W->LineTraceSingleByChannel(H,N.Location+FVector(0,0,100),N.Location-FVector(0,0,100),ECC_Visibility,Q)||H.ImpactNormal.Z<.7||FMath::Abs(H.ImpactPoint.Z-N.Location.Z)>20){Error=FString::Printf(TEXT("Tutorial %s ground rejected"),Names[K]);return false;}
        const double HH=C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),RR=C->GetCapsuleComponent()->GetScaledCapsuleRadius();Targets[K]=FVector(Wants[K].X,Wants[K].Y,H.ImpactPoint.Z+HH+1);
        if(W->OverlapBlockingTestByChannel(Targets[K],C->GetActorQuat(),C->GetCapsuleComponent()->GetCollisionObjectType(),FCollisionShape::MakeCapsule(RR,HH),Q,FCollisionResponseParams(C->GetCapsuleComponent()->GetCollisionResponseToChannels()))){Error=FString::Printf(TEXT("Tutorial %s standing capsule rejected"),Names[K]);return false;}
        if(!Complete(W,C,Targets[K]-FVector(0,0,HH),M->FarBankFeet)){Error=FString::Printf(TEXT("Tutorial %s complete C route rejected"),Names[K]);return false;}
        for(int J=0;J<K;++J)if(FVector::Dist2D(Targets[K],Targets[J])<200){Error=TEXT("Tutorial actor spacing rejected");return false;}
        auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("id"),Names[K]);A->SetArrayField(TEXT("feet_cm"),V(Targets[K]-FVector(0,0,HH)));A->SetArrayField(TEXT("floor_cm"),V(H.ImpactPoint));A->SetStringField(TEXT("support"),GetPathNameSafe(H.GetComponent()));A->SetNumberField(TEXT("normal_z"),H.ImpactNormal.Z);A->SetBoolField(TEXT("standing_capsule_clear"),true);A->SetBoolField(TEXT("complete_c_path"),true);Rows.Add(MakeShared<FJsonValueObject>(A));
        UE_LOG(LogTemp,Display,TEXT("PARIS_TUTORIAL_LAYOUT_ADMIT id=%s feet=%s support=%s normal=%.6f"),Names[K],*(Targets[K]-FVector(0,0,HH)).ToString(),*GetPathNameSafe(H.GetComponent()),H.ImpactNormal.Z);
    }
    for(int K=0;K<3;++K){Roster[K]->SetActorLocation(Targets[K],false);Roster[K]->GetCharacterMovement()->StopMovementImmediately();}
    for(int K=1;K<3;++K)if(auto* A=Cast<AAIController>(Roster[K]->GetController())){
        auto* F=A->FindFunction(TEXT("PC_SetSearchRole"));if(!F){Error=TEXT("Relocated Ally role endpoint missing");return false;}
        FStructOnScope Args(F);FindFProperty<FBoolProperty>(F,TEXT("Patrol"))->SetPropertyValue_InContainer(Args.GetStructMemory(),false);
        *FindFProperty<FStructProperty>(F,TEXT("PatrolPoint"))->ContainerPtrToValuePtr<FVector>(Args.GetStructMemory())=Targets[K];FindFProperty<FDoubleProperty>(F,TEXT("Radius"))->SetPropertyValue_InContainer(Args.GetStructMemory(),500);
        A->ProcessEvent(F,Args.GetStructMemory());for(const TCHAR* Field:{TEXT("GuardAnchor"),TEXT("HomePoint")})if(auto* P=FindFProperty<FStructProperty>(A->GetClass(),Field))*P->ContainerPtrToValuePtr<FVector>(A)=Targets[K];
    }
    Proof(W)->SetArrayField(TEXT("new_starts"),Rows);return true;
}
void Ready(AParisBridgeMission* M){
    if(!Enabled())return;ConfigureReady(M);FString Out;if(!FParse::Value(FCommandLine::Get(),TEXT("ParisTutorialSitesOut="),Out))return;
    auto O=Proof(M->GetWorld());O->SetStringField(TEXT("status"),TEXT("pass_tutorial_start_sites_native_paths"));O->SetStringField(TEXT("state"),M->ReadMissionState());
    FString Text;auto Writer=TJsonWriterFactory<>::Create(&Text);FJsonSerializer::Serialize(O.ToSharedRef(),Writer);IFileManager::Get().MakeDirectory(*Out,true);FFileHelper::SaveStringToFile(Text,*(Out/TEXT("RESULT.json")));FPlatformMisc::RequestExit(false);
}
}

namespace ParisTutorial {void ClearWorld(UWorld* W){NavStarted.Remove(W);NavReady.Remove(W);Proofs.Remove(W);}}
