#include "ParisGameplayAV.h"
#include "ParisBridgeMission.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/AnimSequence.h"
#include "AudioMixerBlueprintLibrary.h"
#include "BrainComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "AIController.h"
#include "Components/AudioComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "HAL/FileManager.h"
#include "HAL/PlatformProcess.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/FileHelper.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundWaveProcedural.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UnrealType.h"

namespace ParisGameplayAV
{
namespace
{
bool Flag(const UObject* O,const TCHAR* Key)
{auto* P=O?FindFProperty<FBoolProperty>(O->GetClass(),Key):nullptr;return P&&P->GetPropertyValue_InContainer(O);}
double Number(const UObject* O,const TCHAR* Key)
{
 auto* P=O?FindFProperty<FNumericProperty>(O->GetClass(),Key):nullptr;if(!P)return -1;
 const void* V=P->ContainerPtrToValuePtr<void>(O);return P->IsFloatingPoint()?P->GetFloatingPointPropertyValue(V):P->GetSignedIntPropertyValue(V);
}
FName Action(const UObject* O)
{auto* P=O?FindFProperty<FNameProperty>(O->GetClass(),TEXT("ActionState")):nullptr;return P?P->GetPropertyValue_InContainer(O):NAME_None;}
uint32 LE(const uint8* P){return uint32(P[0])|(uint32(P[1])<<8)|(uint32(P[2])<<16)|(uint32(P[3])<<24);}
struct FCue{TArray<uint8> PCM;float Seconds=0;};
struct FTrack
{
 FVector Position;int64 Shots=0;double Loaded=0,Distance=0;bool Dead=false,Grounded=true;
 FName State=NAME_None;int32 Variation=0;TMap<FString,int32> Counts;
};
struct FVoice
{
 TStrongObjectPtr<USoundWaveProcedural> Wave;TWeakObjectPtr<UAudioComponent> Component;double End=0;
 FVoice(USoundWaveProcedural* W,UAudioComponent* C,double E):Wave(W),Component(C),End(E){}
 FVoice(FVoice&&)=default;FVoice& operator=(FVoice&&)=default;
};
struct FSession
{
 TMap<FString,FCue> Cues;TMap<TWeakObjectPtr<ACharacter>,FTrack> Actors;TArray<FVoice> Voices;
 TStrongObjectPtr<USoundAttenuation> Near;TStrongObjectPtr<USoundAttenuation> Far;TStrongObjectPtr<USoundAttenuation> Impact;
 TArray<TSharedPtr<FJsonValue>> Events;FString AuditDir,Generation;bool Capture=false,Ready=false;
};
TMap<UWorld*,TUniquePtr<FSession>> Sessions;FDelegateHandle CleanupHandle;
TStrongObjectPtr<USoundAttenuation> Attenuation(float Radius,float Falloff)
{
 auto* A=NewObject<USoundAttenuation>();auto& S=A->Attenuation;
 S.bAttenuate=true;S.bSpatialize=true;S.AttenuationShape=EAttenuationShape::Sphere;
 S.AttenuationShapeExtents=FVector(Radius,0,0);S.FalloffDistance=Falloff;
 S.DistanceAlgorithm=EAttenuationDistanceModel::Logarithmic;
 return TStrongObjectPtr<USoundAttenuation>(A);
}
void Write(FSession& S)
{
 if(S.AuditDir.IsEmpty())return;
 auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("generation"),S.Generation);
 O->SetBoolField(TEXT("cues_ready"),S.Ready);O->SetBoolField(TEXT("master_mix_recorded"),S.Capture);
 O->SetArrayField(TEXT("events"),S.Events);TArray<TSharedPtr<FJsonValue>> Actors;
 for(const auto& Pair:S.Actors)
 {
  auto A=MakeShared<FJsonObject>();A->SetStringField(TEXT("actor"),Pair.Key.IsValid()?Pair.Key->GetName():TEXT("expired"));
  for(const auto& Count:Pair.Value.Counts)A->SetNumberField(Count.Key,Count.Value);
  Actors.Add(MakeShared<FJsonValueObject>(A));
 }
 O->SetArrayField(TEXT("actors"),Actors);FString J;auto W=TJsonWriterFactory<>::Create(&J);FJsonSerializer::Serialize(O,W);
 FFileHelper::SaveStringToFile(J,*(S.AuditDir/TEXT("audio_events_")+S.Generation+TEXT(".json")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM);
}
void Cleanup(UWorld* World,bool,bool)
{
 auto* P=Sessions.Find(World);if(!P)return;FSession& S=*P->Get();
 for(auto& V:S.Voices)if(V.Component.IsValid())V.Component->Stop();S.Voices.Empty();
 if(S.Capture)UAudioMixerBlueprintLibrary::StopRecordingOutput(World,EAudioRecordingExportType::WavFile,TEXT("game_mix_")+S.Generation,S.AuditDir);
 Write(S);Sessions.Remove(World);
}
void Play(UWorld* W,FSession& S,ACharacter* C,FTrack& Track,const FString& Cue,float Volume=1)
{
 if(!S.Ready||!S.Cues.Contains(Cue)||S.Voices.Num()>=24)return;
 const FCue& Data=S.Cues[Cue];auto* Wave=NewObject<USoundWaveProcedural>();
 Wave->SetSampleRate(48000);Wave->NumChannels=1;Wave->Duration=Data.Seconds;Wave->SoundGroup=SOUNDGROUP_Effects;
 Wave->bLooping=false;Wave->QueueAudio(Data.PCM.GetData(),Data.PCM.Num());
 const float Gain=.72f*Volume;const bool Gun=Cue==TEXT("fire"),Death=Cue==TEXT("death");
 auto* Settings=Gun?S.Far.Get():Death?S.Impact.Get():S.Near.Get();
 if(auto* Camera=UGameplayStatics::GetPlayerCameraManager(W,0))
  if(FVector::DistSquared(Camera->GetCameraLocation(),C->GetActorLocation())>FMath::Square(Settings->Attenuation.GetMaxDimension()))return;
 auto* Component=UGameplayStatics::SpawnSoundAtLocation(W,Wave,C->GetActorLocation(),FRotator::ZeroRotator,Gain,1,0,Settings,nullptr,true);
 if(!Component){UE_LOG(LogTemp,Error,TEXT("PARIS_AV_AUDIO_PLAY_FAILED cue=%s"),*Cue);return;}
 S.Voices.Emplace(Wave,Component,W->GetTimeSeconds()+Data.Seconds+.15);
 ++Track.Counts.FindOrAdd(Cue);
 if(!S.AuditDir.IsEmpty())
 {
  auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("actor"),C->GetName());E->SetStringField(TEXT("cue"),Cue);
  E->SetNumberField(TEXT("time"),W->GetTimeSeconds());E->SetNumberField(TEXT("shots"),Number(C,TEXT("ShotSequence")));
  E->SetNumberField(TEXT("health"),Number(C,TEXT("Health")));E->SetBoolField(TEXT("dead"),Flag(C,TEXT("IsDead")));
  E->SetNumberField(TEXT("volume"),Gain);
  if(Death)if(auto* Single=C->GetMesh()->GetSingleNodeInstance())
  {E->SetBoolField(TEXT("death_clip_playing"),Single->IsPlaying());E->SetNumberField(TEXT("death_clip_time"),Single->GetCurrentTime());E->SetNumberField(TEXT("death_clip_length"),Single->GetLength());E->SetStringField(TEXT("death_clip"),Single->GetCurrentAsset()?Single->GetCurrentAsset()->GetName():TEXT("None"));}
  S.Events.Add(MakeShared<FJsonValueObject>(E));
  UE_LOG(LogTemp,Display,TEXT("PARIS_AV_AUDIO actor=%s cue=%s time=%.3f shots=%.0f"),*C->GetName(),*Cue,W->GetTimeSeconds(),Number(C,TEXT("ShotSequence")));
 }
}
}
void Initialize(){if(!CleanupHandle.IsValid())CleanupHandle=FWorldDelegates::OnWorldCleanup.AddStatic(&Cleanup);}
void Shutdown()
{
 TArray<UWorld*> Worlds;Sessions.GetKeys(Worlds);for(auto* W:Worlds)Cleanup(W,false,false);
 if(CleanupHandle.IsValid())FWorldDelegates::OnWorldCleanup.Remove(CleanupHandle);CleanupHandle.Reset();
}
void Prime(AParisBridgeMission* Mission,const TArray<TObjectPtr<ACharacter>>& Roster)
{
 auto* W=Mission->GetWorld();if(Sessions.Contains(W))Cleanup(W,false,false);
 auto State=MakeUnique<FSession>();auto& S=*State;S.Generation=Mission->RunGeneration;
 S.Near=Attenuation(140,2200);S.Far=Attenuation(300,16000);S.Impact=Attenuation(120,6000);
 const FString Dir=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPlatformProcess::BaseDir(),TEXT("../../Audio")));
 S.Ready=true;
 for(const TCHAR* Name:{TEXT("step_walk_a"),TEXT("step_walk_b"),TEXT("step_run_a"),TEXT("step_run_b"),TEXT("step_slow_a"),TEXT("step_slow_b"),TEXT("crawl"),TEXT("fire"),TEXT("death"),TEXT("reload"),TEXT("reload_end"),TEXT("land")})
 {
  TArray<uint8> Bytes;const bool Loaded=FFileHelper::LoadFileToArray(Bytes,*(Dir/(FString(Name)+TEXT(".wav"))));
  const bool Valid=Loaded&&Bytes.Num()>44&&FMemory::Memcmp(Bytes.GetData(),"RIFF",4)==0&&FMemory::Memcmp(Bytes.GetData()+8,"WAVEfmt ",8)==0&&
   LE(Bytes.GetData()+16)==16&&Bytes[20]==1&&Bytes[21]==0&&Bytes[22]==1&&Bytes[23]==0&&LE(Bytes.GetData()+24)==48000&&
   Bytes[32]==2&&Bytes[33]==0&&Bytes[34]==16&&Bytes[35]==0&&FMemory::Memcmp(Bytes.GetData()+36,"data",4)==0&&
   LE(Bytes.GetData()+40)==uint32(Bytes.Num()-44)&&(Bytes.Num()-44)%2==0;
  if(!Valid){S.Ready=false;UE_LOG(LogTemp,Error,TEXT("PARIS_AV_CUE_INVALID %s"),Name);continue;}
  FCue C;C.PCM.Append(Bytes.GetData()+44,Bytes.Num()-44);C.Seconds=C.PCM.Num()/96000.f;
  S.Cues.Add(Name,MoveTemp(C));
 }
 for(const auto& Pawn:Roster)if(auto* C=Pawn.Get();IsValid(C))
 {
  FTrack T;T.Position=C->GetActorLocation();T.Shots=int64(Number(C,TEXT("ShotSequence")));T.Loaded=Number(C,TEXT("LoadedAmmo"));
  T.Dead=Flag(C,TEXT("IsDead"));T.State=Action(C);T.Grounded=C->GetCharacterMovement()->IsMovingOnGround();S.Actors.Add(C,MoveTemp(T));
 }
 if(FParse::Value(FCommandLine::Get(),TEXT("ParisAVAuditOut="),S.AuditDir))
 {
  IFileManager::Get().MakeDirectory(*S.AuditDir,true);UAudioMixerBlueprintLibrary::StartRecordingOutput(W,150);S.Capture=true;
 }
 UE_LOG(LogTemp,Display,TEXT("PARIS_AV_PRIMED cues=%d ready=%d restored=%d events=0"),S.Cues.Num(),S.Ready,W->URL.HasOption(TEXT("ParisLoad")));
 Sessions.Add(W,MoveTemp(State));
}
void Tick(AParisBridgeMission* Mission,const TArray<TObjectPtr<ACharacter>>& Roster)
{
 auto* W=Mission->GetWorld();auto* P=Sessions.Find(W);if(!P)return;FSession& S=*P->Get();
 for(int32 I=S.Voices.Num()-1;I>=0;--I)if(!S.Voices[I].Component.IsValid()||W->GetTimeSeconds()>=S.Voices[I].End)
 {if(S.Voices[I].Component.IsValid())S.Voices[I].Component->Stop();S.Voices.RemoveAtSwap(I);}
 for(const auto& Pawn:Roster)if(auto* C=Pawn.Get();IsValid(C))
 {
  auto* T=S.Actors.Find(C);if(!T)continue;const FVector Position=C->GetActorLocation();
  const bool Dead=Flag(C,TEXT("IsDead")),Ground=C->GetCharacterMovement()->IsMovingOnGround();
  const int64 Shots=int64(Number(C,TEXT("ShotSequence")));const double Loaded=Number(C,TEXT("LoadedAmmo"));
  const FName State=Action(C);
  if(Shots>T->Shots)Play(W,S,C,*T,TEXT("fire"),1);
  if(Dead&&!T->Dead)Play(W,S,C,*T,TEXT("death"),.65);
  if(!Dead)
  {
   if(State==TEXT("Reloading")&&T->State!=State)Play(W,S,C,*T,TEXT("reload"),.55);
   if(Loaded>T->Loaded&&T->State==TEXT("Reloading"))Play(W,S,C,*T,TEXT("reload_end"),.55);
   if(Ground&&!T->Grounded)Play(W,S,C,*T,TEXT("land"),.6);
   const double Delta=FVector::Dist2D(Position,T->Position),Speed=C->GetVelocity().Size2D();
   const double Posture=Number(C,TEXT("DesiredPosture"));
   if(Ground&&Speed>12&&Delta>0&&Delta<250&&State!=TEXT("Reloading"))
   {
    const double Stride=Posture==2?38:Flag(C,TEXT("PC_IsRunning"))||Speed>220?105:Speed<90?55:82;
    T->Distance+=Delta;
    if(T->Distance>=Stride)
    {
     T->Distance=FMath::Fmod(T->Distance,Stride);
     const FString Base=Posture==2?TEXT("crawl"):Speed>220?TEXT("step_run"):Speed<90?TEXT("step_slow"):TEXT("step_walk");
     const FString Cue=Posture==2?Base:Base+(T->Variation++%2?TEXT("_b"):TEXT("_a"));
     Play(W,S,C,*T,Cue,Posture==2?.32:Posture==1?.42:Speed<90?.35:.65);
    }
   }
   else if(!Ground||Speed<2||Delta>=250)T->Distance=0;
  }
  T->Position=Position;T->Shots=Shots;T->Loaded=Loaded;T->Dead=Dead;T->State=State;T->Grounded=Ground;
 }
}
bool RestoreTerminalDeath(ACharacter* C,FString& Error)
{
 auto* Mesh=C?C->GetMesh():nullptr;auto* Single=Mesh?Mesh->GetSingleNodeInstance():nullptr;
 auto* Clip=Single?Cast<UAnimSequence>(Single->GetCurrentAsset()):nullptr;
 if(!Flag(C,TEXT("IsDead"))||!Clip||Clip->GetName()!=TEXT("Rifle_Death_3")||Single->GetLength()<=0)
 {Error=TEXT("Saved death requires the existing single-node Rifle_Death_3.");return false;}
 const float End=Single->GetLength();Single->SetPosition(End,false);Single->SetPlaying(false);
 Mesh->TickAnimation(0,false);Mesh->RefreshBoneTransforms();Mesh->UpdateComponentToWorld();
 UE_LOG(LogTemp,Display,TEXT("PARIS_AV_RESTORE_DEAD actor=%s clip=%s position=%.6f playing=0 notifies=0"),*C->GetName(),*Clip->GetPathName(),End);
 return true;
}
bool VerifyRestoredCorpses(UWorld* W,FString& Error)
{
 int32 Corpses=0;
 for(TActorIterator<ACharacter> I(W);I;++I)if(I->ActorHasTag(TEXT("G1_German1"))||I->ActorHasTag(TEXT("G1_German2"))||I->ActorHasTag(TEXT("G1_German3")))
 {
  auto* C=*I;auto* S=C->GetMesh()->GetSingleNodeInstance();auto* A=Cast<AAIController>(C->GetController());
  if(!Flag(C,TEXT("IsDead"))||Number(C,TEXT("Health"))!=0||!S||S->IsPlaying()||FMath::Abs(S->GetCurrentTime()-S->GetLength())>.001||
     C->GetCapsuleComponent()->GetCollisionEnabled()!=ECollisionEnabled::NoCollision||C->GetCharacterMovement()->MovementMode!=MOVE_None||
     (A&&A->GetBrainComponent()&&A->GetBrainComponent()->IsRunning()))
  {Error=TEXT("Saved corpse terminal-pose/lifecycle gate failed: ")+C->GetName();return false;}
  ++Corpses;
 }
 if(Corpses!=3){Error=TEXT("Saved corpse roster is incomplete.");return false;}return true;
}
FString Inspect(UWorld* W)
{
 auto O=MakeShared<FJsonObject>();auto* S=Sessions.Find(W);O->SetBoolField(TEXT("primed"),S!=nullptr);
 if(S){O->SetBoolField(TEXT("ready"),(*S)->Ready);O->SetNumberField(TEXT("events"),(*S)->Events.Num());O->SetNumberField(TEXT("voices"),(*S)->Voices.Num());}
 FString J;auto Writer=TJsonWriterFactory<>::Create(&J);FJsonSerializer::Serialize(O,Writer);return J;
}
}
