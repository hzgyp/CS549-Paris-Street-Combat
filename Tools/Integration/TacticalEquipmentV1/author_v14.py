from prepare import OUT
from pathlib import Path
import shutil
here=Path(__file__).parent
p=here/'ParisEquipmentSmoke.inl';s=p.read_bytes()
old=b'LOD->RequiredModule=DuplicateObject<UParticleModuleRequired>(SourceLOD->RequiredModule,PS)'
assert s.count(old)==1
s=s.replace(old,b'LOD->RequiredModule=NewObject<UParticleModuleRequired>(PS)')
old=b'Required->Material=Source->Emitters[0]->LODLevels[0]->RequiredModule->Material;'
assert s.count(old)==1
s=s.replace(old,b'Required->Material=SourceLOD->RequiredModule->Material;Required->SubImages_Horizontal=SourceLOD->RequiredModule->SubImages_Horizontal;Required->SubImages_Vertical=SourceLOD->RequiredModule->SubImages_Vertical;Required->InterpolationMethod=SourceLOD->RequiredModule->InterpolationMethod;')
s=s.replace(b'LOD->Modules.Add(DuplicateObject<UParticleModule>(Module.Get(),PS))',b'LOD->Modules.Add(Module)')
p.write_bytes(s)
base=OUT/'candidate_full_v14/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
assert not (OUT/'candidate_full_v14/build-game.json').exists()
shutil.copyfile(p,base/p.name)
p=Path('Failures/MI027-20261011-smoke-atlas-hazard-owner/ANALYSIS.md');s=p.read_bytes();s+='\n\nv13 smoke 原生运行在 Required::Serialize 的 cooked-data 检查退出3：DuplicateObject 会经过加载序列化，却不是 cooking archive，不能复制这种已 cook 模块。引擎 ParticleModules.cpp 1104–1123 明确对应这个失败，不是GPU启动异常。后续新建 Required，仅复制必要图集数/插值/材质值；只读引用现有已cook的 SubUV/dynamic 模块，不串行化副本或修改原件。v13运行/源码保留，重新检查实际画面与粒子数据。\n'.encode();p.write_bytes(s)
print('v14 retains existing cooked SubUV/dynamic references and copies necessary public Required values without serialized duplication')
