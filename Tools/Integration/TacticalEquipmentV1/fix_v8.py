from prepare import OUT
from pathlib import Path
import shutil
here=Path(__file__).parent
p=here/'ParisTacticalEquipment.cpp';s=p.read_bytes();s=s.replace(b'#include "Engine/World.h"',b'#include "Engine/World.h"\r\n#include "Engine/OverlapResult.h"');p.write_bytes(s)
p=here/'ParisEquipmentAudio.inl';s=p.read_bytes();s=s.replace(b'const FString File=',b'FString File=');s=s.replace(b'checkf(FFileHelper::LoadFileToArray(Bytes,*File)',b'if(!FPaths::FileExists(File))File=FPaths::ProjectDir()/TEXT("Audio/equipment_explosion.wav");checkf(FFileHelper::LoadFileToArray(Bytes,*File)');p.write_bytes(s)
base=OUT/'candidate_full_v8/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1'
assert not (OUT/'candidate_full_v8/build-editor.json').exists()
for name in ['ParisTacticalEquipment.h','ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentSave.cpp','ParisEquipmentSightBridge.h','ParisEquipmentWorld.inl','ParisEquipmentAudio.inl','ParisEquipmentChecks.inl']:shutil.copyfile(here/name,base/'Private'/name)
for name,header in [('ParisBridgeMission.cpp','ParisBridgeMission.h'),('ParisMissionInteraction.cpp','ParisMissionInteraction.h'),('ParisBridgeMissionV1.cpp','Modules/ModuleManager.h')]:
 p=base/'Private'/name;s=p.read_bytes()
 if name!='ParisBridgeMissionV1.cpp':
  include=('#include "'+header+'"\r\n').encode();assert s.count(include)==1;s=include+s.replace(include,b'');p.write_bytes(s)
audio=OUT/'candidate_full_v8/Project/Audio';audio.mkdir(exist_ok=True);shutil.copyfile(OUT/'intake-explosion/explosion.wav',audio/'equipment_explosion.wav')
print('v8 includes restored first-header ordering and explicit overlap definition; Editor audio fallback')
