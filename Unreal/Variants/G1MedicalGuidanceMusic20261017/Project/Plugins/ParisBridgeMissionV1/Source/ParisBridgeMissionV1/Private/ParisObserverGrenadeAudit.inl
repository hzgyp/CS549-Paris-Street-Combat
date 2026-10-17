// Explicit opt-in only. Records real input and visible/native frames; no production fixtures.
int32 OGStep=0,OGIndex=0,OGItem=1;double OGAt=0;bool OGDone=false;FString OGView;
TArray<TSharedPtr<FJsonValue>> OGFrames,OGChecks;
void OGFinish(bool Pass,const FString& Why){
 auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Pass?TEXT("pass_observer_grenade_sequence"):TEXT("failed_observer_grenade_sequence"));O->SetStringField(TEXT("reason"),Why);
 O->SetStringField(TEXT("scope"),TEXT("Real controller wheel/primary/Escape/V; declared AI hold and flat site; ordinary V or named supplementary camera. Visual inspection required; no human acceptance."));
 O->SetStringField(TEXT("view"),OGView);O->SetArrayField(TEXT("frames"),OGFrames);O->SetArrayField(TEXT("checks"),OGChecks);FString J;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&J));FFileHelper::SaveStringToFile(J,*(PPOut/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);OGDone=true;FPlatformMisc::RequestExit(false);
}
bool OGC(bool B,const TCHAR* N){auto O=MakeShared<FJsonObject>();O->SetBoolField(TEXT("pass"),B);O->SetStringField(TEXT("check"),N);OGChecks.Add(MakeShared<FJsonValueObject>(O));if(!B)OGFinish(false,N);return B;}
void OGFrame(UWorld* W,ACharacter* P,const FString& Label){
 auto O=OBFrame(W,P,Label);O->SetNumberField(TEXT("probe_step"),OGStep);O->SetNumberField(TEXT("age"),W->GetTimeSeconds()-OGAt);
 auto* D=OBD(W,P);auto& E=ParisTacticalEquipment::Session(W);
 if(D&&D->UnifiedVisibleBody()){
  auto J=MakeShared<FJsonObject>();auto* B=D->UnifiedVisibleBody();
  for(FName N:{TEXT("root"),TEXT("pelvis"),TEXT("spine_01"),TEXT("spine_03"),TEXT("hand_l"),TEXT("index_01_l"),TEXT("middle_01_l"),TEXT("middle_03_l"),TEXT("ring_01_l"),TEXT("ring_03_l"),TEXT("pinky_01_l")})J->SetObjectField(N.ToString(),OBT(B->GetSocketTransform(N)));
  O->SetObjectField(TEXT("visible_world_bones"),J);
  AActor* Prop=E.Held.IsValid()?E.Held.Get():E.SelectedVisual.Get();
  if(Prop){auto Q=MakeShared<FJsonObject>();Q->SetObjectField(TEXT("world"),OBT(Prop->GetActorTransform()));Q->SetObjectField(TEXT("relative"),OBT(Prop->GetRootComponent()->GetRelativeTransform()));
   if(auto* C=Prop->FindComponentByClass<UStaticMeshComponent>()){Q->SetObjectField(TEXT("mesh_world"),OBT(C->GetComponentTransform()));Q->SetObjectField(TEXT("bounds_origin"),OBT(FTransform(C->GetStaticMesh()->GetBounds().Origin)));Q->SetObjectField(TEXT("bounds_extent"),OBT(FTransform(C->GetStaticMesh()->GetBounds().BoxExtent)));}
   O->SetObjectField(TEXT("prop_detail"),Q);
  }
 }
 if(E.StowedFrag.IsValid())O->SetObjectField(TEXT("stow_actor"),OBActor(E.StowedFrag.Get()));
 O->SetBoolField(TEXT("native_grenade_section_shown"),E.StowBody.IsValid()?E.StowBody->IsMaterialSectionShown(1,0):true);
 O->SetBoolField(TEXT("crouched"),P->bIsCrouched);O->SetNumberField(TEXT("desired_posture"),Num(P,TEXT("DesiredPosture")));O->SetNumberField(TEXT("selected_slot"),E.SelectedSlot);O->SetNumberField(TEXT("frag_stock"),E.Frag);O->SetNumberField(TEXT("smoke_stock"),E.Smoke);
 if(OGFrames.Num()<3000)OGFrames.Add(MakeShared<FJsonValueObject>(O));
}
void OGPhoto(UWorld* W,ACharacter* P,const FString& N){OGFrame(W,P,N);PPPhoto(N);}


void OGStowCamera(UWorld* W,ACharacter* P,APlayerController* PC){
 if(OGView==TEXT("ordinary"))return;
 FVector Offset=OGView==TEXT("front")?FVector(310,0,0):OGView==TEXT("left")?FVector(0,-310,0):FVector(-310,0,0);
 if(Num(P,TEXT("DesiredPosture"))==2)Offset.Z=220;
 auto* C=W->SpawnActor<ACameraActor>();C->SetOwner(P);C->GetCameraComponent()->SetFieldOfView(65);
 const auto Aim=P->GetActorLocation()+FVector(0,0,-10);C->SetActorLocation(Aim+P->GetActorTransform().TransformVectorNoScale(Offset));C->SetActorRotation((Aim-C->GetActorLocation()).Rotation());PC->SetViewTarget(C);if(PC->PlayerCameraManager)PC->PlayerCameraManager->SetGameCameraCutThisFrame();
}
bool OGStowOnly(UWorld* W,ACharacter* P,AParisBridgePlayerController* PC,double Age){
 auto& E=ParisTacticalEquipment::Session(W);auto Next=[&](int32 N){OGStep=N;OGAt=W->GetTimeSeconds();};
 auto Capture=[&](const TCHAR* Label){OGStowCamera(W,P,PC);OGPhoto(W,P,Label);};
 if(OGStep==30&&Age>.4){Capture(TEXT("stow_stand"));Next(40);return true;}
 if(OGStep==31&&Age>.8){if(!OGC(P->bIsCrouched,TEXT("real_control_crouch")))return true;Capture(TEXT("stow_crouch"));Next(41);return true;}
 if(OGStep==32&&Age>.7){PPTap(PC,EKeys::Z);Next(33);return true;}
 if(OGStep==33&&Age>3.&&Name(P,TEXT("ActionState"))==TEXT("Ready")){if(!OGC(Num(P,TEXT("DesiredPosture"))==2,TEXT("native_prone_endpoint_before_photo")))return true;Capture(TEXT("stow_prone"));Next(42);return true;}
 if(OGStep==34&&Age>3.&&Name(P,TEXT("ActionState"))==TEXT("Ready")){if(!OGC(Num(P,TEXT("DesiredPosture"))==0,TEXT("native_standing_endpoint_before_photo")))return true;Capture(TEXT("stow_stand_again"));Next(43);return true;}
 if(OGStep==35&&Age>.5){Capture(TEXT("stow_walk"));Next(44);return true;}
 if(OGStep==36&&Age>.5){if(!OGC(E.StowedFrag.IsValid()&&!E.StowedFrag->IsHidden()&&E.StowBody.IsValid()&&!E.StowBody->IsMaterialSectionShown(1,0),TEXT("belt_actor_survives_real_posture_inputs_native_section_hidden")))return true;OGFinish(true,TEXT("Unobscured stow-only posture/locomotion capture; original stocks, no grenade deployment or CPU readback. Actual image review required."));return true;}
 // Wait until the requested frame has been consumed before the next input.
 if(OGStep==40&&Age>.15){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftControl,IE_Pressed,1));Next(31);return true;}
 if(OGStep==41&&Age>.15){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftControl,IE_Released,0));Next(32);return true;}
 if(OGStep==42&&Age>.15){PPTap(PC,EKeys::Z);Next(34);return true;}
 if(OGStep==43&&Age>.15){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Pressed,1));Next(35);return true;}
 if(OGStep==44&&Age>.15){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Released,0));Next(36);return true;}
 if(Age>12)OGFinish(false,TEXT("stow_only_posture_timeout"));return true;
}

void OGTick(UWorld* W){
 if(OGDone||!W||!W->IsGameWorld())return;auto* M=AParisBridgeMission::Find(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));if(!M||!P||!PC)return;
 const double Now=W->GetTimeSeconds(),Age=Now-OGAt;auto& E=ParisTacticalEquipment::Session(W);OGFrame(W,P,TEXT("tick"));if(FScreenshotRequest::IsScreenshotRequested())return;
 auto Next=[&](int32 N){OGStep=N;OGAt=Now;OGIndex=0;};
 if(OGStep>=30){OGStowOnly(W,P,PC,Age);return;}
 if(OGStep==0){if(M->Phase!=TEXT("Ready")||!OBD(W,P))return;FParse::Value(FCommandLine::Get(),TEXT("ParisGrenadeView="),OGView);M->StartMission();PPHold(W);Next(1);return;}
 if(OGStep==1&&Age>.4){PPPlace(W,P,PC);Next(2);return;}
 if(OGStep==2&&Age>.5){PPTap(PC,EKeys::V);Next(3);return;}
 if(OGStep==3&&Age>.6){
  if(OGView==TEXT("front"))BodyCamera(W,P,PC,FVector(220,0,0));else if(OGView==TEXT("left"))BodyCamera(W,P,PC,FVector(0,-220,0));else if(OGView==TEXT("right"))BodyCamera(W,P,PC,FVector(0,220,0));else if(OGView==TEXT("rear"))BodyCamera(W,P,PC,FVector(-220,0,0));Next(4);return;
 }
 if(OGStep==4&&Age>.4&&FParse::Param(FCommandLine::Get(),TEXT("ParisStowOnly"))){OGStowCamera(W,P,PC);Next(30);return;}
 if(OGStep==4&&Age>.4){if(!OGC(E.StowedFrag.IsValid()&&!E.StowedFrag->IsHidden()&&E.StowBody.IsValid()&&!E.StowBody->IsMaterialSectionShown(1,0)&&E.StowedFrag->GetRootComponent()->GetAttachSocketName()==TEXT("pelvis"),TEXT("rifle_has_one_belt_frag_and_native_armpit_hidden")))return;
  int32 Count=0;for(TActorIterator<AActor> I(W);I;++I)if(I->ActorHasTag(TEXT("ParisObserverStowedGrenade")))++Count;
  if(!OGC(Count==1,TEXT("one_observer_stow_actor")))return;OGPhoto(W,P,TEXT("01_rifle"));Next(5);return;}
 if(OGStep==13&&Age>.2){OGFinish(true,TEXT("Native body material sections and original-size grenade geometry captured at rifle Ready; no visual repair claimed"));return;}
 if(OGStep==5&&Age>.1){PPTap(PC,EKeys::MouseScrollDown);Next(6);return;}
 if(OGStep==6){const double Ts[]={.025,.065,.1,.14,.18,.23,.3,.4,.6,.9};if(OGIndex<10&&Age>=Ts[OGIndex]){OGPhoto(W,P,FString::Printf(TEXT("%s_switch_%02d"),OGItem==1?TEXT("frag"):TEXT("smoke"),OGIndex++));return;}
  if(OGIndex==10&&Age>1.1){if(!OGC(E.SelectedSlot==OGItem&&E.SelectedVisual.IsValid(),TEXT("real_wheel_has_selected_prop")))return;
   if(!OGC(E.StowedFrag.IsValid()&&E.StowedFrag->IsHidden()==(OGItem==1),TEXT("frag_stow_hidden_only_when_frag_is_selected")))return;Next(7);return;}}
 if(OGStep==7&&Age>.1){PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,IE_Pressed,1));Next(8);return;}
 if(OGStep==8){const double Ts[]={.05,.2,.45,.9,1.2};if(OGIndex<5&&Age>=Ts[OGIndex]){OGPhoto(W,P,FString::Printf(TEXT("%s_prepare_%02d"),OGItem==1?TEXT("frag"):TEXT("smoke"),OGIndex++));return;}
  if(Age>1.4){if(OGItem==1){PPTap(PC,EKeys::Escape);PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,IE_Released,0));Next(9);}else{PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::LeftMouseButton,IE_Released,0));Next(10);}return;}}
 if(OGStep==9||OGStep==10){const double Ts[]={.025,.065,.1,.2,.3,.4,.6,.9,1.3,1.8};if(OGIndex<10&&Age>=Ts[OGIndex]){OGPhoto(W,P,FString::Printf(TEXT("%s_%s_%02d"),OGItem==1?TEXT("frag"):TEXT("smoke"),OGStep==9?TEXT("cancel"):TEXT("release"),OGIndex++));return;}
  if(OGIndex==10&&Age>2.2&&E.ThrowKind.IsEmpty()){
   if(OGItem==1){if(!OGC(E.Frag==1&&E.FragThrown==0,TEXT("frag_cancel_original_resources")))return;OGItem=2;PPTap(PC,EKeys::MouseScrollUp);Next(6);return;}
   if(!OGC(E.Smoke==0&&E.SmokeThrown==1&&Num(P,TEXT("LoadedAmmo"))==4&&Num(P,TEXT("ReserveAmmo"))==8,TEXT("smoke_release_one_original_resource_no_rifle_change")))return;Next(11);return;
  }}
 if(OGStep==11&&Age>.4){OGPhoto(W,P,TEXT("final_rifle"));Next(12);return;}
 if(OGStep==12&&Age>.2){PPTap(PC,EKeys::V);Next(19);return;}
 if(OGStep==19&&Age>.5){if(!OGC(!E.StowedFrag.IsValid()&&!E.StowBody.IsValid(),TEXT("first_person_releases_stow_actor_and_section_override")))return;PPTap(PC,EKeys::V);Next(20);return;}
 if(OGStep==20&&Age>.6){if(!OGC(E.StowedFrag.IsValid()&&!E.StowedFrag->IsHidden()&&E.StowBody.IsValid(),TEXT("V_return_restores_single_belt_display")))return;OGPhoto(W,P,TEXT("belt_V_return"));Next(21);return;}
 if(OGStep==21&&Age>.2){OGFinish(true,TEXT("Frag/smoke equip timelines, real prepare/cancel/release, original resources and return recorded. Inspect actual screenshots before acceptance."));return;}
 if(Age>20)OGFinish(false,FString::Printf(TEXT("probe_stage_timeout_%d"),OGStep));
}
