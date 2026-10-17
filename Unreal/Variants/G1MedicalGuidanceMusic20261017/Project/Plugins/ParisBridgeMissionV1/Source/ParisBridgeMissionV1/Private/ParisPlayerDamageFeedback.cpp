// Presentation only: observe actual health after the original damage/save lifecycle.
#include "ParisPlayerDamageFeedback.h"
#include "ParisBridgeMission.h"
#include "ParisCombatUI.h"
#include "ParisPlayerDeath.h"
#include "ParisEquipmentState.h"
#include "ParisTacticalEquipment.h"
#include "AudioMixerBlueprintLibrary.h"
#include "AIController.h"
#include "BrainComponent.h"
#include "ParisAudioPreferences.h"
#include "Components/AudioComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Canvas.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "HAL/PlatformProcess.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/App.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#include "Sound/SoundWaveProcedural.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"
#include "UObject/StructOnScope.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "InputKeyEventArgs.h"
#include "InputCoreTypes.h"
#include "UnrealClient.h"

namespace ParisPlayerDamageFeedback {
namespace {
double Num(const UObject* O,const TCHAR* Key){auto* F=O?FindFProperty<FNumericProperty>(O->GetClass(),Key):nullptr;if(!F)return -1;const auto* V=F->ContainerPtrToValuePtr<void>(O);return F->IsFloatingPoint()?F->GetFloatingPointPropertyValue(V):F->GetSignedIntPropertyValue(V);}
bool Dead(const ACharacter* P){auto* F=P?FindFProperty<FBoolProperty>(P->GetClass(),TEXT("IsDead")):nullptr;return !P||Num(P,TEXT("Health"))<=0||(F&&F->GetPropertyValue_InContainer(P));}
struct FState {
 TWeakObjectPtr<ACharacter> Player;FString Generation;double Restore=-1;
 bool Primed=false,Enabled=false,CueAttempted=false,CueReady=false;
 double Health=0,Max=100,Trail=0,HitAt=-100,Peak=0,VoiceAt=-100,VoiceEnd=-100;
 int32 DamageCount=0,VoiceCount=0,LimitedCount=0,ResetCount=0,DrawFrames=0;
 double LastDelta=0,MaxAlpha=0,LastObservedAt=0;
 TArray<uint8> PCM;TStrongObjectPtr<USoundWaveProcedural> Wave;
 TWeakObjectPtr<UAudioComponent> Voice;
 TArray<TSharedPtr<FJsonValue>> Events;
};
TMap<TWeakObjectPtr<UWorld>,FState> States;FDelegateHandle TickHandle,PreHandle,CleanupHandle;
void StopVoice(FState& S){if(S.Voice.IsValid())S.Voice->Stop();S.Voice.Reset();S.Wave.Reset();S.VoiceEnd=-100;}
void ClearVisual(FState& S){StopVoice(S);S.Trail=S.Health;S.Peak=0;S.HitAt=-100;}
uint32 LE(const uint8* P){return uint32(P[0])|(uint32(P[1])<<8)|(uint32(P[2])<<16)|(uint32(P[3])<<24);}
void LoadCue(FState& S){
 if(S.CueAttempted)return;S.CueAttempted=true;
 FString File=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../Audio/player_hurt.wav")));
 if(!FPaths::FileExists(File))File=FPaths::ProjectDir()/TEXT("Audio/player_hurt.wav");TArray<uint8> B;
 S.CueReady=FFileHelper::LoadFileToArray(B,*File)&&B.Num()>44&&FMemory::Memcmp(B.GetData(),"RIFF",4)==0&&FMemory::Memcmp(B.GetData()+8,"WAVEfmt ",8)==0&&LE(B.GetData()+16)==16&&B[20]==1&&B[21]==0&&B[22]==1&&B[23]==0&&LE(B.GetData()+24)==48000&&B[32]==2&&B[33]==0&&B[34]==16&&B[35]==0&&FMemory::Memcmp(B.GetData()+36,"data",4)==0&&LE(B.GetData()+40)==uint32(B.Num()-44);
 if(S.CueReady)S.PCM.Append(B.GetData()+44,B.Num()-44);else UE_LOG(LogTemp,Error,TEXT("PARIS_PLAYER_HURT_CUE_INVALID %s"),*File);
}
void PlayHurt(UWorld* W,FState& S){
 const double Now=W->GetTimeSeconds();if(Now-S.VoiceAt<.15){++S.LimitedCount;return;}LoadCue(S);if(!S.CueReady)return;StopVoice(S);
 auto* Wave=NewObject<USoundWaveProcedural>();Wave->SetSampleRate(48000);Wave->NumChannels=1;Wave->Duration=S.PCM.Num()/96000.f;Wave->SoundGroup=SOUNDGROUP_Effects;Wave->bLooping=false;ParisAudioPreferences::Route(W,Wave,ParisAudioPreferences::EBus::Effects);Wave->QueueAudio(S.PCM.GetData(),S.PCM.Num());
 auto* Voice=UGameplayStatics::SpawnSound2D(W,Wave,.70f,1.f,0.f,nullptr,false,true);
 if(!Voice){UE_LOG(LogTemp,Error,TEXT("PARIS_PLAYER_HURT_AUDIO_FAILED"));return;}S.Wave.Reset(Wave);S.Voice=Voice;S.VoiceAt=Now;S.VoiceEnd=Now+Wave->Duration; ++S.VoiceCount;
}
double TrailHealth(UWorld* W,const FState& S){const double T=FMath::Clamp((W->GetTimeSeconds()-S.HitAt-.12)/.45,0.,1.);return FMath::Max(S.Health,FMath::Lerp(S.Trail,S.Health,T));}
bool Visible(UWorld* W,const FState& S){auto* M=AParisBridgeMission::Find(W);auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));return S.Enabled&&S.Player.IsValid()&&!Dead(S.Player.Get())&&M&&!M->CheckpointDialogVisible()&&(M->AllowsPlay()||M->Phase==TEXT("Won"))&&!UGameplayStatics::IsGamePaused(W)&&!ParisCombatUI::IsOpen(PC)&&!ParisPlayerDeath::Presenting(W);}
double Alpha(UWorld* W,const FState& S){
 if(!Visible(W,S))return 0;const double Age=W->GetTimeSeconds()-S.HitAt;
 const double Envelope=Age<0||Age>=.6?0:Age<.06?.35+.65*Age/.06:Age<.16?1:1-(Age-.16)/.44;
 return FMath::Clamp(FMath::Max(S.Peak*Envelope,S.Health/S.Max<=.25?.04:0.),0.,.22);
}
void Tick(UWorld* W,ELevelTick,float){
 if(!W||!W->IsGameWorld())return;auto* M=AParisBridgeMission::Find(W);auto* P=UGameplayStatics::GetPlayerCharacter(W,0);if(!M||!P)return;
 auto& S=States.FindOrAdd(W);const double HP=Num(P,TEXT("Health")),Max=Num(P,TEXT("MaxHealth")),Restore=Num(P,TEXT("RestoreGeneration")),Now=W->GetTimeSeconds();
 if(!FMath::IsFinite(HP)||HP<0||!FMath::IsFinite(Max)||Max<=0){ClearVisual(S);S.Enabled=false;S.Primed=false;return;}
 const bool Active=M->AllowsPlay()||M->Phase==TEXT("Won");
 if(!S.Primed||S.Player.Get()!=P||S.Generation!=M->RunGeneration||S.Restore!=Restore){S.Health=HP;ClearVisual(S);S.Player=P;S.Generation=M->RunGeneration;S.Restore=Restore;S.Max=Max;S.Primed=true;S.Enabled=Active&&!Dead(P);S.VoiceAt=-100;++S.ResetCount;S.LastObservedAt=Now;LoadCue(S);return;}
 S.Max=Max;S.LastObservedAt=Now;
 if(UGameplayStatics::IsGamePaused(W)){StopVoice(S);return;}
 if(S.Voice.IsValid()&&Now>=S.VoiceEnd)StopVoice(S);
 if(Dead(P)||!Active){S.Health=HP;ClearVisual(S);S.Enabled=false;return;}
 if(!S.Enabled){S.Health=HP;ClearVisual(S);S.Enabled=true;return;}
 const double Delta=S.Health-HP;
 if(Delta>.001){
  const double Old=S.Health,Trail=TrailHealth(W,S);S.Health=HP;S.Trail=FMath::Max(Trail,Old);S.HitAt=Now;S.Peak=FMath::Clamp(.10+Delta/Max*.30,.10,.22);S.LastDelta=Delta;++S.DamageCount;
  PlayHurt(W,S);
  if(S.Events.Num()<512){auto E=MakeShared<FJsonObject>();E->SetNumberField(TEXT("time"),Now);E->SetNumberField(TEXT("before"),Old);E->SetNumberField(TEXT("after"),HP);E->SetNumberField(TEXT("delta"),Delta);E->SetNumberField(TEXT("voices"),S.VoiceCount);S.Events.Add(MakeShared<FJsonValueObject>(E));}
 }else if(Delta<-.001){S.Health=HP;ClearVisual(S);}else S.Health=HP;
}
void Cleanup(UWorld* W,bool,bool){if(auto* S=States.Find(W))StopVoice(*S);States.Remove(W);}
void BeginTick(UWorld* W,ELevelTick,float){if(W&&W->IsGameWorld()&&UGameplayStatics::IsGamePaused(W))if(auto* S=States.Find(W))StopVoice(*S);}
}
void DrawEdges(AParisBridgeHUD* HUD,AParisBridgeMission* M,float Width,float Height){
 auto* W=HUD->GetWorld();auto* S=States.Find(W);if(!S)return;const double A=Alpha(W,*S);if(A<=0)return;
 constexpr int32 Bands=24;
 for(int32 I=0;I<Bands;++I){const float X=Width*.15f*I/Bands,Y=Height*.15f*I/Bands,DX=Width*.15f/Bands,DY=Height*.15f/Bands;const float T=1.f-(I+.5f)/Bands;const FLinearColor C(.68f,.025f,.018f,A*T*T);
  HUD->DrawRect(C,X,Y,DX,Height-2*Y);HUD->DrawRect(C,Width-X-DX,Y,DX,Height-2*Y);HUD->DrawRect(C,X+DX,Y,Width-2*(X+DX),DY);HUD->DrawRect(C,X+DX,Height-Y-DY,Width-2*(X+DX),DY);
 }
 ++S->DrawFrames;S->MaxAlpha=FMath::Max(S->MaxAlpha,A);
}
double TrailFraction(UWorld* W){const auto* S=States.Find(W);return S&&Visible(W,*S)?FMath::Clamp(TrailHealth(W,*S)/S->Max,0.,1.):0;}
bool CriticalVisible(UWorld* W){const auto* S=States.Find(W);return S&&Visible(W,*S)&&S->Health/S->Max<=.25;}
TSharedPtr<FJsonObject> Inspect(UWorld* W){auto O=MakeShared<FJsonObject>();const auto* S=States.Find(W);O->SetBoolField(TEXT("primed"),S&&S->Primed);O->SetBoolField(TEXT("visible"),S&&Visible(W,*S));O->SetBoolField(TEXT("critical"),CriticalVisible(W));O->SetBoolField(TEXT("cue_ready"),S&&S->CueReady);O->SetBoolField(TEXT("voice_active"),S&&S->Voice.IsValid()&&S->Voice->IsPlaying());O->SetNumberField(TEXT("health"),S?S->Health:-1);O->SetNumberField(TEXT("damage_count"),S?S->DamageCount:0);O->SetNumberField(TEXT("voice_count"),S?S->VoiceCount:0);O->SetNumberField(TEXT("limited_count"),S?S->LimitedCount:0);O->SetNumberField(TEXT("reset_count"),S?S->ResetCount:0);O->SetNumberField(TEXT("draw_frames"),S?S->DrawFrames:0);O->SetNumberField(TEXT("max_alpha"),S?S->MaxAlpha:0);O->SetNumberField(TEXT("alpha"),S?Alpha(W,*S):0);O->SetNumberField(TEXT("trail_health"),S?TrailHealth(W,*S):0);O->SetNumberField(TEXT("hit_age"),S?W->GetTimeSeconds()-S->HitAt:100);O->SetNumberField(TEXT("last_delta"),S?S->LastDelta:0);O->SetNumberField(TEXT("observed_at"),S?S->LastObservedAt:0);if(S)O->SetArrayField(TEXT("events"),S->Events);return O;}
#include "ParisPlayerDamageProbe.inl"
void Initialize(){TickHandle=FWorldDelegates::OnWorldPostActorTick.AddStatic(&Tick);PreHandle=FWorldDelegates::OnWorldTickStart.AddStatic(&BeginTick);CleanupHandle=FWorldDelegates::OnWorldCleanup.AddStatic(&Cleanup);InitializeProbe();}
void Shutdown(){ShutdownProbe();FWorldDelegates::OnWorldPostActorTick.Remove(TickHandle);FWorldDelegates::OnWorldTickStart.Remove(PreHandle);FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);for(auto& Pair:States)StopVoice(Pair.Value);States.Empty();}
}
