"""Publish the manually reviewed build; freeze exact retirement recovery first."""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/g1-audio-publication-20261009'
TRIAL = ROOT / 'tmp/Playtest-G1-Foley-V2-20261009'
VARIANT = ROOT / 'Unreal/Variants/G1FootContactAudio20261009'
RELEASE = 'paris-g1-playtest-20261009-audio-v2'
AID = 'paris-g1-packaged-playtest'
AUDIO_ID = 'paris-g1-recorded-audio'
GAME = '53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec'
ZIP = OUT / 'Paris-G1-Audio-V2-20261009.zip'
SHARE = ROOT / 'Assets/LocalShared/SFTP'
PROOF = ROOT / 'Docs/Development/G1AudioPublicationV2'
PY = Path(sys.executable)
PS = Path(os.environ['USERPROFILE']) / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
TARGETS = (
    'tmp/Playtest-G1-HUD-20261009',
    'tmp/Playtest-G1-AV-20261009',
    'tmp/Playtest-G1-Foley-20261009',
    'tmp/g1-playtest-revision-20261008/hud_v3/Archive',
    'tmp/g1-av-revision-20261009/candidate_v2/Archive',
    'tmp/g1-av-revision-20261009/candidate_v3/Archive',
    'tmp/g1-recorded-foley-20261009/candidate_v1/Archive',
    'tmp/g1-foot-contact-audio-v2-20261009/candidate_v1/Archive',
    'tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Archive',
)
CACHE = {}


def now():
    return datetime.now().astimezone().isoformat()


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')


def sha(path):
    info = path.stat()
    key = (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)
    if key not in CACHE:
        with path.open('rb') as stream:
            CACHE[key] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return CACHE[key]


def row(path, base=ROOT):
    return dict(path=path.relative_to(base).as_posix(), size_bytes=path.stat().st_size, sha256=sha(path))


def verify(path, item):
    assert path.is_file() and path.stat().st_size == item['size_bytes'] and sha(path) == item['sha256'], str(path)


def safe(name):
    path = ROOT / name
    assert path.resolve().is_relative_to(ROOT.resolve()) and path != ROOT, 'Outside workspace'
    for p in (path, *path.parents):
        if p == ROOT:
            break
        if p.exists():
            assert not p.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT, 'Reparse path: ' + str(p)
    return path


def inventory(folder):
    safe(folder.relative_to(ROOT).as_posix())
    found = []
    for parent, dirs, files in os.walk(folder, followlinks=False):
        for name in dirs + files:
            assert not (Path(parent) / name).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
        found += [Path(parent) / name for name in files]
    return sorted(found)


def idle_acl():
    expression = "$p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(UnrealEditor|WW2FranceLiberation|UnrealPak|ShaderCompileWorker|UnrealBuildTool|AutomationTool).*\\.exe$' -or ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool')});if($p.Count){throw 'Preserve active user/build processes'};(Get-Acl -LiteralPath '" + str(SHARE) + "').Sddl"
    return subprocess.check_output([str(PS), '-NoProfile', '-Command', expression], text=True).strip()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def transport():
    value = module('audio_publication_transport', ROOT / 'Tools/Integration/publish_native_playtest.py')
    value.OUT = OUT
    return value


def guards():
    sys.path.insert(0, str(ROOT / 'Tools/Integration'))
    from verify_team_source import verify_source
    guard = module('audio_publication_guards', ROOT / 'Tools/Integration/NPCInteractionV1/common.py')
    assert verify_source()['source_files'] == 758
    rows = guard.guard_rows()
    assert len(rows) == 703 and guard.guards_match(rows)
    native = read(ROOT / 'Assets/Sync/manifests/paris-gameplay-native-playtest.json')
    assert len(native['files']) == 359
    for item in native['files']:
        verify(ROOT / item['path'], item)
    source = read(VARIANT / 'SOURCE_MANIFEST.json')['files']
    assert len(source) == 42
    author = ROOT / 'tmp/g1-foot-contact-audio-v2-20261009/candidate_v2/Project'
    for item in source:
        verify(VARIANT / 'Project' / item['path'], item)
        verify(author / item['path'], item)
    return dict(source758=True, native359=True, protected703=True, selected42=True, authoring42=True)


def freeze():
    assert not (OUT / 'freeze.json').exists(), 'Preserve occupied freeze'
    acl = idle_acl()
    print('Verifying selected trial, source and protected anchors', flush=True)
    protected = guards()
    delivery = read(ROOT / 'tmp/g1-foot-contact-audio-v2-20261009/delivery.json')
    actual = {p.relative_to(TRIAL).as_posix() for p in inventory(TRIAL)}
    assert actual == {r['path'] for r in delivery['trial_files']} and len(actual) == 88
    for item in delivery['trial_files']:
        verify(TRIAL / item['path'], item)
    exe = TRIAL / 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
    assert sha(exe) == GAME
    cmd = TRIAL / 'PLAY_G1_REVISION.cmd'
    assert cmd.stat().st_nlink == 1 and all(s not in cmd.read_text() for s in ['ParisUXTest', 'ParisAVAuditOut', 'ParisAVSoloPlayer', 'NoSound', 'UnfocusedVolumeMultiplier'])
    preserve = []
    for name in ['Docs/Development/CURRENT_AUDIO_REVIEW.json', 'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json', 'Assets/Sync/CATALOG.json', 'Assets/Sync/manifests/paris-g1-packaged-playtest.json', 'Docs/Development/TeamSyncV1/AUTHORIZED_CATALOG_20261008.json']:
        p = ROOT / name
        shutil.copyfile(p, OUT / ('before-' + p.name))
        preserve.append(row(p))
    state = dict(at=now(), authorization='User manually retested and selects audio V2; authorizes obsolete local/SFTP packages removal, resource publication and Git commit/push',
                 game_sha256=GAME, root_acl=acl, free_before_bytes=shutil.disk_usage(ROOT).free,
                 protected=protected, trial_files=delivery['trial_files'], before=preserve,
                 source_manifest=row(VARIANT / 'SOURCE_MANIFEST.json'))
    write(OUT / 'freeze.json', state)
    print(json.dumps(dict(status='frozen_reviewed_build', files=88, protected=protected)), flush=True)


def package():
    state = read(OUT / 'freeze.json')
    assert idle_acl() == state['root_acl'] and not ZIP.exists()
    extras = OUT / 'sidecars'
    extras.mkdir()
    prerequisite = Path('C:/Program Files/Epic Games/UE_5.8/Engine/Extras/Redist/en-us/vc_redist.x64.exe')
    shutil.copyfile(prerequisite, extras / prerequisite.name)
    write(extras / 'SOURCE_VARIANT.json', dict(release=RELEASE, game_sha256=GAME, source_variant=VARIANT.relative_to(ROOT).as_posix(),
          source_manifest_sha256=state['source_manifest']['sha256'], source_files=42, audio_files=33, manual_review='Passed by Yupu Guo; selected for continued development',
          native_anchor='paris-native-playtest-20261008-g1-npc-vfx-v1', save_schema='ParisG1PlaytestV5', save_directory='%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestFoleyV220261009'))
    (extras / 'README.md').write_text('''# Paris G1 reviewed audio V2

Private Windows x64 build for Yupu Guo, Yuqi Pu and Jingdi Wu. Extract the entire
ZIP, then run PLAY_G1_REVISION.cmd. Install bundled vc_redist.x64.exe only if
the Microsoft x64 runtime is missing. Press Enter to start. WASD walk, Shift run,
Alt slow walk, Space jump, Left Ctrl crouch, Z prone, R reload while standing, left mouse
fire. F6/Ctrl+R restart, F9 load. After the three G1 guards are defeated, enter
the highlighted save circle and follow its consent prompt. User saves are absent
from this ZIP; the V5 schema and isolated audio-V2 save directory are retained.

Yupu manually retested this exact executable and selects it as the development
baseline. Models, finger poses, weapon/ammunition and save logic remain. Player
steps follow evaluated feet; takeoff/landing Foley and actual recorded M1 reports
are included. German live-fire audio remains a known source gap. Audio/CREDITS.txt
and PROVENANCE.json document sources; UI contains the Cinzel OFL notices.
No Unreal Editor/Python is needed to play. SOURCE_VARIANT.json pins the42-file
Git variant. Rebuilding requires entitled private native dependencies and the
separate33-cue manifest. Editor recook, teammate-machine, FPS/stress, natural-turn
video and course acceptance are separate. Do not publicly redistribute vendor
cooked assets. See the matching Git handoff for source and asset restoration.
''', 'utf-8')
    (extras / 'README_ZH.md').write_text('''# 巴黎G1人工复验音效V2

仅供Yupu Guo、Yuqi Pu、Jingdi Wu本项目私下使用。Windows x64，完整解压ZIP后
双击PLAY_G1_REVISION.cmd；只有缺少微软x64运行库时才安装随包vc_redist.x64.exe。
Enter开始，WASD走路、Shift跑步、Alt静步、Space跳跃、左Ctrl蹲下、Z匍匐、站立R换弹、
鼠标左键开枪。F6/Ctrl+R重开，F9读档。消灭G1三个守卫后进入高亮存档圈，按实际
提示确认保存。包内不含个人存档，保留V5格式和独立音效V2存档目录。

Yupu已人工复验此精确程序并选为开发基础。模型、手指、枪械/弹药与存档逻辑保留；
玩家脚步跟随实际骨骼阶段，补起跳/落地拟音及M1实录枪声。德军实录枪声仍有来源
缺口。Audio内有来源/许可记录，UI内有Cinzel字体OFL许可。试玩无需UE编辑器或
Python；SOURCE_VARIANT.json对应Git的42文件源码。重建需合法私有原生依赖及
单独33音效清单。编辑器重新烹饪、组员电脑、性能/压力、自然转身视频和课程验收
需分别完成，不公开转发商业烹饪资产。
''', 'utf-8')
    members = []
    inputs = [(TRIAL / r['path'], r['path'], r) for r in state['trial_files']]
    inputs += [(p, p.name, row(p, extras)) for p in sorted(extras.iterdir())]
    print('Writing selected ZIP64; every input checked against frozen bytes', flush=True)
    with zipfile.ZipFile(ZIP, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for path, name, item in inputs:
            verify(path, item)
            archive.write(path, name)
            members.append(dict(path=name, size_bytes=item['size_bytes'], sha256=item['sha256']))
    print('Reading every packaged member in full', flush=True)
    with zipfile.ZipFile(ZIP) as archive:
        assert len(archive.infolist()) == len(members)
        for item in members:
            with archive.open(item['path']) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == item['sha256']
            assert archive.getinfo(item['path']).file_size == item['size_bytes']
    write(OUT / 'package.json', dict(at=now(), zip=row(ZIP), members=members))
    print(json.dumps(dict(status='full_package_readback_pass', zip=row(ZIP), members=len(members))), flush=True)


def upload():
    state = read(OUT / 'package.json')
    assert idle_acl() == read(OUT / 'freeze.json')['root_acl']
    assert not (SHARE / 'releases' / RELEASE).exists(), 'Immutable release already exists'
    bridge = transport()
    audio_dir = TRIAL / 'Windows/WW2FranceLiberation/Audio'
    restore_dir = VARIANT / 'RuntimeAudio'
    restore_dir.mkdir()
    audio = []
    for p in sorted(audio_dir.glob('*.wav')):
        target = restore_dir / p.name
        shutil.copyfile(p, target)
        audio.append(row(target))
    assert len(audio) == 33
    assets = [state['zip'], *audio]
    commands = [f'mkdir "/incoming/{RELEASE}"']
    prefixes = set()
    final_rows = []
    for item in assets:
        h = item['sha256']; remote = f'/objects/sha256/{h[:2]}/{h}'
        final = SHARE / remote.lstrip('/')
        if not final.exists():
            if h[:2] not in prefixes and not final.parent.exists():
                commands.append(f'mkdir "/objects/sha256/{h[:2]}"')
            prefixes.add(h[:2])
            part = f'/incoming/{RELEASE}/{h}.part'
            commands += [f'put "{(ROOT / item["path"]).as_posix()}" "{part}"', f'rename "{part}" "{remote}"']
        back = OUT / 'readbacks' / h
        back.parent.mkdir(exist_ok=True)
        commands.append(f'get "{remote}" "{back.as_posix()}"')
        final_rows.append(dict(**item, storage='sftp', remote_path=remote))
    commands.append(f'rmdir "/incoming/{RELEASE}"')
    print('Authenticated upload and final immutable-object download', flush=True)
    bridge.batch(commands, 'objects')
    for item in final_rows:
        verify(OUT / 'readbacks' / item['sha256'], item)
    common = dict(schema_version=1, asset_version=RELEASE, owner='Yupu Guo', published_at=now(), license_record='Assets/Sync/RIGHTS.md',
                  sharing_status='owner_attested_private_three_member_original_and_derivative_sharing', recipients=['Yupu Guo', 'Yuqi Pu', 'Jingdi Wu'],
                  game_sha256=GAME, source_variant=VARIANT.relative_to(ROOT).as_posix(), source_manifest_sha256=read(OUT / 'freeze.json')['source_manifest']['sha256'],
                  verification=dict(method='Pinned-host authenticated SFTP final-object download and full SHA256/size comparison', manual_review='Yupu selects exact audio V2 after manual retest', second_machine='Not performed; assigned to teammates', editor_recook='Not performed', fps_stress='Not established'))
    package_manifest = dict(**common, asset_id=AID, source='Exact manually retested normal audio-V2 trial, unchanged native cooked closure',
                            engine='Unreal Engine5.8.2 CL56702186 Windows x64 Development', dependencies=[], runtime_python_required=False,
                            runtime_editor_bridge_required=False, scope='Private playable baseline; not course completion', entry='Extract all and run PLAY_G1_REVISION.cmd',
                            archive_members=state['members'], files=[final_rows[0]], file_count=1, size_bytes=final_rows[0]['size_bytes'])
    audio_manifest = dict(**common, asset_id=AUDIO_ID, source='Recorded CC0 Foley and M1 source derivatives; original synthesized German report retained explicitly',
                         dependencies=[], provenance=VARIANT.relative_to(ROOT).as_posix() + '/AUDIO_MANIFEST.json',
                         credits=VARIANT.relative_to(ROOT).as_posix() + '/AUDIO_CREDITS.txt',
                         scope='33 exact runtime audio cues for selected42-file source; copy to <Project>/Audio before Game build',
                         files=final_rows[1:], file_count=33, size_bytes=sum(r['size_bytes'] for r in final_rows[1:]))
    commands = [f'mkdir "/releases/{RELEASE}"']
    manifests = []
    for aid, manifest in [(AID, package_manifest), (AUDIO_ID, audio_manifest)]:
        local = OUT / (aid + '.json');write(local, manifest)
        remote = f'/releases/{RELEASE}/{local.name}'
        commands += [f'put "{local.as_posix()}" "{remote}"', f'get "{remote}" "{(OUT / ("returned-" + local.name)).as_posix()}"']
        manifests.append(dict(asset_id=aid, path=local.name, sha256=sha(local), release_manifest=remote))
    alias = f'/releases/{RELEASE}/{ZIP.name}'
    commands += [f'ln "{final_rows[0]["remote_path"]}" "{alias}"', f'get "{alias}" "{(OUT / "named-readback.zip").as_posix()}"']
    bridge.batch(commands, 'release')
    verify(OUT / 'named-readback.zip', final_rows[0])
    for item in manifests:
        verify(OUT / ('returned-' + item['path']), row(OUT / item['path']))
    probe = OUT / 'crud-probe.txt';probe.write_text('Audio V2 shared release CRUD check\n', 'utf-8')
    folder = f'/releases/{RELEASE}/_crud_probe'; returned = OUT / 'crud-returned.txt'
    bridge.batch([f'mkdir "{folder}"', f'put "{probe.as_posix()}" "{folder}/p.txt"', f'put "{probe.as_posix()}" "{folder}/p.txt"',
                  f'rename "{folder}/p.txt" "{folder}/q.txt"', f'get "{folder}/q.txt" "{returned.as_posix()}"', f'rm "{folder}/q.txt"', f'rmdir "{folder}"'], 'crud')
    verify(returned, row(probe))
    assert idle_acl() == read(OUT / 'freeze.json')['root_acl']
    guides = []
    for suffix, body in [('', f'Download {ZIP.name}, extract all, run PLAY_G1_REVISION.cmd. Private three-member release. Read bundled README.md. SHA256 {final_rows[0]["sha256"]}. Older HUD ZIP is retired; use this reviewed audio V2. Second-machine verification remains with teammates.\n'),
                         ('_ZH', f'下载{ZIP.name}，完整解压后双击PLAY_G1_REVISION.cmd。仅供三名组员私下使用，操作见包内README_ZH.md。SHA256 {final_rows[0]["sha256"]}。旧HUD包退休，改用此人工复验音效V2；另一台电脑由组员验证。\n')]:
        p=OUT / ('DOWNLOAD_README' + suffix + '.md');p.write_text(body, 'utf-8');guides.append(p)
    commands=[]
    for p in guides:
        remote=f'/releases/{RELEASE}/{p.name}'
        commands += [f'put "{p.as_posix()}" "{remote}"', f'get "{remote}" "{(OUT / ("returned-" + p.name)).as_posix()}"']
    bridge.batch(commands, 'guides')
    for p in guides:verify(OUT / ('returned-' + p.name), row(p))
    write(OUT / 'publication.json', dict(status='verified_pending_selection', at=now(), release=RELEASE, download=alias,
          manifests=manifests, zip=final_rows[0], audio_files=33, authenticated_readback=True, named_readback=True, shared_crud=True, root_acl_unchanged=True))
    for item in final_rows:(OUT / 'readbacks' / item['sha256']).unlink()
    (OUT / 'named-readback.zip').unlink()
    print('Package,33 audio objects, manifests, named download and shared CRUD verified', flush=True)


def select():
    state = read(OUT / 'publication.json'); assert state['status'] == 'verified_pending_selection'
    protected=guards()
    catalog_path=ROOT / 'Assets/Sync/CATALOG.json';catalog=read(catalog_path);before=row(catalog_path)
    ledger_path=ROOT / 'Docs/Development/TeamSyncV1/AUTHORIZED_CATALOG_20261008.json';ledger=read(ledger_path)
    assert before==ledger['current']
    old=ROOT / 'Assets/Sync/manifests/paris-g1-packaged-playtest.json'
    archived=ROOT / 'Assets/Sync/retired/paris-g1-playtest-20261009-hud-v3.json'
    assert not archived.exists();archived.parent.mkdir(exist_ok=True);shutil.copyfile(old,archived)
    old_selection=next(r for r in catalog['active_manifests'] if r['asset_id']==AID)
    catalog['retired_packaged_releases']=catalog.get('retired_packaged_releases',[])+[dict(**old_selection, retired_manifest=archived.relative_to(ROOT).as_posix(), reason='User selects manually reviewed audio V2 and authorizes deletion of obsolete packaged download bytes; see retirement receipt')]
    catalog['active_manifests']=[r for r in catalog['active_manifests'] if r['asset_id']!=AID]
    for item in state['manifests']:
        src=OUT/item['path'];assert sha(src)==item['sha256']
        dest=ROOT/'Assets/Sync/manifests'/item['path'];shutil.copyfile(src,dest);manifest=read(dest)
        catalog['active_manifests'].append(dict(asset_id=item['asset_id'],asset_version=RELEASE,path=dest.relative_to(ROOT).as_posix(),sha256=sha(dest),
            file_count=manifest['file_count'],size_bytes=manifest['size_bytes'],release_manifest=item['release_manifest']))
    catalog['updated_at']=now();write(catalog_path,catalog)
    proof_path=PROOF/'AUTHORIZED_CATALOG_20261009.json'
    authorization='2026-10-09 user manually approves audio V2 baseline and authorizes Git/SFTP publication and obsolete package removal'
    write(proof_path,dict(authorization=authorization,original=before,current=row(catalog_path),release=RELEASE,
        preserved_native_asset_version=ledger['release'],preserved_native_manifest_sha256=ledger['manifest_sha256'],native_selections_unchanged=True,
        previous_proof=ledger.get('current_update_proof'),previous_proof_sha256=ledger.get('current_update_proof_sha256'),authenticated_readback=True))
    ledger['previous_audio_publication_catalog']=before;ledger['current']=row(catalog_path);ledger['current_authorization']=authorization
    ledger['current_update_proof']=proof_path.relative_to(ROOT).as_posix();ledger['current_update_proof_sha256']=sha(proof_path);write(ledger_path,ledger)
    assert guards()==protected
    state['status']='verified_selected';write(OUT/'publication.json',state)
    print('Catalog now selects reviewed package and33 audio cues; native selections exact',flush=True)


def recovery():
    assert read(OUT/'publication.json')['status']=='verified_selected'
    assert idle_acl()==read(OUT/'freeze.json')['root_acl']
    assert not (OUT/'retirement.json').exists(),'Preserve occupied retirement plan'
    retained={}
    for p in inventory(TRIAL)+inventory(OUT/'sidecars'):
        item=row(p);retained[(item['sha256'],item['size_bytes'])]=item['path']
    targets=[];files=[];unique={}
    print('Hashing exact obsolete output inventory; deduplicating against selected bytes',flush=True)
    for name in TARGETS:
        folder=safe(name);assert folder.is_dir(),name
        found=inventory(folder)
        for p in found:
            item=row(p);info=p.stat();item.update(target=name,mtime_ns=info.st_mtime_ns)
            key=(item['sha256'],item['size_bytes'])
            if key in retained:item['recovery']=dict(kind='retained_file',path=retained[key])
            else:
                unique.setdefault(item['sha256'],p)
                item['recovery']=dict(kind='zip_entry',entry='objects/'+item['sha256'])
            files.append(item)
        targets.append(dict(path=name,files=len(found),size_bytes=sum(p.stat().st_size for p in found),kind='directory'))
    old_manifest=read(OUT/'before-paris-g1-packaged-playtest.json')
    old_zip=ROOT/old_manifest['files'][0]['path'];verify(old_zip,old_manifest['files'][0])
    zip_members=[]
    with zipfile.ZipFile(old_zip) as archive:
        assert len(archive.infolist())==len(old_manifest['archive_members'])
        for item in old_manifest['archive_members']:
            key=(item['sha256'],item['size_bytes'])
            entry=archive.getinfo(item['path']);assert entry.file_size==item['size_bytes']
            with archive.open(item['path']) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256']
            record=dict(item)
            if key in retained:record['recovery']=dict(kind='retained_file',path=retained[key])
            else:
                # Exact bytes from an inventoried obsolete directory can be reused.
                match=next((r for r in files if (r['sha256'],r['size_bytes'])==key),None)
                if match:record['recovery']=match['recovery']
                else:
                    extract=OUT/'recovery-inputs'/item['sha256'];extract.parent.mkdir(exist_ok=True)
                    if not extract.exists():
                        with archive.open(item['path']) as src,extract.open('xb') as dst:shutil.copyfileobj(src,dst)
                    verify(extract,item);unique.setdefault(item['sha256'],extract)
                    record['recovery']=dict(kind='zip_entry',entry='objects/'+item['sha256'])
            zip_members.append(record)
    recovery_zip=OUT/'retired_unique_files.zip'
    print('Compressing unique retired bytes; preserving source/logs/raw/save trees',flush=True)
    if not recovery_zip.exists():
        with zipfile.ZipFile(recovery_zip,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as archive:
            for h,p in unique.items():archive.write(p,'objects/'+h)
    with zipfile.ZipFile(recovery_zip) as archive:
        assert {i.filename for i in archive.infolist()}=={'objects/'+h for h in unique},'Occupied recovery ZIP does not match exact inputs'
        for h,p in unique.items():
            with archive.open('objects/'+h) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==h
            assert archive.getinfo('objects/'+h).file_size==p.stat().st_size
    recovery_row=row(recovery_zip)
    for item in files+zip_members:
        if item['recovery']['kind']=='zip_entry':item['recovery'].update(archive_path=recovery_row['path'],archive_sha256=recovery_row['sha256'])
    old_zip_row=row(old_zip);old_zip_row.update(kind='file',mtime_ns=old_zip.stat().st_mtime_ns)
    targets.append(old_zip_row)
    remote_object=old_manifest['files'][0]['remote_path']
    remote_alias='/releases/paris-g1-playtest-20261009-hud-v3/Paris-G1-HUD-20261009.zip'
    object_info=(SHARE/remote_object.lstrip('/')).stat();alias_info=(SHARE/remote_alias.lstrip('/')).stat()
    assert object_info.st_ino==alias_info.st_ino and object_info.st_size==old_manifest['files'][0]['size_bytes'] and object_info.st_nlink==2
    authenticated_path=OUT/'old-remote-authenticated-proof.json'
    if authenticated_path.exists():
        auth=read(authenticated_path)
        assert auth['remote_path']==remote_object and auth['alias']==remote_alias and auth['sha256']==old_manifest['files'][0]['sha256']
        assert auth['size_bytes']==object_info.st_size and auth['shared_inode']==object_info.st_ino and auth['links']==2
    else:
        remote_check=OUT/'old-sftp-retirement-readback.zip'
        assert not remote_check.exists(),'Preserve occupied old-package readback'
        transport().batch([f'get "{remote_object}" "{remote_check.as_posix()}"'],'old-package-retirement-readback')
        verify(remote_check,old_manifest['files'][0])
        write(authenticated_path,dict(at=now(),remote_path=remote_object,alias=remote_alias,
            sha256=sha(remote_check),size_bytes=remote_check.stat().st_size,shared_inode=object_info.st_ino,links=2,
            method='Pinned-host authenticated SFTP full download; local shell read denied, ACL unchanged'))
        remote_check.unlink()
    active=read(ROOT/'Assets/Sync/CATALOG.json')['active_manifests']
    assert all(remote_object not in {r['remote_path'] for r in read(ROOT/s['path'])['files']} for s in active)
    plan=dict(schema_version=1,authorization=read(OUT/'freeze.json')['authorization'],at=now(),targets=targets,files=files,
        old_zip=dict(file=old_zip_row,members=zip_members),recovery_zip=recovery_row,remote_remove=[remote_alias,remote_object],
        preserved_recovery_zip='Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/delivery_v1/Paris_Street_Combat_G1_Private_Candidate_Win64.zip',
        source_logs_raw_video_user_saves_untouched=True,free_before_delete_bytes=shutil.disk_usage(ROOT).free)
    write(OUT/'retirement.json',plan)
    write(PROOF/'RECOVERY_MAP_20261009.json',dict(schema_version=1,scope='Exact obsolete local directory files; prior raw receipts unchanged',
        recovery_zip=recovery_row,files=[{k:v for k,v in r.items() if k not in ['mtime_ns','target']} for r in files],old_package_members=zip_members))
    write(PROOF/'RETIREMENT_INVENTORY_20261009.json',dict(targets=targets,remote_remove=plan['remote_remove'],plan_sha256=sha(OUT/'retirement.json'),
        recovery_map_sha256=sha(PROOF/'RECOVERY_MAP_20261009.json'),recovery_zip=recovery_row,retained_legacy_recovery_zip=plan['preserved_recovery_zip']))
    print(json.dumps(dict(status='recovery_frozen_verified',targets=len(targets),files=len(files),unique_files=len(unique),recovery_zip=recovery_row)),flush=True)


def check_recovery():
    plan=read(OUT/'retirement.json');verify(ROOT/plan['recovery_zip']['path'],plan['recovery_zip'])
    unique={}
    with zipfile.ZipFile(ROOT/plan['recovery_zip']['path']) as archive:
        for item in plan['files']+plan['old_zip']['members']:
            rec=item['recovery']
            if rec['kind']=='retained_file':verify(ROOT/rec['path'],item)
            elif rec['entry'] not in unique:
                with archive.open(rec['entry']) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==item['sha256']
                assert archive.getinfo(rec['entry']).file_size==item['size_bytes'];unique[rec['entry']]=True
    return plan


def predelete():
    assert idle_acl()==read(OUT/'freeze.json')['root_acl']
    plan=check_recovery();guards()
    for target in plan['targets']:
        p=safe(target['path'])
        if target['kind']=='file':verify(p,target);assert p.stat().st_mtime_ns==target['mtime_ns']
        else:
            expected=[r for r in plan['files'] if r['target']==target['path']]
            assert {f.relative_to(ROOT).as_posix() for f in inventory(p)}=={r['path'] for r in expected}
            for item in expected:verify(ROOT/item['path'],item);assert (ROOT/item['path']).stat().st_mtime_ns==item['mtime_ns']
    print('All exact cleanup inputs, recovery bytes, protection and idle checks pass',flush=True)


def remote_retire():
    assert idle_acl()==read(OUT/'freeze.json')['root_acl'];plan=check_recovery()
    assert all(not (ROOT/t['path']).exists() for t in plan['targets'])
    old_manifest=read(OUT/'before-paris-g1-packaged-playtest.json');item=old_manifest['files'][0]
    active=read(ROOT/'Assets/Sync/CATALOG.json')['active_manifests']
    assert all(item['remote_path'] not in {f['remote_path'] for f in read(ROOT/s['path'])['files']} for s in active)
    authenticated=read(OUT/'old-remote-authenticated-proof.json')
    assert authenticated['sha256']==item['sha256'] and authenticated['size_bytes']==item['size_bytes']
    for name in plan['remote_remove']:
        info=(SHARE/name.lstrip('/')).stat()
        assert info.st_ino==authenticated['shared_inode'] and info.st_size==item['size_bytes']
    assert set(plan['remote_remove'])=={'/releases/paris-g1-playtest-20261009-hud-v3/Paris-G1-HUD-20261009.zip',item['remote_path']}
    assert (SHARE/item['remote_path'].lstrip('/')).stat().st_nlink==2,'Unknown hardlink reference'
    print('Removing only confirmed retired SFTP HUD ZIP alias/object',flush=True)
    bridge=transport();bridge.batch([f'rm "{p}"' for p in plan['remote_remove']],'retired-package-removal')
    assert all(not (SHARE/p.lstrip('/')).exists() for p in plan['remote_remove'])
    for suffix,body in [('', 'This HUD packaged download was retired by Yupu on9October2026 after manual audio-V2 acceptance. Its named ZIP and corresponding hash object were deleted to save space. Manifest metadata and exact unique-file recovery remain. Use /releases/'+RELEASE+'/'+ZIP.name+'.\n'),('_ZH','用户于2026年10月9日人工复验并选用音效V2；本旧HUD试玩ZIP及哈希对象已清理节省空间。清单与精确差异恢复档保留。请改下载/releases/'+RELEASE+'/'+ZIP.name+'。\n')]:
        p=OUT/('RETIRED'+suffix+'.md');p.write_text(body,'utf-8')
        remote='/releases/paris-g1-playtest-20261009-hud-v3/'+p.name
        bridge.batch([f'put "{p.as_posix()}" "{remote}"',f'get "{remote}" "{(OUT/("returned-"+p.name)).as_posix()}"'],'retired-guide'+suffix)
        verify(OUT/('returned-'+p.name),row(p))
        old_guide='DOWNLOAD_README'+suffix+'.md'
        redirect='/releases/paris-g1-playtest-20261009-hud-v3/'+old_guide
        returned=OUT/('redirect-returned-'+old_guide)
        original=OUT/('before-retired-'+old_guide)
        bridge.batch([f'get "{redirect}" "{original.as_posix()}"',f'put "{p.as_posix()}" "{redirect}"',f'get "{redirect}" "{returned.as_posix()}"'],'retired-redirect'+suffix)
        verify(returned,row(p))
    assert idle_acl()==read(OUT/'freeze.json')['root_acl']
    write(OUT/'remote-retirement.json',dict(at=now(),removed=plan['remote_remove'],removed_physical_bytes=item['size_bytes'],metadata_retained=True,root_acl_unchanged=True))


def verify_final():
    freeze=read(OUT/'freeze.json');plan=check_recovery();protected=guards()
    for item in freeze['trial_files']:verify(TRIAL/item['path'],item)
    assert len(inventory(TRIAL))==88
    assert all(not (ROOT/t['path']).exists() for t in plan['targets'])
    remote=read(OUT/'remote-retirement.json');assert all(not (SHARE/p.lstrip('/')).exists() for p in remote['removed'])
    assert idle_acl()==freeze['root_acl']
    publication=read(OUT/'publication.json')
    commands=[]
    for item in publication['manifests']:
        manifest=read(OUT/item['path'])
        assert sha(ROOT/'Assets/Sync/manifests'/item['path'])==item['sha256']
        for f in manifest['files']:
            assert (SHARE/f['remote_path'].lstrip('/')).stat().st_size==f['size_bytes']
            commands.append(f'ls -l "{f["remote_path"]}"')
    assert publication['authenticated_readback'] and publication['named_readback']
    assert (SHARE/publication['download'].lstrip('/')).stat().st_size==publication['zip']['size_bytes']
    commands.append(f'ls -l "{publication["download"]}"')
    transport().batch(commands,'final-authenticated-presence')
    user_saves=read(OUT/'user-save-guards.json')
    for item in user_saves:verify(Path(item['path']),item)
    result=dict(status='reviewed_audio_v2_selected_published_old_packages_retired',finished=now(),release=RELEASE,download=publication['download'],game_sha256=GAME,
        zip=publication['zip'],audio_files=33,local_targets_removed=len(plan['targets']),logical_local_removed_bytes=sum(t['size_bytes'] for t in plan['targets']),
        remote_removed_physical_bytes=remote['removed_physical_bytes'],compact_recovery_bytes=plan['recovery_zip']['size_bytes'],free_before_bytes=freeze['free_before_bytes'],
        free_after_bytes=shutil.disk_usage(ROOT).free,actual_net_free_increase_bytes=shutil.disk_usage(ROOT).free-freeze['free_before_bytes'],
        protected=protected,current_trial88_exact=True,user_saves_unchanged=len(user_saves),manual_review='Passed by user; active development baseline',natural_turn_video='Pending, no new recording',second_machine='Not tested',git='Matching commit/push requested; exact final HEAD is recorded outside its own Git tree')
    write(OUT/'result.json',result);write(PROOF/'RESULT_20261009.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step',choices=['freeze','package','upload','select','recovery','predelete','remote-retire','verify'])
    args=parser.parse_args();OUT.mkdir(exist_ok=True)
    {'freeze':freeze,'package':package,'upload':upload,'select':select,'recovery':recovery,'predelete':predelete,'remote-retire':remote_retire,'verify':verify_final}[args.step]()
