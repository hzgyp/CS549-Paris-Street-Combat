// Finite opt-in witnesses; declared fixtures, never enabled by the normal entry.
namespace {
FString ProbeMode,ProbeOut;FDelegateHandle ProbeHandle;bool ProbeDone=false;int32 ProbeStep=0;
double ProbeAt=0,DeathAt=0;FString ProbeGeneration;TArray<TSharedPtr<FJsonValue>> ProbeChecks;
void Tap(APlayerController* PC,FKey K){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Released,0));}
double Number(const UObject* O,const TCHAR* K){auto* F=O?FindFProperty<FNumericProperty>(O->GetClass(),K):nullptr;if(!F)return -1;auto* V=F->ContainerPtrToValuePtr<void>(O);return F->IsFloatingPoint()?F->GetFloatingPointPropertyValue(V):F->GetSignedIntPropertyValue(V);}
void Damage(ACharacter* P){auto* F=P->FindFunction(TEXT("PC_ApplyDamage"));check(F);FStructOnScope Params(F);auto* Amount=CastField<FNumericProperty>(F->FindPropertyByName(TEXT("Amount")));check(Amount);Amount->SetFloatingPointPropertyValue(Amount->ContainerPtrToValuePtr<void>(Params.GetStructMemory()),1000);P->ProcessEvent(F,Params.GetStructMemory());}
void FinishProbe(UWorld* W,bool Pass,const FString& Why){auto O=Inspect(W);O->SetStringField(TEXT("status"),Pass?TEXT("pass_player_death_")+ProbeMode:TEXT("failed_player_death_")+ProbeMode);O->SetStringField(TEXT("reason"),Why);O->SetStringField(TEXT("scope"),TEXT("real controller input and original death/damage; NPC AI held; mine relocation, endpoint damage posture fixtures; no natural-combat claim"));O->SetArrayField(TEXT("checks"),ProbeChecks);FString J;auto Writer=TJsonWriterFactory<>::Create(&J);FJsonSerializer::Serialize(O,Writer);FFileHelper::SaveStringToFile(J,*(ProbeOut/TEXT("RESULT.json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);ProbeDone=true;FPlatformMisc::RequestExit(false);}
bool Require(UWorld* W,bool Pass,const TCHAR* Name){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("check"),Name);O->SetBoolField(TEXT("pass"),Pass);ProbeChecks.Add(MakeShared<FJsonValueObject>(O));if(!Pass)FinishProbe(W,false,Name);return Pass;}
void Picture(const TCHAR* Name){FScreenshotRequest::RequestScreenshot(ProbeOut/FString(Name),false,false);}
void ProbeTick(UWorld* W,ELevelTick,float){
 if(ProbeDone||!W||!W->IsGameWorld()||UGameplayStatics::IsGamePaused(W))return;auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!M||!PC||!P)return;
 if(FScreenshotRequest::IsScreenshotRequested())return;auto& E=ParisTacticalEquipment::Session(W);const double Now=W->GetTimeSeconds();
 if(ProbeStep==0){if(M->Phase!=TEXT("Ready"))return;bool DisplayReady=false;for(TActorIterator<AActor> I(W);I;++I)if(I->GetOwner()==P&&Object(*I,TEXT("Pose"))&&Object(*I,TEXT("Gun"))){auto* F=FindFProperty<FBoolProperty>(I->GetClass(),TEXT("Initialized"));DisplayReady|=F&&F->GetPropertyValue_InContainer(*I);}if(!DisplayReady)return;
  M->StartMission();for(TActorIterator<ACharacter> I(W);I;++I)if(auto* AI=Cast<AAIController>(I->GetController()))if(AI->GetBrainComponent())AI->GetBrainComponent()->PauseLogic(TEXT("Finite death visual isolation"));ProbeGeneration=M->RunGeneration;ProbeAt=Now;ProbeStep=1;
  if(ProbeMode==TEXT("crouch"))Tap(PC,EKeys::LeftControl);else if(ProbeMode==TEXT("prone")){P->SetActorLocation(FVector(1762.5,-20662.5,114.402)+FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()),false);P->GetCharacterMovement()->StopMovementImmediately();Tap(PC,EKeys::Z);}return;
 }
 if(ProbeStep==1&&Now-ProbeAt>.8){
  Picture(TEXT("01_before.png"));ProbeStep=2;return;
 }
 if(ProbeStep==2){
  if(ProbeMode==TEXT("mine")){const auto& T=E.Traps[0];P->SetActorLocation(T.Position+FVector(0,0,P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()),false);P->GetCharacterMovement()->StopMovementImmediately();}
  else if(ProbeMode==TEXT("frag")){PC->SetControlRotation(FRotator(-80,PC->GetControlRotation().Yaw,0));Tap(PC,EKeys::G);}
  else {if(ProbeMode==TEXT("crouch")&&!Require(W,P->bIsCrouched,TEXT("actual_crouched_before_death")))return;if(ProbeMode==TEXT("prone")&&!Require(W,Number(P,TEXT("DesiredPosture"))==2,TEXT("actual_prone_before_death")))return;Damage(P);}
  ProbeAt=Now;ProbeStep=3;return;
 }
 if(ProbeStep==3){if(Now-ProbeAt>15){FinishProbe(W,false,TEXT("original hazard did not kill"));return;}if(!Dead(P)||!Inspect(W)->GetBoolField(TEXT("started")))return;if(DeathAt==0)DeathAt=Now;if(Now-DeathAt<.2)return;
  if(!Require(W,Presenting(W)&&!PC->InteractionMenuVisible(),TEXT("early_dead_HUD_and_terminal_actions_suppressed")))return;
  const double Loaded=Number(P,TEXT("LoadedAmmo")),Reserve=Number(P,TEXT("ReserveAmmo"));Tap(PC,EKeys::F6);Tap(PC,EKeys::F9);Tap(PC,EKeys::LeftMouseButton);Tap(PC,EKeys::G);
  if(!Require(W,M->RunGeneration==ProbeGeneration&&Number(P,TEXT("LoadedAmmo"))==Loaded&&Number(P,TEXT("ReserveAmmo"))==Reserve,TEXT("early_restart_load_fire_equipment_input_blocked")))return;
  Picture(TEXT("02_death_start.png"));ProbeStep=4;return;
 }
 if(ProbeStep==4&&Now-DeathAt>.8){auto O=Inspect(W);if(!Require(W,O->GetBoolField(TEXT("body_visible"))&&O->GetBoolField(TEXT("camera_owned"))&&O->GetNumberField(TEXT("clip_time"))>.5&&O->GetBoolField(TEXT("playing")),TEXT("full_body_owned_camera_original_clip_advances")))return;Picture(TEXT("03_falling.png"));ProbeStep=5;return;}
 if(ProbeStep==5&&Now-DeathAt>2.6){if(!Require(W,Presenting(W)&&!PC->InteractionMenuVisible(),TEXT("no_restart_overlay_before_collapse_finishes")))return;Picture(TEXT("04_collapse.png"));ProbeStep=6;return;}
 if(ProbeStep==6){if(Now-DeathAt>8){FinishProbe(W,false,TEXT("terminal sequence timeout"));return;}if(!Complete(W))return;auto O=Inspect(W);if(!Require(W,M->Phase==TEXT("Lost")&&PC->InteractionMenuVisible()&&!O->GetBoolField(TEXT("playing"))&&O->GetNumberField(TEXT("clip_time"))>=O->GetNumberField(TEXT("clip_length"))-.025,TEXT("terminal_pose_then_original_Lost_menu")))return;Picture(TEXT("05_terminal_menu.png"));ProbeAt=Now;ProbeStep=7;return;}
 if(ProbeStep==7&&Now-ProbeAt>.3){Tap(PC,EKeys::F6);Tap(PC,EKeys::Left);Tap(PC,EKeys::Enter);ProbeAt=Now;ProbeStep=8;return;}
 if(ProbeStep==8){if(Now-ProbeAt>25){FinishProbe(W,false,TEXT("restart did not produce Ready"));return;}if(M->RunGeneration==ProbeGeneration||M->Phase!=TEXT("Ready"))return;if(!Require(W,!Dead(P)&&!Presenting(W)&&!Complete(W)&&!Inspect(W)->GetBoolField(TEXT("camera_owned"))&&Number(P,TEXT("Health"))==100,TEXT("new_world_restart_alive_and_death_camera_cleaned")))return;Picture(TEXT("06_restarted.png"));ProbeAt=Now;ProbeStep=9;return;}
 if(ProbeStep==9&&Now-ProbeAt>.3)FinishProbe(W,true,TEXT("actual original death clip, input/HUD delay, corpse then menu, normal restart cleanup"));
}
void InitializeProbe(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisDeathProbe="),ProbeMode))return;check(ProbeMode==TEXT("mine")||ProbeMode==TEXT("frag")||ProbeMode==TEXT("damage")||ProbeMode==TEXT("crouch")||ProbeMode==TEXT("prone"));check(FParse::Value(FCommandLine::Get(),TEXT("ParisDeathOut="),ProbeOut));IFileManager::Get().MakeDirectory(*ProbeOut,true);ProbeHandle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&ProbeTick);}
void ShutdownProbe(){if(ProbeHandle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(ProbeHandle);}
}
