from pathlib import Path
root=Path(__file__).resolve().parents[3]
p=root/'tmp/g1-tactical-equipment-20261010/candidate_equipment_wheel_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
f=p/'ParisTacticalEquipment.cpp';t=f.read_text('utf-8')
# SceneViewport emits both digital wheel keys and MouseWheelAxis for each notch.
# Selection uses the digital pair only, to avoid selecting twice on real hardware.
t=t.replace('    if(Params.Key==EKeys::MouseWheelAxis&&Params.Event==IE_Axis&&Params.AmountDepressed!=0)Wheel=Params.AmountDepressed>0?-1:1;\n','')
t=t.replace('if(S.ThrowStage==TEXT("Release")||S.ThrowCommitted)return true;','if(S.ReleaseQueued||S.ThrowStage==TEXT("Release")||S.ThrowCommitted)return true;')
t=t.replace('if(Params.Key==EKeys::E&&M->InsideCheckpoint()){if','if(Params.Key==EKeys::E&&M->InsideCheckpoint()){if(S.ReleaseQueued||S.ThrowStage==TEXT("Release"))return true;if')
t=t.replace('if(S.ThrowStage==TEXT("Start")||S.ThrowStage==TEXT("Hold")){S.ReleaseQueued=false;','if(!S.ReleaseQueued&&(S.ThrowStage==TEXT("Start")||S.ThrowStage==TEXT("Hold"))){S.ReleaseQueued=false;')
t=t.replace('S.HadWindowFocus&&!Focus&&!S.ThrowKind.IsEmpty()&&','S.HadWindowFocus&&!Focus&&!S.ReleaseQueued&&!S.ThrowKind.IsEmpty()&&')
t=t.replace('#include "ParisEquipmentChecks.inl"','#include "ParisEquipmentChecks.inl"\n#include "ParisEquipmentWheelChecks.inl"')
t=t.replace('if(CheckMode==TEXT("models")){','if(CheckMode==TEXT("wheel")){EquipmentWheelCheck(W,M,S,PC,P,DT);return;}\n    if(CheckMode==TEXT("models")){',1)
f.write_text(t,encoding='utf-8')
print('Digital wheel only; release commitment guarded; probe included')
