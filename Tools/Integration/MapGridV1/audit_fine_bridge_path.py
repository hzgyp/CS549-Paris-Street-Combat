"""Reconstruct the C-bank fine route from reciprocal native links, no role movement."""
import argparse,json,math
from collections import defaultdict,deque
from pathlib import Path
import numpy as np
from grid_core import digest

def audit(entry):
    summary=json.loads((entry/'derived/manifest.json').read_text());scope=summary['scopes']['full']
    assert scope['C_fine_graph_same_group']
    ends=scope['C_test_endpoint_projection'];start,goal=[x['selected_id'] for x in ends];gid=ends[0]['group']
    with np.load(entry/'derived/full_filters.npz') as archive:group=archive['group'];base=archive['base']
    selected=set(np.flatnonzero((group==gid)&base).tolist());pairs=set()
    for line in (entry/'links/samples.jsonl').open(encoding='utf-8'):
        r=json.loads(line)
        if r['admitted'] and r['from'] in selected and r['to'] in selected:pairs.add((r['from'],r['to']))
    neighbors=defaultdict(list)
    for a,b in sorted(pairs):
        if (b,a) in pairs:neighbors[a].append(b)
    parent={start:None};queue=deque([start])
    while queue and goal not in parent:
        a=queue.popleft()
        for b in neighbors[a]:
            if b not in parent:parent[b]=a;queue.append(b)
    assert goal in parent
    route=[];k=goal
    while k is not None:route.append(k);k=parent[k]
    route.reverse();nodes=json.loads((entry/'links/nodes.json').read_text());points=[nodes[k]['feet_cm'] for k in route]
    bridge=[n for n in (nodes[k] for k in route) if abs(n['feet_cm'][0]-3955.002013788201)<=728.8503615140834 and abs(n['feet_cm'][1]+20836.729894594904)<=651.60465325557]
    assert bridge and all(40<=n['feet_cm'][2]<=300 for n in bridge),'C area above-water city route required'
    length=sum(math.dist(a,b) for a,b in zip(points,points[1:]));result={'status':'pass_C_expanded_fine_reciprocal_route','scope':'full_disposable_survey',
        'start_node':start,'goal_node':goal,'group':gid,'route_nodes':route,'feet_cm':points,'path_length_m':length/100,
        'bridge_area_nodes':len(bridge),'bridge_area_min_feet_z_cm':min(n['feet_cm'][2] for n in bridge),
        'bridge_area_max_feet_z_cm':max(n['feet_cm'][2] for n in bridge),'new_role_movement_performed':False,
        'saved_navigation_C_same_group':summary['scopes']['saved']['C_fine_graph_same_group'],
        'source_links_sha256':digest(entry/'links/samples.jsonl'),'source_nodes_sha256':digest(entry/'links/nodes.json')}
    target=entry/'artifact/audit_C_fine_path.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('route_nodes','feet_cm')}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);audit(p.parse_args().entry)
