"""Authenticate completed G1 proofs and failure references; no native writes."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest
bank=STORE/'Evidence/G1MissionV1'
required=('staging_author_v2_20261008','spawn_view_v1_20261008','travel_v4_20261008',
          'functional_v4_20261008','load_v2_20261008','lifecycle_v1_20261008',
          'outcomes_v2_20261008','encounter_v2_20261008','plain_v1_20261008')
out=bank/'closure_v1_20261008'
assert not out.exists(),'Preserve existing closure'
rows=guard_rows();assert len(rows)==703 and guards_match(rows)
proofs=[]
def row(path):
    return {'path':path.relative_to(ROOT).as_posix(),'size_bytes':path.stat().st_size,'sha256':digest(path)}
for identity in required:
    folder=bank/identity
    audit_file=folder/('audit_python_log_v2.json' if identity=='plain_v1_20261008' else 'audit.json')
    audit=json.loads(audit_file.read_text())
    assert audit['status']=='pass_native_entry_audit' and all(audit['checks'].values()),identity
    proofs.append({'identity':identity,'audit':row(audit_file),
                   'raw':row(folder/'result.json') if (folder/'result.json').exists() else None})
admission=json.loads((bank/'staging_author_v2_20261008/result.json').read_text())
assert all(digest(ROOT/f['path'])==f['sha256'] for f in admission['files'])
assert all(digest(ROOT/p)==h for p,h in admission['old_controls'].items())
# Every authenticated owned package is also checked by each later native admission.
runtime=json.loads((bank/'plain_v1_20261008/runtime_manifest.json').read_text(encoding='utf-8-sig'))
assert all(digest(ROOT/f['path'])==f['sha256'] for f in runtime['files'])
def manifest(name,identities,extra=()):
    target=ROOT/'Failures'/name/'MANIFEST.json';assert not target.exists()
    paths=[]
    for identity in identities:
        paths.extend(p for p in (bank/identity).rglob('*') if p.is_file())
        log=ROOT/'tmp/g1-mission-v1'/f'{identity}.log'
        paths.extend(p for p in (log,Path(str(log)+'.exit.json')) if p.is_file())
    paths.extend(p for p in extra if p.is_file())
    paths=sorted(set(paths))
    value={'schema':'paris_failure_reference_manifest_v1','date':'2026-10-08',
           'private_bytes_retained_in_place':True,'no_failed_receipt_relabelled':True,
           'files':[row(p) for p in paths]}
    target.write_text(json.dumps(value,indent=2)+'\n')
    return row(target)
mi=('author_v1_20261008','author_v2_20261008','author_v3_20261008',
    'ready_v1_20261008','encounter_config_v1_20261008','functional_v1_20261008',
    'functional_v2_20261008','functional_v3_20261008','travel_v1_20261008','travel_v2_20261008','plain_v1_20261008')
build_logs=list((ROOT/'tmp').glob('g1*build*.log'))
failures=[manifest('MI001-20261008-g1-mission-authoring',mi,build_logs),
          manifest('ML022-20261008-g1-initial-visual-site',
                   ('view_v1_20261008','ready_v2_20261008','travel_v2_20261008','travel_v3_20261008',
                    'spawn_view_v1_20261008','staging_author_v2_20261008','functional_v4_20261008'))]
figure=bank/'staging_layout_v2_20261008'
out.mkdir()
result={'schema':'paris_g1_functional_closure_v1','status':'pass_bounded_local_functional_checks',
        'date':'2026-10-08','protected_count':703,'protected_exact':True,'proofs':proofs,
        'runtime_manifest':row(bank/'plain_v1_20261008/runtime_manifest.json'),
        'selected_native_admission':row(bank/'staging_author_v2_20261008/result.json'),
        'selected_owned_files':admission['files'],'old_valid_controls_unchanged':True,
        'config':row(bank/'staging_config_v2_20261008/config.json'),
        'layout':[row(figure/'layout.json'),row(figure/'G1_MVP_LAYOUT_20261008.png')],
        'failure_manifests':failures,'commercial_bytes_private':True,
        'not_passed':['unassisted_complete_human_playthrough','measured_1080p_60fps_stress',
                      'shipping_package','second_machine','demo_video','progress_pdf','whole_assignment3'],
        'git_commit_or_push':False}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'proofs':len(proofs),'protected':703,'closure':str(out)},indent=2))
