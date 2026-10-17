#pragma once
#include "CoreMinimal.h"
class UFont;
namespace ParisLanguage {
bool Chinese();
void SetChinese(bool Chinese);
FString Text(const FString& Source);
UFont* Font(UFont* EnglishFont);
void Initialize();
void Shutdown();
}
