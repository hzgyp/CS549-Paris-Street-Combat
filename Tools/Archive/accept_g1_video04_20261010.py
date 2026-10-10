"""Record the user's final-video approval and completed recording cleanup."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'Assets/LocalShared/Deliverables/Assignment3/DemoDraft04_20261010'
RET=ROOT/'tmp/g1-video-retirement-20261010'
def read(path):return json.loads(path.read_text('utf-8-sig'))
def save(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n','utf-8')
def main():
    plan=read(RET/'MANIFEST.json');result=read(RET/'RESULT.json')
    assert result['status']=='completed_only_approved_game_video_retained'
    video=ROOT/plan['keep']['path']
    assert hashlib.sha256(video.read_bytes()).hexdigest()==plan['keep']['sha256']
    assert all(not (ROOT/x['path']).exists() for x in plan['delete'])
    assert len((RET/'DELETED.jsonl').read_text('utf-8-sig').splitlines())==24
    guards=read(ROOT/'tmp/g1-demo-draft03-20261009/protection_video_retirement_after_20261010.json')
    assert len(guards['checks'])==45 and all(x['exact'] for x in guards['checks'])
    approved=dict(status='pass_human_review',date='2026-10-10',recorded_at=datetime.now(timezone.utc).isoformat(),
        authorization='User: 视频没问题，就保留这个一个完整视频，其他录制的可以删除',
        sha256=plan['keep']['sha256'],scope='Final video04 approved; does not approve rejected report or public hosting/course submission')
    retirement=dict(status='deleted_by_explicit_user_authorization',date='2026-10-10',
        manifest='tmp/g1-video-retirement-20261010/MANIFEST.json',result='tmp/g1-video-retirement-20261010/RESULT.json',
        original_recording_bytes_retained=False,nonvideo_evidence_retained=True)
    for name in ['RECEIPT.json','TIMELINE.json','QA/result.json']:
        path=DEST/name;value=read(path)
        value['human_video_review']=approved
        value['recording_retirement']=retirement
        if name=='TIMELINE.json':value.update(status='human_approved_final_video',human_review='Pass by user10October2026')
        if name=='RECEIPT.json':
            value['status']='recording04_human_approved_final_video'
            for take in value['takes']:take['current_raw_availability']='Deleted by later user authorization; hashes/logs/screenshots retained'
        save(path,value)
    selector=ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json';value=read(selector)
    value['approved_demo_video']=dict(**approved,path=plan['keep']['path'],duration_seconds=158.23333333333332,public_url=None)
    value['remaining_gates']=['public video link/reviewer access' if x=='video' else x for x in value['remaining_gates'] if x!='natural-turn recording correction']
    save(selector,value)
    save(RET/'APPROVAL.json',approved)
    notice='# Video retirement —10 October2026\n\nUser approves final video04 and explicitly permits deletion of other game recordings.\nRelevant original video bytes are deleted, not recoverable from an archive. Historical\nhashes/receipts/source/logs/screenshots remain evidence; old statements that raw video\nis retained are superseded only for entries in the frozen cleanup inventory.\n\nSee Docs/Development/G1_VIDEO_RETIREMENT_20261010_ZH.md and private\ntmp/g1-video-retirement-20261010/MANIFEST.json / RESULT.json.\nFinal approved videoSHA80481952 remains; failure analysis remains valid.\n'
    for case in ['MI011-20261008-window-recording-content','MI014-20261009-checkpoint-death-audio',
                 'MI015-20261009-audio-realism-turn','MI017-20261010-demo-input','MI018-20261010-native-stat-placement']:
        (ROOT/'Failures'/case/'VIDEO_RETIREMENT_20261010.md').write_text(notice,'utf-8')
    for folder in ['DemoDraft20261009','DemoDraft02_20261009','DemoDraft03_20261009']:
        (DEST.parent/folder/'VIDEO_RETIRED_20261010.md').write_text(notice,'utf-8')
    print(json.dumps(dict(status='human_approval_and_retirement_recorded',deleted_files=result['deleted_files'],released_bytes=result['observed_free_increase'],approved_video=str(video)),ensure_ascii=False))
if __name__=='__main__':main()
