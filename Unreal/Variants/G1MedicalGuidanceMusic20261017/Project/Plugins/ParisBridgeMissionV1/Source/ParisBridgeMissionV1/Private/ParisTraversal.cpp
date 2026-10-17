#include "ParisTraversal.h"
#include "ParisBridgeMission.h"
#include "ParisCombatUI.h"
#include "ParisEquipmentState.h"
#include "ParisTacticalEquipment.h"
#include "ParisPlayerDeath.h"
#include "ParisFirstPersonApprovedActor.h"
#include "ParisActionBindings.h"
#include "Camera/PlayerCameraManager.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/Skeleton.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/UnrealType.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "ParisTraversalCurve.inl"

namespace ParisTraversal {
namespace {
double Num(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!P)return -999;const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));}
bool Flag(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),K):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
FName Name(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr;return P?P->GetPropertyValue_InContainer(O):NAME_None;}
void PutName(UObject* O,const TCHAR* K,FName V){if(auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr)P->SetPropertyValue_InContainer(O,V);}
void Invoke(UObject* O,const TCHAR* N){if(O)if(auto* F=O->FindFunction(N))O->ProcessEvent(F,nullptr);}
UObject* Obj(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FObjectPropertyBase>(O->GetClass(),K):nullptr;return P?P->GetObjectPropertyValue_InContainer(O):nullptr;}
struct FState {
 TWeakObjectPtr<ACharacter> Player;TWeakObjectPtr<AParisBridgePlayerController> PC;
 TWeakObjectPtr<UAnimSequence> Clip;TWeakObjectPtr<UClass> AnimClass;TWeakObjectPtr<AActor> Box;
 TWeakObjectPtr<ACameraActor> Camera;TWeakObjectPtr<AActor> OldView;
 TWeakObjectPtr<UCameraComponent> PawnCamera;FTransform OriginalCamera;FVector CameraHeadOffset;
 TWeakObjectPtr<AActor> Gun,Display;bool OldBodyHidden=false,OldOwnerNoSee=false,OldGunHidden=true,OldDisplayHidden=false;
 bool Running=false,Observer=false,Locks=false,FixtureAttempted=false;double Age=0,Duration=2.1333334442279053,NoticeUntil=0;
 FVector Start,Forward;double Half=0,Radius=0;EMovementMode OldMode=MOVE_Walking;EAnimationMode::Type OldAnimMode=EAnimationMode::AnimationBlueprint;
 FString Generation,Reason=TEXT("NotStarted"),Notice;int32 ObserverSide=0;int32 Starts=0,Completions=0,Cancels=0,Steps=0;double MaxStep=0;
 double Height=0,Depth=0,Front=0,MotionInset=0;int32 SpaceAttempts=0,JumpFallbacks=0;TWeakObjectPtr<UPrimitiveComponent> Obstacle;
 TArray<TSharedPtr<FJsonValue>> Events;
};
TMap<UWorld*,TUniquePtr<FState>> States;FDelegateHandle CleanupHandle;
FState& State(UWorld* W){auto* S=States.Find(W);if(S)return **S;auto P=MakeUnique<FState>();auto& R=*P;States.Add(W,MoveTemp(P));return R;}
TArray<TSharedPtr<FJsonValue>> V(const FVector& X){return {MakeShared<FJsonValueNumber>(X.X),MakeShared<FJsonValueNumber>(X.Y),MakeShared<FJsonValueNumber>(X.Z)};}
FVector Curve(double T){const double I=FMath::Clamp(T/2.1333334442279053*64,0.,64.);const int32 A=FMath::FloorToInt(I),B=FMath::Min(A+1,64);return FMath::Lerp(TraversalRoot[A],TraversalRoot[B],I-A);}
FVector Point(const FState& S,double T){auto R=Curve(T);
 // The native motion expects a roughly100cm front distance. A close approach
 // keeps the initial lift in place, then rejoins the same obstacle-relative
 // motion. This avoids backing up, teleporting, or pushing the capsule into
 // the box while the original animation is still below its top.
 if(S.MotionInset>.01){const double X=FMath::Max(0.,R.Y-S.MotionInset),B=FMath::Clamp(X/12.,0.,1.);R.Y=X*B*B*(3-2*B);}
 const double A=FMath::Clamp((T-1.25)/.65,0.,1.);R.Z-=TraversalRoot[64].Z*A*A*(3-2*A);return S.Start+S.Forward*R.Y+FVector::UpVector*R.Z;}
FCollisionQueryParams Query(ACharacter* P){return FCollisionQueryParams(SCENE_QUERY_STAT(ParisTraversal),false,P);}
bool Occupied(UWorld* W,ACharacter* P,const FVector& At,double RR,double HH){TArray<FOverlapResult> Hits;W->OverlapMultiByObjectType(Hits,At,P->GetActorQuat(),FCollisionObjectQueryParams(ECC_Pawn),FCollisionShape::MakeCapsule(RR,HH),Query(P));for(const auto& H:Hits)if(Cast<APawn>(H.GetActor()))return true;return false;}
void Event(UWorld* W,FState& S,const FString& Kind,const FString& Detail){auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("time"),W->GetTimeSeconds());O->SetStringField(TEXT("kind"),Kind);O->SetStringField(TEXT("detail"),Detail);S.Events.Add(MakeShared<FJsonValueObject>(O));UE_LOG(LogTemp,Display,TEXT("PARIS_TRAVERSAL %s %s"),*Kind,*Detail);}
bool Ground(UWorld* W,ACharacter* P,FVector At,double Range,FHitResult& H){auto Q=Query(P);return W->LineTraceSingleByChannel(H,At+FVector(0,0,25),At-FVector(0,0,Range),ECC_Visibility,Q)&&H.ImpactNormal.Z>=.95;}
bool Support(UWorld* W,ACharacter* P,const FVector& Feet,double Radius,FString& Why){
 for(int32 I=0;I<9;++I){const double A=(I-1)*PI*.25;const FVector Offset=I?FVector(FMath::Cos(A),FMath::Sin(A),0)*Radius*.9:FVector::ZeroVector;FHitResult H;
  if(!Ground(W,P,Feet+Offset,25,H)||FMath::Abs(H.ImpactPoint.Z-Feet.Z)>12){Why=TEXT("Landing footprint lacks level support");return false;}}
 return true;
}
bool Plan(AParisBridgePlayerController* PC,FState& S,bool& Nearby,FString& Why){
 auto* P=Cast<ACharacter>(PC->GetPawn());auto* W=PC->GetWorld();if(!P){Why=TEXT("Player absent");return false;}
 const double HH=P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight(),RR=P->GetCapsuleComponent()->GetScaledCapsuleRadius();const FVector Feet=P->GetActorLocation()-FVector(0,0,HH),F=P->GetActorForwardVector().GetSafeNormal2D();auto Q=Query(P);FHitResult Front;
 Nearby=W->LineTraceSingleByChannel(Front,Feet+FVector(0,0,40),Feet+F*180+FVector(0,0,40),ECC_Visibility,Q);
 if(!Nearby){Why=TEXT("No low obstacle; ordinary jump");return false;}
 if(Flag(P,TEXT("IsDead"))||Num(P,TEXT("DesiredPosture"))!=0||P->bIsCrouched||!P->GetCharacterMovement()->IsMovingOnGround()){Why=TEXT("Stand on the ground to vault");return false;}
 if(Name(P,TEXT("ActionState"))!=TEXT("Ready")||ParisTacticalEquipment::Session(W).SelectedSlot!=0||!ParisTacticalEquipment::Session(W).ThrowKind.IsEmpty()){Why=TEXT("Finish action and select rifle before vaulting");return false;}
 if(PC->IsInputKeyDown(EKeys::LeftMouseButton)||PC->IsInputKeyDown(EKeys::RightMouseButton)){Why=TEXT("Release fire/aim before vaulting");return false;}
 bool DisplayReady=false;for(TActorIterator<AParisFirstPersonApprovedActor> I(W);I;++I)if(I->GetOwner()==P&&I->Initialized){DisplayReady=true;break;}
 if(!DisplayReady){Why=TEXT("First person display preparing");return false;}
 if(!Support(W,P,Feet,RR,Why)){Why=TEXT("Starting footprint lacks level support");return false;}
 const double Distance=FVector::DotProduct(Front.ImpactPoint-Feet,F);
 const double Facing=FVector::DotProduct(Front.ImpactNormal,F);
 if(Distance<RR-4||Distance>112){Why=FString::Printf(TEXT("Obstacle distance %.1f cm; approach within %.0f-112 cm"),Distance,RR-4);return false;}
 if(Facing>-.8){Why=FString::Printf(TEXT("Face the obstacle more directly (alignment %.3f)"),-Facing);return false;}
 FHitResult Top;const FVector Sample=Feet+F*(Distance+5);
 if(!W->LineTraceSingleByChannel(Top,Sample+FVector(0,0,160),Sample+FVector(0,0,30),ECC_Visibility,Q)||Top.GetComponent()!=Front.GetComponent()||Top.ImpactNormal.Z<.98){Why=TEXT("Obstacle needs a clear flat top");return false;}
 const double H=Top.ImpactPoint.Z-Feet.Z;if(H<90||H>105){Why=TEXT("Supported obstacle height: 90-105 cm");return false;}
 double D=0;for(double X=5;X<=115;X+=2){FHitResult T;const FVector A=Feet+F*(Distance+X);const bool Hit=W->LineTraceSingleByChannel(T,A+FVector(0,0,160),A+FVector(0,0,30),ECC_Visibility,Q);
  if(!Hit||T.GetComponent()!=Top.GetComponent()){D=X;break;}if(T.ImpactNormal.Z<.98||FMath::Abs(T.ImpactPoint.Z-Top.ImpactPoint.Z)>2){Why=TEXT("Top surface is not a stable level plane");return false;}}
 if(D<50||D>85){Why=TEXT("Supported obstacle depth: 50-85 cm");return false;}
 const FVector Right=FVector::CrossProduct(FVector::UpVector,F);for(int32 Side:{-1,1}){FHitResult T;const FVector A=Feet+F*(Distance+D*.5)+Right*(RR+12)*Side;
  if(!W->LineTraceSingleByChannel(T,A+FVector(0,0,160),A+FVector(0,0,30),ECC_Visibility,Q)||T.GetComponent()!=Top.GetComponent()||T.ImpactNormal.Z<.98){Why=TEXT("Obstacle too narrow for the original capsule");return false;}}
 S.Start=P->GetActorLocation();S.Forward=F;S.Half=HH;S.Radius=RR;S.Front=Distance;S.Height=H;S.Depth=D;S.MotionInset=FMath::Max(0.,100.-Distance);S.Obstacle=Top.GetComponent();
 const FVector End=Point(S,S.Duration),EndFeet=End-FVector(0,0,HH);
 if(Occupied(W,P,End,RR,HH)){Why=TEXT("Landing occupied by another pawn");return false;}
 if(!Support(W,P,EndFeet,RR,Why))return false;
 FVector Prev=S.Start;const auto Shape=FCollisionShape::MakeCapsule(RR,HH);const auto Profile=P->GetCapsuleComponent()->GetCollisionProfileName();
 for(int32 I=1;I<=128;++I){const FVector Next=Point(S,S.Duration*I/128.);FHitResult Hit;
  if(W->SweepSingleByProfile(Hit,Prev,Next,P->GetActorQuat(),Profile,Shape,Q)||W->OverlapBlockingTestByProfile(Next,P->GetActorQuat(),Profile,Shape,Q)||Occupied(W,P,Next,RR,HH)){Why=TEXT("Full capsule path blocked or overhead clearance insufficient");return false;}Prev=Next;}
 return true;
}
void Finish(UWorld* W,FState& S,bool Completed,const FString& Why){
 auto* P=S.Player.Get();auto* PC=S.PC.Get();S.Running=false;S.Reason=Why;if(Completed)++S.Completions;else ++S.Cancels;
 if(S.PawnCamera.IsValid())S.PawnCamera->SetRelativeTransform(S.OriginalCamera);S.PawnCamera.Reset();
 if(P&&!Flag(P,TEXT("IsDead"))){
  auto* Move=P->GetCharacterMovement();Move->StopMovementImmediately();Move->SetMovementMode(Completed?S.OldMode:MOVE_Falling);P->StopJumping();
  P->GetMesh()->SetAnimationMode(S.OldAnimMode);if(S.OldAnimMode==EAnimationMode::AnimationBlueprint&&S.AnimClass.IsValid())P->GetMesh()->SetAnimInstanceClass(S.AnimClass.Get());
  if(Name(P,TEXT("ActionState"))==TEXT("Vaulting"))PutName(P,TEXT("ActionState"),TEXT("Ready"));PutName(P,TEXT("ActivePose"),NAME_None);Invoke(P,TEXT("PC_UpdateActionPose"));
 }
 if(PC&&S.Locks){PC->SetIgnoreMoveInput(false);PC->SetIgnoreLookInput(false);}S.Locks=false;
 Event(W,S,Completed?TEXT("complete"):TEXT("cancel"),Why);
}
void Observe(UWorld* W,FState& S){
 if(!S.Observer)return;auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));if(!P||!PC||!S.Camera.IsValid())return;
 ParisActionBindings::SetObserver(P,true);
 const FVector Feet=(P->GetMesh()->GetSocketLocation(TEXT("foot_l"))+P->GetMesh()->GetSocketLocation(TEXT("foot_r")))*.5;const FVector Aim=(P->GetMesh()->GetSocketLocation(TEXT("head"))+Feet)*.5;// Keep a readable body view near a wall. Prefer the current side while
 // it has room; otherwise choose a clear side with a real camera sphere sweep.
 const FVector Offsets[]={FVector(-320,180,120),FVector(-320,-180,120),FVector(40,-370,120),FVector(40,370,120),FVector(350,60,120)};
 auto Q=Query(P);for(TActorIterator<AActor> I(W);I;++I)if(I->ActorHasTag(TEXT("ParisUnifiedPerspectiveDisplay"))||I->ActorHasTag(TEXT("ParisEquipmentOwned")))Q.AddIgnoredActor(*I);if(S.Gun.IsValid())Q.AddIgnoredActor(S.Gun.Get());if(S.Display.IsValid())Q.AddIgnoredActor(S.Display.Get());
 FVector At;double Best=-1;int32 Side=S.ObserverSide;
 for(int32 N=0;N<5;++N){const int32 I=(S.ObserverSide+N)%5;const FVector Desired=Aim+P->GetActorTransform().TransformVectorNoScale(Offsets[I]);FHitResult H;FVector Candidate=Desired;
  if(W->SweepSingleByChannel(H,Aim,Desired,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(12),Q))Candidate=H.bStartPenetrating?Aim:H.Location+H.ImpactNormal*2;
  const double Distance=FVector::Distance(Aim,Candidate);if(Distance>Best){Best=Distance;At=Candidate;Side=I;}if(Distance>=270)break;
 }
 const bool Cut=Side!=S.ObserverSide;S.ObserverSide=Side;
 S.Camera->SetActorLocation(At);S.Camera->SetActorRotation((Aim-At).Rotation());
 if(Cut&&PC->PlayerCameraManager)PC->PlayerCameraManager->SetGameCameraCutThisFrame();
}
void SetupFixture(UWorld* W,FState& S){
 if(S.FixtureAttempted)return;auto* M=AParisBridgeMission::Find(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!M||!P||M->Phase==TEXT("Preparing"))return;S.FixtureAttempted=true;
 auto* Mesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/WW2City/Environment/Mesh/Props/SM_Crate_01a.SM_Crate_01a"));if(!Mesh){Event(W,S,TEXT("fixture_missing"),TEXT("Original crate is not in cooked content"));return;}
 const FVector Proposed(6287.5,-20487.5,110.);FHitResult H;FString Why;if(!Ground(W,P,Proposed,80,H)||!Support(W,P,H.ImpactPoint,90,Why)){Event(W,S,TEXT("fixture_rejected"),TEXT("Practice site lacks native ground support"));return;}
 double BaseZ=H.ImpactPoint.Z,MinZ=BaseZ;for(int32 X:{-1,1})for(int32 Y:{-1,1}){FHitResult Corner;if(!Ground(W,P,H.ImpactPoint+FVector(35*X,75*Y,0),25,Corner)){Event(W,S,TEXT("fixture_rejected"),TEXT("Crate base corner unsupported"));return;}BaseZ=FMath::Max(BaseZ,Corner.ImpactPoint.Z);MinZ=FMath::Min(MinZ,Corner.ImpactPoint.Z);}if(BaseZ-MinZ>2){Event(W,S,TEXT("fixture_rejected"),TEXT("Rigid crate foundation height spread exceeds2cm"));return;}BaseZ+=.02;
 auto* Box=W->SpawnActor<AStaticMeshActor>();Box->Tags.Add(TEXT("ParisTraversalPracticeFixture"));auto* C=Box->GetStaticMeshComponent();C->SetMobility(EComponentMobility::Movable);C->SetStaticMesh(Mesh);C->SetCollisionProfileName(TEXT("BlockAll"));C->SetCanEverAffectNavigation(false);
 const auto B=Mesh->GetBounds();const FVector Scale(70/(2*B.BoxExtent.X),150/(2*B.BoxExtent.Y),100/(2*B.BoxExtent.Z));Box->SetActorScale3D(Scale);
 const FVector Center(H.ImpactPoint.X,H.ImpactPoint.Y,BaseZ+50);Box->SetActorLocation(Center-B.Origin*Scale);Box->SetActorRotation(FRotator::ZeroRotator);
 auto Q=Query(P);Q.AddIgnoredActor(Box);FVector Origin,Extent;Box->GetActorBounds(false,Origin,Extent);if(W->OverlapBlockingTestByChannel(Origin,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeBox(Extent-FVector(.5)),Q)){Box->Destroy();Event(W,S,TEXT("fixture_rejected"),TEXT("Practice crate overlaps another blocking actor"));return;}
 S.Box=Box;Event(W,S,TEXT("fixture"),FString::Printf(TEXT("original=SM_Crate_01a scale=%s actual=%s ground=%s"),*Scale.ToString(),*(Extent*2).ToString(),*H.GetActor()->GetPathName()));
}
void Cleanup(UWorld* W,bool,bool){States.Remove(W);}
}
bool Active(const ACharacter* P){auto* S=P?States.Find(P->GetWorld()):nullptr;return S&&(*S)->Running&&(*S)->Player.Get()==P;}
AActor* Fixture(UWorld* W){return State(W).Box.Get();}
bool Request(AParisBridgePlayerController* PC,FString& Why){
 auto* M=AParisBridgeMission::Find(PC);if(!M||(!M->AllowsPlay()&&M->Phase!=TEXT("Won"))||M->CheckpointDialogVisible()||ParisCombatUI::IsOpen(PC)){Why=TEXT("Gameplay input unavailable");return false;}
 auto* W=PC->GetWorld();auto& S=State(W);if(S.Running){Why=TEXT("Already vaulting");return false;}bool Nearby=false;if(!Plan(PC,S,Nearby,Why)){S.Notice=Why;S.NoticeUntil=W->GetTimeSeconds()+3;Event(W,S,TEXT("reject"),Why);return false;}
 auto* P=Cast<ACharacter>(PC->GetPawn());auto* Clip=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Vault_1m.Rifle_Vault_1m"));
 if(!Clip||!Clip->GetSkeleton()->IsCompatibleMesh(P->GetMesh()->GetSkeletalMeshAsset())){Why=TEXT("Current native Vault clip missing or incompatible");S.Notice=Why;S.NoticeUntil=W->GetTimeSeconds()+3;Event(W,S,TEXT("reject"),Why);return false;}
 S.Player=P;S.PC=PC;S.Clip=Clip;S.Duration=Clip->GetPlayLength();S.Age=0;S.OldMode=P->GetCharacterMovement()->MovementMode;S.OldAnimMode=P->GetMesh()->GetAnimationMode();S.AnimClass=P->GetMesh()->GetAnimClass();S.Generation=M->RunGeneration;S.Running=true;++S.Starts;S.Reason=TEXT("Vaulting");
 S.PawnCamera=Cast<UCameraComponent>(Obj(P,TEXT("ParisPlayerCamera")));if(S.PawnCamera.IsValid()){S.OriginalCamera=S.PawnCamera->GetRelativeTransform();S.CameraHeadOffset=P->GetActorTransform().InverseTransformVector(S.PawnCamera->GetComponentLocation()-P->GetMesh()->GetSocketLocation(TEXT("head")));}
 P->StopJumping();P->ConsumeMovementInputVector();P->GetCharacterMovement()->StopMovementImmediately();P->GetCharacterMovement()->SetMovementMode(MOVE_Flying);PutName(P,TEXT("ActionState"),TEXT("Vaulting"));P->GetMesh()->PlayAnimation(Clip,false);
 PC->SetIgnoreMoveInput(true);PC->SetIgnoreLookInput(true);S.Locks=true;Event(W,S,TEXT("start"),FString::Printf(TEXT("height=%.4f depth=%.4f front=%.4f inset=%.4f original_capsule=%.4f/%.4f native=%s"),S.Height,S.Depth,S.Front,S.MotionInset,S.Radius,S.Half,*Clip->GetPathName()));return true;
}
bool Input(AParisBridgePlayerController* PC,const FInputKeyEventArgs& K){
 auto* W=PC->GetWorld();auto& S=State(W);if(K.Key==EKeys::V&&K.Event==IE_Pressed){SetObserver(PC,!S.Observer);return true;}
 if(S.Running){if(K.Key==EKeys::SpaceBar)return true;if(K.Event==IE_Released)return false;return K.Key==EKeys::LeftMouseButton||K.Key==EKeys::RightMouseButton||K.Key==EKeys::R||K.Key==EKeys::LeftControl||K.Key==EKeys::RightControl||K.Key==EKeys::Z||K.Key==EKeys::MouseScrollUp||K.Key==EKeys::MouseScrollDown||K.Key==EKeys::E;}
 if(K.Key!=EKeys::SpaceBar||K.Event!=IE_Pressed)return false;auto* P=Cast<ACharacter>(PC->GetPawn());if(!P)return false;const FVector Feet=P->GetNavAgentLocation();FHitResult H;auto Q=Query(P);if(!W->LineTraceSingleByChannel(H,Feet+FVector(0,0,40),Feet+P->GetActorForwardVector()*180+FVector(0,0,40),ECC_Visibility,Q))return false;
 ++S.SpaceAttempts;FString Why;if(Request(PC,Why))return true;
 ++S.JumpFallbacks;Event(W,S,TEXT("jump_fallback"),Why);return false;
}
void RefreshObserver(UWorld* W){if(W)if(auto* S=States.Find(W))Observe(W,**S);}
void SetObserver(AParisBridgePlayerController* PC,bool Value){
 auto* W=PC->GetWorld();auto& S=State(W);if(S.Observer==Value)return;auto* P=Cast<ACharacter>(PC->GetPawn());if(!P)return;
 if(Value){S.OldView=PC->GetViewTarget();S.OldBodyHidden=P->GetMesh()->bHiddenInGame;S.OldOwnerNoSee=P->GetMesh()->bOwnerNoSee;S.Gun=Cast<AActor>(Obj(P,TEXT("WeaponAppearance")));if(S.Gun.IsValid()){S.OldGunHidden=S.Gun->IsHidden();}
  for(TActorIterator<AParisFirstPersonApprovedActor> I(W);I;++I)if(I->GetOwner()==P&&I->Initialized){S.Display=*I;S.OldDisplayHidden=I->IsHidden();break;}
  S.ObserverSide=0;S.Camera=W->SpawnActor<ACameraActor>();S.Camera->SetOwner(P);S.Camera->GetCameraComponent()->SetFieldOfView(75);S.Observer=true;Observe(W,S);PC->SetViewTarget(S.Camera.Get());if(PC->PlayerCameraManager)PC->PlayerCameraManager->SetGameCameraCutThisFrame();
 }else{if(PC->GetViewTarget()==S.Camera.Get()){if(S.OldView.IsValid())PC->SetViewTarget(S.OldView.Get());else PC->SetViewTarget(P);}if(!Flag(P,TEXT("IsDead"))){P->GetMesh()->SetHiddenInGame(S.OldBodyHidden);P->GetMesh()->SetOwnerNoSee(S.OldOwnerNoSee);if(S.Gun.IsValid())S.Gun->SetActorHiddenInGame(true);if(S.Display.IsValid())S.Display->SetActorHiddenInGame(S.OldDisplayHidden);}ParisActionBindings::SetObserver(P,false);if(S.Camera.IsValid())S.Camera->Destroy();S.Camera.Reset();S.Observer=false;}
 Event(W,S,TEXT("observer"),Value?TEXT("third_person_original_body_and_gun"):TEXT("first_person_original_camera"));
}
void Tick(UWorld* W,float DT){
 auto& S=State(W);SetupFixture(W,S);auto* P=S.Player.Get();auto* M=AParisBridgeMission::Find(W);
 if(S.Observer&&(ParisPlayerDeath::Presenting(W)||!M||M->Phase==TEXT("Ready")))if(auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0)))SetObserver(PC,false);
 if(S.Running){
  if(!P||!M||S.Generation!=M->RunGeneration||Flag(P,TEXT("IsDead"))||M->Phase==TEXT("Lost")||M->Phase==TEXT("Ready")){Finish(W,S,false,TEXT("Original lifecycle interrupted vault"));return;}
  if(W->IsPaused()||DT<=0)return;P->ConsumeMovementInputVector();auto* Move=P->GetCharacterMovement();Move->StopMovementImmediately();
  const double BeginAge=S.Age,NextAge=FMath::Min(S.Duration,S.Age+FMath::Min(double(DT),.05));const int32 Count=FMath::Max(1,FMath::CeilToInt((NextAge-BeginAge)*120));auto Q=Query(P);
  for(int32 I=1;I<=Count;++I){const double Age=FMath::Lerp(BeginAge,NextAge,double(I)/Count);const FVector Next=Point(S,Age),Before=P->GetActorLocation();FHitResult Check;
   if(W->SweepSingleByProfile(Check,Before,Next,P->GetActorQuat(),P->GetCapsuleComponent()->GetCollisionProfileName(),FCollisionShape::MakeCapsule(S.Radius,S.Half),Q)||Occupied(W,P,Next,S.Radius,S.Half)){Finish(W,S,false,TEXT("Dynamic blocker stopped full capsule sweep"));return;}
   FHitResult Hit;Move->MoveUpdatedComponent(Next-Before,P->GetActorQuat(),true,&Hit,ETeleportType::None);S.MaxStep=FMath::Max(S.MaxStep,FVector::Distance(Before,P->GetActorLocation()));++S.Steps;
   if(Hit.bBlockingHit||FVector::Distance(P->GetActorLocation(),Next)>.05){Finish(W,S,false,TEXT("Actual swept movement was blocked"));return;}S.Age=Age;
  }
  PutName(P,TEXT("ActionState"),TEXT("Vaulting"));if(auto* A=P->GetMesh()->GetSingleNodeInstance()){A->SetPosition(S.Age,false);A->SetPlaying(false);}else{Finish(W,S,false,TEXT("Original body motion source lost"));return;}
  if(S.PawnCamera.IsValid()){auto* C=S.PawnCamera.Get();auto* Parent=C->GetAttachParent();if(Parent){const FVector Base=Parent->GetComponentTransform().TransformPosition(S.OriginalCamera.GetLocation());const FVector Head=P->GetMesh()->GetSocketLocation(TEXT("head"))+P->GetActorTransform().TransformVector(S.CameraHeadOffset);const double In=FMath::Clamp(S.Age/.2,0.,1.),Out=FMath::Clamp((S.Duration-S.Age)/.25,0.,1.);C->SetWorldLocation(FMath::Lerp(Base,Head,In*In*(3-2*In)*Out*Out*(3-2*Out)));}}
  if(S.Age>=S.Duration){FString Why;if(!Support(W,P,P->GetActorLocation()-FVector(0,0,S.Half),S.Radius,Why))Finish(W,S,false,Why);else Finish(W,S,true,TEXT("Swept native trajectory and supported landing complete"));}
 }
 Observe(W,S);
}
FString Hint(UWorld* W){auto& S=State(W);if(S.Running)return TEXT("VAULTING  /  V VIEW");if(W->GetTimeSeconds()<S.NoticeUntil)return S.Notice;return TEXT("LOW OBSTACLE TRIAL  /  FACE CRATE + SPACE  /  V VIEW");}
FString Inspect(UWorld* W){auto& S=State(W);auto O=MakeShared<FJsonObject>();O->SetBoolField(TEXT("active"),S.Running);O->SetBoolField(TEXT("observer"),S.Observer);O->SetStringField(TEXT("reason"),S.Reason);O->SetNumberField(TEXT("age"),S.Age);O->SetNumberField(TEXT("starts"),S.Starts);O->SetNumberField(TEXT("completions"),S.Completions);O->SetNumberField(TEXT("cancels"),S.Cancels);O->SetNumberField(TEXT("steps"),S.Steps);O->SetNumberField(TEXT("max_step_cm"),S.MaxStep);O->SetNumberField(TEXT("height_cm"),S.Height);O->SetNumberField(TEXT("depth_cm"),S.Depth);O->SetNumberField(TEXT("front_cm"),S.Front);O->SetNumberField(TEXT("motion_inset_cm"),S.MotionInset);O->SetNumberField(TEXT("space_attempts"),S.SpaceAttempts);O->SetNumberField(TEXT("jump_fallbacks"),S.JumpFallbacks);O->SetNumberField(TEXT("original_capsule_radius"),S.Radius);O->SetNumberField(TEXT("original_capsule_half"),S.Half);O->SetArrayField(TEXT("start"),V(S.Start));O->SetArrayField(TEXT("events"),S.Events);if(S.Box.IsValid()){FVector B,E;S.Box->GetActorBounds(false,B,E);O->SetArrayField(TEXT("fixture_center"),V(B));O->SetArrayField(TEXT("fixture_dimensions"),V(E*2));O->SetStringField(TEXT("fixture"),S.Box->GetPathName());}FString J;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&J));return J;}
void Initialize(){CleanupHandle=FWorldDelegates::OnWorldCleanup.AddStatic(&Cleanup);}
void Shutdown(){if(CleanupHandle.IsValid())FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);States.Empty();}
}
