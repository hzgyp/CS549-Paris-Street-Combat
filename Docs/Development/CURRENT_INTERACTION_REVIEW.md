## 2026-10-10：已被正式清场基线取代

本文件以下为历史记录；普通试玩目录已退休，源与测试收据保留。
当前入口和52文件基线见 [CURRENT_DEVELOPMENT_BASELINE](CURRENT_DEVELOPMENT_BASELINE.md)，
旧字节见本轮恢复清单。

# 当前菜单与存档交互复查候选

10 October 2026。candidate_v4 本机 Game 回归通过，等待用户人工复验；原
audio V2 保持已选开发基线。

普通试玩：`tmp/Playtest-G1-Interaction-V4-20261010/PLAY_G1_REVISION.cmd`。
使用独立 `G1Interaction20261010` 用户存档目录，没有测试辅助参数。

已实现鼠标/键盘菜单、禁用 Load 原因、开始点击不射击；E 可重新请求存档并
说明失败原因，原安全/枪械/资源/存档事务和模型手指保留。1080p/720p 菜单、
兼容旧槽/负例重试/新进程恢复、完整新任务清场保存回归通过。

读 [实施方案](G1_TEAM_FEEDBACK_IMPLEMENTATION_20261010_ZH.md)、
[结果及复验清单](G1_TEAM_FEEDBACK_RESULT_20261010_ZH.md)、
[MI019](../../Failures/MI019-20261010-menu-checkpoint-interaction/FAILURE_ANALYSIS.md)
和同名 JSON，核对 exact source/Game 身份。v3 失败入口禁止作为试玩候选。
不可从旧目录名称推断当前选择；候选必须得到人工复验后才可替换已选基线。
