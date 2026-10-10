"""Review-only actual action excerpt; mandatory full mission remains separate."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tmp/g1-voice-audition-20261009/runtime'))
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'tmp/g1-demo-draft03-20261009'
FF=Path(r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
def main():
    a=json.loads((WORK/'actions_probe_v3/av_audit/admission.json').read_text());assert a['status']=='admitted_actions_actual_av_frames_and_native_input'
    dest=WORK/'actions_preview_v1';dest.mkdir();e=a['events'];start=round((e['step_intro']-1)*30)/30;end=round((e['pass_actions_pending_media_review']+.7)*30)/30;duration=end-start
    narr=json.loads((WORK/'narration_normalized_v1/NARRATION.json').read_text())['segments']
    stem=np.zeros((round(duration*48000),2),dtype=np.float32);windows=[]
    for name,at in [('opening',.15),('movement',e['step_prone']-start+.15)]:
        row=next(x for x in narr if x['id']==name);data,sr=sf.read(row['normalized_path'],dtype='float32');assert sr==48000
        i=round(at*sr);stem[i:i+len(data)]+=data[:,None];windows.append((at,at+len(data)/sr,row['text']))
    sf.write(dest/'AI_Michael.wav',stem,48000,subtype='PCM_24')
    def stamp(t):
        cs=round(t*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100);return f'{h}:{m:02}:{s:02}.{cs:02}'
    captions=[(0,duration,'AUTOMATED UE INPUT | A / MICHAEL AI VOICE | 1x | ACTION EXCERPT','Label')]
    captions += [(x,y,t,'Caption') for x,y,t in windows]
    for name,length,text in [('step_walk',2,'Walk'),('step_run',2,'Sprint'),('step_slow',2,'Slow walk'),('step_jump',2,'Jump and landing'),('step_crouch',2,'Crouch'),('step_continuous_turn',5,'Continuous turn with ordinary input'),('step_reload',8.8,'Standing reload: 2 / 16 to 8 / 10'),('step_shot',2.6,'Recorded M1 gunshot: 8 / 10 to 7 / 10')]:
        at=e[name]-start;captions.append((at,min(duration,at+length),text,'Caption'))
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow, Alignment, Encoding
Style: Caption,Segoe UI,34,&H00F4F0E5,&H00FFFFFF,&H90110F0B,&H90110F0B,0,0,0,0,100,100,0,0,420,420,28,3,6,0,2,1
Style: Label,Segoe UI,23,&H00D8C9A4,&H00FFFFFF,&H70100F0B,&H70100F0B,0,0,0,0,100,100,0,0,440,440,28,3,4,0,8,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    (dest/'captions.ass').write_text(header+'\n'.join(f'Dialogue: 0,{stamp(x)},{stamp(y)},{style},,0,0,0,,{text}' for x,y,text,style in captions)+'\n','utf-8-sig')
    duck='+'.join(f'between(t,{x-.1:.3f},{y+.1:.3f})' for x,y,_ in windows)
    filters=f"[0:v]trim=start_frame={round(start*30)}:end_frame={round(end*30)},setpts=PTS-STARTPTS,subtitles=captions.ass[v];[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,volume='if(gt({duck},0),0.8,1.8)':eval=frame[g];[g][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.95:level=0:latency=1[a]"
    cmd=[str(FF),'-hide_banner','-nostdin','-i',a['video'],'-i','AI_Michael.wav','-filter_complex',filters,'-map','[v]','-map','[a]','-c:v','libx264','-threads','4','-preset','fast','-crf','20','-pix_fmt','yuv420p','-r','30','-enc_time_base:v','1:30','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart','Paris_G1_Actions_Preview.mp4']
    with (dest/'render.log').open('w') as log:subprocess.run(cmd,cwd=dest,stdout=log,stderr=log,check=True)
    result=dict(status='actual_action_preview_not_complete_script03',duration=duration,start=start,end=end,source=a['video'],source_sha256=a['sha256'],voice='A / Michael / am_michael',audio='Captured game audio with separate disclosed AI stem; no replacement Foley',captions=captions,output_sha256=hashlib.sha256((dest/'Paris_G1_Actions_Preview.mp4').read_bytes()).hexdigest())
    (dest/'manifest.json').write_text(json.dumps(result,indent=2),'utf-8');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
