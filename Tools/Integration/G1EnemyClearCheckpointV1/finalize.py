"""Publish local review metadata only after verified native receipts; no Git/SFTP adoption."""
from prepare import ROOT,OUT,SOURCE,load,sha
from pathlib import Path
import json
def main():
 r=load(OUT/'RUNTIME.json');v=load(OUT/'verification.json');assert v['status'].startswith('pass_')
 assert r['game_sha256']==v['game_sha256'];old=load(OUT/'freeze.json')['parent']
 selector=dict(schema_version=2,date='2026-10-10',review_id='g1-enemy-clear-checkpoint-'+r['revision']+'-20261010',status=v['status'],selection='Latest local checkpoint candidate; official selected audio V2 unchanged',authorization='User: all checkpoint save objective gates depend only on complete enemy elimination',rule='Original registered German1/2/3 all dead: G1 complete and checkpoint unlocked. No far-bank/occupation/squad/posture/movement/safe-seconds gate. Circle entry and explicit confirmation retained.',plan='G1_ENEMY_CLEAR_CHECKPOINT_IMPLEMENTATION_20261010_ZH.md',result='G1_ENEMY_CLEAR_CHECKPOINT_RESULT_20261010_ZH.md',source_snapshot=SOURCE.relative_to(ROOT).as_posix(),source_files=52,source_manifest=(SOURCE.parent/'SOURCE_MANIFEST.json').relative_to(ROOT).as_posix(),source_manifest_sha256=r['source_manifest_sha256'],active_authoring_project=(OUT/r['revision']/'Project/WW2FranceLiberation.uproject').relative_to(ROOT).as_posix(),playable_directory=Path(r['path']).relative_to(ROOT).as_posix(),playable_entry=(Path(r['path'])/'PLAY_G1_REVISION.cmd').relative_to(ROOT).as_posix(),game_sha256=r['game_sha256'],save_directory='%LOCALAPPDATA%/ParisStreetCombat/'+r['user_directory'],save_prefix='ParisG1PlaytestV5',verified_runs=v['verified_runs'],private_verification=(OUT/'verification.json').relative_to(ROOT).as_posix(),previous_checkpoint_candidate=old,publication='No baseline adoption, commit/push, cleanup, SFTP/video/PDF changes')
 docs=ROOT/'Docs/Development'
 (docs/'CURRENT_CHECKPOINT_REVIEW.json').write_text(json.dumps(selector,indent=2)+'\n',encoding='utf-8')
 (docs/'CURRENT_CHECKPOINT_REVIEW.md').write_text('''# 当前 checkpoint 本地复检候选

2026-10-10，最新用户规则：完全消灭该区域的登记敌军即可完成任务并解锁 checkpoint。
不再要求经过指定远岸点、站在占领中心、队友全部过桥、站立、停步或安全等待。
保留进入金色圈主动 E 确认，写盘与回读通过后才显示成功窗口。

见 [实施](G1_ENEMY_CLEAR_CHECKPOINT_IMPLEMENTATION_20261010_ZH.md)、
[结果](G1_ENEMY_CLEAR_CHECKPOINT_RESULT_20261010_ZH.md) 和 [JSON](CURRENT_CHECKPOINT_REVIEW.json)。
正常入口：`'''+selector['playable_entry']+'''`。
模型、手指、枪械、弹药、原存档校验和终态尸体保护；旧候选及其测试保留。
本轮有限隔离原生诊断通过，人工试玩待复验；正式 selected audio V2 未覆盖，未发布。
本轮没有新的自然交火、小队过桥、性能或第二台电脑验收。
''',encoding='utf-8')
 table='\n'.join('| '+name+' | '+run['status']+' | '+str(run['checks'])+' | 0 |' for name,run in v['verified_runs'].items())
 result='''# G1 清场即可完成与保存修复结果

2026-10-10，本地候选 '''+r['revision']+'''，人工试玩待复验。
用户最新规则优先于旧版小队到达/占领阶段门槛；旧小队测试结果作为历史证据保留。

## 已修复

三名登记德军实际死亡即直接 Won 并解锁圈，Crossing 阶段也可完成，
不会因漏过指定远岸点或队友尚未过桥卡住。0/1/2 名死亡不能解锁。
保存提示、E/F5 发起交互、失败重试和实际存储共用清场条件；姿态、速度、
小队 Ready/位置和安全等待秒数不再作为存储 admission。
仍需在金色圈内主动按 E，成功后 OK 窗口和关闭询问保留，同次进圈 E/F5 不重复写。
双槽序号、身份/资源守恒、原存档 schema/checksum、写盘及回读校验保持原字节逻辑。
保存低姿态时仅把 player 的位置高度按原站姿胶囊换算，供原 lifecycle loader
恢复同一脚底位置；现场姿态、其他角色位置与存档字段均不改变。

## 验证与范围

| 独立运行 | 状态 | 检查数 | 退出码 |
| --- | --- | ---: | ---: |
'''+table+'''

clearance 是明确的隔离门槛回归：原新游戏六人阵容、诊断玩家摆到 G1、
AI hold、逐个执行原 PC_Die 端点；不是自然交火或实际移动过桥。
实测最后一敌死亡时任务仍来自 Crossing、两名活盟军均在对岸且 transit 未完成，
立即 Won；移动/蹲姿圈内 E 直接进入 Saving，真实写盘回读成功 serial1。
隔离的下一槽只读造成真实写失败、旧槽和序号不变，Retry 后成功 serial2。
全过程无 Waiting/Finish securing，写盘均发生在 Saving 已画出之后。
成功窗口/提示消失、重复键、圈外交互拒绝、F9/F6 与新进程 serial2 恢复通过。
legacy 单独读取原 V5 已验证 journal，尸体第一帧及三秒终态保持。
模型/手指/枪械和固定 NPC 位置、导航碰撞/AI 实现没有变化。

52 源文件只改任务/HUD、交互 admission、有限诊断三个 cpp；反射声明不变。
1754 原生资产、父源/Game、当前用户文件、Catalog 与七个原受保护区段通过。
旧失败 candidate_v1 注释编译错误及 v2 低姿态恢复中心偏移见 MI023，原 Project/日志保留。
没有进入 Editor、录制、清理、Git/SFTP 发布或新自然交战/小队/性能/第二机验收。

## 可复查身份与入口

- 正常试玩：`'''+selector['playable_entry']+'''`。
- 独立正常用户目录：`'''+selector['save_directory']+'''`，原 V5 格式。
- Game SHA256：`'''+r['game_sha256']+'''`。
- 52-file manifest SHA256：`'''+r['source_manifest_sha256']+'''`。
- 新源：`'''+selector['source_snapshot']+'''`；当前 Project：`'''+selector['active_authoring_project']+'''`。
- 私有原生结果/图片/保护清单：`'''+OUT.relative_to(ROOT).as_posix()+'''`。

人工复验：从新任务自行过桥、击杀三敌；无需特意经过远岸点或等小队。
进金色圈按 E，查看 CHECKPOINT SAVED / OK；关闭后不应再有 E SAVE / ESC LATER。
F9 检查死亡德军、资源与已完成任务；F6 重开应有三名活敌军且圈再次锁定。
本轮仅 Game 构建；后续 Editor 入口必须重新构建当前匹配源，不能使用缓存 Editor DLL。
'''
 (docs/'G1_ENEMY_CLEAR_CHECKPOINT_RESULT_20261010_ZH.md').write_text(result,encoding='utf-8')
 prefix='''## 2026-10-10：checkpoint 清场判定修复（最新用户规则）

所有 checkpoint 的任务门槛只看登记敌军完全消灭；G1 不再依赖远岸点、占领阶段、
小队到达、姿态或停步。详见 CURRENT_CHECKPOINT_REVIEW 与清场修复实施/结果。
正常入口 `'''+selector['playable_entry']+'''`，独立用户目录，原事务/资源/模型保留。
有限隔离原生门槛、实际写盘失败重试、F9/F6/新旧 V5 恢复通过，人工试玩待复验。
旧小队结果仍是历史证据，清场成功不能当作新的全小队过桥通过。
正式 selected JSON 保留 audio V2；无自动发布/删除/进入旧 Editor。

'''
 for name in ['HANDOFF.md','Docs/Development/CURRENT_DEVELOPMENT_BASELINE.md']:
  p=ROOT/name;text=p.read_text(encoding='utf-8-sig');assert prefix.split('\n')[0] not in text;p.write_text(prefix+text,encoding='utf-8')
 (Path(r['path'])/'README_CHECKPOINT_RULE.md').write_text('''Checkpoint objective: eliminate every registered G1 guard.
No far-bank marker, squad arrival, posture or movement requirement.
Enter the gold circle and press E to save. CHECKPOINT SAVED / OK appears only after verified disk write.
Normal entry: PLAY_G1_REVISION.cmd. No observer or pre-completed save in this entry.
This local candidate requires human review; prior source, model, weapon and save anchors retained.
''',encoding='utf-8')
 print(json.dumps(dict(status='local_review_metadata_written',entry=selector['playable_entry'],runs=selector['verified_runs'])))
if __name__=='__main__':main()
