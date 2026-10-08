"""Freeze the mission's new guard candidates and current protected epoch."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,guard_rows,guards_match,digest
sys.path.insert(0,str(ROOT/'Tools/Integration/MissionLayoutV1'))
from build_layout import selected_nodes
out=STORE/'Evidence/G1MissionV1/config_v1_20261008'
assert not out.exists()
rows=guard_rows();assert len(rows)==703 and guards_match(rows)
layout_file=STORE/'Evidence/MissionLayoutV1/layout_v2_20261008/layout.json'
layout=json.loads(layout_file.read_text());points={p['id']:p for p in layout['points']}
f=STORE/'Evidence/FineMapGridV1/expanded_v2_20261007'
bank=json.loads((STORE/'Evidence/UEStandardNavigationV1/bank_v1_20261007/bank.json').read_text())
assert all(digest(f/n)==h for n,h in bank['source_sha256'].items())
z=np.load(f/'derived/full_filters.npz');spec=layout['grid_spec']
x=spec['xmin_cm']+(z['c']+.5)*25;y=spec['ymax_cm']-(z['r']+.5)*25
base=z['base']&(z['layer']==0)&~z['quarantine'];chosen=[]
for xy in ([7550,-20050],[7350,-20500]):
 ids=np.flatnonzero(base);j=int(ids[np.argmin((x[ids]-xy[0])**2+(y[ids]-xy[1])**2)])
 assert np.hypot(x[j]-xy[0],y[j]-xy[1])<150
 chosen.append(j)
nodes,source_hash=selected_nodes(f/'links/nodes.json',set(chosen))
roster=[]
for label,id,key in (('PC_City_Player','Player','S'),('PC_City_Ally1','Ally1','A1'),('PC_City_Ally2','Ally2','A2'),('PC_City_Enemy1','German1','G1')):
 roster.append({'label':label,'id':id,'feet_cm':points[key]['feet_cm'],'source_node':points[key]['node_id'],'yaw':35 if id in ('Player','Ally1','Ally2') else 180})
for k,j in enumerate(chosen,2):
 n=nodes[j];roster.append({'label':f'PC_City_Enemy{k}','id':f'German{k}','feet_cm':n['feet_cm'],'source_node':j,'yaw':180,'support_component':n['component']})
out.mkdir(parents=True)
result={'schema':'paris_g1_config_v1','map':'/Game/ParisCombat/Maps/LV_ParisG1_Midterm_V1','controller':'/Game/ParisCombat/Mission/G1V1/BP_PCG1ControllerV1',
 'fingerprint':'G1V1_20261008_original703_roster6_v1','roster':roster,'protected_rows':rows,'layout_sha256':digest(layout_file),
 'nodes_sha256':source_hash,'navigation_bounds_cm':{'min':[-5000,-28000,-100],'max':[10000,-17500,2000]},
 'status':'frozen_static_candidates_runtime_unaccepted'}
(out/'config.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='protected_rows'},indent=2))
