"""Freeze bounded cases from authenticated completed survey, no UE mutation."""
import json, math, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
OUT=STORE/'Evidence/FormalMapVerificationV1/case_bank_v3_20261007'
assert not OUT.exists(), 'Preserve unique case bank'
base=STORE/'Evidence/PureMapSurveyV1/fixed_static_vehicle_v20_20261007'
a=json.loads((base/'audit_v1.json').read_text())
r=json.loads((base/'survey.json').read_text())
assert a['status']=='pass_receipt_audit' and a['full_finite_case_coverage'] and not r['errors']
assert len(guard_rows())==703 and guards_match(guard_rows())
inventory=json.loads((base.parent/'inventory_v4_20261007/inventory.json').read_text())
blockers={b['component']:b for b in inventory['blockers']}
old=json.loads((STORE/'Evidence/MissionConnectivityV1/current_query_v1_20261007/query.json').read_text())
bounds=old['nav_bounds']; origin=bounds['origin_cm']; extent=bounds['extent_cm']

def inside(p):
    return all(origin[i]-extent[i]+(300 if i<2 else 25)<=p[i]<=origin[i]+extent[i]-(300 if i<2 else 25) for i in range(3))

def eligible_floor(f):
    comp=re.sub(r'UEDPIE_\d+_','',f.get('component',''))
    b=blockers.get(comp,{})
    return f.get('walkable_floor') and '/Game/WW2City/' in comp and 'LV_Proxy' not in comp and 'Landscape' not in comp and not str(b.get('mesh','')).startswith('/Engine/BasicShapes/')

passed=[c for c in r['cases'] if c['status']=='passed']
by_edge={(c['from'],c['to']):c for c in passed}
choices=[]
for c in passed:
    reverse=by_edge.get((c['to'],c['from']))
    if not reverse or c['id']>reverse['id']:continue
    if not inside(c['source_cm']) or not inside(c['goal_cm']):continue
    if not eligible_floor(c['standing']['native_floor']) or not eligible_floor(c['final_native_floor']):continue
    floors=[s['native_floor'] for s in c['samples'] if s['native_floor'].get('walkable_floor')]
    if not floors or not all(eligible_floor(f) for f in floors) or not any('BP_Road' in f.get('component','') for f in floors):continue
    if not 400<=c['path_length_cm']<=2000:continue
    planar=math.dist(c['source_cm'][:2],c['goal_cm'][:2]); dz=abs(c['source_cm'][2]-c['goal_cm'][2])
    turn=0
    for p,q,s in zip(c['path_cm'],c['path_cm'][1:],c['path_cm'][2:]):
        v=[q[i]-p[i] for i in range(2)];w=[s[i]-q[i] for i in range(2)]
        nv=math.hypot(*v);nw=math.hypot(*w)
        if nv>1 and nw>1:turn=max(turn,math.degrees(math.acos(max(-1,min(1,sum(x*y for x,y in zip(v,w))/(nv*nw))))))
    choices.append((c,reverse,planar,dz,turn))

rules=[('flat',lambda x:x[3]<=25 and x[4]<=15 and x[2]>=400),
       ('turning',lambda x:x[3]<=60 and (x[0].get('narrow') or x[4]>=40)),
       ('height',lambda x:75<=x[3]<=450)]
points=[]
for c in passed:
    for index,s in enumerate(c['samples']):
        p=s['body_cm'][:2]+[s['foot_z_cm']]
        if inside(p) and eligible_floor(s['native_floor']) and 'MOVE_WALKING' in s['mode']:
            points.append({'feet_cm':p,'source_case':c['id'],'sample_index':index,'floor_component':s['native_floor']['component']})

def sites(center,count,minimum=100):
    candidates=[p for p in points if math.dist(p['feet_cm'][:2],center[:2])<=500 and abs(p['feet_cm'][2]-center[2])<=30]
    ordered=sorted(candidates,key=lambda p:(math.dist(p['feet_cm'],center),p['source_case'],p['sample_index']))
    result=[]
    for p in ordered:
        if all(math.dist(p['feet_cm'][:2],q['feet_cm'][:2])>=minimum for q in result):result.append(p)
        if len(result)==count:return result
    raise AssertionError(('Insufficient distinct authenticated sites',center,count,len(result)))

routes=[];used=set();rejected=[]
for name,predicate in rules:
    options=sorted([x for x in choices if predicate(x) and x[0]['id'] not in used],key=lambda x:x[0]['id'])
    selected=None
    for c,rev,planar,dz,turn in options:
        try:
            candidate={'category':name,'case':c['id'],'reverse_case':rev['id'],'source_cm':c['source_cm'],'goal_cm':c['goal_cm'],
                'from':c['from'],'to':c['to'],'path_cm':c['path_cm'],'length_cm':c['path_length_cm'],'height_cm':dz,'turn_degrees':turn,
                'source_sites':sites(c['source_cm'],5),'goal_sites':sites(c['goal_cm'],5)}
            for direction in ('out','back'):
                start=c['source_cm'] if direction=='out' else c['goal_cm'];goal=c['goal_cm'] if direction=='out' else c['source_cm']
                dx,dy=goal[0]-start[0],goal[1]-start[1];norm=math.hypot(dx,dy)
                requested=[goal[0]+400*dx/norm,goal[1]+400*dy/norm,goal[2]]
                candidate['leader_'+direction]=sites(requested,1)[0]
            selected=candidate;used.add(c['id']);break
        except AssertionError as error:rejected.append({'category':name,'case':c['id'],'reason':str(error),'physical_attempts':0})
    assert selected,('No candidate with complete predeclared fixture capacity',name)
    routes.append(selected)

park_candidates=[p for p in points if all(min(math.dist(p['feet_cm'][:2],s[:2]) for s in [x['source_cm'],x['goal_cm']])>=1500 for x in routes)]
assert park_candidates
parking_center=min(park_candidates,key=lambda p:(math.hypot(*p['feet_cm'][:2]),p['source_case'],p['sample_index']))['feet_cm']
parking=sites(parking_center,6,120)
bank={'status':'frozen_from_authenticated_finite_survey','all_coordinates_temporary_tests':True,'final_layout_selected':False,
    'main_individual_legs':36,'early_control_legs':6,'allied_follow_episodes':6,'german_traffic_episodes':6,'opposing_traffic_episodes':2,'fresh_encounters':3,
    'rules':{'saved_navigation_bounds':bounds,'margin_xy_cm':300,'margin_z_cm':25,'route_length_cm':[400,2000],
        'extra_sites_max_xy_cm':500,'extra_sites_max_z_cm':30,'minimum_separation_cm':100,'selection':'smallest source case ID per eligible category; nearest authenticated walking points; no post-failure substitutions'},
    'routes':routes,'parking_sites':parking,'pre_entry_capacity_rejections':rejected,'inputs':{str(p.relative_to(ROOT)).replace('\\','/'):digest(p) for p in [base/'audit_v1.json',base/'survey.json',base/'graph.json',base.parent/'inventory_v4_20261007/inventory.json',STORE/'Evidence/MissionConnectivityV1/current_query_v1_20261007/query.json',ROOT/'Docs/Development/MissionLoopV1/FORMAL_ROLE_SQUAD_TEST_PLAN_20261007.md',Path(__file__).resolve()]}}
OUT.mkdir(parents=True)
(OUT/'cases.json').write_text(json.dumps(bank,indent=2)+'\n')
(OUT/'prepare_cases.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':bank['status'],'routes':[{k:x[k] for k in ('category','case','reverse_case','length_cm','height_cm','turn_degrees')} for x in routes],'parking_sites':len(parking)},indent=2))
