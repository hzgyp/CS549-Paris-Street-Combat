"""Verify narrow death-render changes and native/resource/save protection."""
from pathlib import Path
import sys,argparse
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,read,write,rows,sha,INNER
ap=argparse.ArgumentParser();ap.add_argument('revision');a=ap.parse_args()
freeze=read(ROOT/'tmp/g1-player-death-20261011/freeze.json');old=ROOT/freeze['parent']['source_snapshot'];new=OUT/a.revision/'Project'
assert rows(old)==freeze['parent_files']
prefix='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/'
allowed=['ParisBridgeMission.cpp','ParisBridgeMissionV1.cpp','ParisMissionInteraction.cpp','ParisCombatUI.cpp','ParisTacticalEquipment.cpp','ParisEquipmentAudio.inl','ParisPressureMineChecks.inl']
changed=[r['path'] for r in freeze['parent_files'] if sha(new/r['path'])!=r['sha256']]
assert set(changed)=={prefix+n for n in allowed},changed
for n in allowed:
    text=(new/prefix/n).read_text('utf-8-sig')
    text=text.replace('#include "ParisPlayerDeath.h"\n','')
    if n=='ParisBridgeMissionV1.cpp':text=text.replace('  ParisPlayerDeath::Initialize();\n','').replace('override{ParisPlayerDeath::Shutdown();','override{')
    if n=='ParisBridgeMission.cpp':text=text.replace('    if(ParisPlayerDeath::Presenting(this))return;\n','').replace(':M->Phase==TEXT("Lost")?TEXT("YOU DIED")','').replace('!(MenuVisible && M->Phase==TEXT("Lost")) && ','')
    if n=='ParisMissionInteraction.cpp':text=text.replace(' && !ParisPlayerDeath::Presenting(this)','').replace('    if(ParisPlayerDeath::Presenting(this))return true;\n','')
    if n=='ParisCombatUI.cpp':text=text.replace('if(ParisPlayerDeath::Presenting(PC))return false;','')
    if n=='ParisTacticalEquipment.cpp':
        for line in ['#include "NiagaraComponent.h"\n','#include "NiagaraFunctionLibrary.h"\n','#include "NiagaraSystem.h"\n','#include "TimerManager.h"\n']:text=text.replace(line,'',1)
        for line in ['#include "ParisExplosionVisual.inl"\n','#include "Distributions/DistributionFloatConstantCurve.h"\n','#include "Particles/ParticleSystemComponent.h"\n']:text=text.replace(line,'',1)
    if n=='ParisEquipmentAudio.inl':text=text.replace('    ExplosionVisual(W,At);','    auto* Flash=Prop(W,TEXT("Blast"),At);auto* Light=NewObject<UPointLightComponent>(Flash);Flash->AddInstanceComponent(Light);Light->SetupAttachment(Flash->GetRootComponent());Light->SetIntensity(6000);Light->SetAttenuationRadius(650);Light->SetLightColor(FLinearColor(1,.58,.22));Light->RegisterComponent();Flash->SetLifeSpan(.12f);')
    if n=='ParisPressureMineChecks.inl':text=text.replace('CheckClock>4.5&&ParisPlayerDeath::Complete(W)','CheckClock>(CheckMode==TEXT("mine_post_clear_frag")?6:.5)')
    assert text==(old/prefix/n).read_text('utf-8-sig'),n
original=read(OUT/'freeze.json')
for row in original['protected_native']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
assert rows(ROOT/original['parent']['source_snapshot'])==original['parent_files']
assert sha(ROOT/original['parent']['playable_directory']/INNER)==original['parent']['game_sha256']
assert sha(ROOT/'Assets/Sync/CATALOG.json')==original['catalog_sha256']
for protected in [original,freeze]:assert rows(Path(protected['user_root']))==protected['user_files']
assert rows(ROOT/freeze['parent']['playable_directory'])==freeze['parent_normal_files']
assert all(not (ROOT/r['path']).exists() and sha(ROOT/'tmp/g1-player-death-20261011/RetiredRootLaunchers'/r['path'])==r['sha256'] for r in freeze['root_trial_wrappers'])
write(OUT/a.revision/'death-protection.json',dict(status='pass',parent_files=69,native_files=len(original['protected_native']),changed_parent_files=changed,all_other_parent_files_exact=True,reflection_models_fingers_gun_damage_save_equipment_AI_navigation_exact=True,parent_normal_users_formal_Catalog_exact=True,root_trial_wrappers_relocated=True))
print('PASS exact native/formal/parent/users and bounded death-render-only changes')
