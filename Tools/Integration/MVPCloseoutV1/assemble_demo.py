"""Encode real viewport frames at recorded wall times; no simulation speed changes."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from PIL import Image
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/MVPCloseoutV1'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def srt_time(value):
    ms=round(value*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

def main():
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('stress');p.add_argument('--identity',default='demo_v1');a=p.parse_args()
    run=ROOT/'tmp/mvp-closeout-20261008'/a.run;stress=ROOT/'tmp/mvp-closeout-20261008'/a.stress
    r=json.loads((run/'result.json').read_text());audit=json.loads((run/'read_only_audit.json').read_text())
    load=json.loads((stress/'finite_stress_result.json').read_text())
    assert r['status']=='pass_three_scripted_integrated_rounds_human_gate_pending' and audit['rounds']==3
    frames=r['realtime_viewport_frames'];assert len(frames)>900 and len({f['file'] for f in frames})==len(frames)
    times=[f['wall_seconds'] for f in frames];assert all(b>a for a,b in zip(times,times[1:]))
    origin=times[0];duration=times[-1]-origin;assert 120<=duration<=180
    out=STORE/a.identity;assert not out.exists(),'Preserve occupied media identity';out.mkdir()
    concat=[];gaps=[]
    for i,f in enumerate(frames):
        path=(run/f['file']).resolve();assert path.parent==run.resolve()/'frames' and path.is_file()
        with Image.open(path) as im:assert im.size==(f['width'],f['height'])==(1920,1080)
        # ffconcat single quoting: paths are generated inside this task, never shell commands.
        concat.append("file '"+str(path).replace('\\','/').replace("'","'\\''")+"'")
        if i+1<len(frames):
            delta=times[i+1]-times[i];concat.append(f'duration {delta:.9f}')
            if delta>.5:gaps.append(dict(start=times[i]-origin,seconds=delta))
    (out/'frames.ffconcat').write_text('ffconcat version 1.0\n'+'\n'.join(concat)+'\n')
    stages={
      'native_ready_six_member_roster':'Six-person native G1 map. Accepted models and original rifle actions retained.',
      'original_mission_started':'Navigation + collision: cross bridge C with original UE movement, capsules and speeds.',
      'player_physically_crossed_bridge':'NPC behavior: regroup two Allies. Original 55 cm / 25 s far-bank gate.',
      'both_allies_original_55cm_25sec_far_bank_gate_pass':'Both Allies arrived. Advance to G1; scripted visible-target aim and original weapon transactions.',
      'native_won':'G1 captured. Checkpoint keeps actual health, ammunition and deaths.',
      'won_checkpoint_saved_original_resources':'Safe Won checkpoint saved. Next: load the original journal into a fresh world.',
      'fresh_world_won_resource_restore_verified':'Fresh-world checkpoint restore verified: health, ammunition and deaths match.',
      'original_fresh_roster_resources_verified':'Full restart verified: six initial actors and original resources restored.'}
    cues=[(0,'Animation, collision, navigation and NPC AI in one running G1 mission.')]
    for e in r['events']:
        if e.get('event') in stages and origin<=e.get('wall_seconds',-1)<=times[-1]:
            cues.append((e['wall_seconds']-origin,stages[e['event']]))
    for gap in gaps:
        cues.append((gap['start'],f"Capture / loading gap: {gap['seconds']:.2f} s. Last actual frame held; no simulated movement inserted."))
    last=f"Separate stress entry: {load['measured_total_combatants']} starting combatants, {load['average_fps']:.2f} FPS mean. "
    last+='60 FPS missed; 12 / 18 not run under the declared stop.' if load['status']=='stop_at_initial_level_performance_limit' else 'Higher-load results are not established by this recording.'
    cues.append((duration-12,last));cues.sort(key=lambda x:x[0])
    subs=[]
    for i,(start,label) in enumerate(cues):
        end=cues[i+1][0] if i+1<len(cues) else duration
        if end-start<.05:continue
        subs.append(f'{len(subs)+1}\n{srt_time(start)} --> {srt_time(end)}\n{label}\nScripted input | Actual wall time | Silent capture requested at 10 Hz; not an FPS benchmark\n')
    (out/'annotations.srt').write_text('\n'.join(subs),encoding='utf-8')
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();video=out/'Paris_Street_Combat_G1_RealTime_Demo.mp4'
    args=[ffmpeg,'-hide_banner','-nostdin','-f','concat','-safe','0','-i','frames.ffconcat',
        '-vf',"scale=1280:720,subtitles=annotations.srt:force_style='FontName=Arial,FontSize=16,Alignment=2,MarginV=58,Outline=1,BorderStyle=3,BackColour=&H90000000'",
        '-fps_mode','vfr','-c:v','libx264','-preset','medium','-crf','20','-threads','8','-pix_fmt','yuv420p','-movflags','+faststart',video.name]
    with (out/'encode.log').open('w') as log:
        proc=subprocess.run(args,cwd=out,stdout=log,stderr=subprocess.STDOUT)
    assert proc.returncode==0,'Preserve failed media entry'
    count,actual_duration=imageio_ffmpeg.count_frames_and_secs(str(video));assert 120<=actual_duration<=180 and abs(actual_duration-duration)<.5
    qa=[]
    for i,t in enumerate([2,duration*.25,duration*.5,duration*.75,duration-2]):
        path=out/f'review_{i}.png'
        subprocess.run([ffmpeg,'-hide_banner','-nostdin','-ss',str(t),'-i',str(video),'-frames:v','1',str(path)],check=True,capture_output=True)
        qa.append(dict(seconds=t,file=path.name))
    launch=json.loads((run/'launch.json').read_text())
    record=dict(status='encoded_pending_visual_review',source_run=a.run,source_build=launch['build'],source_binary_sha256=launch['binary_sha256'],stress_run=a.stress,actual_duration_seconds=actual_duration,
        source_wall_span_seconds=duration,encoded_frames=count,source_frames=len(frames),capture_gaps=gaps,visual_review_frames=qa,
        simulation_speed='unchanged; recorded wall-time intervals',audio='silent',capture_nominal_hz=10,
        video_sha256=sha(video),input_receipt_sha256={str(run/'result.json'):sha(run/'result.json'),str(stress/'finite_stress_result.json'):sha(stress/'finite_stress_result.json')},
        scope='Real running software with scripted player input. Not human play, natural two-sided combat, performance or complete course acceptance.')
    (out/'media_receipt.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))

if __name__=='__main__':main()
