// Finite opt-in matching-Game verification. No normal launcher enables this file.
#include "ParisAudioPreferences.h"
#include "ParisBridgeMission.h"
#include "ParisCombatUI.h"
#include "ParisLanguage.h"
#include "AudioDevice.h"
#include "AudioThread.h"
#include "AudioMixerBlueprintLibrary.h"
#include "Components/AudioComponent.h"
#include "Containers/Ticker.h"
#include "Dom/JsonObject.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "HAL/FileManager.h"
#include "InputKeyEventArgs.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/ConfigCacheIni.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Sound/SoundClass.h"
#include "Sound/SoundWaveProcedural.h"
#include "UObject/UObjectIterator.h"
namespace ParisAudioCheck { namespace {
FTSTicker::FDelegateHandle Handle;FString Mode,Out,Pending;int32 Step=0,Assertions=0;double At=0,Begin=0,ReadyAt=0;bool Done=false,Recording=false;
TArray<TSharedPtr<FJsonValue>> Evidence;
void Finish(const FString& Status,const FString& Why){if(Done)return;Done=true;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Status);O->SetStringField(TEXT("reason"),Why);O->SetNumberField(TEXT("assertions"),Assertions);const auto* Branch=GConfig->FindBranch(NAME_None,GGameUserSettingsIni);O->SetStringField(TEXT("ini"),Branch?Branch->IniPath:GGameUserSettingsIni);O->SetArrayField(TEXT("evidence"),Evidence);FString Raw;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&Raw));FFileHelper::SaveStringToFile(Raw,*(Out/TEXT("RESULT.json")));FPlatformMisc::RequestExit(false);}
bool Check(bool Good,const TCHAR* Why){++Assertions;if(!Good)Finish(TEXT("failed_audio"),Why);return Good;}
void Tap(AParisBridgePlayerController* PC,FKey K){for(auto E:{IE_Pressed,IE_Released})PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,E,E==IE_Pressed?1.f:0.f));}
void Image(AParisBridgePlayerController* PC,const TCHAR* Name){Pending=Out/(FString(Name)+TEXT(".png"));PC->ConsoleCommand(FString::Printf(TEXT("Shot SHOWUI -nosuffix filename=%s"),*Pending),false);}
void Go(AParisBridgePlayerController* PC,int32 Row){for(int32 I=0;I<6&&ParisCombatUI::Inspect(PC)->GetIntegerField(TEXT("audio_row"))!=Row;++I)Tap(PC,EKeys::Down);}
bool Vol(int32 I,float V){return Check(FMath::IsNearlyEqual(ParisAudioPreferences::Volume(ParisAudioPreferences::EBus(I)),V,.001f),TEXT("Native audio control expected volume"));}
bool Disk(){const TCHAR* Keys[]={TEXT("Master"),TEXT("Music"),TEXT("Ambience"),TEXT("Effects"),TEXT("Voice")};const auto* Branch=GConfig->FindBranch(NAME_None,GGameUserSettingsIni);if(!Check(Branch&&!Branch->IniPath.IsEmpty(),TEXT("Resolved physical preference file")))return false;FConfigFile F;F.Read(Branch->IniPath);for(int32 I=0;I<5;++I){float V=-1;if(!Check(F.GetFloat(TEXT("ParisAudioPreferences"),Keys[I],V)&&FMath::IsNearlyEqual(V,ParisAudioPreferences::Volume(ParisAudioPreferences::EBus(I)),.001f),TEXT("Actual independent audio INI disk readback")))return false;}return true;}
bool Snapshot(UWorld* W,AParisBridgePlayerController* PC,const TCHAR* Name,float MusicMix){
 auto O=ParisCombatUI::Inspect(PC);O->SetStringField(TEXT("step"),Name);int32 Music=0;float Mix=-1;auto Device=W->GetAudioDevice();
 for(TObjectIterator<UAudioComponent> I;I;++I)if(I->GetWorld()==W&&I->IsPlaying())if(auto* Wave=Cast<USoundWaveProcedural>(I->Sound))if(Wave->NumChannels==2){++Music;O->SetBoolField(TEXT("music_ui"),I->bIsUISound);O->SetNumberField(TEXT("music_queued_bytes"),Wave->GetAvailableAudioByteCount());O->SetNumberField(TEXT("music_component_gain"),I->VolumeMultiplier);if(Device.IsValid()){auto* Class=Wave->SoundClassObject.Get();FAudioThread::RunCommandOnAudioThread([Device,Class,&Mix]() mutable {if(auto* P=Device->GetSoundClassCurrentProperties(Class))Mix=P->Volume;});FAudioCommandFence Fence;Fence.BeginFence();Fence.Wait();}}
 O->SetNumberField(TEXT("music_streams"),Music);O->SetNumberField(TEXT("music_effective_class_gain"),Mix);Evidence.Add(MakeShared<FJsonValueObject>(O));
 if(!Check(O->HasField(TEXT("music_component_gain"))&&FMath::IsNearlyEqual(O->GetNumberField(TEXT("music_component_gain")),1.6,.035),TEXT("Actual opening music settles to stronger component gain")))return false;
 return Check(Music==1,TEXT("Exactly one live stereo music stream through menu/mute"))&&Check(FMath::IsNearlyEqual(Mix,MusicMix,.015f),TEXT("Actual mixer gain equals master times music, once"));
}
void TickWorld(UWorld* W){
 if(Done||!W||!W->IsGameWorld())return;const double Now=FPlatformTime::Seconds();if(Now-Begin>95){Finish(TEXT("failed_audio_timeout"),TEXT("Finite audio/menu check deadline"));return;}
 auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));if(!M||!PC||M->Phase!=TEXT("Ready"))return;
 if(ReadyAt==0)ReadyAt=Now;if(Now-ReadyAt<3.2)return;if(Step==0){int32 Count=0;float Gain=-1;for(TObjectIterator<UAudioComponent> I;I;++I)if(I->GetWorld()==W&&I->IsPlaying())if(auto* Wave=Cast<USoundWaveProcedural>(I->Sound))if(Wave->NumChannels==2){++Count;Gain=I->VolumeMultiplier;}if(Count!=1||!FMath::IsNearlyEqual(Gain,1.6f,.035f))return;}
 if(!Pending.IsEmpty()){if(!FPaths::FileExists(Pending)||Now-At<.7)return;Pending.Empty();}if(Now-At<.85)return;At=Now;
 if(Step==0){
  if(Mode==TEXT("persist")){if(!Vol(0,1)||!Vol(1,.45f)||!Vol(2,.95f)||!Vol(3,.95f)||!Vol(4,.95f)||!Disk())return;}
  else {const float D[]={1,.4f,1,1,1};for(int32 I=0;I<5;++I)if(!Vol(I,D[I]))return;}
  Tap(PC,EKeys::Escape);for(int I=0;I<3;++I)Tap(PC,EKeys::Right);Tap(PC,EKeys::A);
  if(!Check(ParisCombatUI::IsOpen(PC)&&UGameplayStatics::IsGamePaused(W)&&ParisCombatUI::Inspect(PC)->GetIntegerField(TEXT("settings_tab"))==1,TEXT("Actual Esc pause/settings/audio navigation")))return;
  Image(PC,ParisLanguage::Chinese()?TEXT("audio_zh"):TEXT("audio_en"));++Step;return;
 }
 if(Step==50){Finish(TEXT("pass_audio_defaults"),TEXT("Actual restore defaults row and disk persistence"));return;}
 if(Step==1){if(Mode==TEXT("defaults")){Go(PC,0);Tap(PC,EKeys::Left);Go(PC,5);Tap(PC,EKeys::Enter);const float D[]={1,.4f,1,1,1};for(int I=0;I<5;++I)if(!Vol(I,D[I]))return;if(!Disk())return;Image(PC,TEXT("audio_defaults_zh"));Step=50;return;}if(!Snapshot(W,PC,TEXT("menu_music"),Mode==TEXT("persist")?.45f:.4f))return;if(Mode==TEXT("persist")){Finish(TEXT("pass_audio_persistence"),TEXT("Fresh process read actual audio preferences and retained one paused music stream"));return;}
  UAudioMixerBlueprintLibrary::StartRecordingOutput(W,20);Recording=true;
  for(int32 I=0;I<5;++I){Go(PC,I);Tap(PC,EKeys::Left);if(!Vol(I,I==1?.35f:.95f))return;}if(!Disk())return;++Step;return;
 }
 if(Step==2){
  // Native mouse hit path in the same scaled reference geometry as the renderer.
  int32 X=0,Y=0;PC->GetViewportSize(X,Y);const double S=FMath::Min(X/1920.,Y/1080.);
  PC->SetMouseLocation(int32((X-1920*S)/2+(1000+520*.62)*S),int32((Y-1080*S)/2+(439+72+25)*S));
  Tap(PC,EKeys::LeftMouseButton);if(!Vol(1,.62f)||!Check(ParisCombatUI::Inspect(PC)->GetIntegerField(TEXT("audio_drag"))==-1,TEXT("Mouse release finishes and persists slider"))||!Disk())return;
  Tap(PC,EKeys::L);if(!Check(!ParisLanguage::Chinese(),TEXT("Live English audio labels")))return;Image(PC,TEXT("audio_en_adjusted"));++Step;return;
 }
 if(Step==3){if(!Snapshot(W,PC,TEXT("partial_master"),.95f*.62f))return;Go(PC,0);for(int I=0;I<20;++I)Tap(PC,EKeys::Left);if(!Vol(0,0))return;++Step;return;}
 if(Step==4){if(!Snapshot(W,PC,TEXT("master_muted"),0))return;Go(PC,0);for(int I=0;I<20;++I)Tap(PC,EKeys::Right);Go(PC,1);for(int I=0;I<20;++I)Tap(PC,EKeys::Left);if(!Vol(0,1)||!Vol(1,0))return;++Step;return;}
 if(Step==5){if(!Snapshot(W,PC,TEXT("music_muted"),0))return;Go(PC,1);for(int I=0;I<9;++I)Tap(PC,EKeys::Right);if(!Vol(1,.45f)||!Disk())return;++Step;return;}
 if(Step==6){if(!Snapshot(W,PC,TEXT("unmuted"),.45f))return;Tap(PC,EKeys::L);Image(PC,TEXT("audio_zh_adjusted"));++Step;return;}
 if(Step==7){if(Recording){UAudioMixerBlueprintLibrary::StopRecordingOutput(W,EAudioRecordingExportType::WavFile,TEXT("actual_menu_mix"),Out);Recording=false;}Tap(PC,EKeys::D);Image(PC,TEXT("display_zh"));++Step;return;}
 if(Step==8){Tap(PC,EKeys::Escape);if(!Check(!ParisCombatUI::IsOpen(PC)&&!UGameplayStatics::IsGamePaused(W),TEXT("Original menu closes/unpauses")))return;Finish(TEXT("pass_audio_native_ui"),TEXT("Native keyboard/mouse five controls, disk preferences, mixer master multiplication, pause/music mute lifecycle and bilingual frames"));}
}
bool Tick(float){if(GEngine)for(auto& C:GEngine->GetWorldContexts())if(auto* W=C.World())if(W->IsGameWorld()){TickWorld(W);break;}return !Done;}
}
void Initialize(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisAudioCheck="),Mode)||!FParse::Value(FCommandLine::Get(),TEXT("ParisAudioOut="),Out))return;IFileManager::Get().MakeDirectory(*Out,true);Begin=At=FPlatformTime::Seconds();Handle=FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateStatic(&Tick));}
void Shutdown(){if(Handle.IsValid())FTSTicker::GetCoreTicker().RemoveTicker(Handle);}
}
