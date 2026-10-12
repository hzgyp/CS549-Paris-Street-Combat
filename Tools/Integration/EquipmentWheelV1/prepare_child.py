from pathlib import Path
import sys,shutil,subprocess
root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import sha,rows,read,write,OUT
parent=read(root/'tmp/g1-grenade-models-20261011/DELIVERY_20261011.json')
files=read(root/parent['source_manifest'])['files']
assert sha(root/parent['source_manifest'])==parent['source_manifest_sha256']
assert rows(root/parent['source_snapshot'])==files
base=root/'tmp/g1-equipment-wheel-20261011';assert not (base/'freeze.json').exists()
native=read(root/'tmp/g1-tactical-equipment-20261010/freeze.json')['protected_native']
for r in native:assert sha(root/r['path'])==r['sha256'],r['path']
user=Path.home()/'AppData/Local/ParisStreetCombat'/parent['user_dir']
write(base/'freeze.json',dict(parent=parent,parent_files=files,trial_files=rows(root/parent['playable_directory']),user_root=str(user),user_files=rows(user) if user.exists() else [],protected_native=native,catalog_sha256=sha(root/'Assets/Sync/CATALOG.json')))
target=OUT/'candidate_equipment_wheel_v1';assert not target.exists()
project=target/'Project';shutil.copytree(root/parent['source_snapshot'],project)
shutil.copytree(root/parent['active_authoring_project']/'Binaries',project/'Binaries')
cmd="New-Item -ItemType Junction -Path '"+str(project/'Content')+"' -Value '"+str(root/'Unreal/ParisStreetCombat/Content')+"' | Out-Null"
subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,check=True)
write(target/'prepare.json',dict(status='independent_source_prepared',project=str(project),revision='candidate_equipment_wheel_v1',parent_revision=parent['revision']))
print(project)
