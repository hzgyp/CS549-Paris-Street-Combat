# 组员恢复当前确定版本

2026年10月20日。请从清理后的开发仓库重新克隆，按该次克隆的 Catalog 恢复。仅供郭昱普、蒲宇琪、吴景迪三名已获授权成员开发协作。SFTP 地址、账户、私钥和已核验的主机指纹文件通过原有私下渠道获取，不进入 Git；这些操作不用于课程提交。

教学正式版仍是 tutorial1.0／source145／revision12。Game SHA256：`3bb90f646cbbfb3652bab5fcab23c0af2b3bd2d7add577028e6810a9c5576967`；源码清单 SHA256：`faa136ed3bbafa07e93253b3c6faefab6eb4380cc06e657ee9d3c67baa0a9c91`。平台与 NPC 代码沿用17—18日选定版本。本轮只补齐恢复依赖，不改变玩法或绘测结果。

使用 Python3.13 和 Windows OpenSSH，在克隆根目录先查看计划：

```powershell
python Tools/Integration/restore_selected_development.py workbench plan
python Tools/Integration/restore_selected_development.py tutorial-source plan
```

| 参数 | 恢复内容 | 位置 |
|---|---|---|
| `workbench` | 平台首次刷新必需的历史源码清单、使用关系及设计文档上下文，以及 NPC 的16张候选／状态图和原始校验记录 | 克隆内的原始相对路径，可用于首次刷新与巴黎二维模拟。 |
| `npc` | 仅恢复上述17个绘测文件 | 原 `tmp/map-survey-overnight-20261013/collections/complete_v3/figures_v1` 路径。 |
| `tutorial-source` | 城市、原生人物、已采用动作与模型依赖、完整145源码含私有曲线、当前音频／UI／装备、原生覆盖层 | 独立新目录 `tmp/Restored-Development-20261020/Tutorial/Project`，旁边保留准确源码清单；不混入旧 Editor DLL。 |
| `tutorial-game` | 已验收的教学1.0原有 ZIP | `tmp/Restored-Development-20261020/Game`，只下载和解压既有包。 |

选择所需参数，下面三条逐条执行，上一步成功后再运行下一步。尖括号替换为私下获取的信息：

```powershell
python Tools/Integration/restore_selected_development.py workbench download --host <私有地址> --user <私有账户> --port 22222 --identity <私钥路径> --known-hosts <已核验主机指纹文件>
python Tools/Integration/restore_selected_development.py workbench apply
python Tools/Integration/restore_selected_development.py workbench verify
```

恢复教学源码或既有试玩包时，将三条中的 `workbench` 换成 `tutorial-source` 或 `tutorial-game`。下载先进入 `tmp/Selected-Development-Restore/<参数>/objects`，验证大小、SHA256和压缩包成员后才放置文件。发现不同的已有文件、目录联接或路径越界会停止，不会覆盖改动；请保留冲突并使用新克隆。失败的部分下载留作诊断，重试前需移开。日志和凭据信息保持私有。

平台的 Python／JS 依赖另按 `Tools/AssetWorkbench/setup.ps1` 安装，这不是 UE 构建。用 `Tools/AssetWorkbench/run.ps1 -BindAddress 127.0.0.1` 启动本机模式并执行经过认证的 Refresh index；默认8765端口，遇占用自行选空闲端口。各成员生成自己的配置、索引数据库、会话与浏览器布局，不复制本机这些状态。此上下文包不包含历史私有预览／原生封面缓存及权利未确认的入库／研究原件；可选预览缺失仍保持原范围。允许共享的原生原件仍按既有 Catalog 清单恢复。

源码恢复后，需另行审查依赖并构建与145源码匹配的 UE5.8.2 Editor，才能进入编辑器。工具不编译、不 cook、不启动游戏，也不迁移个人存档。本机正式入口仍是 `Releases/Paris-Tutorial-1.0-20261017/PLAY_TUTORIAL.cmd`，原 UserDir 与存档不变。组员实际在第二台电脑恢复和运行仍待本人测试，不能由本机下载校验代替。

[English guide](SELECTED_DEVELOPMENT_RESTORE_20261020.md)。[实现计划](SFTP_RESTORE_STORAGE_IMPLEMENTATION_20261020.md)与[核验结果](SFTP_RESTORE_STORAGE_RESULT_20261020.md)。
