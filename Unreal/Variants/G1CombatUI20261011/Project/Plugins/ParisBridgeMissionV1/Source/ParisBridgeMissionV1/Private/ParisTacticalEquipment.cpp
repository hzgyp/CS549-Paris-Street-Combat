#include "ParisTacticalEquipment.h"
#include "ParisCombatUI.h"
#include "Camera/PlayerCameraManager.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"
#include "Engine/Texture2D.h"
#include "ImageUtils.h"
#include "RenderTimer.h"
#include "RHI.h"
#include "ParisEquipmentState.h"
#include "ParisEquipmentSightBridge.h"
#include "ParisBridgeMission.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/Skeleton.h"
#include "AIController.h"
#include "Navigation/PathFollowingComponent.h"
#include "BrainComponent.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/AudioComponent.h"
#include "Particles/ParticleSystem.h"
#include "Particles/ParticleEmitter.h"
#include "Particles/ParticleSpriteEmitter.h"
#include "Particles/ParticleLODLevel.h"
#include "Particles/ParticleModuleRequired.h"
#include "Particles/Spawn/ParticleModuleSpawn.h"
#include "Particles/Lifetime/ParticleModuleLifetime.h"
#include "Particles/Size/ParticleModuleSize.h"
#include "Particles/Velocity/ParticleModuleVelocity.h"
#include "Particles/Location/ParticleModuleLocation.h"
#include "Particles/Color/ParticleModuleColorOverLife.h"
#include "Distributions/DistributionFloatConstant.h"
#include "Distributions/DistributionFloatParticleParameter.h"
#include "Distributions/DistributionVectorConstant.h"
#include "Distributions/DistributionVectorUniform.h"
#include "Particles/ParticleSystemComponent.h"
#include "ParticleEmitterInstances.h"
#include "Particles/SubUV/ParticleModuleSubUV.h"
#include "Particles/Parameter/ParticleModuleParameterDynamic.h"
#include "Sound/SoundWaveProcedural.h"
#include "Sound/SoundAttenuation.h"
#include "HAL/PlatformProcess.h"
#include "Misc/Paths.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "NavigationSystem.h"
#include "NavigationPath.h"
#include "InputKeyEventArgs.h"
#include "Serialization/JsonSerializer.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"
#include "UnrealClient.h"

namespace ParisTacticalEquipment {
namespace {
TMap<UWorld*,TUniquePtr<FEquipmentSession>> Sessions;
FDelegateHandle TickHandle,PreTickHandle,CleanupHandle;
FString CheckMode,CheckOut;
bool CheckFinished=false;
int32 CheckStep=0;
double CheckClock=0;
UObject* Obj(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FObjectPropertyBase>(O->GetClass(),K):nullptr;return P?P->GetObjectPropertyValue_InContainer(O):nullptr;}
double Num(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!P)return -1;const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):P->GetSignedIntPropertyValue(V);}
bool SetNum(UObject* O,const TCHAR* K,double X){auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!P)return false;void* V=P->ContainerPtrToValuePtr<void>(O);if(P->IsFloatingPoint())P->SetFloatingPointPropertyValue(V,X);else P->SetIntPropertyValue(V,int64(X));return true;}
FName Name(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr;return P?P->GetPropertyValue_InContainer(O):NAME_None;}
void SetName(UObject* O,const TCHAR* K,FName X){if(auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr)P->SetPropertyValue_InContainer(O,X);}
bool Dead(const ACharacter* C){return !IsValid(C)||Num(C,TEXT("Health"))<=0;}
bool Flag(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),K):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
void Invoke(UObject* O,const TCHAR* K,double X=0,const TCHAR* Arg=nullptr){auto* F=O?O->FindFunction(K):nullptr;if(!F)return;FStructOnScope Params(F);if(Arg)if(auto* P=CastField<FNumericProperty>(F->FindPropertyByName(Arg)))P->SetFloatingPointPropertyValue(P->ContainerPtrToValuePtr<void>(Params.GetStructMemory()),X);O->ProcessEvent(F,Params.GetStructMemory());}
TArray<ACharacter*> Combatants(UWorld* W){TArray<ACharacter*> A;for(TActorIterator<ACharacter> I(W);I;++I)if(I->FindFunction(TEXT("PC_ApplyDamage")))A.Add(*I);return A;}
AActor* Display(UWorld* W,ACharacter* P){for(TActorIterator<AActor> I(W);I;++I)if(I->GetOwner()==P && Obj(*I,TEXT("Pose")) && Obj(*I,TEXT("Gun")))return *I;return nullptr;}
void Event(UWorld* W,const FString& Kind,const FString& Id,double Amount=0){auto& S=Session(W);auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("kind"),Kind);E->SetStringField(TEXT("id"),Id);E->SetNumberField(TEXT("amount"),Amount);E->SetNumberField(TEXT("time"),W->GetTimeSeconds());S.Events.Add(MakeShared<FJsonValueObject>(E));UE_LOG(LogTemp,Display,TEXT("PARIS_EQUIPMENT %s %s %.6f"),*Kind,*Id,Amount);}
void Notice(UWorld* W,const FString& Text){auto& S=Session(W);S.Notice=Text;S.NoticeUntil=W->GetTimeSeconds()+3;}
UStaticMesh* Shape(const TCHAR* K){return LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Engine/BasicShapes/%s.%s"),K,K));}
UStaticMeshComponent* Part(AActor* A,const TCHAR* Mesh,FVector Size,FVector At,FLinearColor Color){auto* C=NewObject<UStaticMeshComponent>(A);A->AddInstanceComponent(C);C->SetStaticMesh(Shape(Mesh));C->SetCollisionEnabled(ECollisionEnabled::NoCollision);C->SetCanEverAffectNavigation(false);C->SetupAttachment(A->GetRootComponent());C->SetRelativeScale3D(Size);C->SetRelativeLocation(At);C->RegisterComponent();if(auto* M=C->CreateDynamicMaterialInstance(0)){M->SetVectorParameterValue(TEXT("Color"),Color);M->SetVectorParameterValue(TEXT("BaseColor"),Color);}return C;}
AActor* Prop(UWorld* W,const FString& Kind,FVector P){auto* A=W->SpawnActor<AActor>();auto* R=NewObject<USceneComponent>(A);A->AddInstanceComponent(R);A->SetRootComponent(R);R->RegisterComponent();A->SetActorLocation(P);A->Tags.Add(TEXT("ParisEquipmentOwned"));const FLinearColor Green(.12,.17,.065),Steel(.23,.25,.23);
    if(Kind==TEXT("Frag")){Part(A,TEXT("Sphere"),FVector(.065,.065,.095),FVector::ZeroVector,Green);Part(A,TEXT("Cylinder"),FVector(.027,.027,.022),FVector(0,0,5),Steel);auto* Lever=Part(A,TEXT("Cube"),FVector(.01,.017,.105),FVector(0,2.4,1),Steel);Lever->SetRelativeRotation(FRotator(0,0,15));}
    else if(Kind==TEXT("Smoke")){Part(A,TEXT("Cylinder"),FVector(.065,.065,.14),FVector::ZeroVector,Green);Part(A,TEXT("Cylinder"),FVector(.068,.068,.008),FVector(0,0,6.8),Steel);Part(A,TEXT("Cube"),FVector(.01,.018,.105),FVector(0,3.2,3),Steel);}return A;
}
void IgnoreProps(UWorld* W,FCollisionQueryParams& Q){for(TActorIterator<AActor> I(W);I;++I)if(I->ActorHasTag(TEXT("ParisEquipmentOwned")))Q.AddIgnoredActor(*I);}
void HideGun(UWorld* W,ACharacter* P,bool Hidden){if(auto* D=Display(W,P))if(auto* G=Cast<UPrimitiveComponent>(Obj(D,TEXT("Gun"))))G->SetVisibility(!Hidden,true);}
void EndThrow(UWorld* W,FEquipmentSession& S,bool Died=false){auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(S.Held.IsValid())S.Held->Destroy();S.Held.Reset();HideGun(W,P,Died);if(P&&!Died){P->GetMesh()->SetAnimationMode(EAnimationMode::Type(S.OriginalAnimMode));if(S.OriginalAnimClass.IsValid()&&S.OriginalAnimMode==EAnimationMode::AnimationBlueprint)P->GetMesh()->SetAnimInstanceClass(S.OriginalAnimClass.Get());SetName(P,TEXT("ActionState"),TEXT("Ready"));SetName(P,TEXT("ActivePose"),NAME_None);Invoke(P,TEXT("PC_UpdateActionPose"));}S.ThrowKind.Empty();S.ThrowStage.Empty();S.ReleaseQueued=false;S.ThrowCommitted=false;S.ActionClock=0;}
void PlayThrow(UWorld* W,FEquipmentSession& S,const FString& Stage){auto* P=UGameplayStatics::GetPlayerCharacter(W,0);const FString Suffix=Stage==TEXT("Start")?TEXT("Start"):Stage==TEXT("Cancel")?TEXT("Cancel"):TEXT("Far");const FString Path=TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Grenade_Throw_")+Suffix+TEXT(".Rifle_Grenade_Throw_")+Suffix;S.ThrowClip.Reset(LoadObject<UAnimSequence>(nullptr,*Path));checkf(S.ThrowClip.IsValid()&&S.ThrowClip->GetSkeleton()->IsCompatibleMesh(P->GetMesh()->GetSkeletalMeshAsset()),TEXT("Grenade clip must match existing hierarchy"));P->GetMesh()->PlayAnimation(S.ThrowClip.Get(),false);S.ThrowStage=Stage;S.ActionClock=0;}
void BeginThrow(UWorld* W,const FString& Kind){auto& S=Session(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!P||Dead(P)||!S.ThrowKind.IsEmpty()||Name(P,TEXT("ActionState"))!=TEXT("Ready"))return;auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized"))){Notice(W,TEXT("FIRST PERSON EQUIPMENT PREPARING"));return;}if((Kind==TEXT("Frag")?S.Frag:S.Smoke)==0){Notice(W,TEXT("NO GRENADES REMAIN"));return;}S.OriginalAnimMode=P->GetMesh()->GetAnimationMode();S.OriginalAnimClass=P->GetMesh()->GetAnimClass();S.ThrowKind=Kind;SetName(P,TEXT("ActionState"),TEXT("Throwing"));HideGun(W,P,true);S.Held=Prop(W,Kind,P->GetActorLocation());if(auto* Pose=Cast<UPoseableMeshComponent>(Obj(D,TEXT("Pose")))){S.Held->AttachToComponent(Pose,FAttachmentTransformRules::SnapToTargetNotIncludingScale,TEXT("hand_r"));const FVector Palm=Pose->GetSocketLocation(TEXT("middle_01_r"));const FVector Tips=(Pose->GetSocketLocation(TEXT("middle_03_r"))+Pose->GetSocketLocation(TEXT("ring_03_r")))*.5;const FVector Center=(Palm+Tips)*.5;S.Held->SetActorRelativeLocation(Pose->GetSocketTransform(TEXT("hand_r")).InverseTransformPosition(Center));}PlayThrow(W,S,TEXT("Start"));Event(W,TEXT("prepare"),Kind);}
void CommitThrow(UWorld* W,FEquipmentSession& S){if(S.ThrowCommitted)return;auto* PC=UGameplayStatics::GetPlayerController(W,0);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisGrenadeRelease),false,P);IgnoreProps(W,Q);FHitResult Hit;const FVector Want=Eye+View.Vector()*45;FVector At=Want;if(W->SweepSingleByChannel(Hit,Eye,Want,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(3.3),Q))At=Hit.Location;
    FBall Ball;Ball.Kind=S.ThrowKind;int32& Count=Ball.Kind==TEXT("Frag")?S.FragThrown:S.SmokeThrown;int32& Inventory=Ball.Kind==TEXT("Frag")?S.Frag:S.Smoke;check(Inventory>0);--Inventory;++Count;Ball.Id=Ball.Kind+FString::FromInt(Count);Ball.Position=At;Ball.Velocity=View.Vector()*1100+FVector(0,0,200)+P->GetVelocity()*.5;Ball.Visual=Prop(W,Ball.Kind,At);S.Balls.Add(Ball);S.ThrowCommitted=true;if(S.Held.IsValid())S.Held->Destroy();S.Held.Reset();Event(W,TEXT("commit"),Ball.Id);
}
void ThrowTick(UWorld* W,FEquipmentSession& S,float DT){if(S.ThrowKind.IsEmpty())return;auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(Dead(P)){EndThrow(W,S,true);return;}HideGun(W,P,true);S.ActionClock+=DT;
    if(S.ThrowStage==TEXT("Start")&&S.ActionClock>=S.ThrowClip->GetPlayLength()){if(S.ReleaseQueued)PlayThrow(W,S,TEXT("Release"));else{S.ThrowStage=TEXT("Hold");P->GetMesh()->GetSingleNodeInstance()->SetPlaying(false);}}
    else if(S.ThrowStage==TEXT("Hold")&&S.ReleaseQueued)PlayThrow(W,S,TEXT("Release"));else if(S.ThrowStage==TEXT("Release")){if(S.ActionClock>=.55)CommitThrow(W,S);if(S.ActionClock>=S.ThrowClip->GetPlayLength())EndThrow(W,S);}else if(S.ThrowStage==TEXT("Cancel")&&S.ActionClock>=S.ThrowClip->GetPlayLength())EndThrow(W,S);
}
#include "ParisEquipmentAudio.inl"
void Blast(UWorld* W,FVector At,const FString& Id,double Radius=600,double MaxDamage=180){Event(W,TEXT("blast"),Id);ExplosionAV(W,At);for(auto* C:Combatants(W))if(!Dead(C)){const double Distance=FVector::Distance(At,C->GetActorLocation());if(Distance>Radius)continue;int32 Visible=0;FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisBlastOcclusion),true);IgnoreProps(W,Q);for(const FVector Offset:{FVector(0,0,-40),FVector::ZeroVector,FVector(0,0,55)}){FHitResult Hit;if(!W->LineTraceSingleByChannel(Hit,At,C->GetActorLocation()+Offset,ECC_Visibility,Q)||Hit.GetActor()==C)++Visible;}const double Damage=MaxDamage*FMath::Clamp(1.-Distance/Radius,0.,1.)*Visible/3.;if(Damage>0){const double Before=Num(C,TEXT("Health"));Invoke(C,TEXT("PC_ApplyDamage"),Damage,TEXT("Amount"));Event(W,TEXT("damage"),C->GetName(),Before-Num(C,TEXT("Health")));Event(W,TEXT("damage_before_health"),C->GetName(),Before);Event(W,TEXT("damage_after_health"),C->GetName(),Num(C,TEXT("Health")));}}}
#include "ParisEquipmentWorld.inl"
void BallTick(UWorld* W,FEquipmentSession& S,float DT){for(int32 I=S.Balls.Num()-1;I>=0;--I){auto& B=S.Balls[I];double Left=FMath::Min(double(DT),B.Fuse);while(Left>0){const double Step=FMath::Min(Left,1./120.);Left-=Step;FCollisionQueryParams Q(SCENE_QUERY_STAT(ParisEquipmentSweep),false);IgnoreProps(W,Q);if(B.Age<.2)Q.AddIgnoredActor(UGameplayStatics::GetPlayerCharacter(W,0));FHitResult Hit;B.Velocity.Z+=W->GetGravityZ()*Step;const FVector Want=B.Position+B.Velocity*Step;if(W->SweepSingleByChannel(Hit,B.Position,Want,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(3.3),Q)){B.Position=Hit.Location+Hit.ImpactNormal*.05;B.Velocity=(B.Velocity-2*FVector::DotProduct(B.Velocity,Hit.ImpactNormal)*Hit.ImpactNormal)*.45;if(B.Velocity.Size()<35&&Hit.ImpactNormal.Z>.65)B.Velocity=FVector::ZeroVector;}else B.Position=Want;B.Age+=Step;B.Fuse-=Step;}if(B.Visual.IsValid()){B.Visual->SetActorLocation(B.Position);B.Visual->AddActorLocalRotation(FRotator(DT*130,DT*90,DT*30));}if(B.Fuse<=.000001){if(B.Kind==TEXT("Frag"))Blast(W,B.Position,B.Id);else {FSmoke C;C.Id=B.Id;C.Position=B.Position;S.Clouds.Add(C);SmokeVisual(W,S.Clouds.Last());Event(W,TEXT("smoke_deployed"),B.Id);}if(B.Visual.IsValid())B.Visual->Destroy();S.Balls.RemoveAt(I);}}}
void Picture(const TCHAR* Name){FScreenshotRequest::RequestScreenshot(CheckOut/FString(Name),false,false);}
void FinishCheck(UWorld* W,bool Pass,const FString& Why){auto& S=Session(W);auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Pass?FString(TEXT("pass_native_"))+CheckMode:FString(TEXT("failed_"))+CheckMode);O->SetStringField(TEXT("reason"),Why);O->SetStringField(TEXT("scope"),TEXT("real controller input; NPC brains paused for action isolation; not natural combat"));O->SetArrayField(TEXT("events"),S.Events);O->SetNumberField(TEXT("frag"),S.Frag);O->SetNumberField(TEXT("frag_thrown"),S.FragThrown);O->SetNumberField(TEXT("active_balls"),S.Balls.Num());auto* P=UGameplayStatics::GetPlayerCharacter(W,0);O->SetStringField(TEXT("player_location"),P->GetActorLocation().ToString());O->SetNumberField(TEXT("player_health"),Num(P,TEXT("Health")));O->SetNumberField(TEXT("capsule_half"),P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());for(const TCHAR* Field:{TEXT("ShotOutcome"),TEXT("ShotAimPoint")})if(auto* F=FindFProperty<FProperty>(P->GetClass(),Field)){FString V;F->ExportText_InContainer(0,V,P,P,P,PPF_None);O->SetStringField(Field,V);}O->SetStringField(TEXT("action"),Name(P,TEXT("ActionState")).ToString());O->SetNumberField(TEXT("loaded"),Num(P,TEXT("LoadedAmmo")));O->SetNumberField(TEXT("reserve"),Num(P,TEXT("ReserveAmmo")));O->SetNumberField(TEXT("shots"),Num(P,TEXT("ShotSequence")));if(auto* D=Display(W,P)){O->SetNumberField(TEXT("finger_error"),Num(D,TEXT("FingerRotationErrorDegrees")));O->SetNumberField(TEXT("grip_alpha"),Num(D,TEXT("HoldingAppliedAlpha")));}FString J;auto Writer=TJsonWriterFactory<>::Create(&J);FJsonSerializer::Serialize(O,Writer);FFileHelper::SaveStringToFile(J,*(CheckOut/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);CheckFinished=true;FPlatformMisc::RequestExit(false);}
#include "ParisEquipmentChecks.inl"
void Check(UWorld* W,AParisBridgeMission* M,FEquipmentSession& S,float DT){if(CheckMode.IsEmpty()||CheckFinished)return;auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!PC||!P)return;
    if(M->Phase==TEXT("Error")){FinishCheck(W,false,M->Feedback);return;}
    if(CheckMode!=TEXT("throw")){EquipmentCheck(W,M,S,PC,P,DT);return;}
    if(CheckStep==0){if(M->Phase!=TEXT("Ready"))return;auto* D=Display(W,P);if(!D||!Flag(D,TEXT("Initialized"))){CheckClock+=DT;if(CheckClock>15)FinishCheck(W,false,TEXT("Formal first person did not initialize"));return;}M->StartMission();for(auto* C:Combatants(W))if(auto* AI=Cast<AAIController>(C->GetController()))if(AI->GetBrainComponent())AI->GetBrainComponent()->PauseLogic(TEXT("Independent throw presentation check"));PC->SetControlRotation(FRotator(-5,0,0));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::G,IE_Pressed,1));CheckStep=1;CheckClock=0;return;}
    CheckClock+=DT;
    if(CheckStep==1&&CheckClock>.85){Picture(TEXT("01_prepare.png"));PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::G,IE_Released,0));CheckStep=2;CheckClock=0;}
    else if(CheckStep==2&&CheckClock>.25){Picture(TEXT("02_release.png"));CheckStep=3;CheckClock=0;}
    else if(CheckStep==3&&CheckClock>.4){Picture(TEXT("03_commit.png"));CheckStep=4;CheckClock=0;}
    else if(CheckStep==4&&CheckClock>1.2){Picture(TEXT("04_return.png"));CheckStep=5;CheckClock=0;PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::G,IE_Pressed,1));}
    else if(CheckStep==5&&CheckClock>.2){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::Escape,IE_Pressed,1));CheckStep=6;CheckClock=0;}
    else if(CheckStep==6&&CheckClock>1.4){Picture(TEXT("05_cancel_return.png"));CheckStep=7;CheckClock=0;}
    else if(CheckStep==7&&CheckClock>.3){const bool Good=S.Frag==1&&S.FragThrown==1&&S.ThrowKind.IsEmpty()&&Name(P,TEXT("ActionState"))==TEXT("Ready")&&Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))+Num(P,TEXT("ShotSequence"))==18;FinishCheck(W,Good,TEXT("Preparation, unique release, cancel without spend, authoritative weapon resources"));}
}
void Tick(UWorld* W,ELevelTick,float DT){if(!W||!W->IsGameWorld())return;auto* M=AParisBridgeMission::Find(W);if(!M)return;auto& S=Session(W);if(CheckMode!=TEXT("survey")&&M->Phase!=TEXT("Preparing")&&M->Phase!=TEXT("Error")&&!SetupSites(W,S)){M->Phase=TEXT("Error");M->Feedback=TEXT("Equipment site failed ground/capsule/full-path validation.");}ThrowTick(W,S,DT);BallTick(W,S,DT);SmokeTick(W,S,DT);if(M->AllowsPlay()||M->Phase==TEXT("Won")){TrapTick(W,S,DT);HazardTick(W,S);}Check(W,M,S,DT);}
void Cleanup(UWorld* W,bool,bool){auto* S=Sessions.Find(W);if(S){ClearVisuals(**S);Sessions.Remove(W);}}
}
FEquipmentSession& Session(UWorld* W){auto* Existing=Sessions.Find(W);if(Existing)return **Existing;auto S=MakeUnique<FEquipmentSession>();auto* M=AParisBridgeMission::Find(W);S->Generation=M?M->RunGeneration:FString();for(int32 I=1;I<=2;++I){FTrap T;T.Id=TEXT("Trap")+FString::FromInt(I);S->Traps.Add(T);FSupply B;B.Id=TEXT("Supply")+FString::FromInt(I);S->Supplies.Add(B);}auto& Result=*S;Sessions.Add(W,MoveTemp(S));return Result;}
void ClearVisuals(FEquipmentSession& S){if(S.Held.IsValid())S.Held->Destroy();for(auto& B:S.Balls)if(B.Visual.IsValid())B.Visual->Destroy();for(auto& C:S.Clouds)if(C.Visual.IsValid())C.Visual->Destroy();for(auto& T:S.Traps)if(T.Visual.IsValid())T.Visual->Destroy();for(auto& B:S.Supplies)if(B.Visual.IsValid())B.Visual->Destroy();}
void CreateVisuals(UWorld* W,FEquipmentSession& S){if(S.Initialized)SiteVisuals(W,S);else check(SetupSites(W,S));for(auto& B:S.Balls)B.Visual=Prop(W,B.Kind,B.Position);for(auto& C:S.Clouds)SmokeVisual(W,C);}
bool OwnsNavigation(const AAIController* AI){if(!AI||!AParisBridgeMission::Find(AI)||!AParisBridgeMission::Find(AI)->AllowsPlay())return false;auto* Existing=Sessions.Find(AI->GetWorld());if(!Existing)return false;for(const auto& E:(*Existing)->Evades)if(E.Pawn.Get()==AI->GetPawn()&&!Dead(E.Pawn.Get())&&AI->GetWorld()->GetTimeSeconds()<E.Until)return true;return false;}
bool Occluded(UWorld* W,const FVector& From,const FVector& To){return CloudBlock(W,From,To);}
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& Params){
    auto* M=AParisBridgeMission::Find(PC);if(!M||(!M->AllowsPlay()&&M->Phase!=TEXT("Won")))return false;auto* W=PC->GetWorld();auto& S=Session(W);
    if(Params.Key==EKeys::E&&M->InsideCheckpoint()){if(!S.ThrowKind.IsEmpty())EndThrow(W,S);S.EHeld=false;S.DisarmClock=0;return false;}
    if(S.EHeld){if(Params.Key==EKeys::Escape&&Params.Event==IE_Pressed){S.EHeld=false;S.DisarmClock=0;S.InteractId.Empty();Notice(W,TEXT("DISARM CANCELLED"));return true;}if(Params.Key==EKeys::LeftMouseButton||Params.Key==EKeys::R)return true;}
    if(Params.Key==EKeys::G||Params.Key==EKeys::Q){const FString Kind=Params.Key==EKeys::G?TEXT("Frag"):TEXT("Smoke");if(Params.Event==IE_Pressed){S.EHeld=false;S.DisarmClock=0;S.InteractId.Empty();BeginThrow(W,Kind);}if(Params.Event==IE_Released&&S.ThrowKind==Kind)S.ReleaseQueued=true;return true;}
    if(!S.ThrowKind.IsEmpty()){if(Params.Key==EKeys::Escape&&Params.Event==IE_Pressed){if(!S.ThrowCommitted)PlayThrow(W,S,TEXT("Cancel"));else EndThrow(W,S);return true;}if(Params.Key==EKeys::LeftMouseButton||Params.Key==EKeys::R||Params.Key==EKeys::E)return true;}
    return WorldInput(W,S,Params);
}
FString HudInventory(UWorld* W){auto& S=Session(W);return FString::Printf(TEXT("G  FRAG %d     Q  SMOKE %d"),S.Frag,S.Smoke);}
FString HudInteraction(UWorld* W){auto& S=Session(W);if(!S.ThrowKind.IsEmpty())return S.ThrowStage==TEXT("Start")||S.ThrowStage==TEXT("Hold")?FString::Printf(TEXT("RELEASE %s TO THROW  /  ESC CANCEL"),S.ThrowKind==TEXT("Frag")?TEXT("G"):TEXT("Q")):TEXT("THROWING");if(S.EHeld)return TEXT("DISARMING  /  RELEASE E OR MOVE TO CANCEL");const FString Id=Target(W,S);if(Id.StartsWith(TEXT("Trap")))return TEXT("HOLD E 2s  DISARM MINE");for(const auto& B:S.Supplies)if(B.Id==Id)return B.Remaining?FString::Printf(TEXT("E  AMMO SUPPLY  /  %d ROUNDS"),B.Remaining):TEXT("AMMO BOX EMPTY");if(S.NoticeUntil>W->GetTimeSeconds())return S.Notice;auto* P=UGameplayStatics::GetPlayerCharacter(W,0);for(const auto& T:S.Traps)if(T.Discovered&&T.State==TEXT("Armed")&&P&&FVector::Dist2D(P->GetActorLocation(),T.Position)<450)return TEXT("ENEMY MINE NEARBY  /  WATCH THE GROUND");return FString();}
float HudProgress(UWorld* W){return float(Session(W).DisarmClock/2.);}
TArray<TPair<FVector,float>> MineHints(UWorld* W){TArray<TPair<FVector,float>> H;auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!P||Dead(P))return H;auto& S=Session(W);for(const auto& T:S.Traps)if(T.Discovered&&T.State==TEXT("Armed")&&VisiblePoint(W,P,T.Position+FVector(0,0,10),800,0))H.Emplace(T.Position+FVector(0,0,15),float(FVector::Dist2D(P->GetActorLocation(),T.Position)/100));return H;}
void PreTick(UWorld* W,ELevelTick,float){auto* Existing=Sessions.Find(W);if(Existing&&!(*Existing)->Clouds.IsEmpty())SmokeTick(W,**Existing,0);}
void Initialize(){FParse::Value(FCommandLine::Get(),TEXT("ParisEquipmentCheck="),CheckMode);FParse::Value(FCommandLine::Get(),TEXT("ParisEquipmentOut="),CheckOut);FString Prefix;if(!FParse::Value(FCommandLine::Get(),TEXT("ParisSavePrefix="),Prefix))FCommandLine::Append(TEXT(" -ParisSavePrefix=ParisEquipmentV1"));TickHandle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);PreTickHandle=FWorldDelegates::OnWorldPreActorTick.AddStatic(&PreTick);CleanupHandle=FWorldDelegates::OnWorldCleanup.AddStatic(&Cleanup);}
void Shutdown(){FWorldDelegates::OnWorldPostActorTick.Remove(TickHandle);FWorldDelegates::OnWorldPreActorTick.Remove(PreTickHandle);FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);Sessions.Empty();}
}
void UParisEquipmentSightBridge::Seen(APawn* Pawn){if(Sensor.IsValid()&&Pawn&&!ParisTacticalEquipment::Occluded(Pawn->GetWorld(),Sensor->GetSensorLocation(),Pawn->GetActorLocation()))Original.Broadcast(Pawn);}
