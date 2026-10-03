# FP001 — rejected first-person view V1

**归档完成，原候选退役。** 首先读 [失败原因](FAILURE_ANALYSIS.md)，再按需查看 [原文档](Docs/FIRST_PERSON_VIEW_REPAIR_RESULT_20261003_ZH.md)、[清单](MANIFEST.json) 和 [核验结果](VERIFICATION.json)。

- 664 项原文件/快照，640,322,531 字节，全部核对大小及 SHA-256。
- 7 个独有原生资产移出 active Content，6 份文档、14 个专用工具和原库存移入本案例。
- 共用源码的 3 处文件保存 [修改前快照](Changes/Before/) 与 [撤回差异](Changes/withdraw_fp001.patch)，只撤回本试验部分。v25 二进制私下保留，部署恢复至经过原哈希验证的 pre-FP 版本。
- 原有 40 个原生文件及 V3 地图不变；归档后独立、Bridge 禁用的 V3 战斗回归 15 项/62 断言通过，退出 0。全体选中本地资源 17,273 项哈希验证通过。
- 没有提交、推送、Catalog/allowlist 更改、远程资源发布或自动恢复授权。

## 实际目录

本目录保存可管理的文字、源码及元数据。二进制/图像/日志等实际归档位于：

`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/FailureArchive/FP001-20261003-first-person-view/`

其中 `Native/Content/ParisCombat/` 保持资产原相对结构；`Evidence/FirstPersonViewV1/` 与 `Evidence/Runtime/` 保存试验记录；`LogsAndBuild/`、`Crashes/`、`DeployedV25/` 保存相关产物。商业衍生字节不会进入 Git。共享模型、原动作和此前 V4 草稿仍在原位置，属于受保护依赖，不是本案例产生的 7 个资产。

原证据内部路径没有重写。通过 MANIFEST 的 `original_path` 查找相应 `archive_path`。归档工具的原路径依赖已经失效；不可在此目录运行它们。后续复用须经过审查并使用新身份。

归档后可选的空目录清理被自动审批拒绝，因此原位置可能保留空目录；文件已迁移且逐项核验，空目录不代表仍有活动资产。没有尝试绕过该拒绝。

## 完整性检查

`Tools/Archive/verify_failure_archive.py --case FP001-20261003-first-person-view` 验证归档与退役路径。

`--protected` 额外比对此时的 40 文件基线。未来若获准修改了这些文件，不能把历史基线差异当成恢复旧文件的理由。归档本身的字节仍应保持一致。

## 新工作入口

[V2 实施文档](../../Docs/Development/FIRST_PERSON_PRESENTATION_REBUILD_V2_ZH.md)明确说明本次如何避免重犯；不是重启本案例。静止构图、运动、枪口接口和最终人工作为不同验收阶段，不相互冒充。
