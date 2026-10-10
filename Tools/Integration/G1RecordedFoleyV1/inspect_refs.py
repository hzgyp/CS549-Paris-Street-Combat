"""Read existing captures only; decode source references and report transient times."""
import json,subprocess,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from intake import ROOT,OUT,digest,save_json,row

FF=Path('C:/Users/hzgyp/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')

def load(p):
    with wave.open(str(p),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(48000,1,2)
        return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768
def decode():
    dest=OUT/'decoded';dest.mkdir(exist_ok=True);rows=[]
    for s in json.loads((OUT/'intake/sources.json').read_text('utf-8')):
        if not s['status'].startswith('acquired'):continue
        target=dest/(s['name']+'.wav')
        if not target.exists():
            subprocess.run([str(FF),'-nostdin','-v','error','-i',str(OUT/'intake'/s['local']),'-ac','1','-ar','48000','-c:a','pcm_s16le','-bitexact',str(target)],check=True)
        x=load(target);n=480;env=np.array([np.max(np.abs(x[i:i+n])) for i in range(0,len(x),n)])
        rms=np.array([np.sqrt(np.mean(x[i:i+n]**2)) for i in range(0,len(x),n)])
        # Diagnostic clusters; selection is reviewed separately, never automatic realism acceptance.
        threshold=max(.012,float(np.max(rms))*.16)
        active=np.where(rms>threshold)[0];groups=[]
        for i in active:
            if not groups or i-groups[-1][-1]>8:groups.append([int(i)])
            else:groups[-1].append(int(i))
        peaks=[dict(start=g[0]*.01,end=(g[-1]+1)*.01,peak_time=(g[0]+np.argmax(env[g[0]:g[-1]+1]))*.01,
                    peak=float(np.max(env[g[0]:g[-1]+1]))) for g in groups]
        rows.append(dict(name=s['name'],seconds=len(x)/48000,peak=float(np.max(np.abs(x))),rms=float(np.sqrt(np.mean(x*x))),clusters=peaks,sha256=digest(target)))
        im=Image.new('RGB',(1500,250),'white');d=ImageDraw.Draw(im);d.text((12,8),s['name']+'  '+str(round(len(x)/48000,3))+'s',fill='black')
        for k in range(1440):
            a=int(k*len(x)/1440);b=max(a+1,int((k+1)*len(x)/1440));v=x[a:b]
            d.line((30+k,135-float(np.max(v))*95,30+k,135-float(np.min(v))*95),fill=(30,65,80))
        for sec in range(int(len(x)/48000)+1):
            px=30+sec*1440/(len(x)/48000);d.text((px,227),str(sec),fill='black')
        im.save(dest/(s['name']+'_wave.png'))
    save_json(dest/'analysis.json',rows);print(json.dumps([dict(name=r['name'],seconds=r['seconds'],clusters=r['clusters'] if r['name'] in ['kar98','coat','body_dirt'] else len(r['clusters'])) for r in rows],indent=2))

def old_frames():
    raw=ROOT/'tmp/g1-demo-draft02-20261009/raw/2026-10-09 19-50-56.mkv'
    review=OUT/'old_footage_review';review.mkdir(exist_ok=True)
    times=[64.9,65.15,65.45,65.85,66.35,66.85,67.35,67.85,68.35,68.85]
    sheet=Image.new('RGB',(1600,5*485),(22,22,22));d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        p=review/(f'reload_{t:.2f}.png')
        if not p.exists():subprocess.run([str(FF),'-nostdin','-v','error','-ss',str(t),'-i',str(raw),'-frames:v','1',str(p)],check=True)
        im=Image.open(p);im.resize((800,450)).save(review/(f'reload_{t:.2f}_small.png'))
        sheet.paste(im.resize((800,450)),((i%2)*800,(i//2)*485))
        d.text(((i%2)*800+12,(i//2)*485+456),f'Existing raw {t:.2f}s / reload +{t-64.918:.3f}s',fill='white')
    sheet.save(review/'reload_sheet.png')
    save_json(review/'references.json',dict(raw=row(raw,ROOT),frames=[row(p,review) for p in sorted(review.glob('reload_*.png'))],
       note='Extracted from existing recording; no new screen recording',nominal_reload_start=64.918,
       loaded_commit_start=66.984,source_cue_log= 'tmp/g1-demo-draft02-20261009/probe/game.log'))

if __name__=='__main__':decode();old_frames()
