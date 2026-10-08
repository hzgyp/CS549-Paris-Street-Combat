"""One measured near-bank staging proposal; no asset changes or coordinate sweep."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest
sys.path.insert(0,str(ROOT/'Tools/Integration/MissionLayoutV1'))
from build_layout import selected_nodes
out=STORE/'Evidence/G1MissionV1/staging_config_v2_20261008';assert not out.exists() and guards_match(guard_rows())
old=STORE/'Evidence/G1MissionV1/config_v1_20261008/config.json';config=json.loads(old.read_text())
proof=STORE/'Evidence/G1MissionV1/travel_v2_20261008/result.json';r=json.loads(proof.read_text());leg=r['legs'][0]
assert len(r['legs'])==2 and leg['index']==0 and all(x['body_error_cm']<=55 and not x['squad_failed'] for x in leg['allies'])
requests=[leg['actual_player_feet_cm']]+[x['feet_cm'] for x in leg['allies']]
f=STORE/'Evidence/FineMapGridV1/expanded_v2_20261007';z=np.load(f/'derived/full_filters.npz');s=json.loads((f/'grid_spec.json').read_text())
x=s['xmin_cm']+(z['c']+.5)*25;y=s['ymax_cm']-(z['r']+.5)*25;base=z['base']&(z['layer']==0)&~z['quarantine'];chosen=[]
for request in requests:
 allowed=base.copy()
 for j in chosen:allowed&=(x-x[j])**2+(y-y[j])**2>=150**2
 ids=np.flatnonzero(allowed);j=int(ids[np.argmin((x[ids]-request[0])**2+(y[ids]-request[1])**2)])
 assert np.hypot(x[j]-request[0],y[j]-request[1])<150;chosen.append(j)
nodes,h=selected_nodes(f/'links/nodes.json',set(chosen));assert len({int(z['group'][j]) for j in chosen})==1
for p,j,request in zip(config['roster'],chosen,requests):
 n=nodes[j];p.update(feet_cm=n['feet_cm'],source_node=j,yaw=0,support_component=n['component'],actual_reference_feet_cm=request,
  snap_distance_cm=float(np.hypot(x[j]-request[0],y[j]-request[1])))
config.update(fingerprint='G1V2_20261008_nearbank703_roster6_v1',slot_prefix='ParisG1V2',source_config_sha256=digest(old),
 staging_reference={'path':proof.relative_to(ROOT).as_posix(),'sha256':digest(proof)},nodes_sha256=h,
 status='frozen_nearbank_staging_unsaved_visual_unaccepted')
out.mkdir(parents=True);(out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
print([(p['id'],p['feet_cm'],p['snap_distance_cm']) for p in config['roster'][:3]])
