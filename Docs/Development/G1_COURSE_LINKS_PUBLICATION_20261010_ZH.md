# G1 课程视频与可执行包链接发布

最新交付变更（10 October）：用户明确要求将已选定两页报告放入既有下载目录
并打包，再 Git commit/push。当前私有 `CS549-Assignment3-20261010.zip` 包含六个
文件，82,038 字节，SHA1171bcb6，成员大小/SHA、CRC、PDF 两页及50保护哈希通过。
原游戏/视频/访问配置/两下载脚本/原团队密钥不变，仅说明补充报告。报告
SHA6379243d 与已批准版本一致；之前不压缩和报告待制作快照被后续用户选择
取代。详见 [实施与检查](ASSIGNMENT3_DELIVERY_BUNDLE_20261010.md)。课程平台
上传和独立评阅者下载仍未完成；本次没有新的网络传输或服务器更改。

2026-10-10。用户明确要求将已批准视频发布到自己的YouTube，记录链接，并检查
课程文件分享服务是否支持约8GB；若不能，采用本地SFTP和独立访问密钥包。
本次不重写RP001拒绝的报告，不改游戏，不推送Git或公开原始商业素材/现有团队凭据。

## 已读案例与本次改变

已读HANDOFF/当前基线、视频04结果与清理记录、MI014–MI018及RP001、团队同步/
素材权益、现有audioV2发布结果。上传完整158.233秒视频04，SHA80481952，
英文字幕/A-Michael配音/实际声音/实时UE数据不改。当前正常试玩包为
Paris-G1-Audio-V2-20261009.zip，8,476,572,643字节、92成员，SHA7a8c225a；
普通Game53ab、正式42源与资产逻辑保留，不用诊断录制Game替代交付。
视频默认采用课程常用的Unlisted（有链接可观看），记录实际频道/链接/可见性和
处理状态。公开视频说明只含游戏内容和自动输入/配音/实时统计说明，不包含凭据。

## 早期检查与流程

确认当前已登录频道身份、完整成片大小/哈希及用户人工批准后上传。标题/英文说明
依据实际四pillar和G1/保存/死亡重开，不声称课程完成。按YouTube真实上传流程
填写内容和受众属性，确认最终处理/发布状态及外部观看页后记录链接。
课程文档提到网盘/itch.io，先验证官方上传说明；网页上传限额与butler能力分开。
包已含真实Windows EXE及全部依赖，校验现有ZIP/内部入口，不只提供单独EXE。
确认服务/账号及编译包评阅者权限后才交付相应渠道。

若采用SFTP，复用已发布不可变包；按下载需求准备独立、限定只读单包的访问方式。
不把现有三人共用账户密钥、密码或服务器私钥打进公开下载包，不修改原团队ACL。
访问文件上传到明确的课程交付渠道，与公开视频/公共Git分开。任何新凭据或网络
配置需要具体、可审查方案；先完成说明、范围和验证，再处理必要用户步骤。

## 停止条件

未知频道/上传重复、哈希漂移、上传/版权检查错误、安全提示、不可确认的新许可、
错误网站或不明确凭据上传位置即停止相关分支，保留证据。没有成功页/外部实际链接
不宣称发布完成。不改安全设置、绕过认证或向公开网站泄露团队访问凭据。
私有记录tmp/g1-course-links-publication-20261010，公开文档只记录非敏感链接与说明。

## 实际结果：2026-10-10 10:43 EDT

YouTube发布完成：[观看视频](https://youtu.be/zdnksqCxtzk)，频道yupu Guo，
频道ID UC5Q8fqD53TJ2WTcw4LMdR1A。标题为Paris Street Combat | CS549 Assignment 3
MVP | G1 Bridgehead。选择Unlisted，持有链接的人可观看；不是Private。
非儿童内容、无付费推广、Gaming类别、English语言，AI配音在说明及AI use项披露。
说明记录四pillar、G1/存档/真实死亡重开、正常速度、录制输入与实时统计范围。
Studio实际显示Video published和检查No issues found；观看页正确标题/频道、
Unlisted、2:38及可播放，设置菜单显示Auto(1080p HD)。没有下载或替换成片。
上传时最初扩展file chooser缺本地文件权限，普通Windows文件窗口成功完成，
未修改权限；先前要求用户开启扩展文件权限的问项不再需要执行。

本轮现有完整ZIP重新核对SHA7a8c225a/8,476,572,643字节；92成员，
内部普通Game53ab重新计算SHA通过，PLAY_G1_REVISION.cmd入口存在，解压总量
8,476,555,645字节。不是单独一个缺资产的EXE；解压全包后执行入口。

若用户所指网站为itch.io，它支持本包：[官方quick start](https://itch.io/docs/itch/integrating/quickstart.html)
说明网页2GB、butler30GB；[butler上传说明](https://itch.io/docs/butler/pushing.html)
明确按未压缩总量30GB限制，可直接输入现有ZIP。无需因8GB自动改走SFTP。
具体网站仍待用户确认；未登录/新建itch项目、安装butler或上传游戏包。

现有SFTP的audio V2不可变包继续可供原三人团队使用，路径仍为
/releases/paris-g1-playtest-20261009-audio-v2/Paris-G1-Audio-V2-20261009.zip。
本次不是新的远程SFTP读回或外网/导师下载测试。Assets/Sync/RIGHTS.md仅确认
三人商业素材私下共享，明确未授权external build rights；对课程评阅者或公众的
编译包许可问项仍待答复。没有新访问凭据、密钥包或对外发布。

实际证据保存在私有目录：YOUTUBE_PUBLISHED.png、YOUTUBE_WATCH.png、
PUBLICATION.json、PACKAGE_CHECK.json。当前selector和验收/交接入口已记录视频链接。
游戏/source/model/手指/枪械/资源/存档不变，报告仍RP001拒绝，本轮不提交/推送Git。

## 后续明确选择与实施修订：10 October2026

用户选择优先本地SFTP，确认编译游戏允许导师/助教私下评阅，指定密钥包仅准备
到本机、由用户上传课程平台。随后明确要求“跟我组员用同一个账户和密钥”，
不新增用户。因此前述独立单包只读账户计划停止，未执行创建/配置/ACL操作。
按新的明确范围封装既有cs549sftp账户的同一客户端私钥和固定服务器公钥，
不生成新密钥，不复制服务器私钥，不修改团队/服务权限或新增端口。

此账户仍具有团队共享资源的增删改能力；下载指南明确说明，不能将其标为只读
或单包隔离。评阅的编译包许可写入Assets/Sync/RIGHTS.md，商业源码公众分发
仍未授权。实际访问ZIP保存在ignored的Assets/LocalShared/Deliverables/
Assignment3；公开Git只保存非敏感路径/状态及权益说明，端点/客户端私钥不入Git。

已读失败记录和本次早期门槛延续上文。新的早期检查为：现有私钥与已有公钥
配对、固定host key的本机及公网端点SFTP认证/列表/下载成功。只请求ls/stat/read，
不进行团队写入测试；完整8.48GB包通过实际SFTP读回哈希，可流式核验避免额外
复制8GB。公网同机连接成功只证明本机到公网转发路径，不伪称独立外网电脑
验证或教授已下载。客户端Windows下载脚本固定主机公钥、使用同一密钥、断点
续传并验证ZIP SHA，解压后运行PLAY_G1_REVISION.cmd。

密钥漂移、host key不匹配、服务目录/包变化、端点无法认证或下载哈希不同则停止
相应交付并记录，不更改服务/防火墙/ACL绕过。最终本机密钥ZIP不含游戏或用户
存档/团队其他资源；它只是领取已存在SFTP试玩包的连接凭据和说明。

### 客户端预检的失败与修正

首次Windows PowerShell5.1的Set-Acl新FileSecurity触发SeSecurityPrivilege失败，
后续现有包分支通过但新下载分支暴露工具转义丢失反斜杠，及子进程Get-FileHash
自动加载不可用。三个失败脚本及真实log保存在私有证据根，不用一次parser通过
代替下载分支运行。最终采用只加载Access节的.NET文件DACL方法保护复制出的
密钥、char92/47明确转换路径、.NET流式SHA256避免cmdlet加载依赖。
不改原密钥/服务器权限。当前版本在普通Windows PowerShell5.1下，真实SFTP
127字节partial续传到完整发布README、中文本机路径、哈希核对及校验后rename
通过；已有错误终稿文件被拒绝并保持原字节。这个小文件测试不是8GB游戏传输
证明，完整游戏另由真实公网SFTP流式读回记录核验。

## SFTP 本机交付结果，10 October 2026

最终交付包：`Assets/LocalShared/Deliverables/Assignment3/CS549-G1-SFTP-Access-20261010.zip`，6,964 字节，10 个文件。
ZIP SHA256：`a7407f2ea075232251009e11e832cbec1b9ac92f1021146177507c6743c4c37c`。
原组员私钥逐字节复用，未新增用户/密钥，未修改服务器/原密钥/服务端权限；
仅保护本机交付 ZIP 与解压出的客户端密钥副本。共享账号仍有团队资源 CRUD
权限，不标为只读或单包隔离。ZIP、端点和客户端密钥留在 Git ignored 私有目录。

既有 SFTP 发布目录与游戏包不改动。固定服务器公钥的 loopback 与公网转发
认证通过；真实公网 SFTP 流式读回完整 8,476,572,643 字节，耗时 653.08 秒，
SHA256 为 `7a8c225ad66ea673e20d0259324c3b5fef25be25bb66fcdddb5344533bd26d7d`，
与已发布游戏一致。测试范围是本机到公网转发路径，不能当作独立外网电脑或
导师已下载的证据。Windows PowerShell 5.1 最终下载脚本的真实小文件续传、
中文路径、SHA 校验后更名、错误已有文件保护，以及真实 8GB 已有包哈希分支
均通过；不把小文件续传测试写成脚本全量下载 8GB。ZIP 压缩完整性、10 文件
内容对照、原密钥/公钥/known_hosts 保护哈希和脚本最终哈希均复核通过。

用户将本机小 ZIP 上传课程平台私密附件；本次不代为提交课程平台。评阅者
完整解压连接包，运行 `DOWNLOAD_GAME.cmd`，待 8.48GB 游戏下载校验通过，
再完整解压游戏并运行 `PLAY_G1_REVISION.cmd`。建议至少 18GB 可用空间；
本机需保持开机联网，公网地址变化时需更新连接包。用户课程附件上传与独立
评阅者下载尚未验证，不能据此宣称课程已提交/通过。

YouTube 已发布并记录： https://youtu.be/zdnksqCxtzk 。当前正式 audio V2 的
模型/动作/手指/枪械/弹药/HUD/存档及源代码、游戏 EXE 不变。Assignment3 报告
仍是 REJECTED/RP001，不在此次连接交付中改写或标为通过。未 Git commit/push。
私有结果：`tmp/g1-course-links-publication-20261010/ACCESS_KIT_RESULT_PRIVATE.json`、
`SFTP_CHECK.json`、`CLIENT_CHECK.json`；端点不进入公开文档。

## 用户发布链接更正的检查与实施范围，10 October 2026

用户提供新链接 https://youtu.be/SktbFHNYP54 并请求检查。本次读取 HANDOFF、
当前发布记录、MI018（实际性能面板可读性）及 RP001（报告重点不能被替代）。
仅核对新公开视频并更正当前提交链接、交接/验收记录与本机连接包中的视频地址；
不重新录制，不修改游戏或报告，不删除旧 YouTube 发布，旧链接保留为历史记录。

早期验收：观看页面标题/频道、实际播放时长与高清质量，Studio 的上传文件名、
公开可见性及说明与已批准的 video04 一致。当前已见标题 Paris Street Combat |
CS549 Assignment 3 | MVP Demo，频道 yupu Guo，观看页 2:38、Auto(1080p HD)，
Studio 文件名 Paris_G1_MVP_Draft_04_Live_Performance.mp4，Public、HD complete。
Studio 侧栏四舍五入显示 2:39，观看播放器显示 2:38，均符合 2–3 分钟要求；
不将平台转码视频冒充可取得原始文件 SHA 的下载核验。

停止条件：访问/播放失败、关键内容不符，或出现密钥/端点/下载脚本漂移。
连接 ZIP 更新前保存其私有旧副本，只替换视频链接相关字段，检查 10 个成员、
ZIP 完整性、其他成员原字节及原密钥一致。无需重复 8GB SFTP 传输，既有网络/
断点续传验证仍归属于此前相同服务器、游戏与下载脚本。

### 新链接检查与连接包更新结果

新链接 https://youtu.be/SktbFHNYP54 已确认为 Public、1080p HD 完成，观看页 2:38。
画面抽查见实时性能面板/完整小地图、玩家血量 0/PLAYER LOST/F6 重开等待，
以及 Fresh Ready 恢复到 100 血量、2+16 弹药、两名盟军/三名守卫。英文内嵌
字幕保留，自动 YouTube CC 开启时有重复叠字；观看可关闭 CC。

当前提交链接改为用户提供的新链接。旧 zdnksqCxtzk 只作为历史发布，未删除。
本机连接 ZIP 同名更新为 6,964 字节，SHA256：`e8d9bafcb2f4c8054b0ad5cacc693af6b616cb393a71fb2226e149b91b3c2921`。
原 6,964 字节 ZIP 留在私有证据目录作历史副本。只替换 CONNECTION.json/
README.md 的视频地址；其余 8 文件（含相同密钥、SSH 配置和下载脚本）原字节
不变，ZIP 10 成员逐字节对照及压缩完整性通过。游戏包/服务器不变，未再做
8GB 网络传输或声学复验，未重新录制/发布/删视频，未 Git commit/push。
新检查私有记录：USER_VIDEO_LINK_CHECK.json；课程平台附件仍由用户上传。

## 连接目录精简实施，10 October 2026

用户更正交付方式：先仅使用目录，不要新增压缩包；目录只保留直接有用的文件。
此前“上传连接 ZIP”的建议被本条更正。本次已读 HANDOFF、失败索引、本记录
客户端预检失败（ACL/路径转义/hash cmdlet）及私有 URL 换行预检记录。

改为 5 文件：下载入口、下载脚本、连接配置、原组员私钥、合并的中英文说明。
客户端 `.pub` 不参与此下载，去掉独立文件；`known_hosts` 原用于固定服务器
身份，其服务器公钥合并到连接配置，脚本运行时在临时目录生成校验/SSH 配置
并清理。保留 StrictHostKeyChecking，不把精简解释为取消服务器身份确认。
SHA 校验值合并到连接配置，去掉重复 SHA 文件和第二份说明。仅更改客户端
组织方式，现有账户、原密钥、SFTP 服务、8GB 游戏及视频不变。

早期验收：5 文件闭合，原私钥一致；普通 Windows PowerShell 5.1 实际小文件
断点续传/哈希校验通过，故意错误服务器公钥时连接被拒绝，临时文件已清理。
停止条件：原密钥或端点漂移、误改服务端、已验证包被改写、校验无法工作。
旧 10 文件目录与既有连接 ZIP 移到私有历史目录，不新增打包，不重复 8GB 传输。

### 目录精简实际结果

五文件交付目录已完成。原组员私钥及原始保护哈希一致；新下载脚本在普通
Windows PowerShell 5.1 下真实续传发布 README（已有 127 字节 partial），中文/
空格路径、SHA 校验及更名通过。故意使用错误服务器公钥的独立试验被 OpenSSH
拒绝，partial 原字节保留；成功/失败两条路径都清理了临时 SSH 文件。仅对这个
小文件做本轮实际传输，不重复 8GB 验证。当前端点、账户、原私钥、游戏本体和
视频链接不变。5 个交付文件闭合，旧 ZIP 移出交付目录，未新建压缩包。
私有结果：ACCESS_DIRECTORY_RESULT_PRIVATE.json、ACCESS_DIRECTORY_CLIENT_CHECK.json。
此前 ZIP 交付建议及客户端状态是历史；当前只交付目录。
