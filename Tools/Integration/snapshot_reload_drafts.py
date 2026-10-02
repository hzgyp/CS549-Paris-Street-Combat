"""Private immutable diagnostic snapshot; never Catalog/production admission."""
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SHARE=ROOT/'Assets/LocalShared/SFTP'
STORE=SHARE/'workspaces/yg745/paris-gameplay-v1'
EVIDENCE=STORE/'Evidence/P4/SimplifiedReload20261002'
RUN='paris-reload-draft-20261002-v1'
OUT=ROOT/'tmp'/RUN
OUT.mkdir(parents=True,exist_ok=True)
POWERSHELL=shutil.which('pwsh')

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def batch(commands,identity):
    profile=Path(os.environ['USERPROFILE'])
    p=subprocess.run(['sftp','-b','-','-i',str(profile/'.ssh/cs549_sftp_ed25519'),'-o','UserKnownHostsFile='+str(profile/'.ssh/known_hosts_cs549'),'-o','StrictHostKeyChecking=yes','-o','IdentitiesOnly=yes','-P','22222','cs549sftp@127.0.0.1'],input='\n'.join(commands)+'\n',capture_output=True,text=True)
    (OUT/(identity+'.log')).write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
    if p.returncode:raise RuntimeError('Snapshot transfer failed: inspect private task log, no metadata adoption')
def acl():
    return subprocess.check_output([POWERSHELL,'-NoProfile','-Command',f"(Get-Acl -LiteralPath '{SHARE}').Sddl"],text=True).strip()

if (OUT/'started.json').exists():raise RuntimeError('Snapshot attempted: inspect retained state, do not repeat')
count=subprocess.check_output([POWERSHELL,'-NoProfile','-Command','@(Get-Process UnrealEditor,UnrealEditor-Cmd,blender -ErrorAction SilentlyContinue).Count'],text=True)
assert int(count.strip())==0, 'Close affected editors'
old=read(ROOT/'Assets/Integration/LOCAL_DRAFT_INVENTORY_20261001.json')
fresh=read(EVIDENCE/'fresh_v2.json')
assert fresh['status']=='pass_fresh_bounded_reload_only' and not fresh['bridge_available']
cases=[read(EVIDENCE/f'probe_{f}_v1.json') for f in (30,60,120)]
assert all(x['status']=='pass_probe_bounded_reload_only' and all(c['all_pass'] for c in x['cases']) for x in cases)
records=[{'path':(STORE/e['workspace_path']).relative_to(ROOT).as_posix(),'sha256':e['sha256'],'size_bytes':e['size_bytes']} for e in old['files']]
assert len(records)==25 and len(fresh['assets'])==3
records += [{k:e[k] for k in ('path','sha256','size_bytes')} for e in fresh['assets']]
for e in records:
    p=ROOT/e['path'];assert p.resolve().is_relative_to(STORE.resolve())
    assert p.stat().st_size==e['size_bytes'] and digest(p)==e['sha256'], 'Preserve unique changed drafts'
dest=ROOT/'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json'
assert not dest.exists() and not (SHARE/'releases'/RUN).exists()
root_acl=acl()
(OUT/'started.json').write_text(json.dumps({'status':'uploading_private_diagnostic_snapshot','run_id':RUN,'root_acl_sha256':hashlib.sha256(root_acl.encode()).hexdigest()}),encoding='utf-8')
commands=[f'mkdir "/incoming/{RUN}"'];prefixes=set()
for e in records:
    sha=e['sha256'];e['storage']='sftp';e['remote_path']=f'/objects/sha256/{sha[:2]}/{sha}'
    final=SHARE/e['remote_path'].lstrip('/')
    if not final.exists():
        parent=sha[:2]
        if parent not in prefixes and not final.parent.exists():commands.append(f'mkdir "/objects/sha256/{parent}"')
        prefixes.add(parent)
        stage=f'/incoming/{RUN}/{sha}.part'
        commands += [f'put "{(ROOT/e["path"]).as_posix()}" "{stage}"',f'rename "{stage}" "{e["remote_path"]}"']
    commands.append(f'get "{e["remote_path"]}" "{(OUT/(sha+".dat")).as_posix()}"')
commands.append(f'rmdir "/incoming/{RUN}"')
batch(commands,'files')
for e in records:
    p=OUT/(e['sha256']+'.dat');assert p.stat().st_size==e['size_bytes'] and digest(p)==e['sha256']
assert acl()==root_acl
snapshot={'schema_version':1,'asset_id':'paris-reload-diagnostic-draft-snapshot','asset_version':RUN,
    'status':'VERIFIED_PRIVATE_DIAGNOSTIC_SNAPSHOT_NOT_CATALOG_SELECTED','owner':'yg745','engine':fresh['engine'],
    'verified_at':datetime.now().astimezone().isoformat(),'catalog_selected':False,'restore_authority':False,
    'scope':'28 team-owned native drafts frozen for rollback/diagnostic continuity only; not final P2/P3/P4, FP, history, performance or package acceptance',
    'dependencies':['character-ue582-integration-baseline'],'dependency_record':'Assets/Sync/manifests/character-ue582-integration-baseline.json',
    'runtime_workspace':STORE.relative_to(ROOT).as_posix(),'files':records,'file_count':28,'new_reload_files':3,'unchanged_previous_files':25,
    'size_bytes':sum(e['size_bytes'] for e in records),
    'tests':{'native_groups':18,'assertions_passed':sum(len(c['cases']) for x in cases for c in x['cases']),
        'fixed_steps_per_second':[30,60,120],'playback_rates':[.5,1,1.5],'bridge_disabled_fresh_packages':3},
    'verification':'All 28 final immutable objects downloaded over authenticated, pinned-host SFTP and SHA-256/size verified; protected root ACL unchanged',
    'git_publication':'not committed or pushed','restoration_note':'Not Catalog-selected: do not automatically overwrite local work. Snapshot needs its published native dependencies and later coordinated owner-specific restoration.'}
local=OUT/'draft-snapshot.json';local.write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
download=OUT/'manifest-download.json'
batch([f'mkdir "/releases/{RUN}"',f'put "{local.as_posix()}" "/releases/{RUN}/draft-snapshot.json"',f'get "/releases/{RUN}/draft-snapshot.json" "{download.as_posix()}"'],'manifest')
assert digest(download)==digest(local) and acl()==root_acl
shutil.copyfile(local,dest)
print(json.dumps({'status':snapshot['status'],'files':28,'new_files':3,'bytes':snapshot['size_bytes'],'tests':snapshot['tests']}))
