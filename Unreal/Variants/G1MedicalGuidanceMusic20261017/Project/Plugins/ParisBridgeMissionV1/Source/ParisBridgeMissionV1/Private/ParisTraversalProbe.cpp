#include "ParisTraversalProbe.h"
#include "ParisTraversal.h"
#include "ParisBridgeMission.h"
#include "ParisTacticalEquipment.h"
#include "ParisEquipmentState.h"
#include "ParisCombatUI.h"
#include "ParisPlayerDeath.h"
#include "Camera/CameraComponent.h"
#include "Misc/CoreDelegates.h"
#include "UObject/StructOnScope.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/BoxComponent.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "AIController.h"
#include "BrainComponent.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "UObject/UnrealType.h"
#include "Serialization/JsonSerializer.h"
#include "UnrealClient.h"

namespace ParisTraversalProbe {
namespace {
FDelegateHandle Handle,WallHandle;TWeakObjectPtr<UWorld> ProbeWorld;double PauseWall=0,PauseAge=0;FVector PausePosition;FDelegateHandle Unused;FString Mode,Out,Stage=TEXT("boot");double Clock=0,BeforeSum=0,Shot=0;int32 Step=0,Images=0;bool Finished=false;
FTransform InitialCamera;float InitialFOV=90;bool InitialControlRotation=false;bool CameraCaptured=false;FVector Start;TWeakObjectPtr<AActor> Blocker;TArray<TSharedPtr<FJsonValue>> Samples,Assertions;TSharedPtr<FJsonObject> Root;
bool InputW=false,InputReleased=false;FVector InputOrigin,InputStopped;double ContactStable=0,InputFallbackBefore=0;TArray<TSharedPtr<FJsonValue>> InputCases;
void HoldBrains(UWorld* W){for(TActorIterator<AAIController> I(W);I;++I){auto* F=I->FindFunction(TEXT("PC_EnableCombat"));if(F){FStructOnScope V(F);if(auto* B=FindFProperty<FBoolProperty>(F,TEXT("Enabled")))B->SetPropertyValue_InContainer(V.GetStructMemory(),false);I->ProcessEvent(F,V.GetStructMemory());}I->StopMovement();if(I->GetBrainComponent())I->GetBrainComponent()->PauseLogic(TEXT("Explicit traversal fixture isolation including original combat schedule"));}}
UCameraComponent* Camera(ACharacter* P){const auto* F=FindFProperty<FObjectPropertyBase>(P->GetClass(),TEXT("ParisPlayerCamera"));return F?Cast<UCameraComponent>(F->GetObjectPropertyValue_InContainer(P)):nullptr;}
double Age(UWorld* W){TSharedPtr<FJsonObject> O;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(ParisTraversal::Inspect(W)),O);return O->GetNumberField(TEXT("age"));}
double Num(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!P)return -999;const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V));}
bool Flag(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),K):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
FName Name(const UObject* O,const TCHAR* K){const auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),K):nullptr;return P?P->GetPropertyValue_InContainer(O):NAME_None;}
TArray<TSharedPtr<FJsonValue>> V(const FVector& X){return {MakeShared<FJsonValueNumber>(X.X),MakeShared<FJsonValueNumber>(X.Y),MakeShared<FJsonValueNumber>(X.Z)};}
void Finish(UWorld* W,bool Pass,const FString& Why){if(Finished)return;Finished=true;Root->SetStringField(TEXT("status"),Pass?TEXT("pass_native_traversal_")+Mode:TEXT("failed_traversal_")+Mode);Root->SetStringField(TEXT("reason"),Why);Root->SetStringField(TEXT("scope"),TEXT("Original actual player in current cooked city; explicit relocated start, original-mesh scaled fixture, NPC brains paused for isolation. Not natural combat/map-wide acceptance."));Root->SetStringField(TEXT("traversal"),ParisTraversal::Inspect(W));Root->SetArrayField(TEXT("assertions"),Assertions);Root->SetArrayField(TEXT("samples"),Samples);if(Mode==TEXT("input"))Root->SetArrayField(TEXT("input_cases"),InputCases);FString J;FJsonSerializer::Serialize(Root.ToSharedRef(),TJsonWriterFactory<>::Create(&J));FFileHelper::SaveStringToFile(J,*(Out/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);FPlatformMisc::RequestExit(false);}
bool Check(UWorld* W,bool Good,const FString& Why){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("check"),Why);O->SetBoolField(TEXT("pass"),Good);Assertions.Add(MakeShared<FJsonValueObject>(O));if(!Good)Finish(W,false,Why);return Good;}
void Image(const FString& Tag){FScreenshotRequest::RequestScreenshot(Out/(Tag+TEXT(".png")),false,false);}
void Tap(AParisBridgePlayerController* PC,FKey K){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Released,0));}
void Reset(UWorld* W,ACharacter* P,AParisBridgePlayerController* PC){auto* B=ParisTraversal::Fixture(W);FVector O,E;B->GetActorBounds(false,O,E);const double HH=P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();Start=FVector(O.X-E.X-100,O.Y,O.Z-E.Z+HH+2);P->SetActorLocation(Start,false);P->SetActorRotation(FRotator::ZeroRotator);PC->SetControlRotation(FRotator::ZeroRotator);P->GetCharacterMovement()->SetMovementMode(MOVE_Walking);P->GetCharacterMovement()->StopMovementImmediately();Root->SetArrayField(TEXT("relocated_fixture_start"),V(Start));}
AActor* Cube(UWorld* W,FVector At,FVector Size){auto* A=W->SpawnActor<AStaticMeshActor>();auto* C=A->GetStaticMeshComponent();C->SetMobility(EComponentMobility::Movable);auto* Mesh=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/WW2City/Environment/Mesh/Props/SM_Crate_01a.SM_Crate_01a"));check(Mesh);C->SetStaticMesh(Mesh);C->SetCollisionProfileName(TEXT("BlockAll"));C->SetCanEverAffectNavigation(false);const auto B=Mesh->GetBounds();const FVector Scale=Size/(B.BoxExtent*2);A->SetActorScale3D(Scale);A->SetActorLocation(At-B.Origin*Scale);A->Tags.Add(TEXT("ParisTraversalNegativeFixture"));return A;}

void Sample(UWorld* W,ACharacter* P){auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("time"),W->GetTimeSeconds());O->SetStringField(TEXT("stage"),Stage);O->SetArrayField(TEXT("location"),V(P->GetActorLocation()));O->SetStringField(TEXT("action"),Name(P,TEXT("ActionState")).ToString());O->SetNumberField(TEXT("mode"),P->GetCharacterMovement()->MovementMode);O->SetNumberField(TEXT("capsule_half"),P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());O->SetNumberField(TEXT("capsule_radius"),P->GetCapsuleComponent()->GetScaledCapsuleRadius());O->SetNumberField(TEXT("health"),Num(P,TEXT("Health")));O->SetNumberField(TEXT("loaded"),Num(P,TEXT("LoadedAmmo")));O->SetNumberField(TEXT("reserve"),Num(P,TEXT("ReserveAmmo")));O->SetNumberField(TEXT("shots"),Num(P,TEXT("ShotSequence")));O->SetStringField(TEXT("traversal"),ParisTraversal::Inspect(W));
 auto Bones=MakeShared<FJsonObject>();for(const TCHAR* N:{TEXT("foot_l"),TEXT("foot_r"),TEXT("hand_l"),TEXT("hand_r"),TEXT("head"),TEXT("pelvis")})Bones->SetArrayField(N,V(P->GetMesh()->GetSocketLocation(N)));O->SetObjectField(TEXT("actual_body_bones"),Bones);if(auto* A=P->GetMesh()->GetSingleNodeInstance())O->SetNumberField(TEXT("body_clip_time"),A->GetCurrentTime());Samples.Add(MakeShared<FJsonValueObject>(O));}
const TCHAR* InputLabel(){const TCHAR* Names[]={TEXT("center_contact_tp"),TEXT("left_offset_contact_fp"),TEXT("right_offset_contact_fp"),TEXT("original_100cm"),TEXT("reverse_surface_jump"),TEXT("angled_contact"),TEXT("excess_offset_jump"),TEXT("deep_side_jump"),TEXT("distant_jump")};return Names[Step];}
bool InputExpectsVault(){return Step<6&&Step!=4;}
double InspectNumber(UWorld* W,const TCHAR* Key){TSharedPtr<FJsonObject> O;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(ParisTraversal::Inspect(W)),O);return O->GetNumberField(Key);}
void InputKey(AParisBridgePlayerController* PC,FKey Key,bool Down){PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,Down?IE_Pressed:IE_Released,Down?1:0));}
void SetupInputCase(UWorld* W,AParisBridgePlayerController* PC,ACharacter* P){
 if(Step>=9){Root->SetArrayField(TEXT("input_cases"),InputCases);Finish(W,true,TEXT("Original heldW reaches real crate contact; five centered/offset/100cm/angled vaults complete and four rejected requests fall back to original jump"));return;}
 ParisTraversal::SetObserver(PC,Step==0);auto* B=ParisTraversal::Fixture(W);FVector O,E;B->GetActorBounds(false,O,E);
 const double Yaw=Step==4?180:(Step==5?15:(Step==7?90:0));const FVector F=FRotator(0,Yaw,0).Vector(),Right=FVector::CrossProduct(FVector::UpVector,F);
 const double Offset=Step==1?-15:(Step==2?15:(Step==6?55:0));const double Distance=Step==3?100:(Step==8?150:160);
 const FVector Face=Step==4?FVector(O.X+E.X,O.Y,O.Z-E.Z):(Step==7?FVector(O.X,O.Y-E.Y,O.Z-E.Z):FVector(O.X-E.X,O.Y,O.Z-E.Z));
 FVector Feet=Face-F*Distance+Right*Offset;FHitResult Ground;FCollisionQueryParams Q(SCENE_QUERY_STAT(TraversalInputSetup),false,P);
 if(!Check(W,W->LineTraceSingleByChannel(Ground,Feet+FVector(0,0,25),Feet-FVector(0,0,120),ECC_Visibility,Q)&&Ground.ImpactNormal.Z>.95,TEXT("input_case_setup_has_actual_native_ground")))return;
 Feet.Z=Ground.ImpactPoint.Z;InputOrigin=Feet+FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()+.5);
 P->SetActorLocation(InputOrigin,false);P->SetActorRotation(FRotator(0,Yaw,0));PC->SetControlRotation(FRotator(Step==1?-18:0,Yaw,0));P->GetCharacterMovement()->StopMovementImmediately();P->GetCharacterMovement()->SetMovementMode(MOVE_Walking);P->StopJumping();
 auto Row=MakeShared<FJsonObject>();Row->SetStringField(TEXT("case"),InputLabel());Row->SetArrayField(TEXT("explicit_setup_location"),V(InputOrigin));Row->SetNumberField(TEXT("yaw"),Yaw);Row->SetNumberField(TEXT("offset_cm"),Offset);Row->SetBoolField(TEXT("expects_vault"),InputExpectsVault());InputCases.Add(MakeShared<FJsonValueObject>(Row));
 ContactStable=0;Images=0;InputReleased=false;Clock=0;Stage=TEXT("input_settle");
}
void InputTick(UWorld* W,AParisBridgePlayerController* PC,ACharacter* P,float DT){
 if(Stage==TEXT("settle")&&Clock>.7){SetupInputCase(W,PC,P);return;}
 if(Stage==TEXT("input_settle")&&Clock>.5){
  if(!Check(W,P->GetCharacterMovement()->IsMovingOnGround(),TEXT("original_movement_settled_on_actual_ground")))return;
  if(Step==3||Step==8){InputStopped=P->GetActorLocation();Stage=TEXT("input_trigger");Clock=0;return;}
  InputKey(PC,EKeys::W,true);InputW=true;Stage=TEXT("input_walk");Clock=0;return;
 }
 if(Stage==TEXT("input_walk")){
  if(Clock>8){InputKey(PC,EKeys::W,false);InputW=false;Finish(W,false,TEXT("Original heldW binding did not reach crate contact"));return;}
  const double Advance=FVector::Distance(P->GetActorLocation(),InputOrigin);
  FHitResult Contact;const FVector Feet=P->GetActorLocation()-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()),F=P->GetActorForwardVector().GetSafeNormal2D();FCollisionQueryParams Q(SCENE_QUERY_STAT(TraversalInputContact),false,P);
  const bool Hit=W->LineTraceSingleByChannel(Contact,Feet+FVector(0,0,40),Feet+F*180+FVector(0,0,40),ECC_Visibility,Q);
  const double Facing=Hit?FMath::Abs(FVector::DotProduct(Contact.ImpactNormal,F)):0;
  const bool AtContact=Hit&&Contact.GetActor()==ParisTraversal::Fixture(W)&&Facing>.5&&Contact.Distance<=P->GetCapsuleComponent()->GetScaledCapsuleRadius()/Facing+.5;
  if(Advance<=100||!AtContact)return;
  InputKey(PC,EKeys::W,false);InputW=false;InputStopped=P->GetActorLocation();
  if(!Check(W,Advance>100&&!ParisTraversal::Active(P),TEXT("original_heldW_reaches_physical_box_without_auto_vault")))return;
  Stage=TEXT("input_trigger");Clock=0;return;
 }
 if(Stage==TEXT("input_trigger")&&Clock>.15){
  InputFallbackBefore=InspectNumber(W,TEXT("jump_fallbacks"));InputKey(PC,EKeys::SpaceBar,true);InputReleased=false;
  auto Row=InputCases.Last()->AsObject();Row->SetArrayField(TEXT("space_location"),V(P->GetActorLocation()));Row->SetStringField(TEXT("immediate_traversal"),ParisTraversal::Inspect(W));
  if(!Check(W,ParisTraversal::Active(P)==InputExpectsVault(),FString::Printf(TEXT("%s_actual_Space_expected_admission"),InputLabel())))return;
  Stage=InputExpectsVault()?TEXT("input_vault"):TEXT("input_jump");Clock=0;return;
 }
 if((Stage==TEXT("input_vault")||Stage==TEXT("input_jump"))&&!InputReleased&&Clock>.08){InputKey(PC,EKeys::SpaceBar,false);InputReleased=true;}
 if(Stage==TEXT("input_vault")){
  if(Step<2&&Images<4&&Age(W)>=TArray<double>{.12,.38,.65,.90}[Images]*2.133333){Image(FString::Printf(TEXT("%s_%d"),InputLabel(),Images));++Images;}
  if(Clock<2.6||ParisTraversal::Active(P))return;
  if(!Check(W,Name(P,TEXT("ActionState"))==TEXT("Ready")&&P->GetCharacterMovement()->IsMovingOnGround(),FString::Printf(TEXT("%s_completes_grounded_Ready"),InputLabel())))return;
  if(!Check(W,Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))==BeforeSum&&Num(P,TEXT("ShotSequence"))==Shot,TEXT("actual_input_vault_preserves_original_ammo")))return;
  if(!Check(W,InspectNumber(W,TEXT("jump_fallbacks"))==InputFallbackBefore,TEXT("successful_vault_does_not_also_jump")))return;
  Stage=TEXT("input_return");Clock=0;Images=0;return;
 }
 if(Stage==TEXT("input_jump")&&Clock>.2){
  if(!Check(W,!ParisTraversal::Active(P)&&P->GetCharacterMovement()->IsFalling()&&P->GetActorLocation().Z>InputStopped.Z+10,FString::Printf(TEXT("%s_same_Space_original_jump_not_swallowed"),InputLabel())))return;
  if(!Check(W,InspectNumber(W,TEXT("jump_fallbacks"))==InputFallbackBefore+1,TEXT("rejected_request_delivers_one_original_jump")))return;
  Stage=TEXT("input_jump_land");Clock=0;return;
 }
 if(Stage==TEXT("input_jump_land")&&Clock>2){if(!Check(W,P->GetCharacterMovement()->IsMovingOnGround()&&Name(P,TEXT("ActionState"))==TEXT("Ready"),TEXT("fallback_jump_lands_with_original_input_ready")))return;Stage=TEXT("input_return");Clock=0;Images=0;return;}
 if(Stage==TEXT("input_return")&&Clock>.55&&Images==0){Image(FString::Printf(TEXT("%s_return"),InputLabel()));Images=1;return;}
 if(Stage==TEXT("input_return")&&Clock>1.0){InputCases.Last()->AsObject()->SetStringField(TEXT("completed_traversal"),ParisTraversal::Inspect(W));++Step;SetupInputCase(W,PC,P);}
}
void Tick(UWorld* W,ELevelTick,float DT){
 if(Finished||!W->IsGameWorld()||W->GetNetMode()==NM_Client)return;auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;if(!M||!P||M->Phase==TEXT("Preparing"))return;
 Clock+=DT;if(Clock>105){Finish(W,false,TEXT("Explicit probe timeout"));return;}
 if(Stage==TEXT("boot")){
  bool Ready=false;for(TActorIterator<AActor> I(W);I;++I)if(I->GetOwner()==P&&Flag(*I,TEXT("Initialized")))Ready=true;if(!Ready||!ParisTraversal::Fixture(W))return;
  M->StartMission();HoldBrains(W);ProbeWorld=W;if(auto* C=Camera(P)){InitialCamera=C->GetRelativeTransform();InitialFOV=C->FieldOfView;InitialControlRotation=C->bUsePawnControlRotation;CameraCaptured=true;}
  Root->SetStringField(TEXT("mesh"),P->GetMesh()->GetSkeletalMeshAsset()->GetPathName());BeforeSum=Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"));Shot=Num(P,TEXT("ShotSequence"));Reset(W,P,PC);Stage=TEXT("settle");Clock=0;return;
 }
 Sample(W,P);
 if(Mode==TEXT("input")){InputTick(W,PC,P,DT);return;}
 if(Stage==TEXT("settle")&&Clock>.7){Clock=0;FString Why;
  if(Mode==TEXT("inspect")){const bool Good=ParisTraversal::Request(PC,Why);Root->SetStringField(TEXT("request_reason"),Why);if(!Good){Finish(W,false,Why);return;}Stage=TEXT("vault");return;}
  if(Mode==TEXT("visual")){ParisTraversal::SetObserver(PC,true);if(!Check(W,ParisTraversal::Request(PC,Why),TEXT("actual_player_third_person_vault_admitted")))return;Stage=TEXT("vault");Images=0;return;}
  if(Mode==TEXT("safety")){Stage=TEXT("negative");Step=0;return;}
  Finish(W,false,TEXT("Unknown explicit traversal mode"));return;
 }
 if(Stage==TEXT("vault")){
  if(Mode==TEXT("visual")&&Images<4&&Age(W)>=TArray<double>{.12,.38,.65,.90}[Images]*2.133333){Image(FString::Printf(TEXT("%s_vault_%d"),Step?TEXT("fp"):TEXT("tp"),Images));++Images;}
  if(Age(W)>.25&&Age(W)<.30){Tap(PC,EKeys::R);Tap(PC,EKeys::LeftMouseButton);Tap(PC,EKeys::MouseScrollDown);Tap(PC,EKeys::SpaceBar);}
  if(Clock<2.6||ParisTraversal::Active(P))return;
  if(!Check(W,Name(P,TEXT("ActionState"))==TEXT("Ready")&&P->GetCharacterMovement()->IsMovingOnGround(),TEXT("full_native_vault_finishes_ready_grounded")))return;
  if(!Check(W,Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))==BeforeSum&&Num(P,TEXT("ShotSequence"))==Shot&&ParisTacticalEquipment::Session(W).SelectedSlot==0,TEXT("vault_blocks_fire_reload_wheel_without_resource_change")))return;
  Root->SetArrayField(TEXT("camera_initial_location"),V(InitialCamera.GetLocation()));Root->SetArrayField(TEXT("camera_actual_location"),V(Camera(P)->GetRelativeLocation()));Root->SetArrayField(TEXT("camera_initial_scale"),V(InitialCamera.GetScale3D()));Root->SetArrayField(TEXT("camera_actual_scale"),V(Camera(P)->GetRelativeScale3D()));Root->SetNumberField(TEXT("camera_initial_fov"),InitialFOV);Root->SetNumberField(TEXT("camera_actual_fov"),Camera(P)->FieldOfView);Root->SetBoolField(TEXT("camera_initial_control"),InitialControlRotation);Root->SetBoolField(TEXT("camera_actual_control"),Camera(P)->bUsePawnControlRotation);if(!Check(W,!CameraCaptured||(Camera(P)->GetRelativeLocation().Equals(InitialCamera.GetLocation(),.001)&&Camera(P)->GetRelativeScale3D().Equals(InitialCamera.GetScale3D(),.000001)&&Camera(P)->FieldOfView==InitialFOV&&Camera(P)->bUsePawnControlRotation==InitialControlRotation),TEXT("original_camera_installation_within_0_001cm_after_return")))return;
  Stage=TEXT("returned");Clock=0;Images=0;return;
 }
 if(Stage==TEXT("returned")&&Clock>.55&&Images==0){Image(Step?TEXT("fp_return"):TEXT("tp_return"));Images=1;return;}
 if(Stage==TEXT("returned")&&Clock>1.1){if(Mode==TEXT("visual")&&Step==0){ParisTraversal::SetObserver(PC,false);Reset(W,P,PC);P->SetActorLocation(Start-FVector(80,0,0),false);PC->SetControlRotation(FRotator(-18,0,0));Root->SetNumberField(TEXT("first_person_review_pitch_degrees"),-18);Step=1;Stage=TEXT("approach");Clock=0;return;}Finish(W,true,TEXT("Actual full-capsule traversal completed; fine contact requires image review"));return;}
 if(Stage==TEXT("approach")){if(P->GetActorLocation().X<Start.X-8){P->AddMovementInput(FVector(1,0,0),1);if(Clock>3)Finish(W,false,TEXT("Original approach movement did not advance"));return;}if(!Check(W,FVector::Distance(P->GetActorLocation(),Start-FVector(80,0,0))>65,TEXT("actual_original_character_movement_approaches_before_vault")))return;FString Why;if(!Check(W,ParisTraversal::Request(PC,Why),TEXT("approaching_player_vault_admitted")))return;Stage=TEXT("vault");Clock=0;Images=0;return;}
 if(Stage==TEXT("repeat_settle")&&Clock>.6){FString Why;if(!Check(W,ParisTraversal::Request(PC,Why),TEXT("actual_player_first_person_vault_admitted")))return;Stage=TEXT("vault");Clock=0;Images=0;return;}
 if(Stage==TEXT("negative")&&Clock>.2){
  auto* B=ParisTraversal::Fixture(W);FVector O,E;B->GetActorBounds(false,O,E);FString Why;bool Good=false;
  if(Step==0){B->SetActorScale3D(B->GetActorScale3D()*FVector(1,1,1.3));B->SetActorLocation(B->GetActorLocation()+FVector(0,0,15));Good=!ParisTraversal::Request(PC,Why);Root->SetStringField(TEXT("high_reason"),Why);if(!Check(W,Good&&Why.Contains(TEXT("height")),TEXT("reject_high_obstacle")))return;B->SetActorScale3D(B->GetActorScale3D()/FVector(1,1,1.3));B->SetActorLocation(B->GetActorLocation()-FVector(0,0,15));}
  if(Step==1){B->SetActorScale3D(B->GetActorScale3D()*FVector(2,1,1));B->SetActorLocation(B->GetActorLocation()+FVector(E.X,0,0));Good=!ParisTraversal::Request(PC,Why);Root->SetStringField(TEXT("deep_reason"),Why);if(!Check(W,Good&&Why.Contains(TEXT("depth")),TEXT("reject_deep_obstacle")))return;B->SetActorScale3D(B->GetActorScale3D()/FVector(2,1,1));B->SetActorLocation(B->GetActorLocation()-FVector(E.X,0,0));}
  if(Step==2){Blocker=Cube(W,Start+FVector(130,0,160),FVector(200,200,15));Good=!ParisTraversal::Request(PC,Why);if(!Check(W,Good,TEXT("reject_overhead_full_capsule_blocker")))return;Blocker->Destroy();Blocker.Reset();}
  if(Step==3){Blocker=Cube(W,Start+FVector(337,0,30),FVector(70,80,160));Good=!ParisTraversal::Request(PC,Why);if(!Check(W,Good,TEXT("reject_blocked_landing")))return;Blocker->Destroy();Blocker.Reset();}
  if(Step==4){Tap(PC,EKeys::MouseScrollDown);Good=!ParisTraversal::Request(PC,Why);if(!Check(W,Good&&ParisTacticalEquipment::Session(W).SelectedSlot==1,TEXT("selected_grenade_rejects_without_spend")))return;Tap(PC,EKeys::MouseScrollUp);}
  if(Step==5){PC->SetControlRotation(FRotator(0,180,0));Tap(PC,EKeys::LeftMouseButton);Stage=TEXT("fire_wait");Clock=0;return;}
  if(Step==6){if(!Check(W,ParisTraversal::Request(PC,Why),TEXT("dynamic_cancel_initially_admitted")))return;Stage=TEXT("dynamic");Clock=0;return;}
  ++Step;Clock=0;return;
 }
 if(Stage==TEXT("fire_wait")&&Clock>.4){if(!Check(W,Num(P,TEXT("ShotSequence"))>Shot,TEXT("actual_original_shot_prepares_partial_reload")))return;BeforeSum=Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"));Shot=Num(P,TEXT("ShotSequence"));Tap(PC,EKeys::R);Stage=TEXT("reload_admission_wait");Clock=0;return;}
 if(Stage==TEXT("reload_admission_wait")&&Clock>.15){PC->SetControlRotation(FRotator::ZeroRotator);P->SetActorRotation(FRotator::ZeroRotator);FString Why;Root->SetStringField(TEXT("actual_reload_state"),Name(P,TEXT("ActionState")).ToString());if(!Check(W,Name(P,TEXT("ActionState"))==TEXT("Reloading")&&!ParisTraversal::Request(PC,Why),TEXT("original_reload_state_not_overwritten")))return;Stage=TEXT("reload_wait");Clock=0;return;}
 if(Stage==TEXT("reload_wait")&&Clock>5){if(!Check(W,Name(P,TEXT("ActionState"))==TEXT("Ready")&&Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))==BeforeSum,TEXT("original_reload_completion_conserved")))return;PC->SetControlRotation(FRotator::ZeroRotator);P->SetActorRotation(FRotator::ZeroRotator);Step=6;Stage=TEXT("negative");Clock=0;return;}
 if(Stage==TEXT("dynamic")){if(Clock>.45&&!Blocker.IsValid())Blocker=Cube(W,Start+FVector(210,0,160),FVector(40,140,150));if(Clock<1.2||ParisTraversal::Active(P))return;if(!Check(W,!ParisTraversal::Active(P)&&Name(P,TEXT("ActionState"))==TEXT("Ready"),TEXT("dynamic_obstacle_cancels_and_restores_action")))return;if(Blocker.IsValid())Blocker->Destroy();Blocker.Reset();Stage=TEXT("cancel_settle");Clock=0;return;}
 if(Stage==TEXT("cancel_settle")&&Clock>2){if(!Check(W,P->GetCharacterMovement()->IsMovingOnGround()&&!PC->IsMoveInputIgnored()&&!PC->IsLookInputIgnored(),TEXT("cancel_real_gravity_lands_and_input_locks_release")))return;Reset(W,P,PC);Stage=TEXT("extra");Step=0;Clock=0;}
 if(Stage==TEXT("extra")&&Clock>.6){
  auto* B=ParisTraversal::Fixture(W);FString Why;
  if(Step==0){const FVector Feet=Start-FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight());Blocker=Cube(W,Feet+FVector(40,0,238),FVector(280,240,20));B->SetActorLocation(B->GetActorLocation()+FVector(0,0,250));P->SetActorLocation(Start+FVector(0,0,250),false);const bool Rejected=!ParisTraversal::Request(PC,Why);Root->SetStringField(TEXT("unsupported_reason"),Why);if(!Check(W,Rejected&&Why.Contains(TEXT("Landing")),TEXT("raised_visible_platform_has_no_supported_far_landing")))return;B->SetActorLocation(B->GetActorLocation()-FVector(0,0,250));P->SetActorLocation(Start,false);Blocker->Destroy();Blocker.Reset();++Step;Clock=0;return;}
  if(Step==1){ACharacter* Other=nullptr;for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_Ally1"))){Other=*I;break;}if(!Check(W,Other!=nullptr,TEXT("actual_ally_exists_for_occupied_landing_fixture")))return;const FVector Old=Other->GetActorLocation();Other->SetActorLocation(Start+FVector(336.9,0,0),false);const bool Rejected=!ParisTraversal::Request(PC,Why);Other->SetActorLocation(Old,false);Root->SetStringField(TEXT("occupied_reason"),Why);if(!Check(W,Rejected&&Why.Contains(TEXT("occupied")),TEXT("actual_pawn_occupied_landing_rejected")))return;++Step;Clock=0;return;}
  if(Step==2){P->SetActorLocation(Start-FVector(350,0,0),false);P->GetCharacterMovement()->SetMovementMode(MOVE_Walking);PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::SpaceBar,IE_Pressed,1));Stage=TEXT("empty_jump");Clock=0;return;}
  if(Step==3){Reset(W,P,PC);if(!Check(W,ParisTraversal::Request(PC,Why),TEXT("pause_vault_initially_admitted")))return;Stage=TEXT("pause_enter");Clock=0;return;}
  if(Step==4){Reset(W,P,PC);if(!Check(W,ParisTraversal::Request(PC,Why),TEXT("death_vault_initially_admitted")))return;Stage=TEXT("death_enter");Clock=0;return;}
 }
 if(Stage==TEXT("empty_jump")&&Clock>.2){if(!Check(W,P->GetCharacterMovement()->IsFalling()&&!ParisTraversal::Active(P),TEXT("ordinary_empty_ground_space_jumps_without_vault")))return;PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::SpaceBar,IE_Released,0));Stage=TEXT("empty_jump_land");Clock=0;return;}
 if(Stage==TEXT("empty_jump_land")&&Clock>2){if(!Check(W,P->GetCharacterMovement()->IsMovingOnGround(),TEXT("ordinary_jump_lands_normally")))return;Step=3;Stage=TEXT("extra");Clock=0;return;}
 if(Stage==TEXT("pause_enter")&&Age(W)>.45){PauseAge=Age(W);PausePosition=P->GetActorLocation();Tap(PC,EKeys::Escape);PauseWall=FPlatformTime::Seconds();Stage=TEXT("paused");return;}
 if(Stage==TEXT("pause_resume")&&!ParisTraversal::Active(P)&&Clock>2.6){if(!Check(W,Name(P,TEXT("ActionState"))==TEXT("Ready")&&P->GetCharacterMovement()->IsMovingOnGround(),TEXT("paused_vault_resumes_to_supported_ready")))return;Step=4;Stage=TEXT("extra");Clock=0;return;}
 if(Stage==TEXT("death_enter")&&Age(W)>.45){auto* F=P->FindFunction(TEXT("PC_ApplyDamage"));if(!Check(W,F!=nullptr,TEXT("original_damage_interface_available")))return;FStructOnScope Values(F);auto* Amount=FindFProperty<FNumericProperty>(F,TEXT("Amount"));if(!Check(W,Amount!=nullptr,TEXT("original_damage_amount_parameter")))return;void* D=Amount->ContainerPtrToValuePtr<void>(Values.GetStructMemory());Amount->SetFloatingPointPropertyValue(D,200);P->ProcessEvent(F,Values.GetStructMemory());Stage=TEXT("death_wait");Clock=0;return;}
 if(Stage==TEXT("death_wait")&&Clock>4.5){if(!Check(W,Flag(P,TEXT("IsDead"))&&M->Phase==TEXT("Lost")&&!ParisTraversal::Active(P),TEXT("original_death_interrupts_vault_and_presents_lost")))return;if(!Check(W,!CameraCaptured||(Camera(P)->GetRelativeLocation().Equals(InitialCamera.GetLocation(),.001)&&Camera(P)->GetRelativeScale3D().Equals(InitialCamera.GetScale3D(),.000001)&&Camera(P)->FieldOfView==InitialFOV&&Camera(P)->bUsePawnControlRotation==InitialControlRotation),TEXT("death_releases_temporary_camera_installation")))return;Image(TEXT("death_after_vault"));Finish(W,true,TEXT("Full capsule admission/rejections, actual original jump, pause, dynamic cancellation and death lifecycle pass"));}

}
void WallTick(){if(Finished||Stage!=TEXT("paused")||FPlatformTime::Seconds()-PauseWall<.7)return;auto* W=ProbeWorld.Get();auto* PC=W?Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0)):nullptr;auto* P=PC?Cast<ACharacter>(PC->GetPawn()):nullptr;if(!W||!PC||!P)return;if(!Check(W,W->IsPaused()&&FVector::Distance(P->GetActorLocation(),PausePosition)<.000001&&FMath::Abs(Age(W)-PauseAge)<.000001,TEXT("actual_menu_pause_freezes_vault_age_and_capsule")))return;Tap(PC,EKeys::Escape);Stage=TEXT("pause_resume");Clock=0;}

}
void Initialize(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisTraversalCheck="),Mode)||!FParse::Value(FCommandLine::Get(),TEXT("ParisTraversalOut="),Out))return;IFileManager::Get().MakeDirectory(*Out,true);Root=MakeShared<FJsonObject>();Handle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);WallHandle=FCoreDelegates::OnEndFrame.AddStatic(&WallTick);}
void Shutdown(){if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);if(WallHandle.IsValid())FCoreDelegates::OnEndFrame.Remove(WallHandle);}
}
