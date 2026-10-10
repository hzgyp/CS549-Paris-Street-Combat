"""Bounded edits of licensed field recordings; never replace the approved fire cue."""
import shutil,wave,json
from pathlib import Path
import numpy as np
from intake import ROOT,OUT,digest,save_json,row
from inspect_refs import load

RATE=48000
def write(p,x):
    assert np.all(np.isfinite(x)) and np.max(np.abs(x))<.98
    pcm=np.round(x*32767).astype('<i2')
    with wave.open(str(p),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())

def main():
    audio=OUT/'candidate_v1/Audio';assert not audio.exists(),'Preserve existing candidate'
    audio.mkdir(parents=True);edits=[];sources=json.loads((OUT/'intake/sources.json').read_text('utf-8'))
    for s in sources:assert s['status'].startswith('acquired') and digest(OUT/'intake'/s['local'])==s['sha256']
    decoded={s['name']:load(OUT/'decoded'/(s['name']+'.wav')) for s in sources}
    def cut(name,a,b,peak,lead=0):
        v=decoded[name][round(a*RATE):round(b*RATE)].copy();v-=np.mean(v)
        # Retain timbre and natural internal timing; bounded gain/fades only.
        gain=min(4.0,peak/max(np.max(np.abs(v)),1e-9));v*=gain
        fade=min(round(.012*RATE),len(v)//4);v[:48]*=np.linspace(0,1,48);v[-fade:]*=np.linspace(1,0,fade)
        v=np.concatenate([np.zeros(round(lead*RATE)),v]) if lead else v
        return v,dict(source=name,source_start=a,source_end=b,linear_gain=float(gain),leading_silence=lead,
                      processing='Mono48k decode, DC removal, <=4x gain, 1ms onset/12ms end fades; no pitch/time changes')
    def emit(name,source,a,b,peak,lead=0):
        v,e=cut(source,a,b,peak,lead);write(audio/(name+'.wav'),v);e.update(output=name+'.wav');edits.append(e);return v
    walking=[(.078,.42),(.66,1.05),(1.24,1.62),(1.78,2.17),(2.37,2.80),(2.99,3.43)]
    running=[(23.91,24.20),(24.33,24.62),(24.72,25.01),(25.12,25.43),(25.52,25.82),(26.35,26.64)]
    for i,(a,b) in enumerate(walking):
        emit('step_walk_'+chr(97+i),'boots_stone',a,b,.42)
        emit('step_slow_'+chr(97+i),'boots_stone',a,b,.30)
    for i,(a,b) in enumerate(running):emit('step_run_'+chr(97+i),'boots_rock_walk_run',a,b,.50)
    for i,(a,b) in enumerate([(.72,1.08),(2.48,2.84),(3.95,4.31)]):emit('crawl_'+chr(97+i),'coat',a,b,.20)
    emit('reload_handling','coat',1.22,1.62,.16)
    emit('reload_m1_open','m1_back',.135,.52,.34)
    emit('reload_m1_load','m1_reload',1.49,1.79,.34)
    emit('reload_m1_close','m1_forward',.205,.465,.38)
    emit('reload_k98_open','kar98',1.285,1.665,.34)
    emit('reload_k98_load','kar98',5.14,5.73,.30)
    emit('reload_k98_close','kar98',3.035,3.69,.38)
    emit('death','body_dirt',.35,1.53,.48,.65)
    left,le=cut('boots_stone',.078,.42,.30);right,re=cut('boots_stone',.66,1.05,.30)
    landing=np.zeros(max(len(left),round(.034*RATE)+len(right)))
    landing[:len(left)]+=left;landing[round(.034*RATE):round(.034*RATE)+len(right)]+=right
    write(audio/'land.wav',landing);edits.append(dict(output='land.wav',layers=[le,re],second_offset=.034,
        origin='Adapted two boot contacts for landing; not a dedicated jump landing recording'))
    fire=OUT/'rejected_avv3/Audio/fire.wav';shutil.copyfile(fire,audio/'fire.wav');assert digest(audio/'fire.wav')==digest(fire)
    rows=[]
    for p in sorted(audio.glob('*.wav')):
        x=load(p);rows.append(dict(**row(p,audio),seconds=len(x)/RATE,peak=float(np.max(np.abs(x))),rms=float(np.sqrt(np.mean(x*x))),clipped_samples=int(np.sum(np.abs(x)>=.999)),header_44_bytes=p.stat().st_size==44+len(x)*2))
    assert len(rows)==31 and all(r['clipped_samples']==0 and r['header_44_bytes'] for r in rows)
    credits='Recorded Foley candidate, 9 October2026. Manual acoustic review pending.\n\n'
    for s in sources:credits+=s['name']+' by '+s['author']+'\n'+s['page']+'\nCC0-1.0: https://creativecommons.org/publicdomain/zero/1.0/\nOfficial publicly published HQ MP3 reference; not the original uncompressed WAV.\n\n'
    credits+='Approved fire.wav retained byte-identically from AVv3 original synthesis. All other cues use adapted recordings. No human death voice. Landing is a two-contact boot adaptation; crawl uses coat rustle. No claim of an exact WWII uniform or sole recording.\n'
    (audio/'CREDITS.txt').write_text(credits,'utf-8')
    receipt=dict(status='recorded_foley_candidate_manual_review_pending',license='CC0-1.0 for downloaded references',sources=sources,
        edits=edits,files=rows,approved_fire_sha256=digest(fire),recording_hold=True,
        limitations=['Published lossy HQ MP3 references, decoded to PCM; not original WAV fidelity','Hard-ground Foley only, no material-specific map','Generic existing reload gesture retained; stage contact review remains human gate','No model auditory input; do not claim listening acceptance from metrics'])
    save_json(audio/'PROVENANCE.json',receipt)
    review=OUT/'listening';review.mkdir()
    def timeline(name,parts,length):
        x=np.zeros(round(length*RATE))
        for at,cue,gain in parts:
            data=load(audio/(cue+'.wav'))*gain;start=round(at*RATE);x[start:start+len(data)]+=data
        write(review/(name+'.wav'),x)
    timeline('01_walk',[(i*.55,'step_walk_'+chr(97+i%6),.72*.65) for i in range(12)],6.7)
    timeline('02_run',[(i*.35,'step_run_'+chr(97+i%6),.72*.80) for i in range(12)],4.3)
    timeline('03_slow',[(i*.85,'step_slow_'+chr(97+i),.72*.35) for i in range(6)],5.6)
    timeline('04_M1_reload',[(0,'reload_handling',.72*.35),(.14*4.133333,'reload_m1_open',.72*.55),(2.066667,'reload_m1_load',.72*.55),(.68*4.133333,'reload_m1_close',.72*.55)],4.7)
    timeline('05_K98_reload',[(0,'reload_handling',.72*.35),(.14*2.166667,'reload_k98_open',.72*.55),(1.083333,'reload_k98_load',.72*.55),(.68*2.166667,'reload_k98_close',.72*.55)],2.7)
    timeline('06_crawl',[(i*.63,'crawl_'+chr(97+i%3),.72*.32) for i in range(6)],3.8)
    timeline('07_body_impact',[(0,'death',.72*.65)],2.1)
    timeline('08_landing',[(0,'land',.72*.6)],.7)
    save_json(review/'MANIFEST.json',dict(scope='Constructed source listening examples, not a UE recording or video soundtrack',
        files=[row(p,review) for p in sorted(review.glob('*.wav'))],fire_protected=True,manual_acceptance='pending'))
    print(json.dumps(dict(audio_files=len(rows),approved_fire=digest(fire),source_licenses='CC0',clip_review='human pending',recording_hold=True)))

if __name__=='__main__':main()
