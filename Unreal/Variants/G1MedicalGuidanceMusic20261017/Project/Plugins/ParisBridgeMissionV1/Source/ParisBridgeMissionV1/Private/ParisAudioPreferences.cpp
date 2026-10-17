#include "ParisAudioPreferences.h"
#include "AudioDevice.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/ConfigCacheIni.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundClass.h"
#include "Sound/SoundMix.h"
#include "UObject/StrongObjectPtr.h"

namespace ParisAudioPreferences {
namespace {
constexpr float DefaultValues[]={1.f,.4f,1.f,1.f,1.f};
const TCHAR* Keys[]={TEXT("Master"),TEXT("Music"),TEXT("Ambience"),TEXT("Effects"),TEXT("Voice")};
constexpr auto Section=TEXT("ParisAudioPreferences");
float Values[]={1.f,.4f,1.f,1.f,1.f};
bool Loaded=false;
struct FMix {
 TStrongObjectPtr<USoundClass> Classes[5];
 TStrongObjectPtr<USoundMix> Mix;
};
TMap<UWorld*,TUniquePtr<FMix>> Mixes;
FDelegateHandle CleanupHandle;
int32 Index(EBus Bus){return FMath::Clamp(int32(Bus),0,4);}
void Load(){
 if(Loaded)return;Loaded=true;
 for(int32 I=0;I<5;++I){float V=DefaultValues[I];if(GConfig)GConfig->GetFloat(Section,Keys[I],V,GGameUserSettingsIni);Values[I]=FMath::IsFinite(V)?FMath::Clamp(V,0.f,1.f):DefaultValues[I];}
}
void Apply(UWorld* W,FMix& M){
 for(int32 I=0;I<5;++I)UGameplayStatics::SetSoundMixClassOverride(W,M.Mix.Get(),M.Classes[I].Get(),Values[I],1.f,0.f,I==0);
}
void Cleanup(UWorld* W,bool,bool){
 if(auto* M=Mixes.Find(W))UGameplayStatics::PopSoundMixModifier(W,(*M)->Mix.Get());
 Mixes.Remove(W);
}
FMix* Ensure(UWorld* W){
 if(!IsValid(W)||W->bIsTearingDown)return nullptr;
 if(auto* Existing=Mixes.Find(W))return Existing->Get();
 auto Audio=W->GetAudioDevice();if(!Audio.IsValid())return nullptr;
 auto M=MakeUnique<FMix>();
 for(int32 I=0;I<5;++I)M->Classes[I].Reset(NewObject<USoundClass>());
 for(int32 I=1;I<5;++I){M->Classes[I]->ParentClass=M->Classes[0].Get();M->Classes[0]->ChildClasses.Add(M->Classes[I].Get());}
 // Transient runtime classes have no PostLoad: register the complete tree explicitly.
 for(auto& C:M->Classes)Audio->RegisterSoundClass(C.Get());
 M->Mix.Reset(NewObject<USoundMix>());M->Mix->Duration=-1;M->Mix->InitialDelay=0;M->Mix->FadeInTime=0;M->Mix->FadeOutTime=0;
 for(int32 I=0;I<5;++I){FSoundClassAdjuster A;A.SoundClassObject=M->Classes[I].Get();A.VolumeAdjuster=1;A.PitchAdjuster=1;A.bApplyToChildren=I==0;M->Mix->SoundClassEffects.Add(A);}
 auto* Result=M.Get();Mixes.Add(W,MoveTemp(M));Apply(W,*Result);UGameplayStatics::PushSoundMixModifier(W,Result->Mix.Get());return Result;
}
}
void Initialize(){Load();if(!CleanupHandle.IsValid())CleanupHandle=FWorldDelegates::OnWorldCleanup.AddStatic(&Cleanup);}
void Shutdown(){
 for(auto& Pair:Mixes)if(IsValid(Pair.Key))UGameplayStatics::PopSoundMixModifier(Pair.Key,Pair.Value->Mix.Get());
 Mixes.Empty();if(CleanupHandle.IsValid())FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);CleanupHandle.Reset();
}
float Volume(EBus Bus){Load();return Values[Index(Bus)];}
void SetVolume(EBus Bus,float Value){
 Load();const int32 I=Index(Bus);const float Next=FMath::IsFinite(Value)?FMath::Clamp(Value,0.f,1.f):DefaultValues[I];
 if(FMath::IsNearlyEqual(Values[I],Next,.00001f))return;Values[I]=Next;
 for(auto& Pair:Mixes)if(IsValid(Pair.Key)&&!Pair.Key->bIsTearingDown)Apply(Pair.Key,*Pair.Value);
}
void Defaults(){Load();for(int32 I=0;I<5;++I)Values[I]=DefaultValues[I];for(auto& Pair:Mixes)if(IsValid(Pair.Key)&&!Pair.Key->bIsTearingDown)Apply(Pair.Key,*Pair.Value);}
bool Save(){
 Load();if(!GConfig||GGameUserSettingsIni.IsEmpty())return false;
 for(int32 I=0;I<5;++I)GConfig->SetFloat(Section,Keys[I],Values[I],GGameUserSettingsIni);
 GConfig->Flush(false,GGameUserSettingsIni);
 // Read actual disk bytes, rather than accepting values from the in-memory cache.
 const auto* Branch=GConfig->FindBranch(NAME_None,GGameUserSettingsIni);if(!Branch||Branch->IniPath.IsEmpty())return false;
 FConfigFile Disk;Disk.Read(Branch->IniPath);
 for(int32 I=0;I<5;++I){float V=-1;if(!Disk.GetFloat(Section,Keys[I],V)||!FMath::IsFinite(V)||!FMath::IsNearlyEqual(V,Values[I],.0001f))return false;}
 return true;
}
void Route(UWorld* W,USoundBase* Sound,EBus Bus){Initialize();if(!Sound)return;if(auto* M=Ensure(W))Sound->SoundClassObject=M->Classes[Index(Bus)].Get();}
}
