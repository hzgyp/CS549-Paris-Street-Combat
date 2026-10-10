"""Compose admitted actual takes at 1x with English captions and separate A voice."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'tmp/g1-demo-draft03-20261009'
sys.path.insert(0,str(ROOT/'tmp/g1-voice-audition-20261009/runtime'))
import numpy as np
import soundfile as sf
FF=Path(r'C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
DEST=ROOT/'Assets/LocalShared/Deliverables/Assignment3/DemoDraft03_20261009'
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def ass_time(t):
    c=round(t*100);h,c=divmod(c,360000);m,c=divmod(c,6000);s,c=divmod(c,100)
    return f'{h}:{m:02}:{s:02}.{c:02}'
def srt_time(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def main():
    assert not DEST.exists(),'Retain previous deliverable identity';DEST.mkdir(parents=True)
    data={}
    for case,status in [('actions_probe_v3','admitted_actions_actual_av_frames_and_native_input'),('victory_v6','admitted_victory_save_restore_actual_av_frames_and_native_input'),('defeat_v5','admitted_genuine_defeat_restart_actual_av_frames_and_native_input')]:
        a=json.loads((WORK/case/'av_audit/admission.json').read_text());assert a['status']==status
        assert sha(a['video'])==a['sha256'];data[case]=a
    ae=data['actions_probe_v3']['events'];ve=data['victory_v6']['events'];de=data['defeat_v5']['events']
    def frame(t):return round(t*30)/30
    clips=[]
    def clip(case,start,end,name,cut):
        start,end=frame(start),frame(end);assert start<end
        offset=sum(x['duration'] for x in clips)
        clips.append(dict(case=case,source=data[case]['video'],source_sha256=data[case]['sha256'],start=start,end=end,duration=end-start,output_start=offset,name=name,cut_disclosure=cut))
        return offset,start,end
    ao,astart,_=clip('actions_probe_v3',ae['step_intro']-1,ae['pass_actions_pending_media_review']+.7,'Actions and collision','Separate action run; complete continuous turns/reload')
    vo,vstart,_=clip('victory_v6',ve['step_bridge']-.2,ve['pass_victory_save_restore_pending_media_review']+.8,'Bridge C and G1','New mission run; repeated Ready and standing reload omitted')
    do,dstart,dend=clip('defeat_v5',de['step_intro']-1,de['step_defeat_approach']+.8,'Fresh defeat run','Separate fresh mission')
    co,cstart,cend=clip('defeat_v5',de['actual_player_damage_100.0_to_65.0']-2,de['pass_genuine_enemy_defeat_restart_pending_media_review']+.8,'Genuine damage, Lost, F6 and Ready','Approach cut before first damage; subsequent chain continuous')
    eo,estart,_=clip('defeat_v5',cend,cend+7.5,'Remaining work','Continuous idle Ready tail from same take')
    duration=sum(x['duration'] for x in clips);assert 120<=duration<=180,duration
    assert cstart<de['actual_player_damage_100.0_to_65.0']<de['step_lost_hold']<de['step_restart_wait']<de['step_fresh_ready']<cend
    assert vstart<ve['normal_combat_input']<ve['step_saved']<ve['step_load_wait']<ve['step_corpse_observe']<clips[1]['end']
    def at(case,event):
        if case=='a':return ao+ae[event]-astart
        if case=='v':return vo+ve[event]-vstart
        return co+de[event]-cstart
    narr=json.loads((WORK/'narration_normalized_v1/NARRATION.json').read_text())['segments']
    schedule=[('opening',.15),('movement',at('a','step_prone')+.15),('navigation',vo+.2),('combat',at('v','normal_combat_input')-5.3),('checkpoint',at('v','step_corpse_framing')+1),('restore',at('v','step_load_wait')+.8),('defeat',do+.1),('ending',eo+.2)]
    stem=np.zeros((round(duration*48000),2),np.float32);windows=[]
    for name,t in schedule:
        row=next(x for x in narr if x['id']==name);audio,sr=sf.read(row['normalized_path'],dtype='float32');assert sr==48000
        end=t+len(audio)/sr;assert 0<=t<end<=duration
        i=round(t*sr);stem[i:i+len(audio)]+=audio[:,None]
        windows.append(dict(id=name,start=t,end=end,text=row['text'],stem=row['normalized_path'],sha256=sha(row['normalized_path'])))
    for a,b in zip(sorted(windows,key=lambda x:x['start']),sorted(windows,key=lambda x:x['start'])[1:]):assert a['end']<=b['start']
    sf.write(DEST/'AI_Michael.wav',stem,48000,subtype='PCM_24')
    captions=[]
    def cap(x,y,text,style='Caption'):
        assert 0<=x<y<=duration,(x,y,text);captions.append(dict(start=x,end=y,text=text,style=style))
    cap(0,duration,'AUTOMATED UE INPUT  |  A / MICHAEL AI VOICE  |  1x', 'Label')
    cap(0,6.5,'Paris Street Combat  |  G1 bridgehead MVP','Title')
    for w in windows:
        cap(w['start'],w['end'],w['text'])
    # Short event captions use actual event times; leave original game cues clear.
    for event,length,text in [('step_crawl',4,'Prone clearance: rubble blocks forward travel'),('step_walk',2,'Walk'),('step_run',2,'Sprint'),('step_slow',2,'Slow walk'),('step_jump',2,'Jump and landing'),('step_crouch',2,'Crouch'),('step_continuous_turn',5,'Continuous input turn: no camera snap'),('step_reload',8.8,'Standing reload: 2 / 16 to 8 / 10'),('step_shot',2.6,'Recorded M1 shot: 8 / 10 to 7 / 10')]:
        t=at('a',event)
        if event=='step_crawl':t=max(t,windows[1]['end']+.1);length=max(.2,at('a','step_rise')-t)
        cap(t,min(vo,t+length),text)
    cap(vo,vo+3,'New mission run: bridge C to G1','Section')
    cap(at('v','step_squad_observe'),at('v','step_squad_turn_forward'),'Both Allies follow along the bridge')
    cap(at('v','normal_combat_input')+.1,at('v','step_g1'),'NPC pursuit; finite ammo and original reload')
    cap(at('v','step_prompt'),at('v','step_saved'),'Stop inside the gold circle; press E to save')
    cap(at('v','step_saved'),at('v','step_safe_look'),'Saved: 7 loaded / 2 reserve / 100 health')
    cap(at('v','step_changed_ammo'),at('v','step_load_wait'),'One later shot: 7 to 6 loaded; no re-save')
    cap(at('v','step_corpse_observe'),do,'F9 restores 7 / 2 and 100 health; corpses stay down')
    cap(at('v','step_load_wait'),at('v','step_corpse_observe'),'F9: actual reload interval retained','Section')
    cap(do,co,'Separate fresh run: defeat and restart','Section')
    cap(co,at('d','step_lost_hold'),'Approach cut before first hit; real enemy damage')
    cap(at('d','step_lost_hold'),at('d','step_restart_wait'),'Health 0: MISSION LOST; no return fire')
    cap(at('d','step_restart_wait'),at('d','step_fresh_ready'),'F6: actual restart interval retained')
    cap(at('d','step_fresh_ready'),eo,'Fresh Ready: 100 health / 2 + 16 ammo / 2 Allies / 3 guards')
    cap(eo,duration,'Current build stress test and teammate validation: PENDING','Section')
    header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, MarginL, MarginR, MarginV, BorderStyle, Outline, Shadow, Alignment, Encoding
Style: Caption,Segoe UI,34,&H00F4F0E5,&H00FFFFFF,&H90110F0B,&H90110F0B,0,0,0,0,100,100,0,0,420,420,28,3,6,0,2,1
Style: Label,Segoe UI,23,&H00D8C9A4,&H00FFFFFF,&H70100F0B,&H70100F0B,0,0,0,0,100,100,0,0,440,440,20,3,4,0,8,1
Style: Section,Segoe UI,28,&H00D8C9A4,&H00FFFFFF,&H70100F0B,&H70100F0B,0,0,0,0,100,100,0,0,440,440,57,3,4,0,8,1
Style: Title,Segoe UI,38,&H00F4F0E5,&H00FFFFFF,&H70100F0B,&H70100F0B,1,0,0,0,100,100,0,0,440,440,57,3,5,0,8,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    (DEST/'English.ass').write_text(header+'\n'.join(f"Dialogue: 0,{ass_time(x['start'])},{ass_time(x['end'])},{x['style']},,0,0,0,,{x['text']}" for x in captions)+'\n','utf-8-sig')
    # Include readable disclosures in the editable sidecar, including overlaps.
    (DEST/'English.srt').write_text('\n\n'.join(f"{i+1}\n{srt_time(x['start'])} --> {srt_time(x['end'])}\n{x['text']}" for i,x in enumerate(sorted(captions,key=lambda x:(x['start'],x['end']))))+'\n','utf-8')
    filters=[];inputs=[];pairs=[]
    for i,c in enumerate(clips):
        inputs+=['-ss',str(c['start']),'-t',str(c['duration']),'-i',c['source']]
        filters += [f'[{i}:v]trim=duration={c["duration"]},setpts=PTS-STARTPTS,setsar=1[v{i}]',f'[{i}:a]atrim=duration={c["duration"]},asetpts=PTS-STARTPTS,aresample=48000[a{i}]']
        pairs.append(f'[v{i}][a{i}]')
    filters.append(''.join(pairs)+f'concat=n={len(clips)}:v=1:a=1[rawv][rawa]')
    filters.append('[rawv]subtitles=English.ass[v]')
    duck='+'.join(f'between(t,{max(0,w["start"]-.1):.3f},{w["end"]+.1:.3f})' for w in windows)
    filters.append(f"[rawa]volume='if(gt({duck},0),0.8,1.8)':eval=frame[g]")
    filters.append(f'[g][{len(clips)}:a]amix=inputs=2:normalize=0,alimiter=limit=0.95:level=0:latency=1[a]')
    (DEST/'filter.txt').write_text(';\n'.join(filters),'utf-8')
    timeline=dict(status='composing_actual_review',duration=duration,clips=clips,narration=windows,captions=captions,voice='Selected A / Michael / am_michael stock AI voice',audio='Captured original game audio; narration is separate and disclosed. No replacement Foley/music.',speed='1x; explicit separate runs and one pre-damage travel cut',selected_normal_game_sha256='53ab36d9da1975a2f8e1109fcf6745cc40e96d371fc89fbfa009139b91950aec',current_build_stress='Pending, no old measurements reused',human_review='Pending')
    (DEST/'TIMELINE.json').write_text(json.dumps(timeline,indent=2)+'\n','utf-8');print(json.dumps(dict(duration=duration,clips=clips,narration=windows)),flush=True)
    video=DEST/'Paris_G1_MVP_Draft_03.mp4'
    command=[str(FF),'-hide_banner','-nostdin']+inputs+['-i','AI_Michael.wav','-filter_complex_script','filter.txt','-map','[v]','-map','[a]','-c:v','libx264','-threads','4','-preset','fast','-crf','20','-pix_fmt','yuv420p','-r','30','-enc_time_base:v','1:30','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-movflags','+faststart',video.name]
    with (DEST/'render.log').open('w') as log:subprocess.run(command,cwd=DEST,stdout=log,stderr=log,check=True)
    timeline['status']='composed_pending_final_decode_and_frame_review';timeline['output_sha256']=sha(video)
    (DEST/'TIMELINE.json').write_text(json.dumps(timeline,indent=2)+'\n','utf-8');print(json.dumps(dict(status=timeline['status'],video=str(video),sha256=timeline['output_sha256'])),flush=True)
if __name__=='__main__':main()
