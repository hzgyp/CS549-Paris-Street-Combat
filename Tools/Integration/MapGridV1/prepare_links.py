"""Normalize native samples and schedule cardinal links without inferred free space."""
import argparse
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from grid_core import digest


def city(row):
    mesh=row.get('mesh','');component=row.get('component','')
    return (mesh.startswith('/Game/WW2City/') and '/Proxy/' not in mesh
            and '/LV_Proxy.' not in component and 'Landscape' not in row.get('actor_class',''))


def normalize(entry, saved_only=False):
    saved=defaultdict(list)
    with (entry/'saved/samples.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line)
            if r['admitted'] and city(r):saved[(r['c'],r['r'])].append(r)
    dest=entry/('saved_links' if saved_only else 'links');dest.mkdir()
    db=sqlite3.connect(dest/'cells.sqlite')
    db.execute('CREATE TABLE surfaces (c INTEGER,r INTEGER,z REAL,sample_id INTEGER,reason TEXT,city INTEGER,raw TEXT)')
    counts=Counter();by_cell=defaultdict(list);batch=[]
    with (entry/('saved' if saved_only else 'full')/'samples.jsonl').open(encoding='utf-8') as f:
        for line in f:
            r=json.loads(line);is_city=city(r)
            reason=r['reason'] if not r['admitted'] else 'city_geometry_clear' if is_city else 'non_city_or_unclassified_support'
            counts[reason]+=1
            batch.append((r['c'],r['r'],r['nav_cm'][2],r['id'],reason,int(is_city),line.rstrip()))
            if len(batch)>=8192:
                db.executemany('INSERT INTO surfaces VALUES (?,?,?,?,?,?,?)',batch);batch=[]
            if not (r['admitted'] and is_city):continue
            peers=by_cell[(r['c'],r['r'])]
            equal=next((n for n in peers if abs(n['nav_cm'][2]-r['nav_cm'][2])<=.01 and
                        abs(n['feet_cm'][2]-r['feet_cm'][2])<=.01 and n['component']==r['component']),None)
            proofs=[s['id'] for s in saved[(r['c'],r['r'])] if abs(s['nav_cm'][2]-r['nav_cm'][2])<=.01
                    and abs(s['feet_cm'][2]-r['feet_cm'][2])<=.01 and s['component']==r['component']]
            if equal:
                equal['sample_ids'].append(r['id']);equal['polys'].append(r['p'])
                equal['saved_sample_ids']=sorted(set(equal['saved_sample_ids']+proofs))
                continue
            peers.append({'c':r['c'],'r':r['r'],'nav_cm':r['nav_cm'],'feet_cm':r['feet_cm'],
                          'p':r['p'],'polys':[r['p']],'sample_ids':[r['id']],
                          'component':r['component'],'mesh':r['mesh'],
                          'saved_sample_ids':proofs,'road':bool('Road' in r['component'] or 'Road' in r['mesh'])})
    if batch:db.executemany('INSERT INTO surfaces VALUES (?,?,?,?,?,?,?)',batch)
    db.execute('CREATE INDEX surface_cell ON surfaces(c,r)');db.commit();db.close()
    nodes=[]
    for key,peers in sorted(by_cell.items(),key=lambda item:(item[0][1],item[0][0])):
        for layer,n in enumerate(sorted(peers,key=lambda n:n['nav_cm'][2])):
            n.update({'id':len(nodes),'layer':layer,'saved':bool(n['saved_sample_ids'])})
            nodes.append(n)
    count=0
    with (dest/'requests.jsonl').open('x',encoding='utf-8') as out:
        for n in nodes:
            for dc,dr in ((1,0),(-1,0),(0,1),(0,-1)):
                for other in by_cell.get((n['c']+dc,n['r']+dr),[]):
                    if abs(n['feet_cm'][2]-other['feet_cm'][2])>45:continue
                    request={'id':count,'from':n['id'],'to':other['id'],'p':n['p'],
                             'start_nav_cm':n['nav_cm'],'end_nav_cm':other['nav_cm'],
                             'start_feet_cm':n['feet_cm'],'end_feet_cm':other['feet_cm']}
                    out.write(json.dumps(request,separators=(',',':'))+'\n');count+=1
    (dest/'nodes.json').write_text(json.dumps(nodes,separators=(',',':'))+'\n',encoding='utf-8')
    report={'native_rows':sum(counts.values()),'reasons':dict(counts),'city_geometry_nodes':len(nodes),
            'saved_city_nodes':sum(n['saved'] for n in nodes),'directed_link_requests':count,
            'layers':max((n['layer'] for n in nodes),default=0)+1,
            'nodes_sha256':digest(dest/'nodes.json'),'requests_sha256':digest(dest/'requests.jsonl')}
    (dest/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);p.add_argument('--saved-only',action='store_true')
    a=p.parse_args();normalize(a.entry,a.saved_only)
