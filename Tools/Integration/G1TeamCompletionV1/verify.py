"""Validate immutable parents/assets and actual current-Game results; no game writes."""
from pathlib import Path
import json,re,math
from prepare import ROOT,OUT,SOURCE,rows,sha,load

def declarations(text):return re.findall(r'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',text)

def main():
    f=load(OUT/'freeze.json');p1=ROOT/f['parent']['source_snapshot'];p0=f['prior_freeze'];selected=p0['selected_parent_freeze']
    for epoch,base in [(f,p1),(p0,ROOT/p0['parent']['source_snapshot']),(selected,ROOT/selected['parent']['source_snapshot'])]:
        assert rows(base)==epoch['parent_files'],str(base)
    for row in selected['protected_native']:assert sha(ROOT/row['path'])==row['sha256'],row['path']
    assert sha(ROOT/'Assets/Sync/CATALOG.json')==selected['catalog_sha256']
    for game,key in [(f['p1_game'],f['p1_game_sha256']),(p0['p0_game'],p0['p0_game_sha256']),(selected['normal_game'],selected['normal_game_sha256'])]:assert sha(Path(game))==key
    for path,key in [(f['p1_user_root'],f['p1_user_files']),(p0['p0_user_root'],p0['p0_user_files']),(selected['user_root'],selected['user_files'])]:assert rows(Path(path))==key
    manifest=load(SOURCE.parent/'SOURCE_MANIFEST.json');assert rows(SOURCE)==manifest['files'] and len(manifest['files'])==52
    runtime=load(OUT/'RUNTIME.json');prepared=load(OUT/runtime['revision']/'prepare.json');build=load(OUT/runtime['revision']/'build.json')
    for row in manifest['files']:assert sha(Path(prepared['project'])/row['path'])==row['sha256'],row['path']
    assert sha(SOURCE.parent/'SOURCE_MANIFEST.json')==runtime['source_manifest_sha256']==prepared['source_manifest_sha256']
    assert sha(Path(runtime['path'])/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==runtime['game_sha256']==build['game_sha256']
    base='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/'
    changed={base+'Private/ParisBridgeMission.cpp',base+'Private/ParisBridgeMissionV1.cpp',base+'Public/ParisBridgeMission.h'}
    assert {r['path'] for r in f['parent_files'] if sha(SOURCE/r['path'])!=r['sha256']}==changed
    for header in SOURCE.rglob('*.h'):
        old=p1/header.relative_to(SOURCE)
        if old.exists():assert declarations(header.read_text(encoding='utf-8-sig'))==declarations(old.read_text(encoding='utf-8-sig'))
    new=(SOURCE/(base+'Private/ParisBridgeMission.cpp')).read_text(encoding='utf-8-sig');old=(p1/(base+'Private/ParisBridgeMission.cpp')).read_text(encoding='utf-8-sig')
    blocks=[('bool AParisBridgeMission::SaveCheckpoint()','bool AParisBridgeMission::ApplySnapshot('),('bool AParisBridgeMission::ValidateSnapshot(','bool AParisBridgeMission::SaveCheckpoint()'),('bool AParisBridgeMission::ApplySnapshot(','bool AParisBridgePlayerController::InputKey('),('bool AParisBridgeMission::StartMission()','bool AParisBridgeMission::ApplyBridgeNavigationConstraint('),('bool AParisBridgeMission::ApplyBridgeNavigationConstraint(','void AParisBridgeMission::Tick('),('bool AParisBridgeMission::IsSafeBoundary(','bool AParisBridgeMission::ValidateSnapshot(')]
    for start,end in blocks:assert new[new.index(start):new.index(end)]==old[old.index(start):old.index(end)],start
    start='void AParisBridgePlayerController::PostProcessInput('
    assert new[new.index(start):].replace('    ParisCompletionProbe::ObserveProneCause(P);\n','').replace('        ParisCompletionProbe::ObserveProneCause(P,true);\n','')==old[old.index(start):]
    # Existing P0/P1 interaction, radar, resource configuration, locomotion and audio files exact.
    carried=['ParisMissionInteraction.cpp','ParisTeamP1.cpp','ParisGameplayAV.cpp','ParisInteractionProbe.cpp','ParisP1Probe.cpp']
    for name in carried:assert sha(SOURCE/(base+'Private/'+name))==sha(p1/(base+'Private/'+name))
    launcher=(Path(runtime['path'])/'PLAY_G1_REVISION.cmd').read_text(encoding='utf-8-sig')
    assert runtime['user_directory'] in launcher and not any(x in launcher for x in ['ParisP1Out','ParisUXTest','ParisInteractionProbe','ParisDemo','ParisAVAuditOut','ParisProneCauseOut','ParisSpaceSurveyOut','ParisPathWitnessOut'])
    v6=Path(load(OUT/'candidate_v6/prepare.json')['project'])
    assert {r['path'] for r in manifest['files'] if sha(v6/r['path'])!=r['sha256']}=={base+'Private/ParisBridgeMissionV1.cpp'},'Only opt-in observer changes after v6'
    results={}
    for identity in ['menu_v1','ammo_v1','actions_v1','route_v4','checkpoint_v1','restore_v1']:
        folder=OUT/'checks'/identity;path=folder/'result.json';r=load(path);receipt=load(folder/'launch.json')
        assert receipt['exit_code']==0 and receipt['game_sha256']==(load(OUT/'candidate_v6/build.json')['game_sha256'] if identity in {'menu_v1','ammo_v1'} else runtime['game_sha256']),identity
        assert r['status'].startswith('pass_'),(identity,r['status'])
        if 'checks' in r:assert all(x['pass'] for x in r['checks']),identity
        if 'samples' in r:assert all(x['loaded']+x['reserve']+x['shots']==18 for x in r['samples']),identity
        results[identity]=dict(status=r['status'],game_sha256=receipt['game_sha256'],result_sha256=sha(path),scope='v6 production exact; carried receipt, not v9 rerun' if identity in {'menu_v1','ammo_v1'} else 'current v9 Game native run',checks=len(r.get('checks',r.get('events',[]))))
    route=load(OUT/'checks/route_v4/result.json');won=json.loads(route['won_mission_state'])
    assert won['phase']=='Won' and won['bridge_transit_complete'] and won['living_defenders']==0
    allies=won['snapshot']['actors'][1:3];assert all(not a['dead'] and a['location'][0]>=5600 for a in allies)
    required={'defenders_2_unlocked_0','defenders_1_unlocked_0','defenders_0_unlocked_1','pass_original_bridge_transit_completed_before_victory','pass_both_living_allies_actually_across_before_victory','pass_clear_three_entry_prompt_no_autosave','pass_explicit_safe_confirmation_once','pass_first_loaded_frame_terminal_corpses','pass_full_restart_checkpoint_reset'}
    assert required.issubset({x['event'] for x in route['events']})
    ammo=load(OUT/'checks/ammo_v1/result.json');initial=json.loads(ammo['initial'])['snapshot']['actors'];proposal=load(OUT/'subset_proposal.json')
    for actor in initial[1:]:
        target=proposal['npc_feet'][actor['id']];hh=96.2331619263 if actor['id'].startswith('Ally') else 95.2641525269
        assert math.dist(actor['location'][:2],target[:2])<25,(actor['id'],actor['location'])
        assert abs(actor['location'][2]-hh-target[2])<10,(actor['id'],'feet_z')
    a=initial[1:3];assert math.dist(a[0]['location'][:2],a[1]['location'][:2])>=500
    for actor in a:assert math.dist(actor['location'][:2],initial[0]['location'][:2])>=350
    for a in initial[3:]:
        for b in initial[3:]:
            if a['id']<b['id']:assert math.dist(a['location'][:2],b['location'][:2])>=350
    cp=load(OUT/'checks/checkpoint_v1/result.json');rs=load(OUT/'checks/restore_v1/result.json');want=json.loads(cp['journal'])['snapshot'];got=json.loads(rs['restored'])['snapshot']
    assert want['serial']==got['serial']==2
    for a,b in zip(want['actors'],got['actors']):
        for key in ['id','class','health','dead','loaded','reserve','shots']:assert a[key]==b[key],(a['id'],key)
        assert math.dist(a['location'],b['location'])<.001
    result=dict(status='pass_fixed_layout_and_p0_p1_native_checks_pending_manual_review',game_sha256=runtime['game_sha256'],source_manifest_sha256=runtime['source_manifest_sha256'],source_files=52,native_guards=len(selected['protected_native']),parents_and_normal_saves_exact=True,cooked_reflection_exact=True,protected_transaction_ai_navigation_blocks_exact=len(blocks),ordinary_entry_no_diagnostics=True,verified_runs=results,actual_initial_actor_locations={a['id']:a['location'] for a in initial},won_allies_actual_locations={a['id']:a['location'] for a in allies},prone_positive_not_accepted=True,p2_ads_enbloc_not_implemented=True)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))

if __name__=='__main__':main()
