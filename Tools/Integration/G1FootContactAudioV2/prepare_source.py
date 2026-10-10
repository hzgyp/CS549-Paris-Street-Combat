"""Read evaluated player feet; retain models, movement, gun/ammo/save and reload."""
import json,shutil,subprocess
from common import ROOT,OUT,digest,save,row

def replace(s,a,b):assert s.count(a)==1,a[:140];return s.replace(a,b,1)

def main():
    frozen=json.loads((OUT/'freeze.json').read_text('utf-8-sig'));parent=frozen['parent']
    source=ROOT/parent['source_snapshot'];project=OUT/'candidate_v1/Project'
    assert not project.exists(),'Preserve occupied source attempt'
    for r in frozen['source_files']:assert digest(source/r['path'])==r['sha256']
    shutil.copytree(source,project)
    command="New-Item -ItemType Junction -Path '"+str(project/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run(['C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-Command',command],check=True)
    cpp=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp';before=cpp.read_text('utf-8-sig');s=before
    s=replace(s,'struct FTrack\n{','struct FFoot {double Height=0,Drop=0,LastContact=-100;bool Descending=false;};\nstruct FTrack\n{')
    s=replace(s,' double ReloadStart=-1;', ' FFoot Feet[2];bool FeetInitialized=false,FootWarning=false;double FootPosture=-1,LastStep=-100;int32 ContactFoot=-1;\n double ReloadStart=-1;')
    s=replace(s,' TArray<TSharedPtr<FJsonValue>> Events;', ' TArray<TSharedPtr<FJsonValue>> FootSamples;TArray<TSharedPtr<FJsonValue>> Events;')
    s=replace(s,' O->SetArrayField(TEXT("events"),S.Events);',' O->SetArrayField(TEXT("foot_samples"),S.FootSamples);O->SetArrayField(TEXT("events"),S.Events);')
    s=replace(s,'const bool Gun=Cue==TEXT("fire"),Death=', 'const bool Gun=Cue==TEXT("fire")||Cue==TEXT("fire_m1"),Death=')
    s=replace(s,'  E->SetNumberField(TEXT("reload_age"),',
      '  E->SetBoolField(TEXT("grounded"),C->GetCharacterMovement()->IsMovingOnGround());E->SetNumberField(TEXT("velocity_z"),C->GetVelocity().Z);\n'
      '  E->SetStringField(TEXT("contact_foot"),Track.ContactFoot==0?TEXT("foot_l"):Track.ContactFoot==1?TEXT("foot_r"):TEXT("None"));\n'
      '  if(Track.ContactFoot>=0)E->SetNumberField(TEXT("contact_height"),Track.Feet[Track.ContactFoot].Height);\n'
      '  E->SetNumberField(TEXT("reload_age"),')
    marker='}\n}\nvoid Initialize()'
    foot=r'''}
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
  for(int32 I=0;I<2;++I){T.Feet[I].Height=Z[I];T.Feet[I].Drop=0;T.Feet[I].Descending=false;}
  T.FeetInitialized=Moving;T.FootPosture=Posture;return;
 }
 // A contact-phase edge from the evaluated pose, not a time/distance metronome.
 for(int32 I=0;I<2;++I)
 {
  auto& F=T.Feet[I];const double Dz=Z[I]-F.Height;F.Height=Z[I];
  if(Dz<-.04){F.Descending=true;F.Drop-=Dz;continue;}
  if(F.Descending)
  {
   if(F.Drop>=1.2&&Z[I]<=Z[1-I]+2.5&&Now-F.LastContact>=.22&&Now-T.LastStep>=.11)
   {
    F.LastContact=Now;T.LastStep=Now;T.ContactFoot=I;
    const FString Base=Speed>220?TEXT("step_run"):Speed<90?TEXT("step_slow"):TEXT("step_walk");
    const FString Cue=Base+TEXT("_")+FString::Chr(TCHAR('a'+T.Variation++%6));
    Play(W,S,C,T,Cue,Posture==1?.42:Speed<90?.35:Speed>220?.80:.65);T.ContactFoot=-1;
   }
   F.Descending=false;F.Drop=0;
  }
 }
}
}
void Initialize()'''
    s=replace(s,marker,foot)
    s=replace(s,'TEXT("crawl_c"),TEXT("fire"),TEXT("death")','TEXT("crawl_c"),TEXT("fire"),TEXT("fire_m1"),TEXT("jump"),TEXT("death")')
    s=replace(s,'  if(Shots>T->Shots)Play(W,S,C,*T,TEXT("fire"),1);',
      '  if(Shots>T->Shots)Play(W,S,C,*T,Number(C,TEXT("TeamId"))==1?TEXT("fire"):TEXT("fire_m1"),1);')
    s=replace(s,'   if(Ground&&!T->Grounded)Play(W,S,C,*T,TEXT("land"),.6);',
      '   if(T->Grounded&&!Ground&&C->GetCharacterMovement()->IsFalling()&&C->GetVelocity().Z>80)Play(W,S,C,*T,TEXT("jump"),.48);\n'
      '   if(Ground&&!T->Grounded)Play(W,S,C,*T,TEXT("land"),.85);')
    s=replace(s,'   if(Ground&&Speed>12&&Delta>0&&Delta<250&&State!=TEXT("Reloading"))',
      '   if(C->IsPlayerControlled())PlayerFootAudio(W,S,C,*T,State,Ground,Speed,Delta,Posture);\n'
      '   if(!C->IsPlayerControlled()||Posture==2)\n'
      '   if(Ground&&Speed>12&&Delta>0&&Delta<250&&State!=TEXT("Reloading"))')
    assert s[s.index('bool RestoreTerminalDeath'):]==before[before.index('bool RestoreTerminalDeath'):]
    assert s[s.index('void ReloadAudio'):s.index('\n}\nvoid PlayerFootAudio')+2]==before[before.index('void ReloadAudio'):before.index('\n}\n}\nvoid Initialize()')+2]
    cpp.write_text(s,'utf-8')
    changed=[r['path'] for r in frozen['source_files'] if digest(project/r['path'])!=r['sha256']]
    assert changed==['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp']
    save(OUT/'candidate_v1/prepare.json',dict(status='single_helper_prepared_runtime_unverified',project=str(project),parent=parent,source_files=[row(project/r['path'],project) for r in frozen['source_files']],
       changed_paths=changed,reuse_archive=frozen['reuse_archive'],archive_files=frozen['archive_files'],protected_files=frozen['protected_files'],recording_hold=True))
    print(json.dumps(dict(source_files=42,changed=changed)))

if __name__=='__main__':main()
