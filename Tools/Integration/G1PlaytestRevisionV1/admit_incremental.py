"""Read-only reconciliation after Windows path-spelling admission failure."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
from revise_source import replace_once
BASE=ROOT/'tmp/g1-playtest-revision-20261008'

def expected_text(path,text):
    if path.endswith('/ParisBridgeMission.cpp'):
        return replace_once(text,'            if(Params.Key==EKeys::R && bMissionControlHeld) { M->RestartMission(); return true; }\n','').replace('Ctrl+R','F6')
    if path.endswith('/ParisBridgeMissionV1.cpp'):
        t=replace_once(text,'Go(W,P,TEXT("crouch"));Tap(PC,EKeys::LeftControl);','Go(W,P,TEXT("crouch"));Key(PC,EKeys::LeftControl,true);')
        t=replace_once(t,'Image(PC,TEXT("crouch"));Tap(PC,EKeys::LeftControl);Go(W,P,TEXT("stand"));return;',
            'Image(PC,TEXT("crouch"));AmmoBefore=Number(P,TEXT("LoadedAmmo"));Generation=M->RunGeneration;Tap(PC,EKeys::R);Go(W,P,TEXT("crouch_reload"));return;')
        marker='   if(Step==TEXT("stand")&&Age>=1)'
        add='''   if(Step==TEXT("crouch_reload")&&Age>=1){if(!Check(M->RunGeneration==Generation&&M->Phase==TEXT("Crossing")&&Number(P,TEXT("LoadedAmmo"))==AmmoBefore,TEXT("held_control_reload_no_restart")))return;Key(PC,EKeys::LeftControl,false);Tap(PC,EKeys::LeftControl);Go(W,P,TEXT("stand"));return;}
'''
        return replace_once(t,marker,add+marker)
    return text

def main():
    old=BASE/'candidate_v3';out=BASE/'candidate_v5';assert not out.exists()
    prepared=json.loads((old/'prepare_revision.json').read_text());project=Path(prepared['project']);frozen=old/'SourceAtV3'
    built=json.loads((old/'build_revision.json').read_text(encoding='utf-8-sig'))
    admitted=BASE/'plain_v1/read_only_audit.json';audit=json.loads(admitted.read_text())
    assert audit['numeric_status']=='ordinary_ready_only_no_action_or_checkpoint_claim'
    assert built['status']=='built_private_revision_runtime_unverified'
    assert digest(project/'Binaries/Win64/WW2FranceLiberation.exe')==built['game_sha256']
    assert verify_source()['source_files']==758
    guards=guard_rows();assert len(guards)==703 and guards_match(guards)
    changed=[]
    for row in prepared['private_source_files']:
        prior=frozen/row['path'];current=project/row['path'];assert digest(prior)==row['sha256']
        normalized=Path(row['path']).as_posix()
        assert current.read_text()==expected_text(normalized,prior.read_text()),'Unexpected source change: '+normalized
        if digest(current)!=row['sha256']:changed.append(normalized)
    assert set(changed)=={'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp',
                          'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp'}
    assert digest(project/'WW2FranceLiberation.uproject')==digest(frozen/'WW2FranceLiberation.uproject')
    evidence=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/Failures/MI012/incremental_preflight_v1'
    assert not evidence.exists();evidence.mkdir()
    shutil.copyfile(ROOT/'Failures/MI012-20261008-packaged-human-integration/prepare_incremental_v4_STOPPED.py',evidence/'failed_prepare_incremental.py')
    (evidence/'negative.json').write_text(json.dumps(dict(status='stopped_path_spelling_guard_no_build_or_native_save',
        actual_changed_paths=changed,reason='Two intended cpp changes match the frozen source transformation exactly. Windows backslash records were compared with slash literals. Preserve raw guard and frozen V3; distinct normalized read-only admission.',
        frozen_source_files=prepared['private_source_files'],protected_files_unchanged=703),indent=2)+'\n')
    cooked=project/'Saved/Cooked/Windows';assert cooked.is_dir()
    cooked_rows=[dict(path=str(f.relative_to(cooked)),size_bytes=f.stat().st_size,sha256=digest(f)) for f in cooked.rglob('*') if f.is_file()]
    archive_rows=[dict(path=str(f.relative_to(old/'Archive')),size_bytes=f.stat().st_size,sha256=digest(f)) for f in (old/'Archive').rglob('*') if f.is_file()]
    containers=[r for r in archive_rows if r['path'].endswith('.ucas')];assert containers
    out.mkdir();shutil.copytree(old/'UI',out/'UI')
    receipt=dict(prepared,identity='candidate_v5',reuse_v3_cook=True,project=str(project),
        reuse_scope='Frozen V3 headers/defaults/config/assets exact. Exactly two cpp implementations differ. Rebuild monolithic executable only; reuse authenticated packaged files. V4 path-spelling negative retained, not rolled back or bypassed.',
        v3_admission_sha256=digest(admitted),v3_game_sha256=built['game_sha256'],changed_implementation_paths=changed,
        reuse_archive=str(old/'Archive'),archive_files=archive_rows,cooked_files=cooked_rows,reused_content_payloads=containers,
        protected_files=guards,private_source_files=[dict(r,sha256=digest(project/r['path'])) for r in prepared['private_source_files']])
    (out/'prepare_revision.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(identity='candidate_v5',status=receipt['status'],changed=changed,archive_files=len(archive_rows)),indent=2))
if __name__=='__main__':main()
