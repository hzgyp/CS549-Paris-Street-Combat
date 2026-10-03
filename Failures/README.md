# 失败案例索引 / Failure case index

**开发前必读。** 每个新工作包先阅读需求与本索引，再阅读直接相关案例的失败分析。实施文档必须列出“已读案例、这次改变了什么、如何证明不会重犯”。功能测试通过不能替代人工视觉验收。没有相关案例时也要明确记录查阅结果。

这里保存经验和证据，不是可以直接执行的旧方案。归档脚本含历史绝对路径、旧 package 名和一次性保存操作；禁止从归档原地运行。需要复用时只提取经过审查的片段，使用新版本/证据名并重新验证。

| 案例 | 状态/范围 | 开发前必须记住 |
| --- | --- | --- |
| [FP001 — 第一人称强行入镜与前臂裁切](FP001-20261003-first-person-view/FAILURE_ANALYSIS.md) | 本次专门归档；7 个原生资产及独有文档/工具，实际迁移状态见 MANIFEST/VERIFICATION | 先建立自然持枪参考；双臂入镜、枪口数值对准和测试通过都不等于画面合格。 |
| [关联：V2 首轮静止实验](../Docs/Development/FIRST_PERSON_PRESENTATION_REBUILD_RESULT_20261003_ZH.md) | 归档后重建的有限诊断；未生成原生资产，源快照/结果/截图留在独立证据目录，本次登记关联 | 三种整套姿态搬位均出现自身遮挡，按预定条件停止；不要继续扫偏移。截图需核对实际游戏视口，不能只检查文件存在。 |
| [关联：连续手臂动态取样](../Docs/Development/CONTINUOUS_ARMS_DYNAMIC_RESULT_20261003_ZH.md) | 新机制内部动作/枪口测试已有结果；保留启动、误取编辑器图、相机浮点完全相等断言失败 | 失败full批次即使退出0也不能写整体通过；使用声明容差、独立补测与逐图复核。泛用换弹/代理握点不等于M1专用接触验收。 |
| [关联：UE原生显示迁移](../Docs/Development/CONTINUOUS_ARMS_NATIVE_IMPLEMENTATION_V1_ZH.md) | 用户认可预览模型但反馈移动卡顿，要求去除Python显示更新；保留两次反射名作者失败 | Python脚本名不等于C++反射函数名，核对安装头文件。标准Blueprint编译/运行必须重新验收。未冻结截图有请求/实际帧差异，不可拿下一阶段图证明换弹接触；去除Python不等于城市性能通过。 |
| [关联：V4 瞄准试验](../Docs/Development/RIFLE_CROSSHAIR_ALIGNMENT_RESULT_20261002.md) | 较早未选中试验；本次仅关联登记，原生资产仍按原库存保留，未宣称已迁移 | 枪口收敛时仍可能失去手部接触或第一人称取景；不能用这份未通过版本作为已验收基线。 |
| [关联：粗糙手指层被否决](../Docs/Development/WEAPON_GRIP_REPAIR_RESULT_20261002.md) | 历史失败；原资料保留原位 | 数值接触不能替代网格检查；原手指姿态保护，禁止重启该方案。 |
| [关联：详细人物生产路线停止](../AGENTS.md#failed-character-production-route---binding-project-decision) | 项目绑定决定；旧实验保留原位 | 使用已完成、授权兼容的资产；不通过新技能/更长提示/更多轮次重启被否决的详细人物制作。 |

## 存储及新增案例规范

- 本目录的分析、源代码、差异、清单可进入源码管理；本轮没有提交或推送。
- 商业衍生原生资产、图片/录像、日志/崩溃及二进制产物保存在 ignored 的私有工作区 FailureArchive。案例 MANIFEST 给出逐文件原位置、归档位置、大小及 SHA-256。不能将其 force-add 到 Git。
- 同一失败案例保留失败与成功的局部测试，注明它们各自证明什么；不得把干净重跑写成已经解释此前崩溃。
- 移动共享文件前检查依赖。共用资源留在原位；共用源码只撤回本案例的修改，保存 before snapshot 和准确 diff，禁止整文件 Git 回滚覆盖其他工作。
- 离线原生归档保持原 package 内部身份。它不是 package 改名、Catalog 选择或自动恢复权限；恢复必须先检查原路径是否已被新工作占用，再单独计划。

## Required pre-development review

Read the requirements and this index before authoring. Every implementation document records relevant case IDs, the changed hypothesis/design, an early falsifiable acceptance check and a stopping condition. Preserve factual distinctions between visual rejection, runtime failure, known limitation and unverified cause. A new approach must explain how it differs from the rejected one before spending another iteration.
