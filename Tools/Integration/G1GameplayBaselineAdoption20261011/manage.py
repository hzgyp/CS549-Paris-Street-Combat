"""Freeze and verify the reviewed local gameplay adoption and exact retirement."""
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'tmp/g1-gameplay-baseline-adoption-20261011'
PROOF = ROOT / 'Docs/Development/G1GameplayBaselineAdoption20261011'
LANE = ROOT / 'tmp/g1-tactical-equipment-20261010'
CURRENT = 'tmp/Playtest-G1-GrenadeEquip-20261011'
AUTHOR = 'tmp/g1-tactical-equipment-20261010/candidate_grenade_equip_v1/Project'
GAME = 'b5357cd4ff39454ec40d72ba96ce8ab379f0e039c83b6170263f631e45c4124d'
MANIFEST = '9ac0620c0794c2cc64c0b701d50e7dba4a82941bee7d147be1f72cd604d9312d'
INNER = 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
KEEP_CANDIDATES = {'candidate_grenade_equip_v1', 'candidate_grenade_equip_build_v4', 'candidate_full_v8', 'candidate_full_v16'}
OLD_PLAYABLES = ['TacticalEquipment-20261010', 'PressureMine-20261011', 'CombatUI-20261011', 'FieldManualUI-20261011', 'DeathPresentation-20261011', 'GrenadeModels-20261011', 'EquipmentWheel-20261011']
META = {'.json', '.txt', '.log', '.rsp', '.response', '.manifest', '.xml', '.ini', '.cpp', '.h', '.cs', '.bat', '.cmd', '.ps1', '.py', '.modules', '.target'}
CACHE = {}

def now():
    return datetime.now().astimezone().isoformat()

def read(p):
    return json.loads(p.read_text('utf-8-sig'))

def write(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', 'utf-8')

def reparse(p):
    return bool(p.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)

def safe(rel):
    p = Path(os.path.abspath(ROOT / rel))
    assert p.is_relative_to(ROOT) and p != ROOT, 'Outside workspace'
    q = p
    while q != ROOT:
        if q.exists():
            assert not reparse(q), str(q)
        q = q.parent
    return p

def files(p, skip=None):
    for directory, names, leaves in os.walk(p, followlinks=False):
        base = Path(directory)
        names[:] = sorted(n for n in names if not reparse(base/n) and not (skip and skip(base/n)))
        for n in sorted(leaves):
            f = base/n
            assert not reparse(f), str(f)
            if not (skip and skip(f)):
                yield f

def sha(p):
    s = p.stat()
    key = (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns)
    if key not in CACHE:
        with p.open('rb') as stream:
            CACHE[key] = hashlib.file_digest(stream, 'sha256').hexdigest()
    return CACHE[key]

def row(p, hashed=True):
    s = p.stat()
    r = dict(path=p.relative_to(ROOT).as_posix(), size_bytes=s.st_size, mtime_ns=s.st_mtime_ns)
    if hashed:
        r['sha256'] = sha(p)
    return r

def verify(p, r):
    assert p.is_file() and p.stat().st_size == r['size_bytes'] and sha(p) == r['sha256'], str(p)

def engines():
    code = "@(Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'UnrealEditor|WW2France|UnrealPak|ShaderCompile|UnrealBuildTool|AutomationTool' -or ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool') } | Select-Object ProcessId,ParentProcessId,Name,CommandLine) | ConvertTo-Json -Compress"
    r = subprocess.run(['powershell', '-NoProfile', '-Command', code], capture_output=True, text=True, check=True)
    value = json.loads(r.stdout or '[]')
    return value if isinstance(value, list) else [value]

def check_processes(targets):
    procs=engines();approved=set()
    paths=[safe(t['path']) for t in targets]
    projects={str(p).split(os.sep+'Project'+os.sep)[0]+os.sep+'Project' for p in paths if os.sep+'Project'+os.sep in str(p)}
    for proc in procs:
        cmd=proc.get('CommandLine') or ''
        assert cmd and not proc['Name'].startswith('WW2France'), 'Preserve active game/unidentified process'
        assert not any(str(p).lower() in cmd.lower() for p in paths), proc['ProcessId']
        assert not any(p.lower() in cmd.lower() for p in projects), proc['ProcessId']
        matches=re.findall(r'"([^"]+\.uproject)"|(\S+\.uproject)',cmd)
        if matches and any(Path(a or b).is_file() for a,b in matches):
            approved.add(proc['ProcessId'])
    for proc in procs:
        if proc['ProcessId'] in approved:
            continue
        assert proc['Name']=='ShaderCompileWorker.exe' and proc['ParentProcessId'] in approved, 'Unknown build owner; preserve process'
    return procs

def selected_checks():
    delivery = read(ROOT/'tmp/g1-grenade-equip-20261011/DELIVERY_20261011.json')
    assert delivery['game_sha256'] == GAME and delivery['source_manifest_sha256'] == MANIFEST
    manifest = ROOT/delivery['source_manifest']
    assert sha(manifest) == MANIFEST
    source = ROOT/delivery['source_snapshot']
    declared = read(manifest)['files']
    assert len(declared) == 76
    assert {f.relative_to(source).as_posix() for f in files(source)} == {r['path'] for r in declared}
    for r in declared:
        verify(source/r['path'], r)
        verify(ROOT/AUTHOR/r['path'], r)
    assert sha(ROOT/CURRENT/INNER) == sha(ROOT/AUTHOR/'Binaries/Win64/WW2FranceLiberation.exe') == GAME
    actual = {f.relative_to(ROOT/CURRENT).as_posix(): f for f in files(ROOT/CURRENT)}
    assert set(actual) == {r['path'] for r in delivery['normal_files']}
    for r in delivery['normal_files']:
        verify(actual[r['path']], r)
    entry = (ROOT/delivery['playable_entry']).read_text('utf-8-sig')
    assert 'G1GrenadeEquip20261011' in entry and 'ParisGrenadeEquipV2' in entry
    assert not any(k in entry for k in ['Probe', 'EquipmentCheck', 'Observer', 'Solo', 'Background', 'BlastDiag'])
    assert reparse(ROOT/AUTHOR/'Content') and os.path.samefile(ROOT/AUTHOR/'Content', ROOT/'Unreal/ParisStreetCombat/Content')
    assert len(delivery['checks']) == 15
    for r in delivery['checks']:
        p = ROOT/r['result']
        assert sha(p) == r['sha256'] and read(p)['status'] == r['status'] and r['status'].startswith('pass')
        launch = read(p.parent/'launch.json')
        assert launch['exit_code'] == 0 and launch['game_sha256'] == GAME
    return delivery

def target_list():
    targets = [dict(path='tmp/Playtest-G1-'+p, role='obsolete_playable', exact_recovery=True) for p in OLD_PLAYABLES]
    for candidate in sorted(LANE.glob('candidate_*')):
        if candidate.name in KEEP_CANDIDATES:
            continue
        for n in ['Runtime', 'Archive']:
            p = candidate/n
            if p.is_dir():
                targets.append(dict(path=p.relative_to(ROOT).as_posix(), role='superseded_runtime', exact_recovery=True))
        project = candidate/'Project'
        if not project.is_dir():
            continue
        for directory, names, _ in os.walk(project, followlinks=False):
            base = Path(directory)
            names[:] = sorted(n for n in names if n != 'Saved' and not reparse(base/n))
            for n in list(names):
                if n in {'Binaries', 'Intermediate', 'DerivedDataCache'}:
                    p = safe((base/n).relative_to(ROOT).as_posix())
                    targets.append(dict(path=p.relative_to(ROOT).as_posix(), role='superseded_binary' if n == 'Binaries' else 'rebuildable_cache', exact_recovery=n == 'Binaries'))
                    names.remove(n)
    for t in targets:
        assert safe(t['path']).is_dir(), t['path']
    return sorted(targets, key=lambda t: t['path'])

def prepare():
    assert not OUT.exists(), 'Preserve occupied identity'
    free = shutil.disk_usage(ROOT).free
    delivery = selected_checks()
    targets = target_list()
    absolute = [safe(t['path']) for t in targets]
    exact_paths = {str(t) for t in absolute}
    path_prefixes = tuple(str(t)+os.sep for t in absolute)
    def retired(p):
        s = str(p)
        if s in exact_paths or s.startswith(path_prefixes):
            return True
        # Prune protected current/active derived and volatile directories before
        # walking, instead of visiting every file and rejecting it afterwards.
        parts = p.relative_to(ROOT).parts
        return any(c in parts for c in KEEP_CANDIDATES) and any(n in parts for n in ['Intermediate','DerivedDataCache','Saved'])
    check_processes(targets)
    OUT.mkdir()
    write(OUT/'previous_baseline.json', read(ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json'))
    write(OUT/'previous_equipment_review.json', read(ROOT/'Docs/Development/CURRENT_EQUIPMENT_INPUT_REVIEW.json'))
    protected = {}
    def protect(p):
        protected[str(p)] = dict(path=str(p), size_bytes=p.stat().st_size, sha256=sha(p))
    freeze = read(ROOT/'tmp/g1-grenade-equip-20261011/freeze.json')
    for r in freeze['protected_native']:
        verify(ROOT/r['path'], r)
        protect(ROOT/r['path'])
    assert len(freeze['protected_native']) == 1754
    assert sha(ROOT/'Assets/Sync/CATALOG.json') == freeze['catalog_sha256']
    protect(ROOT/'Assets/Sync/CATALOG.json')
    evidence_roots = ['Unreal/Variants', CURRENT, 'tmp/Playtest-G1-EnemyClear-candidate_v3-20261010', 'tmp/g1-tactical-equipment-20261010', 'tmp/g1-grenade-equip-20261011', 'tmp/g1-combat-ui-20261011', 'tmp/g1-player-death-20261011', 'tmp/g1-grenade-models-20261011', 'tmp/g1-equipment-wheel-20261011', 'Failures']
    for rel in evidence_roots:
        for p in files(ROOT/rel, retired):
            # Active/current build caches and continuously-written Editor data are
            # outside the deletion scope; avoid freezing those volatile files.
            parts = p.relative_to(ROOT).parts
            if any(c in parts for c in KEEP_CANDIDATES) and any(n in parts for n in ['Intermediate', 'DerivedDataCache', 'Saved']):
                continue
            protect(p)
    user_root = Path(os.environ['LOCALAPPDATA'])/'ParisStreetCombat'
    user_files = list(files(user_root)) if user_root.exists() else []
    for p in user_files:
        protect(p)
    print('Protected source/raw/native/current and latest user files', len(protected), flush=True)
    retained = {}
    for rel in [CURRENT, AUTHOR+'/Binaries', 'tmp/Playtest-G1-EnemyClear-candidate_v3-20261010', 'tmp/g1-tactical-equipment-20261010/candidate_full_v8', 'tmp/g1-tactical-equipment-20261010/candidate_full_v16']:
        for p in files(ROOT/rel, lambda q: q.name in {'Intermediate', 'Saved', 'DerivedDataCache'}):
            retained[(p.stat().st_size, sha(p))] = p.relative_to(ROOT).as_posix()
    inventory, mappings, unique, metadata = [], [], {}, []
    for i, t in enumerate(targets):
        paths = list(files(safe(t['path'])))
        for p in paths:
            r = row(p, t['exact_recovery'])
            r['target'] = t['path']
            inventory.append(r)
            if t['exact_recovery']:
                key = (r['size_bytes'], r['sha256'])
                if key in retained:
                    rec = dict(kind='retained_file', path=retained[key])
                else:
                    rec = dict(kind='zip_entry', entry='objects/'+r['sha256'])
                    unique.setdefault(r['sha256'], p)
                mappings.append(dict(path=r['path'], size_bytes=r['size_bytes'], sha256=r['sha256'], recovery=rec))
            elif p.suffix.lower() in META:
                dest = OUT/'BuildMetadata'/p.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, dest)
                r['sha256'] = sha(p)
                assert sha(dest) == r['sha256']
                metadata.append(dict(r, retained_path=dest.relative_to(ROOT).as_posix()))
        t.update(file_count=len(paths), size_bytes=sum(p.stat().st_size for p in paths))
        if (i+1) % 15 == 0:
            print('Inventoried', i+1, '/', len(targets), flush=True)
    archive_path = OUT/'retired_unique_files.zip'
    with zipfile.ZipFile(archive_path, 'x', zipfile.ZIP_DEFLATED, compresslevel=3, allowZip64=True) as z:
        for i, (digest, p) in enumerate(unique.items()):
            z.write(p, 'objects/'+digest)
            if (i+1) % 20 == 0:
                print('Archived', i+1, '/', len(unique), flush=True)
    archive = dict(path=archive_path.relative_to(ROOT).as_posix(), size_bytes=archive_path.stat().st_size, sha256=sha(archive_path))
    for r in mappings:
        if r['recovery']['kind'] == 'zip_entry':
            r['recovery']['archive_path'] = archive['path']
    write(PROOF/'RECOVERY_MAP_20261011.json', dict(schema_version=1, recovery_zip=archive, files=mappings))
    write(OUT/'retirement.json', dict(prepared_at=now(), free_before_prepare_bytes=free, targets=targets, files=inventory, protected=list(protected.values()), metadata=metadata, user_root=str(user_root), user_files=[str(p) for p in user_files], original_engines=engines(), game_sha256=GAME))
    write(PROOF/'RETIREMENT_INVENTORY_20261011.json', dict(authorization='User manual review: logic accepted with remaining sleeve occlusion; adopt and retire obsolete local versions', private_inventory=(OUT/'retirement.json').relative_to(ROOT).as_posix(), inventory_sha256=sha(OUT/'retirement.json'), recovery_map_sha256=sha(PROOF/'RECOVERY_MAP_20261011.json'), recovery_zip=archive, targets=targets, logical_removed_bytes=sum(t['size_bytes'] for t in targets)))
    verify_all(False)
    print('PREPARED', len(targets), 'targets; recovery GiB', round(archive['size_bytes']/2**30, 2), flush=True)

def proof():
    authority = read(PROOF/'RETIREMENT_INVENTORY_20261011.json')
    assert sha(OUT/'retirement.json') == authority['inventory_sha256']
    assert sha(PROOF/'RECOVERY_MAP_20261011.json') == authority['recovery_map_sha256']
    return authority, read(OUT/'retirement.json'), read(PROOF/'RECOVERY_MAP_20261011.json')

def verify_live_logs(plan):
    for r in plan.get('live_editor_logs',[]):
        verify(ROOT/r['snapshot']['path'],r['snapshot'])
        with Path(r['path']).open('rb') as stream:
            original=stream.read(r['size_bytes'])
        assert len(original)==r['size_bytes'] and hashlib.sha256(original).hexdigest()==r['sha256'], 'Original live Editor log prefix changed'

def verify_all(removed):
    authority, plan, mapping = proof()
    selected_checks()
    for r in plan['protected']:
        verify(Path(r['path']), r)
    verify_live_logs(plan)
    assert sorted(str(p) for p in files(Path(plan['user_root']))) == sorted(plan['user_files'])
    for r in plan['metadata']:
        verify(ROOT/r['retained_path'], r)
    verify(ROOT/mapping['recovery_zip']['path'], mapping['recovery_zip'])
    checked = set()
    if removed:
        # The deletion runner reaches this receipt only after its full predelete
        # recovery readback passed. The archive is outside all deletion targets;
        # its unchanged SHA proves those verified objects are still identical.
        assert read(OUT/'local-retirement.json')['targets']==len(plan['targets'])
    with zipfile.ZipFile(ROOT/mapping['recovery_zip']['path']) as z:
        for r in mapping['files']:
            rec = r['recovery']
            if rec['kind'] == 'retained_file':
                verify(safe(rec['path']), r)
            elif rec['entry'] not in checked:
                assert z.getinfo(rec['entry']).file_size == r['size_bytes']
                if not removed:
                    with z.open(rec['entry']) as s:
                        assert hashlib.file_digest(s, 'sha256').hexdigest() == r['sha256']
                checked.add(rec['entry'])
    for t in plan['targets']:
        p = safe(t['path'])
        if removed:
            assert not p.exists(), str(p)
        else:
            actual = {f.relative_to(ROOT).as_posix(): f for f in files(p)}
            expected = [r for r in plan['files'] if r['target'] == t['path']]
            assert set(actual) == {r['path'] for r in expected}
            for r in expected:
                f = actual[r['path']]
                assert f.stat().st_size == r['size_bytes'] and f.stat().st_mtime_ns == r['mtime_ns']
                if 'sha256' in r:
                    verify(f, r)
    print('PASS retained source/native/user/raw, recovery readback and exact retirement scope', flush=True)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['prepare', 'predelete', 'postdelete'])
    args = p.parse_args()
    if args.mode == 'prepare':
        prepare()
    else:
        verify_all(args.mode == 'postdelete')
