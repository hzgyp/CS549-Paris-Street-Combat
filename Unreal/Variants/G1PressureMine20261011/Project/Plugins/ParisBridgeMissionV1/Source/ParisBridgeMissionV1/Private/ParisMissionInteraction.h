#pragma once
#include "CoreMinimal.h"

namespace ParisMissionInteraction {
inline bool MenuPhase(const FString& Phase) {
    return Phase==TEXT("Ready") || Phase==TEXT("Lost") || Phase==TEXT("Error");
}
inline FVector2D ScreenPoint(FVector2D P,FIntPoint Size) {
    const double S=FMath::Min(Size.X/1920.,Size.Y/1080.);
    return FVector2D((Size.X-1920*S)*.5,(Size.Y-1080*S)*.5)+P*S;
}
inline int32 MenuHit(FVector2D Screen,FIntPoint Size) {
    if(Size.X<=0 || Size.Y<=0)return INDEX_NONE;
    const double S=FMath::Min(Size.X/1920.,Size.Y/1080.);
    const FVector2D P=(Screen-FVector2D((Size.X-1920*S)*.5,(Size.Y-1080*S)*.5))/S;
    if(P.X<750 || P.X>1170)return INDEX_NONE;
    for(int32 I=0;I<3;++I)if(P.Y>=750+I*58 && P.Y<=794+I*58)return I;
    return INDEX_NONE;
}
inline int32 CheckpointHit(FVector2D Screen,FIntPoint Size,bool Failure) {
    if(Size.X<=0 || Size.Y<=0)return INDEX_NONE;
    const double S=FMath::Min(Size.X/1920.,Size.Y/1080.);
    const FVector2D P=(Screen-FVector2D((Size.X-1920*S)*.5,(Size.Y-1080*S)*.5))/S;
    if(P.Y<622 || P.Y>666)return INDEX_NONE;
    if(!Failure)return P.X>=810 && P.X<=1110?0:INDEX_NONE;
    if(P.X>=670 && P.X<=930)return 0;
    return P.X>=990 && P.X<=1250?1:INDEX_NONE;
}
}

namespace ParisInteractionProbe { void Initialize(); void Shutdown(); }
