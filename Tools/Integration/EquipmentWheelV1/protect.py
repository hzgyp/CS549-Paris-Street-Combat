from pathlib import Path
import sys
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,sha,read,write,rows,INNER
rev=sys.argv[1];freeze=read(root/'tmp/g1-equipment-wheel-20261011/freeze.json');parent=freeze['parent']
compiled=OUT/rev/'compiled-source-game';project=Path(read(OUT/rev/'prepare.json')['project'])
current=rows(compiled);by={r['path']:r for r in current};old={r['path']:r for r in freeze['parent_files']}
changed=[k for k in old if old[k]!=by[k]];added=[k for k in by if k not in old]
prefix='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/'
allowed=['ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentChecks.inl','ParisCombatUI.cpp','ParisCombatUIProbe.cpp','ParisPlayerDeathProbe.inl']
assert set(changed)=={prefix+x for x in allowed},changed
assert added==[prefix+'ParisEquipmentWheelChecks.inl'],added
assert all(sha(project/r['path'])==r['sha256'] for r in current)
assert rows(root/parent['source_snapshot'])==freeze['parent_files']
assert rows(root/parent['playable_directory'])==freeze['trial_files']
user=Path(freeze['user_root']);assert (rows(user) if user.exists() else [])==freeze['user_files']
assert sha(root/'Assets/Sync/CATALOG.json')==freeze['catalog_sha256']
for r in freeze['protected_native']:assert sha(root/r['path'])==r['sha256'],r['path']
before=(root/parent['source_snapshot']/prefix/'ParisTacticalEquipment.cpp').read_text('utf-8');after=(compiled/prefix/'ParisTacticalEquipment.cpp').read_text('utf-8')
def fun(t,name):
    pos=t.index('void '+name+'(');start=t.index('{',pos);depth=1;i=start+1
    while depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
    return t[pos:i]
names=['CommitThrow','PlayThrow','ThrowTick','BallTick','Blast']
for name in names:assert fun(before,name)==fun(after,name),name
begin=fun(before,'BeginThrow');child=fun(after,'BeginThrow');assert child.replace('ClearSelectedVisual(S);','')==begin
native_gun_save=[prefix+x for x in ['ParisBridgeMission.cpp','ParisMissionInteraction.cpp','ParisEquipmentSave.cpp','ParisEquipmentWorld.inl','ParisGrenadeMesh.inl','ParisPressureMineMesh.inl','ParisPlayerDeath.cpp']]
assert all(old[k]==by[k] for k in native_gun_save)
runtime=Path(read(OUT/rev/'runtime.json')['path']);runtime_files=rows(runtime)
trial={r['path']:r for r in freeze['trial_files'] if r['path'].startswith('Windows/')}
for r in runtime_files:
    if r['path']!=INNER:assert r==trial[r['path']],r['path']
write(OUT/rev/'protection.json',dict(status='pass',changed=changed,added=added,source_files=len(current),native_files=len(freeze['protected_native']),protected_parent_trial_files=len(freeze['trial_files']),gameplay_functions_identical=names,begin_throw_original_attachment_animation_admission_identical=True,gun_and_save_source_identical=native_gun_save,user_files_exact=True,catalog_exact=True,all_runtime_assets_identical_except_exe=True))
print('PROTECTION PASS',len(current),len(freeze['protected_native']))
