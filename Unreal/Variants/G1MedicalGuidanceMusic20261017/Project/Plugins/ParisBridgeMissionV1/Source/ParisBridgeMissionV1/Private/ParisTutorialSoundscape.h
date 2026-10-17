#pragma once
#include "CoreMinimal.h"
class AParisBridgeMission;
namespace ParisTutorialSoundscape
{
enum class EMenuCue : uint8 { Navigate,Confirm,Back };
void Menu(AParisBridgeMission* Mission,EMenuCue Cue);
void Initialize();
void Shutdown();
void Prime(AParisBridgeMission* Mission);
void Suspend(AParisBridgeMission* Mission);
void Greeting(AParisBridgeMission* Mission,int32 Ally);
void CancelGreeting(AParisBridgeMission* Mission,int32 Ally);
void Recruited(AParisBridgeMission* Mission,int32 Ally);
void Saved(AParisBridgeMission* Mission,bool Complete);
// English source text: the HUD translates it on every draw, never caches a chosen language.
FString Subtitle(const AParisBridgeMission* Mission);
}
