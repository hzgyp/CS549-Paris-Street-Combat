"""Decode the final MP4 and sample actual frame/audio timeline; no UI input."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tmp/g1-voice-audition-20261009/runtime'))
import numpy as np
FF=Path(r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
DEST=ROOT/'Assets/LocalShared/Deliverables/Assignment3/DemoDraft03_20261009'
def run(args):return subprocess.run([str(FF),'-hide_banner','-nostdin']+args,capture_output=True,check=True)
def main():
    video=DEST/'Paris_G1_MVP_Draft_03.mp4';timeline=json.loads((DEST/'TIMELINE.json').read_text())
    assert timeline['status']=='composed_pending_final_decode_and_frame_review'
    assert hashlib.sha256(video.read_bytes()).hexdigest()==timeline['output_sha256']
    audit=DEST/'QA';audit.mkdir()
    r=run(['-v','info','-xerror','-i',str(video),'-map','0:v:0','-map','0:a:0','-f','null','-'])
    (audit/'decode.log').write_bytes(r.stderr)
    text=r.stderr.decode('utf-8','replace');assert '1920x1080' in text and '30 fps' in text
    frames=int(re.findall(r'frame=\s*(\d+)',text)[-1]);assert frames==round(timeline['duration']*30),(frames,timeline['duration'])
    pcm=run(['-v','error','-i',str(video),'-map','0:a:0','-ac','2','-ar','48000','-f','f32le','-']).stdout
    x=np.frombuffer(pcm,'<f4').reshape(-1,2);peak=float(np.max(np.abs(x)));assert 0<peak<.99
    assert abs(len(x)/48000-timeline['duration'])<.1
    stems=[]
    for w in timeline['narration']:
        chunk=x[round(w['start']*48000):round(w['end']*48000)].astype(np.float64)
        rms=float(np.sqrt(np.mean(chunk**2)));assert rms>.001
        stems.append(dict(id=w['id'],start=w['start'],end=w['end'],mixed_window_rms=rms))
    # Sample each event requiring visible actual evidence, using admitted source times.
    clips=timeline['clips'];work=ROOT/'tmp/g1-demo-draft03-20261009'
    source_events={k:json.loads((work/k/'av_audit/admission.json').read_text())['events'] for k in ['actions_probe_v3','victory_v6','defeat_v5']}
    selected=[('opening',.6),('squad',clips[1]['output_start']+source_events['victory_v6']['step_squad_observe']-clips[1]['start']+.5),('save_prompt',clips[1]['output_start']+source_events['victory_v6']['step_prompt']-clips[1]['start']+.5),('saved',clips[1]['output_start']+source_events['victory_v6']['step_saved']-clips[1]['start']+1),('changed_ammo',clips[1]['output_start']+source_events['victory_v6']['step_changed_ammo']-clips[1]['start']+.5),('f9_wait',clips[1]['output_start']+source_events['victory_v6']['step_load_wait']-clips[1]['start']+2),('restore_early',clips[1]['output_start']+source_events['victory_v6']['step_corpse_observe']-clips[1]['start']+.1),('restore_3',clips[1]['output_start']+source_events['victory_v6']['step_corpse_observe']-clips[1]['start']+3),('defeat_intro',clips[2]['output_start']+1),('damage',clips[3]['output_start']+source_events['defeat_v5']['actual_player_damage_100.0_to_65.0']-clips[3]['start']+.5),('lost',clips[3]['output_start']+source_events['defeat_v5']['step_lost_hold']-clips[3]['start']+1),('f6_wait',clips[3]['output_start']+source_events['defeat_v5']['step_restart_wait']-clips[3]['start']+2),('new_ready',clips[3]['output_start']+source_events['defeat_v5']['step_fresh_ready']-clips[3]['start']+1),('pending',timeline['duration']-3)]
    for name,t in selected:run(['-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-q:v','2','-update','1',str(audit/(name+'.jpg'))])
    loud=run(['-v','info','-i',str(video),'-map','0:a:0','-af','loudnorm=I=-20:TP=-3:LRA=11:print_format=json','-f','null','-'])
    (audit/'loudness.log').write_bytes(loud.stderr)
    result=dict(status='final_decode_audio_numeric_pass_visual_pending',video=str(video),duration=frames/30,frames=frames,width=1920,height=1080,frame_rate=30,sha256=timeline['output_sha256'],bytes=video.stat().st_size,audio_peak=peak,audio_rms=float(np.sqrt(np.mean(x.astype(np.float64)**2))),voice_windows=stems,frames_to_review=[dict(name=n,seconds=t,path=str(audit/(n+'.jpg'))) for n,t in selected],limit='Numeric media/AV and actual frame review do not establish subjective sound quality, manual play, FPS, stress, teammate or course acceptance.')
    (audit/'result.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps({k:v for k,v in result.items() if k!='frames_to_review'},indent=2),flush=True)
if __name__=='__main__':main()
