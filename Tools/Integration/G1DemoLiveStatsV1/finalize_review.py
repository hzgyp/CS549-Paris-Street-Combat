"""Record actual completed local image review; never changes game/media bytes."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'Assets/LocalShared/Deliverables/Assignment3/DemoDraft04_20261010'
WORK=ROOT/'tmp/g1-demo-draft04-20261010'
def main():
    qa=json.loads((DEST/'QA/result.json').read_text('utf-8'))
    timeline=json.loads((DEST/'TIMELINE.json').read_text('utf-8'))
    assert qa['status']=='final_decode_audio_numeric_pass_visual_pending'
    assert timeline['status']=='composed_pending_final_decode_and_frame_review'
    assert hashlib.sha256(Path(qa['video']).read_bytes()).hexdigest()==qa['sha256']==timeline['output_sha256']
    assert len(qa['frames_to_review'])==14 and all(Path(x['path']).is_file() for x in qa['frames_to_review'])
    source=json.loads((WORK/'recording_stats_v1/source_verification.json').read_text('utf-8'))
    guards=json.loads((ROOT/'tmp/g1-demo-draft03-20261009/protection_video04_after.json').read_text('utf-8'))
    assert len(source['checks'])==178 and all(x['exact'] for x in source['checks'])
    assert guards['status']=='protected_source_user_files_game_exact'
    assert len(guards['checks'])==45 and all(x['exact'] for x in guards['checks'])
    cases=[]
    for name in ['actions_panel_v1','victory_panel_v1','defeat_panel_v1']:
        a=json.loads((WORK/name/'av_audit/admission.json').read_text('utf-8'))
        assert a['status'].startswith('admitted_')
        cases.append(dict(case=name,status=a['status'],video=a['video'],sha256=a['sha256']))
    reviewed_at=datetime.now(timezone.utc).isoformat()
    qa['status']='local_media_decode_audio_and_14_frame_review_pass'
    qa['visual_review']=dict(reviewed_at=reviewed_at,reviewer='Codex actual image inspection',all_14_reviewed=True,
        findings=['Readable English captions/live panel; minimap, health, ammo and save prompts intact.',
                  'Real damage, Lost, F6 waiting and Ready visible; damage through restart continuous at1x.',
                  'Restored corpses down; post-load texture warning and environment loading retained.',
                  'Live counters change; no historical performance numbers added in captions.'],human_review='Pending')
    timeline.update(status='local_review_draft_complete_human_review_pending',actual_video_duration=qa['duration'],actual_video_frames=qa['frames'],qa_receipt='QA/result.json')
    receipt=dict(status='recording04_local_review_complete',reviewed_at=reviewed_at,video=qa['video'],sha256=qa['sha256'],duration=qa['duration'],bytes=qa['bytes'],takes=cases,
        diagnostic_game_sha256='aa11d14dde3ff346089a9fbb70647bfd84e220ec5cc70713fd5bd57fd2757a78',normal_game_sha256=guards['normal_game_sha256'],source_closure_checks=178,protected_source_user_checks=45,
        human_video_review='Pending',public_upload='Not performed',git_push='Not performed',report='10 October report rejected; rewrite deferred for joint discussion')
    for path,value in [('QA/result.json',qa),('TIMELINE.json',timeline),('RECEIPT.json',receipt)]:
        (DEST/path).write_text(json.dumps(value,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='takes'},indent=2))
if __name__=='__main__':main()
