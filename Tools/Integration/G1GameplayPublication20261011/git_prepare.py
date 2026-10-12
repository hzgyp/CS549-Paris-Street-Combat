"""Explicit publication paths; never sweep unrelated active platform code."""
import argparse,ast,json,subprocess,hashlib
from pathlib import Path
from publish import ROOT,OUT,read,write,sha

EXACT={'.gitattributes','.gitignore','AGENTS.md','HANDOFF.md','README.md','Failures/README.md','PLAY_CURRENT_G1.cmd','Assets/ASSET_INDEX.md','Assets/TEAM_SYNC_WORKFLOW.md','Tools/AssetWorkbench/asset_index.py','Tools/Archive/restore_intermediate_archive.ps1','Tools/Archive/execute_cache_cleanup_20261011.ps1','Tools/Archive/prepare_cache_cleanup_20261011.py','Tools/Integration/G1AudioPublicationV2/restore_file.py'}
PREFIXES=('Assets/Sync/','Assets/Registry/','Unreal/Variants/G1','Docs/Images/MissionLoopV1/','Docs/Development/MissionLoopV1/','Docs/Development/G1','Docs/Development/CURRENT_','Docs/Development/TEAM_CURRENT_BUILD_','Docs/Development/TeamSyncV1/','Docs/Development/INTERMEDIATE_STORAGE_CLEANUP','Failures/MI0','Tools/AssetCreation/GrenadeModelsV1/','Tools/AssetCreation/PressureMineV1/','Tools/Integration/G1Team','Tools/Integration/G1Checkpoint','Tools/Integration/G1EnemyClear','Tools/Integration/G1Gameplay','Tools/Integration/CombatUIV1/','Tools/Integration/FieldManualUIV1/','Tools/Integration/PlayerDeathV1/','Tools/Integration/GrenadeModelsV1/','Tools/Integration/GrenadeEquipV2/','Tools/Integration/EquipmentWheelV1/','Tools/Integration/TacticalEquipmentV1/')
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def plan():
    tracked=git('diff','--name-only','-z').decode().split('\0')
    untracked=git('ls-files','--others','--exclude-standard','-z').decode().split('\0')
    paths=sorted({p for p in tracked+untracked if p and (p in EXACT or p.startswith(PREFIXES))})
    excluded=sorted({p for p in tracked+untracked if p and p not in paths})
    assert not git('diff','--cached','--name-only').strip(),'Preserve an existing staged change; inspect it'
    for p in paths:
        f=ROOT/p;assert f.is_file() and f.stat().st_size<25*2**20,p
        if f.suffix.lower()=='.py':ast.parse(f.read_text('utf-8-sig'),filename=p)
        if f.suffix.lower()=='.json':json.loads(f.read_text('utf-8-sig'))
        assert f.suffix.lower() not in {'.zip','.wav','.ttf','.fbx','.blend','.glb','.uasset','.umap','.dll','.pdb','.exe'}
    write(OUT/'GIT_PATH_PLAN.json',dict(paths=paths,excluded_unrelated=excluded,parent=git('rev-parse','HEAD').decode().strip()))
    print('PUBLICATION PATH PLAN',len(paths),'files;',len(excluded),'unrelated paths excluded')
def stage():
    p=read(OUT/'GIT_PATH_PLAN.json');assert git('rev-parse','HEAD').decode().strip()==p['parent']
    # Actual active token and private-key body must never be present in selected
    # source bytes. Do not print either secret or matching snippets.
    secret=read(ROOT/'Assets/LocalWorking/AssetWorkbench/runtime/session.json')['token'].encode()
    key=(Path.home()/'.ssh/cs549_sftp_ed25519').read_bytes()
    for name in p['paths']:
        raw=(ROOT/name).read_bytes();assert secret not in raw and key not in raw,'Private credential in selected file: '+name
    psfiles=[name for name in p['paths'] if name.endswith('.ps1')]
    write(OUT/'PUBLICATION_POWERSHELL_FILES.json',psfiles)
    for i in range(0,len(p['paths']),40):
        subprocess.run(['git','-C',str(ROOT),'add','--',*p['paths'][i:i+40]],check=True,capture_output=True)
    staged=git('diff','--cached','--name-only','-z').decode().split('\0');staged=sorted(x for x in staged if x)
    assert staged==p['paths'], 'Unexpected staged set'
    pinned=[]
    for manifest in sorted((ROOT/'Unreal/Variants').glob('G1*/SOURCE_MANIFEST.json')):
        rel=manifest.relative_to(ROOT).as_posix()
        if rel not in staged:continue
        src=manifest.parent/'Project';rows=read(manifest)['files']
        assert hashlib.sha256(git('show',':'+rel)).hexdigest()==sha(manifest),rel
        for r in rows:
            name=(src/r['path']).relative_to(ROOT).as_posix()
            data=git('show',':'+name)
            assert len(data)==r['size_bytes'] and hashlib.sha256(data).hexdigest()==r['sha256'],name
        pinned.append(dict(manifest=rel,files=len(rows)))
    write(OUT/'STAGED_SOURCE_PROOF.json',dict(status='pass_exact_snapshot_bytes_no_credentials',staged_files=len(staged),snapshots=pinned,parent=p['parent']))
    print('STAGED EXACT',len(staged),'files;',len(pinned),'source snapshots byte verified')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('step',choices=['plan','stage']);a=ap.parse_args();{'plan':plan,'stage':stage}[a.step]()
