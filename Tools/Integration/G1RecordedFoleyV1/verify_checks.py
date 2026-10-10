"""Verify actual UE playback/resource/restore; do not infer acoustic acceptance."""
import json,re,wave
import numpy as np
from intake import ROOT,OUT,digest,save_json,row
from inspect_refs import load

def mix(path):
    with wave.open(str(path),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(48000,2,2)
        x=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float).reshape(-1,2)/32768
    return x
def match(signal,template):
    # Exact time-domain waveform match across the diagnostic native mix. Independent from event counters.
    n=len(signal);m=len(template);size=1<<(n+m-1).bit_length()
    corr=np.fft.irfft(np.fft.rfft(signal,size)*np.fft.rfft(template[::-1],size),size)[m-1:n]
    sums=np.concatenate([[0],np.cumsum(signal*signal)]);energy=sums[m:]-sums[:-m]
    norm=np.sqrt(np.maximum(energy,1e-14)*np.sum(template*template));score=corr/norm
    i=int(np.argmax(score));return dict(correlation=float(score[i]),sample_start=i,seconds=i/48000)

def main():
    receipts={}
    for mode in ['actions','legacy']:
        case=OUT/'checks'/mode
        launch=json.loads((case/'launch.json').read_text('utf-8-sig'));result=json.loads((case/'result.json').read_text('utf-8-sig'))
        assert launch['exit_code']==0 and result['status'].startswith('pass_'),(mode,result.get('status'))
        log=(case/'game.log').read_text('utf-8-sig')
        assert not re.search(r'(Fatal error|Assertion failed|Ensure condition failed|PARIS_AV_CUE_INVALID|PARIS_AV_AUDIO_PLAY_FAILED|Script error)',log,re.I)
        manifests=[json.loads(p.read_text('utf-8-sig')) for p in sorted(case.glob('audio_events_*.json'))]
        assert manifests and all(a['cues_ready'] for a in manifests)
        mixes=[]
        for p in sorted(case.glob('game_mix_*.wav')):
            x=mix(p);mixes.append(dict(**row(p,case),seconds=len(x)/48000,peak=float(np.max(np.abs(x))),
                rms=float(np.sqrt(np.mean(x*x))),clipped_samples=int(np.sum(np.abs(x)>=.999)),nonzero=int(np.count_nonzero(x))))
        assert mixes and all(m['clipped_samples']==0 for m in mixes)
        events=[e for a in manifests for e in a['events']]
        receipts[mode]=dict(status=result['status'],pid=launch['pid'],exit_code=launch['exit_code'],mixes=mixes,
             cues={name:sum(e['cue']==name for e in events) for name in sorted({e['cue'] for e in events})})
        if mode=='actions':
            steps=[e for e in events if e['cue'].startswith('step_')];assert len(steps)>10
            reload=[e for e in events if e['cue'].startswith('reload_')]
            assert [e['cue'] for e in reload]==['reload_handling','reload_m1_open','reload_m1_load','reload_m1_close']
            assert reload[0]['loaded']==2 and reload[0]['reserve']==16
            assert reload[2]['loaded']==8 and reload[2]['reserve']==10
            assert .56<reload[1]['reload_age']<.63 and 2.02<reload[2]['reload_age']<2.12 and 2.78<reload[3]['reload_age']<2.88
            assert sum(e['cue']=='fire' for e in events)==1
            data=mix(next(case.glob('game_mix_*.wav'))).mean(axis=1)
            checks={}
            for name in ['reload_m1_open','reload_m1_load','reload_m1_close','fire']:
                checks[name]=match(data,load(OUT/'candidate_v1/Audio'/(name+'.wav')))
                assert checks[name]['correlation']>.90,(name,checks[name])
            receipts[mode].update(reload=reload,actual_native_waveform_matches=checks,
                native_events=[e for e in result['events'] if 'reload_conserved' in str(e) or 'fire_consumes' in str(e)])
        else:
            # UUID lexical order is not travel order. Admit the final Phase generation in the actual log.
            generation=re.findall(r'PARIS_G1_PHASE \w+ generation=([0-9A-F-]+)',log)[-1]
            loaded=[a for a in manifests if a['generation']==generation]
            assert len(loaded)==1 and all(e['cue']!='death' for e in loaded[0]['events']),'No repeated saved death sound'
            # Original observer's live three-second terminal corpse assertion is authoritative.
            assert any('first_loaded_frame_terminal_corpses' in str(e) for e in result['events'])
            assert 'settled_loaded_audio' in result
            first=json.loads(result['first_loaded_audio']);state=json.loads(result['settled_loaded_audio'])
            for observed in [first,state]:assert observed['ready'] and observed['events']==0 and observed['voices']==0
            late=loaded[0]['events']
            assert all(e['time']>3 and e['cue']=='fire' and e['shots']==10 and e['loaded']==6 for e in late),late
            receipts[mode].update(restored_generation_count=len(loaded),first_loaded_audio=first,settled_loaded_audio=state,
                later_events=late,later_event_note='One new accepted shot after the three-second gate; native input origin unclassified, no new death')
    fire=OUT/'candidate_v1/Audio/fire.wav'
    assert digest(fire)==json.loads((OUT/'freeze.json').read_text('utf-8'))['approved_fire']['sha256']
    receipt=dict(status='pass_scoped_actual_audio_resource_and_legacy_restore',checks=receipts,
        approved_fire_sha256=digest(fire),manual_acoustic_acceptance='PENDING',recording_hold=True,
        limits=['No model auditory input; waveform match is playback evidence only','K98 reload, crawl and body-impact contact not exercised in this action loop','Reload interruption branch implemented but no active-voice interruption observed in these loops','No FPS/stress/natural turning/course acceptance'])
    save_json(OUT/'checks/verification.json',receipt)
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
