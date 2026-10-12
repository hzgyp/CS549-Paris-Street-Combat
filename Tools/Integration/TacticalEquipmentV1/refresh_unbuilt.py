from prepare import OUT
from pathlib import Path
import shutil
revision='candidate_full_v6';assert not (OUT/revision/'build-game.json').exists()
here=Path(__file__).parent;base=OUT/revision/'Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
for name in ['ParisTacticalEquipment.h','ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentSave.cpp','ParisEquipmentSightBridge.h','ParisEquipmentWorld.inl','ParisEquipmentAudio.inl','ParisEquipmentChecks.inl']:shutil.copyfile(here/name,base/name)
p=base/'ParisTacticalEquipment.cpp';data=p.read_bytes();needle=b'Pass?TEXT("pass_native_throw_early_gate_requires_image_review"):TEXT("failed")';assert data.count(needle)==1;data=data.replace(needle,b'Pass?TEXT("pass_native_")+CheckMode:TEXT("failed_")+CheckMode');p.write_bytes(data)
p=base/'ParisBridgeMission.cpp';data=p.read_bytes();needle=b'    for(const auto& V:CachedEnemyLocations) Dot(V,Danger,2.5);';assert data.count(needle)==1;data=data.replace(needle,b'    FVector EquipmentEye;FRotator EquipmentView;PlayerOwner->GetPlayerViewPoint(EquipmentEye,EquipmentView);\r\n    for(const auto& V:CachedEnemyLocations) if(!ParisTacticalEquipment::Occluded(GetWorld(),EquipmentEye,V)) Dot(V,Danger,2.5);');p.write_bytes(data)
print('Unbuilt v6 source refreshed before its immutable compilation snapshot')
