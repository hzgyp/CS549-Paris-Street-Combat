from pathlib import Path
from prepare import OUT
import shutil
here=Path(__file__).parent
p=here/'ParisTacticalEquipment.h';s=p.read_bytes().replace(b'class AParisBridgeMission;',b'class AAIController;\r\nclass AParisBridgeMission;').replace(b'void Initialize();',b'bool OwnsNavigation(const AAIController* Controller);\r\nvoid Initialize();');p.write_bytes(s)
p=here/'ParisTacticalEquipment.cpp';s=p.read_bytes()
needle=b'bool Occluded(UWorld* W,'
new=b'''bool OwnsNavigation(const AAIController* AI){if(!AI||!AParisBridgeMission::Find(AI)||!AParisBridgeMission::Find(AI)->AllowsPlay())return false;auto* Existing=Sessions.Find(AI->GetWorld());if(!Existing)return false;for(const auto& E:(*Existing)->Evades)if(E.Pawn.Get()==AI->GetPawn()&&!Dead(E.Pawn.Get())&&AI->GetWorld()->GetTimeSeconds()<E.Until)return true;return false;}\r\n'''
assert s.count(needle)==1;s=s.replace(needle,new+needle);p.write_bytes(s)
base=OUT/'candidate_full_v15/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
assert not (OUT/'candidate_full_v15/build-game.json').exists()
for name in ['ParisTacticalEquipment.h','ParisTacticalEquipment.cpp']:shutil.copyfile(here/name,base/name)
p=base/'ParisBridgeMission.cpp';s=p.read_bytes();needle=b'bool UParisBridgeMissionLibrary::UpdateBridgeSquad(AAIController* Controller)\r\n{\r\n';assert s.count(needle)==1;s=s.replace(needle,needle+b'    if(ParisTacticalEquipment::OwnsNavigation(Controller))return true;\r\n');p.write_bytes(s)
p=here/'verify_protection.py';s=p.read_bytes();s=s.replace(b'old=(parent/(b+\'Private/ParisBridgeMission.cpp\')).read_bytes()',b'old=(parent/(b+\'Private/ParisBridgeMission.cpp\')).read_bytes()\nnew=new.replace(b\'    if(ParisTacticalEquipment::OwnsNavigation(Controller))return true;\\r\\n\',b\'\')');p.write_bytes(s)
p=Path('Failures/MI027-20261011-smoke-atlas-hazard-owner/ANALYSIS.md');s=p.read_bytes();s+='\n\nv14 的实际速度0、路径状态Idle、位移0.796cm继续失败。读取 G1MissionV1/ue_bridge_hook.py 与原 UpdateBridgeSquad：hook 安装于 Controller ReceiveTick，独立于 Brain；原 CombatHold 分支调用 PC_PolicyHold/StopMovement，确会覆盖装备 MoveTo。v15 仅在有效、存活、AllowsPlay 的短暂装备导航所有权期间让桥接hook返回已处理；其余逐字进入原小队算法。结束恢复原状态，不修改BT/native包，不以暂停Brain代替Tick所有权。v14 135粒子、6x6图集、alpha0.595仍无充分可见浓烟；材质只读审计后再定参数，不把粒子存在当作显示通过。\n'.encode();p.write_bytes(s)
print('v15 bridge Controller Tick yields only to active finite equipment navigation; original bridge algorithm retained')
