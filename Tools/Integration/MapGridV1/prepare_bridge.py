"""Freeze a bridge-specific native-topology bank without changing the grid."""
import argparse,ast,json,math
from collections import Counter,deque
from pathlib import Path
from grid_core import digest
from planning_data import PlanningData

def chain(parent,end):
    result=[]
    while end is not None:result.append(end);end=parent[end]
    return list(reversed(result))

def prepare(root):
    root=root.resolve();store=root/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1';e=store/'Evidence'
    grid=e/'MapGridV1/full_v1_20261007';inventory=e/'PureMapSurveyV1/inventory_v4_20261007/inventory.json'
    inv=json.loads(inventory.read_text());bridges=[b for b in inv['blockers'] if 'Bridge' in (b['mesh'] or '')]
    bridges.sort(key=lambda b:-b['origin_cm'][1]);assert len(bridges)==3
    data=PlanningData(grid);nav={scope:json.loads((grid/folder/'navmesh.json').read_text()) for scope,folder in [('current','saved'),('survey','full')]}
    discovery={'inventory_sha256':digest(inventory),'grid_nodes_sha256':digest(grid/'derived_v3/nodes.json'),
        'native_sources':{scope:digest(grid/folder/'navmesh.json') for scope,folder in [('current','saved'),('survey','full')]},
        'local_search_halfwidth_cm':3500,'local_nav_z_slab_cm':[40,300],'diagnostic_search_not_physical_proof':True,'bridges':[]}
    for i,b in enumerate(bridges):
        x,y,_=b['origin_cm'];deck=[n for n in data.nodes if n['component']==b['component']]
        info={'id':chr(65+i),'component':b['component'],'mesh':b['mesh'],'origin_cm':b['origin_cm'],'extent_cm':b['extent_cm'],'scopes':{}}
        for scope in ['current','survey']:
            ns=[n for n in deck if n['scope']==scope];local=[n for n in data.nodes if n['scope']==scope and abs(n['feet_cm'][0]-x)<3500 and abs(n['feet_cm'][1]-y)<3500]
            polys={p['id']:p for p in nav[scope]['polygons']};allowed={p['id'] for p in nav[scope]['polygons'] if abs(p['surface_cm'][0]-x)<3500 and abs(p['surface_cm'][1]-y)<3500 and 40<p['surface_cm'][2]<300}
            # Direction across the chain of bridge placements, used only to select
            # two distinct bank sides; native path and actual bridge floor are required.
            tangent=[bridges[-1]['origin_cm'][j]-bridges[0]['origin_cm'][j] for j in [0,1]];length=math.hypot(*tangent);normal=[-tangent[1]/length,tangent[0]/length]
            side=lambda n:(n['feet_cm'][0]-x)*normal[0]+(n['feet_cm'][1]-y)*normal[1]
            start=[n for n in local if n['road'] and side(n)<-900];goal=[n for n in local if n['road'] and side(n)>900]
            if scope=='current':
                start=[n for n in start if data.eligible(n,'task',True)];goal=[n for n in goal if data.eligible(n,'task',True)]
            start.sort(key=lambda n:(math.dist(n['feet_cm'][:2],[x,y]),n['id']));goal.sort(key=lambda n:(math.dist(n['feet_cm'][:2],[x,y]),n['id']))
            bridge_polys={p for n in ns for p in n['polys']};best=None
            for s in start[:40]:
                parent={p:None for p in s['polys'] if p in allowed};q=deque(parent)
                while q:
                    a=q.popleft()
                    for link in polys[a]['neighbors']:
                        t=link['to']
                        if t in allowed and t not in parent:parent[t]=a;q.append(t)
                for t in goal[:40]:
                    endpoints=[p for p in t['polys'] if p in parent]
                    for end in endpoints:
                        path=chain(parent,end)
                        if not set(path)&bridge_polys:continue
                        cost=math.dist(s['feet_cm'][:2],[x,y])+math.dist(t['feet_cm'][:2],[x,y])
                        if best is None or (cost,s['id'],t['id'])<best[0]:best=((cost,s['id'],t['id']),s,t,path)
            info['scopes'][scope]={'clear_deck_nodes':len(ns),'road_connected_grid_deck_nodes':sum(data.base(n,scope=='current') for n in ns),
                'grid_deck_groups':dict(Counter(n['saved_group' if scope=='current' else 'group'] for n in ns)),
                'local_road_endpoints':[len(start),len(goal)],'native_polygon_candidate_found':bool(best)}
            if best:
                _,s,t,path=best;info['scopes'][scope]['candidate']={'source_cm':s['feet_cm'],'goal_cm':t['feet_cm'],'source_node':s['id'],'goal_node':t['id'],
                    'native_polygon_path':path,'bridge_polygons_on_path':sorted(set(path)&bridge_polys),'source_group':s['saved_group' if scope=='current' else 'group'],
                    'goal_group':t['saved_group' if scope=='current' else 'group'],'bank_normal_xy':normal}
        discovery['bridges'].append(info)
    target=e/'BridgeConnectivityV1';target.mkdir(exist_ok=True);dest=target/'bank_v1_20261007';dest.mkdir()
    (dest/'discovery.json').write_text(json.dumps(discovery,indent=2)+'\n')
    eligible=[b for b in discovery['bridges'] if b['scopes']['current']['native_polygon_candidate_found']]
    assert len(eligible)==1 and eligible[0]['id']=='C','Freeze only measured saved-nav southern candidate'
    bridge=eligible[0];c=bridge['scopes']['current']['candidate']
    old=e/'FormalMapVerificationV1/case_bank_v3_20261007/cases.json';oldbank=json.loads(old.read_text())
    for point in [c['source_cm'],c['goal_cm']]:assert min(math.dist(point[:2],p['feet_cm'][:2]) for p in oldbank['parking_sites'])>=1000
    route={**c,'category':'southern_bridge_crossing','source_sites':[],'goal_sites':[],
           'bridge_component':bridge['component'],'bridge_origin_cm':bridge['origin_cm'],'bridge_id':'C'}
    bank={'routes':[route],'parking_sites':oldbank['parking_sites'],'planned_legs':6,'source_entry':'bridge_bank_v1',
          'grid_spec':data.spec,'final_layout_selected':False,'positions_are_temporary_tests':True,'discovery_sha256':digest(dest/'discovery.json')}
    (dest/'cases.json').write_text(json.dumps(bank,indent=2)+'\n')
    source=e/'FormalMapVerificationV1/solo_v1_20261007/ue_verify.py';audit=json.loads((source.parent/'audit_v1.json').read_text())
    assert digest(source)==audit['inputs']['ue_verify.py'];text=source.read_text()
    replacements={"BANK_PATH=STORE/'Evidence/FormalMapVerificationV1/case_bank_v3_20261007/cases.json'":"BANK_PATH=Path(os.environ['CS549_BRIDGE_BANK'])",
      'Docs/Development/MissionLoopV1/FORMAL_ROLE_SQUAD_TEST_PLAN_20261007.md':'Docs/Development/MissionLoopV1/BRIDGE_CONNECTIVITY_PLAN_20261007.md',
      "for route_index in ([0] if STAGE=='Early' else range(3)):":'for route_index in range(len(routes)):',
      'middle=(unreal.Vector(*current[\'source_cm\'])+unreal.Vector(*current[\'goal_cm\']))*.5':"middle=unreal.Vector(*routes[current['route']]['bridge_origin_cm'])",
      'look=middle+unreal.Vector(0,0,95);location=middle+unreal.Vector(250,-200,650)': 'look=middle+unreal.Vector(0,0,300);location=middle+unreal.Vector(700,-700,2400)'}
    for old,new in replacements.items():assert text.count(old)==1,old;text=text.replace(old,new)
    needle="            all_arrived=True\n";assert text.count(needle)==1
    added="""            expected_component=routes[current['route']]['bridge_component']
            bridge_rows=[x for x in data if x['floor_component'].replace('UEDPIE_0_','')==expected_component]
            if bridge_rows and not current.get('bridge_capture_requested'):
                current['bridge_capture_requested']=True;capture(current['id']+'_bridge',now)
            all_arrived=True
""";text=text.replace(needle,added)
    needle="            if all_arrived:\n                current.update";assert text.count(needle)==1
    added="""            if all_arrived:
                expected_component=routes[current['route']]['bridge_component']
                visited=[x for sample in current['samples'] for x in sample['members'] if x['floor_component'].replace('UEDPIE_0_','')==expected_component]
                if not visited:reject('actual_bridge_floor_unobserved',now,data);return
                center=routes[current['route']]['bridge_origin_cm']
                if any(abs(p[0]-center[0])>3500 or abs(p[1]-center[1])>3500 for m in current['members'] for p in m['request']['path_cm']):reject('bridge_neighborhood_detour',now,data);return
                current['actual_bridge_floor_samples']=len(visited)
                current.update""";text=text.replace(needle,added)
    ast.parse(text);(dest/'ue_bridge_verify.py').write_text(text)
    (dest/'adaptation.json').write_text(json.dumps({'original_source_sha256':digest(source),'bank_sha256':digest(dest/'cases.json'),
        'adapted_source_sha256':digest(dest/'ue_bridge_verify.py'),'replacements':replacements,
        'extra_observation':'original bridge floor samples/capture and native path neighborhood admission; no movement changes'},indent=2)+'\n')
    print(json.dumps({'bank':str(dest),'routes':[route],'discovery':[{ 'id':b['id'],'scopes':b['scopes']} for b in discovery['bridges']]}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3]);prepare(p.parse_args().root)
