"""Adopt reviewed G1 bytes and retire only frozen local generated versions."""
import argparse
import hashlib
import json
import os
import shutil
import stat
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/g1-checkpoint-baseline-adoption-20261010'
PROOF = ROOT / 'Docs/Development/G1CheckpointBaselineAdoption20261010'
CURRENT = 'tmp/Playtest-G1-EnemyClear-candidate_v3-20261010'
AUTHOR = 'tmp/g1-enemy-clear-checkpoint-20261010/candidate_v3/Project'
GAME = 'b40409b08830cc0e1d306ceab0575d7e61db382f50853426bbda58d08f385079'
MANIFEST = '66d8c6e3fc005090ebe44e31f6a8dabd0fdbe1871ffed613cb3769f5b334508a'
INNER = 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
LANES = {
    'g1-team-feedback-20261010': range(1, 5),
    'g1-team-feedback-p1-20261010': range(1, 10),
    'g1-team-completion-20261010': range(1, 10),
    'g1-checkpoint-dialog-20261010': range(1, 4),
    'g1-enemy-clear-checkpoint-20261010': range(1, 3),
    'g1-playtest-revision-20261008': [3],
    'g1-av-revision-20261009': [1],
    'g1-recorded-foley-20261009': [1],
    'g1-foot-contact-audio-v2-20261009': [1, 2],
}
PLAYABLES = [
    'Playtest-G1-Checkpoint-candidate_v2-20261010', 'Playtest-G1-Checkpoint-candidate_v3-20261010',
    *['Playtest-G1-Completion-candidate_v%d-20261010' % n for n in [2, 4, 5, 6, 7, 8, 9]],
    'Playtest-G1-EnemyClear-candidate_v2-20261010', 'Playtest-G1-Foley-V2-20261009',
    'Playtest-G1-Interaction-20261010', 'Playtest-G1-Interaction-V4-20261010',
    *['Playtest-G1-TeamP1-candidate_v%d-20261010' % n for n in [2, 3, 6, 7, 8, 9]],
]
CACHE = {}


def now():
    return datetime.now().astimezone().isoformat()


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf-8')


def safe(rel):
    path = Path(os.path.abspath(ROOT / rel))
    assert path.is_relative_to(ROOT) and path != ROOT, rel
    cursor = path
    while cursor != ROOT:
        if cursor.exists():
            assert not cursor.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT, str(cursor)
        cursor = cursor.parent
    return path


def files(path, skip=None):
    """Never traverse Content junctions; caches may also be excluded."""
    for directory, names, leaves in os.walk(path, followlinks=False):
        base = Path(directory)
        names[:] = [n for n in names if not (base / n).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
                    and (skip is None or not skip(base / n))]
        for name in sorted(leaves):
            p = base / name
            assert not p.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT, str(p)
            if skip is None or not skip(p):
                yield p


def sha(path):
    s = path.stat()
    key = (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
    if key not in CACHE:
        with path.open('rb') as stream:
            CACHE[key] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return CACHE[key]


def row(path, hashed=True):
    s = path.stat()
    r = dict(path=path.relative_to(ROOT).as_posix(), size_bytes=s.st_size, mtime_ns=s.st_mtime_ns)
    if hashed:
        r['sha256'] = sha(path)
    return r


def verify(path, item):
    assert path.is_file() and path.stat().st_size == item['size_bytes'] and sha(path) == item['sha256'], str(path)


def selected_checks():
    review = read(ROOT / 'Docs/Development/CURRENT_CHECKPOINT_REVIEW.json')
    assert review['game_sha256'] == GAME and review['source_manifest_sha256'] == MANIFEST
    manifest = ROOT / review['source_manifest']
    assert sha(manifest) == MANIFEST
    source = ROOT / review['source_snapshot']
    declared = read(manifest)['files']
    assert len(declared) == 52
    assert {p.relative_to(source).as_posix() for p in files(source)} == {r['path'] for r in declared}
    for r in declared:
        verify(source / r['path'], r)
        verify(ROOT / AUTHOR / r['path'], r)
    content = ROOT / AUTHOR / 'Content'
    assert content.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
    assert os.path.samefile(content, ROOT / 'Unreal/ParisStreetCombat/Content')
    assert sha(ROOT / CURRENT / INNER) == sha(ROOT / AUTHOR / 'Binaries/Win64/WW2FranceLiberation.exe') == GAME
    entry = (ROOT / CURRENT / 'PLAY_G1_REVISION.cmd').read_text('utf-8-sig')
    assert 'G1EnemyClearv320261010' in entry
    assert not any(k in entry for k in ['ParisUXTest','ParisInteractionProbe','ParisAVAuditOut','ParisDemo','ParisSpaceSurveyOut'])
    for name, receipt in review['verified_runs'].items():
        p = ROOT / 'tmp/g1-enemy-clear-checkpoint-20261010/checks' / name
        assert sha(p / 'RESULT.json') == receipt['result_sha256']
        result = read(p / 'RESULT.json')
        assert all(c['pass'] for c in result['checks']) and len(result['checks']) == receipt['checks']
        assert read(p / 'launch.json')['exit_code'] == 0
    return review


def target_list():
    targets = [dict(path='tmp/' + p, kind='directory', role='obsolete_playable', exact_recovery=True) for p in PLAYABLES]
    for lane, versions in LANES.items():
        for n in versions:
            project = safe('tmp/%s/candidate_v%d/Project' % (lane, n))
            assert project.is_dir(), str(project)
            for directory, names, _ in os.walk(project, followlinks=False):
                base = Path(directory)
                names[:] = [name for name in names if not (base / name).lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT]
                for name in list(names):
                    if name in {'Binaries', 'Intermediate', 'DerivedDataCache'}:
                        p = safe((base / name).relative_to(ROOT).as_posix())
                        targets.append(dict(path=p.relative_to(ROOT).as_posix(), kind='directory',
                            role='superseded_binary' if name == 'Binaries' else 'rebuildable_cache', exact_recovery=name == 'Binaries'))
                        names.remove(name)
    targets.append(dict(path='tmp/g1-audio-publication-20261009/Paris-G1-Audio-V2-20261009.zip',
        kind='file', role='old_formal_zip_remote_retained', exact_recovery=False))
    assert CURRENT not in {t['path'] for t in targets}
    assert all(not t['path'].startswith(AUTHOR + '/') for t in targets)
    return sorted(targets, key=lambda t:t['path'])


def prepare():
    assert not OUT.exists(), 'Preserve occupied audit identity'
    free = shutil.disk_usage(ROOT).free
    review = selected_checks()
    targets = target_list()
    target_paths = [safe(t['path']) for t in targets]
    def retired(p):
        return any(p == t or p.is_relative_to(t) for t in target_paths)
    OUT.mkdir()
    write(OUT / 'previous_baseline.json', read(ROOT / 'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json'))
    write(OUT / 'previous_checkpoint_review.json', review)
    protected = {}
    def protect(p):
        protected[str(p)] = dict(path=str(p), size_bytes=p.stat().st_size, sha256=sha(p))
    native = read(ROOT / 'tmp/g1-enemy-clear-checkpoint-20261010/freeze.json')
    assert len(native['protected_native']) == 1754
    for r in native['protected_native']:
        p = ROOT / r['path']
        assert sha(p) == r['sha256'], r['path']
        protect(p)
    assert sha(ROOT / 'Assets/Sync/CATALOG.json') == native['catalog_sha256']
    protect(ROOT / 'Assets/Sync/CATALOG.json')
    for path in [ROOT / CURRENT, ROOT / AUTHOR, ROOT / review['source_snapshot'], *[ROOT / 'tmp' / lane for lane in LANES]]:
        for p in files(path, retired):
            protect(p)
    user_root = Path(os.environ['LOCALAPPDATA']) / 'ParisStreetCombat'
    user_files = []
    if user_root.exists():
        for p in files(user_root):
            protect(p)
            user_files.append(str(p))
    previous_recovery = read(ROOT / 'Docs/Development/G1AudioPublicationV2/RECOVERY_MAP_20261009.json')
    legacy = read(ROOT / 'Docs/Development/PackageRetirementV1/RECOVERY_OVERRIDE_20261009.json')['files'][0]
    for p in [ROOT / previous_recovery['recovery_zip']['path'], ROOT / legacy['archive_path']]:
        protect(p)
    print('Protected current source/authoring, 1754 native assets, all user files and preserved evidence.', flush=True)
    retained = {}
    for path in [ROOT / CURRENT, ROOT / AUTHOR / 'Binaries']:
        for p in files(path):
            retained[(p.stat().st_size, sha(p))] = p.relative_to(ROOT).as_posix()
    inventory = []
    mappings = []
    unique = {}
    old_zip_expected = read(ROOT / 'Docs/Development/G1AudioPublicationV2/RESULT_20261009.json')['zip']
    for i, t in enumerate(targets):
        p = safe(t['path'])
        items = [p] if t['kind'] == 'file' else sorted(files(p))
        assert p.exists() and items, t['path']
        rows = []
        for f in items:
            r = row(f, t['exact_recovery'] or t['kind'] == 'file')
            r['target'] = t['path']
            rows.append(r)
            if t['exact_recovery']:
                key = (r['size_bytes'], r['sha256'])
                if key in retained:
                    rec = dict(kind='retained_file', path=retained[key])
                else:
                    rec = dict(kind='zip_entry', entry='objects/' + r['sha256'])
                    unique.setdefault(r['sha256'], f)
                mappings.append(dict(path=r['path'], size_bytes=r['size_bytes'], sha256=r['sha256'], recovery=rec))
        if t['kind'] == 'file':
            verify(p, old_zip_expected)
            t['sha256'] = rows[0]['sha256']
        t['file_count'] = len(rows)
        t['size_bytes'] = sum(r['size_bytes'] for r in rows)
        inventory.extend(rows)
        if i % 15 == 0:
            print('Inventoried %d/%d retirement targets.' % (i + 1, len(targets)), flush=True)
    archive_path = OUT / 'retired_unique_files.zip'
    with zipfile.ZipFile(archive_path, 'x', zipfile.ZIP_DEFLATED, compresslevel=3, allowZip64=True) as z:
        for i, (digest, p) in enumerate(unique.items()):
            z.write(p, 'objects/' + digest)
            if i % 20 == 0:
                print('Archived %d/%d unique recovery files.' % (i + 1, len(unique)), flush=True)
    archive = dict(path=archive_path.relative_to(ROOT).as_posix(), size_bytes=archive_path.stat().st_size, sha256=sha(archive_path))
    for r in mappings:
        if r['recovery']['kind'] == 'zip_entry':
            r['recovery'].update(archive_path=archive['path'], archive_sha256=archive['sha256'])
    mapping = dict(schema_version=1, scope='Retired local playable/Binaries files; derived caches excluded', recovery_zip=archive, files=mappings)
    write(PROOF / 'RECOVERY_MAP_20261010.json', mapping)
    write(OUT / 'retirement.json', dict(schema_version=1, prepared_at=now(), free_before_prepare_bytes=free,
        targets=targets, files=inventory, protected=list(protected.values()), user_files=user_files,
        old_formal_zip_remote_retained=old_zip_expected))
    authority = dict(date='2026-10-10', authorization='User manual review passed; adopt latest baseline and delete superseded local versions',
        private_inventory='tmp/g1-checkpoint-baseline-adoption-20261010/retirement.json',
        inventory_sha256=sha(OUT / 'retirement.json'), recovery_map_sha256=sha(PROOF / 'RECOVERY_MAP_20261010.json'),
        targets=targets, logical_removed_bytes=sum(t['size_bytes'] for t in targets), recovery_zip=archive,
        no_remote_mutation=True, no_git_publication=True)
    write(PROOF / 'RETIREMENT_INVENTORY_20261010.json', authority)
    verify_all(False)
    print(json.dumps(dict(status='prepared_verified', targets=len(targets), old_playables=len(PLAYABLES),
        recovery_bytes=archive['size_bytes'], logical_removed_bytes=authority['logical_removed_bytes'])), flush=True)


def proof():
    authority = read(PROOF / 'RETIREMENT_INVENTORY_20261010.json')
    assert sha(OUT / 'retirement.json') == authority['inventory_sha256']
    assert sha(PROOF / 'RECOVERY_MAP_20261010.json') == authority['recovery_map_sha256']
    return authority, read(OUT / 'retirement.json'), read(PROOF / 'RECOVERY_MAP_20261010.json')


def verify_all(removed):
    authority, plan, mapping = proof()
    selected_checks()
    for i, r in enumerate(plan['protected']):
        verify(Path(r['path']), r)
        if (i + 1) % 1000 == 0:
            print('Verified %d/%d retained file identities.' % (i + 1, len(plan['protected'])), flush=True)
    # User launches must not silently change the frozen save epoch during cleanup.
    user_root = Path(os.environ['LOCALAPPDATA']) / 'ParisStreetCombat'
    assert sorted(str(p) for p in files(user_root)) == sorted(plan['user_files'])
    verify(ROOT / mapping['recovery_zip']['path'], mapping['recovery_zip'])
    checked = set()
    with zipfile.ZipFile(ROOT / mapping['recovery_zip']['path']) as z:
        for r in mapping['files']:
            rec = r['recovery']
            if rec['kind'] == 'retained_file':
                verify(safe(rec['path']), r)
            elif rec['entry'] not in checked:
                info = z.getinfo(rec['entry'])
                assert info.file_size == r['size_bytes']
                with z.open(rec['entry']) as stream:
                    assert hashlib.file_digest(stream, 'sha256').hexdigest() == r['sha256']
                checked.add(rec['entry'])
                if len(checked) % 25 == 0:
                    print('Read back %d unique recovery objects.' % len(checked), flush=True)
    for t in plan['targets']:
        p = safe(t['path'])
        if removed:
            assert not p.exists(), str(p)
        else:
            actual = [p] if t['kind'] == 'file' else list(files(p))
            expected = [r for r in plan['files'] if r['target'] == t['path']]
            assert {r['path'] for r in expected} == {f.relative_to(ROOT).as_posix() for f in actual}
            by_name = {r['path']:r for r in expected}
            for f in actual:
                r = by_name[f.relative_to(ROOT).as_posix()]
                assert f.stat().st_size == r['size_bytes'] and f.stat().st_mtime_ns == r['mtime_ns']
                if 'sha256' in r:
                    verify(f, r)
    print('PASS: selected bytes, assets/users/evidence, recovery readback and retirement scope verified.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'predelete', 'postdelete'])
    a = parser.parse_args()
    if a.mode == 'prepare':
        prepare()
    else:
        verify_all(a.mode == 'postdelete')


if __name__ == '__main__':
    main()
