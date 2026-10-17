// Bounded opt-in native menu language test; normal entry has no probe behavior.
#include "ParisLanguage.h"
#include "Containers/Ticker.h"
#include "Engine/Engine.h"
#include "ParisBridgeMission.h"
#include "ParisCombatUI.h"
#include "Engine/World.h"
#include "Misc/Paths.h"
#include "Kismet/GameplayStatics.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/FileHelper.h"
#include "HAL/FileManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
namespace ParisLanguage {
namespace {
FTSTicker::FDelegateHandle Handle;FString Mode,Out,Pending;int32 Step=0,Assertions=0;double At=0,Begin=0;bool Done=false;
void Finish(const FString& Status,const FString& Why){if(Done)return;Done=true;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("status"),Status);O->SetStringField(TEXT("reason"),Why);O->SetNumberField(TEXT("assertions"),Assertions);O->SetStringField(TEXT("language"),Chinese()?TEXT("zh-Hans"):TEXT("en"));O->SetStringField(TEXT("scope"),TEXT("Actual menu keyboard language switching/persistence and same renderer screenshots; no gameplay/resource/save mutation"));FString Raw;FJsonSerializer::Serialize(O,TJsonWriterFactory<>::Create(&Raw));FFileHelper::SaveStringToFile(Raw,*(Out/TEXT("RESULT.json")));FPlatformMisc::RequestExit(false);}
bool Check(bool Good,const TCHAR* Why){++Assertions;if(!Good)Finish(TEXT("failed_language"),Why);return Good;}
void Tap(AParisBridgePlayerController* PC,FKey K){for(auto E:{IE_Pressed,IE_Released})PC->InputKey(FInputKeyEventArgs::CreateSimulated(K,E,E==IE_Pressed?1.f:0.f));}
void Image(AParisBridgePlayerController* PC,const TCHAR* Name){Pending=Out/(FString(Name)+TEXT(".png"));PC->ConsoleCommand(FString::Printf(TEXT("Shot SHOWUI -nosuffix filename=%s"),*Pending),false);At=FPlatformTime::Seconds();}
void TickWorld(UWorld* W,ELevelTick,float){if(Done||!W||!W->IsGameWorld())return;if(FPlatformTime::Seconds()-Begin>80){Finish(TEXT("failed_language_timeout"),TEXT("bounded native menu check"));return;}auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));if(!M||!PC||M->Phase!=TEXT("Ready"))return;if(!Pending.IsEmpty()){if(!FPaths::FileExists(Pending)||FPlatformTime::Seconds()-At<.6)return;Pending.Empty();}if(Step==0){
 bool Expected=Mode!=TEXT("persist_en");if(!Check(Chinese()==Expected,TEXT("Default or persisted language")))return;
 if(!Check(Text(TEXT("CP0 TRAINING"))==(Expected?TEXT("CP0 教学存档点"):TEXT("CP0 TRAINING")),TEXT("Exact display translation")))return;
 if(Expected&&!Check(Text(TEXT("2 / 3 guards eliminated"))==TEXT("已消灭守卫 2 / 3"),TEXT("Dynamic numeric translation")))return;
 Image(PC,Expected?TEXT("ready_zh"):TEXT("ready_en"));++Step;return;}
 if(Step==1){Tap(PC,EKeys::Escape);for(int I=0;I<3;++I)Tap(PC,EKeys::Right);if(!Check(ParisCombatUI::IsOpen(PC)&&ParisCombatUI::Inspect(PC)->GetIntegerField(TEXT("page"))==3,TEXT("Native settings navigation")))return;Image(PC,Chinese()?TEXT("settings_zh"):TEXT("settings_en"));++Step;return;}
 if(Step==2){const bool Old=Chinese();Tap(PC,EKeys::L);if(!Check(Chinese()!=Old,TEXT("Native language toggle")))return;if(!Check(Text(TEXT("CHECKPOINTS"))==(Chinese()?TEXT("存档管理"):TEXT("CHECKPOINTS")),TEXT("Display cache follows toggle")))return;Image(PC,Chinese()?TEXT("settings_switched_zh"):TEXT("settings_switched_en"));++Step;return;}
 if(Step==3){if(Mode==TEXT("set_en")||Mode==TEXT("persist_en")){Finish(TEXT("pass_language_persistence"),TEXT("Read saved preference in fresh process; native toggle written"));return;}Tap(PC,EKeys::L);if(!Check(Chinese(),TEXT("Return to Simplified Chinese")))return;for(int I=0;I<3;++I)Tap(PC,EKeys::Left);Image(PC,TEXT("mission_zh"));++Step;return;}
 if(Step==4){Tap(PC,EKeys::Right);Image(PC,TEXT("squad_zh"));++Step;return;}
 if(Step==5){Tap(PC,EKeys::Right);Image(PC,TEXT("controls_zh"));++Step;return;}
 if(Step==6){ParisCombatUI::ShowCheckpointList(PC);Image(PC,TEXT("checkpoints_zh"));++Step;return;}
 if(Step==7){Tap(PC,EKeys::Escape);Tap(PC,EKeys::Escape);if(!Check(!ParisCombatUI::IsOpen(PC),TEXT("Original pause menu closes")))return;Finish(TEXT("pass_language_native_ui"),TEXT("Chinese menu/HUD, dynamic text, native switch/cache and remembered preference"));}
}
}
bool Tick(float Delta){if(GEngine)for(const auto& Context:GEngine->GetWorldContexts())if(auto* W=Context.World())if(W->IsGameWorld()){TickWorld(W,LEVELTICK_All,Delta);break;}return !Done;}
void Initialize(){if(!FParse::Value(FCommandLine::Get(),TEXT("ParisLanguageCheck="),Mode)||!FParse::Value(FCommandLine::Get(),TEXT("ParisLanguageOut="),Out))return;IFileManager::Get().MakeDirectory(*Out,true);Begin=FPlatformTime::Seconds();Handle=FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateStatic(&Tick));}
void Shutdown(){if(Handle.IsValid())FTSTicker::GetCoreTicker().RemoveTicker(Handle);}
}
