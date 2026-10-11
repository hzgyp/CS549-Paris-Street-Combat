# Assignment 1、2 最终 PDF 的 Git 发布

2026-10-11。用户明确要求将 Assignment 1、2 的最终作业 PDF 同步到 Git，
方便组员直接查看，并要求排除另一个窗口的开发改动。

## 已读案例与本次改变

已读 AGENTS、HANDOFF、Failures/README 与 RP001 报告重点偏移分析、
Proposal README/插图来源、Assignment 2 要求核对、Assignment 3 PDF 发布
记录、团队同步规则及课程 PDF 守卫。RP001 提醒不能把发布或排版检查变成
报告内容重写；本次不重新生成报告，也不修改提案、模型或正式玩法。

直接跟踪现有最终文件，不搬迁、不另存副本，保留已有文档相对链接：

- [Assignment 1 最终 PDF](../Proposal/CS549_Assignment1_Proposal.pdf)：
  两页，651,899 字节，SHA-256
  `5d426fb9f6247765d63ba833a2b5a5da7f65fceb26c84c413093ee0a0e97c22a`。
- [Assignment 2 最终 PDF](../Proposal/CS549_Assignment2_Proposal.pdf)：
  两页，347,301 字节，SHA-256
  `c6a89f1eff2bfef4d150421e90436492fc83e0231f2285aa9ac0b53b23919d69`。

登记精确路径、公开内容检查和原始字节哈希，添加精确 ignore/attributes 规则。
课程报告守卫仅扩展允许的文档位置到 `Docs/Proposal/`，仍逐文件核对批准表，
不全局放开 PDF。Assignment 3 原有批准路径与字节保持不变。

旧 `project-document-assets` SFTP 清单也记录了这两份报告，且大小/哈希与本次
完全相同。保留原清单、Catalog 和服务器存量，不篡改历史、不重新上传或删除；
当前作业查看渠道改为 Git。其他未批准文档/素材仍按原私有清单恢复。

## 早期验收与停止条件

核对两份报告为当前巴黎/四支柱版本，而非 22 September 历史合并稿。
检查完整文本、元数据、XMP、链接和嵌入附件，复看四页渲染；不公开私密邮件、
连接凭据或供应商原始图库图片。两份报告内为已注明来源的自编流程图和新生成
ImageGen 概念图；原始供应商 JPEG 不随本次发布。

暂存 PDF 必须与上述字节哈希精确相同；原始 DOCX、旧 PDF、商用素材、私有下载
ZIP/配置/密钥仍忽略。课程 PDF/文档图回归及原 pre-commit/pre-push 守卫必须通过。
只逐路径暂存本任务内容，AGENTS/ignore/attributes 只暂存本任务的局部增量；
不提交其他窗口的地图、装备、基线、图像批准表或工具改动。

若版本不符、公开内容有问题、哈希变化、暂存混入未知改动、守卫失败或远端
发生分歧，则停止修正。不 force-add、不绕过 hook、不强推，不删除历史文件。
正常推送后核对远端 main 与两份公开 PDF 字节。Git 分享不代表 Canvas 提交。

## 状态

两份最终报告的四页已复看，页面、概念图和流程图可读，无截断或重叠；报告内容
与原字节不变。完整文本、常规/XMP 元数据、官方 URI 链接检查通过，无加密、
嵌入附件、启动或 JavaScript 动作。元数据中的 `26.8.0.0` 是 LibreOffice
生成器版本，不是连接端点。Poppler 曾输出 Symbol/ArialUnicode 字体提示；
实际四页渲染未发现异常字形，因此不重新生成或改写已确认的 PDF。

14 项课程 PDF 回归与原有 14 项文档图回归共 28 项通过。两份精确最终 PDF
路径可跟踪，旧合并稿/DOCX/私密邮件/下载 ZIP 仍忽略；PDF 的 text 属性关闭、
filter 未设置，不使用 LFS。新批准表保留 Assignment 3 的原始批准哈希。

仅按上述任务范围执行正常提交/推送；以本轮实际 Git 提交和远端 main/PDF
读回核对作为发布证据。无新游戏验收、SFTP 改动或 Canvas 提交。
