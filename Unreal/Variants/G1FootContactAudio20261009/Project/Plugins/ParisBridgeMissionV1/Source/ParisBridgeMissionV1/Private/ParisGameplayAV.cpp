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
struct FFoot {double Height=0,Drop=0,LastContact=-100,Low=0;bool Descending=false,Armed=true;};
struct FTrack
{
 FVector Position;int64 Shots=0;double Loaded=0,Distance=0;bool Dead=false,Grounded=true;
 FName State=NAME_None;int32 Variation=0;TMap<FString,int32> Counts;
 FFoot Feet[2];bool FeetInitialized=false,FootWarning=false;double FootPosture=-1,LastStep=-100;int32 ContactFoot=-1;
 double ReloadStart=-1;int64 ReloadToken=-1;bool ReloadOpened=false,ReloadInserted=false,ReloadClosed=false;
};
struct FVoice
{
 TStrongObjectPtr<USoundWaveProcedural> Wave;TWeakObjectPtr<UAudioComponent> Component;double End=0;
 TWeakObjectPtr<ACharacter> Owner;FString Cue;
 FVoice(USoundWaveProcedural* W,UAudioComponent* C,double E,ACharacter* O,const FString& N):Wave(W),Component(C),End(E),Owner(O),Cue(N){}
 FVoice(FVoice&&)=default;FVoice& operator=(FVoice&&)=default;
};
struct FSession
{
 TMap<FString,FCue> Cues;TMap<TWeakObjectPtr<ACharacter>,FTrack> Actors;TArray<FVoice> Voices;
 TStrongObjectPtr<USoundAttenuation> Near;TStrongObjectPtr<USoundAttenuation> Far;TStrongObjectPtr<USoundAttenuation> Impact;
 TArray<TSharedPtr<FJsonValue>> FootSamples;TArray<TSharedPtr<FJsonValue>> Events;FString AuditDir,Generation;bool Capture=false,Ready=false;
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
 O->SetArrayField(TEXT("foot_samples"),S.FootSamples);O->SetArrayField(TEXT("events"),S.Events);TArray<TSharedPtr<FJsonValue>> Actors;
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
 if(!S.AuditDir.IsEmpty()&&FParse::Param(FCommandLine::Get(),TEXT("ParisAVSoloPlayer"))&&!C->IsPlayerControlled())return;
 if(!S.Ready||!S.Cues.Contains(Cue)||S.Voices.Num()>=24)return;
 const FCue& Data=S.Cues[Cue];auto* Wave=NewObject<USoundWaveProcedural>();
 Wave->SetSampleRate(48000);Wave->NumChannels=1;Wave->Duration=Data.Seconds;Wave->SoundGroup=SOUNDGROUP_Effects;
 Wave->bLooping=false;Wave->QueueAudio(Data.PCM.GetData(),Data.PCM.Num());
 const float Gain=.72f*Volume;const bool Gun=Cue==TEXT("fire")||Cue==TEXT("fire_m1"),Death=Cue==TEXT("death");
 auto* Settings=Gun?S.Far.Get():Death?S.Impact.Get():S.Near.Get();
 if(auto* Camera=UGameplayStatics::GetPlayerCameraManager(W,0))
  if(FVector::DistSquared(Camera->GetCameraLocation(),C->GetActorLocation())>FMath::Square(Settings->Attenuation.GetMaxDimension()))return;
 auto* Component=UGameplayStatics::SpawnSoundAtLocation(W,Wave,C->GetActorLocation(),FRotator::ZeroRotator,Gain,1,0,Settings,nullptr,true);
 if(!Component){UE_LOG(LogTemp,Error,TEXT("PARIS_AV_AUDIO_PLAY_FAILED cue=%s"),*Cue);return;}
 S.Voices.Emplace(Wave,Component,W->GetTimeSeconds()+Data.Seconds+.15,C,Cue);
 ++Track.Counts.FindOrAdd(Cue);
 if(!S.AuditDir.IsEmpty())
 {
  auto E=MakeShared<FJsonObject>();E->SetStringField(TEXT("actor"),C->GetName());E->SetStringField(TEXT("cue"),Cue);
  E->SetNumberField(TEXT("time"),W->GetTimeSeconds());E->SetNumberField(TEXT("shots"),Number(C,TEXT("ShotSequence")));
  E->SetNumberField(TEXT("health"),Number(C,TEXT("Health")));E->SetBoolField(TEXT("dead"),Flag(C,TEXT("IsDead")));
  E->SetNumberField(TEXT("volume"),Gain);
  E->SetNumberField(TEXT("loaded"),Number(C,TEXT("LoadedAmmo")));E->SetNumberField(TEXT("reserve"),Number(C,TEXT("ReserveAmmo")));
  E->SetNumberField(TEXT("team"),Number(C,TEXT("TeamId")));E->SetNumberField(TEXT("reload_action"),Number(C,TEXT("ReloadActionID")));
  E->SetBoolField(TEXT("grounded"),C->GetCharacterMovement()->IsMovingOnGround());E->SetNumberField(TEXT("velocity_z"),C->GetVelocity().Z);
  E->SetStringField(TEXT("contact_foot"),Track.ContactFoot==0?TEXT("foot_l"):Track.ContactFoot==1?TEXT("foot_r"):TEXT("None"));
  if(Track.ContactFoot>=0)E->SetNumberField(TEXT("contact_height"),Track.Feet[Track.ContactFoot].Height);
  E->SetNumberField(TEXT("reload_age"),Track.ReloadStart<0?-1:W->GetTimeSeconds()-Track.ReloadStart);
  if(Death)if(auto* Single=C->GetMesh()->GetSingleNodeInstance())
  {E->SetBoolField(TEXT("death_clip_playing"),Single->IsPlaying());E->SetNumberField(TEXT("death_clip_time"),Single->GetCurrentTime());E->SetNumberField(TEXT("death_clip_length"),Single->GetLength());E->SetStringField(TEXT("death_clip"),Single->GetCurrentAsset()?Single->GetCurrentAsset()->GetName():TEXT("None"));}
  S.Events.Add(MakeShared<FJsonValueObject>(E));
  UE_LOG(LogTemp,Display,TEXT("PARIS_AV_AUDIO actor=%s cue=%s time=%.3f shots=%.0f"),*C->GetName(),*Cue,W->GetTimeSeconds(),Number(C,TEXT("ShotSequence")));
 }
}
void StopReloadVoices(FSession& S,ACharacter* C)
{
 int32 Stopped=0;
 for(int32 I=S.Voices.Num()-1;I>=0;--I)if(S.Voices[I].Owner.Get()==C&&S.Voices[I].Cue.StartsWith(TEXT("reload_")))
 {
  if(S.Voices[I].Component.IsValid())S.Voices[I].Component->FadeOut(.025f,0);
  S.Voices.RemoveAtSwap(I);++Stopped;
 }
 if(Stopped)UE_LOG(LogTemp,Display,TEXT("PARIS_FOLEY_RELOAD_STOP actor=%s voices=%d state=%s dead=%d"),*C->GetName(),Stopped,*Action(C).ToString(),Flag(C,TEXT("IsDead")));
}
void ReloadAudio(UWorld* W,FSession& S,ACharacter* C,FTrack& T,FName State,bool Dead,double Loaded)
{
 const int64 Token=int64(Number(C,TEXT("ReloadActionID")));
 if(Dead||State!=TEXT("Reloading"))
 {
  if(T.ReloadStart>=0)StopReloadVoices(S,C);
  T.ReloadStart=-1;T.ReloadOpened=T.ReloadInserted=T.ReloadClosed=false;return;
 }
 if(T.ReloadStart<0||T.ReloadToken!=Token)
 {
  StopReloadVoices(S,C);T.ReloadStart=W->GetTimeSeconds();T.ReloadToken=Token;
  T.ReloadOpened=T.ReloadInserted=T.ReloadClosed=false;
  Play(W,S,C,T,TEXT("reload_handling"),.35);
 }
 // Presentation only: derive each actor's original rate-aware duration. Never write ammo or action state.
 const double Duration=Number(C,TEXT("ReloadDuration")),Rate=Number(C,TEXT("ReloadPlayRate"));
 if(!FMath::IsFinite(Duration)||!FMath::IsFinite(Rate)||Duration<=0||Rate<=0)return;
 const double Length=Duration/Rate,Age=W->GetTimeSeconds()-T.ReloadStart;
 const FString Weapon=Number(C,TEXT("TeamId"))==1?TEXT("reload_k98_"):TEXT("reload_m1_");
 if(!T.ReloadOpened&&Age>=Length*.14){T.ReloadOpened=true;Play(W,S,C,T,Weapon+TEXT("open"),.55);}
 if(!T.ReloadInserted&&Loaded>T.Loaded){T.ReloadInserted=true;Play(W,S,C,T,Weapon+TEXT("load"),.55);}
 if(!T.ReloadClosed&&T.ReloadInserted&&Age>=Length*.68){T.ReloadClosed=true;Play(W,S,C,T,Weapon+TEXT("close"),.55);}
}
void PlayerFootAudio(UWorld* W,FSession& S,ACharacter* C,FTrack& T,FName State,bool Ground,double Speed,double Delta,double Posture)
{
 auto* Mesh=C->GetMesh();const FName Names[2]={TEXT("foot_l"),TEXT("foot_r")};
 if(!Mesh||Mesh->GetBoneIndex(Names[0])==INDEX_NONE||Mesh->GetBoneIndex(Names[1])==INDEX_NONE)
 {
  if(!T.FootWarning){T.FootWarning=true;UE_LOG(LogTemp,Error,TEXT("PARIS_FOOT_BONES_MISSING actor=%s"),*C->GetName());}
  T.FeetInitialized=false;return;
 }
 const double Z[2]={Mesh->GetSocketTransform(Names[0],RTS_Component).GetLocation().Z,Mesh->GetSocketTransform(Names[1],RTS_Component).GetLocation().Z};
 const double Now=W->GetTimeSeconds();
 const bool Moving=Ground&&Speed>12&&Delta>0&&Delta<250&&Posture<2&&State!=TEXT("Reloading");
 if(!S.AuditDir.IsEmpty()&&S.FootSamples.Num()<15000)
 {
  auto F=MakeShared<FJsonObject>();F->SetNumberField(TEXT("time"),Now);F->SetStringField(TEXT("actor"),C->GetName());
  F->SetNumberField(TEXT("left_z"),Z[0]);F->SetNumberField(TEXT("right_z"),Z[1]);F->SetNumberField(TEXT("speed"),Speed);
  F->SetNumberField(TEXT("delta_cm"),Delta);F->SetBoolField(TEXT("grounded"),Ground);F->SetBoolField(TEXT("moving"),Moving);
  F->SetNumberField(TEXT("posture"),Posture);F->SetStringField(TEXT("action"),State.ToString());S.FootSamples.Add(MakeShared<FJsonValueObject>(F));
 }
 if(!Moving||!T.FeetInitialized||T.FootPosture!=Posture)
 {
  for(int32 I=0;I<2;++I){T.Feet[I].Height=Z[I];T.Feet[I].Low=Z[I];T.Feet[I].Armed=true;T.Feet[I].Drop=0;T.Feet[I].Descending=false;}
  T.FeetInitialized=Moving;T.FootPosture=Posture;return;
 }
 // A contact-phase edge from the evaluated pose, not a time/distance metronome.
 for(int32 I=0;I<2;++I)
 {
  auto& F=T.Feet[I];const double Dz=Z[I]-F.Height;F.Height=Z[I];F.Low=FMath::Min(F.Low,Z[I]);
  // A planted heel/toe roll is not another step; require a fresh visible lift.
  if(!F.Armed&&Z[I]>=F.Low+1.0&&Z[I]>=Z[1-I]+1.5)F.Armed=true;
  if(Dz<-.04){F.Descending=true;F.Drop-=Dz;continue;}
  if(F.Descending)
  {
   if(F.Armed&&F.Drop>=1.2&&Z[I]<=Z[1-I]+2.5&&Now-F.LastContact>=.22&&Now-T.LastStep>=.11)
   {
    F.LastContact=Now;F.Armed=false;F.Low=Z[I];T.LastStep=Now;T.ContactFoot=I;
    const FString Base=Speed>220?TEXT("step_run"):Speed<90?TEXT("step_slow"):TEXT("step_walk");
    const FString Cue=Base+TEXT("_")+FString::Chr(TCHAR('a'+T.Variation++%6));
    Play(W,S,C,T,Cue,Posture==1?.42:Speed<90?.35:Speed>220?.80:.65);T.ContactFoot=-1;
   }
   F.Descending=false;F.Drop=0;
  }
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
 TArray<FString> CueNames;
 for(const TCHAR* Base:{TEXT("step_walk"),TEXT("step_run"),TEXT("step_slow")})
  for(int32 I=0;I<6;++I)CueNames.Add(FString(Base)+TEXT("_")+FString::Chr(TCHAR('a'+I)));
 for(const TCHAR* Name:{TEXT("crawl_a"),TEXT("crawl_b"),TEXT("crawl_c"),TEXT("fire"),TEXT("fire_m1"),TEXT("jump"),TEXT("death"),TEXT("land"),TEXT("reload_handling"),
  TEXT("reload_m1_open"),TEXT("reload_m1_load"),TEXT("reload_m1_close"),TEXT("reload_k98_open"),TEXT("reload_k98_load"),TEXT("reload_k98_close")})CueNames.Add(Name);
 for(const FString& CueName:CueNames)
 {
  const TCHAR* Name=*CueName;
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
  T.Dead=Flag(C,TEXT("IsDead"));T.State=Action(C);T.Variation=C->GetUniqueID()%6;T.Grounded=C->GetCharacterMovement()->IsMovingOnGround();S.Actors.Add(C,MoveTemp(T));
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
  if(Shots>T->Shots)Play(W,S,C,*T,Number(C,TEXT("TeamId"))==1?TEXT("fire"):TEXT("fire_m1"),1);
  if(Dead&&!T->Dead)Play(W,S,C,*T,TEXT("death"),.65);
  ReloadAudio(W,S,C,*T,State,Dead,Loaded);
  if(!Dead)
  {

   if(T->Grounded&&!Ground&&C->GetCharacterMovement()->IsFalling()&&C->GetVelocity().Z>80)Play(W,S,C,*T,TEXT("jump"),.65);
   if(Ground&&!T->Grounded)Play(W,S,C,*T,TEXT("land"),.85);
   const double Delta=FVector::Dist2D(Position,T->Position),Speed=C->GetVelocity().Size2D();
   const double Posture=Number(C,TEXT("DesiredPosture"));
   if(C->IsPlayerControlled())PlayerFootAudio(W,S,C,*T,State,Ground,Speed,Delta,Posture);
   if(!C->IsPlayerControlled()||Posture==2)
   if(Ground&&Speed>12&&Delta>0&&Delta<250&&State!=TEXT("Reloading"))
   {
    const double Stride=Posture==2?38:Flag(C,TEXT("PC_IsRunning"))||Speed>220?105:Speed<90?55:82;
    T->Distance+=Delta;
    if(T->Distance>=Stride)
    {
     T->Distance=FMath::Fmod(T->Distance,Stride);
     const FString Base=Posture==2?TEXT("crawl"):Speed>220?TEXT("step_run"):Speed<90?TEXT("step_slow"):TEXT("step_walk");
     const FString Cue=Base+TEXT("_")+FString::Chr(TCHAR('a'+T->Variation++%(Posture==2?3:6)));
     Play(W,S,C,*T,Cue,Posture==2?.32:Posture==1?.42:Speed<90?.35:Speed>220?.80:.65);
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
