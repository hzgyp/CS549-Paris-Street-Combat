from pathlib import Path
from prepare import OUT
import shutil
here=Path(__file__).parent
p=here/'ParisEquipmentSmoke.inl';s=p.read_bytes()
old=b'Required->Material=SourceLOD->RequiredModule->Material;'
assert s.count(old)==1
s=s.replace(old,b'auto* Material=UMaterialInstanceDynamic::Create(SourceLOD->RequiredModule->Material,PS);Material->SetScalarParameterValue(TEXT("Opacity"),1.f);Material->SetScalarParameterValue(TEXT("Fade_Distance"),20.f);Material->SetVectorParameterValue(TEXT("Color"),FLinearColor(.72,.73,.70));Required->Material=Material;')
p.write_bytes(s)
p=here/'ParisEquipmentChecks.inl';s=p.read_bytes();old=b'R->SetNumberField(TEXT("interpolation"),int32(Required->InterpolationMethod));';assert s.count(old)==1;s=s.replace(old,old+b'float MaterialOpacity=0;Required->Material->GetScalarParameterValue(FMaterialParameterInfo(TEXT("Opacity")),MaterialOpacity);R->SetNumberField(TEXT("material_opacity"),MaterialOpacity);');p.write_bytes(s)
base=OUT/'candidate_full_v15/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private'
assert not (OUT/'candidate_full_v15/build-game.json').exists()
for name in ['ParisEquipmentSmoke.inl','ParisEquipmentChecks.inl']:shutil.copyfile(here/name,base/name)
p=Path('Failures/MI027-20261011-smoke-atlas-hazard-owner/ANALYSIS.md');s=p.read_bytes();s+='\n\n只读 Editor commandlet MATERIALS.json 测得 MI_Smoke 的材质 Opacity=0.1、Fade_Distance=0；此前只调粒子透明度遗漏了材质自身倍率。下一 transient MID 使用已cook父材质，明确Opacity=1/Fade_Distance=20，复用已有实例的软接触尺度，仍用同一烟浓度驱动粒子alpha与体积；原材质字节不变，实际截图才作显示门槛。材料审计进程正常自行退出，主Editor保持开着。补正上文位置描述：ue_bridge_hook.py 在 PC_UpdateSquad override 插入桥接hook，并非脚本直接安装ReceiveTick；确定的冲突是原hook中的PC_PolicyHold/StopMovement，具体调用调度不冒称已逐帧追踪。\n'.encode();p.write_bytes(s)
print('Audited original material opacity0.1; transient cooked-parent MID opacity1, fade20, same logical smoke concentration')
