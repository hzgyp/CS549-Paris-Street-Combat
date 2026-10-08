"""Two-entry player crossing proof; keep the first specialized negative intact."""
import json,math,re,sys
from pathlib import Path
from grid_core import digest

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import guard_rows,guards_match

def audit(base):
    first=base/'runtime_C_v1_20261007';second=base/'runtime_reverse_v3_20261007';bank=base/'bank_reverse_v3_20261007'
    b=json.loads((bank/'cases.json').read_text());route=b['routes'][0];results=[];sources={};captures=[]
    inventory_path=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/PureMapSurveyV1/inventory_v4_20261007/inventory.json'
    inv={n['component']:n for n in json.loads(inventory_path.read_text())['blockers']};cx,cy,_=route['bridge_origin_cm'];ex,ey,_=route['bridge_extent_cm']
    for entry,direction in [(first,'out'),(second,'back')]:
        r=json.loads((entry/'result.json').read_text());end=json.loads((entry/'exit.json').read_text(encoding='utf-8-sig'))
        assert end['exit_code']==end['strict_log_errors']==0 and r['vehicle_max_drift_cm']==0
        assert r['protected_bytes_unchanged'] and r['current_guards']==703 and r['original_player_possession_preserved']
        assert r['map_saved']==r['nav_rebuilt']==r['final_layout_selected']==False and r['native_bootstrap_gate']=='pass_original_six_bodies_five_brains_selected_bindings_resources'
        assert len(r['formal_profiles'])==6 and r['formal_profiles'][0]['class'].endswith('/BP_PCParisPlayerV1.BP_PCParisPlayerV1_C')
        for field,plugin in [('helper_sha256','ParisFormalSurveyV1'),('pure_helper_sha256','ParisMapSurveyV1')]:
            assert r[field]==digest(ROOT/f'Unreal/ParisStreetCombat/Plugins/{plugin}/Binaries/Win64/UnrealEditor-{plugin}.dll')
        assert len(r['cases'])==1;c=r['cases'][0];assert c['direction']==direction;m=c['members'][0];assert m['index']==0
        if direction=='out':assert c['status']=='negative' and c['reason']=='actual_bridge_floor_unobserved'
        else:assert c['status']=='passed' and not r['errors']
        s=m['standing'];f=m['final'];q=m['request'];event=m['completion']
        assert s['standing_pass'] and not s['blockers'] and s['walkable_floor'] and s['movement_mode']==1
        assert q['started'] and event['result_code']==0 and event['controller']==q['controller'] and event['request_id']==q['request_id']
        assert f['walkable_floor'] and f['movement_mode']==1 and f['controller']['status_code']==0
        xy=math.dist(f['feet_cm'][:2],m['goal_cm'][:2]);z=abs(f['feet_cm'][2]-m['goal_cm'][2]);assert xy<=35 and z<=35
        inside=[];maxstep=0
        for sample in c['samples']:
            n=sample['members'][0];p=n['feet_cm'];assert n['walkable_floor'] and n['movement_mode']==1 and n['resources']==r['startup_resources'][0]
            assert abs(p[0]-cx)<=3500 and abs(p[1]-cy)<=3500 and p[2]>40
            component=re.sub(r'UEDPIE_[0-9]+_','',n['floor_component'])
            if abs(p[0]-cx)<=ex and abs(p[1]-cy)<=ey:
                assert 40<p[2]<=300 and component in route['allowed_overlay_supports'] and component in inv
                assert inv[component]['mesh']==route['allowed_overlay_supports'][component] and inv[component]['mesh'].startswith('/Game/WW2City/Environment/')
                inside.append({'feet_cm':p,'component':component,'mesh':inv[component]['mesh']})
        assert inside
        for p in q['path_cm']:assert abs(p[0]-cx)<=3500 and abs(p[1]-cy)<=3500
        normal=route['bank_normal_xy'];side=lambda p:sum((p[j]-route['bridge_origin_cm'][j])*normal[j] for j in [0,1])
        assert side(m['source_cm'])*side(m['goal_cm'])<0 and min(abs(side(m['source_cm'])),abs(side(m['goal_cm'])))>900
        log=ROOT/'tmp/bridge-connectivity-v1'/(entry.name+'.log');assert not re.search(r'Error:|Fatal:|Ensure condition failed|Assertion failed|Accessed None|BOOTSTRAP_FAILED',log.read_text(errors='replace'))
        for p in [entry/'result.json',entry/'exit.json',entry/'ue_bridge_verify.py',log]:sources[p.relative_to(ROOT).as_posix()]=digest(p)
        for cap in r['captures']:
            p=entry/cap['file'];assert p.is_file();captures.append({'file':p.relative_to(ROOT).as_posix(),'sha256':digest(p)})
        results.append({'entry':entry.name,'direction':direction,'raw_case_status':c['status'],'independent_native_move_status':'pass',
            'actual_bridge_overlay_samples':len(inside),'overlay_meshes':sorted({n['mesh'] for n in inside}),
            'xy_error_cm':xy,'feet_error_cm':z,'native_path_length_cm':q['path_length_cm'],'exit':end})
    first_r=json.loads((first/'result.json').read_text());observed=first_r['cases'][0]['members'][0]['final']['feet_cm']
    assert route['goal_cm']==observed and route['source_cm']==first_r['cases'][0]['members'][0]['source_cm']
    r2=json.loads((second/'result.json').read_text());assert r2['bank_sha256']==digest(bank/'cases.json') and r2['summary']=={'planned':1,'recorded':1,'passed':1,'negative':0,'unmeasured':0}
    assert r2['cases'][0]['members'][0]['source_placement'] # New entry, not continuous actor state.
    assert len(guard_rows())==703 and guards_match(guard_rows())
    for p in [bank/'cases.json',bank/'adaptation.json',bank/'outward_evidence_v1.json',inventory_path]:sources[p.relative_to(ROOT).as_posix()]=digest(p)
    result={'status':'pass_original_player_two_direction_cross_bank_overlay_route','confirmed_two_way_roles':[0],
        'bridge_id':'C','cases':results,'first_specialized_negative_unchanged':True,'first_other_five_legs_unmeasured':True,
        'independent_entries_not_uninterrupted_roundtrip':True,'captures':captures,'sources':sources,'protected_rows':703,
        'other_bridges_unaccepted':['A','B'],'not_whole_map_or_arbitrary_deck_admission':True}
    target=second/'audit_v1.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':audit((ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/BridgeConnectivityV1').resolve())
