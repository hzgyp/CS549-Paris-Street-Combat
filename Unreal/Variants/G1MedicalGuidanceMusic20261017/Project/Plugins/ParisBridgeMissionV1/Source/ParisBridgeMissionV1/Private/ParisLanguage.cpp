// Presentation-only translation. Never rewrites mission state or save payloads.
#include "ParisLanguage.h"
#include "Engine/Font.h"
#include "Fonts/CompositeFont.h"
#include "UObject/StrongObjectPtr.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/ConfigCacheIni.h"
#include "Internationalization/Regex.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
namespace ParisLanguage {
namespace {
int32 Selected=-1;
TMap<FString,FString> Exact,Cache;
struct FPattern {FString Source,Target,Regex;int32 Count=0;};
TArray<FPattern> Patterns;
TSet<FString> Missing;
FString UI(){return FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../UI")));}
void Load(){
 static bool Loaded=false;if(Loaded)return;Loaded=true;
 FString Raw;checkf(FFileHelper::LoadFileToString(Raw,*(UI()/TEXT("zh-Hans.json"))),TEXT("Packaged zh-Hans catalogue required"));
 TSharedPtr<FJsonObject> Root;check(FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Raw),Root));
 for(const auto& Pair:Root->GetObjectField(TEXT("exact"))->Values){const FString Key(*Pair.Key);Exact.Add(Key,Pair.Value->AsString());Exact.Add(Key.ToUpper(),Pair.Value->AsString());}
 for(const auto& Value:Root->GetArrayField(TEXT("patterns"))){auto P=Value->AsObject();Patterns.Add({P->GetStringField(TEXT("source")),P->GetStringField(TEXT("target")),P->GetStringField(TEXT("regex")),int32(P->GetNumberField(TEXT("count")))});}
 UE_LOG(LogTemp,Display,TEXT("PARIS_LANGUAGE_CATALOG exact=%d patterns=%d"),Exact.Num(),Patterns.Num());
}
FString Translate(const FString& Source,int32 Depth){
 if(const auto* V=Exact.Find(Source))return *V;
 if(const auto* V=Exact.Find(Source.ToUpper()))return *V;
 if(Depth<3)for(const auto& P:Patterns){FRegexMatcher Match(FRegexPattern(P.Regex),Source);if(!Match.FindNext())continue;FString Result=P.Target;
  for(int32 I=0;I<P.Count;++I)Result.ReplaceInline(*FString::Printf(TEXT("{%d}"),I),*Translate(Match.GetCaptureGroup(I+1),Depth+1));return Result;}
 if(Source.Contains(TEXT("\n"))){TArray<FString> Lines;Source.ParseIntoArrayLines(Lines,false);for(auto& Line:Lines)Line=Translate(Line,Depth+1);return FString::Join(Lines,TEXT("\n"));}
 if(Source.Len()>5&&!Missing.Contains(Source)){Missing.Add(Source);UE_LOG(LogTemp,Display,TEXT("PARIS_LANGUAGE_UNTRANSLATED %s"),*Source);}
 return Source;
}
}
bool Chinese(){if(Selected<0){FString Value;GConfig->GetString(TEXT("ParisLanguage"),TEXT("Language"),Value,GGameUserSettingsIni);FParse::Value(FCommandLine::Get(),TEXT("ParisLanguage="),Value);Selected=Value.Equals(TEXT("en"),ESearchCase::IgnoreCase)?0:1;}return Selected==1;}
void SetChinese(bool Value){Selected=Value?1:0;Cache.Empty();GConfig->SetString(TEXT("ParisLanguage"),TEXT("Language"),Value?TEXT("zh-Hans"):TEXT("en"),GGameUserSettingsIni);GConfig->Flush(false,GGameUserSettingsIni);UE_LOG(LogTemp,Display,TEXT("PARIS_LANGUAGE_CHANGED selected=%s preference=%s"),Value?TEXT("zh-Hans"):TEXT("en"),*GGameUserSettingsIni);}
FString Text(const FString& Source){if(!Chinese()||Source.IsEmpty())return Source;Load();if(const auto* V=Cache.Find(Source))return *V;auto Result=Translate(Source,0);if(Cache.Num()>1024)Cache.Empty();Cache.Add(Source,Result);return Result;}
UFont* Font(UFont* EnglishFont){if(!Chinese())return EnglishFont;static TStrongObjectPtr<UFont> Held;if(!Held.IsValid()){const FString File=UI()/TEXT("DroidSansFallback.ttf");check(FPaths::FileExists(File));Held.Reset(NewObject<UFont>());Held->FontCacheType=EFontCacheType::Runtime;Held->GetMutableInternalCompositeFont()=FCompositeFont(FName(TEXT("Regular")),File,EFontHinting::Default,EFontLoadingPolicy::LazyLoad);UE_LOG(LogTemp,Display,TEXT("PARIS_LANGUAGE_FONT loaded=%s"),*File);}return Held.Get();}
}
