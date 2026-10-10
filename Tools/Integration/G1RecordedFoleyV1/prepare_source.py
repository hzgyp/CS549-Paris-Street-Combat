"""Extend exact AVv3 by one nonreflected audio-helper translation unit only."""
import json,shutil,subprocess,sys
from pathlib import Path
from intake import ROOT,OUT,digest,save_json,row

def replace(s,old,new):
    assert s.count(old)==1,old[:180]
    return s.replace(old,new,1)

def main():
    candidate=OUT/'candidate_v1';project=candidate/'Project';assert not project.exists(),'Preserve existing source'
    selector=json.loads((OUT/'freeze.json').read_text('utf-8'))['parent']
    source=ROOT/selector['source_snapshot'];manifest=ROOT/selector['source_manifest']
    assert digest(manifest)==selector['source_manifest_sha256']
    original=json.loads(manifest.read_text('utf-8-sig'))['files'];assert len(original)==42
    for r in original:assert digest(source/r['path'])==r['sha256']
    sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
    from common import guard_rows,guards_match
    guards=guard_rows();assert len(guards)==703 and guards_match(guards)
    shutil.copytree(source,project)
    taskNative=ROOT/'Unreal/ParisStreetCombat/Content'
    cmd="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(taskNative).replace("'","''")+"' | Out-Null"
    subprocess.run(['C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-Command',cmd],check=True)
    cpp=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp'
    before=cpp.read_text('utf-8-sig');s=before
    s=replace(s,' FName State=NAME_None;int32 Variation=0;TMap<FString,int32> Counts;',
      ' FName State=NAME_None;int32 Variation=0;TMap<FString,int32> Counts;\n'
      ' double ReloadStart=-1;int64 ReloadToken=-1;bool ReloadOpened=false,ReloadInserted=false,ReloadClosed=false;')
    s=replace(s,' FVoice(USoundWaveProcedural* W,UAudioComponent* C,double E):Wave(W),Component(C),End(E){}',
      ' TWeakObjectPtr<ACharacter> Owner;FString Cue;\n'
      ' FVoice(USoundWaveProcedural* W,UAudioComponent* C,double E,ACharacter* O,const FString& N):Wave(W),Component(C),End(E),Owner(O),Cue(N){}')
    s=replace(s,' S.Voices.Emplace(Wave,Component,W->GetTimeSeconds()+Data.Seconds+.15);',
      ' S.Voices.Emplace(Wave,Component,W->GetTimeSeconds()+Data.Seconds+.15,C,Cue);')
    s=replace(s,'  E->SetNumberField(TEXT("volume"),Gain);',
      '  E->SetNumberField(TEXT("volume"),Gain);\n'
      '  E->SetNumberField(TEXT("loaded"),Number(C,TEXT("LoadedAmmo")));E->SetNumberField(TEXT("reserve"),Number(C,TEXT("ReserveAmmo")));\n'
      '  E->SetNumberField(TEXT("team"),Number(C,TEXT("TeamId")));E->SetNumberField(TEXT("reload_action"),Number(C,TEXT("ReloadActionID")));\n'
      '  E->SetNumberField(TEXT("reload_age"),Track.ReloadStart<0?-1:W->GetTimeSeconds()-Track.ReloadStart);')
    anchor='}\n}\nvoid Initialize()'
    helper='''}
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
}
void Initialize()'''
    s=replace(s,anchor,helper)
    old=' for(const TCHAR* Name:{TEXT("step_walk_a"),TEXT("step_walk_b"),TEXT("step_run_a"),TEXT("step_run_b"),TEXT("step_slow_a"),TEXT("step_slow_b"),TEXT("crawl"),TEXT("fire"),TEXT("death"),TEXT("reload"),TEXT("reload_end"),TEXT("land")})'
    new=''' TArray<FString> CueNames;
 for(const TCHAR* Base:{TEXT("step_walk"),TEXT("step_run"),TEXT("step_slow")})
  for(int32 I=0;I<6;++I)CueNames.Add(FString(Base)+TEXT("_")+FString::Chr(TCHAR('a'+I)));
 for(const TCHAR* Name:{TEXT("crawl_a"),TEXT("crawl_b"),TEXT("crawl_c"),TEXT("fire"),TEXT("death"),TEXT("land"),TEXT("reload_handling"),
  TEXT("reload_m1_open"),TEXT("reload_m1_load"),TEXT("reload_m1_close"),TEXT("reload_k98_open"),TEXT("reload_k98_load"),TEXT("reload_k98_close")})CueNames.Add(Name);
 for(const FString& CueName:CueNames)
 {
  const TCHAR* Name=*CueName;'''
    # Replace includes its existing opening brace, avoiding an extra nested scope.
    s=replace(s,old+'\n {',new)
    s=replace(s,'  T.Dead=Flag(C,TEXT("IsDead"));T.State=Action(C);T.Grounded=C->GetCharacterMovement()->IsMovingOnGround();S.Actors.Add(C,MoveTemp(T));',
      '  T.Dead=Flag(C,TEXT("IsDead"));T.State=Action(C);T.Variation=C->GetUniqueID()%6;T.Grounded=C->GetCharacterMovement()->IsMovingOnGround();S.Actors.Add(C,MoveTemp(T));')
    s=replace(s,'  if(Dead&&!T->Dead)Play(W,S,C,*T,TEXT("death"),.65);',
      '  if(Dead&&!T->Dead)Play(W,S,C,*T,TEXT("death"),.65);\n  ReloadAudio(W,S,C,*T,State,Dead,Loaded);')
    s=replace(s,'   if(State==TEXT("Reloading")&&T->State!=State)Play(W,S,C,*T,TEXT("reload"),.55);\n   if(Loaded>T->Loaded&&T->State==TEXT("Reloading"))Play(W,S,C,*T,TEXT("reload_end"),.55);','')
    s=replace(s,'     const FString Cue=Posture==2?Base:Base+(T->Variation++%2?TEXT("_b"):TEXT("_a"));\n     Play(W,S,C,*T,Cue,Posture==2?.32:Posture==1?.42:Speed<90?.35:.65);',
      '     const FString Cue=Base+TEXT("_")+FString::Chr(TCHAR(\'a\'+T->Variation++%(Posture==2?3:6)));\n     Play(W,S,C,*T,Cue,Posture==2?.32:Posture==1?.42:Speed<90?.35:Speed>220?.80:.65);')
    # Explicit proof of the accepted shot and corpse implementation remaining literal.
    for exact in ['  if(Shots>T->Shots)Play(W,S,C,*T,TEXT("fire"),1);',
       ' const float Gain=.72f*Volume;const bool Gun=Cue==TEXT("fire"),Death=Cue==TEXT("death");',
       ' S.Near=Attenuation(140,2200);S.Far=Attenuation(300,16000);S.Impact=Attenuation(120,6000);']:
        assert exact in s and exact in before
    assert s[s.index('bool RestoreTerminalDeath'):]==before[before.index('bool RestoreTerminalDeath'):]
    cpp.write_text(s,'utf-8')
    changed=[r['path'] for r in original if digest(project/r['path'])!=r['sha256']]
    assert changed==['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp']
    files=[row(project/r['path'],project) for r in original]
    archive=ROOT/'tmp/g1-av-revision-20261009/candidate_v3/Archive'
    audio={r['path']:r for r in json.loads((candidate/'Audio/PROVENANCE.json').read_text('utf-8'))['files']}
    assert digest(candidate/'Audio/fire.wav')==digest(OUT/'rejected_avv3/Audio/fire.wav')
    payload=[row(p,archive) for p in sorted(archive.rglob('*')) if p.is_file() and 'Audio' not in p.parts]
    assert len(payload)==47
    save_json(candidate/'prepare.json',dict(status='prepared_single_cpp_runtime_unverified',project=str(project),
        parent=selector,changed_paths=changed,source_files=files,descriptor_sha256=digest(project/'WW2FranceLiberation.uproject'),
        reuse_archive=str(archive),archive_files=payload,protected_files=guards,approved_fire_sha256=audio['fire.wav']['sha256'],
        recording_hold=True,scope='One nonreflected audio helper; source/header/default/config/observer/resource/save/model/rig/finger data untouched'))
    print(json.dumps(dict(changed=changed,source_files=len(files),archive_files=len(payload))))

if __name__=='__main__':main()
