from pathlib import Path
root=Path(__file__).resolve().parents[3]
f=root/'tmp/g1-tactical-equipment-20261010/candidate_equipment_wheel_v1/Project/Plugins/ParisBridgeMissionV1/Source/ParisBridgeMissionV1/Private/ParisEquipmentWheelChecks.inl'
t=f.read_text('utf-8');old='CheckStep==10&&S.ThrowKind.IsEmpty()&&CheckClock>4'
assert old in t;t=t.replace(old,'CheckStep==10&&S.ThrowKind.IsEmpty()&&!S.Clouds.IsEmpty()')
f.write_text(t,encoding='utf-8')
f=root/'Docs/Development/MissionLoopV1/EQUIPMENT_WHEEL_INPUT_IMPLEMENTATION_20261011_ZH.md'
t=f.read_text('utf-8');t+='\nv3补充（MI043）：保留原Start/Far动作及提交后的3.5秒引信，烟幕见证等待实际Clouds生成再查库存和返回枪械，仍有30秒失败截止；不从按下时刻提前要求已有烟幕。v2失败源／Game／结果保持。\n';f.write_text(t,encoding='utf-8')
print('Smoke witness uses actual deployment state; unchanged fuse')
