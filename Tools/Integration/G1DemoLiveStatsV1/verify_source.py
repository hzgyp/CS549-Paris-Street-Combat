"""Read-only source/cooked closure guards for the isolated diagnostics build."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];W=ROOT/'tmp/g1-demo-draft04-20261010/recording_stats_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((W/'prepare.json').read_text());checks=[]
for row in p['files']:
 for base in [Path(p['project']),W/'compiled_source_snapshot']:
  checks.append(dict(path=str(base/row['path']),exact=sha(base/row['path'])==row['sha256']))
old=json.loads((ROOT/'tmp/g1-demo-draft03-20261009/recording_v6_prepare.json').read_text('utf-8-sig'))
runtime=Path(p['stable_runtime']).parents[4]
for row in old['normal_files']:
 if row['path'] in ['PLAY_G1_REVISION.cmd','Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe']:continue
 checks.append(dict(path=str(runtime/row['path']),exact=sha(runtime/row['path'])==row['sha256']))
assert all(r['exact'] for r in checks)
out=dict(status='diagnostic_source_and_cooked_closure_exact',checks=checks)
(W/'source_verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(status=out['status'],checked=len(checks))))
