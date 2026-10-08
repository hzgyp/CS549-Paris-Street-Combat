"""Freeze new near-hub interaction sites and a separate observer; no terrain replays."""
import ast,json,math,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest

def main():
    parent=STORE/'Evidence/NativeConvergenceV1';original=json.loads((parent/'bank_v1_20261007/bank.json').read_text())
    audit=json.loads((parent/'full_v1_20261007/audit.json').read_text());assert audit['status']=='pass_independent_convergence_audit' and audit['cases']==134
    out=parent/'crowd_bank_v1_20261007';assert not out.exists()
    source=STORE/original['source'];f=np.load(source/'derived/saved_filters.npz');nodes=json.loads((source/'saved_links/nodes.json').read_text())
    h=original['hub'];ids=np.flatnonzero(f['base']&(f['group']==h['group'])&(f['count3']>=13)&~f['quarantine'])
    excluded={tuple(s['source_cm'][:2]) for s in original['cases']};selected=[]
    for angle in (0,120,240):
        rad=math.radians(angle);desired=np.array(h['feet_cm'][:2])+1500*np.array([math.cos(rad),math.sin(rad)])
        xy=np.c_[-50400+(f['c'][ids]+.5)*25,50400-(f['r'][ids]+.5)*25];dd=np.sum((xy-desired)**2,axis=1)
        for index in np.argsort(dd):
            k=int(ids[index]);n=nodes[k];p=n['feet_cm'][:2]
            if tuple(p) in excluded or math.dist(p,h['feet_cm'][:2])<500 or math.dist(p,h['feet_cm'][:2])>2500:continue
            if any(math.dist(p,s['feet_cm'][:2])<300 for s in selected):continue
            selected.append(n);break
    assert len(selected)==3
    cases=[]
    for j,(n,role) in enumerate(zip(selected,('allied','allied','german'))):
        cases.append({'id':f'crowd_{j}_{role}','origin_index':j,'role':role,'source_node_id':n['id'],'source_cm':n['feet_cm'],
                      'source_component':n['component'],'source_mesh':n['mesh'],'c':n['c'],'r':n['r'],'layer':n['layer'],
                      'survey_group':int(f['group'][n['id']]),'source_scope':'saved','native_navigation_scope':'saved'})
    bank={**original,'schema':'paris_native_crowd_bank_v1','cases':cases,'early_ids':[],'origins':selected,
          'original_bank_sha256':digest(parent/'bank_v1_20261007/bank.json'),'terrain_audit_sha256':digest(parent/'full_v1_20261007/audit.json'),
          'plan_sha256':digest(ROOT/'Docs/Development/MissionLoopV1/NATIVE_CONVERGENCE_CROWD_PLAN_20261007.md')}
    bank.pop('runtime_samples_per_role');bank.pop('tile_cm')
    bank['runtime_samples_by_role']={'allied':2,'german':1};bank['crowd_agents']=3
    out.mkdir();(out/'bank.json').write_text(json.dumps(bank,indent=2)+'\n')
    src=(ROOT/'Tools/Integration/NativeConvergenceV1/ue_convergence.py').read_text()
    replacements={"Evidence/NativeConvergenceV1/bank_v1_20261007/bank.json":"Evidence/NativeConvergenceV1/crowd_bank_v1_20261007/bank.json",
        "'source_white_scope':'full'":"'source_white_scope':'saved'",
        "assert STAGE!='Crowd','Crowd requires a distinct frozen bank after terrain audit'":"assert STAGE=='Crowd','Separate frozen crowd observer only'",
        "report['hub_standing']=hub_checks;phase='next';write();return":"""report['hub_standing']=hub_checks
            report['crowd_move_ignore_before_travel']=[]
            for a in bodies:
                for other in bodies:
                    if other!=a:a.capsule_component.ignore_actor_when_moving(other,False)
                remaining=[x.get_path_name() for x in a.capsule_component.copy_array_of_move_ignore_actors()]
                assert not remaining
                report['crowd_move_ignore_before_travel'].append({'actor':a.get_path_name(),'remaining':remaining,'pawn_response':str(a.capsule_component.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN))})
            assert all(x['before']==x['after'] for x in report['avoidance_group_isolation'])
            phase='next';write();return""",
        "bodies[i].set_actor_hidden_in_game(True);bodies[i].set_actor_enable_collision(False);bodies[i].character_movement.set_component_tick_enabled(False)":"bodies[i].character_movement.stop_movement_immediately()",
        "sample={**x,'game_seconds':t":"sample={**x,'other_bodies_cm':{str(j):xyz(bodies[j].get_actor_location()) for j in (1,2,3) if j!=i},'game_seconds':t"}
    for old,new in replacements.items():assert src.count(old)==1,(old,src.count(old));src=src.replace(old,new)
    ast.parse(src);driver=ROOT/'Tools/Integration/NativeConvergenceV1/ue_crowd.py';assert not driver.exists();driver.write_text(src)
    launcher=(ROOT/'Tools/Integration/NativeConvergenceV1/run_convergence.ps1').read_text()
    launcher=launcher.replace("[ValidateSet('Early','Full')][string]$Stage='Early'","[ValidateSet('Crowd')][string]$Stage='Crowd'")
    launcher=launcher.replace("if($Stage -eq 'Full'){","if($Stage -eq 'Crowd'){")
    launcher=launcher.replace('early_v2_20261007/audit.json','full_v1_20261007/audit.json')
    launcher=launcher.replace('-or -not $taskEarly.early_mechanism_pass','-or $taskEarly.cases -ne 134')
    launcher=launcher.replace('ue_convergence.py','ue_crowd.py').replace("$(if($Stage -eq 'Early'){12}else{60})","12")
    p=ROOT/'Tools/Integration/NativeConvergenceV1/run_crowd.ps1';assert not p.exists();p.write_text(launcher)
    print(json.dumps({'bank':str(out),'cases':cases,'bank_sha256':digest(out/'bank.json')}))

if __name__=='__main__':main()
