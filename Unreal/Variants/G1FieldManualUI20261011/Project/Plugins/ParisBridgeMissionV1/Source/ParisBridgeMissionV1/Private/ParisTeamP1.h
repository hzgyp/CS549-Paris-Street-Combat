#pragma once
#include "CoreMinimal.h"
class ACharacter;
class AParisBridgeMission;
namespace ParisTeamP1 {
bool ConfigureFreshLoadout(ACharacter* Player);
bool ConfigureFreshLayout(AParisBridgeMission* Mission,FString& Error);
void UpdatePlayerMovement(ACharacter* Player,bool Paused);
// North-up map, centimetres. The texture covers only the retained survey bounds.
constexpr double RadarRadiusCm=2500.0;
FVector2D RadarPoint(FVector World,FVector Player,double CX,double CY,double R);
FVector2D SurveyUV(FVector World);
TArray<FVector2D> ClipSurvey(const TArray<FVector2D>& Polygon);
}
namespace ParisP1Probe {void Initialize();void Shutdown();}
