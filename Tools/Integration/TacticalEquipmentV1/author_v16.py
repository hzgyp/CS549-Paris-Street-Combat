from pathlib import Path
from prepare import OUT
import shutil
p=Path(__file__).parent/'ParisEquipmentSmoke.inl';s=p.read_bytes();old=b'SetScalarParameterValue(TEXT("Opacity"),1.f)';assert s.count(old)==1;s=s.replace(old,b'SetScalarParameterValue(TEXT("Opacity"),3.f)');p.write_bytes(s)
base=OUT/'candidate_full_v16/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private';assert not (OUT/'candidate_full_v16/build-game.json').exists();shutil.copyfile(p,base/p.name)
p=Path('Failures/MI027-20261011-smoke-atlas-hazard-owner/ANALYSIS.md');s=p.read_bytes();s+='\n\nv15_early 已有可见烟，逻辑双向过滤/穿烟射击通过，且实际避险位移和Brain恢复通过；但画面仍能辨认中央敌人的姿态，记为烟浓度不足，不能给满浓度视觉通过。基于这张135粒子/180cm/alpha0.595/材质Opacity1的实际画面，做一次有界材质倍率3的浓度校正，粒子数、尺寸、逻辑半径、Shader/原资产不变；再看同一受控车道图，若仍可清楚辨认目标则停止本参数方案。机制回归有确切v15_early身份；v16仅此一行数值变化，新的烟幕/存取/性能必须实跑，其他逐字未变机制可明确承接，不改称v16实跑。\n'.encode();p.write_bytes(s)
print('v16 single bounded visual-density calibration after actual v15 image; all other source bytes retained')
