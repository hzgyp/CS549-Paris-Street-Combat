"""Freeze finite uniform origins and a real central floor; never edit source maps."""
import gc,json,math,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
SOURCE=STORE/'Evidence/FineMapGridV1/expanded_v2_20261007'
OUT=STORE/'Evidence/NativeConvergenceV1/bank_v1_20261007'

def main():
    assert not OUT.exists(),'Frozen bank identity occupied'
    selection=json.loads((ROOT/'Docs/Development/MissionLoopV1/FINE_GRID_SELECTION_20261007.json').read_text())
    assert digest(SOURCE/'artifact/closure.json')==selection['closure_sha256']
    rows=guard_rows();assert len(rows)==703 and guards_match(rows)
    spec=json.loads((SOURCE/'grid_spec.json').read_text())
    sf=np.load(SOURCE/'derived/saved_filters.npz')
    candidates=np.flatnonzero(sf['base']&(sf['count3']>=25))
    xx=-50400+(sf['c'][candidates]+.5)*25;yy=50400-(sf['r'][candidates]+.5)*25
    hub_id=int(candidates[np.lexsort((candidates,xx*xx+yy*yy))[0]])
    nodes=json.loads((SOURCE/'saved_links/nodes.json').read_text());hub=nodes[hub_id]
    hub={**hub,'scope':'saved','group':int(sf['group'][hub_id]),'stations_3m':int(sf['count3'][hub_id])}
    del nodes,sf;gc.collect()
    ff=np.load(SOURCE/'derived/full_filters.npz');c=ff['c'];r=ff['r'];base=ff['base'];layers=ff['layer']
    ids=np.flatnonzero(base);tiles={}
    for k in ids.tolist():tiles.setdefault((int(c[k]//200),int(r[k]//200),int(layers[k])),[]).append(k)
    selected=[]
    for (tc,tr,l),members in sorted(tiles.items()):
        arr=np.array(members);comfortable=arr[ff['count3'][arr]>=13]
        use=comfortable if len(comfortable) else arr
        d=(c[use]+.5-(tc*200+100))**2+(r[use]+.5-(tr*200+100))**2
        k=int(use[np.lexsort((use,d))[0]])
        selected.append({'node_id':k,'tile':[tc,tr,l],'tile_white_centres':len(members),
                         'group':int(ff['group'][k]),'stations_3m':int(ff['count3'][k])})
    fn=json.loads((SOURCE/'links/nodes.json').read_text())
    match=np.flatnonzero((c==hub['c'])&(r==hub['r'])&base)
    match=[int(k) for k in match if fn[int(k)]['component']==hub['component'] and abs(fn[int(k)]['feet_cm'][2]-hub['feet_cm'][2])<=.01]
    assert len(match)==1,'Do not associate unequal scope floor identities'
    hub['display_full_node_id']=match[0]
    origins=[]
    for s in selected:
        n=fn[s['node_id']];assert base[s['node_id']] and not ff['quarantine'][s['node_id']]
        origins.append({**s,'node':n,'hub_xy_distance_cm':math.dist(n['feet_cm'][:2],hub['feet_cm'][:2])})
    assert len(origins)==69
    origins.sort(key=lambda x:(x['hub_xy_distance_cm'],x['node_id']))
    cases=[]
    for j,s in enumerate(origins):
        for role in ('allied','german'):
            cases.append({'id':f'origin_{j:03d}_{role}','origin_index':j,'role':role,'source_node_id':s['node_id'],
                          'source_cm':s['node']['feet_cm'],'source_component':s['node']['component'],
                          'source_mesh':s['node']['mesh'],'c':s['node']['c'],'r':s['node']['r'],'layer':s['node']['layer'],
                          'survey_group':s['group'],'source_scope':'full','native_navigation_scope':'saved'})
    nearby=[j for j,s in enumerate(origins) if s['group']==ff['group'][hub['display_full_node_id']] and 1000<s['hub_xy_distance_cm']<8000]
    assert len(nearby)>=2
    early_ids=[s['id'] for s in cases if s['origin_index'] in nearby[:2]]
    names=['grid_spec.json','derived/full_filters.npz','derived/saved_filters.npz','links/nodes.json',
           'saved_links/nodes.json','derived/manifest.json','derived/full_walk_L0.png','artifact/closure.json']
    sources={name:digest(SOURCE/name) for name in names}
    helpers={name:digest(ROOT/f'Unreal/ParisStreetCombat/Plugins/{name}/Binaries/Win64/UnrealEditor-{name}.dll')
             for name in ('ParisFormalSurveyV1','ParisMapSurveyV1','ParisGridSurveyV1')}
    bank={'schema':'paris_native_convergence_bank_v1','source':SOURCE.relative_to(STORE).as_posix(),'source_sha256':sources,
          'grid_spec':spec,'hub':hub,'origins':origins,'cases':cases,'early_ids':early_ids,'helpers':helpers,
          'protected_rows':rows,'cell_cm':25,'tile_cm':5000,'runtime_samples_per_role':69,
          'selection_rule':'Closest to each occupied physical tile centre among count3>=13 when available; stable node-id tie break',
          'semantic_floors_completed':False,'final_layout_selected':False,'browser_tablet_work_deferred':True,
          'plan_sha256':digest(ROOT/'Docs/Development/MissionLoopV1/NATIVE_CONVERGENCE_IMPLEMENTATION_20261007.md')}
    OUT.mkdir(parents=True);(OUT/'bank.json').write_text(json.dumps(bank,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(OUT),'hub_cm':hub['feet_cm'],'hub_distance_m':math.hypot(*hub['feet_cm'][:2])/100,
                      'origins':len(origins),'cases':len(cases),'early':early_ids,'bank_sha256':digest(OUT/'bank.json')}))

if __name__=='__main__':main()
