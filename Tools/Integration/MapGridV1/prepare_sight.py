"""Freeze geometric encounter sight pairs after reciprocal grid links finish."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from grid_core import connected_components, digest


def prepare(entry):
    nodes=json.loads((entry/'links/nodes.json').read_text(encoding='utf-8'))
    edges=[];outgoing=defaultdict(set)
    with (entry/'links/samples.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            if r['admitted']:edges.append((r['from'],r['to']));outgoing[r['from']].add(r['to'])
    groups=connected_components(range(len(nodes)),edges)
    by_cell=defaultdict(list)
    for n in nodes:by_cell[(n['c'],n['r'])].append(n)
    for i,group in enumerate(groups):
        has_road=any(nodes[k]['road'] for k in group)
        for k in group:nodes[k]['group']=i;nodes[k]['road_connected']=has_road
    saved_nodes=json.loads((entry/'saved_links/nodes.json').read_text(encoding='utf-8'))
    saved_edges=[]
    with (entry/'saved_links/samples.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            if r['admitted']:saved_edges.append((r['from'],r['to']))
    saved_groups=connected_components(range(len(saved_nodes)),saved_edges)
    saved_proofs={}
    for group_id,group in enumerate(saved_groups):
        has_road=any(saved_nodes[k]['road'] for k in group)
        for k in group:
            for proof in saved_nodes[k]['sample_ids']:saved_proofs[proof]=(k,group_id,has_road)
    for n in nodes:
        proofs=[saved_proofs[p] for p in n['saved_sample_ids']]
        n['saved_node_ids']=sorted({v[0] for v in proofs})
        n['saved_group']=proofs[0][1] if proofs else -1
        n['saved_road_connected']=any(v[2] for v in proofs)
        assert len({v[1] for v in proofs})<=1,'Matched exact surface split into conflicting saved groups'
    pairs=set();request_count=0
    dest=entry/'sight';dest.mkdir()
    with (dest/'requests.jsonl').open('x',encoding='utf-8') as out:
        for n in nodes:
            if not n['road_connected'] or len(outgoing[n['id']])<2:continue
            for dc,dr in ((1,0),(-1,0),(0,1),(0,-1)):
                for distance in (5,10,15,20):
                    targets=[other for other in by_cell.get((n['c']+dc*distance,n['r']+dr*distance),[])
                             if other['group']==n['group'] and abs(other['feet_cm'][2]-n['feet_cm'][2])<=200]
                    if not targets:continue
                    other=min(targets,key=lambda t:abs(t['feet_cm'][2]-n['feet_cm'][2]))
                    pair=tuple(sorted((n['id'],other['id'])))
                    if pair not in pairs:
                        pairs.add(pair)
                        req={'id':request_count,'from':pair[0],'to':pair[1],'sight':True,'eye_height_cm':140,
                             'start_feet_cm':nodes[pair[0]]['feet_cm'],'end_feet_cm':nodes[pair[1]]['feet_cm']}
                        out.write(json.dumps(req,separators=(',',':'))+'\n');request_count+=1
                    break
    (dest/'nodes.json').write_text(json.dumps(nodes,separators=(',',':'))+'\n',encoding='utf-8')
    report={'reciprocal_components':len(groups),'largest_component_nodes':len(groups[0]) if groups else 0,
            'saved_reciprocal_components':len(saved_groups),'largest_saved_component_nodes':len(saved_groups[0]) if saved_groups else 0,
            'sight_requests':request_count,'eye_height_cm':140,'distances_m':[5,10,15,20],
            'requests_sha256':digest(dest/'requests.jsonl')}
    (dest/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);prepare(p.parse_args().entry)
