"""Actual 25 cm centers in a frozen city-support envelope; no pixel resampling."""
import argparse,json
from pathlib import Path
from grid_core import polygon_cells,cell_xy,digest,PROFILE
from prepare_links import city

BRIDGES=[(-15978.070182685,17610.558595381),(-6841.830525979,60.071411216),(3955.002013788,-20836.729894595)]

def controls(nav,spec,coarse,out):
    import math
    known=json.loads((coarse.parent/'early_v3_20261007/result.json').read_text())
    road=known['early_controls'][0]['request']['xyz'];stack_xy=known['early_controls'][1]['requests'][0]['xyz'][:2]
    near=[];stacks={};bridges=[[] for _ in BRIDGES]
    for p in nav['polygons']:
        xs=[v[0] for v in p['vertices_cm']];ys=[v[1] for v in p['vertices_cm']]
        targets=[road[:2],stack_xy]+[list(b) for b in BRIDGES]
        if not any(min(xs)<=x+200 and max(xs)>=x-200 and min(ys)<=y+200 and max(ys)>=y-200 for x,y in targets):continue
        for c,r in polygon_cells(p,spec):
            x,y=cell_xy(spec,c,r);req={'id':0,'p':p['id'],'c':c,'r':r,'xyz':[x,y,p['surface_cm'][2]]}
            if math.dist([x,y],road[:2])<=200:near.append(req)
            if math.dist([x,y],stack_xy)<=150:stacks.setdefault((c,r),[]).append(req)
            for k,b in enumerate(BRIDGES):
                if math.dist([x,y],b)<=200:bridges[k].append(req)
    picked=min(near,key=lambda r:math.dist(r['xyz'][:2],road[:2])+abs(r['xyz'][2]-road[2]))
    options=[rs for rs in stacks.values() if max(r['xyz'][2] for r in rs)-min(r['xyz'][2] for r in rs)>200]
    assert options
    pair=sorted(min(options,key=lambda rs:math.dist(rs[0]['xyz'][:2],stack_xy)),key=lambda r:r['xyz'][2]);pair=[pair[0],pair[-1]]
    selected=[sorted(rows,key=lambda r:math.dist(r['xyz'][:2],BRIDGES[k]))[:64] for k,rows in enumerate(bridges)]
    assert all(selected)
    result={'road':picked,'stack':pair,'bridges':selected,'coordinate_checks':len(near)+sum(map(len,bridges))}
    (out/'early_controls.json').write_text(json.dumps(result,separators=(',',':'))+'\n')

def prepare(nav_path,out,spec_path,coarse):
    nav=json.loads(nav_path.read_text());spec=json.loads(spec_path.read_text())
    assert spec['cell_cm']==25 and spec['columns']==spec['rows']==4032
    name=out.name;assert name in ('saved','full')
    old=coarse/name;observed=set();city_polys=set()
    for line in (old/'samples.jsonl').open(encoding='utf-8'):
        r=json.loads(line);observed.add(r['p'])
        if city(r):city_polys.add(r['p'])
    polys={p['id']:p for p in nav['polygons']}
    # Polygon refs are opaque per rebuilt NavMesh, not persistent world identities.
    # Exact world vertices select an envelope only; new native admission still uses
    # the fresh ref and fresh floor/overlap records at every quarter-meter center.
    old_nav=json.loads((old/'navmesh.json').read_text())
    signature=lambda p:tuple(sorted(tuple(v) for v in p['vertices_cm']))
    old_signatures={p['id']:signature(p) for p in old_nav['polygons']}
    fresh_by_signature={}
    for p in nav['polygons']:fresh_by_signature.setdefault(signature(p),[]).append(p['id'])
    assert all(old_signatures[p] in fresh_by_signature for p in city_polys),'City envelope geometry changed'
    remap=lambda ids:{q for p in ids if p in old_signatures for q in fresh_by_signature.get(old_signatures[p],[])}
    selected=remap(city_polys);mapped_city=set(selected)
    observed=remap(observed)
    for p in mapped_city:
        selected.update(n['to'] for n in polys[p]['neighbors'] if n['to'] in polys)
    missed=set(polys)-observed;selected.update(missed)
    bridge_polys=set()
    for p in polys.values():
        xs=[v[0] for v in p['vertices_cm']];ys=[v[1] for v in p['vertices_cm']]
        if any(min(xs)<=x+3500 and max(xs)>=x-3500 and min(ys)<=y+3500 and max(ys)>=y-3500 for x,y in BRIDGES):
            bridge_polys.add(p['id'])
    selected.update(bridge_polys)
    count=0;omitted=[]
    with (out/'candidates.jsonl').open('x',encoding='utf-8') as f:
        for p in nav['polygons']:
            if p['id'] not in selected:continue
            cells=polygon_cells(p,spec)
            if not cells:omitted.append(p['id'])
            for c,r in cells:
                x,y=cell_xy(spec,c,r)
                f.write(json.dumps({'id':count,'c':c,'r':r,'p':p['id'],'xyz':[x,y,p['surface_cm'][2]]},separators=(',',':'))+'\n');count+=1
    meta={'spec':spec,'candidate_count':count,'omitted_polygons':omitted,'profile':PROFILE,
          'selected_polygons':sorted(selected),'excluded_non_city_only_polygons':sorted(set(polys)-selected),
          'previously_city_support_polygons':len(city_polys),'previously_center_missed_polygons':len(missed),
          'bridge_neighborhood_polygons':len(bridge_polys),'coarse_source_sha256':digest(old/'samples.jsonl'),
          'envelope_identity':'exact_sorted_world_vertices_not_rebuild_polygon_refs',
          'matched_city_geometry_signatures':len(city_polys),'exact_geometry_match_uses_no_rounding':True,
          'candidate_sha256':digest(out/'candidates.jsonl'),'source_nav_sha256':digest(nav_path)}
    (out/'candidate_manifest.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8')
    controls(nav,spec,coarse,out)
    print(json.dumps({'candidates':count,'polygons':len(selected),'excluded':len(polys)-len(selected),'omitted':len(omitted)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('nav',type=Path);p.add_argument('out',type=Path);p.add_argument('--spec',type=Path,required=True);p.add_argument('--coarse',type=Path,required=True)
    a=p.parse_args();prepare(a.nav,a.out,a.spec,a.coarse)
