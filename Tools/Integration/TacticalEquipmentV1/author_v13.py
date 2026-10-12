from pathlib import Path
import shutil
from prepare import OUT
here=Path(__file__).parent
base=OUT/'candidate_full_v13/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
assert not (OUT/'candidate_full_v13/build-game.json').exists()
p=here/'ParisEquipmentSmoke.inl';s=p.read_bytes().replace(b'for(auto* Module:SourceLOD->Modules)',b'for(auto Module:SourceLOD->Modules)').replace(b'DuplicateObject<UParticleModule>(Module,PS)',b'DuplicateObject<UParticleModule>(Module.Get(),PS)');p.write_bytes(s)
p=here/'ParisEquipmentChecks.inl';s=p.read_bytes().replace(b'M->Phase.ToString()',b'M->Phase');p.write_bytes(s)
for name in ['ParisTacticalEquipment.h','ParisTacticalEquipment.cpp','ParisEquipmentState.h','ParisEquipmentSave.cpp','ParisEquipmentSightBridge.h','ParisEquipmentWorld.inl','ParisEquipmentAudio.inl','ParisEquipmentChecks.inl','ParisEquipmentSmoke.inl']:shutil.copyfile(here/name,base/name)
p=base.parent/'ParisBridgeMissionV1.Build.cs';s=p.read_bytes();s=s.replace(b'"RenderCore",',b'"RenderCore", "RHI",');p.write_bytes(s)
p=Path('Failures/README.md');s=p.read_bytes();s=b'11 October equipment smoke/evade: [MI027](MI027-20261011-smoke-atlas-hazard-owner/ANALYSIS.md) retains the invisible-smoke image, MoveTo-without-movement failure and v12 compile prerequisites. Require matching cooked atlas inputs and actual finite movement.\n\n'+s;p.write_bytes(s)
p=Path('Docs/Development/MissionLoopV1/TACTICAL_EQUIPMENT_IMPLEMENTATION_20261010_ZH.md');s=p.read_bytes();s+=('\n\n11 October continuation: MI027 read. Preserve original cooked smoke atlas/SubUV/dynamic inputs in transient instances; record actual particle count/alpha/size and inspect dense image. Finite hazard ownership records and restores original Hold/Generation, proving actual movement and brain resume. v12 failed compile is retained; v13 fixes UObject pointer iteration/serializer prerequisites, with a separate opt-in current-six-actor normal-AI performance check. No relaxation of asset/save/path admission; stop on missing actual rendering or movement.\n').encode();p.write_bytes(s)
print('v13 prerequisites corrected; source installed')
