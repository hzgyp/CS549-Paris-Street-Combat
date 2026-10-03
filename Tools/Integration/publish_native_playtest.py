"""Publish this dated private playtest; never modifies native source packages."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARE = ROOT / 'Assets/LocalShared/SFTP'
RUN = 'paris-native-playtest-20261003-v1'
OUT = ROOT / 'tmp' / RUN
AID = 'paris-gameplay-native-playtest'

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    with p.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def verify(p, e):
    if p.stat().st_size != e['size_bytes'] or sha(p) != e['sha256']:
        raise RuntimeError('Mismatched bytes: ' + str(p))

def batch(commands, label):
    profile = Path(os.environ['USERPROFILE'])
    process = subprocess.run(['sftp', '-b', '-', '-P', '22222',
        '-i', str(profile / '.ssh/cs549_sftp_ed25519'),
        '-o', 'UserKnownHostsFile=' + str(profile / '.ssh/known_hosts_cs549'),
        '-o', 'StrictHostKeyChecking=yes', '-o', 'IdentitiesOnly=yes',
        'cs549sftp@127.0.0.1'], input='\n'.join(commands) + '\n',
        text=True, capture_output=True)
    (OUT / (label + '.log')).write_text(process.stdout + '\n' + process.stderr, encoding='utf-8')
    if process.returncode:
        raise RuntimeError('SFTP failed; preserve private log ' + label)

def idle_and_acl():
    ps = shutil.which('pwsh')
    count = subprocess.check_output([ps, '-NoProfile', '-Command',
        '@(Get-Process UnrealEditor,UnrealEditor-Cmd,blender -ErrorAction SilentlyContinue).Count'], text=True)
    if int(count.strip()):
        raise RuntimeError('Affected editor is running')
    return subprocess.check_output([ps, '-NoProfile', '-Command',
        "(Get-Acl -LiteralPath '" + str(SHARE) + "').Sddl"], text=True).strip()

def publish():
    root_acl = idle_and_acl()
    if (OUT / 'started.json').exists():
        raise RuntimeError('Occupied publication identity; inspect state before recovery')
    audit = read(OUT / 'dependency-audit-v2.json')
    assert audit['status'] == 'pass_required_closure_with_vendor_soft_gaps' and audit['guarded_bytes_unchanged'] and not audit['hard_missing_packages']
    known_vendor_gaps = {
        '/Game/Library_Meshingun/ToolsCollection_Meshingun/MaterialCustomizer_Meshingun/Blueprint/BP_Customizable',
        '/Game/Library_Meshingun/ToolsCollection_Meshingun/MaterialCustomizer_Meshingun/Blueprint/BP_Customizable_Pawn',
        '/Game/WW2City/CarsSet/Mesh/Car_2_Rig/ABP_Car_02',
        '/Game/WW2City/Library_Meshingun/ToolsCollection_Meshingun/RopeCatenaryGenerator_Meshingun/Asset/Texture/T_TintMask_02_TM',
        '/Game/WorldProceduralToolkit/Blueprints/Library/BPL_DebugLib'}
    assert set(audit['missing_packages']) == known_vendor_gaps, 'New unknown missing reference'
    assert all(p.startswith('/Game/WW2City/') for refs in audit['missing_referencers'].values() for p in refs)
    unexpected = [p for p in audit['external_dependencies'] if not p.startswith(('/Engine/', '/Script/', '/ACLPlugin/', '/Niagara/', '/MeshModelingToolsetExp/'))]
    assert not unexpected, 'Unknown engine/plugin dependencies'
    inventory = read(ROOT / 'Assets/Integration/CITY_CONTINUOUS_ARMS_NATIVE_INVENTORY_20261003.json')
    for e in inventory['files']:
        verify(ROOT / e['path'], e)
    catalog = read(ROOT / 'Assets/Sync/CATALOG.json')
    city = read(ROOT / 'Assets/Sync/manifests/france-liberation-content.json')
    city_by_path = {f['path']: f for f in city['files']}
    active_paths = set()
    for selection in catalog['active_manifests']:
        manifest = read(ROOT / selection['path'])
        active_paths.update(f['path'] for f in manifest['files'])
    files = []
    for e in audit['files']:
        verify(ROOT / e['path'], e)
        if e['path'] in city_by_path:
            assert e['sha256'] == city_by_path[e['path']]['sha256'], 'City baseline differs'
            continue
        assert e['path'] not in active_paths, 'Conflicting active restore owner'
        assert not any(x in e['package'] for x in ('FirstPersonViewV1', 'FirstPersonViewV2', 'WeaponAimingV4', 'WeaponGrip')), 'Rejected trial reachable'
        assert e['path'].startswith('Unreal/ParisStreetCombat/Content/')
        files.append({**e, 'storage': 'sftp', 'remote_path': f"/objects/sha256/{e['sha256'][:2]}/{e['sha256']}"})
    assert files and not any(x['asset_id'] == AID for x in catalog['active_manifests'])
    assert not (SHARE / 'releases' / RUN).exists()
    write(OUT / 'started.json', {'status': 'uploading', 'release': RUN, 'root_acl_sha256': hashlib.sha256(root_acl.encode()).hexdigest()})
    commands = [f'mkdir "/incoming/{RUN}"']
    prefixes, downloads, uploaded, reused = set(), {}, [], []
    for e in files:
        h = e['sha256']
        if h in downloads:
            continue
        final = SHARE / e['remote_path'].lstrip('/')
        if final.exists():
            # Final bytes are authenticated and rehashed after the batch below.
            reused.append(h)
        else:
            if h[:2] not in prefixes and not final.parent.exists():
                commands.append(f'mkdir "/objects/sha256/{h[:2]}"')
            prefixes.add(h[:2])
            stage = f'/incoming/{RUN}/{h}.part'
            commands += [f'put "{(ROOT / e["path"]).as_posix()}" "{stage}"', f'rename "{stage}" "{e["remote_path"]}"']
            uploaded.append(h)
        dest = OUT / 'verified-downloads' / h
        dest.parent.mkdir(parents=True, exist_ok=True)
        downloads[h] = (dest, e)
        commands.append(f'get "{e["remote_path"]}" "{dest.as_posix()}"')
    commands.append(f'rmdir "/incoming/{RUN}"')
    batch(commands, 'objects')
    for dest, e in downloads.values():
        verify(dest, e)
        verify(ROOT / e['path'], e)
    now = datetime.now().astimezone().isoformat()
    manifest = {'schema_version': 1, 'asset_id': AID, 'asset_version': RUN,
        'owner': 'Yupu Guo', 'published_at': now, 'engine': audit['engine'],
        'source': 'Saved Paris gameplay and its hard/soft native package dependency closure, excluding already selected WW2City bytes',
        'license_record': 'Assets/Sync/RIGHTS.md',
        'sharing_status': 'owner_attested_private_three_member_original_and_derivative_sharing',
        'recipients': ['Yupu Guo', 'Yuqi Pu', 'Jingdi Wu'],
        'scope': 'Private editor-backed native playtest; not packaged executable, final motion/FPS/history/MVP acceptance',
        'entry': audit['entry'], 'runtime_plugins': ['UE5.8.2 bundled ACLPlugin, Niagara and MeshModelingToolsetExp; no downloaded plugin'],
        'runtime_python_required': False, 'runtime_editor_bridge_required': False,
        'dependencies': ['france-liberation-content'], 'retired_paths': [],
        'verification': {'method': 'All final immutable objects downloaded via authenticated pinned-host SFTP and SHA-256/size checked before Catalog selection',
                         'dependency_audit': 'No missing hard dependencies; all existing hard/soft dependencies selected; five unchanged supplier soft gaps recorded; all 43 native guards unchanged',
                         'second_machine_test': 'Assigned to teammates; not performed'},
        'known_vendor_soft_reference_gaps': audit['missing_referencers'],
        'files': files, 'file_count': len(files), 'size_bytes': sum(e['size_bytes'] for e in files)}
    local = OUT / (AID + '.json')
    write(local, manifest)
    downloaded_manifest = OUT / 'verified-manifest.json'
    remote_manifest = f'/releases/{RUN}/{AID}.json'
    batch([f'mkdir "/releases/{RUN}"', f'put "{local.as_posix()}" "{remote_manifest}"',
           f'get "{remote_manifest}" "{downloaded_manifest.as_posix()}"'], 'manifest')
    verify(downloaded_manifest, {'sha256': sha(local), 'size_bytes': local.stat().st_size})
    # Exercise shared-account CRUD only in this new release's unique probe.
    probe = OUT / 'crud-probe.txt'
    probe.write_text('Team native playtest shared CRUD probe\n', encoding='utf-8')
    remote_probe = f'/releases/{RUN}/_crud_probe'
    returned = OUT / 'crud-returned.txt'
    batch([f'mkdir "{remote_probe}"', f'put "{probe.as_posix()}" "{remote_probe}/probe.txt"',
           f'put "{probe.as_posix()}" "{remote_probe}/probe.txt"',
           f'rename "{remote_probe}/probe.txt" "{remote_probe}/renamed.txt"',
           f'get "{remote_probe}/renamed.txt" "{returned.as_posix()}"',
           f'rm "{remote_probe}/renamed.txt"', f'rmdir "{remote_probe}"'], 'crud')
    verify(returned, {'sha256': sha(probe), 'size_bytes': probe.stat().st_size})
    assert idle_and_acl() == root_acl, 'Protected root ACL changed'
    for e in inventory['files']:
        verify(ROOT / e['path'], e)
    write(OUT / 'publication.json', {'status': 'verified_pending_adoption', 'release': RUN,
        'asset_id': AID, 'file_count': len(files), 'size_bytes': manifest['size_bytes'],
        'uploaded_unique_objects': len(uploaded), 'uploaded_bytes': sum(downloads[h][1]['size_bytes'] for h in uploaded),
        'reused_unique_objects': len(reused), 'sftp_verified_unique_objects': len(downloads),
        'manifest_sha256': sha(local), 'root_acl_unchanged': True,
        'shared_account_crud': 'create/overwrite/rename/read/delete verified; exact probes removed',
        'external_connectivity': 'not retested', 'teammate_test': 'delegated to teammates; not performed',
        'verified_at': now})
    print(json.dumps(read(OUT / 'publication.json')))

def adopt():
    status = read(OUT / 'publication.json')
    assert status['status'] == 'verified_pending_adoption'
    source = OUT / (AID + '.json')
    assert sha(source) == status['manifest_sha256']
    dest = ROOT / 'Assets/Sync/manifests' / source.name
    assert not dest.exists(), 'Do not overwrite selected manifest'
    shutil.copyfile(source, dest)
    manifest = read(dest)
    catalog = read(ROOT / 'Assets/Sync/CATALOG.json')
    assert not any(e['asset_id'] == AID for e in catalog['active_manifests'])
    catalog['active_manifests'].append({'asset_id': AID, 'asset_version': RUN,
        'path': dest.relative_to(ROOT).as_posix(), 'sha256': sha(dest),
        'file_count': manifest['file_count'], 'size_bytes': manifest['size_bytes'],
        'release_manifest': f'/releases/{RUN}/{AID}.json'})
    catalog['updated_at'] = datetime.now().astimezone().isoformat()
    write(ROOT / 'Assets/Sync/CATALOG.json', catalog)
    write(ROOT / 'Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json',
          {**status, 'status': 'verified_private_sftp_catalog_selected',
           'git_publication': 'pending commit/push', 'source_runtime_test': 'CONTINUOUS_ARMS_NATIVE_RESULT_20261003.md'})
    # These authenticated download samples are disposable, not a second asset
    # workspace. Remove exact verified task files only; retain reports/logs.
    for e in manifest['files']:
        sample = OUT / 'verified-downloads' / e['sha256']
        if sample.exists():
            verify(sample, e)
            sample.unlink()
    print('Catalog adopted verified private native playtest')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('publish', 'adopt'))
    globals()[parser.parse_args().mode]()
