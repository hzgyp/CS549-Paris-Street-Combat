"""Publish existing saved native bytes after a read-only unified closure audit.

No engine entry, package save, Git command or license inference is performed.
Publication requires an explicit recorded team-sharing attestation for new VFX.
"""
import argparse
import copy
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/team-sync-20261008-v1'
RELEASE = 'paris-native-playtest-20261008-g1-npc-vfx-v1'
AID = 'paris-gameplay-native-playtest'
DEST = ROOT / 'Assets/Sync/manifests/paris-gameplay-native-playtest.json'
sys.path.insert(0, str(ROOT / 'Tools/Integration/NPCInteractionV1'))
from common import guard_rows, guards_match, digest, STORE

spec = importlib.util.spec_from_file_location('team_sync_transport', ROOT / 'Tools/Integration/publish_native_playtest.py')
transport = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transport)
transport.OUT = OUT
read, sha, verify = transport.read, digest, transport.verify


def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def row(p):
    return {'path': p.relative_to(ROOT).as_posix(), 'size_bytes': p.stat().st_size, 'sha256': sha(p)}


def unchanged(rows):
    for f in rows:
        verify(ROOT / f['path'], f)


def prepare():
    assert not OUT.exists(), 'Preserve occupied release identity'
    acl = transport.idle_and_acl()
    guards = guard_rows()
    assert len(guards) == 703 and guards_match(guards)
    g1 = read(STORE / 'Evidence/G1MissionV1/closure_v1_20261008/result.json')
    assert g1['status'] == 'pass_bounded_local_functional_checks'
    unchanged(g1['selected_owned_files'])
    for proof in g1['proofs']:
        verify(ROOT / proof['audit']['path'], proof['audit'])
    runtime = read(ROOT / g1['runtime_manifest']['path'])
    unchanged(runtime['files'])
    installed = read(STORE / 'Evidence/MuzzleFlashV1/install_local_v1_20261008/result.json')
    # Installation's original unpassed-runtime flag remains historical. The
    # later independent Formal audit supplies completion, never a rewritten flag.
    formal = read(STORE / 'Evidence/MuzzleFlashV1/formal_transactions_v1_20261008/audit.json')
    assert formal['status'].startswith('pass'), 'Latest formal muzzle audit required'
    frozen = {'release': RELEASE, 'base_git': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'guards': guards + g1['selected_owned_files'] + runtime['files'],
        'previous_manifest_sha256': sha(DEST),
        'catalog_sha256': sha(ROOT / 'Assets/Sync/CATALOG.json'),
        'root_acl_sha256': __import__('hashlib').sha256(acl.encode()).hexdigest(),
        'muzzle_formal': row(STORE / 'Evidence/MuzzleFlashV1/formal_transactions_v1_20261008/audit.json'),
        'g1_closure': row(STORE / 'Evidence/G1MissionV1/closure_v1_20261008/result.json')}
    write(OUT / 'frozen.json', frozen)
    print('Frozen current protected epoch, G1 admission and latest muzzle proof')


def candidate():
    transport.idle_and_acl()
    frozen = read(OUT / 'frozen.json')
    unchanged(frozen['guards'])
    audit = read(OUT / 'dependency-audit.json')
    assert audit['status'] == 'pass_readonly_dependency_closure' and not audit['errors']
    old = read(DEST)
    assert sha(DEST) == frozen['previous_manifest_sha256']
    assert audit['missing_referencers'] == old['known_vendor_soft_reference_gaps']
    assert all(p.startswith(('/Engine/', '/Script/', '/ACLPlugin/', '/Niagara/',
        '/MeshModelingToolsetExp/', '/InterchangeAssets/')) for p in audit['external_dependencies']), 'Unknown external plugin mount'
    city = {f['path']: f for f in read(ROOT / 'Assets/Sync/manifests/france-liberation-content.json')['files']}
    files = []
    for f in audit['files']:
        verify(ROOT / f['path'], f)
        if f['path'] in city:
            assert all(f[k] == city[f['path']][k] for k in ('size_bytes', 'sha256')), 'Changed city baseline'
            continue
        files.append(f)
    # Dynamically loaded profile was an audit root. Native editor modules are
    # file dependencies, not /Game registry packages; include each current one.
    binaries = ROOT / 'Unreal/ParisStreetCombat/Plugins'
    for plugin in ('ParisGripBindingV18', 'ParisNPCGripV15', 'ParisBridgeMissionV1', 'ParisMuzzleFlashV1'):
        folder = binaries / plugin / 'Binaries/Win64'
        modules = read(folder / 'UnrealEditor.modules')
        engine_modules = read(Path('C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.modules'))
        assert modules['BuildId'] == engine_modules['BuildId'], 'Editor ABI mismatch'
        files.append(row(folder / 'UnrealEditor.modules'))
        for name in modules['Modules'].values():
            files.append(row(folder / name))
    assert len({f['path'] for f in files}) == len(files)
    old_by = {f['path']: f for f in old['files']}
    new_by = {f['path']: f for f in files}
    assert set(old_by) <= set(new_by), 'Existing approved closure unexpectedly retired'
    manifest = copy.deepcopy(old)
    manifest.update(asset_version=RELEASE, published_at=datetime.now().astimezone().isoformat(),
        source='Current saved formal Paris and G1 mission, original selected models/grips, native NPC combat, recoil and muzzle presentation',
        scope='Private UE5.8.2 editor-backed team restore; second-machine runtime verification assigned to teammates',
        entry='/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1',
        entries={'g1': '/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1',
                 'formal': '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'},
        files=[{**f, 'storage': 'sftp', 'remote_path': '/objects/sha256/' + f['sha256'][:2] + '/' + f['sha256']}
               for f in sorted(files, key=lambda f: f['path'])],
        verification={'method': 'Authenticated pinned-host final immutable object and manifest readback; size/SHA-256 verified before Catalog selection',
            'dependency_audit': 'Read-only two-map plus dynamic-profile registry closure; unchanged five vendor soft gaps; no missing hard package',
            'second_machine_test': 'Assigned to teammates; not performed by publisher', 'shipping_build': 'not built'})
    manifest['runtime_plugins'] = list(old['runtime_plugins']) + [
        'ParisBridgeMissionV1 native G1/save runtime; enable with G1 launcher',
        'ParisMuzzleFlashV1 native presentation; enabled by matching Git descriptor']
    manifest['file_count'] = len(files)
    manifest['size_bytes'] = sum(f['size_bytes'] for f in files)
    source_contract = ROOT / 'Assets/Sync/TEAM_SOURCE_CONTRACT_20261008.json'
    manifest['source_contract'] = {'path': source_contract.relative_to(ROOT).as_posix(),
                                   'sha256': sha(source_contract)}
    manifest['current_functional_results'] = [
        'Docs/Development/MissionLoopV1/G1_MIDTERM_RESULT_20261008.md',
        'Docs/Development/NPCInteractionV1/NPC_FORMAL_COMBAT_RESULT_20261007.md',
        'Docs/Development/RecoilV1/RECOIL_RESULT_20261007.md',
        'Docs/Development/MuzzleFlashV1/MUZZLE_FLASH_FORMAL_RESULT_20261008.md']
    write(OUT / (AID + '.json'), manifest)
    changes = {'added': sorted(set(new_by) - set(old_by)),
               'changed': sorted(p for p in old_by if old_by[p]['sha256'] != new_by[p]['sha256']),
               'unchanged': sum(old_by[p]['sha256'] == new_by[p]['sha256'] for p in old_by)}
    write(OUT / 'changes.json', changes)
    print(json.dumps({'files': len(files), 'bytes': manifest['size_bytes'],
                      'added': len(changes['added']), 'changed': len(changes['changed']), 'unchanged': changes['unchanged']}))


def publish():
    assert not (OUT / 'started.json').exists(), 'Preserve occupied transfer'
    assert 'MsvFx_MuzzleFlash_Pack' in (ROOT / 'Assets/Sync/RIGHTS.md').read_text(), 'Record explicit VFX team-sharing attestation first'
    frozen = read(OUT / 'frozen.json')
    unchanged(frozen['guards'])
    acl = transport.idle_and_acl()
    assert __import__('hashlib').sha256(acl.encode()).hexdigest() == frozen['root_acl_sha256']
    manifest_file = OUT / (AID + '.json')
    manifest = read(manifest_file)
    unchanged(manifest['files'])
    assert not (transport.SHARE / 'releases' / RELEASE).exists(), 'Preserve immutable release'
    assert sha(DEST) == frozen['previous_manifest_sha256']
    write(OUT / 'started.json', {'release': RELEASE, 'manifest_sha256': sha(manifest_file)})
    commands = [f'mkdir "/incoming/{RELEASE}"']
    prefixes, downloads, uploaded, reused = set(), {}, [], []
    for f in manifest['files']:
        h = f['sha256']
        if h in downloads:
            continue
        final = transport.SHARE / f['remote_path'].lstrip('/')
        if final.exists():
            reused.append(h)
        else:
            if h[:2] not in prefixes and not final.parent.exists():
                commands.append(f'mkdir "/objects/sha256/{h[:2]}"')
            prefixes.add(h[:2])
            stage = f'/incoming/{RELEASE}/{h}.part'
            commands.extend([f'put "{(ROOT / f["path"]).as_posix()}" "{stage}"',
                             f'rename "{stage}" "{f["remote_path"]}"'])
            uploaded.append(h)
        dest = OUT / 'verified-downloads' / h
        dest.parent.mkdir(parents=True, exist_ok=True)
        downloads[h] = (dest, f)
        commands.append(f'get "{f["remote_path"]}" "{dest.as_posix()}"')
    commands.append(f'rmdir "/incoming/{RELEASE}"')
    transport.batch(commands, 'objects')
    for dest, f in downloads.values():
        verify(dest, f)
    unchanged(manifest['files'])
    remote = f'/releases/{RELEASE}/{AID}.json'
    returned = OUT / 'verified-manifest.json'
    transport.batch([f'mkdir "/releases/{RELEASE}"', f'put "{manifest_file.as_posix()}" "{remote}"',
                     f'get "{remote}" "{returned.as_posix()}"'], 'manifest')
    verify(returned, row(manifest_file))
    probe = OUT / 'crud.txt'
    probe.write_text('Unified team release private CRUD probe\n', encoding='utf-8')
    remoteprobe = f'/releases/{RELEASE}/_crud_probe'
    returned = OUT / 'crud-returned.txt'
    transport.batch([f'mkdir "{remoteprobe}"', f'put "{probe.as_posix()}" "{remoteprobe}/probe.txt"',
        f'put "{probe.as_posix()}" "{remoteprobe}/probe.txt"',
        f'rename "{remoteprobe}/probe.txt" "{remoteprobe}/renamed.txt"',
        f'get "{remoteprobe}/renamed.txt" "{returned.as_posix()}"',
        f'rm "{remoteprobe}/renamed.txt"', f'rmdir "{remoteprobe}"'], 'crud')
    verify(returned, row(probe))
    assert transport.idle_and_acl() == acl, 'Root ACL drift'
    unchanged(frozen['guards'])
    status = {'status': 'verified_pending_catalog_selection', 'release': RELEASE, 'asset_id': AID,
        'manifest_sha256': sha(manifest_file), 'previous_manifest_sha256': frozen['previous_manifest_sha256'],
        'file_count': manifest['file_count'], 'size_bytes': manifest['size_bytes'],
        'uploaded_unique_objects': len(uploaded), 'uploaded_bytes': sum(downloads[h][1]['size_bytes'] for h in uploaded),
        'reused_unique_objects': len(reused), 'verified_unique_objects': len(downloads),
        'root_acl_unchanged': True, 'shared_account_crud': 'create/overwrite/rename/read/delete passed; probes removed',
        'verified_at': datetime.now().astimezone().isoformat(), 'teammate_test': 'not performed; assigned to teammates'}
    write(OUT / 'publication.json', status)
    print(json.dumps(status))


def adopt():
    status = read(OUT / 'publication.json')
    assert status['status'] == 'verified_pending_catalog_selection'
    assert sha(DEST) == status['previous_manifest_sha256']
    source = OUT / (AID + '.json')
    assert sha(source) == status['manifest_sha256']
    unchanged(read(source)['files'])
    catalog = read(ROOT / 'Assets/Sync/CATALOG.json')
    assert sha(ROOT / 'Assets/Sync/CATALOG.json') == read(OUT / 'frozen.json')['catalog_sha256']
    entry = next(e for e in catalog['active_manifests'] if e['asset_id'] == AID)
    entry.update(asset_version=RELEASE, sha256=sha(source), file_count=status['file_count'],
        size_bytes=status['size_bytes'], release_manifest=f'/releases/{RELEASE}/{AID}.json')
    # Exact manifest bytes are the contract. Never normalize after selection.
    DEST.write_bytes(source.read_bytes())
    catalog['updated_at'] = status['verified_at']
    write(ROOT / 'Assets/Sync/CATALOG.json', catalog)
    write(ROOT / 'Assets/Sync/NATIVE_PLAYTEST_PUBLICATION_STATUS.json', {**status,
        'status': 'verified_private_sftp_catalog_selected', 'git_publication': 'matching source pending commit/push',
        'teammate_guide': 'Docs/Development/TEAM_PLAYTEST_ZH.md'})
    original_catalog = next(f for f in read(OUT / 'frozen.json')['guards'] if f['path'] == 'Assets/Sync/CATALOG.json')
    write(ROOT / 'Docs/Development/TeamSyncV1/AUTHORIZED_CATALOG_20261008.json', {
        'authorization': '2026-10-08 user requests current source and assets synchronized for teammates; teammate runtime verification delegated',
        'release': RELEASE, 'original': original_catalog, 'current': row(ROOT / 'Assets/Sync/CATALOG.json'),
        'manifest_sha256': status['manifest_sha256'], 'only_catalog_guard_advances': True,
        'previous_guard_snapshots_unchanged': True})
    removed = 0
    for f in read(source)['files']:
        sample = OUT / 'verified-downloads' / f['sha256']
        if sample.exists():
            verify(sample, f)
            sample.unlink()
            removed += 1
    write(OUT / 'final.json', {**status, 'status': 'verified_private_sftp_catalog_selected',
                              'verified_disposable_samples_removed': removed})
    print('Selected exact verified native manifest; source publication remains')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('prepare', 'candidate', 'publish', 'adopt'))
    globals()[parser.parse_args().mode]()
