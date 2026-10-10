"""Analyze the declared warmup boundary; retain all subsequent native frames."""
import csv,hashlib,json,math,statistics,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'tmp/assignment3-review-20261010/performance'
def stats(values):
    v=sorted(values)
    return {'mean':statistics.mean(v),'median':statistics.median(v),'p95':v[math.ceil(len(v)*.95)-1],'max':v[-1]}
def analyze(case):
    d=BASE/case;launch=json.loads((d/'launch.json').read_text('utf-8-sig'))
    assert launch['status']=='owned_game_exited' and launch['exit_code']==0
    path=d/f'UserDir/Saved/Profiling/CSV/{case}.csv'
    with path.open(encoding='utf-8-sig',newline='') as f:raw=list(csv.DictReader(f))
    assert raw[-2]['FrameTime']=='FrameTime' and raw[-1]['EVENTS'].startswith('[HasHeaderRowAtEnd]'),'Incomplete CSV'
    frames=[];elapsed=0;warm=0
    rows=[r for r in raw[:-2]]
    for row in rows:
        ft=float(row['FrameTime']);assert math.isfinite(ft) and ft>0
        if elapsed>=30000:frames.append(row)
        else:warm+=1
        elapsed+=ft
    values=[float(r['FrameTime']) for r in frames];s=stats(values)
    expected=12000 if case.startswith('baseline') else 15000 if case=='dynamic_v6' else 6000
    assert len(rows)==expected
    log=(d/'game.log').read_text('utf-8',errors='replace')
    assert 'PARIS_G1_PHASE Ready' in log and 'Capture Ended. Writing CSV' in log
    ready_allied=set(re.findall(r'PARIS_ALLIED_GRIP_READY (\S+)',log));ready_german=set(re.findall(r'PARIS_GERMAN_GRIP_READY (\S+)',log))
    assert len(ready_allied)==2 and len(ready_german)==3
    metrics={}
    for col in ['GameThreadTime','RenderThreadTime','GPUTime','GameThreadTime_CriticalPath','RenderThreadTime_CriticalPath','MemoryFreeMB']:
        vals=[float(r[col]) for r in frames if col in r and r[col] not in ('',None)]
        if vals:metrics[col]=stats(vals)
    return {'case':case,'csv':path.relative_to(ROOT).as_posix(),'csv_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256((d/'game.log').read_bytes()).hexdigest(),'complete_native_footer':True,'capture_frames':len(rows),'warmup_excluded_frames':warm,'warmup_seconds':30,'post_warmup_frames':len(frames),'seconds':sum(values)/1000,'fps':1000/s['mean'],'mean_ms':s['mean'],'median_ms':s['median'],'p95_ms':s['p95'],'max_ms':s['max'],'over_50ms':sum(v>50 for v in values),'over_100ms':sum(v>100 for v in values),'over_16_667ms_percent':100*sum(v>1000/60 for v in values)/len(values),'ready_allied':sorted(ready_allied),'ready_german':sorted(ready_german),'other_metrics':metrics,'game_sha256':launch['game_sha256']}

def dynamic():
    from datetime import datetime,timedelta
    d=BASE/'dynamic_v6';receipt=analyze('dynamic_v6')
    result=json.loads((d/'result.json').read_text('utf-8-sig'))
    assert result['status']=='pass_victory_save_restore_pending_media_review',result['status']
    assert all(len(s['agents'])==5 for s in result['samples']),'Roster addition/removal'
    log=(d/'game.log').read_text('utf-8',errors='replace')
    times={}
    for line in log.splitlines():
        m=re.match(r'\[(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2}:\d{3})\]',line)
        if not m:continue
        t=datetime.strptime(m[1],'%Y.%m.%d-%H.%M.%S:%f')
        if 'Capture Stop requested' in line:times['capture_stop']=t
        for phase in ('Crossing','Clearing','Won'):
            if f'PARIS_G1_PHASE {phase} ' in line and phase not in times:times[phase]=t
    assert all(k in times for k in ('capture_stop','Crossing','Won')),times
    with (d/'UserDir/Saved/Profiling/CSV/dynamic_v6.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))[:-2]
    ft=[float(r['FrameTime']) for r in rows]
    origin=times['capture_stop']-timedelta(seconds=sum(ft)/1000)
    cursor=0;active=[]
    for v in ft:
        start=origin+timedelta(milliseconds=cursor);end=start+timedelta(milliseconds=v)
        if start>=times['Crossing'] and end<=times['Won']:active.append(v)
        cursor+=v
    assert active
    s=stats(active)
    receipt.update({'helper_status':result['status'],'roster':'Original five NPC actors in every sample; deaths reduce live population naturally','phase_times_UTC':{k:v.isoformat() for k,v in times.items()},'active_mission':{'frames':len(active),'seconds':sum(active)/1000,'fps':1000/s['mean'],'mean_ms':s['mean'],'p95_ms':s['p95'],'max_ms':s['max'],'over_50ms':sum(v>50 for v in active),'alignment':'Approximate native log/CSV wall-clock window: Crossing through first Won. CSV final frame endpoint anchored to native capture-stop log; boundary-crossing frames excluded. No synchronized phase counters were added.'},'limitations':'One disclosed V6 ordinary-input/20Hz telemetry helper workload, not three matched normalGame active runs or sustained six-live combat capacity. Whole post-warmup metrics include Won/save/load/terminal observations and actual loading hitch.'})
    return receipt
def main():
    probe=analyze('run1');probe['acceptance']='Excluded short probe; post-warmup duration below60s'
    runs=[analyze(case) for case in ('baseline1','baseline2','baseline3')]
    assert all(r['seconds']>=60 for r in runs),'Insufficient declared interval; preserve, stop'
    summary={'date':'2026-10-10','game_sha256':runs[0]['game_sha256'],'hardware':{'CPU':'Intel Core i9-12900F','GPU':'RTX3080','VRAM_MiB':10240,'RAM_bytes':34138124288,'GPU_driver':'617.14'},'mean_target_pass':all(r['fps']>=60 for r in runs),'runs':runs,'retained_short_probe':probe,'dynamic_workload':dynamic(),'scope':'Ready NPC brains gated off: three existing stationary initial-scene render baselines, exact normal selected Game. Separate oneV6 ordinary-input dynamic workload explicitly disclosed. Not three normalGame active runs/sustained six-live combat capacity. Hardware causality is not isolated.'}
    (BASE/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n','utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('retained_short_probe','runs')},indent=2));print(json.dumps([{k:r[k] for k in ('case','seconds','fps','mean_ms','p95_ms','max_ms')} for r in runs],indent=2))
if __name__=='__main__':main()
