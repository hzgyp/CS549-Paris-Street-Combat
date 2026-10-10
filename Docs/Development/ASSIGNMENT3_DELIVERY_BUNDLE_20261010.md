# Assignment 3 报告与下载目录打包

2026-10-10。用户明确要求把当前 Paris Street Combat Assignment3 报告放入之前的
下载脚本目录，然后打包，最后 Git commit/push。本条取代此前“仅目录、不压缩”
的交付偏好；仍使用现有组员账号/密钥，课程平台私密附件由用户上传。

## 已读案例、本次改变

已读 AGENTS、HANDOFF、当前开发基线 JSON/Markdown、Failures/README、RP001
报告重点偏移分析/恢复说明、交付目录清理记录与课程连接发布记录。
RP001 提醒报告要保留四支柱与 AI 效用的结合；本次不改已批准报告内容。
清理记录区分历史证据与交付物；本包只含当前下载目录和两页报告，不加入视频、
历史档案或 8GB 游戏。已有游戏 SFTP 校验不被本次本机 ZIP 检查冒充为新网络测试。

从交付根目录移动报告到 `SFTPAccess_20261010`，保留原 `output/pdf` 报告。
说明文件补充报告文件名；下载脚本、连接配置和原密钥保持精确字节。
新 ZIP 放在同一 Assignment3 交付根目录，保留一个 `SFTPAccess_20261010/`
顶层目录。PDF、访问文件和 ZIP 均仅在 Git ignored 的私有本机目录中。
公开 Git 仅提交匹配的源码、工具、文档、失败案例与非敏感验证元数据。

## 早期验收和停止条件

先确认报告为 81,345 字节、两页，SHA256 为
`6379243d8e003906362972533927f9f503971513836fb0556f191d4679cd8f6f`，
交付目录五个访问文件齐全，目的文件/ZIP 尚不存在。移动目标的解析绝对路径
必须位于指定交付根目录；检查链接/重解析点。冻结视频、Game、源清单/42源文件
与访问文件哈希，移动后检查未授权内容精确不变。

ZIP 必须恰有六个文件，CRC、全部成员大小/SHA、原 PDF 哈希/页数均通过；
不存在 `.pub`、独立 `known_hosts`、其他凭据或历史材料。遇到路径越界、链接、
原文件变化、哈希/成员检查失败就停止。Git 提交前检查源码语法、staged diff、
本地资产及仓库 pre-commit/pre-push 守卫；不绕过守卫，不提交私有二进制/密钥。
正常推送 `main` 后读取远端 HEAD 核对，不强推、不改服务端或游戏逻辑。

## 状态

本机打包已完成。报告从交付根目录移动到下载目录，仍为两页、81,345 字节，
与 `output/pdf` 原件和选定 SHA 精确一致。说明补充报告位置；原连接配置、
两项下载脚本、团队私钥精确不变，无 `.pub` 或独立 `known_hosts`。

ZIP：`Assets/LocalShared/Deliverables/Assignment3/CS549-Assignment3-20261010.zip`，
82,038 字节，恰有六个 `SFTPAccess_20261010/` 文件成员。SHA256：
`1171bcb68dc21cd4beb668e7b19ed8ba074ac69691ae77fdd6830c6e7cbc9ca9`。
全部成员大小/SHA 读回、CRC、ZIP 内 PDF 两页检查通过；50 个未授权改变的保护
文件精确匹配（原报告、当前视频、Game、源清单/42源、四个访问文件）。六个
目录文件及 ZIP 的 Git ignore 检查通过。私有冻结/结果位于
`tmp/assignment3-delivery-bundle-20261010/BEFORE.json`、`RESULT.json`。

Git 发布包括本次及此前录制/报告/清理的相关源码、工具、文档与失败分析。
34 个 Python/JSON 文件语法检查、8 个 PowerShell 脚本静态解析通过；原端点与
密钥字节不在 84 个暂存源码/文档文件中。`check_asset_storage.py --local --git`
检查 13 个 active manifests、17,682 文件（约37.69 GiB）通过；`--git --staged`
及 staged diff 检查通过，当前 ZIP 与暂存 selector 一致。远端 main 仍与父提交
656db9b14b20 一致。正常 commit/push 仍运行原 pre-commit/pre-push 守卫；实际
远端 HEAD 核对决定发布结果，精确提交/远端 SHA 写入本机 `PUBLICATION.json`。
本机打包不代表新网络传输、游戏测试或课程提交；课程平台上传与评阅者独立
下载仍待完成。
