#pragma once
#include "CoreMinimal.h"

class ACharacter;

// Presentation only. The medical gameplay owner retains input, time and resource authority.
namespace ParisMedicalAction {
bool Ready(ACharacter* Player);
bool Begin(ACharacter* Player, double DurationSeconds);
// False requires cancellation BEFORE the gameplay owner considers healing/consumption.
bool Tick(ACharacter* Player, double ElapsedSeconds, double DurationSeconds);
void End(ACharacter* Player);
// Call from the medical owner's module shutdown; End is sufficient per pawn/world lifecycle.
void Shutdown();
}
