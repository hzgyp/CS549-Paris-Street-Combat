// Opt-in candidate regression. Production bindings are active in every ordinary run.
namespace {
int32 OBStep=0,OBPhoto=0,OBDeferred=0;double OBAt=0,OBWall=0,OBAmmo=0,OBReserve=0,OBShots=0,OBCommits=0,OBFrag=0,OBSmoke=0,OBReloadLoaded=0;double OBLifeWall=0,OBPauseTime=0;FVector OBMoveStart;bool OBOriginalHidden=false,OBOriginalOwnerNoSee=true;bool OBDone=false,OBSwap1=false,OBSwap2=false,OBReloadChecked=false;
TArray<TSharedPtr<FJsonValue>> OBFrames,OBChecks;
TSharedPtr<FJsonObject> OBT(const FTransform& T){auto O=MakeShared<FJsonObject>();const auto V=T.GetLocation();const auto Q=T.GetRotation();const auto Scale=T.GetScale3D();O->SetArrayField(TEXT("scale"),{MakeShared<FJsonValueNumber>(Scale.X),MakeShared<FJsonValueNumber>(Scale.Y),MakeShared<FJsonValueNumber>(Scale.Z)});O->SetArrayField(TEXT("t"),{MakeShared<FJsonValueNumber>(V.X),MakeShared<FJsonValueNumber>(V.Y),MakeShared<FJsonValueNumber>(V.Z)});O->SetArrayField(TEXT("q"),{MakeShared<FJsonValueNumber>(Q.X),MakeShared<FJsonValueNumber>(Q.Y),MakeShared<FJsonValueNumber>(Q.Z),MakeShared<FJsonValueNumber>(Q.W)});return O;}
AParisFirstPersonApprovedActor* OBD(UWorld* W,ACharacter* P){for(TActorIterator<AParisFirstPersonApprovedActor> I(W);I;++I)if(I->GetOwner()==P&&I->Initialized)return *I;return nullptr;}
TSharedPtr<FJsonObject> OBActor(AActor* A){auto O=MakeShared<FJsonObject>();if(!A)return O;O->SetStringField(TEXT("actor"),A->GetPathName());O->SetStringField(TEXT("class"),A->GetClass()->GetPathName());O->SetBoolField(TEXT("hidden"),A->IsHidden());O->SetObjectField(TEXT("world"),OBT(A->GetActorTransform()));if(auto* C=A->GetRootComponent()){O->SetStringField(TEXT("attach_component"),C->GetAttachParent()?C->GetAttachParent()->GetPathName():TEXT("None"));O->SetStringField(TEXT("socket"),C->GetAttachSocketName().ToString());}return O;}


void BodyCamera(UWorld* W,ACharacter* P,APlayerController* PC,const FVector& Offset){
 auto* C=W->SpawnActor<ACameraActor>();C->SetOwner(P);C->GetCameraComponent()->SetFieldOfView(55);const auto Aim=P->GetActorLocation()+FVector(0,0,40);C->SetActorLocation(Aim+P->GetActorTransform().TransformVectorNoScale(Offset));C->SetActorRotation((Aim-C->GetActorLocation()).Rotation());PC->SetViewTarget(C);if(PC->PlayerCameraManager)PC->PlayerCameraManager->SetGameCameraCutThisFrame();
}
void DumpSkin(USkinnedMeshComponent* Mesh,const TCHAR* Name){TArray<FFinalSkinVertex> Vs;Mesh->GetCPUSkinnedVertices(Vs,0);auto O=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Rows;for(const auto& V:Vs){Rows.Add(MakeShared<FJsonValueArray>(TArray<TSharedPtr<FJsonValue>>{MakeShared<FJsonValueNumber>(V.Position.X),MakeShared<FJsonValueNumber>(V.Position.Y),MakeShared<FJsonValueNumber>(V.Position.Z)}));}O->SetArrayField(TEXT("vertices"),Rows);FString J;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&J));FFileHelper::SaveStringToFile(J,*(PPOut/(FString(Name)+TEXT(".json"))),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);}

void BodyInventory(UWorld* W,ACharacter* P){
 auto Root=MakeShared<FJsonObject>();TArray<TSharedPtr<FJsonValue>> Actors;
 for(TActorIterator<AActor> It(W);It;++It){auto* A=*It;if(A!=P&&A->GetOwner()!=P&&!A->IsA<AParisFirstPersonApprovedActor>())continue;
  auto AO=OBActor(A);TArray<TSharedPtr<FJsonValue>> Meshes;TArray<UMeshComponent*> Cs;A->GetComponents(Cs);
  for(auto* C:Cs){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("component"),C->GetPathName());O->SetStringField(TEXT("class"),C->GetClass()->GetPathName());O->SetBoolField(TEXT("hidden"),C->bHiddenInGame);O->SetBoolField(TEXT("visible"),C->IsVisible());O->SetBoolField(TEXT("owner_no_see"),C->bOwnerNoSee);O->SetBoolField(TEXT("only_owner_see"),C->bOnlyOwnerSee);O->SetObjectField(TEXT("world"),OBT(C->GetComponentTransform()));
   TArray<TSharedPtr<FJsonValue>> Mats;for(int32 I=0;I<C->GetNumMaterials();++I)Mats.Add(MakeShared<FJsonValueString>(C->GetMaterial(I)?C->GetMaterial(I)->GetPathName():TEXT("None")));O->SetArrayField(TEXT("materials"),Mats);
   if(auto* S=Cast<USkinnedMeshComponent>(C)){O->SetBoolField(TEXT("nanite"),S->ShouldNaniteSkin());O->SetBoolField(TEXT("cpu_skin"),S->GetCPUSkinningEnabled());O->SetStringField(TEXT("asset"),S->GetSkinnedAsset()?S->GetSkinnedAsset()->GetPathName():TEXT("None"));TArray<TSharedPtr<FJsonValue>> Bones;
    for(int32 I=0;I<S->GetNumBones();++I){auto B=OBT(S->GetBoneTransform(I,FTransform::Identity));B->SetStringField(TEXT("name"),S->GetBoneName(I).ToString());B->SetBoolField(TEXT("bone_hidden"),S->IsBoneHidden(I));Bones.Add(MakeShared<FJsonValueObject>(B));}O->SetArrayField(TEXT("bones"),Bones);
   }else if(auto* Static=Cast<UStaticMeshComponent>(C))O->SetStringField(TEXT("asset"),Static->GetStaticMesh()?Static->GetStaticMesh()->GetPathName():TEXT("None"));
   Meshes.Add(MakeShared<FJsonValueObject>(O));
  }AO->SetArrayField(TEXT("meshes"),Meshes);Actors.Add(MakeShared<FJsonValueObject>(AO));
 }Root->SetArrayField(TEXT("actors"),Actors);FString J;FJsonSerializer::Serialize(Root,TJsonWriterFactory<>::Create(&J));FFileHelper::SaveStringToFile(J,*(PPOut/TEXT("body_inventory.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}

TSharedPtr<FJsonObject> OBFrame(UWorld* W,ACharacter* P,const FString& Label){
 auto O=MakeShared<FJsonObject>();auto* D=OBD(W,P);auto& E=ParisTacticalEquipment::Session(W);auto* PC=UGameplayStatics::GetPlayerController(W,0);auto* B=P->GetMesh();
 O->SetObjectField(TEXT("player_world"),OBT(P->GetActorTransform()));O->SetStringField(TEXT("label"),Label);O->SetNumberField(TEXT("step"),OBStep);O->SetNumberField(TEXT("time"),W->GetTimeSeconds());O->SetNumberField(TEXT("age"),W->GetTimeSeconds()-OBAt);O->SetStringField(TEXT("action"),Name(P,TEXT("ActionState")).ToString());O->SetStringField(TEXT("active_pose"),Name(P,TEXT("ActivePose")).ToString());O->SetNumberField(TEXT("loaded"),Num(P,TEXT("LoadedAmmo")));O->SetNumberField(TEXT("reserve"),Num(P,TEXT("ReserveAmmo")));O->SetNumberField(TEXT("shots"),Num(P,TEXT("ShotSequence")));O->SetNumberField(TEXT("reload_commits"),Num(P,TEXT("ReloadCommitCount")));O->SetNumberField(TEXT("health"),Num(P,TEXT("Health")));O->SetNumberField(TEXT("body_anim_mode"),int32(B->GetAnimationMode()));O->SetBoolField(TEXT("body_hidden"),B->bHiddenInGame);O->SetBoolField(TEXT("body_owner_no_see"),B->bOwnerNoSee);O->SetStringField(TEXT("body_anim_class"),B->GetAnimClass()?B->GetAnimClass()->GetPathName():TEXT("None"));
 if(auto* S=B->GetSingleNodeInstance()){O->SetStringField(TEXT("body_clip"),S->GetCurrentAsset()?S->GetCurrentAsset()->GetName():TEXT("None"));O->SetNumberField(TEXT("body_clip_time"),S->GetCurrentTime());}
 auto Bones=MakeShared<FJsonObject>();for(FName N:{TEXT("spine_03"),TEXT("upperarm_r"),TEXT("lowerarm_r"),TEXT("hand_r"),TEXT("hand_l")}){auto T=B->GetSocketTransform(N,RTS_Component);Bones->SetObjectField(N.ToString(),OBT(T));}O->SetObjectField(TEXT("body_bones_component"),Bones);
 O->SetObjectField(TEXT("body_hand_r_world"),OBT(B->GetSocketTransform(TEXT("hand_r"),RTS_World)));
 auto* G=Cast<AActor>(Obj(P,TEXT("WeaponAppearance")));auto Gun=OBActor(G);auto* Grip=Cast<USkeletalMeshComponent>(Obj(G,TEXT("GripMesh")));if(Grip){Gun->SetStringField(TEXT("grip_mesh"),Grip->GetPathName());Gun->SetBoolField(TEXT("grip_is_actual_body"),Grip==B);Gun->SetObjectField(TEXT("grip_hand_world"),OBT(Grip->GetSocketTransform(TEXT("hand_r"))));}if(G){Gun->SetNumberField(TEXT("distance_to_body_hand_cm"),FVector::Distance(G->GetActorLocation(),B->GetSocketLocation(TEXT("hand_r"))));if(Grip)Gun->SetNumberField(TEXT("distance_to_grip_hand_cm"),FVector::Distance(G->GetActorLocation(),Grip->GetSocketLocation(TEXT("hand_r"))));}if(G)for(TActorIterator<AActor> I(W);I;++I)if(Obj(*I,TEXT("DisplayGun"))==G){auto Driver=OBActor(*I);for(const TCHAR* K:{TEXT("PoseMesh"),TEXT("SourceMesh"),TEXT("BodySource"),TEXT("SkeletalMeshComponent")})if(auto* C=Cast<USkeletalMeshComponent>(Obj(*I,K))){auto Mesh=MakeShared<FJsonObject>();Mesh->SetStringField(TEXT("component"),C->GetPathName());Mesh->SetBoolField(TEXT("is_body"),C==B);Mesh->SetObjectField(TEXT("hand_r_world"),OBT(C->GetSocketTransform(TEXT("hand_r"))));if(auto* S=C->GetSingleNodeInstance())Mesh->SetStringField(TEXT("clip"),S->GetCurrentAsset()?S->GetCurrentAsset()->GetName():TEXT("None"));Driver->SetObjectField(K,Mesh);Gun->SetNumberField(TEXT("distance_to_driver_hand_cm"),FVector::Distance(G->GetActorLocation(),C->GetSocketLocation(TEXT("hand_r"))));}Gun->SetObjectField(TEXT("driver"),Driver);break;}
 O->SetObjectField(TEXT("legacy_rifle"),Gun);
 TArray<TSharedPtr<FJsonValue>> OldRifles;
 auto* AcceptedGunComp=D?Cast<UStaticMeshComponent>(Obj(D,TEXT("Gun"))):nullptr;
 if(AcceptedGunComp)for(TActorIterator<AActor> It(W);It;++It){auto* A=*It;if(A==D||A->GetOwner()!=P||A->ActorHasTag(TEXT("ParisUnifiedPerspectiveDisplay")))continue;TArray<UStaticMeshComponent*> Cs;A->GetComponents(Cs);for(auto* C:Cs)if(C->GetStaticMesh()==AcceptedGunComp->GetStaticMesh()){OldRifles.Add(MakeShared<FJsonValueObject>(OBActor(A)));break;}}
 O->SetArrayField(TEXT("all_legacy_rifles"),OldRifles);

 if(D){auto F=OBActor(D);F->SetBoolField(TEXT("recoil_active"),D->RecoilActive);F->SetNumberField(TEXT("recoil_starts"),D->RecoilStarts);F->SetNumberField(TEXT("recoil_age"),D->RecoilAge);if(auto* Pose=Cast<USceneComponent>(Obj(D,TEXT("Pose"))))F->SetObjectField(TEXT("pose_relative"),OBT(Pose->GetRelativeTransform()));if(auto* GunComp=Cast<UStaticMeshComponent>(Obj(D,TEXT("Gun")))){F->SetBoolField(TEXT("rifle_component_visible"),GunComp->IsVisible());F->SetObjectField(TEXT("rifle_world"),OBT(GunComp->GetComponentTransform()));}O->SetObjectField(TEXT("approved_FP"),F);}
 O->SetStringField(TEXT("view_target"),PC&&PC->GetViewTarget()?PC->GetViewTarget()->GetPathName():TEXT("None"));auto* Cam=Cast<UCameraComponent>(Obj(P,TEXT("ParisPlayerCamera")));if(Cam)O->SetObjectField(TEXT("gameplay_camera"),OBT(Cam->GetComponentTransform()));if(PC&&PC->PlayerCameraManager)O->SetObjectField(TEXT("render_camera"),OBT(FTransform(PC->PlayerCameraManager->GetCameraRotation(),PC->PlayerCameraManager->GetCameraLocation())));
 if(E.EquipmentPoseSource.IsValid()){auto Source=MakeShared<FJsonObject>();for(FName N:{TEXT("root"),TEXT("pelvis"),TEXT("spine_01"),TEXT("spine_03"),TEXT("upperarm_l"),TEXT("hand_l"),TEXT("hand_r")})Source->SetObjectField(N.ToString(),OBT(E.EquipmentPoseSource->GetSocketTransform(N,RTS_Component)));O->SetObjectField(TEXT("native_equipment_source"),Source);}
 O->SetNumberField(TEXT("selected_slot"),E.SelectedSlot);O->SetStringField(TEXT("throw_kind"),E.ThrowKind);O->SetStringField(TEXT("throw_stage"),E.ThrowStage);O->SetNumberField(TEXT("frag"),E.Frag);O->SetNumberField(TEXT("smoke"),E.Smoke);O->SetStringField(TEXT("equipment_source_tag"),E.EquipmentPoseTag);O->SetObjectField(TEXT("selected_prop"),OBActor(E.SelectedVisual.Get()));O->SetObjectField(TEXT("held_prop"),OBActor(E.Held.Get()));

 if(D){
  TSharedPtr<FJsonObject> Unified;FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(D->InspectUnifiedPresentation()),Unified);O->SetObjectField(TEXT("unified"),Unified);
  auto* VB=D->UnifiedVisibleBody();auto* VG=D->UnifiedVisibleRifle();
  if(VB){auto Body=MakeShared<FJsonObject>();Body->SetObjectField(TEXT("world"),OBT(VB->GetComponentTransform()));
   for(FName N:{TEXT("pelvis"),TEXT("head"),TEXT("foot_l"),TEXT("foot_r"),TEXT("clavicle_l"),TEXT("clavicle_r"),TEXT("upperarm_l"),TEXT("lowerarm_l"),TEXT("hand_l"),TEXT("upperarm_r"),TEXT("lowerarm_r"),TEXT("hand_r")})Body->SetObjectField(N.ToString(),OBT(VB->GetSocketTransform(N,RTS_Component)));
   O->SetObjectField(TEXT("visible_body"),Body);
  }
  if(VG){auto Rifle=MakeShared<FJsonObject>();Rifle->SetObjectField(TEXT("world"),OBT(VG->GetComponentTransform()));Rifle->SetObjectField(TEXT("relative"),OBT(VG->GetRelativeTransform()));Rifle->SetBoolField(TEXT("visible"),VG->IsVisible()&&!VG->bHiddenInGame&&!VG->GetOwner()->IsHidden());Rifle->SetStringField(TEXT("socket"),VG->GetAttachSocketName().ToString());
   O->SetObjectField(TEXT("visible_rifle"),Rifle);}
  O->SetNumberField(TEXT("FP_support_error_cm"),D->SupportErrorCm);O->SetNumberField(TEXT("FP_length_error_cm"),D->LimbLengthErrorCm);O->SetNumberField(TEXT("FP_finger_error_deg"),D->FingerRotationErrorDegrees);
  int32 Live=0;for(TObjectIterator<USceneComponent> I;I;++I)if(I->GetWorld()==W&&I->GetClass()->GetName()==TEXT("NiagaraComponent")&&I->IsActive()&&I->GetAttachParent()==VG)++Live;O->SetNumberField(TEXT("visible_muzzle_components"),Live);
 }
 if(OBFrames.Num()<4000)OBFrames.Add(MakeShared<FJsonValueObject>(O));return O;
}
void OBFinish(UWorld* W,bool Complete,const FString& Reason){
 if(Complete){
  auto Add=[&](bool Pass,const TCHAR* N){auto C=MakeShared<FJsonObject>();C->SetStringField(TEXT("check"),N);C->SetBoolField(TEXT("pass"),Pass);OBChecks.Add(MakeShared<FJsonValueObject>(C));Complete&=Pass;};
  int32 VisibleTP=0,RecoilTP=0,Muzzle=0;bool OldHidden=true,EquipHidden=true,Grip=true,Length=true;int32 LegacyObserved=0;
  for(const auto& V:OBFrames){auto F=V->AsObject();if(F->GetNumberField(TEXT("step"))<3||!F->HasField(TEXT("approved_FP")))continue;
   OldHidden&=F->GetObjectField(TEXT("legacy_rifle"))->GetBoolField(TEXT("hidden"));
   const TSharedPtr<FJsonObject>* U=nullptr;if(!F->TryGetObjectField(TEXT("unified"),U))continue;
   if((*U)->GetBoolField(TEXT("observer"))){++VisibleTP;for(const auto& Old:F->GetArrayField(TEXT("all_legacy_rifles"))){++LegacyObserved;OldHidden&=Old->AsObject()->GetBoolField(TEXT("hidden"));}Length&=(*U)->GetNumberField(TEXT("max_length_error_cm"))<.0001;
    if((*U)->GetNumberField(TEXT("recoil_hand_delta_cm"))>.00001)++RecoilTP;
    if(F->GetNumberField(TEXT("selected_slot"))!=0||!F->GetStringField(TEXT("throw_kind")).IsEmpty())EquipHidden&=!(*U)->GetBoolField(TEXT("rifle_visible"));
    const TSharedPtr<FJsonObject>* R=nullptr;if(F->TryGetObjectField(TEXT("visible_rifle"),R))Grip&=(*R)->GetStringField(TEXT("socket"))==TEXT("hand_r");
   }
   Muzzle+=int32(F->GetNumberField(TEXT("visible_muzzle_components")));
  }
  Add(OldHidden,TEXT("legacy_rifle_hidden_all_active_frames"));Add(EquipHidden,TEXT("shared_equipment_hides_both_rifles"));Add(Grip,TEXT("current_visible_rifle_attached_to_current_hand_r"));Add(Length,TEXT("body_recoil_preserves_arm_lengths"));
  if(PPMode!=TEXT("binding_fp")){Add(VisibleTP>0&&RecoilTP>0,TEXT("native_recoil_reaches_visible_body"));Add(LegacyObserved>=2,TEXT("both_superseded_player_rifles_found_and_checked"));}
  Add(Muzzle>0,TEXT("committed_shot_has_current_visible_rifle_muzzle_effect"));
 }
auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Complete?TEXT("pass_binding_audit_capture"):TEXT("failed_binding_audit_capture"));O->SetStringField(TEXT("reason"),Reason);O->SetStringField(TEXT("mode"),PPMode);O->SetBoolField(TEXT("production_repair_candidate"),true);O->SetStringField(TEXT("scope"),TEXT("Candidate shared FP/V production bindings active; scoped regression and visual review required. Tutorial102 parent, real Tutorial/ProneStrafe/CheckpointHistory flags, original4/8 ammo and1/1 grenades. StartTraining invoked normally; lesson completion is not claimed. Declared AI hold/flat relocation; ordinary V camera, original actual input/resources; no resource injection."));O->SetArrayField(TEXT("frames"),OBFrames);O->SetArrayField(TEXT("checks"),OBChecks);FString J;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&J));FFileHelper::SaveStringToFile(J,*(PPOut/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);OBDone=true;FPlatformMisc::RequestExit(false);}
bool OBC(UWorld* W,bool Pass,const TCHAR* Label){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("check"),Label);O->SetBoolField(TEXT("pass"),Pass);OBChecks.Add(MakeShared<FJsonValueObject>(O));if(!Pass)OBFinish(W,false,Label);return Pass;}
void OBPic(UWorld* W,ACharacter* P,const FString& Name){OBFrame(W,P,Name);PPPhoto(Name);}
#include "ParisObserverGrenadeAudit.inl"
void OBTick(UWorld* W){
 if(FParse::Param(FCommandLine::Get(),TEXT("ParisObserverGrenadeProbe"))){OGTick(W);return;}
 if(OBDone||!W||!W->IsGameWorld())return;auto* M=AParisBridgeMission::Find(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));if(!M||!P||!PC)return;const double Now=W->GetTimeSeconds();auto& E=ParisTacticalEquipment::Session(W);OBFrame(W,P,TEXT("tick"));if(FScreenshotRequest::IsScreenshotRequested())return;
 // Capture the requested state before dispatching the next input. A screenshot
 // is rendered later in this frame, so same-tick action changes mislabel it.
 if(OBDeferred){const int32 Action=OBDeferred;OBDeferred=0;OBAt=Now;
  if(Action==1)PPTap(PC,EKeys::MouseScrollDown);
  if(Action==2)PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,IE_Pressed,1));
  if(Action==3){PPTap(PC,EKeys::Escape);PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,IE_Released,0));}
  if(Action==4){for(int32 I=0;I<3&&E.SelectedSlot!=2;++I)PPTap(PC,EKeys::MouseScrollDown);if(!OBC(W,E.SelectedSlot==2,TEXT("bounded_actual_wheel_smoke_selection")))return;}
  if(Action==5)PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,IE_Released,0));
  if(Action==6)PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::RightMouseButton,IE_Released,0));
  return;
 }

 if(OBStep==0){if(M->Phase!=TEXT("Ready")||!OBD(W,P))return;M->StartMission();PPHold(W);OBWall=FPlatformTime::Seconds();OBAt=Now;OBStep=1;return;}
 if(OBStep==1&&Now-OBAt>.4){if(!FParse::Param(FCommandLine::Get(),TEXT("ParisBodyMovementProbe")))PPPlace(W,P,PC);else {PPHold(W);PC->AddYawInput(20);}
OBAt=Now;OBStep=2;return;}
 if(OBStep==2&&Now-OBAt>.6){OBOriginalHidden=P->GetMesh()->bHiddenInGame;OBOriginalOwnerNoSee=P->GetMesh()->bOwnerNoSee;if(PPMode!=TEXT("binding_fp"))PPTap(PC,EKeys::V);OBAt=Now;OBStep=3;return;}
 if(OBStep==3&&Now-OBAt>.5){BodyInventory(W,P);OBPic(W,P,TEXT("01_idle"));OBAmmo=Num(P,TEXT("LoadedAmmo"));OBReserve=Num(P,TEXT("ReserveAmmo"));OBShots=Num(P,TEXT("ShotSequence"));OBCommits=Num(P,TEXT("ReloadCommitCount"));OBFrag=E.Frag;OBSmoke=E.Smoke;OBAt=Now;OBStep=FParse::Param(FCommandLine::Get(),TEXT("ParisBodyMovementProbe"))?200:FParse::Param(FCommandLine::Get(),TEXT("ParisBodySkinProbe"))?100:4;return;}


 if(OBStep==100&&Now-OBAt>.5){BodyCamera(W,P,PC,FVector(230,0,0));OBStep=101;OBAt=Now;return;}
 if(OBStep==101&&Now-OBAt>.6){OBPic(W,P,TEXT("clone_original_front"));OBStep=102;OBAt=Now;return;}
 if(OBStep==102&&Now-OBAt>.5){P->Tags.Add(TEXT("ParisBodyNativeRifleProbe"));OBStep=103;OBAt=Now;return;}
 if(OBStep==103&&Now-OBAt>.6){OBPic(W,P,TEXT("clone_native_ready_front"));OBStep=104;OBAt=Now;return;}
 if(OBStep==104&&Now-OBAt>.5){P->Tags.Remove(TEXT("ParisBodyNativeRifleProbe"));P->Tags.Add(TEXT("ParisBodyFullRifleProbe"));OBStep=105;OBAt=Now;return;}
 if(OBStep==105&&Now-OBAt>.6){OBPic(W,P,TEXT("clone_full_ready_front"));OBStep=106;OBAt=Now;return;}
 if(OBStep==106&&Now-OBAt>.5){BodyCamera(W,P,PC,FVector(0,-230,0));OBStep=107;OBAt=Now;return;}
 if(OBStep==107&&Now-OBAt>.6){OBPic(W,P,TEXT("clone_full_ready_side"));OBStep=108;OBAt=Now;return;}
 if(OBStep==108&&Now-OBAt>.5){OBFinish(W,false,TEXT("Front/side and native-pose diagnostic captured; not gameplay acceptance"));return;}

 if(OBStep==200&&Now-OBAt>.3){OBMoveStart=P->GetActorLocation();PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Pressed,1));OBStep=201;OBAt=Now;return;}
 if(OBStep==201&&Now-OBAt>.3){OBPic(W,P,TEXT("move_01_walk"));OBStep=202;return;}
 if(OBStep==202&&Now-OBAt>.8){OBPic(W,P,TEXT("move_02_walk"));OBStep=203;return;}
 if(OBStep==203&&Now-OBAt>1.1){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Released,0));if(!OBC(W,FVector::Dist2D(P->GetActorLocation(),OBMoveStart)>50,TEXT("ordinary_spawn_actual_W_moves_over_50cm")))return;PC->AddYawInput(45);OBStep=204;OBAt=Now;return;}
 if(OBStep==204&&Now-OBAt>.5){OBPic(W,P,TEXT("move_03_turn"));OBStep=205;OBAt=Now;return;}
 if(OBStep==205&&Now-OBAt>.3){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Pressed,1));OBStep=206;OBAt=Now;return;}
 if(OBStep==206&&Now-OBAt>.5){OBPic(W,P,TEXT("move_04_second_heading"));OBStep=207;return;}
 if(OBStep==207&&Now-OBAt>.8){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Released,0));OBStep=4;OBAt=Now;return;}

 if(OBStep==4&&Now-OBAt>.4){PPTap(PC,EKeys::LeftMouseButton);OBAt=Now;OBStep=5;OBPhoto=0;return;}
 if(OBStep==5){const double Times[]={.033,.1,.2,.4};if(OBPhoto<4&&Now-OBAt>=Times[OBPhoto]){OBPic(W,P,FString::Printf(TEXT("02_fire_%02d"),OBPhoto++));return;}if(Now-OBAt>.65){if(!OBC(W,Num(P,TEXT("ShotSequence"))==OBShots+1&&Num(P,TEXT("LoadedAmmo"))==OBAmmo-1,TEXT("actual_LMB_one_original_shot_and_one_round_consumed")))return;PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::RightMouseButton,IE_Pressed,1));OBAt=Now;OBStep=6;return;}}
 if(OBStep==6&&Now-OBAt>.4){OBPic(W,P,TEXT("03_aim"));OBDeferred=6;OBAt=Now;OBStep=7;return;}
 if(OBStep==7&&Now-OBAt>.3){PPTap(PC,EKeys::R);OBAt=Now;OBStep=8;OBPhoto=0;return;}
 if(OBStep==8){const double Age=Now-OBAt;if(Age>.1&&!OBReloadChecked){if(!OBC(W,Name(P,TEXT("ActionState"))==TEXT("Reloading"),TEXT("actual_R_admits_original_reload_after_original_input_queue")))return;OBReloadChecked=true;}const double Times[]={.1,1.,2.,3.6,4.1};if(PPMode==TEXT("binding_swap")&&Age>1.2&&!OBSwap1){PPTap(PC,EKeys::V);OBSwap1=true;return;}if(PPMode==TEXT("binding_swap")&&Age>2.4&&!OBSwap2){PPTap(PC,EKeys::V);OBSwap2=true;return;}if(OBPhoto<5&&Age>=Times[OBPhoto]){OBPic(W,P,FString::Printf(TEXT("04_reload_%02d"),OBPhoto++));return;}if(Age>4.5&&Name(P,TEXT("ActionState"))==TEXT("Ready")){if(!OBC(W,Num(P,TEXT("LoadedAmmo"))>OBAmmo-1&&Num(P,TEXT("LoadedAmmo"))+Num(P,TEXT("ReserveAmmo"))==OBAmmo+OBReserve-1&&Num(P,TEXT("ReloadCommitCount"))==OBCommits+1,TEXT("one_original_reload_commit_resources_conserved")))return;OBReloadLoaded=Num(P,TEXT("LoadedAmmo"));OBPic(W,P,TEXT("05_reload_return"));OBDeferred=1;OBAt=Now;OBStep=9;return;}}
 if(OBStep==9&&Now-OBAt>.65){if(!OBC(W,E.SelectedSlot==1&&E.SelectedVisual.IsValid(),TEXT("actual_wheel_frag_ready")))return;OBPic(W,P,TEXT("06_frag_ready"));OBDeferred=2;OBAt=Now;OBStep=10;return;}
 if(OBStep==10&&Now-OBAt>.9){OBPic(W,P,TEXT("07_frag_hold"));OBDeferred=3;OBAt=Now;OBStep=11;return;}
 if(OBStep==11&&Now-OBAt>1.8&&E.ThrowKind.IsEmpty()){if(!OBC(W,E.Frag==OBFrag&&E.FragThrown==0,TEXT("actual_Escape_cancel_no_frag_consumption")))return;OBPic(W,P,TEXT("08_frag_cancel"));OBDeferred=4;OBAt=Now;OBStep=12;return;}
 if(OBStep==12&&Now-OBAt>.6){OBPic(W,P,TEXT("09_smoke_ready"));OBDeferred=2;OBAt=Now;OBStep=13;return;}
 if(OBStep==13&&Now-OBAt>.8){OBPic(W,P,TEXT("10_smoke_hold"));OBDeferred=5;OBAt=Now;OBStep=14;OBPhoto=0;return;}
 if(OBStep==14){const double Times[]={.15,.4,.8};if(OBPhoto<3&&Now-OBAt>=Times[OBPhoto]){OBPic(W,P,FString::Printf(TEXT("11_smoke_throw_%02d"),OBPhoto++));return;}if(Now-OBAt>3&&E.ThrowKind.IsEmpty()){if(!OBC(W,E.SmokeThrown==1&&E.Smoke==OBSmoke-1&&Num(P,TEXT("Health"))==100&&Num(P,TEXT("LoadedAmmo"))==OBReloadLoaded,TEXT("actual_smoke_release_one_consumption_no_damage_or_ammo_change")))return;OBPic(W,P,TEXT("12_final"));OBAt=Now;OBStep=15;return;}}
 if(OBStep==15&&Now-OBAt>.2&&PPMode!=TEXT("binding_lifecycle")&&FParse::Param(FCommandLine::Get(),TEXT("ParisBodyMovementProbe"))){BodyCamera(W,P,PC,FVector(230,0,0));OBStep=210;OBAt=Now;return;}
 if(OBStep==210&&Now-OBAt>.5){OBPic(W,P,TEXT("detail_front"));OBStep=211;OBAt=Now;return;}
 if(OBStep==211&&Now-OBAt>.3){BodyCamera(W,P,PC,FVector(0,-230,0));OBStep=212;OBAt=Now;return;}
 if(OBStep==212&&Now-OBAt>.5){OBPic(W,P,TEXT("detail_right"));OBStep=213;OBAt=Now;return;}
 if(OBStep==213&&Now-OBAt>.3){BodyCamera(W,P,PC,FVector(0,230,0));OBStep=214;OBAt=Now;return;}
 if(OBStep==214&&Now-OBAt>.5){OBPic(W,P,TEXT("detail_left"));OBStep=215;OBAt=Now;return;}
 if(OBStep==215&&Now-OBAt>.3){OBFinish(W,true,TEXT("Ordinary spawn V walking/turning and original bindings; supplemental front/side detail"));return;}
 if(OBStep==15&&Now-OBAt>.2&&PPMode!=TEXT("binding_lifecycle")){OBFinish(W,true,TEXT("Shared FP/V candidate regression completed; visual review remains separate"));return;}

 if(PPMode==TEXT("binding_lifecycle")){
  if(OBStep==15&&Now-OBAt>.3){OBStep=16;OBLifeWall=FPlatformTime::Seconds();OBPauseTime=Now;PPTap(PC,EKeys::Escape);OBPic(W,P,TEXT("13_pause_menu"));return;}
  if(OBStep==16&&FPlatformTime::Seconds()-OBLifeWall>.4){if(!OBC(W,W->IsPaused()&&FMath::Abs(Now-OBPauseTime)<.03,TEXT("V_pause_freezes_world_time")))return;PPTap(PC,EKeys::Escape);OBStep=17;OBAt=Now;return;}
  if(OBStep==17&&Now-OBAt>.5){if(!OBC(W,!W->IsPaused()&&OBD(W,P)->UnifiedObserver(),TEXT("V_resume_retains_current_display")))return;OBPic(W,P,TEXT("14_resume"));OBStep=18;OBAt=Now;return;}
  if(OBStep==18&&Now-OBAt>.3){PPTap(PC,EKeys::Z);OBStep=19;OBAt=Now;return;}
  if(OBStep==19&&Now-OBAt>3.5){if(!OBC(W,Num(P,TEXT("DesiredPosture"))==2,TEXT("actual_V_Z_enters_native_prone")))return;OBPic(W,P,TEXT("15_prone"));OBStep=20;OBAt=Now;return;}
  if(OBStep==20&&Now-OBAt>.3){PPTap(PC,EKeys::Z);OBStep=21;OBAt=Now;return;}
  if(OBStep==21&&Now-OBAt>3.5){if(!OBC(W,Num(P,TEXT("DesiredPosture"))==0,TEXT("actual_V_Z_returns_standing")))return;OBPic(W,P,TEXT("16_stand"));OBStep=22;OBAt=Now;return;}
  if(OBStep==22&&Now-OBAt>.3){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftControl,IE_Pressed,1));OBStep=23;OBAt=Now;return;}
  // Full native Ctrl descent is 0.666667s; inspect only after its endpoint.
  if(OBStep==23&&Now-OBAt>1.0){if(!OBC(W,P->bIsCrouched,TEXT("actual_V_control_crouch")))return;OBPic(W,P,TEXT("17_crouch"));OBStep=24;OBAt=Now;return;}
  if(OBStep==24&&Now-OBAt>.3){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftControl,IE_Released,0));PPTap(PC,EKeys::V);OBStep=25;OBAt=Now;return;}
  if(OBStep==25&&Now-OBAt>.5){PPTap(PC,EKeys::V);OBStep=26;OBAt=Now;return;}
  if(OBStep==26&&Now-OBAt>.5){OBPic(W,P,TEXT("18_toggle_return"));OBStep=27;OBAt=Now;return;}
  if(OBStep==27&&Now-OBAt>.3){auto* F=P->FindFunction(TEXT("PC_ApplyDamage"));check(F);FStructOnScope Params(F);auto* Amount=FindFProperty<FNumericProperty>(F,TEXT("Amount"));check(Amount);Amount->SetFloatingPointPropertyValue(Amount->ContainerPtrToValuePtr<void>(Params.GetStructMemory()),1000.);P->ProcessEvent(F,Params.GetStructMemory());OBStep=28;OBAt=Now;return;}
  if(OBStep==28&&Now-OBAt>.45){if(!OBC(W,Num(P,TEXT("Health"))<=0&&!OBD(W,P)->UnifiedObserver()&&!P->GetMesh()->bHiddenInGame,TEXT("V_death_returns_to_original_visible_body")))return;OBPic(W,P,TEXT("19_death_native"));OBStep=29;OBAt=Now;return;}
  if(OBStep==29&&Now-OBAt>4.2){OBPic(W,P,TEXT("20_death_menu"));OBStep=30;OBAt=Now;return;}
  if(OBStep==30&&Now-OBAt>.25){PPTap(PC,EKeys::F9);OBStep=31;OBLifeWall=FPlatformTime::Seconds();return;}
  if(OBStep==31&&FPlatformTime::Seconds()-OBLifeWall>.25){PPTap(PC,EKeys::Left);PPTap(PC,EKeys::Enter);OBStep=32;OBAt=Now;return;}
  if(OBStep==32&&OBD(W,P)&&M->AllowsPlay()&&Num(P,TEXT("Health"))>0){auto* D=OBD(W,P);if(!OBC(W,Num(P,TEXT("Health"))>0&&M->AllowsPlay()&&D&&!D->UnifiedObserver()&&!D->IsHidden()&&PC->GetViewTarget()==P&&P->GetMesh()->bHiddenInGame==OBOriginalHidden&&P->GetMesh()->bOwnerNoSee==OBOriginalOwnerNoSee,TEXT("actual_F9_restores_original_FP_body_flags_and_view")))return;OBPic(W,P,TEXT("21_actual_FP_retry"));OBStep=33;OBAt=Now;return;}
  if(OBStep==33&&Now-OBAt>.25){OBFinish(W,true,TEXT("V pause/posture/death plus actual F9 checkpoint restore and original FP view/body flags; declared direct death fixture and earned CP0 seed"));return;}
 }
 if(FPlatformTime::Seconds()-OBWall>100&&OBWall>0)OBFinish(W,false,TEXT("Bounded audit timeout; preserve exact input state"));
}
}
