"""Freeze ONE independent bridgehead encounter fixture, not final spawn locations."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
sys.path.insert(0,str(ROOT/'Tools/Integration/MissionLayoutV1'))
from build_layout import selected_nodes
out=STORE/'Evidence/G1MissionV1/encounter_config_v2_20261008';assert not out.exists() and guards_match(guard_rows())
f=STORE/'Evidence/FineMapGridV1/expanded_v2_20261007';z=np.load(f/'derived/full_filters.npz')
s=json.loads((f/'grid_spec.json').read_text());x=s['xmin_cm']+(z['c']+.5)*25;y=s['ymax_cm']-(z['r']+.5)*25
base=z['base']&(z['layer']==0)&~z['quarantine'];chosen={}
t=(x-5837.5)**2+(y+20237.5)**2;ti=int(np.flatnonzero(base)[np.argmin(t[base])])
base&=(z['group']==z['group'][ti])&(t<=300**2)
for name,xy in [('Player',[5712.5,-20237.5]),('Ally1',[5837.5,-20412.5]),('Ally2',[5837.5,-20062.5])]:
 allowed=base.copy()
 for j in chosen.values():allowed&=(x-x[j])**2+(y-y[j])**2>=150**2
 ids=np.flatnonzero(allowed);j=int(ids[np.argmin((x[ids]-xy[0])**2+(y[ids]-xy[1])**2)])
 assert np.hypot(x[j]-xy[0],y[j]-xy[1])<150;chosen[name]=j
nodes,h=selected_nodes(f/'links/nodes.json',set(chosen.values()))
result={'status':'frozen_independent_encounter_not_final_spawns','nodes_sha256':h,'points':{id:nodes[j] for id,j in chosen.items()},'native_seconds':30,'allied_yaw':0}
out.mkdir(parents=True);(out/'config.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v['feet_cm'] for k,v in result['points'].items()})
