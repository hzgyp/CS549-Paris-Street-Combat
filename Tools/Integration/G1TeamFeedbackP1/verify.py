"""Protect original bytes/transactions and audit current candidate native receipts."""
import json,re,math
from pathlib import Path
from prepare import ROOT,OUT,SOURCE,rows,sha

def load(p):return json.loads(p.read_text('utf-8-sig'))
def declarations(s):return re.findall(r'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',s)
def main():
    f=load(OUT/'freeze.json');old=f['selected_parent_freeze'];parent=ROOT/f['parent']['source_snapshot']
    for r in f['parent_files']:assert sha(parent/r['path'])==r['sha256'],r['path']
    assert sha(Path(f['p0_game']))==f['p0_game_sha256']
    assert rows(Path(f['p0_user_root']))==f['p0_user_files']
    selected=ROOT/old['parent']['source_snapshot']
    for r in old['parent_files']:assert sha(selected/r['path'])==r['sha256'],r['path']
    for r in old['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
    assert sha(ROOT/'Assets/Sync/CATALOG.json')==old['catalog_sha256']
    assert sha(Path(old['normal_game']))==old['normal_game_sha256']
    assert rows(Path(old['user_root']))==old['user_files']
    manifest=load(SOURCE.parent/'SOURCE_MANIFEST.json');assert rows(SOURCE)==manifest['files'] and len(manifest['files'])==48
    runtime=load(OUT/'RUNTIME.json');revision=runtime['revision'];plan=load(OUT/revision/'prepare.json');build=load(OUT/revision/'build.json')
    for r in manifest['files']:assert sha(Path(plan['project'])/r['path'])==r['sha256'],r['path']
    assert sha(SOURCE.parent/'SOURCE_MANIFEST.json')==plan['source_manifest_sha256']==runtime['source_manifest_sha256']
    assert sha(Path(runtime['path'])/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==runtime['game_sha256']==build['game_sha256']
    # v9 changes only fresh victory admission and its opt-in observer. Carry the
    # v8 menu/ammo/actions evidence only after proving their production code exact.
    v8=OUT/'candidate_v8';v8_plan=load(v8/'prepare.json');v8_build=load(v8/'build.json')
    v8_source=Path(v8_plan['project'])
    changed=['Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp','Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMissionV1.cpp']
    assert {r['path'] for r in manifest['files'] if sha(v8_source/r['path'])!=r['sha256']}==set(changed)
    old_win='''    { SetPhase(TEXT("Won")); Feedback=TEXT("G1 secured. Enter the gold checkpoint circle to save."); GateBrains(false);
      if(auto* PC=UGameplayStatics::GetPlayerController(this,0)) { PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); } }'''
    new_win='''    {
        // Keep the original squad route active until its actual arrival gate completes.
        // Restored terminal saves never enter this fresh-mission transition.
        if(!bBridgeTransitComplete) Feedback=TEXT("G1 guards cleared. Waiting for the squad to finish crossing.");
        else
        { SetPhase(TEXT("Won")); Feedback=TEXT("G1 secured. Enter the gold checkpoint circle to save."); GateBrains(false);
          if(auto* PC=UGameplayStatics::GetPlayerController(this,0)) { PC->ResetIgnoreMoveInput(); PC->ResetIgnoreLookInput(); } }
    }'''
    current=(SOURCE/changed[0]).read_text('utf-8-sig');previous=(v8_source/changed[0]).read_text('utf-8-sig')
    assert current.count(new_win)==1 and current.replace(new_win,old_win)==previous
    # The existing cooked reflection schema stays exact across both protected parents.
    for p in SOURCE.rglob('*.h'):
        rel=p.relative_to(SOURCE)
        if (parent/rel).exists():assert declarations(p.read_text('utf-8-sig'))==declarations((parent/rel).read_text('utf-8-sig')),str(rel)
    cpp='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp'
    a=(SOURCE/cpp).read_text('utf-8-sig');b=(parent/cpp).read_text('utf-8-sig')
    blocks=[('bool AParisBridgeMission::SaveCheckpoint()','bool AParisBridgeMission::ApplySnapshot('),('bool AParisBridgeMission::ValidateSnapshot(','bool AParisBridgeMission::SaveCheckpoint()'),('bool AParisBridgeMission::ApplySnapshot(','bool AParisBridgePlayerController::InputKey('),('bool AParisBridgeMission::StartMission()','bool AParisBridgeMission::ApplyBridgeNavigationConstraint('),('bool AParisBridgeMission::ApplyBridgeNavigationConstraint(','void AParisBridgeMission::Tick('),('bool AParisBridgeMission::IsSafeBoundary(','bool AParisBridgeMission::ValidateSnapshot(')]
    for start,end in blocks:assert a[a.index(start):a.index(end)]==b[b.index(start):b.index(end)],start
    av='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp'
    s=(SOURCE/av).read_text('utf-8-sig');p=(parent/av).read_text('utf-8-sig')
    expected=p.replace('    const FString Base=Speed>220?TEXT("step_run"):Speed<90?TEXT("step_slow"):TEXT("step_walk");','    const bool Running=Posture==0&&Flag(C,TEXT("RunHeld"))&&!Flag(C,TEXT("SlowHeld"));\n    const FString Base=Running?TEXT("step_run"):Speed<90?TEXT("step_slow"):TEXT("step_walk");',1).replace('    Play(W,S,C,T,Cue,Posture==1?.42:Speed<90?.35:Speed>220?.80:.65);','    Play(W,S,C,T,Cue,Posture==1?.42:Speed<90?.35:Running?.80:.65);',1)
    assert s==expected,'Unexpected audio change'
    launcher=(Path(runtime['path'])/'PLAY_G1_REVISION.cmd').read_text('utf-8-sig')
    assert 'G1TeamP1' in launcher and not any(x in launcher for x in ['ParisP1Out','ParisUXTest','ParisInteractionProbe','ParisDemo','ParisAVAuditOut'])
    result=dict(status='pass_protection',native_guards=len(old['protected_native']),p0_source_files=45,selected_source_files=42,child_source_files=48,protected_blocks_exact=len(blocks),cooked_reflection_exact=True,normal_save_roots_exact=True,game_sha256=runtime['game_sha256'],source_manifest_sha256=runtime['source_manifest_sha256'],ordinary_launcher_no_probe=True)
    native={}
    inherited={'ammo_v4','menu_v2','menu_720p_v2','actions_v2'}
    for identity in ['ammo_v4','menu_v2','menu_720p_v2','actions_v2','route_v2','checkpoint_v2','restore_v2']:
        folder=OUT/'checks'/identity
        if not folder.exists():continue
        launch=load(folder/'launch.json');expected_game=v8_build['game_sha256'] if identity in inherited else runtime['game_sha256']
        assert launch['exit_code']==0 and launch['game_sha256']==expected_game,identity
        path=folder/'RESULT.json';r=load(path);assert r['status'].startswith('pass_'),identity
        if 'checks' in r:assert all(x['pass'] for x in r['checks'])
        native[identity]=dict(status=r['status'],result_sha256=sha(path),checks=len(r.get('checks',r.get('events',[]))),game_sha256=launch['game_sha256'],scope='v8 unchanged menu/ammo/movement production code; carried evidence, not a v9 rerun' if identity in inherited else 'current v9 native run')
        if 'samples' in r:
            assert all(x['loaded']+x['reserve']+x['shots']==18 for x in r['samples']),identity
    result['native']=native
    if 'ammo_v4' in native:
        ammo=load(OUT/'checks/ammo_v4/RESULT.json')
        bs=ammo['ready_assets']['retained_stride_blendspace']
        assert bs['axis_x_max']==bs['axis_y_max']==300 and len(bs['samples'])==17
        assert ammo['ready_assets']['authoritative_gun_class']=='/Script/Engine.StaticMeshActor'
        result['current_stride_inventory_verified']=True
    if 'actions_v2' in native:
        actions=load(OUT/'checks/actions_v2/result.json');stats={}
        for step,expected in [('walk',220),('run',450),('slow',65)]:
            samples=[x for x in actions['samples'] if x['step']==step]
            assert samples and abs(samples[-1]['speed']-expected)<2
            if step!='slow':assert abs(max(x['speed'] for x in samples)-expected)<2
            steady=[x for x in samples if abs(x['speed']-expected)<2]
            assert steady and all(abs(x['animation_rate']-(1.5 if step=='run' else 1))<.03 for x in steady)
            stats[step]=dict(peak_cm_s=max(x['speed'] for x in samples),samples=len(samples),steady_samples=len(steady))
        result['actual_speed_and_cadence']=stats
    prone=load(OUT/'checks/prone_v2/result.json')
    assert prone['status']=='failed_crawl_physical_and_original_obstruction_stop'
    result['unresolved_prone_fixture']=dict(status=prone['status'],forward_cm=prone['crawl_forward_cm'],blocked_drift_cm=prone['blocked_drift_cm'],result_sha256=sha(OUT/'checks/prone_v2/result.json'),positive_crawl_not_accepted=True)
    if 'route_v2' in native:
        route=load(OUT/'checks/route_v2/result.json')
        all_far=[s for s in route['samples'] if len(s['allies'])==2 and all(not a['dead'] and float(re.search(r'X=([-\d.]+)',a['feet'])[1])>=5600 for a in s['allies'])]
        assert all_far,'Both living Allies must actually reach the far bank'
        won=json.loads(route['won_mission_state'])
        assert won['bridge_transit_complete'] and won['phase']=='Won'
        allies=won['snapshot']['actors'][1:3]
        assert len(allies)==2 and all(not x['dead'] and x['location'][0]>=5600 for x in allies)
        result['original_squad_arrival_gate_completed_before_victory']=True
        result['won_allies_actual_actor_locations']={x['id']:x['location'] for x in allies}
        result['actual_both_living_allies_far_bank_samples']=len(all_far)
        result['actual_g1_route_samples']=len(route['samples'])
        required={'defenders_2_unlocked_0','defenders_1_unlocked_0','defenders_0_unlocked_1','pass_original_bridge_transit_completed_before_victory','pass_both_living_allies_actually_across_before_victory','pass_clear_three_entry_prompt_no_autosave','pass_explicit_safe_confirmation_once','pass_first_loaded_frame_terminal_corpses','pass_full_restart_checkpoint_reset'}
        assert required.issubset({x['event'] for x in route['events']})
    if 'checkpoint_v2' in native and 'restore_v2' in native:
        cp=load(OUT/'checks/checkpoint_v2/RESULT.json');rs=load(OUT/'checks/restore_v2/RESULT.json')
        want=json.loads(cp['journal'])['snapshot'];got=json.loads(rs['restored'])['snapshot']
        assert want['serial']==got['serial']==2
        for a,b in zip(want['actors'],got['actors']):
            for key in ['id','class','health','dead','loaded','reserve','shots']:assert a[key]==b[key],(a['id'],key)
            assert math.dist(a['location'],b['location'])<.001
        result['fresh_process_six_actor_restore_exact']=True
    if len(native)==7:result['status']='p1_feature_checks_pass_with_unresolved_prone_fixture_pending_manual_review'
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result))

if __name__=='__main__':main()
