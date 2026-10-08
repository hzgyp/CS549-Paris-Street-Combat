"""Freeze an explicitly authorized standard-controller control, preserving old banks."""
import ast,copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Tools/Integration/NPCInteractionV1'))
from common import STORE,digest,guard_rows,guards_match
HERE=Path(__file__).parent
OUT=STORE/'Evidence/UEStandardNavigationV1/bank_v1_20261007'

def replace_once(text,old,new):
    assert text.count(old)==1,(old[:80],text.count(old))
    return text.replace(old,new)

def main():
    assert not OUT.exists(),'Frozen identity occupied'
    prior=STORE/'Evidence/NativeConvergenceV1'
    old_path=prior/'bank_v1_20261007/bank.json'
    bank=json.loads(old_path.read_text());assert guard_rows()==bank['protected_rows'] and guards_match(bank['protected_rows'])
    old={s['id']:s for n in ('early_v2_20261007','full_v1_20261007') for s in json.loads((prior/n/'result.json').read_text())['cases']}
    assert len(old)==138
    bank=copy.deepcopy(bank);bank.update(schema='paris_standard_controller_control_v1',
        previous_bank_sha256=digest(old_path),early_ids=[s['id'] for s in bank['cases'] if s['origin_index'] in (0,7)],
        user_authorized_paired_retest=True,original_records_retained=True,
        plan_sha256=digest(ROOT/'Docs/Development/MissionLoopV1/UE_STANDARD_NAV_IMPLEMENTATION_20261007.md'))
    for s in bank['cases']:
        s['previous_status']=old[s['id']]['status'];s['previous_reason']=old[s['id']]['reason']
        s['native_navigation_scope']='expanded_unsaved_standard_controller'
    base=(ROOT/'Tools/Integration/NativeConvergenceV1/ue_convergence.py').read_text()
    text=base.replace('CS549_CONVERGE','CS549_STANDARD').replace('NativeConvergenceV1','UEStandardNavigationV1')
    text=replace_once(text,"STAGE in ('Early','Full','Crowd')","STAGE in ('SavedProbe','Early','Full')")
    text=text.replace("assert STAGE!='Crowd','Crowd requires a distinct frozen bank after terrain audit'","assert STAGE in ('SavedProbe','Early','Full')")
    text=text.replace("STAGE!='Crowd'","True")
    text=text.replace("'navigation_scope':'saved'","'navigation_scope':'saved' if STAGE=='SavedProbe' else 'expanded_unsaved'")
    text=text.replace("'nav_rebuilt':False","'nav_rebuilt':STAGE!='SavedProbe'")
    text=text.replace("if STAGE=='Full':a.character_movement.set_groups_to_avoid(0)","a.character_movement.set_groups_to_avoid(0)")
    text=text.replace("if STAGE=='Full':assert not any(after)","assert not any(after)")
    text=replace_once(text,"phase='setup';busy=False;callback=None;world=None;pc=None;fp=None;bodies=[];controllers=[]","phase='setup';busy=False;callback=None;world=None;pc=None;fp=None;bodies=[];controllers=[]\nnav=None;nav_data=None;expansion_started=0")
    text=replace_once(text,"            levels.editor_request_begin_play();phase='ready';write();return", """            if STAGE=='SavedProbe':
                report['editor_navigation']=navigation_info(editor.get_editor_world(),'saved')
                levels.editor_request_begin_play();phase='ready';write();return
            expand_navigation();phase='expanded_ready';write();return""")
    text=replace_once(text,"        world=editor.get_game_world()", """        if phase=='expanded_ready':
            assert time.monotonic()-expansion_started<600,'Natural navigation unlock deadline'
            state=json.loads(unreal.ParisMapSurveyLibrary.navigation_build_state(nav))
            assert not state.get('error'),state
            if state['manual_build_locked']:return
            bounds=state['registered_bounds'];assert len(bounds)==1
            for key in ('min','max'):
                assert max(abs(a-b) for a,b in zip(bounds[0][key+'_cm'],report['temporary_bounds_cm'][key]))<.1
            unreal.SystemLibrary.execute_console_command(editor.get_editor_world(),'RebuildNavigation')
            expansion_started=time.monotonic();phase='generating';write();return
        if phase=='generating':
            assert time.monotonic()-expansion_started<600,'Unsaved generation deadline'
            if unreal.NavigationSystemV1.is_navigation_being_built(editor.get_editor_world()) or time.monotonic()-expansion_started<3:return
            report['editor_navigation']=navigation_info(editor.get_editor_world(),'expanded_unsaved')
            restore_editor_collision()
            levels.editor_request_begin_play();phase='ready';write();return
        world=editor.get_game_world()""")
    text=replace_once(text,"global phase,busy,world,pc,fp,bodies,controllers,profiles,resources,perf,saving,old_throttle,old_autosave,camera,target,queue,phase_time,last_sample,last_write", "global phase,busy,world,pc,fp,bodies,controllers,profiles,resources,perf,saving,old_throttle,old_autosave,camera,target,queue,phase_time,last_sample,last_write,nav,nav_data,expansion_started")
    text=replace_once(text,"            early=set(bank['early_ids']);queue=[c for c in bank['cases'] if (c['id'] in early)==(STAGE=='Early')]", """            nav,nav_data,_=navigation_objects(world)
            report['pie_navigation']=navigation_info(world,'saved' if STAGE=='SavedProbe' else 'expanded_unsaved')
            early=set(bank['early_ids']);queue=[c for c in bank['cases'] if STAGE=='SavedProbe' or (c['id'] in early)==(STAGE=='Early')]""")
    text=replace_once(text,"assert prior['status']=='pass_independent_convergence_audit' and prior['early_mechanism_pass']", "assert prior['status']=='pass_independent_standard_navigation_audit' and prior['early_mechanism_pass']")
    text=replace_once(text,"            report['profiles']=profiles;report['original_resources']=resources", "            assert all(x['walkable_floor'] and x['movement_mode']==1 for x in profiles),'Initial formal profiles must be grounded'\n            report['profiles']=profiles;report['original_resources']=resources")
    text=replace_once(text,"                req=json.loads(unreal.ParisFormalSurveyLibrary.begin_formal_move(controllers[i],unreal.Vector(*bank['hub']['feet_cm'])))", "                req=standard_request(controllers[i],h['feet_cm'])")
    text=replace_once(text,"                if req.get('rejection') or not req.get('started'):record(i,'negative','saved_navigation_complete_path_rejected');continue", """                if req.get('rejection') or not req.get('started'):record(i,'negative','standard_navigation_request_rejected');continue
                if STAGE=='SavedProbe':record(i,'request_admitted','intentional_cancel_before_travel');continue""")
    text=replace_once(text,"        'negative':sum(c['status']=='negative' for c in report['cases']),", "        'negative':sum(c['status']=='negative' for c in report['cases']),\n        'request_admitted':sum(c['status']=='request_admitted' for c in report['cases']),")
    # No old movement request or Python moving-frame positioning is retained.
    assert 'begin_formal_move' not in text
    additions=(HERE/'standard_api.py').read_text()
    text=replace_once(text,'callback=unreal.register_slate_post_tick_callback(tick)',additions+'\ncallback=unreal.register_slate_post_tick_callback(tick)')
    ast.parse(text)
    OUT.mkdir(parents=True);(OUT/'bank.json').write_text(json.dumps(bank,indent=2)+'\n',encoding='utf-8',newline='\n')
    (HERE/'ue_standard.py').write_text(text,encoding='utf-8',newline='\n')
    runner=(ROOT/'Tools/Integration/NativeConvergenceV1/run_convergence.ps1').read_text()
    runner=runner.replace('NativeConvergenceV1','UEStandardNavigationV1').replace('native-convergence-v1','ue-standard-navigation-v1').replace('CS549_CONVERGE','CS549_STANDARD').replace('ue_convergence.py','ue_standard.py')
    runner=runner.replace("ValidateSet('Early','Full')","ValidateSet('SavedProbe','Early','Full')")
    runner=runner.replace('pass_independent_convergence_audit','pass_independent_standard_navigation_audit')
    runner=runner.replace('-EnablePlugins=ParisFormalSurveyV1','-EnablePlugins=ParisFormalSurveyV1,ParisMapSurveyV1')
    runner=runner.replace("if($Stage -eq 'Early'){12}else{60}","if($Stage -eq 'Full'){70}else{20}")
    runner=runner.replace("$taskResult|Select-Object", "if($taskResult.summary.unmeasured -ne 0){throw 'Finite entry incomplete'}\n$taskResult|Select-Object")
    (HERE/'run_standard.ps1').write_text(runner,encoding='utf-8',newline='\n')
    print(json.dumps({'bank':str(OUT),'cases':len(bank['cases']),'early':bank['early_ids'],'bank_sha256':digest(OUT/'bank.json')}))

if __name__=='__main__':main()
