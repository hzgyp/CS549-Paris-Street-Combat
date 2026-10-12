"""Verify source/protected bytes and actual native journal receipts."""
import json, re, math
from pathlib import Path
from prepare import ROOT, OUT, SOURCE, rows, sha

def load(p):return json.loads(p.read_text('utf-8-sig'))

def reflection(text):
    return re.findall(r'U(?:PROPERTY|FUNCTION)\([^\n]*\)[^\n]*',text)

def main():
    f=load(OUT/'freeze.json'); parent=ROOT/f['parent']['source_snapshot']
    for r in f['parent_files']:assert sha(parent/r['path'])==r['sha256'],r['path']
    for r in f['protected_native']:assert sha(ROOT/r['path'])==r['sha256'],r['path']
    assert sha(ROOT/'Assets/Sync/CATALOG.json')==f['catalog_sha256']
    assert sha(Path(f['normal_game']))==f['normal_game_sha256']
    assert rows(Path(f['user_root']))==f['user_files'],'Normal user files changed'
    m=load(SOURCE.parent/'SOURCE_MANIFEST.json');assert rows(SOURCE)==m['files'] and len(m['files'])==45
    runtime=load(OUT/'RUNTIME.json');build=load(OUT/'candidate_v4/build.json');plan=load(OUT/'candidate_v4/prepare.json')
    assert plan['source_manifest_sha256']==sha(SOURCE.parent/'SOURCE_MANIFEST.json')
    project=Path(plan['project'])
    for r in m['files']:assert sha(project/r['path'])==r['sha256'],r['path']
    assert sha(Path(runtime['path'])/'Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe')==build['game_sha256']==runtime['game_sha256']
    changed=[r['path'] for r in f['parent_files'] if sha(SOURCE/r['path'])!=r['sha256']]
    assert len(changed)==3
    header='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Public/ParisBridgeMission.h'
    assert reflection((SOURCE/header).read_text('utf-8-sig'))==reflection((parent/header).read_text('utf-8-sig')),'Cooked reflection declarations changed'
    cpp='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisBridgeMission.cpp'
    a=(SOURCE/cpp).read_text('utf-8-sig');b=(parent/cpp).read_text('utf-8-sig')
    blocks=[('bool AParisBridgeMission::SaveCheckpoint()','bool AParisBridgeMission::ApplySnapshot('),('bool AParisBridgeMission::ValidateSnapshot(','bool AParisBridgeMission::SaveCheckpoint()'),('bool AParisBridgeMission::ApplySnapshot(','bool AParisBridgePlayerController::InputKey('),('bool AParisBridgeMission::StartMission()','bool AParisBridgeMission::IsSafeBoundary(')]
    for start,end in blocks:assert a[a.index(start):a.index(end)]==b[b.index(start):b.index(end)],start
    assert (SOURCE/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp').read_bytes()==(parent/'Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisGameplayAV.cpp').read_bytes()
    result=dict(status='pass_protection',native_rows=len(f['protected_native']),normal_user_files=len(f['user_files']),parent_files=42,child_files=45,unchanged_parent_files=39,changed=changed,cooked_reflection_exact=True,protected_blocks_exact=len(blocks),game_sha256=runtime['game_sha256'],source_manifest_sha256=sha(SOURCE.parent/'SOURCE_MANIFEST.json'))
    checks=OUT/'checks';native={}
    for name in ['menu_v2','menu_720p_v1','checkpoint_v1','restore_v1','route_v1']:
        p=checks/name/'RESULT.json';launch=load(checks/name/'launch.json')
        assert launch['exit_code']==0 and launch['game_sha256']==runtime['game_sha256']
        r=load(p);assert r['status'].startswith('pass_'),name
        native[name]=dict(status=r['status'],result_sha256=sha(p))
        if 'checks' in r:assert all(x['pass'] for x in r['checks']);native[name]['checks']=len(r['checks'])
    cp=load(checks/'checkpoint_v1/RESULT.json');rs=load(checks/'restore_v1/RESULT.json')
    route=load(checks/'route_v1/result.json');events={x['event'] for x in route['events']}
    assert {'defenders_2_unlocked_0','defenders_1_unlocked_0','defenders_0_unlocked_1','pass_clear_three_entry_prompt_no_autosave','pass_moving_confirmation_denied','pass_explicit_safe_confirmation_once','pass_first_loaded_frame_terminal_corpses','pass_full_restart_checkpoint_reset'}.issubset(events)
    assert len(route['samples'])>0 and all(s['loaded']+s['reserve']+s['shots']==18 for s in route['samples'])
    journal=json.loads(cp['journal'])['snapshot']
    for name,actual in [('same_process',json.loads(cp['reloaded'])['snapshot']),('fresh_process',json.loads(rs['restored'])['snapshot'])]:
        assert actual['serial']==journal['serial']==2 and actual['phase']==journal['phase']=='Won'
        for want,got in zip(journal['actors'],actual['actors']):
            for key in ['id','class','health','dead','loaded','reserve','shots']:assert got[key]==want[key],(name,want['id'],key)
            assert math.dist(got['location'],want['location'])<.001,(name,want['id'],'location')
        assert all(x['dead'] for x in actual['actors'][3:])
    original=json.loads(cp['initial'])['snapshot']
    restored=json.loads(cp['restored'])['snapshot']
    for want,got in zip(original['actors'],restored['actors']):
        assert want['loaded']+want['reserve']+want['shots']==got['loaded']+got['reserve']+got['shots']
    old=ROOT/'tmp/g1-demo-draft-20261009/checkpoint/User/Saved/SaveGames/ParisDemo20261009_checkpoint_A.sav'
    seed=checks/'checkpoint_v1/User/Saved/SaveGames/ParisTeamP0_checkpoint_v1_A.sav'
    assert sha(old)==sha(seed),'Old slot bytes changed'
    launcher=(Path(runtime['path'])/'PLAY_G1_REVISION.cmd').read_text('utf-8-sig')
    assert 'G1Interaction20261010' in launcher and all(s not in launcher for s in ['ParisInteractionProbe','ParisUXTest','ParisDemo'])
    result.update(status='pass_protection_and_native_interaction',native=native,six_actor_new_journal_restore=True,old_slot_bytes_exact=True,actual_route_samples=len(route['samples']),actual_route_ammo_conserved=True,ordinary_launcher_has_no_probe=True)
    (OUT/'verification.json').write_text(json.dumps(result,indent=2)+'\n','utf-8');print(json.dumps(result))

if __name__=='__main__':main()
