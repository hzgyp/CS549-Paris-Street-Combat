"""Read concatenated native JSON samples without relabeling them as acceptance."""
import argparse
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('identity');a=p.parse_args()
out=ROOT/'tmp/mvp-closeout-20261008'/a.identity
result=out/'result.json'
if result.exists():
    report=json.loads(result.read_text());rows=report['samples']
    print(json.dumps({k:report[k] for k in ('status','step','elapsed_wall_seconds')}))
else:
    if not (out/'samples.jsonl').exists():
        print(json.dumps({'status':'awaiting_observer_sample','identity':a.identity}))
        raise SystemExit(0)
    text=(out/'samples.jsonl').read_text();decoder=json.JSONDecoder();pos=0;rows=[]
    while pos<len(text):
        while pos<len(text) and text[pos].isspace():pos+=1
        if pos==len(text):break
        try:row,pos=decoder.raw_decode(text,pos)
        except json.JSONDecodeError:break # Current append may be incomplete.
        rows.append(row)
if not rows:
    print(json.dumps({'status':'awaiting_complete_sample','identity':a.identity}))
    raise SystemExit(0)
row=rows[-1]
print(json.dumps({k:row.get(k) for k in ('phase','round','world_seconds','living_defenders','living_allies','movement_diagnostic')},indent=2))
print(json.dumps(row.get('snapshot',{}).get('actors',[]),indent=2))
print(json.dumps(row.get('allied_navigation_diagnostic',[]),indent=2))
