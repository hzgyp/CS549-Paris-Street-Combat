"""Verify protected parent closures and the independent concrete delivery."""
import ast,json
from pathlib import Path
from common import ROOT,OUT,PARENT,digest,save,row
def main():
    frozen=json.loads((OUT/'freeze.json').read_text('utf-8-sig'));delivery=json.loads((OUT/'delivery.json').read_text('utf-8-sig'));selector=delivery['selector']
    source=ROOT/frozen['parent']['source_snapshot']
    for r in frozen['source_files']:assert digest(source/r['path'])==r['sha256']
    for r in frozen['parent_audio']:assert digest(PARENT/'candidate_v1/Audio'/r['path'])==r['sha256']
    archive=Path(frozen['reuse_archive'])
    for r in frozen['archive_files']:assert digest(archive/r['path'])==r['sha256']
    for r in frozen['protected_files']:assert digest(ROOT/r['path'])==r['sha256']
    old_guard=json.loads((ROOT/'tmp/g1-av-revision-20261009/protection_after.json').read_text('utf-8-sig'))
    assert all(old_guard[k] for k in ['source758','protected703','native359','baseline40','old_authoring40','new_source42','old_game']) and old_guard['user_files']==3
    trial=(ROOT/selector['playable_entry']).parent
    for r in delivery['trial_files']:assert digest(trial/r['path'])==r['sha256']
    cmd=trial/'PLAY_G1_REVISION.cmd';assert cmd.stat().st_nlink==1 and all(t not in cmd.read_text('utf-8') for t in ['ParisUXTest','ParisAVAuditOut','NoSound','UnfocusedVolumeMultiplier'])
    manifest=ROOT/selector['source_manifest'];assert digest(manifest)==selector['source_manifest_sha256']
    public=ROOT/selector['source_snapshot'];files=json.loads(manifest.read_text('utf-8-sig'))['files'];assert len(files)==42
    for r in files:assert digest(public/r['path'])==r['sha256']
    for p in Path(__file__).parent.glob('*.py'):ast.parse(p.read_text('utf-8-sig'),filename=str(p))
    assert not any(p.suffix.lower() in ['.mkv','.mp4'] for p in OUT.rglob('*') if p.is_file())
    history=[('Assets/LocalShared/Deliverables/Assignment3/DemoDraft02_20261009/Paris_G1_MVP_Draft_02.mp4','286e8c89544b09ee58618e75a6bcd55a9125c91a6e03d0bf5e5f200d742f4268'),
      ('tmp/g1-demo-draft02-20261009/raw/2026-10-09 19-50-56.mkv','118f5d9076e8bec4ec071a69be0cea0c43cafeb979c5ae33c18400dd17e196d4'),
      ('tmp/g1-demo-draft02-20261009/raw/2026-10-09 19-58-27.mkv','fcb6e4e6228f34a668665886175c3ee2eec2b544d8e6200d76ff79d7567409f6')]
    for path,h in history:assert digest(ROOT/path)==h
    save(ROOT/'Failures/MI016-20261009-player-foot-contact-jump/ADDITIONAL_EVIDENCE.json',dict(import_collision_failure=row(OUT/'freeze_intake_v1_import_failed.py',OUT),
       import_failure_scope='Guard intake failed before freeze or protected data mutation; corrected by explicitly named importlib guard module',checks='tmp/g1-foot-contact-audio-v2-20261009/checks_solo/verification.json',
       rejected_contact_figure='tmp/g1-foot-contact-audio-v2-20261009/checks/actions/foot_contact_plot.png',
       retained_overlap_verifier=row(OUT/'verify_v1_overlap_failed.py',OUT),missing_plot_dependency=row(OUT/'plot_v1_missing_dependency_failed.py',OUT),
       retained_absolute_minimum_verifier=row(OUT/'verify_v2_absolute_minimum_failed.py',OUT),
       retained_overfiltered_descent_verifier=row(OUT/'verify_v3_overfiltered_descent_failed.py',OUT),
       retained_short_window_verifier=row(OUT/'verify_v4_short_regime_window_failed.py',OUT),
       final_figure='tmp/g1-foot-contact-audio-v2-20261009/checks_solo/actions/foot_contact_plot.png',recording_hold=True))
    save(OUT/'completion.json',dict(status='ready_for_manual_revised_audio_review',game_sha256=selector['game_sha256'],trial_files=len(delivery['trial_files']),source_files=42,
      protected703=True,parent42=True,parent31audio=True,parent47archive=True,original_source_native_hud_save_closure=old_guard,old_raw_video_exact=True,no_new_screen_recording=True,
      human_acceptance='PENDING for revised feet/jump/M1 report',recording_hold=True,k98_live_fire_gap=True,publication='None'))
    print(json.dumps(dict(status='ready_for_manual_revised_audio_review',files=len(delivery['trial_files']),all_parent_guards=True,recording='HOLD')))
if __name__=='__main__':main()
