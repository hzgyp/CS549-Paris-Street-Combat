"""Prepare/adopt the explicitly authorized, dated character SFTP publication.

Generated JSON is metadata, not model bytes. The administrator publisher must
verify final server bytes before adoption can update the active catalog.
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = 'character-20261001-v1'
OUT = ROOT / 'tmp' / RUN
INTAKE = 'Assets/LocalShared/SFTP/workspaces/yg745/character-intake-20260930'
LAB = 'Assets/LocalShared/SFTP/workspaces/yg745/character-ue582-v1'
BASELINE = f'/baselines/character-original-intake/{RUN}'
IDS = {'CHAR-G-GermanSoldierWWII': 'german-soldier-original',
       'CHAR-A-USSoldier': 'us-paratrooper-original',
       'ANI-TP-RifleAnimsetPro': 'rifle-animset-pro-original'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def checked(entry):
    p = (ROOT / entry['source_path']).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file():
        raise ValueError(f'Invalid source: {p}')
    if p.stat().st_size != entry['size_bytes'] or digest(p) != entry['sha256']:
        raise ValueError(f'Changed source: {p}')
    return entry


def plan():
    rights = ROOT / 'Assets/Sync/RIGHTS.md'
    if 'On 1 October 2026, Yupu Guo explicitly answered' not in rights.read_text(encoding='utf-8'):
        raise ValueError('Owner sharing attestation is required')
    original = read(ROOT / 'tmp/asset-intake-review/intake_static_inventory.json')
    handoff = read(ROOT / LAB / 'Evidence/Repair20261001/repair_handoff.json')
    assert handoff['file_count'] == 719 and not handoff['changed_originals']
    groups = []
    for asset in original['assets']:
        aid = IDS[asset['asset_id']]
        files = []
        for f in asset['files']:
            remote = f"{BASELINE}/{asset['asset_id']}/{f['path']}"
            files.append(checked({'source_path': f"{INTAKE}/{asset['asset_id']}/{f['path']}",
                'path': 'Assets/LocalShared/SFTP' + remote, 'remote_path': remote,
                'size_bytes': f['size_bytes'], 'sha256': f['sha256']}))
        groups.append({'asset_id': aid, 'source': f"Unchanged delivered {asset['asset_id']} intake",
            'dependencies': ([{'asset_id': 'us-paratrooper-original', 'asset_version': RUN}]
                             if aid == 'german-soldier-original' else []), 'files': files})
    files = []
    for f in handoff['files']:
        files.append(checked({'source_path': f['path'], 'path': f['path'],
            'remote_path': f"/objects/sha256/{f['sha256'][:2]}/{f['sha256']}",
            'size_bytes': f['size_bytes'], 'sha256': f['sha256']}))
    for name in ('AssetCompatibilityLab.uproject', 'Config/DefaultEngine.ini'):
        path = f'{LAB}/{name}'
        p = ROOT / path
        # Never publish engine-generated Android file-server credentials.
        if 'SecurityToken=' in p.read_text(encoding='utf-8-sig'):
            raise ValueError('Remove network security tokens before publication')
        sha = digest(p)
        files.append(checked({'source_path': path, 'path': path,
            'remote_path': f'/objects/sha256/{sha[:2]}/{sha}',
            'size_bytes': p.stat().st_size, 'sha256': sha}))
    groups.append({'asset_id': 'character-ue582-integration-baseline',
        'source': '540 UE 5.8.2 native packages; 148 source textures; 19 FBX, 12 Blender sources; lab descriptor/config',
        'dependencies': [{'asset_id': aid, 'asset_version': RUN} for aid in IDS.values()],
        'files': files})
    value = {'run_id': RUN, 'rights_sha256': digest(rights), 'intake_source': INTAKE,
        'intake_remote': BASELINE, 'groups': groups,
        'file_count': sum(len(g['files']) for g in groups)}
    write(OUT / 'plan.json', value)
    print(json.dumps({'plan': str(OUT / 'plan.json'), 'files': value['file_count'],
        'groups': [{'id': g['asset_id'], 'files': len(g['files'])} for g in groups]}))


def adopt():
    result = read(OUT / 'publication-result.json')
    if result['status'] != 'complete' or result['run_id'] != RUN:
        raise ValueError('Only fully verified publication can enter the catalog')
    client = read(OUT / 'client-verification.json')
    if client['status'] != 'complete' or client['manifest_downloads'] != 4 or client['asset_samples'] != 4:
        raise ValueError('Actual SFTP release access verification is required')
    catalog_path = ROOT / 'Assets/Sync/CATALOG.json'
    catalog = read(catalog_path)
    entries = []
    for release in result['releases']:
        src = OUT / 'verified-manifests' / (release['asset_id'] + '.json')
        if digest(src) != release['manifest_sha256']:
            raise ValueError('Verified manifest changed')
        dst = ROOT / 'Assets/Sync/manifests' / src.name
        if dst.exists() and digest(dst) != digest(src):
            raise ValueError('Existing active manifest differs; inspect before replacement')
        shutil.copyfile(src, dst)
        entries.append({'asset_id': release['asset_id'], 'asset_version': RUN,
            'path': dst.relative_to(ROOT).as_posix(), 'sha256': digest(dst),
            'file_count': release['file_count'], 'size_bytes': release['size_bytes'],
            'release_manifest': release['release_manifest']})
    ids = {r['asset_id'] for r in entries}
    catalog['active_manifests'] = [r for r in catalog['active_manifests'] if r['asset_id'] not in ids] + entries
    catalog['updated_at'] = result['completed_at']
    write(catalog_path, catalog)
    write(ROOT / 'Assets/Sync/CHARACTER_PUBLICATION_STATUS.json', {
        'schema_version': 1, 'run_id': RUN, 'status': 'verified_private_sftp_publication',
        'completed_at': result['completed_at'], 'owner': 'Yupu Guo',
        'original_files': 590, 'repair_files': 721, 'releases': entries,
        'original_relocation': 'Moved to immutable baseline; old intake paths are junction aliases, not copies',
        'root_acl_unchanged': result['root_acl_unchanged'],
        'shared_permissions': 'shared-account Modify (read/create/change/delete); immutability is procedural',
        'repair_workspace_crud': client.get('repair_workspace_crud', 'not tested'),
        'method': 'Authorized administrator compared live source and final server SHA-256/size for every file',
        'sftp_client_verification': client,
        'teammate_restoration': 'not performed', 'external_connectivity': 'not retested',
        'gameplay_integration': 'not started',
        'runtime_limits': 'Lab regressions only; final Paris lighting, gun contact, history, physics, LOD/performance and packaging pending'})
    print(json.dumps({'adopted': len(entries), 'files': sum(r['file_count'] for r in entries)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['plan', 'adopt'])
    args = parser.parse_args()
    plan() if args.mode == 'plan' else adopt()
