"""Nondestructive inventory/recovery preparation for explicitly retired packages."""
import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/PackageRetirement20261009/run_v1'
OLD = STORE / 'Evidence/StorageCleanup20261009/run_v1'
MVPD = STORE / 'Evidence/MVPCloseoutV1/delivery_v1'
HUDD = STORE / 'Evidence/G1HUDConceptV1/delivery_v1'
LATEST = ROOT / 'tmp/Playtest-G1-HUD-20261009'
HUD_ARCHIVE = ROOT / 'tmp/g1-playtest-revision-20261008/hud_v3/Archive'
VARIANT = ROOT / 'Unreal/Variants/G1HUDPlaytest20261009'
AUTHOR = ROOT / 'tmp/g1-playtest-revision-20261008/candidate_v3/Project'
OVERRIDE = ROOT / 'Docs/Development/PackageRetirementV1/RECOVERY_OVERRIDE_20261009.json'
BASELINE = ROOT / 'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json'
GAME_SHA = '497221422d7754d562b4e6d11fd8cc50c9223e40b329b26c8c14391a98d1c42b'
TARGETS = {
    'tmp/Playtest-G1-20261008': 'recoverable',
    'tmp/Playtest-G1-20261009': 'recoverable',
    'tmp/mvp-closeout-20261008/instrument_v13/Archive': 'recoverable',
    'tmp/paris-city-package-20261002/package_v3/Archive': 'retired_generated_payload',
    'Unreal/ParisStreetCombat/Saved/StagedBuilds': 'retired_generated_payload',
}
for ident in ('instrument_v1', 'instrument_v2', 'instrument_v6', 'instrument_v7', 'instrument_v14', 'instrument_v15'):
    TARGETS[f'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1/failures/{ident}/Archive'] = 'recoverable'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def rel(path):
    return path.relative_to(ROOT).as_posix()

def reparse(path):
    return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)

def safe(name):
    path = ROOT / name
    assert path.resolve().is_relative_to(ROOT.resolve()), 'Outside workspace'
    for ancestor in [path] + list(path.parents):
        if ancestor == ROOT:
            break
        if ancestor.exists():
            assert not reparse(ancestor), 'Reparse ancestor: ' + str(ancestor)
    return path

def inventory(folder):
    folder = safe(rel(folder))
    found = []
    for parent, dirs, files in os.walk(folder, followlinks=False):
        for name in dirs + files:
            path = Path(parent) / name
            assert not reparse(path), 'No reparse descendants allowed'
        found += [Path(parent) / name for name in files]
    return sorted(found)

def metadata(path):
    info = path.stat()
    return dict(path=rel(path), size_bytes=info.st_size, mtime_ns=info.st_mtime_ns)

def idle():
    runtime = Path(os.environ['USERPROFILE']) / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/powershell/pwsh.exe'
    expression = "$p=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match '^(UnrealEditor|WW2FranceLiberation|UnrealEditor-Cmd|UnrealPak|ShaderCompileWorker|UnrealBuildTool|AutomationTool).*\\.exe$' -or ($_.Name -eq 'dotnet.exe' -and $_.CommandLine -match 'UnrealBuildTool|AutomationTool')}); if($p.Count){throw 'Preserve active user/build processes'}"
    subprocess.run([str(runtime), '-NoProfile', '-Command', expression], check=True)

def contracts():
    sys.path.insert(0, str(ROOT / 'Tools/Integration'))
    from verify_team_source import verify_source
    sys.path.insert(0, str(ROOT / 'Tools/Integration/NPCInteractionV1'))
    from common import guard_rows, guards_match
    assert verify_source()['source_files'] == 758
    protected = guard_rows(); assert len(protected) == 703 and guards_match(protected)
    contract = read(VARIANT / 'SOURCE_MANIFEST.json')
    assert len(contract['files']) == 40
    for row in contract['files']:
        for base in (VARIANT / 'Project', AUTHOR, HUDD / 'SourcePatch'):
            assert (base / row['path']).stat().st_size == row['size_bytes']
            assert sha(base / row['path']) == row['sha256'], str(base / row['path'])
    assert sha(LATEST / 'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe') == GAME_SHA
    return dict(canonical_source_files=758, protected_files=703, selected_source_files=40,
                source_manifest_sha256=sha(VARIANT / 'SOURCE_MANIFEST.json'), game_sha256=GAME_SHA)

def prepare():
    assert not OUT.exists() and not BASELINE.exists() and not OVERRIDE.exists(), 'Preserve occupied identity'
    idle(); identities = contracts()
    current_rows = []
    receipt = read(HUDD / 'delivery_receipt.json')
    assert len(inventory(LATEST)) == 50
    expected = {r['path']: dict(r) for r in receipt['archive_files']}
    expected['PLAY_G1_REVISION.cmd']['sha256'] = receipt['delivery_launcher_override']['delivered_sha256']
    expected['PLAY_G1_REVISION.cmd']['size_bytes'] = (LATEST / 'PLAY_G1_REVISION.cmd').stat().st_size
    assert {p.relative_to(LATEST).as_posix() for p in inventory(LATEST)} == set(expected) | {'README.md','README_ZH.md','REVISION_RECEIPT.json'}
    print('Verifying the selected latest trial and current recovery inputs', flush=True)
    for file in inventory(LATEST):
        row = {**metadata(file), 'sha256': sha(file)}
        if file.relative_to(LATEST).as_posix() in expected:
            original = expected[file.relative_to(LATEST).as_posix()]
            assert row['size_bytes'] == original['size_bytes'] and row['sha256'] == original['sha256']
        current_rows.append(row)
    old_plan = read(OLD / 'plan.json'); old_result = read(OLD / 'result.json')
    assert sha(OLD / 'plan.json') == old_result['plan_sha256']
    old_unique = OLD / 'intermediate_unique_payloads.zip'
    assert sha(old_unique) == old_plan['zip_sha256']
    old_receipt = read(MVPD / 'delivery_receipt.json')
    old_package = MVPD / 'Paris_Street_Combat_G1_Private_Candidate_Win64.zip'
    assert old_package.stat().st_size == old_receipt['zip_size_bytes'] and sha(old_package) == old_receipt['zip_sha256']
    references = {}
    verified_zip_members = set()
    def zip_check(archive_path, member, digest, size):
        key = (str(archive_path), member)
        if key not in verified_zip_members:
            with zipfile.ZipFile(archive_path) as archive:
                assert archive.getinfo(member).file_size == size
                with archive.open(member) as stream:
                    assert hashlib.file_digest(stream,'sha256').hexdigest() == digest
            verified_zip_members.add(key)
    for file in inventory(HUD_ARCHIVE):
        digest = sha(file)
        references[digest] = dict(kind='retained_file', path=rel(file), size_bytes=file.stat().st_size)
    for row in read(MVPD / 'build_manifest.json')['files']:
        references.setdefault(row['sha256'], dict(kind='existing_zip', archive_path=rel(old_package), entry=row['path'], size_bytes=row['size_bytes']))
    for row in old_plan['zip_objects']:
        references.setdefault(row['sha256'], dict(kind='existing_zip', archive_path=rel(old_unique), entry=row['entry'], size_bytes=row['size_bytes']))
    remap_rows = []
    for row in old_plan['retained_files']:
        if '/instrument_v13/Archive/' in row['path']:
            member = row['path'].split('/Archive/', 1)[1]
            zip_check(old_package, member, row['sha256'], row['size_bytes'])
            remap_rows.append({**row, 'archive_path':rel(old_package),'entry':member,'archive_sha256':old_receipt['zip_sha256']})
        else:
            assert sha(ROOT / row['path']) == row['sha256']
    assert len(remap_rows) == 7
    OUT.mkdir(parents=True)
    new_zip = OUT / 'retired_unique_files.zip'
    objects = {}; files = []; targets = []; used = {}
    with zipfile.ZipFile(new_zip, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=1, allowZip64=True) as archive:
        for target, kind in TARGETS.items():
            print('Inventory/recovery: ' + target, flush=True)
            payload = inventory(ROOT / target); assert payload
            total = 0
            for file in payload:
                row = {**metadata(file), 'target':target}
                assert '/SaveGames/' not in row['path'], 'Protect user saves'
                assert '/Saved/' not in row['path'] or target.endswith('/Saved/StagedBuilds'), 'Protect user Saved directories'
                if kind == 'recoverable':
                    digest = sha(file); row['sha256'] = digest
                    reference = references.get(digest)
                    if reference:
                        assert reference['size_bytes'] == row['size_bytes']
                        if reference['kind'] == 'existing_zip':
                            zip_check(ROOT/reference['archive_path'],reference['entry'],digest,row['size_bytes'])
                        row['recovery'] = dict(reference); used[digest] = dict(reference,sha256=digest)
                    else:
                        assert row['size_bytes'] <= 1024**3, 'Unknown unique large payload; preserve it and reassess'
                        member = 'objects/' + digest
                        if digest not in objects:
                            archive.write(file, member)
                            objects[digest] = dict(entry=member,size_bytes=row['size_bytes'],sha256=digest)
                        row['recovery'] = dict(kind='new_zip',archive_path=rel(new_zip),entry=member,size_bytes=row['size_bytes'])
                else:
                    row['recovery'] = dict(kind='retired_rebuildable_success_payload_no_bit_exact_promise')
                    if file.suffix in {'.exe','.dll','.json','.txt','.ini'}:
                        row['sha256'] = sha(file)
                files.append(row); total += row['size_bytes']
            targets.append(dict(path=target,kind=kind,files=len(payload),size_bytes=total))
    with zipfile.ZipFile(new_zip) as archive:
        for row in objects.values():
            with archive.open(row['entry']) as stream:
                assert hashlib.file_digest(stream,'sha256').hexdigest() == row['sha256']
    override = dict(schema_version=1, authorization='2026-10-09 user selects HUD development baseline and permits obsolete package deletion',
                    original_plan_sha256=old_result['plan_sha256'], files=remap_rows,
                    scope='Only seven instrument_v13 retained-file references advance to verified existing ZIP members; original plan/result unchanged')
    write(OVERRIDE, override)
    latest_zip = ROOT / 'tmp/paris-g1-playtest-20261009-hud-v3/Paris-G1-HUD-20261009.zip'
    published = read(ROOT / 'Assets/Sync/manifests/paris-g1-packaged-playtest.json')
    assert latest_zip.stat().st_size == published['size_bytes']
    selected = dict(schema_version=1, status='selected_active_development_baseline',
        authorization='2026-10-09 user selects this latest local HUD version as the basis for subsequent development',
        selected_at=datetime.now().astimezone().isoformat(), baseline_id='g1-hud-v3-20261009',
        playable_directory=rel(LATEST), playable_entry=rel(LATEST/'PLAY_G1_REVISION.cmd'),
        game_sha256=GAME_SHA, source_snapshot=rel(VARIANT/'Project'),
        source_manifest=rel(VARIANT/'SOURCE_MANIFEST.json'), source_manifest_sha256=identities['source_manifest_sha256'],
        active_authoring_project=rel(AUTHOR/'WW2FranceLiberation.uproject'),
        active_source_files=40, sftp_release=published['asset_version'],
        sftp_download='/releases/paris-g1-playtest-20261009-hud-v3/Paris-G1-HUD-20261009.zip',
        matching_published_source_commit='79421db822c344a693a682f1af6bc3e40cfa0119',
        native_asset_anchor='paris-native-playtest-20261008-g1-npc-vfx-v1',
        canonical_source_contract_role='758-file asset/native integration anchor; not the current starting gameplay/HUD source',
        protected='Original models/rigs/weights/materials/finger poses/accepted gun logic/native source and user checkpoints retained',
        save_prefix='ParisG1PlaytestV5', save_directory='%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestV5',
        remaining_gates=['full motion/contact','low-posture camera and sprint/jump lowering','second machine','performance','natural opposing combat','video','course acceptance'],
        future_rule='Read this selector and failure cases before implementation. Branch from its exact source snapshot or matching active authoring Project. Do not restart from older V13/V10 gameplay/HUD code.')
    write(BASELINE, selected)
    plan = dict(schema_version=1, status='prepared_no_deletion', authorization=override['authorization'],
        created_at=datetime.now().astimezone().isoformat(), targets=targets,files=files,
        new_zip=dict(path=rel(new_zip),size_bytes=new_zip.stat().st_size,sha256=sha(new_zip),objects=list(objects.values())),
        used_recovery_inputs=list(used.values()),
        existing_zip_pins=[dict(path=rel(old_package),sha256=old_receipt['zip_sha256'],size_bytes=old_receipt['zip_size_bytes']),
                           dict(path=rel(old_unique),sha256=old_plan['zip_sha256'],size_bytes=old_plan['zip_size_bytes'])],
        original_cleanup_plan_sha256=old_result['plan_sha256'], original_cleanup_result_sha256=sha(OLD/'result.json'),
        recovery_override_path=rel(OVERRIDE),recovery_override_sha256=sha(OVERRIDE),
        baseline_path=rel(BASELINE),baseline_sha256=sha(BASELINE), current_trial_files=current_rows,
        selected_archive_files=[dict(**metadata(ROOT/r['path']),sha256=d) for d,r in references.items() if r['kind']=='retained_file'],
        current_selected_zip_metadata=metadata(latest_zip), identities=identities,
        unique_zip_members_verified=len(objects), existing_used_zip_members_verified=len(verified_zip_members))
    write(OUT/'plan.json',plan)
    write(OUT/'prepared.json',dict(plan_sha256=sha(OUT/'plan.json'),status='prepared_no_deletion'))
    idle(); contracts()
    print(json.dumps(dict(status=plan['status'],targets=len(targets),logical_bytes=sum(t['size_bytes'] for t in targets),
                         unique_archive_bytes=new_zip.stat().st_size,recovery_remapped_files=len(remap_rows))),flush=True)

def verify(full=False):
    plan = read(OUT/'plan.json'); prepared = read(OUT/'prepared.json')
    assert sha(OUT/'plan.json') == prepared['plan_sha256']
    assert sha(BASELINE) == plan['baseline_sha256'] and sha(OVERRIDE) == plan['recovery_override_sha256']
    assert sha(OLD/'plan.json') == plan['original_cleanup_plan_sha256'] and sha(OLD/'result.json') == plan['original_cleanup_result_sha256']
    assert contracts() == plan['identities']
    for row in plan['current_trial_files'] + plan['selected_archive_files']:
        file=ROOT/row['path']; info=file.stat()
        assert info.st_size==row['size_bytes'] and info.st_mtime_ns==row['mtime_ns']
    assert len(inventory(LATEST))==50 and len(inventory(HUD_ARCHIVE))==47
    latest = plan['current_selected_zip_metadata']; assert metadata(ROOT/latest['path']) == latest
    if full:
        for row in plan['existing_zip_pins'] + [plan['new_zip']]:
            assert (ROOT/row['path']).stat().st_size==row['size_bytes'] and sha(ROOT/row['path'])==row['sha256']
        for row in plan['used_recovery_inputs']:
            if row['kind']=='retained_file': assert sha(ROOT/row['path'])==row['sha256']
        # Package bytes were fully hashed during preparation. Frozen full path/
        # size/time inventories and idle checks detect subsequent changes; the
        # executor independently checks them before any removal. Recheck smaller
        # binaries/text directly; avoid repeating 76GB of identical bulk reads.
        for row in plan['files']:
            if row.get('sha256') and row['size_bytes'] <= 1024**3:
                assert sha(ROOT/row['path'])==row['sha256']
    return plan

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['prepare','predelete','verify'])
    args=parser.parse_args()
    if args.phase=='prepare': prepare()
    elif args.phase=='predelete':
        idle(); verify(full=True); print('Complete protected/backup/input predelete verification passes',flush=True)
    else:
        plan=verify(); assert all(not (ROOT/row['path']).exists() for row in plan['targets'])
        write(OUT/'final_verification.json',dict(status='pass_baseline_and_retired_packages',identities=plan['identities'],
              targets_absent=len(plan['targets']),current_trial_files=50,selected_archive_files=47,original_cleanup_receipts_exact=True,
              verified_at=datetime.now().astimezone().isoformat()))
        print('Selected baseline intact; eleven old output directories absent; recovery remap and original receipts exact',flush=True)
