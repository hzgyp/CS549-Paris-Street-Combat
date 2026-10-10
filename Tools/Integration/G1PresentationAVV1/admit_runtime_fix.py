"""Preserve V2 and admit the documented distance/read-only legacy witnesses."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent;BASE=ROOT/'tmp/g1-av-revision-20261009'
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest
old=BASE/'candidate_v2';new=BASE/'candidate_v3';assert not new.exists()
receipt=json.loads((old/'prepare.json').read_text('utf-8-sig'));project=Path(receipt['project'])
assert json.loads((old/'build.json').read_text('utf-8-sig'))['exit_code']==0
frozen=old/'FrozenSource';assert not frozen.exists()
for row in receipt['private_source_files']+[dict(path='WW2FranceLiberation.uproject',sha256=receipt['descriptor_sha256'])]:
    p=project/row['path'];assert digest(p)==row['sha256'];q=frozen/row['path'];q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
cpp=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp'
s=cpp.read_text('utf-8')
def replace(old,new):
    global s
    assert s.count(old)==1,old[:80];s=s.replace(old,new,1)
replace('#include "BrainComponent.h"','#include "BrainComponent.h"\n#include "Camera/PlayerCameraManager.h"')
replace('TStrongObjectPtr<USoundAttenuation> Near;TStrongObjectPtr<USoundAttenuation> Far;',
        'TStrongObjectPtr<USoundAttenuation> Near;TStrongObjectPtr<USoundAttenuation> Far;TStrongObjectPtr<USoundAttenuation> Impact;')
replace('const float Gain=.72f*Volume;const bool Gun=Cue==TEXT("fire");',
'''const float Gain=.72f*Volume;const bool Gun=Cue==TEXT("fire"),Death=Cue==TEXT("death");
 auto* Settings=Gun?S.Far.Get():Death?S.Impact.Get():S.Near.Get();
 if(auto* Camera=UGameplayStatics::GetPlayerCameraManager(W,0))
  if(FVector::DistSquared(Camera->GetCameraLocation(),C->GetActorLocation())>FMath::Square(Settings->Attenuation.GetMaxDimension()))return;''')
replace('Gun?S.Far.Get():S.Near.Get(),nullptr,true','Settings,nullptr,true')
replace('E->SetNumberField(TEXT("volume"),Gain);S.Events.Add(MakeShared<FJsonValueObject>(E));',
'''E->SetNumberField(TEXT("volume"),Gain);
  if(Death)if(auto* Single=C->GetMesh()->GetSingleNodeInstance())
  {E->SetBoolField(TEXT("death_clip_playing"),Single->IsPlaying());E->SetNumberField(TEXT("death_clip_time"),Single->GetCurrentTime());E->SetNumberField(TEXT("death_clip_length"),Single->GetLength());E->SetStringField(TEXT("death_clip"),Single->GetCurrentAsset()?Single->GetCurrentAsset()->GetName():TEXT("None"));}
  S.Events.Add(MakeShared<FJsonValueObject>(E));''')
replace('S.Near=Attenuation(140,2200);S.Far=Attenuation(300,16000);','S.Near=Attenuation(140,2200);S.Far=Attenuation(300,16000);S.Impact=Attenuation(120,6000);')
cpp.write_text(s,'utf-8');(HERE/'ParisGameplayAV.cpp').write_text(s,'utf-8')
module=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp'
s=module.read_text('utf-8')
replace('check(Mode==TEXT("actions")||Mode==TEXT("checkpoint"));','check(Mode==TEXT("actions")||Mode==TEXT("checkpoint")||Mode==TEXT("legacy"));')
replace('if(M->Phase!=TEXT("Ready")||M->ReadySeconds<12)return;',
'''if(M->Phase!=TEXT("Ready")||M->ReadySeconds<12)return;
   if(Mode==TEXT("legacy")){Generation=M->RunGeneration;Root->SetStringField(TEXT("legacy_journal"),M->InspectCheckpointJournal());Go(W,P,TEXT("load_wait"));Tap(PC,EKeys::F9);return;}''')
replace('if(Step==TEXT("loaded_image")&&Age>=1){Generation=M->RunGeneration;',
        'if(Step==TEXT("loaded_image")&&Age>=1){if(Mode==TEXT("legacy")){Finish(TEXT("pass_legacy_v5_terminal_corpse_compatibility"));return;}Generation=M->RunGeneration;')
module.write_text(s,'utf-8');new.mkdir();shutil.copytree(old/'Audio',new/'Audio');shutil.copytree(old/'UI',new/'UI')
receipt['identity']='candidate_v3';receipt['runtime_negative_frozen_source']=frozen.as_posix()
receipt['private_source_files']=[dict(r,sha256=digest(project/r['path']),size_bytes=(project/r['path']).stat().st_size) for r in receipt['private_source_files']]
receipt['correction']='Separate death distance attenuation, explicit range culling, actual original-death clip witness, isolated copied legacy V5 test; no game transactions/gains/sample/native changes'
(new/'prepare.json').write_text(json.dumps(receipt,indent=2)+'\n','utf-8')
print(json.dumps(dict(status='prepared_runtime_unverified',identity='candidate_v3',frozen_source=str(frozen))))
