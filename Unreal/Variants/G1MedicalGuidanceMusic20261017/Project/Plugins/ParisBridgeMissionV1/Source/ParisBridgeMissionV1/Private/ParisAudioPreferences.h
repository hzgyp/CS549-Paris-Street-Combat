#pragma once
#include "CoreMinimal.h"
class USoundBase;
class UWorld;
namespace ParisAudioPreferences {
enum class EBus : uint8 { Master,Music,Ambience,Effects,Voice };
void Initialize();
void Shutdown();
float Volume(EBus Bus);
void SetVolume(EBus Bus,float Value);
void Defaults();
// Independent per-user preference; never touches a checkpoint or changes gameplay.
bool Save();
void Route(UWorld* World,USoundBase* Sound,EBus Bus);
}
