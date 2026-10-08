"""Independently recompute fine native admission and exact world spacing."""
import argparse,json,math,re,sys
from collections import Counter
from pathlib import Path
from grid_core import PROFILE,cell_xy,world_cell,digest

def audit(entry,saved_only=False):
    root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/NPCInteractionV1'))
    from common import guard_rows,guards_match
    r=json.loads((entry/'result.json').read_text());e=json.loads((entry/'exit.json').read_text(encoding='utf-8-sig'))
    if saved_only:
        assert r['status']=='failed_fine_grid_global_admission' and len(r['errors'])==1
        assert 'Offline candidate preparation failed' in r['errors'][0]
        assert not (entry/'full/samples.jsonl').exists() and not (entry/'links').exists()
    else:assert r['status']=='complete_finite_native_fine_grid_geometry' and not r['errors']
    assert e['exit_code']==e['strict_log_errors']==0 and r['protected_bytes_unchanged'] and r['old_helpers_unchanged']
    assert r['profile']==PROFILE and not r['map_saved'] and not r['formal_navigation_changed'] and not r['final_layout_selected']
    assert r['native_isolation_state']=={'characters':1,'controllers':0,'production_contaminants':[]}
    assert all(v['before']==v['after'] and v['simulation_disabled'] and v['max_drift_cm']==0 for v in r['static_vehicle_admission'])
    rows=json.loads((entry/'guards_before.json').read_text());assert len(rows)==703 and guards_match(rows)
    assert len(guard_rows())==703 and guards_match(guard_rows())
    assert all(digest(Path(p))==h for p,h in r['helper_guards'].items())
    assert r['grid_helper_sha256']==digest(root/'Unreal/ParisStreetCombat/Plugins/ParisGridSurveyV1/Binaries/Win64/UnrealEditor-ParisGridSurveyV1.dll')
    spec=json.loads((entry/'grid_spec.json').read_text());assert spec['cell_cm']==25 and spec['rows']==spec['columns']==4032
    assert spec['xmin_cm']==spec['ymin_cm']==-50400 and spec['xmax_cm']==spec['ymax_cm']==50400
    summaries={};hashes={};max_xy=max_delta=0
    for name in (('saved','saved_links') if saved_only else ('saved','full','saved_links','links')):
        counts=Counter();count=admitted=0;path=entry/name/'samples.jsonl'
        for expected,line in enumerate(path.open(encoding='utf-8')):
            row=json.loads(line);assert row['id']==expected;count+=1;admitted+=int(row['admitted']);counts[row['reason']]+=1
            if name in ('saved','full'):
                xy=cell_xy(spec,row['c'],row['r']);assert xy==row['xyz'][:2] and world_cell(spec,*xy)==(row['c'],row['r'])
                assert row['exact_surface'] and row['xy_drift_cm']<=.01
                assert all(math.isfinite(v) for v in row['nav_cm']+row['feet_cm'])
                max_xy=max(max_xy,math.dist(xy,row['nav_cm'][:2]))
                delta=abs(row['feet_cm'][2]-row['nav_cm'][2]);assert abs(delta-row['height_delta_cm'])<1e-6
                valid=row['floor_walkable'] and not row['floor_penetrating'] and delta<=35 and not row['blockers']
                assert row['admitted']==valid
                if valid:max_delta=max(max_delta,delta)
            else:
                a=row['start_feet_cm'];b=row['end_feet_cm'];assert abs(abs(a[0]-b[0])+abs(a[1]-b[1])-25)<.01
                valid=row['surface_connected'] and not row['capsule_blocked'] and abs(a[2]-b[2])<=45
                assert row['admitted']==valid
                if valid:
                    assert math.dist(row['reached_nav_cm'][:2],row['end_nav_cm'][:2])<=.01 and abs(row['reached_nav_cm'][2]-row['end_nav_cm'][2])<=1
        assert count==r['passes'][name]['recorded']==r['passes'][name]['candidate_count'] and admitted==r['passes'][name]['geometry_clear']
        h=digest(path);assert h==r['passes'][name]['samples_sha256'];hashes[name]=h
        summaries[name]={'records':count,'admitted':admitted,'reasons':dict(counts)}
        print(name,count,admitted,flush=True)
    log=root/'tmp/fine-map-grid-v1'/(entry.name+'.log')
    assert not re.search(r'Error:|Fatal:|Ensure condition failed|=== Handled ensure|RegistrationFailed_AgentNotValid|NavData.*will be removed|Navigation NOT building|navigation build is locked',log.read_text(encoding='utf-8',errors='replace'))
    if not saved_only and r.get('reused_saved_source'):
        receipt=r['reused_saved_source'];source=Path(receipt['source_entry'])
        assert receipt['status']=='pass_saved_scope_native_audit'
        for name in ('saved','saved_links'):assert hashes[name]==receipt['source_hashes'][name]==digest(source/name/'samples.jsonl')
    result={'status':'pass_saved_scope_native_audit' if saved_only else 'pass_independent_fine_native_audit','false_cell_or_link_admissions':0,'spec':spec,'passes':summaries,
            'max_xy_drift_cm':max_xy,'max_admitted_height_delta_cm':max_delta,'protected_rows':703,'guards_exact':True,'helper_hashes':r['helper_guards'],
            'grid_helper_sha256':r['grid_helper_sha256'],'source_hashes':hashes,'source_entry':str(entry.resolve()),'exit':e,'static_only':True,'all_roles_or_squads_passed':False,
            'whole_source_entry_passed':not saved_only,'explicit_reused_saved_source':r.get('reused_saved_source')}
    target=entry/('saved_scope_audit.json' if saved_only else 'audit_native.json');assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('entry',type=Path);p.add_argument('--saved-scope-only',action='store_true');a=p.parse_args();audit(a.entry,a.saved_scope_only)
