// Shared reference-pixel geometry for drawing, hover, mouse drag and keyboard focus.
constexpr double SettingsTabY=367,SettingsTabW=240,SettingsTabH=52;
constexpr double AudioRowY=439,AudioRowStep=72,AudioTrackX=1000,AudioTrackW=520;
constexpr double AudioResetY=811,AudioResetW=350;
const TCHAR* AudioNames[]={TEXT("MASTER VOLUME"),TEXT("MUSIC"),TEXT("AMBIENCE"),TEXT("SOUND EFFECTS"),TEXT("DIALOGUE")};
void AudioSave(AParisBridgePlayerController* PC){State(PC).Toast=ParisAudioPreferences::Save()?TEXT("Audio preferences saved."):TEXT("Audio changed for this session; preferences could not be saved.");}
void UpdateAudioDrag(AParisBridgePlayerController* PC){
 auto& U=State(PC);if(U.AudioDrag<0)return;
 const auto Mouse=Ref(PC);if(Mouse.X<0)return;
 const float Value=float(FMath::Clamp((Mouse.X-AudioTrackX)/AudioTrackW,0.,1.));
 // Whole percentages give a stable displayed and persisted value.
 ParisAudioPreferences::SetVolume(ParisAudioPreferences::EBus(U.AudioDrag),FMath::RoundToInt(Value*100)/100.f);
}
void FinishAudioDrag(AParisBridgePlayerController* PC){auto& U=State(PC);if(U.AudioDrag<0)return;UpdateAudioDrag(PC);U.AudioDrag=-1;AudioSave(PC);}
void DrawAudioSettings(FPaint& P,AParisBridgePlayerController* PC){
 auto& U=State(PC);
 for(int32 I=0;I<5;++I){
  const double Y=AudioRowY+I*AudioRowStep;const bool Focus=U.AudioRow==I;
  if(Focus){P.Box(650,Y-1,1062,57,FLinearColor(.10,.13,.10,.6));P.Line(650,Y+2,650,Y+51,Brass,3);}
  P.Label(AudioNames[I],670,Y+16,21,Focus?Brass:Ivory);
  const float V=ParisAudioPreferences::Volume(ParisAudioPreferences::EBus(I));
  P.Bar(AudioTrackX,Y+24,AudioTrackW,V,Focus?Brass:Green);
  P.Line(AudioTrackX+AudioTrackW*V,Y+15,AudioTrackX+AudioTrackW*V,Y+37,Focus?Brass:Ivory,4);
  P.Text(FString::Printf(TEXT("%d%%"),FMath::RoundToInt(V*100)),1560,Y+12,25,Focus?Brass:Ivory);
 }
 P.Button(TEXT("RESTORE AUDIO DEFAULTS"),660,AudioResetY,AudioResetW,U.AudioRow==5);
 P.Text(TEXT("Drag or use arrows. 0% mutes the channel."),1040,AudioResetY+5,19,Muted);
 P.Text(TEXT("Saved separately from checkpoints."),1040,AudioResetY+31,18,Muted);
 P.Text(TEXT("A: audio  /  D: display  /  Page Up or Down: page"),660,876,18,Muted);
}
bool AudioSettingsInput(AParisBridgePlayerController* PC,const FInputKeyEventArgs& A){
 auto& U=State(PC);if(U.Page!=3||!U.Confirm.IsEmpty())return false;
 if(A.Event!=IE_Pressed)return false;
 if(A.Key!=EKeys::LeftMouseButton)FinishAudioDrag(PC);
 if(A.Key==EKeys::A||A.Key==EKeys::D){FinishAudioDrag(PC);const int32 Tab=A.Key==EKeys::A?1:0;if(U.SettingsTab!=Tab){U.SettingsTab=Tab;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);}return true;}
 if(A.Key==EKeys::LeftMouseButton){
  const auto Mouse=Ref(PC);
  for(int32 I=0;I<2;++I)if(Hit(Mouse,660+I*260,SettingsTabY,SettingsTabW,SettingsTabH)){FinishAudioDrag(PC);if(U.SettingsTab!=I){U.SettingsTab=I;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);}U.SwallowClick=true;return true;}
 }
 if(U.SettingsTab!=1)return false;
 if(A.Key==EKeys::Up||A.Key==EKeys::Down){U.AudioRow=(U.AudioRow+(A.Key==EKeys::Up?5:1))%6;MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Navigate);return true;}
 if(A.Key==EKeys::Left||A.Key==EKeys::Right){
  if(U.AudioRow<5){const auto Bus=ParisAudioPreferences::EBus(U.AudioRow);const float Before=ParisAudioPreferences::Volume(Bus);ParisAudioPreferences::SetVolume(Bus,Before+(A.Key==EKeys::Left?-.05f:.05f));AudioSave(PC);if(!FMath::IsNearlyEqual(Before,ParisAudioPreferences::Volume(Bus)))MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Navigate);}return true;
 }
 if(A.Key==EKeys::Enter){if(U.AudioRow==5){ParisAudioPreferences::Defaults();AudioSave(PC);MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);}return true;}
 if(A.Key==EKeys::LeftMouseButton){
  const auto Mouse=Ref(PC);
  for(int32 I=0;I<5;++I)if(Hit(Mouse,AudioTrackX-12,AudioRowY+I*AudioRowStep+5,AudioTrackW+24,45)){U.AudioRow=U.AudioDrag=I;U.SwallowClick=true;UpdateAudioDrag(PC);MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);return true;}
  if(Hit(Mouse,660,AudioResetY,AudioResetW,52)){U.AudioRow=5;U.SwallowClick=true;ParisAudioPreferences::Defaults();AudioSave(PC);MenuCue(PC,ParisTutorialSoundscape::EMenuCue::Confirm);return true;}
 }
 return false;
}
FString HoverTarget(AParisBridgePlayerController* PC,FVector2D Mouse){
 auto& U=State(PC);
 if(!U.Confirm.IsEmpty()){
  if(Hit(Mouse,705,617,240,52))return TEXT("confirm");if(Hit(Mouse,975,617,240,52))return TEXT("cancel");return FString();
 }
 for(int32 I=0;I<4;++I)if(Hit(Mouse,NavX[I],NavY,NavW[I],NavH))return FString::Printf(TEXT("page%d"),I);
 for(int32 I=0;I<5;++I)if((I!=1||U.CanLoad)&&Hit(Mouse,SideX,SideY+I*SideStep,SideW,SideH))return FString::Printf(TEXT("side%d"),I);
 if(U.Page==2)for(int32 I=0;I<5;++I)if(Hit(Mouse,GroupX+I*GroupStep,GroupY,GroupW,GroupH))return FString::Printf(TEXT("help%d"),I);
 if(U.Page==3){
  for(int32 I=0;I<2;++I)if(Hit(Mouse,660+I*260,SettingsTabY,SettingsTabW,SettingsTabH))return FString::Printf(TEXT("settings%d"),I);
  if(U.SettingsTab==1){
   for(int32 I=0;I<5;++I)if(Hit(Mouse,650,AudioRowY+I*AudioRowStep,1062,57)){U.AudioRow=I;return FString::Printf(TEXT("audio%d"),I);}
   if(Hit(Mouse,660,AudioResetY,AudioResetW,52)){U.AudioRow=5;return TEXT("audioDefaults");}
  }else{
   if(Hit(Mouse,660,465,300,52))return TEXT("hints");if(Hit(Mouse,660,580,300,52))return TEXT("hud");if(Hit(Mouse,660,750,300,52))return TEXT("language");
  }
 }
 if(U.Page==4){
  for(int32 I=0;I<U.HistoryRows.Num();++I)if(Hit(Mouse,660,385+I*123,1042,111))return FString::Printf(TEXT("record%d"),I);
  if(U.HistoryRows.IsValidIndex(U.Record)){
   if(Hit(Mouse,660,800,360,52))return TEXT("historyLoad");
   if(!U.HistoryRows[U.Record].Latest&&Hit(Mouse,1050,800,360,52))return TEXT("historyDelete");
  }
 }
 return FString();
}
