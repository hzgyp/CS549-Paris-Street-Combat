from pathlib import Path
import sys,json
root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'Tools/Integration/TacticalEquipmentV1'))
from prepare import OUT,sha,read,write,rows
rev=sys.argv[1];freeze=read(root/'tmp/g1-grenade-models-20261011/freeze.json');parent=freeze['parent']
compiled=OUT/rev/'compiled-source-game';project=Path(read(OUT/rev/'prepare.json')['project'])
current=rows(compiled);by={r['path']:r for r in current};old={r['path']:r for r in freeze['parent_files']}
changed=[k for k in old if old[k]!=by[k]];added=[k for k in by if k not in old]
cpp='Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisTacticalEquipment.cpp';header=cpp.replace('ParisTacticalEquipment.cpp','ParisGrenadeMesh.inl')
assert changed==[cpp],changed;assert added==[header],added
assert all(sha(project/r['path'])==r['sha256'] for r in current)
assert rows(root/parent['source_snapshot'])==freeze['parent_files']
assert rows(root/parent['playable_directory'])==freeze['trial_files']
user=Path(freeze['user_root']);assert (rows(user) if user.exists() else [])==freeze['user_files']
assert sha(root/'Assets/Sync/CATALOG.json')==freeze['catalog_sha256']
for r in freeze['protected_native']:assert sha(root/r['path'])==r['sha256'],r['path']
before=(root/parent['source_snapshot']/cpp).read_text('utf-8');after=(compiled/cpp).read_text('utf-8')
# Key gameplay functions must remain text-identical despite narrow Prop/probe edits.
names=['BeginThrow','CommitThrow','PlayThrow','EndThrow','ThrowTick','BallTick','Blast']
for name in names:
    def fun(t):
        pos=t.index('void '+name+'(');start=t.index('{',pos);depth=1;i=start+1
        while depth:
            depth+=(t[i]=='{')-(t[i]=='}');i+=1
        return t[pos:i]
    assert fun(before)==fun(after),name
write(OUT/rev/'protection.json',dict(status='pass',changed=changed,added=added,source_files=len(current),parent_files=len(old),native_files=len(freeze['protected_native']),protected_parent_trial_files=len(freeze['trial_files']),key_gameplay_functions_identical=names,other_source_files_bit_identical=True,user_files_exact=True,catalog_exact=True))
print('PROTECTION PASS',len(current),len(freeze['protected_native']))
