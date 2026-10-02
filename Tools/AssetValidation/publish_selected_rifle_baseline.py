"""Dated selected-baseline relocation/publication. Hash verification precedes adoption.

No credentials are recorded. Uses an existing private SSH key and pinned known
hosts only for local SFTP probes. Does not commit/push or touch the chroot ACL.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RUN='rifle-motion-20261002-v1'
OUT=ROOT/'tmp'/RUN
LAB=ROOT/'Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1'
PROJECT=ROOT/'Assets/LocalWorking/Validation/UE582/2026-10-02-rifle-motion-v1'
SHARE=ROOT/'Assets/LocalShared/SFTP'
WORK=SHARE/'workspaces/yg745/rifle-motion-ue582-v1'
SOURCE=ROOT/'Assets/LocalWorking/Intake/2026-10-01/02_Rifle_Pro_MoCap_Pack_D059'
ORIGINAL=SHARE/'baselines/rifle-pro-mocap-original'/RUN
RIGHTS=ROOT/'Assets/Integration/WEAPON_INTAKE_RIGHTS_20261001.md'
OUT.mkdir(parents=True,exist_ok=True)
POWERSHELL=shutil.which('pwsh')
if not POWERSHELL:raise RuntimeError('This host requires PowerShell 7 for ACL/process checks')

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def verify(p,e):
    try:
        valid=p.is_file() and p.stat().st_size==e['size_bytes'] and digest(p)==e['sha256']
    except PermissionError:
        if not p.absolute().is_relative_to(SHARE):raise
        local=OUT/('server-verify-'+e['sha256']+'.dat')
        remote='/'+p.relative_to(SHARE).as_posix()
        sftp_batch([f'get "{remote}" "{local.as_posix()}"'],'verify-'+e['sha256'])
        valid=local.stat().st_size==e['size_bytes'] and digest(local)==e['sha256']
    if not valid:raise RuntimeError('File verification failed: '+str(p.relative_to(ROOT)))
def ordinary(p):
    if p.is_symlink() or p.is_junction():raise RuntimeError('Refusing alias at task target')
    for q in p.rglob('*'):
        if q.is_symlink() or q.is_junction():raise RuntimeError('Refusing reparse descendant')
def safe(p,base):
    p=p.absolute();base=base.resolve()
    if not p.resolve().is_relative_to(base) or p.resolve()==base:raise RuntimeError('Unsafe target')
    return p
def time():return datetime.now().astimezone().isoformat()
def idle():
    result=subprocess.run([POWERSHELL,'-NoProfile','-Command',"$ErrorActionPreference='Stop'; @(Get-Process UnrealEditor,UnrealEditor-Cmd,blender -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True,check=True)
    if int(result.stdout.strip()):raise RuntimeError('Close affected editors before relocation')
def acl():
    return subprocess.check_output([POWERSHELL,'-NoProfile','-Command',f"$ErrorActionPreference='Stop'; (Get-Acl -LiteralPath '{SHARE}').Sddl"],text=True).strip()
def grant(p):
    account=os.environ['COMPUTERNAME']+'\\cs549sftp'
    result=subprocess.run(['icacls',str(p),'/grant',account+':(OI)(CI)M','/T','/C'],capture_output=True,text=True)
    # icacls /C can return zero despite per-file access failures. Reject those
    # and use the exact elevated ACL helper rather than declaring success.
    if result.returncode or 'denied' in result.stderr.lower() or '拒绝' in result.stderr:
        raise RuntimeError('Shared ACL grant incomplete; run exact dated ACL helper')

def project():
    idle()
    if PROJECT.exists():raise RuntimeError('Projection exists; preserve it')
    saved=read(LAB/'Evidence/Baseline20261002/save.json')
    assert saved['status']=='complete_save_bounded_source_motion_only' and not saved['errors']
    assert len(saved['closure'])==33 and not any('M4' in r['package'] for r in saved['closure'])
    records=[]
    for e in saved['closure']:
        p=LAB/e['path'];v={'path':e['path'],'size_bytes':e['size_bytes_after'],'sha256':e['sha256_after']};verify(p,v);records.append(v)
    PROJECT.mkdir()
    for e in records:
        source=safe(LAB/e['path'],LAB);dest=safe(PROJECT/e['path'],PROJECT)
        dest.parent.mkdir(parents=True,exist_ok=True)
        # Move the one selected working copy, not another complete Content copy.
        source.rename(dest);verify(dest,e)
    shutil.copyfile(ROOT/'Tools/AssetValidation/lab_template.uproject',PROJECT/'RifleMotionBaseline.uproject')
    cfg=(ROOT/'Tools/AssetValidation/lab_DefaultEngine.ini').read_text(encoding='utf-8-sig')
    cfg='\n'.join(line for line in cfg.splitlines() if not line.startswith('SecurityToken='))+'\n'
    (PROJECT/'Config').mkdir();(PROJECT/'Config/DefaultEngine.ini').write_text(cfg,encoding='utf-8')
    write(PROJECT/'Evidence/selected_native.json',{'status':'local_selected_closure_pending_fresh','files':records,'source_plan':'Docs/Development/WEAPON_BASELINE_AND_SIMPLIFIED_RELOAD_V1.md'})
    print(json.dumps({'project':PROJECT.relative_to(ROOT).as_posix(),'moved_native_packages':len(records),'bytes':sum(e['size_bytes'] for e in records)}))

def headers(p):
    values=[];data=p.read_bytes()[:65536]
    for match in re.finditer(rb'\+\+UE[45]\+Release-[0-9.]+',data):
        if match.start()>=14:
            major,minor,patch,cl=struct.unpack('<HHHI',data[match.start()-14:match.start()-4])
            if major in (4,5) and minor<100 and patch<100:values.append(f'{major}.{minor}.{patch}')
    return values

def sftp_batch(commands, identity):
    key=Path(os.environ['USERPROFILE'])/'.ssh/cs549_sftp_ed25519'
    known=Path(os.environ['USERPROFILE'])/'.ssh/known_hosts_cs549'
    process=subprocess.run(['sftp','-b','-','-i',str(key),'-o','UserKnownHostsFile='+str(known),'-o','StrictHostKeyChecking=yes','-o','IdentitiesOnly=yes','-P','22222','cs549sftp@127.0.0.1'],input='\n'.join(commands)+'\n',capture_output=True,text=True)
    (OUT/(identity+'.log')).write_text(process.stdout+'\n'+process.stderr,encoding='utf-8')
    if process.returncode:raise RuntimeError('SFTP transfer failed; inspect private task log before recovery')

def publish(recover=False):
    idle()
    if not recover and (OUT/'publication.json').exists():raise RuntimeError('Publication already attempted; inspect exact retained state before recovery')
    current=WORK if recover else PROJECT
    fresh=read(current/'Evidence/Baseline20261002/fresh_v2.json')
    selection=read(current/'Evidence/selected_native.json')
    assert fresh['status']=='complete_fresh_bounded_source_motion_only' and not fresh['errors']
    assert len(fresh['closure'])==33 and not any('M4' in r['package'] for r in fresh['closure'])
    source_entries=next(a['files'] for a in read(ROOT/'tmp/weapon-intake-20261001/original_inventory.json')['assets'] if a['asset_id']=='02_Rifle_Pro_MoCap_Pack_D059')
    assert len(source_entries)==1563 and 'all three incoming deliveries' in RIGHTS.read_text(encoding='utf-8')
    ordinary(ORIGINAL if recover else SOURCE);ordinary(current)
    if not recover and (ORIGINAL.exists() or WORK.exists()):raise RuntimeError('Refuse occupied destinations')
    safe(ORIGINAL,SHARE/'baselines');safe(WORK,SHARE/'workspaces/yg745')
    original_current=ORIGINAL if recover else SOURCE
    for e in source_entries:verify(original_current/e['path'],e)
    if len([p for p in original_current.rglob('*') if p.is_file()])!=len(source_entries):raise RuntimeError('Original file count changed')
    for e in selection['files']:
        verify(current/e['path'],e)
        if '5.8.2' not in headers(current/e['path']):raise RuntimeError('Native package not resaved in UE5.8.2')
    root_acl=acl()
    if recover:
        result=read(OUT/'publication.json')
        assert result['status']=='relocating' and result['run_id']==RUN
        assert not SOURCE.exists() and not PROJECT.exists()
        assert result['root_acl_before_sha256']==hashlib.sha256(root_acl.encode()).hexdigest()
        result['recovery']='Verified exact relocated originals/workspace after local incoming ACL denial; transfers use authorized SFTP account'
    else:
        result={'status':'relocating','run_id':RUN,'started_at':time(),'root_acl_before_sha256':hashlib.sha256(root_acl.encode()).hexdigest()};write(OUT/'publication.json',result)
        ORIGINAL.parent.mkdir(parents=True,exist_ok=True)
        SOURCE.rename(ORIGINAL)
        PROJECT.rename(WORK)
    for e in source_entries:verify(ORIGINAL/e['path'],e)
    for e in selection['files']:verify(WORK/e['path'],e)
    grant(ORIGINAL);grant(WORK)
    original_files=[{'path':(ORIGINAL/e['path']).relative_to(ROOT).as_posix(),'storage':'sftp',
        'remote_path':'/'+(ORIGINAL/e['path']).relative_to(SHARE).as_posix(),'size_bytes':e['size_bytes'],'sha256':e['sha256']} for e in source_entries]
    common={'schema_version':1,'asset_version':RUN,'owner':'Yupu Guo','published_at':time(),
        'license_record':'Assets/Integration/WEAPON_INTAKE_RIGHTS_20261001.md','sharing_status':'owner_attested_private_three_member_original_and_derivative_sharing',
        'recipients':['Yupu Guo','Yuqi Pu','Jingdi Wu'],'retired_paths':[],'dependencies':[],
        'verification':{'method':'Every final server file rehashed SHA-256 and size; authenticated SFTP probes precede adoption','teammate_restoration':'not performed'}}
    original={**common,'asset_id':'rifle-pro-mocap-original','source':'Unmodified complete D059 delivery; provenance and rollback only, not automatic runtime restore',
        'catalog_selected':False,'engine':'Delivered version, not normalized','files':original_files,'file_count':len(original_files),'size_bytes':sum(e['size_bytes'] for e in original_files)}
    native_files=[]
    paths=[WORK/e['path'] for e in selection['files']]+[WORK/'RifleMotionBaseline.uproject',WORK/'Config/DefaultEngine.ini']
    incoming_remote='/incoming/'+RUN
    # The workstation user cannot write the protected incoming tree. Do not
    # relax its ACL: use the existing authorized shared SFTP identity instead.
    # Recovery resumes only this task's unique staging directory. Existing
    # final objects are hash-checked and never rewritten.
    sftp_batch([f'-mkdir "{incoming_remote}"',f'ls "{incoming_remote}"'],'publication-incoming')
    for p in paths:
        sha=digest(p);size=p.stat().st_size;e={'size_bytes':size,'sha256':sha}
        remote=f'/objects/sha256/{sha[:2]}/{sha}';final=safe(SHARE/remote.lstrip('/'),SHARE/'objects')
        if not final.exists():
            commands=[]
            if not final.parent.exists():commands.append(f'mkdir "/objects/sha256/{sha[:2]}"')
            stage=incoming_remote+'/'+sha+'.part'
            commands += [f'put "{p.as_posix()}" "{stage}"',f'rename "{stage}" "{remote}"']
            sftp_batch(commands,'object-'+sha)
        verify(final,e);verify(p,e)
        native_files.append({'path':p.relative_to(ROOT).as_posix(),'storage':'sftp','size_bytes':size,'sha256':sha,'remote_path':remote})
    native={**common,'asset_id':'rifle-pro-mocap-ue582-selected','source':'15 selected generic motions and 18 source-rig/material/texture dependencies, modern editor preview attachment removed; plus clean lab descriptor/config',
        'engine':'UE5.8.2-56702186','engine_plugins':['ACLPlugin (bundled UE animation compression)'],
        'scope':'Accepted generic source-motion baseline only; soldier retarget, foot/contact, FP/M1 reload, history and gameplay acceptance pending',
        'provenance_manifest':'Assets/Sync/manifests/rifle-pro-mocap-original.json','files':native_files,'file_count':len(native_files),'size_bytes':sum(e['size_bytes'] for e in native_files),
        'clips':[e['package'] for e in fresh['clips']]}
    release=SHARE/'releases'/RUN
    if release.exists():raise RuntimeError('Immutable release directory occupied')
    sftp_batch([f'mkdir "/releases/{RUN}"'],'publication-release')
    for m in (original,native):
        local=OUT/(m['asset_id']+'.json');write(local,m)
        final=release/local.name
        sftp_batch([f'put "{local.as_posix()}" "/releases/{RUN}/{local.name}"'],'manifest-'+m['asset_id'])
        verify(final,{'size_bytes':local.stat().st_size,'sha256':digest(local)})
    sftp_batch([f'rmdir "{incoming_remote}"'],'publication-staging-cleanup')
    if acl()!=root_acl:raise RuntimeError('Root ACL changed')
    result.update(status='server_bytes_verified_pending_client_adoption',completed_at=time(),root_acl_unchanged=True,
        original_files=len(source_entries),original_bytes=original['size_bytes'],native_files=native['file_count'],native_bytes=native['size_bytes'],native_package_headers_UE582=33)
    write(OUT/'publication.json',result)
    print(json.dumps(result))

def recover():
    publish(recover=True)

def client():
    result=read(OUT/'publication.json');assert result['status']=='server_bytes_verified_pending_client_adoption'
    key=Path(os.environ['USERPROFILE'])/'.ssh/cs549_sftp_ed25519'
    known=Path(os.environ['USERPROFILE'])/'.ssh/known_hosts_cs549'
    commands=[];checks=[]
    for aid in ('rifle-pro-mocap-original','rifle-pro-mocap-ue582-selected'):
        local=OUT/(aid+'.json');dest=OUT/('download-'+local.name)
        commands.append(f'get "/releases/{RUN}/{local.name}" "{dest.as_posix()}"')
        checks.append((dest,{'size_bytes':local.stat().st_size,'sha256':digest(local)}))
    native=read(OUT/'rifle-pro-mocap-ue582-selected.json')
    # All 35 final immutable selected files, not merely a transfer-size sample.
    for n,e in enumerate(native['files']):
        dest=OUT/f'client-native-{n}.dat';commands.append(f'get "{e["remote_path"]}" "{dest.as_posix()}"');checks.append((dest,e))
    original=read(OUT/'rifle-pro-mocap-original.json')
    e=next(e for e in original['files'] if e['path'].endswith('/W2_Stand_Aim_Reload_IP.uasset'))
    dest=OUT/'client-original-sample.dat';commands.append(f'get "{e["remote_path"]}" "{dest.as_posix()}"');checks.append((dest,e))
    probe=OUT/'crud-source.txt';probe.write_text('CS549 selected motion workspace CRUD probe\n',encoding='utf-8')
    remote='/workspaces/yg745/rifle-motion-ue582-v1/_crud_'+RUN
    commands += [f'mkdir "{remote}"',f'put "{probe.as_posix()}" "{remote}/probe.txt"',f'put "{probe.as_posix()}" "{remote}/probe.txt"',
        f'rename "{remote}/probe.txt" "{remote}/renamed.txt"',f'get "{remote}/renamed.txt" "{(OUT/"crud-download.txt").as_posix()}"',f'rm "{remote}/renamed.txt"',f'rmdir "{remote}"']
    process=subprocess.run(['sftp','-b','-','-i',str(key),'-o','UserKnownHostsFile='+str(known),'-o','StrictHostKeyChecking=yes','-o','IdentitiesOnly=yes','-P','22222','cs549sftp@127.0.0.1'],input='\n'.join(commands)+'\n',capture_output=True,text=True)
    (OUT/'sftp-client.log').write_text(process.stdout+'\n'+process.stderr,encoding='utf-8')
    if process.returncode:raise RuntimeError('SFTP verification failed; keep unpublished metadata and inspect ignored log')
    for p,e in checks:verify(p,e)
    verify(OUT/'crud-download.txt',{'size_bytes':probe.stat().st_size,'sha256':digest(probe)})
    write(OUT/'client.json',{'status':'complete','verified_at':time(),'native_files_downloaded':len(native['files']),
        'manifest_downloads':2,'original_samples':1,'workspace_crud':'create, overwrite, rename, download/read and delete passed; only task probes removed','known_host_check':'strict existing pinned known-hosts; external routing not retested'})
    print('Actual SFTP verified 35 selected files, two manifests, original sample and workspace CRUD')

def adopt():
    result=read(OUT/'publication.json');c=read(OUT/'client.json')
    assert result['status']=='server_bytes_verified_pending_client_adoption' and c['status']=='complete' and c['native_files_downloaded']==35
    catalog=read(ROOT/'Assets/Sync/CATALOG.json')
    if any(e['asset_id']=='rifle-pro-mocap-ue582-selected' for e in catalog['active_manifests']):raise RuntimeError('Already adopted')
    for aid in ('rifle-pro-mocap-original','rifle-pro-mocap-ue582-selected'):
        src=OUT/(aid+'.json');dest=ROOT/'Assets/Sync/manifests'/src.name
        if dest.exists():raise RuntimeError('Manifest exists')
        verify(SHARE/'releases'/RUN/src.name,{'size_bytes':src.stat().st_size,'sha256':digest(src)})
        shutil.copyfile(src,dest)
    native=read(OUT/'rifle-pro-mocap-ue582-selected.json');path='Assets/Sync/manifests/rifle-pro-mocap-ue582-selected.json'
    catalog['active_manifests'].append({'asset_id':native['asset_id'],'asset_version':RUN,'path':path,'sha256':digest(ROOT/path),
        'file_count':native['file_count'],'size_bytes':native['size_bytes'],'release_manifest':f'/releases/{RUN}/rifle-pro-mocap-ue582-selected.json'})
    catalog['updated_at']=time();write(ROOT/'Assets/Sync/CATALOG.json',catalog)
    write(ROOT/'Assets/Sync/RIFLE_MOTION_PUBLICATION_STATUS.json',{**result,'status':'verified_private_sftp_publication','client':c,
        'default_restore':'Only the 35 selected native/config files; complete delivered original is provenance/rollback and not Catalog-selected',
        'git_publication':'not committed/pushed in this task','runtime_scope':'generic source-motion only; no FP/M1/history/gameplay pass'})
    print('Adopted selected native baseline; original provenance manifest intentionally not default-restored')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['project','publish','recover','client','adopt']);args=parser.parse_args();globals()[args.mode]()
