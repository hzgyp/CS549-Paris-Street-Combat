"""Independent finite-request and no-false-admission audit of native grid receipts."""
import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

from grid_core import PROFILE,cell_xy,digest,world_cell


def audit(entry,root):
    sys.path.insert(0,str(root/'Tools/Integration/NPCInteractionV1'))
    from common import guard_rows,guards_match
    r=json.loads((entry/'result.json').read_text(encoding='utf-8'))
    e=json.loads((entry/'exit.json').read_text(encoding='utf-8-sig'))
    assert r['status']=='complete_finite_native_grid_geometry' and not r['errors']
    assert e['exit_code']==e['strict_log_errors']==0
    assert r['protected_bytes_unchanged'] and r['old_helpers_unchanged']
    assert len(guard_rows())==703 and guards_match(guard_rows())
    assert not r['map_saved'] and not r['formal_navigation_changed'] and not r['final_layout_selected']
    assert r['profile']==PROFILE
    assert r['native_isolation_state']=={'characters':1,'controllers':0,'production_contaminants':[]}
    assert all(v['before']==v['after'] and v['simulation_disabled'] and v['max_drift_cm']==0 for v in r['static_vehicle_admission'])
    assert all(digest(Path(p))==h for p,h in r['helper_guards'].items())
    assert r['grid_helper_sha256']==digest(root/'Unreal/ParisStreetCombat/Plugins/ParisGridSurveyV1/Binaries/Win64/UnrealEditor-ParisGridSurveyV1.dll')
    spec=json.loads((entry/'grid_spec.json').read_text(encoding='utf-8'))
    summaries={};sources={};max_xy=max_height=0
    for name in ('saved','full','saved_links','links','sight'):
        count=passed=0;reasons=Counter()
        path=entry/name/'samples.jsonl'
        for expected,line in enumerate(path.open(encoding='utf-8')):
            row=json.loads(line);assert row['id']==expected
            count+=1;passed+=int(row['admitted']);reasons[row['reason']]+=1
            if name in ('saved','full'):
                xy=cell_xy(spec,row['c'],row['r'])
                assert row['xyz'][:2]==xy and world_cell(spec,*xy)==(row['c'],row['r'])
                assert row['exact_surface'] and row['xy_drift_cm']<=.01
                assert all(math.isfinite(x) for x in row['nav_cm']+row['feet_cm'])
                max_xy=max(max_xy,math.dist(row['nav_cm'][:2],xy))
                delta=abs(row['feet_cm'][2]-row['nav_cm'][2])
                assert abs(delta-row['height_delta_cm'])<1e-6
                valid=row['floor_walkable'] and not row['floor_penetrating'] and delta<=35 and not row['blockers']
                assert row['admitted']==valid,'False cell admission'
                if valid:max_height=max(max_height,delta)
            elif name in ('links','saved_links'):
                a=row['start_feet_cm'];b=row['end_feet_cm']
                assert abs(abs(a[0]-b[0])+abs(a[1]-b[1])-100)<.01,'Diagonal/corner-cut link'
                valid=row['surface_connected'] and not row['capsule_blocked'] and abs(a[2]-b[2])<=45
                assert row['admitted']==valid,'False link admission'
                if valid:
                    assert math.dist(row['reached_nav_cm'][:2],row['end_nav_cm'][:2])<=.01
                    assert abs(row['reached_nav_cm'][2]-row['end_nav_cm'][2])<=1
            else:
                assert row['eye_height_cm']==140 and row['admitted']==(row['visible_ab'] and row['visible_ba'])
                assert 500-.01<=math.dist(row['start_feet_cm'][:2],row['end_feet_cm'][:2])<=2000+.01
        assert count==r['passes'][name]['candidate_count']==r['passes'][name]['recorded']
        assert passed==r['passes'][name]['geometry_clear']
        sources[str(path.relative_to(entry))]=digest(path)
        assert sources[str(path.relative_to(entry))]==r['passes'][name]['samples_sha256']
        summaries[name]={'recorded':count,'admitted':passed,'excluded':count-passed,'reasons':dict(reasons)}
    log=root/'tmp/map-grid-v1'/(entry.name+'.log')
    assert not re.search(r'Error:|Fatal:|Ensure condition failed|=== Handled ensure|RegistrationFailed_AgentNotValid|NavData.*will be removed|Navigation NOT building|navigation build is locked',log.read_text(encoding='utf-8',errors='replace'))
    sources.update({p.name:digest(p) for p in (entry/'result.json',entry/'exit.json',entry/'grid_spec.json',log)})
    result={'status':'pass_independent_native_grid_audit','entry':entry.name,'grid':spec,'passes':summaries,
            'max_surface_xy_drift_cm':max_xy,'max_admitted_nav_to_feet_delta_cm':max_height,
            'false_cell_or_link_admissions':0,'all_results_are_static_geometry':True,
            'whole_map_physical_movement_proven':False,'protected_rows':703,'exit':e,'sources':sources}
    target=entry/'audit_native_v1.json';assert not target.exists()
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','passes','max_surface_xy_drift_cm','false_cell_or_link_admissions')}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    a=p.parse_args();audit(a.entry,a.root)
