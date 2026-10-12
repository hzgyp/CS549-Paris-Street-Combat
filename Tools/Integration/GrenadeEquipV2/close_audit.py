from pathlib import Path
import sys,json,subprocess
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import read,write,sha,rows,INNER
base=root/'tmp/g1-grenade-equip-20261011';r=read(base/'DELIVERY_20261011.json');freeze=read(base/'freeze.json')
assert rows(root/r['source_snapshot'])==read(root/r['source_manifest'])['files']
assert sha(root/r['source_manifest'])==r['source_manifest_sha256']
assert rows(root/r['playable_directory'])==r['normal_files']
assert len(r['normal_files'])==100 and sha(root/r['playable_directory']/INNER)==r['game_sha256']
assert rows(root/freeze['parent']['source_snapshot'])==freeze['parent_files']
assert rows(root/freeze['parent']['playable_directory'])==freeze['trial_files']
user=Path(freeze['user_root']);assert (rows(user) if user.exists() else [])==freeze['user_files']
assert sha(root/'Assets/Sync/CATALOG.json')==freeze['catalog_sha256']
for c in r['checks']:
    assert sha(root/c['result'])==c['sha256']
    assert read(root/c['result'])['status']==c['status']
    launch=read((root/c['result']).parent/'launch.json');assert launch['exit_code']==0 and launch['game_sha256']==r['game_sha256']
formal=read(root/'Docs/Development/CURRENT_DEVELOPMENT_BASELINE.json')
assert formal['game_sha256']=='b40409b08830cc0e1d306ceab0575d7e61db382f50853426bbda58d08f385079'
assert rows(root/formal['source_snapshot'])==read(root/formal['source_manifest'])['files']
assert sha(root/formal['playable_directory']/INNER)==formal['game_sha256']
ps="Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'UnrealEditor|WW2France|UnrealBuildTool' } | Select-Object ProcessId,Name | ConvertTo-Json -Compress"
proc=subprocess.run(['powershell','-NoProfile','-Command',ps],capture_output=True,text=True,check=True)
engines=json.loads(proc.stdout);engines=engines if isinstance(engines,list) else [engines]
assert sorted(e['ProcessId'] for e in engines)==[50836,51148],engines
assert all(e['Name']=='UnrealEditor.exe' for e in engines)
assert read(base/'INDEX_REFRESH.json')['status']=='succeeded'
write(base/'CLOSURE_20261011.json',dict(status='pass_local_unified_candidate_manual_review_pending',game_sha256=r['game_sha256'],source_files=76,normal_files=100,checks=len(r['checks']),parent_source_normal_user_exact=True,catalog_exact=True,formal_selected_game_sha256=formal['game_sha256'],native_protection_receipt=r['protection'],native_files=1754,engines=engines,index_refresh='platform succeeded; DB plus JSON/Markdown automatic',publication='none; no adoption/cleanup/Git/SFTP'))
print('CLOSURE PASS',r['playable_entry'])
