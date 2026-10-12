from pathlib import Path
import json,statistics,argparse
ap=argparse.ArgumentParser();ap.add_argument('identity');a=ap.parse_args()
root=Path(__file__).resolve().parents[3]/'tmp/g1-tactical-equipment-20261010/checks'/a.identity
raw=json.loads((root/'PERFORMANCE.json').read_text('utf-8-sig'));s=raw['samples']
def summary(key,group):
    v=sorted(r[key] for r in group if r[key]>0)
    return dict(samples=len(v),mean_ms=statistics.mean(v),p95_ms=v[min(len(v)-1,int(len(v)*.95))],max_ms=max(v)) if v else None
groups={'all_after_1s':s,'with_smoke':[r for r in s if r['clouds']>0],'without_smoke':[r for r in s if not r['clouds']]}
result={'scope':raw['scope'],'groups':{}}
for key,g in groups.items():
    result['groups'][key]={k:summary(k,g) for k in ['frame_ms','game_ms','draw_ms','gpu_ms']}
    if g:result['groups'][key]['mean_fps']=1000/statistics.mean(r['frame_ms'] for r in g)
result['actor_counts']=sorted(set(r['actors'] for r in s));result['phases']=sorted(set(r['phase'] for r in s))
(root/'PERFORMANCE_SUMMARY.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,separators=(',',':')))
