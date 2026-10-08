"""Freeze new exact grid-center test routes and adapt an authenticated observer."""
import argparse
import ast
import json
import math
from collections import deque
from pathlib import Path

from grid_core import digest
from planning_data import PlanningData


def prepare(entry,root):
    data=PlanningData(entry)
    store=root/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
    old_bank_path=store/'Evidence/FormalMapVerificationV1/case_bank_v3_20261007/cases.json'
    old_bank=json.loads(old_bank_path.read_text(encoding='utf-8'))
    parking=old_bank['parking_sites']
    eligible=[n for n in data.nodes if data.base(n,True) and
              min(math.dist(n['feet_cm'][:2],p['feet_cm'][:2]) for p in parking)>=1000]
    assert eligible,'No current-game grid candidates'
    def paths(seed,max_steps=24):
        seen={seed['id']:None};q=deque([(seed['id'],0)])
        while q:
            k,depth=q.popleft()
            if depth>=max_steps:continue
            for target in sorted(data.outgoing[k]):
                if target in seen:continue
                other=data.nodes[target]
                if not data.base(other,True,seed['saved_group']) or not data.reciprocal(data.nodes[k],other,True):continue
                if min(math.dist(other['feet_cm'][:2],p['feet_cm'][:2]) for p in parking)<1000:continue
                seen[target]=k;q.append((target,depth+1))
        return seen
    def chain(seen,target):
        path=[target]
        while seen[path[-1]] is not None:path.append(seen[path[-1]])
        return list(reversed(path))
    routes=[];used=set()
    for name,focus in [('road_connection',[14326,-10374]),('local_connection',[14744,-14359])]:
        seeds=sorted((n for n in eligible if n['road']),key=lambda n:(math.dist(n['feet_cm'][:2],focus),n['id']))
        found=None
        for seed in seeds[:100]:
            seen=paths(seed,12)
            targets=[data.nodes[k] for k in seen if 500<=math.dist(data.nodes[k]['feet_cm'][:2],seed['feet_cm'][:2])<=1000
                     and abs(data.nodes[k]['feet_cm'][2]-seed['feet_cm'][2])<=35 and k not in used]
            if not targets:continue
            target=min(targets,key=lambda n:(abs(math.dist(n['feet_cm'][:2],seed['feet_cm'][:2])-700),n['id']))
            found=(seed,target,chain(seen,target['id']));break
        assert found,'No admitted local grid route '+name
        s,t,path=found;used.update([s['id'],t['id']])
        routes.append({'category':name,'source_cm':s['feet_cm'],'goal_cm':t['feet_cm'],
                       'source_sites':[],'goal_sites':[],'source_node':s['id'],'goal_node':t['id'],'grid_path':path,
                       'saved_group':s['saved_group'],'height_delta_cm':t['feet_cm'][2]-s['feet_cm'][2]})
    # Height is conditional: a clear isolated roof is not a connected height route.
    height=None
    height_candidates=sorted(eligible,key=lambda n:(math.dist(n['feet_cm'][:2],[13898.5,-16449.25]),n['id']))
    for seed in height_candidates[:500]:
        seen=paths(seed,24)
        targets=[data.nodes[k] for k in seen if k not in used and
                 50<=abs(data.nodes[k]['feet_cm'][2]-seed['feet_cm'][2])<=300 and
                 math.dist(data.nodes[k]['feet_cm'][:2],seed['feet_cm'][:2])>=500]
        if targets:
            target=min(targets,key=lambda n:(len(chain(seen,n['id'])),abs(n['feet_cm'][2]-seed['feet_cm'][2]),n['id']))
            height=(seed,target,chain(seen,target['id']));break
    if height:
        s,t,path=height
        routes.append({'category':'height_connection','source_cm':s['feet_cm'],'goal_cm':t['feet_cm'],
                       'source_sites':[],'goal_sites':[],'source_node':s['id'],'goal_node':t['id'],'grid_path':path,
                       'saved_group':s['saved_group'],'height_delta_cm':t['feet_cm'][2]-s['feet_cm'][2]})
    dest=entry/'roundtrip_bank';dest.mkdir()
    bank={'routes':routes,'parking_sites':parking,'source_entry':entry.name,'grid_spec':data.spec,
          'planned_legs':len(routes)*6,'height_route_admitted':bool(height),'final_layout_selected':False,
          'positions_are_temporary_tests':True,'old_parking_bank_sha256':digest(old_bank_path)}
    (dest/'cases.json').write_text(json.dumps(bank,indent=2)+'\n',encoding='utf-8')
    source=store/'Evidence/FormalMapVerificationV1/solo_v1_20261007/ue_verify.py'
    old_audit=json.loads((store/'Evidence/FormalMapVerificationV1/solo_v1_20261007/audit_v1.json').read_text(encoding='utf-8'))
    assert old_audit['status']=='pass_independent_formal_receipt_audit'
    assert digest(source)==old_audit['inputs']['ue_verify.py'],'Original completed observer changed'
    text=source.read_text(encoding='utf-8')
    replacements={"BANK_PATH=STORE/'Evidence/FormalMapVerificationV1/case_bank_v3_20261007/cases.json'":"BANK_PATH=Path(os.environ['CS549_GRID_BANK'])",
                  "Docs/Development/MissionLoopV1/FORMAL_ROLE_SQUAD_TEST_PLAN_20261007.md":"Docs/Development/MissionLoopV1/MAP_GRID_ROUNDTRIP_PLAN_20261007.md",
                  "for route_index in ([0] if STAGE=='Early' else range(3)):":"for route_index in range(len(routes)):"}
    for old,new in replacements.items():
        assert text.count(old)==1,('Frozen observer adaptation contract',old)
        text=text.replace(old,new)
    text=text.replace("report['pre_admission_latch_enabled']=BOOTSTRAP_LATCH",
                      "report['grid_mapping_source_entry']=bank['source_entry']\nreport['grid_coordinate_roundtrip_only']=True\nreport['pre_admission_latch_enabled']=BOOTSTRAP_LATCH")
    ast.parse(text)
    (dest/'ue_grid_roundtrip.py').write_text(text,encoding='utf-8')
    adaptation={'original_source':source.relative_to(root).as_posix(),'original_source_sha256':digest(source),
                'changes':replacements,'bank_sha256':digest(dest/'cases.json'),'adapted_source_sha256':digest(dest/'ue_grid_roundtrip.py')}
    (dest/'adaptation.json').write_text(json.dumps(adaptation,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'planned_legs':bank['planned_legs'],'height_route_admitted':bool(height),'routes':routes}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    a=p.parse_args();prepare(a.entry,a.root)
