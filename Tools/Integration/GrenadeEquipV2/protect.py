from pathlib import Path
import sys,re
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,sha,read,write,rows,INNER
rev=sys.argv[1];freeze=read(root/'tmp/g1-grenade-equip-20261011/freeze.json');parent=freeze['parent'];compiled=OUT/rev/'compiled-source-game'
current=rows(compiled);old={r['path']:r for r in freeze['parent_files']};by={r['path']:r for r in current}
mission='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/';grip='Plugins/ParisGripBindingV18/Source/ParisGripBindingV18/'
changed=[k for k in old if old[k]!=by[k]];added=[k for k in by if k not in old]
allowed={mission+'Private/'+k for k in ['ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentWheelChecks.inl','ParisCombatUI.cpp']}
allowed|={mission+'ParisBridgeMissionV1.Build.cs',grip+'Public/ParisFPUpperBodyV19Actor.h',grip+'Private/ParisFPUpperBodyV19Actor.cpp'}
assert set(changed)==allowed,changed;assert added==[mission+'Private/ParisGrenadeEquipPose.inl'],added
project=Path(read(OUT/rev/'prepare.json')['project']);assert all(sha(project/r['path'])==r['sha256'] for r in current)
before=(root/parent['source_snapshot']/mission/'Private/ParisTacticalEquipment.cpp').read_text('utf-8');after=(compiled/mission/'Private/ParisTacticalEquipment.cpp').read_text('utf-8')
def fun(t,name):
    s=t.index('void '+name+'(');a=t.index('{',s);depth=1;i=a+1
    while depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
    return t[s:i]
names=['BeginThrow','CommitThrow','PlayThrow','ThrowTick','EndThrow','BallTick','Blast']
for n in names:assert fun(before,n)==fun(after,n),n
for k in ['Private/ParisBridgeMission.cpp','Private/ParisMissionInteraction.cpp','Private/ParisEquipmentSave.cpp','Private/ParisEquipmentWorld.inl','Private/ParisGrenadeMesh.inl','Private/ParisPlayerDeath.cpp']:assert old[mission+k]==by[mission+k],k
for prefix in [grip+'Public/ParisFPUpperBodyV19Actor.h']:
    a=(root/parent['source_snapshot']/prefix).read_text('utf-8');b=(compiled/prefix).read_text('utf-8')
    assert re.findall(r'^.*U(?:PROPERTY|FUNCTION).*$',a,re.M)==re.findall(r'^.*U(?:PROPERTY|FUNCTION).*$',b,re.M)
assert rows(root/parent['source_snapshot'])==freeze['parent_files'];assert rows(root/parent['playable_directory'])==freeze['trial_files']
user=Path(freeze['user_root']);assert (rows(user) if user.exists() else [])==freeze['user_files'];assert sha(root/'Assets/Sync/CATALOG.json')==freeze['catalog_sha256']
for r in freeze['protected_native']:assert sha(root/r['path'])==r['sha256'],r['path']
trial={r['path']:r for r in freeze['trial_files'] if r['path'].startswith('Windows/')}
for r in rows(Path(read(OUT/rev/'runtime.json')['path'])):
    if r['path']!=INNER:assert r==trial[r['path']],r['path']
write(OUT/rev/'protection.json',dict(status='pass',changed=changed,added=added,source_files=len(current),native_files=len(freeze['protected_native']),original_throw_gameplay_functions_identical=names,original_gun_save_death_ai_navigation_and_models_unchanged=True,old_reflected_fields_identical=True,parent_source_trial_user_and_catalog_exact=True,runtime_assets_identical_except_exe=True,display_changes='temporary compatible grenade source; original rifle branch and constants retained'))
print('PROTECTION PASS',len(current),len(freeze['protected_native']))
