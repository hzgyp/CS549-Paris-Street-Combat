"""New immutable derivation: remove measured runtime negatives before CC/filtering."""
import argparse,json
from pathlib import Path
from grid_core import connected_components,digest

def derive(entry):
    old=entry/'derived_v2';nodes=json.loads((old/'nodes.json').read_text());meta=json.loads((old/'manifest.json').read_text())
    runtime=json.loads((entry/'runtime_admission.json').read_text());cells={(x['c'],x['r']) for x in runtime['quarantined_cells']}
    for n in nodes:n['quarantined']=(n['c'],n['r']) in cells
    excluded=[n['id'] for n in nodes if n['quarantined']]
    for scope,folder,offset,gkey,rkey in [('survey','links',0,'group','road_connected'),('current','saved_links',meta['current_source_native_offset'],'saved_group','saved_road_connected')]:
        active={n['id'] for n in nodes if n['scope']==scope and not n['quarantined']};edges=[]
        with (entry/folder/'samples.jsonl').open() as f:
            for line in f:
                r=json.loads(line);a=r['from']+offset;b=r['to']+offset
                if r['admitted'] and a in active and b in active:edges.append((a,b))
        for n in nodes:
            if n['scope']==scope:n[gkey]=-1;n[rkey]=False
        for group,ids in enumerate(connected_components(sorted(active),edges)):
            road=any(nodes[k]['road'] for k in ids)
            for k in ids:nodes[k][gkey]=group;nodes[k][rkey]=road
    # Cross-scope metadata is informational; each scope still uses its own CC.
    for n in nodes:
        if n['scope']=='current':
            other=next((nodes[k] for k in n['survey_node_ids'] if not nodes[k]['quarantined']),None)
            n['group']=other['group'] if other else -1;n['road_connected']=other['road_connected'] if other else False
    dest=entry/'derived_v3';dest.mkdir()
    (dest/'nodes.json').write_text(json.dumps(nodes,separators=(',',':'))+'\n')
    (dest/'associations.json').write_bytes((old/'associations.json').read_bytes())
    meta.update({'previous_derivation_sha256':digest(old/'nodes.json'),'runtime_admission_sha256':digest(entry/'runtime_admission.json'),
                 'quarantined_node_ids':excluded,'quarantined_xy_cells':sorted(cells),'nodes_sha256':digest(dest/'nodes.json'),
                 'associations_sha256':digest(dest/'associations.json'),'connected_components_rebuilt_without_quarantine':True})
    (dest/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps({'quarantined_nodes':len(excluded),'quarantined_cells':sorted(cells)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);derive(p.parse_args().entry)
