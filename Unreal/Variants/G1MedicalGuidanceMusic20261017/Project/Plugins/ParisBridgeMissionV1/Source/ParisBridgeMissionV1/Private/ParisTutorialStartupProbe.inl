// Explicit opt-in startup witness; normal play neither records nor supplies inputs.
namespace StartupWitness {
bool Parsed=false,Enabled=false,Done=false;FString Mode,Out,Generation,Pending;
int Boot=0;double Began=0,StageSince=0,LastWrite=-1;int LastStage=-1;
bool CoveredSeen=false,FirstWorld=false,ReadyImage=false,LookImage=false,WalkImage=false,WaitingRestart=false;
TArray<TSharedPtr<FJsonValue>> Samples,Checks;TSet<FString> Captures;
bool Active(){
 if(!Parsed){Parsed=true;Enabled=FParse::Value(FCommandLine::Get(),TEXT("ParisStartupCheck="),Mode)&&FParse::Value(FCommandLine::Get(),TEXT("ParisStartupOut="),Out);if(Enabled){IFileManager::Get().MakeDirectory(*Out,true);Began=FPlatformTime::Seconds();}}
 return Enabled&&!Done;
}
void Save(const FString& Status){
 auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Status);O->SetStringField(TEXT("mode"),Mode);O->SetNumberField(TEXT("world_count"),Boot);O->SetArrayField(TEXT("checks"),Checks);O->SetArrayField(TEXT("samples"),Samples);
 O->SetStringField(TEXT("scope"),TEXT("Opt-in actual fresh/restore preparation and HUD frames; only fresh/restart modes drive Enter/mouse/F6. No resource/AI/collision override."));
 FString T;auto W=TJsonWriterFactory<TCHAR,TCondensedJsonPrintPolicy<TCHAR>>::Create(&T);FJsonSerializer::Serialize(O,W);
 FFileHelper::SaveStringToFile(T,*(Out/(Mode==TEXT("observe")?TEXT("STARTUP_TRACE.json"):TEXT("RESULT.json"))),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
void Finish(const FString& Status){if(Done)return;Save(Status);Done=true;FPlatformMisc::RequestExit(false);}
bool Check(bool Pass,const FString& Label){auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("name"),FString::Printf(TEXT("world%d_"),Boot)+Label);O->SetBoolField(TEXT("pass"),Pass);Checks.Add(MakeShared<FJsonValueObject>(O));if(!Pass)Finish(TEXT("failed_")+Label);return Pass;}
void TapKey(APlayerController* PC,FKey K){PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Pressed,1));PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,IE_Released,0));}
bool Picture(const TCHAR* Name){
 const FString Key=FString::Printf(TEXT("world%d_%s"),Boot,Name);
 if(Captures.Contains(Key))return true;
 if(FScreenshotRequest::IsScreenshotRequested()||!Pending.IsEmpty())return false;
 FScreenshotRequest::RequestScreenshot(Out/(Key+TEXT(".png")),false,false);Pending=Key;Captures.Add(Key);return true;
}
bool ImagesComplete(){
 if(Pending.IsEmpty())return true;
 if(FScreenshotRequest::IsScreenshotRequested()||!IFileManager::Get().FileExists(*(Out/(Pending+TEXT(".png")))))return false;
 Pending.Empty();return true;
}
void NewWorld(AParisBridgeMission* M){
 if(Generation==M->RunGeneration)return;
 Generation=M->RunGeneration;++Boot;CoveredSeen=FirstWorld=ReadyImage=LookImage=WalkImage=false;LastStage=-1;StageSince=0;WaitingRestart=false;
 auto* P=Pawn(M->GetWorld(),TEXT("Player"));
 if(P&&!M->GetWorld()->URL.HasOption(TEXT("ParisLoad")))Check(FVector::Dist2D(P->GetNavAgentLocation(),PlayerStartFeet())<1,TEXT("first_tick_fresh_spawn_is_new_start"));
}
}
void StartupDiagnostics(AParisBridgeMission* M){
 using namespace StartupWitness;if(!Active())return;NewWorld(M);if(Done)return;
 if(Mode!=TEXT("observe")&&FPlatformTime::Seconds()-Began>100){Finish(TEXT("failed_startup_finite_deadline"));return;}
 if(M->Phase==TEXT("Error")){Finish(TEXT("failed_preparation_")+M->Feedback);return;}
 ImagesComplete();if(Mode==TEXT("observe"))return;
 auto* PC=UGameplayStatics::GetPlayerController(M,0);if(!PC||!PC->GetPawn()||WaitingRestart||!ImagesComplete())return;
 if(M->Phase==TEXT("Preparing"))return;
 if(M->Phase==TEXT("Ready")){
  if(!ReadyImage||M->ReadySeconds<.6)return;
  if(!Check(CoveredSeen&&FirstWorld,TEXT("preparing_covered_before_first_world")))return;
  TapKey(PC,EKeys::Enter);return;
 }
 const int S=Step(M);const double Now=M->GetWorld()->GetTimeSeconds();
 if(S!=LastStage){LastStage=S;StageSince=Now;}
 if(S==Look&&LookImage&&Now-StageSince>.5){
  if(!Check(!HasGuidanceGoal(M),TEXT("look_has_no_navigation_marker")))return;
  PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseX,IE_Axis,20));return;
 }
 if(S==Walk){
  if(!Check(HasGuidanceGoal(M)&&FVector::DistSquared(Goal(M),FVector(-1200,-22700,97.280))<.01,TEXT("walk_uses_final_distant_goal")))return;
  if(Now-StageSince<1.1||!WalkImage)return;
  if(!Check(FVector::Dist2D(Goal(M),PlayerStartFeet())>1300,TEXT("first_walk_goal_over_13m_from_start")))return;
  if(Mode==TEXT("restart")&&Boot==1){WaitingRestart=true;TapKey(PC,EKeys::F6);if(!Check(ParisCombatUI::Confirmation(PC)==TEXT("Restart"),TEXT("actual_f6_confirmation_open")))return;TapKey(PC,EKeys::Left);TapKey(PC,EKeys::Enter);return;}
  if(Mode==TEXT("restart")&&!Check(Boot==2,TEXT("actual_f6_second_world")))return;
  Finish(Mode==TEXT("restart")?TEXT("pass_startup_and_f6_restart"):TEXT("pass_first_load_spawn_and_goal"));
 }
}
void StartupHUD(AParisBridgeMission* M,bool Covered){
 using namespace StartupWitness;if(!Active())return;NewWorld(M);if(Done)return;
 auto* P=Pawn(M->GetWorld(),TEXT("Player"));auto* PC=UGameplayStatics::GetPlayerController(M,0);if(!P||!PC)return;
 ImagesComplete();const double Now=M->GetWorld()->GetTimeSeconds();
 auto O=MakeShared<FJsonObject>();O->SetNumberField(TEXT("frame"),double(GFrameCounter));O->SetNumberField(TEXT("world"),Boot);O->SetNumberField(TEXT("time"),Now);O->SetStringField(TEXT("phase"),M->Phase);O->SetNumberField(TEXT("stage"),Step(M));O->SetBoolField(TEXT("covered"),Covered);O->SetBoolField(TEXT("load_travel"),M->GetWorld()->URL.HasOption(TEXT("ParisLoad")));O->SetBoolField(TEXT("goal_visible"),HasGuidanceGoal(M));O->SetStringField(TEXT("feet"),P->GetNavAgentLocation().ToString());O->SetStringField(TEXT("goal"),Goal(M).ToString());
 FVector Eye;FRotator R;PC->GetPlayerViewPoint(Eye,R);O->SetStringField(TEXT("camera"),Eye.ToString());Samples.Add(MakeShared<FJsonValueObject>(O));
 if(M->Phase==TEXT("Preparing")){
  if(!Check(Covered,TEXT("preparing_frame_is_covered")))return;
  CoveredSeen=true;Picture(TEXT("preparing"));
 }else if(!Covered&&!FirstWorld){
  if(!Check(CoveredSeen,TEXT("first_world_follows_cover")))return;
  if(!M->GetWorld()->URL.HasOption(TEXT("ParisLoad"))&&!Check(FVector::Dist2D(P->GetNavAgentLocation(),PlayerStartFeet())<5,TEXT("first_visible_world_at_new_start")))return;
  FirstWorld=true;
 }
 if(!Covered&&FirstWorld&&!ReadyImage&&Picture(TEXT("first_world")))ReadyImage=true;
 if(!Covered&&Step(M)==Look){if(!Check(!HasGuidanceGoal(M),TEXT("look_frame_has_no_goal")))return;if(Picture(TEXT("look")))LookImage=true;}
 if(!Covered&&Step(M)==Walk){if(!Check(HasGuidanceGoal(M)&&FVector::DistSquared(Goal(M),FVector(-1200,-22700,97.280))<.01,TEXT("walk_frame_final_goal")))return;if(Picture(TEXT("walk")))WalkImage=true;}
 if(Now-LastWrite>.25){LastWrite=Now;Save(TEXT("observing_startup"));}
}
