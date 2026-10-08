"""Preserve independently measured saved/expanded collections; no tessellation matching."""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

from grid_core import connected_components,digest


def derive(entry):
    full=json.loads((entry/'sight/nodes.json').read_text(encoding='utf-8'))
    saved=json.loads((entry/'saved_links/nodes.json').read_text(encoding='utf-8'))
    edges=[]
    with (entry/'saved_links/samples.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            if r['admitted']:edges.append((r['from'],r['to']))
    groups=connected_components(range(len(saved)),edges)
    group_for={}
    for i,group in enumerate(groups):
        road=any(saved[k]['road'] for k in group)
        for k in group:group_for[k]=(i,road)
    offset=len(full);by_cell=defaultdict(list);associations=[]
    for n in full:
        n['scope']='survey';n['saved']=False;n['saved_group']=-1;n['saved_road_connected']=False
        by_cell[(n['c'],n['r'],n['component'])].append(n)
    for original in saved:
        native_id=original['id'];n=dict(original)
        n.update({'id':offset+native_id,'scope':'current','saved':True,'native_node_id':native_id,
                  'saved_group':group_for[native_id][0],'saved_road_connected':group_for[native_id][1],
                  'saved_sample_ids':list(n['sample_ids']),'saved_node_ids':[native_id],
                  'group':-1,'road_connected':False,'survey_node_ids':[]})
        for other in by_cell.get((n['c'],n['r'],n['component']),[]):
            delta=math.dist(n['feet_cm'],other['feet_cm'])
            if delta<=.01:
                n['survey_node_ids'].append(other['id']);n['group']=other['group'];n['road_connected']=other['road_connected']
                associations.append({'current_id':n['id'],'survey_id':other['id'],'actual_feet_delta_cm':delta,
                                     'current_feet_cm':n['feet_cm'],'survey_feet_cm':other['feet_cm'],
                                     'current_nav_cm':n['nav_cm'],'survey_nav_cm':other['nav_cm'],
                                     'same_support_component':n['component']})
        full.append(n)
    dest=entry/'derived_v2';dest.mkdir()
    (dest/'nodes.json').write_text(json.dumps(full,separators=(',',':'))+'\n',encoding='utf-8')
    (dest/'associations.json').write_text(json.dumps(associations,separators=(',',':'))+'\n',encoding='utf-8')
    result={'current_nodes':len(saved),'survey_nodes':offset,'current_source_native_offset':offset,
            'same_physical_point_associations':len(associations),'point_identity_tolerance_cm':.01,
            'max_association_feet_delta_cm':max((a['actual_feet_delta_cm'] for a in associations),default=0),
            'originals_unchanged':{p:digest(entry/p) for p in ('saved_links/nodes.json','sight/nodes.json')},
            'nodes_sha256':digest(dest/'nodes.json'),'associations_sha256':digest(dest/'associations.json')}
    (dest/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);derive(p.parse_args().entry)
