"""Final independent identities/history/no-video check; manual review stays pending."""
import ast,json
from datetime import datetime
from intake import ROOT,OUT,digest,save_json,row

selector=json.loads((ROOT/'Docs/Development/CURRENT_AUDIO_REVIEW.json').read_text('utf-8'))
delivery=json.loads((OUT/'delivery.json').read_text('utf-8'))
trial=ROOT/'tmp/Playtest-G1-Foley-20261009'
for r in delivery['trial_files']:
    p=trial/r['path'];assert p.stat().st_size==r['size_bytes'] and digest(p)==r['sha256']
assert len([p for p in trial.rglob('*') if p.is_file()])==91
source=ROOT/selector['source_snapshot'];manifest=ROOT/selector['source_manifest']
assert digest(manifest)==selector['source_manifest_sha256']
for r in json.loads(manifest.read_text('utf-8'))['files']:assert digest(source/r['path'])==r['sha256']
proof=json.loads((ROOT/'tmp/g1-av-revision-20261009/protection_after.json').read_text('utf-8'))
assert proof['status']=='pass_exact_protection'
history={
 'Assets/LocalShared/Deliverables/Assignment3/DemoDraft02_20261009/Paris_G1_MVP_Draft_02.mp4':'286e8c89544b09ee58618e75a6bcd55a9125c91a6e03d0bf5e5f200d742f4268',
 'tmp/g1-demo-draft02-20261009/raw/2026-10-09 19-50-56.mkv':'118f5d9076e8bec4ec071a69be0cea0c43cafeb979c5ae33c18400dd17e196d4',
 'tmp/g1-demo-draft02-20261009/raw/2026-10-09 19-58-27.mkv':'fcb6e4e6228f34a668665886175c3ee2eec2b544d8e6200d76ff79d7567409f6'}
for path,sha in history.items():assert digest(ROOT/path)==sha
assert not list(OUT.rglob('*.mkv')) and not list(OUT.rglob('*.mp4'))
failed=OUT/'delivery_launcher_failure';case_files=[row(p,OUT) for p in sorted(failed.iterdir()) if p.is_file()]
references=json.loads((OUT/'old_footage_review/turn.json').read_text('utf-8'))
supplement=dict(recording_hold=True,unchanged_history=[row(ROOT/p,ROOT) for p in history],
    turn_witness=references,private_failure_files=case_files,
    failure_verifier=row(OUT/'checks/verify_generation_order_v1_FAILED.py',OUT),
    intake_negative=row(OUT/'intake/intake_parser_v1_failed.json',OUT),
    exact_recovery='tmp/g1-recorded-foley-20261009/delivery_launcher_failure/recovery.json')
save_json(ROOT/'Failures/MI015-20261009-audio-realism-turn/ADDITIONAL_EVIDENCE.json',supplement)
for p in (ROOT/'Tools/Integration/G1RecordedFoleyV1').glob('*.py'):ast.parse(p.read_text('utf-8'),filename=str(p))
receipt=dict(status='ready_for_manual_acoustic_review',at=datetime.now().astimezone().isoformat(),
    trial_files=91,source_files=42,game_sha256=selector['game_sha256'],approved_fire_sha256=selector['approved_fire_sha256'],
    scoped_native_audio_checks='checks/verification.json',protection=proof,
    parent_archive_check='admission.json',history_unchanged=True,no_new_mkv_mp4=True,recording_hold=True,
    human_acceptance='PENDING',remaining=selector['remaining'],publication='None')
save_json(OUT/'completion.json',receipt)
print(json.dumps(dict(status=receipt['status'],trial_files=91,source_files=42,protection='pass_exact',history='unchanged',recording='HOLD'),indent=2))
