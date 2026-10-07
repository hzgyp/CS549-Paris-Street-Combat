"""Record unique local binding evidence; no selection, restore or publication."""
import datetime,hashlib,json
from pathlib import Path
from common import ROOT,BASE,CONFIG,guard
OUT=BASE/'cpp_evidence_v1'
assert not OUT.exists();OUT.mkdir()
plugin=ROOT/'Unreal/ParisStreetCombat/Plugins/ParisGripBindingV18'
def record(p):return {'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected':False,'restore_authority':False,
   'published':False,'guards':guard(),'configuration':record(CONFIG),
   'plugin_source':[record(p) for p in plugin.rglob('*') if p.is_file() and not any(k in p.parts for k in ('Binaries','Intermediate'))],
   'installed_editor_binaries':[record(p) for p in (plugin/'Binaries').rglob('*') if p.is_file()],
   'native_trials':{},'compile':'BuildPlugin Win64 editor Development successful/exit0; shipping unbuilt',
   'public_asset_payloads':False}
for identity in ('anim_author_v1','anim_author_v2','cpp_idle_v1','cpp_idle_v2','cpp_idle_v3','cpp_motion_v1'):
    p=BASE/identity/'result.json'
    if p.exists():r['native_trials'][identity]={'record':record(p),'result':json.loads(p.read_text())}
    p=ROOT/'tmp/grip-binding-v18'/f'{identity}.log.exit.json'
    if p.exists():r['native_trials'][identity]['process_exit']=json.loads(p.read_text(encoding='utf-8-sig'))
assert not r['guards']['mismatches']
(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'guard_count':r['guards']['count'],'mismatches':r['guards']['mismatches'],
                  'trials':{i:v['result']['status'] for i,v in r['native_trials'].items()},'selected':False}))
