"""Verify selected identity and all unaffected protected bytes after adoption."""
import hashlib
from pathlib import Path
from manage import ROOT,OUT,PROOF,CURRENT,AUTHOR,GAME,MANIFEST,read,write,sha,verify,verify_live_logs,files,proof,selected_checks,engines,check_processes,now
_,plan,mapping=proof()
r=selected_checks()
baseline=read(ROOT/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json')
assert baseline['status']=='selected_active_development_baseline' and baseline['game_sha256']==GAME
assert baseline['active_source_files']==76 and baseline['source_manifest_sha256']==MANIFEST
assert baseline['playable_entry']==r['playable_entry'] and baseline['save_prefix']=='ParisGrenadeEquipV2'
assert baseline['save_directory']=='%LOCALAPPDATA%/ParisStreetCombat/G1GrenadeEquip20261011'
assert r['playable_entry'].replace('/','\\') in (ROOT/'PLAY_CURRENT_G1.cmd').read_text('utf-8-sig')
for item in plan['protected']:
    path=Path(item['path'])
    if path==ROOT/'Failures/README.md':
        # Adoption adds only a dated preface; historical bytes remain exact.
        data=path.read_bytes()
        start=data.index(b'11October manual complete-gameplay adoption:')
        end=data.index(b'\n\n',start)+2
        original=data[:start]+data[end:]
        assert hashlib.sha256(original).hexdigest()==item['sha256'] and len(original)==item['size_bytes']
    else:
        verify(path,item)
verify_live_logs(plan)
assert sorted(str(p) for p in files(Path(plan['user_root'])))==sorted(plan['user_files'])
assert all(not (ROOT/t['path']).exists() for t in plan['targets'])
for name in ['CURRENT_EQUIPMENT_INPUT_REVIEW','CURRENT_UI_REVIEW']:
    review=read(ROOT/'Docs/Development'/(name+'.json'))
    assert review['game_sha256']==GAME and review['status']=='manually_reviewed_selected_active_baseline'
    assert review['manual_review']=='logic_passed_with_residual_sleeve_occlusion'
assert read(OUT/'INDEX_REFRESH.json')['status']=='succeeded'
original_engines={p['ProcessId'] for p in plan['original_engines'] if p['Name']=='UnrealEditor.exe'}
final_engines=check_processes(plan['targets'])
assert original_engines.issubset({p['ProcessId'] for p in final_engines})
write(PROOF/'CLOSURE_20261011.json',dict(status='pass_selected76_local_adoption_and_retirement',finished=now(),game_sha256=GAME,source_files=76,normal_files=100,existing_checks=15,protected_files=len(plan['protected']),user_files=len(plan['user_files']),targets_removed=len(plan['targets']),index_refresh='succeeded',engines=final_engines,remaining_visual_issue='Minor clothing/sleeve occlusion; not repaired in adoption',publication='local only; no Git/SFTP/video/course update'))
print('CLOSURE PASS formal76; all protected/raw/users/native exact; Editors retained')
