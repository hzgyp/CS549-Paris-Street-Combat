"""Freeze admitted V3, then make a C++-only revision in its private build checkout."""
import json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from verify_team_source import verify_source
from revise_source import replace_once
BASE=ROOT/'tmp/g1-playtest-revision-20261008'

def main():
    admitted=BASE/'plain_v1/read_only_audit.json'
    audit=json.loads(admitted.read_text());assert audit['numeric_status']=='ordinary_ready_only_no_action_or_checkpoint_claim'
    old=BASE/'candidate_v3';out=BASE/'candidate_v4';assert not out.exists()
    prepared=json.loads((old/'prepare_revision.json').read_text())
    built=json.loads((old/'build_revision.json').read_text(encoding='utf-8-sig'))
    assert built['status']=='built_private_revision_runtime_unverified'
    project=Path(prepared['project'])
    for row in prepared['private_source_files']:assert digest(project/row['path'])==row['sha256']
    assert verify_source()['source_files']==758
    guards=guard_rows();assert len(guards)==703 and guards_match(guards)
    cooked=project/'Saved/Cooked/Windows';assert cooked.is_dir()
    cooked_rows=[dict(path=str(f.relative_to(cooked)),size_bytes=f.stat().st_size,sha256=digest(f)) for f in cooked.rglob('*') if f.is_file()]
    archive_rows=[dict(path=str(f.relative_to(old/'Archive')),size_bytes=f.stat().st_size,sha256=digest(f)) for f in (old/'Archive').rglob('*') if f.is_file()]
    containers=[r for r in archive_rows if r['path'].endswith('.ucas')]
    assert containers,'Authenticate actual V3 content payloads as well as Zen cook metadata'
    compiled_game=project/'Binaries/Win64/WW2FranceLiberation.exe'
    assert digest(compiled_game)==built['game_sha256'],'Packaged V3 must match the monolithic build product'
    frozen=old/'SourceAtV3';assert not frozen.exists();frozen.mkdir()
    # Only explicit files; never recursively follow the Content junction.
    for row in prepared['private_source_files']:
        dest=frozen/row['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(project/row['path'],dest)
    shutil.copyfile(project/'WW2FranceLiberation.uproject',frozen/'WW2FranceLiberation.uproject')
    source=project/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
    cpp=source/'ParisBridgeMission.cpp';s=cpp.read_text()
    s=replace_once(s,'            if(Params.Key==EKeys::R && bMissionControlHeld) { M->RestartMission(); return true; }\n','')
    cpp.write_text(s.replace('Ctrl+R','F6'),encoding='utf-8')
    module=source/'ParisBridgeMissionV1.cpp';t=module.read_text()
    t=replace_once(t,'Go(W,P,TEXT("crouch"));Tap(PC,EKeys::LeftControl);','Go(W,P,TEXT("crouch"));Key(PC,EKeys::LeftControl,true);')
    t=replace_once(t,'Image(PC,TEXT("crouch"));Tap(PC,EKeys::LeftControl);Go(W,P,TEXT("stand"));return;',
        'Image(PC,TEXT("crouch"));AmmoBefore=Number(P,TEXT("LoadedAmmo"));Generation=M->RunGeneration;Tap(PC,EKeys::R);Go(W,P,TEXT("crouch_reload"));return;')
    marker='   if(Step==TEXT("stand")&&Age>=1)'
    addition='''   if(Step==TEXT("crouch_reload")&&Age>=1){if(!Check(M->RunGeneration==Generation&&M->Phase==TEXT("Crossing")&&Number(P,TEXT("LoadedAmmo"))==AmmoBefore,TEXT("held_control_reload_no_restart")))return;Key(PC,EKeys::LeftControl,false);Tap(PC,EKeys::LeftControl);Go(W,P,TEXT("stand"));return;}
'''
    t=replace_once(t,marker,addition+marker);module.write_text(t,encoding='utf-8')
    changed=[]
    for row in prepared['private_source_files']:
        if digest(project/row['path'])!=row['sha256']:changed.append(row['path'])
    expected=['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp',
              'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp']
    assert set(changed)==set(expected),'Only method/test implementation changes; header/defaults/config/assets must stay exact'
    out.mkdir();shutil.copytree(old/'UI',out/'UI')
    receipt=dict(prepared,identity='candidate_v4',project=str(project),reuse_v3_cook=True,
        reuse_scope='Same private build checkout. Frozen V3 source retained. Exactly two C++ method/test files change; all headers/defaults/config/native assets unchanged. Rebuild monolithic executable and copy authenticated unchanged packaged files into NEW V4 archive.',
        v3_admission_sha256=digest(admitted),v3_game_sha256=built['game_sha256'],
        changed_implementation_paths=changed,cooked_files=cooked_rows,reused_content_payloads=containers,
        reuse_archive=str(old/'Archive'),archive_files=archive_rows,
        protected_files=guards,private_source_files=[dict(row,sha256=digest(project/row['path'])) for row in prepared['private_source_files']])
    (out/'prepare_revision.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(identity='candidate_v4',status=receipt['status'],changed=changed,reused_cooked_files=len(cooked_rows)),indent=2))
if __name__=='__main__':main()
