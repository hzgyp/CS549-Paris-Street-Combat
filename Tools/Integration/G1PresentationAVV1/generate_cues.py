"""Deterministic original first-pass gameplay Foley; no third-party samples."""
import argparse,hashlib,json,wave
from pathlib import Path
import numpy as np

RATE=48000
def make(kind,variant=0):
    rng=np.random.default_rng(20261009+variant+sum(map(ord,kind)))
    duration={'fire':.85,'death':.72,'reload':.42,'reload_end':.32,'land':.31,'crawl':.38}.get(kind,.27)
    t=np.arange(round(duration*RATE))/RATE
    white=rng.normal(0,1,len(t));low=np.convolve(white,np.ones(15)/15,'same')
    grit=white-np.convolve(white,np.ones(7)/7,'same')
    x=np.zeros_like(t)
    def impact(at,weight,frequency,decay):
        nonlocal x
        u=t-at;mask=u>=0;env=np.where(mask,np.exp(-np.maximum(u,0)/decay),0)
        attack=np.clip(u/.0015,0,1)
        x+=weight*env*attack*(.65*np.sin(2*np.pi*(frequency-30*np.minimum(np.maximum(u,0),.12))*u)+.28*low+.09*grit)
    if kind.startswith('step_') or kind=='land':
        impact(0,.9,87+variant*5,.038);impact(.044,.28,105,.018)
        x+=.11*grit*np.exp(-t/.074)*(1-np.exp(-t/.004))
        if kind=='land':impact(.033,.6,57,.052)
    elif kind=='crawl':
        x=.21*grit*np.sin(np.pi*t/duration)**2*(.5+.5*np.sin(2*np.pi*24*t)**2)+.18*low*np.sin(np.pi*t/duration)**2
    elif kind=='fire':
        x=.65*white*np.exp(-t/.019)*(1-np.exp(-t/.0005))
        impact(.003,1.8,61,.073)
        for at,weight in [(.067,.15),(.142,.105),(.263,.075)]:
            u=np.maximum(t-at,0);x+=weight*(t>=at)*low*np.exp(-u/.075)
        impact(.093,.14,590,.008)
    elif kind=='death':
        impact(.08,1.4,49,.081);impact(.185,.55,73,.041)
        x+=.18*grit*np.exp(-((t-.17)/.10)**2)
        for at in [.14,.22,.29]:impact(at,.12,940+variant*20,.012)
    else:
        for at,weight in ([(.01,.55),(.08,.25),(.28,.8)] if kind=='reload' else [(.015,.8),(.08,.35)]):
            impact(at,weight,790,.009)
        x+=.025*grit*np.exp(-((t-.11)/.058)**2)
    fade=np.minimum(1,(duration-t)/.018)
    x=x*np.maximum(fade,0)
    peak={'fire':.78,'death':.56,'reload':.35,'reload_end':.39,'land':.43,'crawl':.32}.get(kind,.42)
    x=x/max(np.max(np.abs(x)),1e-6)*peak
    return np.round(x*32767).astype('<i2')

def generate(directory):
    directory.mkdir(parents=True,exist_ok=False);rows=[]
    kinds=[f'step_{mode}_{side}' for mode in ['walk','run','slow'] for side in ['a','b']]+['crawl','fire','death','reload','reload_end','land']
    for name in kinds:
        variant=1 if name.endswith('_b') else 0
        samples=make(name.rsplit('_',1)[0] if name.startswith('step_') else name,variant)
        p=directory/(name+'.wav')
        with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(samples.tobytes())
        rows.append(dict(path=p.name,frames=len(samples),seconds=len(samples)/RATE,peak=float(np.max(np.abs(samples.astype(float)))/32768),
                         rms=float(np.sqrt(np.mean((samples.astype(float)/32768)**2))),size_bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    receipt=dict(origin='Original deterministic signal synthesis; no sampled commercial or human voice material',quality='First-pass basic Foley/rifle transient/body/equipment impact; not a historical recording or final professional sound design',
                 sample_rate=RATE,channels=1,pcm_bits=16,files=rows)
    (directory/'PROVENANCE.json').write_text(json.dumps(receipt,indent=2)+'\n','utf-8')
    return receipt
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args();print(json.dumps(generate(Path(a.directory))))
