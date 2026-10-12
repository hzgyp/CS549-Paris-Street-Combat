"""Publish unchanged reviewed76 and preserve the exact private course download."""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/G1GameplayBaselineAdoption20261011'))
from manage import sha,read,write,files,verify,selected_checks,check_processes,GAME,MANIFEST
OUT=ROOT/'tmp/g1-gameplay-publication-20261011'
PROOF=ROOT/'Docs/Development/G1GameplayPublication20261011'
SHARE=ROOT/'Assets/LocalShared/SFTP'
RELEASE='paris-g1-playtest-20261011-gameplay-v1'
ZIP=OUT/'Paris-G1-Gameplay-20261011.zip'
AID='paris-g1-packaged-playtest'
RID='paris-g1-gameplay-runtime-resources'
CID='paris-g1-course-review-package'
TRIAL=ROOT/'tmp/Playtest-G1-GrenadeEquip-20261011'
VARIANT=ROOT/'Unreal/Variants/G1GrenadeEquip20261011'
INNER='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
TEACHER_DOWNLOAD='/releases/paris-g1-playtest-20261009-audio-v2/Paris-G1-Audio-V2-20261009.zip'
TEACHER_SHA='7a8c225ad66ea673e20d0259324c3b5fef25be25bb66fcdddb5344533bd26d7d'
ACCESS=ROOT/'Assets/LocalShared/Deliverables/Assignment3/SFTPAccess_20261010'
PS=Path(os.environ['USERPROFILE'])/'.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'

def now():return datetime.now().astimezone().isoformat()
def row(p):return dict(path=p.relative_to(ROOT).as_posix(),size_bytes=p.stat().st_size,sha256=sha(p))
def acl():
    return subprocess.check_output([str(PS),'-NoProfile','-Command',"(Get-Acl -LiteralPath '"+str(SHARE)+"').Sddl"],text=True).strip()
def transport():
    spec=importlib.util.spec_from_file_location('gameplay_publication_transport',ROOT/'Tools/Integration/publish_native_playtest.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.OUT=OUT;return m
def batch(commands,label):transport().batch(commands,label)
def get(remote,dest,expected,label):
    dest.parent.mkdir(parents=True,exist_ok=True)
    batch([f'get "{remote}" "{dest.as_posix()}"'],label)
    verify(dest,expected)
def check_static(f):
    for r in f['source_files']:verify(VARIANT/'Project'/r['path'],r)
    for r in f['trial_files']:verify(TRIAL/r['path'],r)
    for r in f['native']:verify(ROOT/r['path'],r)
    for r in f['teacher_access']:verify(ROOT/r['path'],r)
    assert acl()==f['root_acl']

def prepare():
    assert not OUT.exists(),'Preserve occupied publication identity'
    OUT.mkdir();r=selected_checks()
    baseline=read(ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json')
    assert baseline['game_sha256']==GAME and baseline['status']=='selected_active_development_baseline'
    assert read(ROOT/'Docs/Development/G1GameplayBaselineAdoption20261011/CLOSURE_20261011.json')['status'].startswith('pass')
    source=read(VARIANT/'SOURCE_MANIFEST.json')['files']
    native=read(ROOT/'tmp/g1-grenade-equip-20261011/freeze.json')['protected_native']
    assert len(native)==1754
    for item in native:verify(ROOT/item['path'],item)
    access=[row(p) for p in files(ACCESS)]
    course_bundle=ROOT/'Assets/LocalShared/Deliverables/Assignment3/CS549-Assignment3-20261010.zip'
    access.append(row(course_bundle))
    connection=read(ACCESS/'CONNECTION.json')
    assert TEACHER_DOWNLOAD in json.dumps(connection,ensure_ascii=False),'Do not change course download target'
    old=read(ROOT/'Assets/Sync/manifests/paris-g1-packaged-playtest.json')
    assert old['asset_version']=='paris-g1-playtest-20261009-audio-v2' and old['files'][0]['sha256']==TEACHER_SHA
    f=dict(at=now(),authorization='User requests Git commit/push and private latest package sync plus old-package cleanup, explicitly retaining course reviewer package',source_files=source,trial_files=r['normal_files'],native=native,teacher_access=access,root_acl=acl(),catalog=row(ROOT/'Assets/Sync/CATALOG.json'),old_package=old,baseline=baseline,checks=r['checks'])
    write(OUT/'freeze.json',f)
    shutil.copyfile(ROOT/'Assets/Sync/CATALOG.json',OUT/'before-CATALOG.json')
    shutil.copyfile(ROOT/'Assets/Sync/manifests/paris-g1-packaged-playtest.json',OUT/'before-package-manifest.json')
    batch(['ls -l /releases','ls -l /releases/paris-g1-playtest-20261009-audio-v2','ls -l /releases/paris-g1-playtest-20261009-hud-v3'],'before-release-inventory')
    backup=OUT/'TeacherReview/Paris-G1-Audio-V2-20261009.zip'
    print('Authenticated full readback of protected teacher ZIP',flush=True)
    get(TEACHER_DOWNLOAD,backup,old['files'][0],'teacher-byte-readback')
    # The teacher alias and object are the same immutable NTFS file, not copies.
    obj=SHARE/old['files'][0]['remote_path'].lstrip('/');alias=SHARE/TEACHER_DOWNLOAD.lstrip('/')
    assert obj.stat().st_ino==alias.stat().st_ino and obj.stat().st_size==old['files'][0]['size_bytes']
    protected_remote=[]
    for p in files(SHARE/'releases/paris-g1-playtest-20261009-audio-v2'):
        protected_remote.append(dict(remote_path='/'+p.relative_to(SHARE).as_posix(),size_bytes=p.stat().st_size))
    write(OUT/'teacher-protection.json',dict(download=TEACHER_DOWNLOAD,zip=row(backup),remote_object=old['files'][0]['remote_path'],alias_object_same_inode=True,remote_files=protected_remote,access_files=access))
    print('Teacher ZIP authenticated/hash verified; course attachments frozen',flush=True)

def package():
    f=read(OUT/'freeze.json');check_static(f)
    assert not ZIP.exists() and not (SHARE/'releases'/RELEASE).exists()
    extras=OUT/'sidecars';extras.mkdir()
    prerequisite=Path('C:/Program Files/Epic Games/UE_5.8/Engine/Extras/Redist/en-us/vc_redist.x64.exe')
    shutil.copyfile(prerequisite,extras/prerequisite.name)
    write(extras/'SOURCE_VARIANT.json',dict(release=RELEASE,source_snapshot='Unreal/Variants/G1GrenadeEquip20261011/Project',source_files=76,source_manifest_sha256=MANIFEST,game_sha256=GAME,manual_review='Logic accepted; minor sleeve occlusion remains',save_prefix='ParisGrenadeEquipV2',user_directory='%LOCALAPPDATA%/ParisStreetCombat/G1GrenadeEquip20261011',teacher_package='Existing audioV2 course delivery is preserved separately; this is the new team build',verification='15 existing final-Game checks; no new Editor/second-machine/large-NPC acceptance'))
    (extras/'README.md').write_text('''# Paris Street Combat: reviewed complete gameplay

Private Windows x64 release for the three project members. Extract everything
and run PLAY_GRENADE_EQUIP.cmd. If necessary install bundled vc_redist.x64.exe.
WASD walk, Shift run, Alt slow, Space jump, Left Ctrl crouch, Z prone, R reload.
Wheel cycles rifle/available frag/available smoke, skipping exhausted equipment.
Hold left mouse to prepare; release to throw. Esc/wheel cancels before release.
Both grenade types exhausted: wheel stays on rifle. Frag can hurt allies/player;
smoke obscures sight and does not stop bullets. Observe mines; hold aimed E nearby
to disarm. Aim at a finite supply box and press E for supplies. Esc field manual
and real pause; Tab squad. Kill all three registered German defenders, enter the
highlighted circle and press E to save; actual validated completion opens success.
F9 load/F6 restart use confirmation. Death shows third-person collapse first.

User manually accepts logic. Minor sleeve occlusion remains. Original models,
rifle finger poses, gun and validated save mechanisms are retained. No personal
save, password, private key or raw supplier bundle is included. Full-motion,
large-NPC, matching Editor and new second-machine validation remain separate.
The course teacher's existing audioV2 ZIP and private access attachment remain
unchanged, independent of this latest team release.
''','utf-8')
    (extras/'FORMAL_README_ZH.md').write_text('''# 最新正式完整玩法版

完整解压，运行PLAY_GRENADE_EQUIP.cmd；必要时安装随包原微软vc_redist.x64.exe。
WASD走、Shift跑、Alt静步、空格跳、左Ctrl蹲、Z匍匐、R换弹。
滚轮只切仍有库存的手雷／烟雾与步枪；左键长按准备、松开投出，松开前Esc／滚轮取消。
投掷物全耗尽后保持步枪。手雷伤害自己／友军；烟雾遮视线、不挡子弹。
观察地雷，近处瞄准长按E拆除；瞄准有限补给箱按E。Esc战地手册／暂停，Tab小队。
全灭三名登记德军后进入高亮圈、按E保存，实际写盘核验成功后显示窗口；F9读档／F6重开需确认。
死亡先第三视角倒地再显示重开菜单。最新人工逻辑通过，衣袖遮挡待修。
原人物／手指常量／枪械／存档保护。未包含个人存档、密钥或原始供应商包。
包内原README_ZH为制作时历史候选说明；本文件与SOURCE_VARIANT说明正式采用状态。
老师原audioV2评阅包及课程访问附件保持原样；本包供三名组员私下测试最新正式版。
''','utf-8')
    inputs=[(TRIAL/x['path'],x['path'],x) for x in f['trial_files']]
    inputs += [(p,p.name,row(p)) for p in sorted(extras.iterdir())]
    members=[]
    print('Writing latest ZIP64 and fully verifying all members',flush=True)
    with zipfile.ZipFile(ZIP,'x',zipfile.ZIP_STORED,allowZip64=True) as z:
        for p,name,item in inputs:
            verify(p,item);z.write(p,name);members.append(dict(path=name,size_bytes=item['size_bytes'],sha256=item['sha256']))
    with zipfile.ZipFile(ZIP) as z:
        assert len(z.infolist())==len(members)
        for item in members:
            assert z.getinfo(item['path']).file_size==item['size_bytes']
            with z.open(item['path']) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256']
    resources=[];destroot=VARIANT/'RuntimeResources';assert not destroot.exists()
    for item in f['trial_files']:
        prefix='Windows/WW2FranceLiberation/'
        if item['path'].startswith(tuple(prefix+x+'/' for x in ['Audio','Equipment','UI'])):
            target=destroot/item['path'][len(prefix):];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(TRIAL/item['path'],target);verify(target,item);resources.append(row(target))
    write(OUT/'package.json',dict(zip=row(ZIP),members=members,resources=resources,teacher_backup=read(OUT/'teacher-protection.json')['zip']))
    print('PACKAGE VERIFIED',len(members),'members;',len(resources),'source runtime files',flush=True)

def upload():
    f=read(OUT/'freeze.json');p=read(OUT/'package.json');assert acl()==f['root_acl']
    assert not (SHARE/'releases'/RELEASE).exists()
    assets=[p['zip'],*p['resources']];commands=[f'mkdir "/incoming/{RELEASE}"'];prefixes=set();final=[]
    for item in assets:
        h=item['sha256'];remote=f'/objects/sha256/{h[:2]}/{h}'
        path=SHARE/remote.lstrip('/')
        if not path.exists():
            if h[:2] not in prefixes and not path.parent.exists():commands.append(f'mkdir "/objects/sha256/{h[:2]}"')
            prefixes.add(h[:2]);part=f'/incoming/{RELEASE}/{h}.part'
            commands += [f'put "{(ROOT/item["path"]).as_posix()}" "{part}"',f'rename "{part}" "{remote}"']
        back=OUT/'readbacks'/h;back.parent.mkdir(exist_ok=True)
        commands.append(f'get "{remote}" "{back.as_posix()}"')
        final.append(dict(item,storage='sftp',remote_path=remote))
    commands.append(f'rmdir "/incoming/{RELEASE}"')
    print('Authenticated latest package/resource upload and final object readback',flush=True)
    batch(commands,'final-objects')
    for item in final:verify(OUT/'readbacks'/item['sha256'],item)
    common=dict(schema_version=1,asset_version=RELEASE,owner='Yupu Guo',published_at=now(),license_record='Assets/Sync/RIGHTS.md',sharing_status='owner_attested_private_three_member_original_and_derivative_sharing',recipients=['Yupu Guo','Yuqi Pu','Jingdi Wu'],game_sha256=GAME,source_variant='Unreal/Variants/G1GrenadeEquip20261011',source_manifest_sha256=MANIFEST,verification=dict(method='Pinned-host authenticated SFTP final byte readback SHA256/size',manual_review='User logic acceptance with residual sleeve occlusion',second_machine='Not retested for76',editor_recook='Not performed'))
    package_manifest=dict(common,asset_id=AID,engine='Unreal Engine5.8.2 Windows x64 Development',source='Unchanged reviewed100-file normal trial plus release guides and Microsoft runtime',scope='Current three-member private formal gameplay; course audioV2 retained separately',dependencies=[],runtime_python_required=False,runtime_editor_bridge_required=False,entry='Extract all; PLAY_GRENADE_EQUIP.cmd',archive_members=p['members'],files=[final[0]],file_count=1,size_bytes=final[0]['size_bytes'])
    resources_manifest=dict(common,asset_id=RID,source='Exact Audio/Equipment/UI runtime inputs for the source76 wrapper',scope='Copy RuntimeResources contents into matching Project before build; private model/texture/audio/font bytes, not Git source',dependencies=[],files=final[1:],file_count=len(final)-1,size_bytes=sum(x['size_bytes'] for x in final[1:]))
    teacher=dict(f['old_package']);teacher.update(asset_id=CID,source='Protected exact previously supplied course audioV2 compiled game; preserved by explicit user instruction11October2026',scope='Private instructor/mentor/TA compiled assessment; original download and course attachment unchanged',recipients=['Yupu Guo','Yuqi Pu','Jingdi Wu','Course instructor/mentor and teaching assistants'],sharing_status='owner_attested_private_course_review_compiled_game',files=[dict(p['teacher_backup'],storage='sftp',remote_path=f['old_package']['files'][0]['remote_path'])],file_count=1,size_bytes=p['teacher_backup']['size_bytes'])
    manifests=[];commands=[f'mkdir "/releases/{RELEASE}"']
    for aid,m in [(AID,package_manifest),(RID,resources_manifest),(CID,teacher)]:
        local=OUT/(aid+'.json');write(local,m);remote=f'/releases/{RELEASE}/{local.name}'
        commands += [f'put "{local.as_posix()}" "{remote}"',f'get "{remote}" "{(OUT/("returned-"+local.name)).as_posix()}"']
        manifests.append(dict(asset_id=aid,path=local.name,sha256=sha(local),release_manifest=remote))
    alias=f'/releases/{RELEASE}/{ZIP.name}'
    commands += [f'ln "{final[0]["remote_path"]}" "{alias}"',f'get "{alias}" "{(OUT/"named-readback.zip").as_posix()}"']
    batch(commands,'release-manifests-alias')
    verify(OUT/'named-readback.zip',final[0])
    for m in manifests:verify(OUT/('returned-'+m['path']),row(OUT/m['path']))
    for name,text in [('DOWNLOAD_README.md',f'Download {ZIP.name}, extract all, run PLAY_GRENADE_EQUIP.cmd. Current source76/Game {GAME}. ZIP SHA256 {p["zip"]["sha256"]}. Three-member private release. Protected older course download remains {TEACHER_DOWNLOAD}.\n'),('DOWNLOAD_README_ZH.md',f'最新正式版：完整解压{ZIP.name}，运行PLAY_GRENADE_EQUIP.cmd。衣袖遮挡待修，逻辑人工通过。ZIP SHA256 {p["zip"]["sha256"]}。仅三名组员私下共享；老师原评阅包{TEACHER_DOWNLOAD}保持。\n')]:
        local=OUT/name;local.write_text(text,'utf-8');remote=f'/releases/{RELEASE}/{name}'
        batch([f'put "{local.as_posix()}" "{remote}"',f'get "{remote}" "{(OUT/("returned-"+name)).as_posix()}"'],'guide-'+name)
        verify(OUT/('returned-'+name),row(local))
    assert acl()==f['root_acl']
    write(OUT/'publication.json',dict(status='authenticated_verified_pending_selection',release=RELEASE,download=alias,manifests=manifests,zip=final[0],resource_files=len(p['resources']),teacher_protected=TEACHER_DOWNLOAD,root_acl_unchanged=True,named_readback=True))
    print('LATEST SFTP BYTES VERIFIED; teacher role retained separately',flush=True)

def select():
    f=read(OUT/'freeze.json');pub=read(OUT/'publication.json')
    assert pub['status']=='authenticated_verified_pending_selection'
    catp=ROOT/'Assets/Sync/CATALOG.json';verify(catp,f['catalog']);cat=read(catp)
    ledgerp=ROOT/'Docs/Development/TeamSyncV1/AUTHORIZED_CATALOG_20261008.json';ledger=read(ledgerp);assert ledger['current']==f['catalog']
    retired=ROOT/'Assets/Sync/retired/paris-g1-playtest-20261009-audio-v2.json';assert not retired.exists();shutil.copyfile(OUT/'before-package-manifest.json',retired)
    oldsel=next(x for x in cat['active_manifests'] if x['asset_id']==AID)
    cat['retained_course_releases']=cat.get('retained_course_releases',[])+[dict(oldsel,retained_manifest=retired.relative_to(ROOT).as_posix(),download=TEACHER_DOWNLOAD,reason='Explicitly protected teacher assessment; bytes/download unchanged; now active as course-review logical role')]
    cat['active_manifests']=[x for x in cat['active_manifests'] if x['asset_id']!=AID]
    for m in pub['manifests']:
        src=OUT/m['path'];assert sha(src)==m['sha256'];dest=ROOT/'Assets/Sync/manifests'/m['path'];shutil.copyfile(src,dest);d=read(dest)
        cat['active_manifests'].append(dict(asset_id=m['asset_id'],asset_version=d['asset_version'],path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),file_count=d['file_count'],size_bytes=d['size_bytes'],release_manifest=m['release_manifest']))
    cat['updated_at']=now();write(catp,cat)
    proof=dict(authorization=f['authorization'],before=f['catalog'],after=row(catp),new_package=pub['zip'],teacher_retained=TEACHER_DOWNLOAD,manifests=pub['manifests'],only_package_and_runtime_roles_advance=True,native_manifests_unchanged=True)
    write(PROOF/'AUTHORIZED_CATALOG_20261011.json',proof)
    ledger.update(previous_gameplay_publication_catalog=f['catalog'],current=row(catp),current_authorization=f['authorization'],current_update_proof='Docs/Development/G1GameplayPublication20261011/AUTHORIZED_CATALOG_20261011.json',current_update_proof_sha256=sha(PROOF/'AUTHORIZED_CATALOG_20261011.json'))
    write(ledgerp,ledger)
    bpath=ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json';b=read(bpath)
    b.update(sftp_release=RELEASE,sftp_download=pub['download'],sftp_manifest='Assets/Sync/manifests/'+AID+'.json',sftp_zip_sha256=pub['zip']['sha256'],runtime_resource_manifest='Assets/Sync/manifests/'+RID+'.json',publication_status='Latest private SFTP bytes verified; matching Git commit/push pending',course_package_retained=dict(download=TEACHER_DOWNLOAD,manifest='Assets/Sync/manifests/'+CID+'.json',game_sha256=f['old_package']['game_sha256']))
    write(bpath,b)
    print('Catalog selects current gameplay and independent retained teacher package',flush=True)

def audit_remote():
    f=read(OUT/'freeze.json');teacher=read(OUT/'teacher-protection.json');pub=read(OUT/'publication.json')
    # Only known G1 packaged-release directories are eligible; never scan/prune
    # unrelated objects, native originals, incoming or teammate workspaces.
    found=[]
    for folder in sorted((SHARE/'releases').glob('paris-g1-playtest-*')):
        for p in files(folder):
            if p.suffix.lower()=='.zip':found.append(dict(path='/'+p.relative_to(SHARE).as_posix(),size_bytes=p.stat().st_size))
    assert {x['path'] for x in found}=={TEACHER_DOWNLOAD,pub['download']},'Unknown old packaged ZIP: retain and investigate'
    for x in teacher['remote_files']:
        p=SHARE/x['remote_path'].lstrip('/');assert p.is_file() and p.stat().st_size==x['size_bytes']
    assert (SHARE/teacher['remote_object'].lstrip('/')).stat().st_ino==(SHARE/TEACHER_DOWNLOAD.lstrip('/')).stat().st_ino
    for x in f['teacher_access']:verify(ROOT/x['path'],x)
    assert acl()==f['root_acl']
    batch([f'ls -l "{TEACHER_DOWNLOAD}"',f'ls -l "{teacher["remote_object"]}"',f'ls -l "{pub["download"]}"'],'final-protected-presence')
    write(PROOF/'REMOTE_RETENTION_20261011.json',dict(status='pass_current_and_teacher_preserved_no_unused_old_zip_remaining',packaged_zips=found,teacher_bytes_full_authenticated_sha256=TEACHER_SHA,teacher_download_unchanged=True,teacher_access_unchanged=True,obsolete_zip_bytes_removed=0,reason='Old HUD ZIP already retired; the only earlier remaining playable ZIP is the explicitly protected teacher package',no_native_objects_or_workspaces_pruned=True,root_acl_unchanged=True))
    print('REMOTE RETENTION PASS: latest plus protected teacher; no obsolete ZIP eligible',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('step',choices=['prepare','package','upload','select','audit-remote']);a=p.parse_args()
    {'prepare':prepare,'package':package,'upload':upload,'select':select,'audit-remote':audit_remote}[a.step]()
