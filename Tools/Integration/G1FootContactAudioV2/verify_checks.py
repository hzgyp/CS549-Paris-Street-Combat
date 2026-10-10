"""Independent trajectory/audio checks; they are not human acoustic approval."""
import json,re,wave,sys
import numpy as np
from common import ROOT,OUT,PARENT,digest,save,row
sys.path.insert(0,str(ROOT/'Tools/Integration/G1RecordedFoleyV1'))
from verify_checks import mix,match

def load(p):
    with wave.open(str(p),'rb') as w:
        assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(48000,1,2)
        return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float)/32768

def main():
    receipts={}
    for mode in ['actions','legacy']:
        case=OUT/'checks_solo'/mode;launch=json.loads((case/'launch.json').read_text('utf-8-sig'));result=json.loads((case/'result.json').read_text('utf-8-sig'))
        assert launch['exit_code']==0 and result['status'].startswith('pass_'),(mode,result.get('status'))
        log=(case/'game.log').read_text('utf-8-sig');assert not re.search(r'Fatal error|Assertion failed|Ensure condition failed|PARIS_AV_CUE_INVALID|PARIS_AV_AUDIO_PLAY_FAILED|PARIS_FOOT_BONES_MISSING|Script error',log,re.I)
        manifests=[json.loads(p.read_text('utf-8-sig')) for p in sorted(case.glob('audio_events_*.json'))]
        assert manifests and all(m['cues_ready'] for m in manifests)
        events=[e for m in manifests for e in m['events']];samples=[s for m in manifests for s in m.get('foot_samples',[])]
        mixes=[]
        for p in sorted(case.glob('game_mix_*.wav')):
            x=mix(p);mixes.append(dict(**row(p,case),seconds=len(x)/48000,peak=float(np.abs(x).max()),clipped_samples=int(np.sum(np.abs(x)>=.999)),nonzero=int(np.count_nonzero(x))))
        assert all(m['clipped_samples']==0 for m in mixes)
        receipts[mode]=dict(status=result['status'],pid=launch['pid'],exit_code=0,mixes=mixes,cue_counts={name:sum(e['cue']==name for e in events) for name in sorted({e['cue'] for e in events})})
        if mode=='actions':
            assert samples and mixes
            times=np.array([s['time'] for s in samples]);speed=np.array([s['speed'] for s in samples]);moving=np.array([s['moving'] for s in samples]);ground=np.array([s['grounded'] for s in samples])
            height=np.array([[s['left_z'],s['right_z']] for s in samples]);steps=[e for e in events if e['cue'].startswith('step_') and e['contact_foot']!='None']
            assert len(steps)>=10,'Actual player contacts, not NPC/distance events, required'
            contacts=[];transitions=[]
            for event in steps:
                idx=int(np.argmin(np.abs(times-event['time'])));side=0 if event['contact_foot']=='foot_l' else 1
                assert ground[idx] and moving[idx] and speed[idx]>12
                # A low local pose minimum with descent beforehand, checked from raw sampled trajectories.
                window=np.where((times>=times[idx]-.14)&(times<=times[idx]+.09)&ground&moving)[0]
                regime=np.where(speed>220,2,np.where(speed<90,0,1))
                if len(window)<3 or np.any(regime[window]!=regime[idx]) or np.ptp(speed[window])>max(10,speed[idx]*.25):
                    transitions.append(dict(event=event,status='UNASSESSED transition, not a contact pass',reason='Different animation blend baseline or insufficient same-regime data'));continue
                assert len(window)>=3
                near=float(height[idx,side]-height[window,side].min());assert near<3.0,(event,near)
                earlier=np.where((times>=times[idx]-.14)&(times<times[idx])&ground&moving)[0]
                assert len(earlier) and height[earlier,side].max()>height[idx,side]+.5,event
                contacts.append(dict(time=event['time'],side=event['contact_foot'],cue=event['cue'],minimum_residual_cm=near))
            assert {e['contact_foot'] for e in steps}=={'foot_l','foot_r'}
            assert len(contacts)>=10,'At least ten independently checked stable gait contacts required'
            assert all(e['grounded'] for e in steps)
            for prefix in ['step_walk','step_run','step_slow']:assert any(e['cue'].startswith(prefix) for e in steps),prefix
            jumps=[e for e in events if e['cue']=='jump'];lands=[e for e in events if e['cue']=='land']
            assert len(jumps)==1 and len(lands)==1 and not jumps[0]['grounded'] and jumps[0]['velocity_z']>80 and lands[0]['grounded']
            assert jumps[0]['time']<lands[0]['time']
            assert not any(jumps[0]['time']<=e['time']<lands[0]['time'] for e in steps)
            shots=[e for e in events if e['cue'].startswith('fire')];assert len(shots)==1 and shots[0]['cue']=='fire_m1'
            assert any('original_fire_consumes_one' in str(e) for e in result['events'])
            reload=[e for e in events if e['cue'].startswith('reload_')]
            assert [e['cue'] for e in reload]==['reload_handling','reload_m1_open','reload_m1_load','reload_m1_close']
            assert reload[0]['loaded']==2 and reload[0]['reserve']==16 and reload[2]['loaded']==8 and reload[2]['reserve']==10
            assert any('original_reload_conserved' in str(e) for e in result['events'])
            audio=mix(next(case.glob('game_mix_*.wav'))).mean(axis=1);matches={}
            for cue in ['fire_m1','jump','land','reload_m1_load']:
                matches[cue]=match(audio,load(OUT/'candidate_v2/Audio'/(cue+'.wav')))
                assert matches[cue]['correlation']>.90,(cue,matches[cue])
            receipts[mode].update(foot_samples=len(samples),player_contacts=steps,stable_player_contacts=contacts,unassessed_transition_contacts=transitions,bone_ranges_cm=(height.max(axis=0)-height.min(axis=0)).tolist(),jump=jumps,land=lands,reload=reload,actual_native_matches=matches)
        else:
            generation=re.findall(r'PARIS_G1_PHASE \w+ generation=([0-9A-F-]+)',log)[-1];restored=[m for m in manifests if m['generation']==generation];assert len(restored)==1
            assert not any(e['cue'] in ['death','jump','land'] or e['cue'].startswith('step_') for e in restored[0]['events'])
            assert any('first_loaded_frame_terminal_corpses' in str(e) for e in result['events'])
            first=json.loads(result['first_loaded_audio']);settled=json.loads(result['settled_loaded_audio'])
            for state in [first,settled]:assert state['ready'] and state['events']==0 and state['voices']==0
            receipts[mode].update(first_loaded_audio=first,settled_loaded_audio=settled,later_events=restored[0]['events'])
    frozen=json.loads((OUT/'freeze.json').read_text('utf-8-sig'))
    for r in frozen['parent_audio']:assert digest(PARENT/'candidate_v1/Audio'/r['path'])==r['sha256']
    receipt=dict(status='pass_scoped_player_contact_jump_recorded_m1_and_legacy_restore',checks=receipts,manual_acoustic_acceptance='PENDING',recording_hold=True,
      limits=['Only stable gait contacts have an independent minimum-window pass; all mixed transitions remain UNASSESSED, not passed','Foot low phase is not proof of physical sole-floor collision or repaired sliding','Human cadence/takeoff/report review pending','K98 live-fire unavailable; prior German cue retained','No new screen recording/turn/FPS/stress/teammate/course pass'])
    save(OUT/'checks_solo/verification.json',receipt)
    print(json.dumps(dict(status=receipt['status'],contacts=len(receipts['actions']['player_contacts']),stable_checked=len(receipts['actions']['stable_player_contacts']),transitions_unassessed=len(receipts['actions']['unassessed_transition_contacts']),foot_samples=receipts['actions']['foot_samples'],matches=receipts['actions']['actual_native_matches'],manual='PENDING')))

if __name__=='__main__':main()
