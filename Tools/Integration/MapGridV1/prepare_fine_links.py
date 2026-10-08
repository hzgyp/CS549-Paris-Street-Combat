"""Independent fine graph per native scope; no saved/expanded height matching."""
import argparse,json
from collections import defaultdict,Counter
from pathlib import Path
from grid_core import digest
from prepare_links import city

def prepare(entry,saved_only=False):
    name='saved' if saved_only else 'full';dest=entry/('saved_links' if saved_only else 'links');dest.mkdir()
    cells=defaultdict(list);counts=Counter();native=0
    for line in (entry/name/'samples.jsonl').open(encoding='utf-8'):
        r=json.loads(line);native+=1;counts[r['reason']]+=1
        if not (r['admitted'] and city(r)):continue
        peers=cells[(r['c'],r['r'])]
        equal=next((n for n in peers if n['component']==r['component'] and abs(n['nav_cm'][2]-r['nav_cm'][2])<=.01 and abs(n['feet_cm'][2]-r['feet_cm'][2])<=.01),None)
        if equal:
            equal['polys'].append(r['p']);equal['sample_ids'].append(r['id']);continue
        peers.append({'c':r['c'],'r':r['r'],'nav_cm':r['nav_cm'],'feet_cm':r['feet_cm'],'p':r['p'],
                      'polys':[r['p']],'sample_ids':[r['id']],'component':r['component'],'mesh':r['mesh'],
                      'road':bool('Road' in r['component'] or 'Road' in r['mesh'])})
    nodes=[]
    for key,peers in sorted(cells.items(),key=lambda item:(item[0][1],item[0][0])):
        for layer,n in enumerate(sorted(peers,key=lambda n:n['nav_cm'][2])):
            n.update(id=len(nodes),layer=layer);nodes.append(n)
    count=0
    with (dest/'requests.jsonl').open('x',encoding='utf-8') as f:
        for n in nodes:
            for dc,dr in ((1,0),(-1,0),(0,1),(0,-1)):
                for b in cells.get((n['c']+dc,n['r']+dr),[]):
                    if abs(n['feet_cm'][2]-b['feet_cm'][2])>45:continue
                    req={'id':count,'from':n['id'],'to':b['id'],'p':n['p'],'start_nav_cm':n['nav_cm'],
                         'end_nav_cm':b['nav_cm'],'start_feet_cm':n['feet_cm'],'end_feet_cm':b['feet_cm']}
                    f.write(json.dumps(req,separators=(',',':'))+'\n');count+=1
    with (dest/'nodes.json').open('x',encoding='utf-8') as f:json.dump(nodes,f,separators=(',',':'));f.write('\n')
    meta={'native_rows':native,'reasons':dict(counts),'city_geometry_nodes':len(nodes),'directed_link_requests':count,
          'layers':max((n['layer'] for n in nodes),default=0)+1,'nodes_sha256':digest(dest/'nodes.json'),'requests_sha256':digest(dest/'requests.jsonl')}
    (dest/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);p.add_argument('--saved-only',action='store_true');a=p.parse_args();prepare(a.entry,a.saved_only)
