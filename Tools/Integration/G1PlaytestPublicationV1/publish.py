"""Publish the frozen HUD playtest; never builds, launches or edits native assets."""
import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RELEASE = 'paris-g1-playtest-20261009-hud-v3'
AID = 'paris-g1-packaged-playtest'
OUT = ROOT / 'tmp' / RELEASE
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
TRIAL = ROOT / 'tmp/Playtest-G1-HUD-20261009'
DELIVERY = STORE / 'Evidence/G1HUDConceptV1/delivery_v1'
VARIANT = ROOT / 'Unreal/Variants/G1HUDPlaytest20261009'
ZIP = OUT / 'Paris-G1-HUD-20261009.zip'
EXPECTED_GAME = '497221422d7754d562b4e6d11fd8cc50c9223e40b329b26c8c14391a98d1c42b'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def verify(path, row):
    assert path.is_file() and path.stat().st_size == row['size_bytes'] and sha(path) == row['sha256'], str(path)

def safe_child(parent, name):
    result = parent / name
    assert result.resolve().is_relative_to(parent.resolve()) and not result.is_symlink()
    return result

def guards():
    sys.path.insert(0, str(ROOT / 'Tools/Integration/NPCInteractionV1'))
    from common import guard_rows, guards_match
    sys.path.insert(0, str(ROOT / 'Tools/Integration'))
    from verify_team_source import verify_source
    assert verify_source()['source_files'] == 758
    rows = guard_rows()
    assert len(rows) == 703 and guards_match(rows)
    return {'canonical_source_files': 758, 'protected_files': 703}

def transport():
    spec = importlib.util.spec_from_file_location('playtest_transport', ROOT / 'Tools/Integration/publish_native_playtest.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.OUT = OUT
    return module

def idle_acl():
    # Read only: never stop a user-owned process or modify the chroot ACL.
    expression = "if (@(Get-Process UnrealEditor,UnrealEditor-Cmd,WW2FranceLiberation,blender -ErrorAction SilentlyContinue).Count) {throw 'Affected process running'}; (Get-Acl -LiteralPath '" + str(ROOT / 'Assets/LocalShared/SFTP') + "').Sddl"
    runtime = Path(os.environ['USERPROFILE']) / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
    assert runtime.is_file(), 'Use the established PowerShell 7 runtime for ACL reads'
    return subprocess.check_output([str(runtime), '-NoProfile', '-Command', expression], text=True).strip()

def prepare():
    assert not OUT.exists() and not VARIANT.exists(), 'Occupied publication identity; inspect before recovery'
    root_acl = idle_acl()
    print('Checking canonical source and protected native inputs', flush=True)
    protected = guards()
    receipt = read(DELIVERY / 'delivery_receipt.json')
    assert receipt['build'] == 'hud_v3' and receipt['game_sha256'] == EXPECTED_GAME
    assert read(TRIAL / 'REVISION_RECEIPT.json') == receipt
    source = receipt['source_patch_files']
    assert len(source) == 40
    assert len(receipt['archive_files']) == 47
    actual = {p.relative_to(TRIAL).as_posix() for p in TRIAL.rglob('*') if p.is_file()}
    expected = {r['path'] for r in receipt['archive_files']} | {'README.md', 'README_ZH.md', 'REVISION_RECEIPT.json'}
    assert actual == expected, 'Unexpected files in user trial; never include user saves/logs'
    OUT.mkdir(parents=True)
    source_manifest = []
    for row in source:
        src = safe_child(DELIVERY / 'SourcePatch', row['path'])
        verify(src, row)
        assert src.suffix in {'.cpp', '.h', '.cs', '.ini', '.uproject', '.uplugin'}
        assert b'\0' not in src.read_bytes(), 'Only source text is public'
        dst = safe_child(VARIANT / 'Project', row['path'])
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        verify(dst, row)
        source_manifest.append(row)
    contract = {'schema_version': 1, 'release': RELEASE, 'game_sha256': EXPECTED_GAME,
                'source_origin': 'Authenticated hud_v3 delivery SourcePatch; all 40 original text files byte-preserved',
                'canonical_asset_version': 'paris-native-playtest-20261008-g1-npc-vfx-v1',
                'scope': 'Packaged candidate source snapshot, not formal source/native adoption', 'files': source_manifest}
    write(VARIANT / 'SOURCE_MANIFEST.json', contract)
    (VARIANT / 'README.md').write_text('''# G1 HUD playtest source variant

9 October 2026. Exact forty-file source/configuration snapshot corresponding to
the privately shared hud_v3 executable. SOURCE_MANIFEST.json pins original bytes;
Project contains only team source/configuration, no purchased Content or binaries.
The canonical Unreal/ParisStreetCombat project and its 758-file contract retain
their previous release. This variant is explicitly selected by the packaged
playtest; cloning Git does not silently replace the formal editor baseline.

Use the packaged SFTP release for direct play: its prerequisites, launcher and
dependency payload are already included. The two readmes describe controls and
limits. Rebuilding additionally requires licensed private Content, including the
retained PlayerActionsV1/V6 dependencies, UE 5.8.2 and a supported Windows C++
toolchain. This source snapshot alone is not a complete editable native release.
Existing G1PlaytestRevisionV1 / G1HUDConceptV1 tools and dated implementation/result
documents record wrapper preparation, selected cook closure and original checks;
their private historical evidence paths are author-side inputs, not public files.
Never copy rejected draft cook directories or infer a teammate rebuild pass.

For a separate wrapper, restore entitled dependencies to a writable copy, overlay
these exact source/configuration paths and generate/build its Game target. The
font sidecar and G1 ground-map data are in the shared playable payload. An Editor
build, clean recook, teammate rebuild and formal source/native adoption have not
been verified for this published snapshot. Do not point a writer at immutable
SFTP objects or use this source publication to broaden asset redistribution.
''', encoding='utf-8')
    extras = OUT / 'bundle-sidecars'
    extras.mkdir()
    prerequisite = Path('C:/Program Files/Epic Games/UE_5.8/Engine/Extras/Redist/en-us/vc_redist.x64.exe')
    assert prerequisite.is_file()
    shutil.copyfile(prerequisite, extras / prerequisite.name)
    write(extras / 'SOURCE_VARIANT.json', contract)
    (extras / 'DISTRIBUTION_README.md').write_text('''# Private G1 HUD playtest — 9 October 2026

For Yupu Guo, Yuqi Pu and Jingdi Wu only. Keep commercial cooked assets private.
Extract the entire ZIP to a normal writable folder; do not launch inside the ZIP.
If the Microsoft VC++ x64 runtime is missing, install vc_redist.x64.exe, then
double-click PLAY_G1_REVISION.cmd. Windows x64; no Unreal Editor/Python required.
Read README.md for controls and known limits. Existing user saves are not included.
The executable is the tested hud_v3, not a new build or completed course release.
SOURCE_VARIANT.json ties the packaged game to the Git source snapshot. Cinzel font
OFL license/provenance accompany the runtime face under Windows/WW2FranceLiberation/UI.
External routing and a teammate-machine run still require teammate verification.
''', encoding='utf-8')
    (extras / 'DISTRIBUTION_README_ZH.md').write_text('''# 私有G1 HUD试玩 — 2026年10月9日

仅供Yupu Guo、Yuqi Pu、Jingdi Wu本项目私下使用，商业烹饪资产请勿公开转发。
把整个ZIP解压到普通可写文件夹；不要在压缩包内直接运行。若缺少微软x64运行库，
先安装vc_redist.x64.exe，再双击PLAY_G1_REVISION.cmd。Windows x64，无需UE编辑器
或Python。操作和限制见README_ZH.md。包内没有个人存档。
游戏为已测试hud_v3，未重新构建，也不代表课程全部验收完成。
SOURCE_VARIANT.json对应Git源码快照；Cinzel字体的OFL许可和来源随原字体保留。
公网连接、组员电脑运行仍由组员验证。
''', encoding='utf-8')
    expected_rows = {r['path']: dict(r) for r in receipt['archive_files']}
    override = receipt['delivery_launcher_override']
    assert override['path'] == 'PLAY_G1_REVISION.cmd'
    expected_rows[override['path']]['sha256'] = override['delivered_sha256']
    expected_rows[override['path']]['size_bytes'] = (TRIAL / override['path']).stat().st_size
    files = [(safe_child(TRIAL, name), name, expected_rows.get(name)) for name in sorted(expected)]
    files += [(p, p.name, None) for p in sorted(extras.iterdir())]
    members = []
    print('Writing ZIP64 and hashing every delivered file', flush=True)
    with zipfile.ZipFile(ZIP, 'x', compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
        for src, name, known in files:
            h = hashlib.sha256()
            size = 0
            with src.open('rb') as stream, archive.open(name, 'w', force_zip64=True) as target:
                for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
                    h.update(block); size += len(block); target.write(block)
            row = dict(path=name, size_bytes=size, sha256=h.hexdigest())
            if known:
                assert row == known, 'Delivered archive input drift: ' + name
            members.append(row)
    print('Reading back every ZIP member and checking hashes', flush=True)
    with zipfile.ZipFile(ZIP) as archive:
        assert len(archive.infolist()) == len(members)
        for row in members:
            with archive.open(row['path']) as stream:
                assert hashlib.file_digest(stream, 'sha256').hexdigest() == row['sha256'], row['path']
            assert archive.getinfo(row['path']).file_size == row['size_bytes']
    assert next(r for r in members if r['path'] == 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')['sha256'] == EXPECTED_GAME
    print('Hashing finished ZIP', flush=True)
    zip_row = dict(path=ZIP.relative_to(ROOT).as_posix(), size_bytes=ZIP.stat().st_size, sha256=sha(ZIP))
    write(OUT / 'package_receipt.json', {'status': 'local_package_verified', 'release': RELEASE,
          'created_at': datetime.now().astimezone().isoformat(), 'root_acl': root_acl,
          'protected': protected, 'zip': zip_row, 'members': members,
          'source_manifest_sha256': sha(VARIANT / 'SOURCE_MANIFEST.json')})
    print(json.dumps({'status': 'local_package_verified', 'files': len(members), **zip_row}), flush=True)

def upload():
    state = read(OUT / 'package_receipt.json')
    assert not (OUT / 'publication.json').exists()
    assert idle_acl() == state['root_acl']
    row = state['zip']; verify(ZIP, row)
    for r in read(VARIANT / 'SOURCE_MANIFEST.json')['files']:
        verify(safe_child(VARIANT / 'Project', r['path']), r)
    bridge = transport(); share = bridge.SHARE
    remote = f"/objects/sha256/{row['sha256'][:2]}/{row['sha256']}"
    assert not (share / 'releases' / RELEASE).exists(), 'Occupied immutable release'
    commands = [f'mkdir "/incoming/{RELEASE}"']
    target = share / remote.lstrip('/')
    if not target.exists():
        if not target.parent.exists():
            commands.append(f'mkdir "/objects/sha256/{row["sha256"][:2]}"')
        stage = f'/incoming/{RELEASE}/playtest.zip.part'
        commands += [f'put "{ZIP.as_posix()}" "{stage}"', f'rename "{stage}" "{remote}"']
    download = OUT / 'sftp-readback.zip'
    assert not download.exists()
    commands += [f'get "{remote}" "{download.as_posix()}"', f'rmdir "/incoming/{RELEASE}"']
    print('Uploading immutable package and downloading through authenticated SFTP', flush=True)
    bridge.batch(commands, 'objects')
    print('Checking downloaded ZIP SHA256 and size', flush=True)
    verify(download, row)
    file_row = {**row, 'storage': 'sftp', 'remote_path': remote}
    manifest = {'schema_version': 1, 'asset_id': AID, 'asset_version': RELEASE,
        'owner': 'Yupu Guo', 'published_at': datetime.now().astimezone().isoformat(),
        'engine': 'Unreal Engine 5.8.2 CL56702186 Windows x64 Development',
        'source': 'Existing tested hud_v3 frozen playable package; no rebuild or native adoption',
        'license_record': 'Assets/Sync/RIGHTS.md',
        'sharing_status': 'owner_attested_private_three_member_original_and_derivative_sharing',
        'recipients': ['Yupu Guo', 'Yuqi Pu', 'Jingdi Wu'],
        'scope': 'Private packaged human playtest; full MVP/course and teammate acceptance incomplete',
        'entry': 'Extract all; run PLAY_G1_REVISION.cmd; bundled vc_redist.x64.exe if runtime missing',
        'runtime_python_required': False, 'runtime_editor_bridge_required': False,
        'dependencies': [], 'dependencies_note': 'Cooked runtime closure bundled; editable rebuild additionally requires entitled native assets',
        'source_variant': VARIANT.relative_to(ROOT).as_posix(),
        'source_manifest_sha256': state['source_manifest_sha256'], 'game_sha256': EXPECTED_GAME,
        'verification': {'zip_members': 'Every member SHA256/size checked via full ZIP readback',
            'sftp': 'Final immutable ZIP and manifest downloaded through pinned-host authenticated SFTP and SHA256/size checked before selection',
            'external_connectivity': 'not retested', 'teammate_machine': 'not performed',
            'runtime': 'Previously recorded hud_v3 ordinary 1080p/720p and finite legitimate checkpoint passes; no new launch'},
        'archive_members': state['members'], 'files': [file_row], 'file_count': 1, 'size_bytes': row['size_bytes']}
    local = OUT / (AID + '.json'); write(local, manifest)
    returned = OUT / 'sftp-manifest.json'
    remote_manifest = f'/releases/{RELEASE}/{AID}.json'
    bridge.batch([f'mkdir "/releases/{RELEASE}"', f'put "{local.as_posix()}" "{remote_manifest}"',
        f'get "{remote_manifest}" "{returned.as_posix()}"'], 'manifest')
    verify(returned, dict(size_bytes=local.stat().st_size, sha256=sha(local)))
    probe = OUT / 'crud-probe.txt'; probe.write_text('Private packaged playtest CRUD verification\n', encoding='utf-8')
    returned_probe = OUT / 'crud-returned.txt'; folder = f'/releases/{RELEASE}/_crud_probe'
    bridge.batch([f'mkdir "{folder}"', f'put "{probe.as_posix()}" "{folder}/probe.txt"',
        f'put "{probe.as_posix()}" "{folder}/probe.txt"', f'rename "{folder}/probe.txt" "{folder}/renamed.txt"',
        f'get "{folder}/renamed.txt" "{returned_probe.as_posix()}"', f'rm "{folder}/renamed.txt"', f'rmdir "{folder}"'], 'crud')
    verify(returned_probe, dict(size_bytes=probe.stat().st_size, sha256=sha(probe)))
    assert idle_acl() == state['root_acl']
    protected = guards()
    write(OUT / 'publication.json', {'status': 'verified_pending_catalog_selection', 'release': RELEASE,
          'manifest_sha256': sha(local), 'zip': file_row, 'members': len(state['members']),
          'protected': protected, 'root_acl_unchanged': True, 'shared_crud': 'pass',
          'authenticated_zip_readback': 'pass', 'authenticated_manifest_readback': 'pass',
          'remote_manifest': remote_manifest, 'external_connectivity': 'not retested',
          'teammate_machine': 'not performed', 'verified_at': datetime.now().astimezone().isoformat()})
    print('SFTP package/manifest readback and shared CRUD verified; prior releases preserved', flush=True)

def link_and_guides():
    state = read(OUT / 'publication.json')
    assert state['status'] == 'verified_pending_catalog_selection'
    bridge = transport()
    directory = bridge.SHARE / 'releases' / RELEASE
    alias_remote = f'/releases/{RELEASE}/{ZIP.name}'
    created = OUT / 'named-link-created.json'
    # Use the shared account: the publishing shell has no authority to relax ACLs.
    # The successful SFTP hard-link extension creates one extra directory entry.
    if not created.exists():
        bridge.batch([f'ln "{state["zip"]["remote_path"]}" "{alias_remote}"'], 'authenticated-hardlink')
        write(created, {'status': 'authenticated_sftp_hardlink_created',
                        'source': state['zip']['remote_path'], 'target': alias_remote,
                        'log_sha256': sha(OUT / 'authenticated-hardlink.log')})
    creation = read(created)
    assert creation['status'] == 'authenticated_sftp_hardlink_created'
    assert creation['source'] == state['zip']['remote_path'] and creation['target'] == alias_remote
    assert creation['log_sha256'] == sha(OUT / 'authenticated-hardlink.log')
    download = safe_child(OUT, 'named-sftp-readback.zip')
    assert not download.exists(), 'Preserve an occupied readback for inspection'
    english = OUT / 'DOWNLOAD_README.md'; chinese = OUT / 'DOWNLOAD_README_ZH.md'
    english.write_text(f'''# Private G1 HUD playtest download

Download {ZIP.name} from this directory, extract all, then run PLAY_G1_REVISION.cmd.
The named file is an NTFS hard link to the immutable SHA256 object selected by
{AID}.json, so it uses no additional package storage. Do not edit either name.
Size: {state['zip']['size_bytes']} bytes.
SHA256: {state['zip']['sha256']}
Only Yupu Guo, Yuqi Pu and Jingdi Wu for this project; no public redistribution.
The package includes controls/known limits, Cinzel OFL notices and VC++ x64 runtime.
Second-machine and external-routing verification remain with the teammates.
''', encoding='utf-8')
    chinese.write_text(f'''# 私有G1 HUD试玩下载

下载本目录的{ZIP.name}，完整解压后双击PLAY_G1_REVISION.cmd。
此易读文件名是清单{AID}.json所选不可变哈希对象的NTFS硬链接，
不再占用一份压缩包空间。请勿修改任一名称下的内容。
大小：{state['zip']['size_bytes']}字节。
SHA256：{state['zip']['sha256']}
仅供Yupu Guo、Yuqi Pu、Jingdi Wu本项目私下使用，请勿公开转发。
包内附操作/限制说明、Cinzel OFL许可及微软x64运行库。
另一台电脑运行和公网连接仍由组员实际核对。
''', encoding='utf-8')
    commands = [f'ls -l "{alias_remote}"', f'get "{alias_remote}" "{download.as_posix()}"']
    for path in [english, chinese]:
        remote = f'/releases/{RELEASE}/{path.name}'
        commands += [f'put "{path.as_posix()}" "{remote}"',
                     f'get "{remote}" "{(OUT / ("returned-" + path.name)).as_posix()}"']
    print('Downloading named SFTP ZIP and release guides for final verification', flush=True)
    bridge.batch(commands, 'named-download-guides')
    verify(download, state['zip'])
    for path in [english, chinese]:
        verify(OUT / ('returned-' + path.name), dict(size_bytes=path.stat().st_size, sha256=sha(path)))
    assert idle_acl() == read(OUT / 'package_receipt.json')['root_acl']
    state['download_path'] = alias_remote
    state['named_download'] = 'Authenticated SFTP hard-link creation passes; full named ZIP and guides authenticated download/SHA256 readback pass; no duplicate archive bytes'
    write(OUT / 'publication.json', state)
    download.unlink()  # Own verified transfer sample only; never the published object.
    print('Readable SFTP ZIP entry and authenticated download guides verified', flush=True)

def select():
    status = read(OUT / 'publication.json')
    assert status['status'] == 'verified_pending_catalog_selection'
    assert 'download_path' in status
    src = OUT / (AID + '.json'); assert sha(src) == status['manifest_sha256']
    catalog_path = ROOT / 'Assets/Sync/CATALOG.json'; catalog = read(catalog_path)
    assert not any(row['asset_id'] == AID for row in catalog['active_manifests'])
    guards()
    ledger_path = ROOT / 'Docs/Development/TeamSyncV1/AUTHORIZED_CATALOG_20261008.json'
    ledger = read(ledger_path)
    old_catalog_row = dict(path=catalog_path.relative_to(ROOT).as_posix(),
                           size_bytes=catalog_path.stat().st_size, sha256=sha(catalog_path))
    assert old_catalog_row == ledger['current']
    assert 'current_authorization' not in ledger, 'Inspect a subsequent ledger update before selecting'
    write(OUT / 'catalog-ledger-before.json', ledger)
    dest = ROOT / 'Assets/Sync/manifests' / src.name
    assert not dest.exists(); shutil.copyfile(src, dest)
    catalog['active_manifests'].append(dict(asset_id=AID, asset_version=RELEASE,
        path=dest.relative_to(ROOT).as_posix(), sha256=sha(dest), file_count=1,
        size_bytes=status['zip']['size_bytes'], release_manifest=status['remote_manifest']))
    catalog['updated_at'] = datetime.now().astimezone().isoformat()
    write(catalog_path, catalog)
    new_catalog_row = dict(path=catalog_path.relative_to(ROOT).as_posix(),
                           size_bytes=catalog_path.stat().st_size, sha256=sha(catalog_path))
    proof_path = ROOT / 'Docs/Development/G1PlaytestPublicationV1/AUTHORIZED_CATALOG_20261009.json'
    write(proof_path, {'authorization': '2026-10-09 user requests Git commit/push and private SFTP playable package sharing',
        'original': old_catalog_row, 'current': new_catalog_row, 'release': RELEASE,
        'packaged_manifest_sha256': status['manifest_sha256'],
        'preserved_native_asset_version': ledger['release'],
        'preserved_native_manifest_sha256': ledger['manifest_sha256'],
        'native_selections_unchanged': True, 'only_catalog_guard_advances': True,
        'authenticated_zip_readback': status['authenticated_zip_readback'],
        'authenticated_manifest_readback': status['authenticated_manifest_readback']})
    # The existing mutable epoch ledger remains the guard API's authority. Preserve
    # its original anchor and Oct8 selection; explicitly record the authorized addition.
    ledger['previous_catalog_selection_20261008'] = dict(ledger['current'])
    ledger['current'] = new_catalog_row
    ledger['current_authorization'] = '2026-10-09 user requests Git commit/push and private SFTP playable package sharing'
    ledger['current_update_proof'] = proof_path.relative_to(ROOT).as_posix()
    ledger['current_update_proof_sha256'] = sha(proof_path)
    write(ledger_path, ledger)
    assert guards() == status['protected']
    status['status'] = 'verified_private_packaged_playtest_selected'; write(OUT / 'publication.json', status)
    # Keep the local release ZIP and immutable remote object; only remove own verified download copy.
    readback = safe_child(OUT, 'sftp-readback.zip')
    verify(readback, status['zip']); readback.unlink()
    print(json.dumps({k: v for k, v in status.items() if k != 'zip'}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['prepare', 'upload', 'link', 'select'])
    args = parser.parse_args()
    {'prepare': prepare, 'upload': upload, 'link': link_and_guides, 'select': select}[args.step]()
