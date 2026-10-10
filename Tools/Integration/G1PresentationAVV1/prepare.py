"""New private wrapper, exact selected HUD source, method-only presentation repair."""
import hashlib,json,shutil,subprocess,sys
from pathlib import Path
from generate_cues import generate

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
OUT=ROOT/'tmp/g1-av-revision-20261009/candidate_v1';PROJECT=OUT/'Project'
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source

def change(text,old,new):
    assert text.count(old)==1,old[:150]
    return text.replace(old,new,1)
def rows(folder):
    return [dict(path=p.relative_to(folder).as_posix(),size_bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(folder.rglob('*')) if p.is_file()]

def main():
    assert not OUT.exists(),'Preserve existing candidate'
    baseline=json.loads((ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json').read_text('utf-8-sig'))
    manifest_path=ROOT/baseline['source_manifest'];assert digest(manifest_path)==baseline['source_manifest_sha256']
    source=ROOT/baseline['source_snapshot'];manifest=json.loads(manifest_path.read_text('utf-8-sig'))['files']
    guards=guard_rows();assert len(guards)==703 and guards_match(guards);assert verify_source()['source_files']==758
    for r in manifest:
        for base in [source,(ROOT/baseline['active_authoring_project']).parent]:
            assert digest(base/r['path'])==r['sha256'] and (base/r['path']).stat().st_size==r['size_bytes']
    native=json.loads((ROOT/'Assets/Sync/manifests/paris-gameplay-native-playtest.json').read_text('utf-8-sig'))
    assert len(native['files'])==359
    for r in native['files']:assert digest(ROOT/r['path'])==r['sha256']
    archive=ROOT/'tmp/g1-playtest-revision-20261008/hud_v3/Archive';archive_rows=rows(archive)
    assert len(archive_rows)==47 and digest(archive/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==baseline['game_sha256']
    # Content remains the existing protected asset home; never save through this alias.
    shutil.copytree(source,PROJECT)
    code='New-Item -ItemType Junction -Path '+"'"+str(PROJECT/'Content').replace("'","''")+"' -Value '"+str(ROOT/'Unreal/ParisStreetCombat/Content').replace("'","''")+"' | Out-Null"
    subprocess.run([r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe','-NoProfile','-Command',code],check=True)
    cpp=PROJECT/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp'
    s=cpp.read_text('utf-8-sig');s=change(s,'#include "ParisBridgeMission.h"','#include "ParisBridgeMission.h"\n#include "ParisGameplayAV.h"')
    s=change(s,'Super::Tick(DeltaSeconds); if(bTravelPending || Phase==TEXT("Error")) return;',
        'Super::Tick(DeltaSeconds); if(bTravelPending || Phase==TEXT("Error")) return;\n    ParisGameplayAV::Tick(this,Roster);')
    s=change(s,'else { SetPhase(TEXT("Ready")); Feedback=TEXT("Press Enter to begin the bridgehead mission."); }\n        return;',
        'else { SetPhase(TEXT("Ready")); Feedback=TEXT("Press Enter to begin the bridgehead mission."); }\n        ParisGameplayAV::Prime(this,Roster);\n        return;')
    s=change(s,'if(A->GetBoolField(TEXT("dead"))) { Invoke(C,TEXT("PC_Die")); DeathLedger.Add(StableIds[I]); }',
        'if(A->GetBoolField(TEXT("dead")))\n        {\n            if(!Invoke(C,TEXT("PC_Die")) || !ParisGameplayAV::RestoreTerminalDeath(C,Error)) return false;\n            DeathLedger.Add(StableIds[I]);\n        }')
    s=change(s,'    auto Tri=[&](FVector2D A,FVector2D B,FVector2D C,FLinearColor Color)',
        '    if(M->Phase==TEXT("Preparing") && GetWorld()->URL.HasOption(TEXT("ParisLoad")))\n    {\n        DrawRect(FLinearColor(.012f,.022f,.018f,1),0,0,Canvas->SizeX,Canvas->SizeY);\n        Text(TEXT("RESTORING CHECKPOINT"),960,488,34,Ivory,true,2);\n        Text(TEXT("Loading the saved mission state"),960,550,18,Quiet,true);\n        return;\n    }\n    auto Tri=[&](FVector2D A,FVector2D B,FVector2D C,FLinearColor Color)')
    cpp.write_text(s,'utf-8')
    module=PROJECT/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp'
    s=module.read_text('utf-8-sig');s=change(s,'#include "ParisBridgeMission.h"','#include "ParisBridgeMission.h"\n#include "ParisGameplayAV.h"')
    s=change(s,' void StartupModule()override\n {',' void StartupModule()override\n {\n  ParisGameplayAV::Initialize();')
    s=change(s,'void ShutdownModule()override{if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);}',
        'void ShutdownModule()override{if(Handle.IsValid())FWorldDelegates::OnWorldPostActorTick.Remove(Handle);ParisGameplayAV::Shutdown();}')
    s=change(s,'if(!Check(M->Phase==TEXT("Won")&&M->SaveSerial==1&&M->CheckpointUnlocked(),TEXT("fresh_saved_checkpoint_load")))return;Go(W,P,TEXT("loaded_settle"));return;',
        'if(!Check(M->Phase==TEXT("Won")&&M->SaveSerial==1&&M->CheckpointUnlocked(),TEXT("fresh_saved_checkpoint_load")))return;FString Why;if(!Check(ParisGameplayAV::VerifyRestoredCorpses(W,Why),TEXT("first_loaded_frame_terminal_corpses")))return;Root->SetStringField(TEXT("first_loaded_audio"),ParisGameplayAV::Inspect(W));Go(W,P,TEXT("loaded_settle"));return;')
    s=change(s,'if(Step==TEXT("loaded_settle")&&Age>=3){Image(PC,TEXT("checkpoint_loaded"));Go(W,P,TEXT("loaded_image"));return;}',
        'if(Step==TEXT("loaded_settle")){FString Why;if(!ParisGameplayAV::VerifyRestoredCorpses(W,Why)){Finish(TEXT("failed_restored_corpse_replay"));return;}if(Age>=3){Root->SetStringField(TEXT("settled_loaded_audio"),ParisGameplayAV::Inspect(W));Event(TEXT("pass_restored_corpses_stopped_for_three_seconds"));Image(PC,TEXT("checkpoint_loaded"));Go(W,P,TEXT("loaded_image"));}return;}')
    module.write_text(s,'utf-8')
    build=PROJECT/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/ParisBridgeMissionV1.Build.cs'
    s=build.read_text('utf-8-sig');s=change(s,'"ImageWrapper", "AIModule"','"ImageWrapper", "AudioMixer", "AIModule"');build.write_text(s,'utf-8')
    base=PROJECT/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1'
    shutil.copyfile(HERE/'ParisGameplayAV.h',base/'Public/ParisGameplayAV.h');shutil.copyfile(HERE/'ParisGameplayAV.cpp',base/'Private/ParisGameplayAV.cpp')
    generate(OUT/'Audio');shutil.copytree(ROOT/'tmp/g1-playtest-revision-20261008/hud_v3/UI',OUT/'UI')
    changes=[r['path'] for r in manifest if digest(PROJECT/r['path'])!=r['sha256']]
    assert len(changes)==3
    all_source=[dict(path=p.relative_to(PROJECT).as_posix(),size_bytes=p.stat().st_size,sha256=digest(p)) for area in ['Config','Plugins','Source'] for p in sorted((PROJECT/area).rglob('*')) if p.is_file()]
    assert len(all_source)==41 # original39 non-descriptor + two helper files
    users=Path.home()/'AppData/Local/ParisStreetCombat/G1PlaytestV5'
    receipt=dict(status='prepared_runtime_unverified',project=str(PROJECT),baseline=baseline,baseline_manifest=manifest,
        changed_paths=changes,new_paths=['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Public/ParisGameplayAV.h','Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp'],
        private_source_files=all_source,descriptor_sha256=digest(PROJECT/'WW2FranceLiberation.uproject'),archive_files=archive_rows,reuse_archive=str(archive),
        protected_files=guards,native_count=359,source758=True,user_files=rows(users),user_root=str(users),
        scope='Method-only terminal-pose/load-cover/audio feedback; no reflected schema/default/config/asset/save/gun transaction change')
    (OUT/'prepare.json').write_text(json.dumps(receipt,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k in ['status','project','changed_paths','new_paths','scope']}))
if __name__=='__main__':main()
