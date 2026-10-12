from pathlib import Path
import sys,json,shutil,subprocess
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import sha,rows,read,write,OUT
parent=read(root/'tmp/g1-player-death-20261011/DELIVERY_20261011.json')
files=read(root/parent['source_manifest'])['files']
assert sha(root/parent['source_manifest'])==parent['source_manifest_sha256']
assert rows(root/parent['source_snapshot'])==files
freeze=read(root/'tmp/g1-tactical-equipment-20261010/freeze.json')
for r in freeze['protected_native']:assert sha(root/r['path'])==r['sha256'],r['path']
trial=root/parent['playable_directory'];inner='Windows/WW2FranceLiberation/Binaries/Win64/WW2FranceLiberation.exe'
assert sha(trial/inner)==parent['game_sha256']
user=Path.home()/'AppData/Local/ParisStreetCombat'/parent['user_dir']
write(root/'tmp/g1-grenade-models-20261011/freeze.json',dict(parent=parent,parent_files=files,trial_files=rows(trial),user_root=str(user),user_files=rows(user) if user.exists() else [],protected_native=freeze['protected_native'],catalog_sha256=sha(root/'Assets/Sync/CATALOG.json')))
revision='candidate_grenade_models_v1';target=OUT/revision;assert not target.exists()
project=target/'Project';shutil.copytree(root/parent['source_snapshot'],project)
author=root/parent['active_authoring_project']
shutil.copytree(author/'Binaries',project/'Binaries')
# Omit the parent's PCH caches. UBT builds one new candidate cache; later
# bounded revisions reuse this same isolated authoring path and retain receipts.
cmd="New-Item -ItemType Junction -Path '"+str(project/'Content')+"' -Value '"+str(root/'Unreal/ParisStreetCombat/Content')+"' | Out-Null"
subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,check=True)
write(target/'prepare.json',dict(status='independent_source_prepared',revision=revision,project=str(project),parent_revision='candidate_death_v6',source_manifest=parent['source_manifest']))
print('PREPARED',project)
