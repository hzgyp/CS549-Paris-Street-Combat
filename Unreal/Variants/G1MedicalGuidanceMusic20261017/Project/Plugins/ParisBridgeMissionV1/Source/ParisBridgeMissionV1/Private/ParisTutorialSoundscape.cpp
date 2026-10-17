#include "ParisTutorialSoundscape.h"
#include "ParisTutorialMusicPolicy.h"
#include "ParisAudioPreferences.h"
#include "HAL/PlatformTime.h"
#include "ParisBridgeMission.h"
#include "ParisTutorial.h"
#include "ParisCombatUI.h"
#include "Components/AudioComponent.h"
#include "Containers/Ticker.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "HAL/PlatformProcess.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Sound/SoundWaveProcedural.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"

namespace ParisTutorialSoundscape
{
namespace
{
struct FCue { TArray<uint8> PCM; float Seconds=0; int32 Channels=1; };
struct FPlayback
{
 TStrongObjectPtr<USoundWaveProcedural> Wave;
 TStrongObjectPtr<UAudioComponent> Component;
 FPlayback(USoundWaveProcedural* W,UAudioComponent* C):Wave(W),Component(C){}
 ~FPlayback(){if(Component.IsValid()){Component->Stop();Component->DestroyComponent();}}
};
struct FDialogue {int32 Ally=-1;bool Joined=false;};
struct FSession
{
 TWeakObjectPtr<AParisBridgeMission> Mission;
 FString Generation;
 TMap<FString,FCue> Cues;
 TUniquePtr<FPlayback> Wind,River,Voice,UI,Distant,Music,MenuUI;
 double MenuEndReal=0,LastNavigateReal=-100;
 float MusicGain=0;
 TArray<FDialogue> Pending;
 FDialogue Current;
 double VoiceEnd=0,UIEnd=0,DistantEnd=0,NextDistant=0,LastGreeting[2]={-100,-100};
 bool JoinedAdmitted[2]={false,false},Suspended=false,Blocked=true;
 float WindGain=0,RiverGain=0;
 int32 LastSaveSerial=-1;
 FRandomStream AmbienceRandom{0x17A0D10}; // Never consume gameplay/AI global random state.
};
TMap<UWorld*,TUniquePtr<FSession>> Sessions;
FDelegateHandle CleanupHandle;
FTSTicker::FDelegateHandle TickHandle;

bool Dead(const ACharacter* C)
{
 if(!IsValid(C))return true;
 const auto* P=FindFProperty<FNumericProperty>(C->GetClass(),TEXT("Health"));
 if(!P)return true;
 const void* V=P->ContainerPtrToValuePtr<void>(C);
 return (P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):double(P->GetSignedIntPropertyValue(V)))<=0;
}
ACharacter* Pawn(UWorld* W,int32 Ally)
{
 const FName Tag(Ally<0?TEXT("G1_Player"):Ally==0?TEXT("G1_Ally1"):TEXT("G1_Ally2"));
 for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(Tag))return *I;
 return nullptr;
}
bool Blocked(const AParisBridgeMission* M)
{
 if(!IsValid(M)||!ParisTutorial::Enabled())return true;
 auto* W=M->GetWorld();if(!W||W->bIsTearingDown||UGameplayStatics::IsGamePaused(W))return true;
 const FString& P=M->Phase;
 if(P!=TEXT("Training")&&P!=TEXT("TrainingCheckpoint")&&P!=TEXT("Crossing")&&P!=TEXT("Clearing")&&P!=TEXT("Occupying")&&P!=TEXT("Won"))return true;
 auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));
 return ParisCombatUI::IsOpen(PC)||Dead(Pawn(W,-1));
}
void StopGameplay(FSession& S)
{
 S.Wind.Reset();S.River.Reset();S.Voice.Reset();S.UI.Reset();S.Distant.Reset();
 S.Pending.Empty();S.Current=FDialogue();S.VoiceEnd=0;S.WindGain=S.RiverGain=0;
}
void Stop(FSession& S){StopGameplay(S);S.Music.Reset();S.MenuUI.Reset();S.MusicGain=0;}
void Cleanup(UWorld* W,bool,bool){Sessions.Remove(W);}
uint32 LE(const uint8* B){return uint32(B[0])|(uint32(B[1])<<8)|(uint32(B[2])<<16)|(uint32(B[3])<<24);}
void Load(FSession& S)
{
 const FString Dir=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../Audio/Tutorial")));
 for(const TCHAR* Id:{TEXT("street_wind"),TEXT("river_water"),TEXT("distant_report"),TEXT("ally1_greeting"),TEXT("ally1_joined"),TEXT("ally2_greeting"),TEXT("ally2_joined"),TEXT("checkpoint_ok"),TEXT("tutorial_complete"),TEXT("menu_navigate"),TEXT("menu_confirm"),TEXT("menu_back"),TEXT("background_music")})
 {
  TArray<uint8> B;
  const bool Valid=FFileHelper::LoadFileToArray(B,*(Dir/(FString(Id)+TEXT(".wav"))))&&B.Num()>44&&
   FMemory::Memcmp(B.GetData(),"RIFF",4)==0&&LE(B.GetData()+4)==uint32(B.Num()-8)&&FMemory::Memcmp(B.GetData()+8,"WAVEfmt ",8)==0&&
   LE(B.GetData()+16)==16&&B[20]==1&&B[21]==0&&(B[22]==1||(FString(Id)==TEXT("background_music")&&B[22]==2))&&B[23]==0&&LE(B.GetData()+24)==48000&&LE(B.GetData()+28)==uint32(96000*B[22])&&
   B[32]==2*B[22]&&B[33]==0&&B[34]==16&&B[35]==0&&FMemory::Memcmp(B.GetData()+36,"data",4)==0&&LE(B.GetData()+40)==uint32(B.Num()-44)&&(B.Num()-44)%(2*B[22])==0;
  if(!Valid){UE_LOG(LogTemp,Warning,TEXT("PARIS_SOUNDSCAPE_CUE_MISSING_OR_INVALID %s; gameplay unaffected"),Id);continue;}
  FCue C;C.Channels=B[22];C.PCM.Append(B.GetData()+44,B.Num()-44);C.Seconds=C.PCM.Num()/(96000.f*C.Channels);S.Cues.Add(Id,MoveTemp(C));
 }
}
TUniquePtr<FPlayback> Play(UWorld* W,const FCue* Cue,float Gain,bool Loop=false,ParisAudioPreferences::EBus Bus=ParisAudioPreferences::EBus::Ambience,bool UI=false)
{
 if(!Cue)return nullptr;
 auto* Wave=NewObject<USoundWaveProcedural>();Wave->SetSampleRate(48000);Wave->NumChannels=Cue->Channels;
 Wave->Duration=Loop?INDEFINITELY_LOOPING_DURATION:Cue->Seconds;
 Wave->SoundGroup=Bus==ParisAudioPreferences::EBus::Voice?SOUNDGROUP_Voice:Bus==ParisAudioPreferences::EBus::Music?SOUNDGROUP_Music:SOUNDGROUP_Effects;Wave->bLooping=false;
 ParisAudioPreferences::Route(W,Wave,Bus);
 if(Loop)Wave->VirtualizationMode=EVirtualizationMode::PlayWhenSilent;
 Wave->QueueAudio(Cue->PCM.GetData(),Cue->PCM.Num());
 // Two-dimensional mix for the nearby interaction; pause never treats speech as UI audio.
 auto* C=UGameplayStatics::CreateSound2D(W,Wave,Gain,1.f,0.f,nullptr,false,false);
 if(!C)return nullptr;
 C->bIsUISound=UI;C->Play();return MakeUnique<FPlayback>(Wave,C);
}
void Loop(UWorld* W,FSession& S,TUniquePtr<FPlayback>& P,const TCHAR* Id,float Gain,ParisAudioPreferences::EBus Bus=ParisAudioPreferences::EBus::Ambience,bool UI=false)
{
 const FCue* C=S.Cues.Find(Id);if(!C)return;
 if(!P)P=Play(W,C,Gain,true,Bus,UI);
 if(!P)return;
 // Supply complete circular PCM blocks before underflow, without restarting the component.
 if(P->Wave->GetAvailableAudioByteCount()<96000*C->Channels)P->Wave->QueueAudio(C->PCM.GetData(),C->PCM.Num());
 P->Component->SetVolumeMultiplier(Gain);
}
FString VoiceId(const FDialogue& D)
{return FString::Printf(TEXT("ally%d_%s"),D.Ally+1,D.Joined?TEXT("joined"):TEXT("greeting"));}
float MusicTarget(const AParisBridgeMission* M,bool MenuOpen,bool Speaking)
{
 if(!IsValid(M))return 0.f;
 using namespace ParisTutorialMusicPolicy;
 const EContext Context=M->Phase==TEXT("Ready")?EContext::Opening:
  MenuOpen?EContext::Pause:
  M->Phase==TEXT("Won")?EContext::Secured:
  !ParisTutorial::CombatStarted(M)?EContext::Training:
  M->LivingDefenders<=0?EContext::Secured:
  M->Phase==TEXT("Clearing")?EContext::Combat:EContext::Approach;
 return Target(Context,Speaking);
}
void StartVoice(UWorld* W,FSession& S,FDialogue D)
{
 if(D.Ally<0||D.Ally>1||Dead(Pawn(W,D.Ally)))return;
 const auto* C=S.Cues.Find(VoiceId(D));if(!C)return;
 S.Voice=Play(W,C,.85f,false,ParisAudioPreferences::EBus::Voice);if(!S.Voice)return;
 S.Current=D;S.VoiceEnd=W->GetTimeSeconds()+FMath::Max(1.6f,C->Seconds+.12f);
 // Make the first spoken syllable audible; recover smoothly after the line ends.
 if(S.Music){S.MusicGain=FMath::Min(S.MusicGain,MusicTarget(S.Mission.Get(),false,true));S.Music->Component->SetVolumeMultiplier(S.MusicGain);}
 UE_LOG(LogTemp,Display,TEXT("PARIS_SOUNDSCAPE_VOICE ally=%d joined=%d cue=%s"),D.Ally+1,D.Joined,*VoiceId(D));
}
FSession* Find(AParisBridgeMission* M)
{
 if(!IsValid(M))return nullptr;
 auto* P=Sessions.Find(M->GetWorld());if(!P||(*P)->Generation!=M->RunGeneration||(*P)->Suspended||Blocked(M))return nullptr;
 return P->Get();
}
bool Tick(float Delta)
{
 // Core ticker also runs while the world is paused: discard interrupted speech rather than resume it.
 for(auto& Pair:Sessions)
 {
  auto& S=*Pair.Value;auto* M=S.Mission.Get();
  if(!M||S.Suspended||S.Generation!=M->RunGeneration||!M->GetWorld()||M->GetWorld()->bIsTearingDown)
  {Stop(S);S.Blocked=true;continue;}
  auto* W=M->GetWorld();const double Now=W->GetTimeSeconds();
  if(S.MenuUI&&FPlatformTime::Seconds()>=S.MenuEndReal)S.MenuUI.Reset();
  auto* PC=Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(W,0));
  const bool MenuOpen=ParisCombatUI::IsOpen(PC),PlayBlocked=Blocked(M);
  if(!Dead(Pawn(W,-1))&&(MenuOpen||M->Phase==TEXT("Ready")||!PlayBlocked)){
   const float Target=MusicTarget(M,MenuOpen,bool(S.Voice));
   S.MusicGain=FMath::FInterpTo(S.MusicGain,Target,Delta,Target<S.MusicGain?5.f:2.5f);
   Loop(W,S,S.Music,TEXT("background_music"),S.MusicGain,ParisAudioPreferences::EBus::Music,true);
  }else{S.Music.Reset();S.MusicGain=0;}
  if(PlayBlocked){StopGameplay(S);S.Blocked=true;continue;}
  if(S.Blocked){S.Blocked=false;S.NextDistant=Now+20;}
  if(S.Voice&&(Now>=S.VoiceEnd||Dead(Pawn(W,S.Current.Ally)))){S.Voice.Reset();S.Current=FDialogue();}
  if(!S.Voice&&!S.Pending.IsEmpty())
  {const auto D=S.Pending[0];S.Pending.RemoveAt(0);StartVoice(W,S,D);}
  if(S.UI&&Now>=S.UIEnd)S.UI.Reset();
  if(S.Distant&&Now>=S.DistantEnd)S.Distant.Reset();
  const float Duck=S.Voice?.30f:1.f;
  if(S.Distant)S.Distant->Component->SetVolumeMultiplier(.16f*Duck);
  S.WindGain=FMath::FInterpTo(S.WindGain,.16f*Duck,Delta,1.2f);
  // Local C-bridge water zone anchored at the witnessed bridge constraint; no full-river claim.
  FVector At=Pawn(W,-1)->GetActorLocation();At.Z=0;
  const float Proximity=FMath::Clamp(1.f-float(FVector::Dist2D(At,FVector(5200,-20800,0))-900)/3200.f,0.f,1.f);
  const float Smooth=Proximity*Proximity*(3.f-2.f*Proximity);
  S.RiverGain=FMath::FInterpTo(S.RiverGain,.20f*Smooth*Duck,Delta,1.2f);
  Loop(W,S,S.Wind,TEXT("street_wind"),S.WindGain);
  // Avoid virtualizing a zero-volume procedural source before its first audible approach.
  if(S.RiverGain>.002f||S.River)Loop(W,S,S.River,TEXT("river_water"),FMath::Max(.001f,S.RiverGain));
  const bool Combat=ParisTutorial::CombatStarted(M)&&M->Phase!=TEXT("Won");
  if(!Combat){S.Distant.Reset();S.NextDistant=Now+20;}
  else if(Now>=S.NextDistant&&!S.Voice&&!S.UI&&!ParisTutorial::DialogVisible(M))
  {
   const auto* C=S.Cues.Find(TEXT("distant_report"));S.Distant=Play(W,C,.16f);
   S.DistantEnd=Now+(C?C->Seconds:0)+.1;S.NextDistant=Now+S.AmbienceRandom.FRandRange(18.f,30.f);
  }
 }
 return true;
}
}
void Initialize()
{
 if(!CleanupHandle.IsValid())CleanupHandle=FWorldDelegates::OnWorldCleanup.AddStatic(&Cleanup);
 if(!TickHandle.IsValid())TickHandle=FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateStatic(&Tick),.05f);
}
void Shutdown()
{
 if(TickHandle.IsValid())FTSTicker::GetCoreTicker().RemoveTicker(TickHandle);TickHandle.Reset();
 if(CleanupHandle.IsValid())FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);CleanupHandle.Reset();Sessions.Empty();
}
void Prime(AParisBridgeMission* M)
{
 if(!IsValid(M)||!ParisTutorial::Enabled())return;
 Initialize();Sessions.Remove(M->GetWorld());auto S=MakeUnique<FSession>();
 S->Mission=M;S->Generation=M->RunGeneration;S->LastSaveSerial=M->SaveSerial;Load(*S);
 UE_LOG(LogTemp,Display,TEXT("PARIS_SOUNDSCAPE_PRIMED cues=%d historical_dialogue_replayed=0"),S->Cues.Num());
 Sessions.Add(M->GetWorld(),MoveTemp(S));
}
void Suspend(AParisBridgeMission* M)
{
 if(!M)return;if(auto* P=Sessions.Find(M->GetWorld())){auto& S=*P->Get();Stop(S);S.Suspended=true;S.Blocked=true;}
}
void Menu(AParisBridgeMission* M,EMenuCue Cue)
{
 if(!IsValid(M)||!ParisTutorial::Enabled()||!ParisCombatUI::IsOpen(Cast<AParisBridgePlayerController>(UGameplayStatics::GetPlayerController(M,0))))return;
 auto* P=Sessions.Find(M->GetWorld());if(!P)return;auto& S=*P->Get();
 if(S.Suspended||S.Generation!=M->RunGeneration||M->GetWorld()->bIsTearingDown)return;
 const double Now=FPlatformTime::Seconds();
 if(Cue==EMenuCue::Navigate&&(Now-S.LastNavigateReal<.08||(S.MenuUI&&Now<S.MenuEndReal)))return;
 if(Cue==EMenuCue::Navigate)S.LastNavigateReal=Now;
 const TCHAR* Id=Cue==EMenuCue::Navigate?TEXT("menu_navigate"):Cue==EMenuCue::Back?TEXT("menu_back"):TEXT("menu_confirm");
 const auto* C=S.Cues.Find(Id);S.MenuUI=Play(M->GetWorld(),C,.35f,false,ParisAudioPreferences::EBus::Effects,true);
 S.MenuEndReal=Now+(C?C->Seconds:0)+.08;
}
void Greeting(AParisBridgeMission* M,int32 Ally)
{
 auto* S=Find(M);if(!S||Ally<0||Ally>1)return;
 const double Now=M->GetWorld()->GetTimeSeconds();
 if(S->Voice||!S->Pending.IsEmpty()||Now-S->LastGreeting[Ally]<6)return;
 S->LastGreeting[Ally]=Now;StartVoice(M->GetWorld(),*S,{Ally,false});
}
void CancelGreeting(AParisBridgeMission* M,int32 Ally)
{
 auto* S=Find(M);if(!S)return;
 if(S->Voice&&S->Current.Ally==Ally&&!S->Current.Joined){S->Voice.Reset();S->Current=FDialogue();}
}
void Recruited(AParisBridgeMission* M,int32 Ally)
{
 auto* S=Find(M);if(!S||Ally<0||Ally>1||S->JoinedAdmitted[Ally]||Dead(Pawn(M->GetWorld(),Ally)))return;
 S->JoinedAdmitted[Ally]=true;
 // Successful recruitment cannot be lost behind a greeting. Only two designated recruits exist.
 if(S->Voice){if(S->Pending.Num()<2)S->Pending.Add({Ally,true});}
 else StartVoice(M->GetWorld(),*S,{Ally,true});
}
void Saved(AParisBridgeMission* M,bool Complete)
{
 auto* S=Find(M);if(!S||M->SaveSerial<=S->LastSaveSerial)return;
 S->LastSaveSerial=M->SaveSerial;const auto* C=S->Cues.Find(Complete?TEXT("tutorial_complete"):TEXT("checkpoint_ok"));
 S->UI=Play(M->GetWorld(),C,.30f,false,ParisAudioPreferences::EBus::Effects);S->UIEnd=M->GetWorld()->GetTimeSeconds()+(C?C->Seconds:0)+.1;
}
FString Subtitle(const AParisBridgeMission* M)
{
 if(!M||Blocked(M))return FString();const auto* P=Sessions.Find(M->GetWorld());if(!P)return FString();
 const auto& S=*P->Get();if(S.Suspended||S.Generation!=M->RunGeneration||!S.Voice||M->GetWorld()->GetTimeSeconds()>=S.VoiceEnd||Dead(Pawn(M->GetWorld(),S.Current.Ally)))return FString();
 const FDialogue& D=S.Current;
 return D.Ally==0?(D.Joined?TEXT("ALLY 1: Go!"):TEXT("ALLY 1: Ready!")):(D.Joined?TEXT("ALLY 2: Yes."):TEXT("ALLY 2: Hey."));
}
}
