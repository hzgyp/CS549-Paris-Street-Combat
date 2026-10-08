"""Authenticate prior movement separately from its specialized support failure."""
import ast,json,math,re
from pathlib import Path
from grid_core import digest

ROOT=Path(__file__).resolve().parents[3]

def prepare(root):
    e=root/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence';base=e/'BridgeConnectivityV1'
    first=base/'runtime_C_v1_20261007';old=base/'bank_v1_20261007';r=json.loads((first/'result.json').read_text());b=json.loads((old/'cases.json').read_text())
    assert r['summary']=={'planned':6,'recorded':1,'passed':0,'negative':1,'unmeasured':5}
    c=r['cases'][0];m=c['members'][0];q=m['request'];event=m['completion'];f=m['final'];s=m['standing']
    assert c['reason']=='actual_bridge_floor_unobserved' and s['standing_pass'] and not s['blockers']
    assert q['started'] and event['result_code']==0 and event['controller']==q['controller'] and event['request_id']==q['request_id']
    xy=math.dist(f['feet_cm'][:2],m['goal_cm'][:2]);z=abs(f['feet_cm'][2]-m['goal_cm'][2]);assert xy<=35 and z<=35 and f['walkable_floor'] and f['movement_mode']==1
    assert f['resources']==r['startup_resources'][0]
    invpath=e/'PureMapSurveyV1/inventory_v4_20261007/inventory.json';inventory=json.loads(invpath.read_text());index={n['component']:n for n in inventory['blockers']}
    discovery=json.loads((old/'discovery.json').read_text());bridge=discovery['bridges'][2];x,y,_=bridge['origin_cm'];ex,ey,_=bridge['extent_cm']
    allowed={n['component']:n['mesh'] for n in inventory['blockers'] if n['mesh'] and n['mesh'].startswith('/Game/WW2City/Environment/') and '/Proxy/' not in n['mesh']
        and abs(n['origin_cm'][0]-x)<=ex+n['extent_cm'][0] and abs(n['origin_cm'][1]-y)<=ey+n['extent_cm'][1]}
    observations=[];outside_landscape=[]
    for sample in c['samples']:
        n=sample['members'][0];p=n['feet_cm'];component=re.sub('UEDPIE_[0-9]+_','',n['floor_component'])
        assert n['walkable_floor'] and n['movement_mode']==1 and n['resources']==r['startup_resources'][0] and p[2]>40
        inside=abs(p[0]-x)<=ex and abs(p[1]-y)<=ey
        if inside:
            assert component in allowed and p[2]<=300
            observations.append({'game_seconds':sample['game_seconds'],'feet_cm':p,'component':component,'mesh':allowed[component]})
        elif 'Landscape' in component:outside_landscape.append(p)
    assert len(observations)==22 and not any(o['component']==bridge['component'] for o in observations)
    evidence={'prior_specialized_status_preserved':'negative','separately_audited_movement':'original_player_outward_native_SUCCESS_grounded_endpoint',
        'xy_error_cm':xy,'feet_error_cm':z,'actual_samples':len(c['samples']),'bridge_overlay_samples':observations,'outside_bridge_landscape_samples':outside_landscape,
        'raw_sources':{str(p.relative_to(root)):digest(p) for p in [first/'result.json',first/'exit.json',old/'cases.json',old/'discovery.json',invpath]},
        'not_uninterrupted_roundtrip':True,'original_resources_exact':True}
    dest=base/'bank_reverse_v3_20261007';dest.mkdir();(dest/'outward_evidence_v1.json').write_text(json.dumps(evidence,indent=2)+'\n')
    route=b['routes'][0];route={**route,'goal_cm':list(f['feet_cm']),'bridge_extent_cm':bridge['extent_cm'],
        'allowed_overlay_supports':allowed,'source_is_prior_goal_for_reverse':True}
    newbank={**b,'routes':[route],'planned_legs':1,'source_entry':'bridge_reverse_v3','directions':['back'],'role_indices':[0],
        'prior_observed_arrival_cm':f['feet_cm'],'not_cross_entry_state_continuity':True,'outward_evidence_sha256':digest(dest/'outward_evidence_v1.json')}
    (dest/'cases.json').write_text(json.dumps(newbank,indent=2)+'\n')
    source=e/'FormalMapVerificationV1/solo_v1_20261007/ue_verify.py';audit=json.loads((source.parent/'audit_v1.json').read_text());assert digest(source)==audit['inputs']['ue_verify.py']
    text=source.read_text();changes={"BANK_PATH=STORE/'Evidence/FormalMapVerificationV1/case_bank_v3_20261007/cases.json'":"BANK_PATH=Path(os.environ['CS549_BRIDGE_BANK'])",
        'Docs/Development/MissionLoopV1/FORMAL_ROLE_SQUAD_TEST_PLAN_20261007.md':'Docs/Development/MissionLoopV1/BRIDGE_OVERLAY_ADMISSION_20261007.md',
        "for route_index in ([0] if STAGE=='Early' else range(3)):":'for route_index in range(len(routes)):',
        "for i in ([0,1,3] if STAGE=='Early' else range(6)):":"for i in bank['role_indices']:",
        "for direction in ('out','back'):queue.append({'id':f'{STAGE.lower()}": "for direction in bank['directions']:queue.append({'id':f'{STAGE.lower()}",
        "middle=(unreal.Vector(*current['source_cm'])+unreal.Vector(*current['goal_cm']))*.5":"middle=unreal.Vector(*routes[current['route']]['bridge_origin_cm'])",
        'look=middle+unreal.Vector(0,0,95);location=middle+unreal.Vector(250,-200,650)':'look=middle+unreal.Vector(0,0,300);location=middle+unreal.Vector(700,-700,2400)'}
    for oldvalue,newvalue in changes.items():assert text.count(oldvalue)==1,oldvalue;text=text.replace(oldvalue,newvalue)
    needle='            all_arrived=True\n';assert text.count(needle)==1
    addition="""            route=routes[current['route']];center=route['bridge_origin_cm'];extent=route['bridge_extent_cm']
            inside=[n for n in data if abs(n['feet_cm'][0]-center[0])<=extent[0] and abs(n['feet_cm'][1]-center[1])<=extent[1]]
            for n in inside:
                component=n['floor_component'].replace('UEDPIE_0_','')
                if component not in route['allowed_overlay_supports'] or not 40<n['feet_cm'][2]<=300:reject('bridge_overlay_support_not_admitted',now,n);return
            if inside and not current.get('bridge_capture_requested'):
                current['bridge_capture_requested']=True;capture(current['id']+'_bridge_overlay',now)
            all_arrived=True
""";text=text.replace(needle,addition)
    needle='            if all_arrived:\n                current.update';assert text.count(needle)==1
    addition="""            if all_arrived:
                route=routes[current['route']];center=route['bridge_origin_cm'];extent=route['bridge_extent_cm']
                visited=[n for sample in current['samples'] for n in sample['members'] if abs(n['feet_cm'][0]-center[0])<=extent[0] and abs(n['feet_cm'][1]-center[1])<=extent[1]]
                if not visited:reject('bridge_footprint_unobserved',now,data);return
                if any(abs(p[0]-center[0])>3500 or abs(p[1]-center[1])>3500 for m in current['members'] for p in m['request']['path_cm']):reject('bridge_neighborhood_detour',now,data);return
                current['actual_bridge_overlay_samples']=len(visited)
                current.update""";text=text.replace(needle,addition)
    ast.parse(text);(dest/'ue_bridge_verify.py').write_text(text)
    (dest/'adaptation.json').write_text(json.dumps({'original_source_sha256':digest(source),'bank_sha256':digest(dest/'cases.json'),
        'adapted_source_sha256':digest(dest/'ue_bridge_verify.py'),'replacements':changes,
        'extra_observation':'verified original overlay footprint/support gate; reverse only; no outward rerun'},indent=2)+'\n')
    print(json.dumps({'bank':str(dest),'prior_movement_end_xy_cm':xy,'prior_movement_end_feet_cm':z,'bridge_overlay_samples':len(observations),
        'reverse_source_cm':f['feet_cm'],'reverse_goal_cm':route['source_cm'],'allowed_overlay_components':len(allowed)}))

if __name__=='__main__':prepare(ROOT)
