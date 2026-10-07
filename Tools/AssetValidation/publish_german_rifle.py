"""Bounded accepted static-model publication; no game, refinement or Git writes.

prepare generates a dated relocation plan. PowerShell performs validated moves.
upload verifies workspace bytes, pinned-host SFTP objects/manifest and CRUD.
Catalog/source adoption is deliberately performed separately with apply_patch.
Never rerun an occupied identity; inspect its private journal before recovery.
"""
import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AID = 'german-rifle-model'
RUN = 'german-rifle-model-20261004-v1'
OUT = ROOT / 'tmp' / RUN
SHARE = ROOT / 'Assets/LocalShared/SFTP'
WORK = SHARE / 'workspaces/yg745/german-rifle-model-v1'
PRIVATE = ROOT / 'Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-fine-texture-v15'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def verify(path, entry):
    assert path.is_file() and path.stat().st_size == entry['size_bytes'] and sha(path) == entry['sha256'], str(path)


def batch(commands, label):
    key = Path(os.environ['USERPROFILE']) / '.ssh/cs549_sftp_ed25519'
    hosts = Path(os.environ['USERPROFILE']) / '.ssh/known_hosts_cs549'
    result = subprocess.run(['sftp', '-b', '-', '-P', '22222', '-i', str(key),
        '-o', 'UserKnownHostsFile=' + str(hosts), '-o', 'StrictHostKeyChecking=yes',
        '-o', 'IdentitiesOnly=yes', 'cs549sftp@127.0.0.1'],
        input='\n'.join(commands) + '\n', text=True, capture_output=True)
    (OUT / (label + '.log')).write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('SFTP failed; inspect private ' + label + '.log; no automatic retry')


def prepare():
    assert not (OUT / 'relocation-plan.json').exists(), 'Occupied plan'
    assert not WORK.exists() and not (SHARE / 'releases' / RUN).exists(), 'Occupied destination'
    assert read(OUT / 'closure_v2.json')['passed'], 'Closure gate'
    for name in ['audit_v1/audit.json', 'material_audit_v1/material_audit.json', 'repeat_audit_v1/audit.json']:
        assert read(PRIVATE / name)['passed'], name
    repeat = read(PRIVATE / 'repeat_audit_v1/audit.json')
    assert repeat['cross_export_images_identical']
    assert 'MW2_Guns_Asset_Library may be used' in (ROOT / 'Assets/Sync/RIGHTS.md').read_text(encoding='utf-8')
    original = read(ROOT / 'Assets/Integration/GERMAN_RIFLE_FINE_TEXTURE_V15_INVENTORY_20261004.json')
    known = {entry['path']: entry for entry in original['private_files']}
    mappings = [
        ('finish_v1/GermanRifle_FineWood_V15.blend', 'Model/GermanRifle_FineWood_V15.blend'),
        ('finish_v1/GermanRifle_FineWood_V15.glb', 'Model/GermanRifle_FineWood_V15.glb')]
    mappings += [(f'finish_v1/{name}.png', f'Evidence/{name}.png') for name in
                 ['pbr_quarter', 'pbr_stock', 'pbr_stock_reverse', 'pbr_handguard']]
    mappings += [(f'material_audit_v1/{name}.png', f'Evidence/{name}.png') for name in ['fresh_stock', 'fresh_handguard']]
    mappings += [(f'presentation_v1/{name}.png', f'Evidence/{name}.png') for name in ['m1_v14_v15', 'v14_v15_stock_native']]
    mappings += [('finish_v1/build_report.json', 'Evidence/build_report.json'),
                 ('audit_v1/audit.json', 'Evidence/geometry_audit.json'),
                 ('material_audit_v1/material_audit.json', 'Evidence/material_audit.json'),
                 ('repeat_audit_v1/audit.json', 'Evidence/repeat_audit.json')]
    files = []
    for src, dest in mappings:
        source = PRIVATE / src
        record = known[source.relative_to(ROOT).as_posix()]
        entry = {'source': source.relative_to(ROOT).as_posix(), 'bundle_path': dest,
                 'path': (WORK / dest).relative_to(ROOT).as_posix(), 'operation': 'move',
                 'size_bytes': record['bytes'], 'sha256': record['sha256']}
        verify(source, entry)
        files.append(entry)
    for source, dest in [(OUT / 'closure_v2.json', 'Evidence/closure.json'),
                         (ROOT / 'Assets/GERMAN_RIFLE_MODEL.md', 'README.md')]:
        files.append({'source': source.relative_to(ROOT).as_posix(), 'bundle_path': dest,
                      'path': (WORK / dest).relative_to(ROOT).as_posix(), 'operation': 'copy',
                      'size_bytes': source.stat().st_size, 'sha256': sha(source)})
    catalog = read(ROOT / 'Assets/Sync/CATALOG.json')
    assert not any(entry['asset_id'] == AID for entry in catalog['active_manifests'])
    occupied = set()
    old = {}
    for selection in catalog['active_manifests']:
        assert sha(ROOT / selection['path']) == selection['sha256']
        old[selection['path']] = selection['sha256']
        occupied.update(entry['path'] for entry in read(ROOT / selection['path'])['files'])
    assert not occupied.intersection(entry['path'] for entry in files)
    write(OUT / 'relocation-plan.json', {'asset_id': AID, 'asset_version': RUN,
          'workspace': WORK.relative_to(ROOT).as_posix(), 'files': files,
          'catalog_before_sha256': sha(ROOT / 'Assets/Sync/CATALOG.json'),
          'protected_manifests': old, 'source_private_root': PRIVATE.relative_to(ROOT).as_posix()})
    print(json.dumps({'planned_files': len(files), 'size_bytes': sum(entry['size_bytes'] for entry in files)}))


def upload():
    assert not (OUT / 'upload-started.json').exists(), 'Occupied upload; inspect journal before recovery'
    plan = read(OUT / 'relocation-plan.json')
    moved = read(OUT / 'relocation.json')
    assert moved['status'] == 'workspace_verified_shared_modify' and moved['root_acl_unchanged']
    assert sha(ROOT / 'Assets/Sync/CATALOG.json') == plan['catalog_before_sha256']
    assert not (SHARE / 'releases' / RUN).exists(), 'Release occupied'
    for entry in plan['files']:
        verify(ROOT / entry['path'], entry)
    write(OUT / 'upload-started.json', {'status': 'uploading', 'run_id': RUN})
    stage_root = f'/incoming/{RUN}'
    commands = [f'mkdir "{stage_root}"']
    uploaded, reused, dirs, unique = [], [], set(), {}
    files = []
    for entry in plan['files']:
        digest = entry['sha256']
        remote = f'/objects/sha256/{digest[:2]}/{digest}'
        files.append({key: entry[key] for key in ['path', 'size_bytes', 'sha256']} | {'storage': 'sftp', 'remote_path': remote})
        if digest in unique:
            continue
        dest = OUT / 'verified-downloads' / digest
        dest.parent.mkdir(parents=True, exist_ok=True)
        unique[digest] = (dest, entry)
        final = SHARE / remote.lstrip('/')
        if final.exists():
            verify(final, entry)
            reused.append(digest)
        else:
            prefix = digest[:2]
            if prefix not in dirs and not final.parent.exists():
                commands.append(f'mkdir "/objects/sha256/{prefix}"')
            dirs.add(prefix)
            stage = stage_root + '/' + digest + '.part'
            commands += [f'put "{(ROOT / entry["path"]).as_posix()}" "{stage}"', f'rename "{stage}" "{remote}"']
            uploaded.append(digest)
        commands.append(f'get "{remote}" "{dest.as_posix()}"')
    commands.append(f'rmdir "{stage_root}"')
    batch(commands, 'objects')
    for dest, entry in unique.values():
        verify(dest, entry)
        verify(ROOT / entry['path'], entry)
    now = datetime.now().astimezone().isoformat()
    manifest = {'schema_version': 1, 'asset_id': AID, 'asset_version': RUN, 'owner': 'Yupu Guo', 'published_at': now,
        'source': 'Accepted V15 static modeling derivative: bounded privately acquired MW2 SP-R components, team wood/furniture/sights, permitted Allied M1 texture detail',
        'license_record': 'Assets/Sync/RIGHTS.md#german-rifle-model-mw2-derived',
        'sharing_status': 'owner_attested_private_three_member_project_use_and_derivative_sharing',
        'recipients': ['Yupu Guo', 'Yuqi Pu', 'Jingdi Wu'], 'dependencies': [], 'retired_paths': [],
        'blender': '5.2.2 LTS d13f752e3b9c', 'formats': ['packed blend', 'embedded glTF 2 GLB'],
        'scope': 'User-accepted static modeling baseline, not a native UE release or complete animated weapon kit',
        'user_modeling_approved': True, 'ue_runtime_accepted': False, 'public_asset_redistribution_allowed': False,
        'entry': {suffix: (WORK / ('Model/GermanRifle_FineWood_V15.' + suffix)).relative_to(ROOT).as_posix() for suffix in ['blend', 'glb']},
        'metrics': {'meshes': 24, 'triangles': 24466, 'materials': 14, 'primitives': 30, 'embedded_images': 36,
                    'dimensions_m': [1.107303977, .079198018, .183007009]},
        'remaining_checks': ['historical weapon variant and donor differences', 'complete mechanical rig and weapon actions',
                             'UE5.8.2 import/material/mips/shimmer', 'hand contact/collision/game integration/FPS', 'teammate restoration'],
        'verification': {'method': 'Every final immutable object downloaded via authenticated pinned-host SFTP, SHA-256 and size matched; packed blend/embedded GLB closure verified',
                         'verified_at': now, 'teammate_restore': 'not performed', 'external_forwarding': 'not retested'},
        'files': files, 'file_count': len(files), 'size_bytes': sum(entry['size_bytes'] for entry in files)}
    local = OUT / (AID + '.json')
    assert not local.exists()
    write(local, manifest)
    remote_manifest = f'/releases/{RUN}/{AID}.json'
    returned = OUT / 'verified-manifest.json'
    batch([f'mkdir "/releases/{RUN}"', f'put "{local.as_posix()}" "{remote_manifest}"',
           f'get "{remote_manifest}" "{returned.as_posix()}"'], 'manifest')
    verify(returned, {'size_bytes': local.stat().st_size, 'sha256': sha(local)})
    # Scoped actual shared-account CRUD: probe bytes use the nonsecret source README.
    probe = f'/workspaces/yg745/german-rifle-model-v1/_crud_{RUN}'
    probe_returned = OUT / 'crud-returned.md'
    guide = next(entry for entry in plan['files'] if entry['bundle_path'] == 'README.md')
    batch([f'mkdir "{probe}"', f'put "{(ROOT / guide["path"]).as_posix()}" "{probe}/probe.md"',
           f'put "{(ROOT / guide["path"]).as_posix()}" "{probe}/probe.md"',
           f'rename "{probe}/probe.md" "{probe}/renamed.md"', f'get "{probe}/renamed.md" "{probe_returned.as_posix()}"',
           f'rm "{probe}/renamed.md"', f'rmdir "{probe}"'], 'workspace-crud')
    verify(probe_returned, guide)
    for path, digest in plan['protected_manifests'].items():
        assert sha(ROOT / path) == digest, 'Previous manifest changed'
    receipt = {'status': 'verified_pending_catalog_adoption', 'asset_id': AID, 'asset_version': RUN,
        'file_count': len(files), 'size_bytes': manifest['size_bytes'], 'uploaded_unique_objects': len(uploaded),
        'reused_unique_objects': len(reused), 'verified_sftp_downloads': len(unique),
        'manifest_sha256': sha(local), 'manifest_size_bytes': local.stat().st_size,
        'shared_account_crud': 'create/overwrite/rename/read/delete passed; only own probe removed',
        'root_acl_unchanged': True, 'git_publication': 'not committed/pushed', 'verified_at': now}
    write(OUT / 'publication.json', receipt)
    print(json.dumps(receipt))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'upload'])
    args = parser.parse_args()
    {'prepare': prepare, 'upload': upload}[args.command]()
