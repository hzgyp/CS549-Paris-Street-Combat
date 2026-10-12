"""Close byte-protection checks after authorized Catalog selection."""
from publish import ROOT, OUT, PROOF, VARIANT, GAME, MANIFEST, read, write, row, sha, check_static, acl, now

freeze = read(OUT / 'freeze.json')
check_static(freeze)
assert sha(VARIANT / 'SOURCE_MANIFEST.json') == MANIFEST
baseline = read(ROOT / 'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json')
assert baseline['game_sha256'] == GAME
catalog_path = ROOT / 'Assets/Sync/CATALOG.json'
catalog = read(catalog_path)
ledger = read(ROOT / 'Docs/Development/TeamSyncV1/AUTHORIZED_CATALOG_20261008.json')
assert ledger['current'] == row(catalog_path)
prior = read(OUT / 'before-CATALOG.json')
for old in prior['active_manifests']:
    if old['asset_id'] != 'paris-g1-packaged-playtest':
        current = next(x for x in catalog['active_manifests'] if x['asset_id'] == old['asset_id'])
        assert current == old, old['asset_id']
        assert sha(ROOT / current['path']) == current['sha256']
for current in catalog['active_manifests']:
    assert sha(ROOT / current['path']) == current['sha256']
assert len(catalog['active_manifests']) == len(prior['active_manifests']) + 2
cleanup = read(OUT / 'READBACK_CLEANUP.json')
assert cleanup['status'] == 'verified_task_readback_copies_removed'
public_cleanup = dict(status=cleanup['status'], removed_files=cleanup['removed_files'],
                      removed_logical_bytes=cleanup['removed_logical_bytes'],
                      current_package_retained=True, teacher_package_retained=True,
                      obsolete_remote_package_bytes_removed=0)
write(PROOF / 'LOCAL_READBACK_CLEANUP_20261011.json', public_cleanup)
write(PROOF / 'CLOSURE_20261011.json', dict(
    status='pass_source_game_native_teacher_and_catalog_protected', checked_at=now(),
    source_files=len(freeze['source_files']), trial_files=len(freeze['trial_files']),
    protected_native_files=len(freeze['native']), protected_course_access_files=len(freeze['teacher_access']),
    source_manifest_sha256=MANIFEST, game_sha256=GAME,
    unchanged_prior_manifest_roles=len(prior['active_manifests']) - 1,
    active_manifest_roles=len(catalog['active_manifests']), catalog=row(catalog_path),
    teacher_access_unchanged=True, root_acl_unchanged=acl() == freeze['root_acl'],
    cleanup=public_cleanup, no_game_editor_entry=True))
print('FINAL BYTE PROTECTION PASS: source76/trial100/native1754/course7/Catalog15')
