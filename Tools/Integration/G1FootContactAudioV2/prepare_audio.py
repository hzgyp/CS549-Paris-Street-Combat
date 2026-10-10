"""Keep reviewed Foley; add recorded takeoff and a bounded first M1 live shot."""
import json,shutil,wave
import numpy as np
from common import ROOT,OUT,PARENT,digest,save,row
RATE=48000
def load(p):
    with wave.open(str(p),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(RATE,1,2)
        return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
def write(p,x):
    assert np.all(np.isfinite(x)) and np.abs(x).max()<.98
    with wave.open(str(p),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(np.round(x*32767).astype('<i2').tobytes())
def main():
    audio=OUT/'candidate_v1/Audio';assert not audio.exists(),'Preserve occupied audio identity'
    shutil.copytree(PARENT/'candidate_v1/Audio',audio)
    original=json.loads((audio/'PROVENANCE.json').read_text('utf-8-sig'))
    source=json.loads((OUT/'intake/source.json').read_text('utf-8-sig'))
    edits=[]
    def cut(p,a,b,peak):
        x=load(p)[round(a*RATE):round(b*RATE)].copy();x-=x.mean();gain=min(4,peak/max(np.abs(x).max(),1e-9));x*=gain
        x[:48]*=np.linspace(0,1,48);n=min(576,len(x)//4);x[-n:]*=np.linspace(1,0,n)
        return x,dict(source=str(p.relative_to(ROOT)),start=a,end=b,linear_gain=float(gain),processing='Mono48k PCM, DC removal, bounded gain, 1ms/12ms fades; no pitch/time change')
    shot,e=cut(OUT/'intake/m1_live_fire.wav',.195,.78,.60)
    write(audio/'fire_m1.wav',shot);e.update(output='fire_m1.wav',page=source['page'],license='CC0-1.0',description='First of eight live shots; no empty-clip ping added; indoor room tail retained');edits.append(e)
    sole,se=cut(PARENT/'decoded/boots_stone.wav',.205,.420,.20)
    cloth,ce=cut(PARENT/'decoded/coat.wav',.72,1.05,.14)
    jump=np.zeros(max(len(sole),len(cloth)));jump[:len(sole)]+=sole;jump[:len(cloth)]+=cloth
    write(audio/'jump.wav',jump);edits.append(dict(output='jump.wav',layers=[se,ce],description='Recorded boot release/scuff and cloth adaptation for takeoff, not a dedicated military jump capture'))
    rows=[]
    for p in sorted(audio.glob('*.wav')):
        x=load(p);rows.append(dict(**row(p,audio),seconds=len(x)/RATE,peak=float(np.abs(x).max()),clipped_samples=int(np.sum(np.abs(x)>=.999)),header_44_bytes=p.stat().st_size==44+len(x)*2))
    assert len(rows)==33 and all(r['clipped_samples']==0 and r['header_44_bytes'] for r in rows)
    for r in original['files']:assert digest(audio/r['path'])==r['sha256']
    credits=(audio/'CREDITS.txt').read_text('utf-8')
    credits=credits.replace('Approved fire.wav retained byte-identically from AVv3 original synthesis. All other cues use adapted recordings.',
      'Original fire.wav retained only for German K98 pending a suitable licensed live-fire source. Player/Allied fire_m1.wav now uses an actual M1 live-fire recording authorized by the user. Other cues use adapted recordings.')
    credits+='\nM1 live firing by MPierluissi\n'+source['page']+'\nCC0-1.0. Public HQ MP3, not original lossless master. Indoor field recording; first single shot trimmed, no added ping.\nJump is a boot/cloth Foley adaptation from the existing credited sources.\n'
    (audio/'CREDITS.txt').write_text(credits,'utf-8')
    provenance=dict(status='foot_contact_audio_v2_candidate_manual_review_pending',parent_provenance=original,sources=[source],edits=edits,files=rows,
      shot_policy='Original successful ShotSequence gating/attenuation retained; Team1 original fire, player/Allied recorded fire_m1',recording_hold=True,
      limitations=['Indoor lossy source, not outdoor lossless capture','Exact K98 live-fire source unavailable; original German report retained','Jump combines boot scuff and cloth, not a dedicated jump source','Human acoustics/contact acceptance pending'])
    save(audio/'PROVENANCE.json',provenance)
    listen=OUT/'listening';listen.mkdir()
    for sourcefile,target in [('fire_m1.wav','01_M1_real_shot.wav'),('jump.wav','02_jump_takeoff.wav'),('land.wav','03_jump_landing.wav')]:shutil.copyfile(audio/sourcefile,listen/target)
    (listen/'README.txt').write_text('Source listening samples only, not a captured game soundtrack. In-game gains and spatial treatment apply separately. Manual review pending.\n','utf-8')
    save(listen/'MANIFEST.json',dict(scope='Source listening examples, not UE recording',files=[row(p,listen) for p in sorted(listen.glob('*.wav'))]))
    print(json.dumps(dict(audio_files=33,new_cues=['fire_m1','jump'],parent_31_wavs_exact=True,shot_seconds=len(shot)/RATE)))
if __name__=='__main__':main()
