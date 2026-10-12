# 清场 checkpoint 正式基线合并与本机版本清理实施

2026-10-10。用户人工复验最新版本无问题，明确要求合并正式基线、删除过渡版本，并减少过时正式版本。

## 已读案例与本次变化

已读 AGENTS、HANDOFF、CURRENT_DEVELOPMENT_BASELINE、CURRENT_CHECKPOINT_REVIEW、
MI019（反射布局与 cooked 包不匹配）、MI022（窗口编译失败及独立启动 GPU 崩溃）、
MI023（清场仍被 Crossing 阶段锁住、低姿态保存后位置漂移），以及先前 HUD/audio 清理的恢复契约。
本次仅正式选定人工通过的 enemy-clear candidate_v3，不重新修改玩法或资产，也不以旧小队门槛回滚清场规则。

正式源为 `Unreal/Variants/G1EnemyClearCheckpoint20261010/Project` 的 52 文件快照，
manifest SHA256 `66d8c6e3fc005090ebe44e31f6a8dabd0fdbe1871ffed613cb3769f5b334508a`；
Game SHA256 `b40409b08830cc0e1d306ceab0575d7e61db382f50853426bbda58d08f385079`。
保留该版本 authoring Project、普通试玩目录和独立用户存档目录。

## 早期验收与精确清理范围

先核对正式 52 文件、匹配 authoring 文件和两份 Game、普通入口无诊断参数、
既有四次原生结果（37/26/31/31 项）、1754 原生保护文件及 Catalog。
用户人工通过记录为本次选择依据，不能扩写为新增性能、第二机、Editor 或课程验收。
冻结用户所有现存 ParisStreetCombat 存档/配置/日志及本轮保留的源、失败、图片、原始检查记录。

仅删除以下本机生成物，实际文件清单、尺寸和时间记录在私有冻结 inventory：

- 除最新 enemy-clear v3 外的 19 个 `tmp/Playtest-G1-*` 试玩目录。
- 已被替代的 feedback v1–v4、P1 v1–v9、completion v1–v9、dialog v1–v3、enemy-clear v1–v2、
  HUD v3、AV v1、recorded-Foley v1、audio V2 v1–v2 Project 内的 Binaries、Intermediate、DerivedDataCache。
  包括其插件内相同名称的派生目录。保留 Project 源、Config、Audio、Content junction、Saved/cooked 输入和构建收据。
- 本机旧 audio V2 发布 ZIP；其现有 SFTP 课程下载对象、说明和凭据附件保持有效，不变更远端。

原模型、手指、动作、枪械、原生地图、导航碰撞、音频源、用户文件、失败源/日志/图、
原始检测结果、legacy V13 ZIP 及早前唯一文件恢复 ZIP 均不在删除范围。
本次保留一份正式可运行目录；旧版本只保留精简源码/证据及去重的唯一二进制恢复包。
当前普通入口不移动，避免破坏已验证路径；增加稳定的当前基线启动入口。

## 恢复与执行

旧试玩/Binaries 的全部文件按 SHA256 去重：相同字节映射到保留的正式目录；
不同的可执行文件、启动器和说明放入私有压缩恢复包，逐项回读校验。
Intermediate/DDC 为可重新构建的缓存，保存清单而不承诺缓存逐字恢复。
本机旧完整发布 ZIP 已有保留的远端认证副本，记录其既有身份；不为同一 ZIP 再留全量本机副本。
旧恢复清单中指向 audio V2 普通目录的引用通过新恢复映射继续解析，原始清单不改写。

执行使用 PowerShell LiteralPath，并逐个验证绝对目标位于当前工作区，拒绝 reparse 目标/后代和当前正式目录。
清理前重新确认没有游戏、Editor 或构建进程；不终止用户进程。
文件集合、尺寸/时间、恢复字节或保护身份变化即停止；不得扩大清理范围或忽略错误。
完成后复核所有目标已移除、正式包/源/原生资产/用户文件未改变，并实测磁盘空闲增量。
当前选择文件和交接入口更新到正式 52 文件；旧结果作为有日期的历史记录保留。
本任务不自动 commit/push、SFTP 同步、录制、进入 Editor 或改写课程 PDF。
