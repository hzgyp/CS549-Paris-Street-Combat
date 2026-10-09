"""Freeze offline road-center sites before native stress admission, not a pass."""
import hashlib
import json
import math
import mmap
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FineMapGridV1/expanded_v2_20261007/links/nodes.json'
out=ROOT/'tmp/mvp-closeout-20261008/stress_sites_preselection.json'
assert not out.exists(), 'Preserve frozen selection'
with p.open('rb') as f, mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data:
    candidates=[]
    for match in re.finditer(rb'\{"c":(\d+),"r":(\d+),[^{}]+\}',data):
        if 2036<=int(match[1])<=2100 and 2828<=int(match[2])<=2872:
            n=json.loads(match[0])
            if n['road'] and n['layer']==0 and n['feet_cm'][2]<200:
                candidates.append(n)
    source_sha=hashlib.sha256(data).hexdigest()
starts=[[1912.5,-20662.5],[1762.5,-21112.5],[1487.5,-20837.5]]
picks=[]
for n in sorted(candidates,key=lambda n:math.dist(n['feet_cm'][:2],starts[0])):
    if all(math.dist(n['feet_cm'][:2],q['feet_cm'][:2])>=210 for q in picks) and all(math.dist(n['feet_cm'][:2],s)>=180 for s in starts):
        picks.append(n)
        if len(picks)==12:break
assert len(picks)==12, 'Do not silently widen search envelope'
out.write_text(json.dumps(dict(scope='Frozen offline road-center preselection; native path/capsule/grounding/runtime NOT yet admitted',source=str(p.relative_to(ROOT)),source_sha256=source_sha,points=picks),indent=2)+'\n')
print(json.dumps([dict(id=n['id'],feet_cm=n['feet_cm']) for n in picks]))
