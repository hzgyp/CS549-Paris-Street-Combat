from pathlib import Path
root=Path(__file__).resolve().parents[3];f=Path(__file__).with_name('deliver.py');t=f.read_text('utf-8')
t=t.replace("'restore_legacy']:check", "'restore_legacy','performance']:check")
t=t.replace(".replace(b'G1GrenadeModels20261011',b'G1GrenadeEquip20261011').replace(b'ParisGrenadeModelsV1',b'ParisGrenadeEquipV2')", ".replace(b'G1EquipmentWheel20261011',b'G1GrenadeEquip20261011').replace(b'ParisEquipmentWheelV1',b'ParisGrenadeEquipV2')")
s=t.index("(normal/'README_ZH.md').write_text('''");e=t.index("''',encoding='utf-8')",s)+len("''',encoding='utf-8')")
readme='''# 手持投掷物与库存轮换修订统一试玩

运行 PLAY_GRENADE_EQUIP.cmd。

- 滚轮在步枪与仍有库存的手雷／烟雾弹之间正反轮换；耗尽类型直接跳过。
- 两种投掷物全用完后保持步枪，滚轮不改变姿势或鼠标按压状态。
- 切到投掷物使用现有手雷就绪Loop，外壳展示在手中；左键按住进入准备／持握，松开投出，完成后回枪。
- 松手前Esc／滚轮取消，不扣库存，旧松开不误射；松手后等待原投出动作完成。G/Q旧直接投掷停用。
- E拆雷／补给／全灭敌军后的圈内保存，Esc战地手册，Tab人物小队保持。

本版修正上一版端枪姿势、手雷遮挡及空槽轮换。原MkII／烟雾模型和贴图、原枪械手指常量／枪械内部逻辑／原保存代码、身体移动、AI／导航、地雷补给及死亡承接。原准备／投出／库存／引信／伤害／烟幕函数逐字保持。独立UserDir G1GrenadeEquip20261011／前缀ParisGrenadeEquipV2；原用户档保持。必须保留完整Windows目录，不能只复制exe。

普通入口没有探针、自动操作、隐藏手部或摄影机／AI／资源覆盖。15项同一Game检查和实际图通过本机验证，细致全程接触／所有动作与人类操作仍由统一试玩评审；未正式采用或发布。
'''
t=t[:s]+"(normal/'README_ZH.md').write_text("+repr(readme)+",encoding='utf-8')"+t[e:]
start=t.index('limitations=[');end=t.index('],publication=',start)+1
t=t[:start]+"limitations=['Actual ready/hold frames reviewed; detailed continuous contact and all locomotion transitions remain manual review.','Temporary FP source only; original body/camera/rifle controls and save schema retained.','Current roster performance only, not expanded NPC stress or second-machine acceptance.']"+t[end:]
f.write_text(t,encoding='utf-8');print('Delivery tool targets fresh UserDir and truthful revised scope')
