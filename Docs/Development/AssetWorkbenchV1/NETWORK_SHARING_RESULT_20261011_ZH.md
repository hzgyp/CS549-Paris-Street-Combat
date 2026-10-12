# 资产平台网络共享结果 — 2026-10-11

本机服务已重启并实际监听`0.0.0.0:8766`，本机配置持久化为`{"port":8766,"host":"0.0.0.0"}`。主局域网地址为`http://192.168.1.75:8766`，原启动器可复用当前共享服务。共享访问需使用含凭证的链接，保存在私有`Assets/LocalWorking/AssetWorkbench/runtime/share-link.txt`，首行为主接口；服务重启后使用重新生成的链接。凭证未写入日志或本说明。

允许访问地址限定为启动时发现的实际IPv4地址、本机名称和localhost。API Origin需与当前请求的scheme/Host一致；会话、CSRF、CSP及注册文件读取边界均保留。仅修改socket监听不足以共享，原先固定127.0.0.1的Host/Origin校验已同步调整。

Windows管理员确认完成，已创建并读回`ParisAssetWorkbench-TCP-8766`规则：入站Allow、TCP8766、LocalSubnet、Private/Domain，以及实际服务Python程序。未关闭防火墙或开放其他端口。规则/结果记录位于私有`runtime/firewall-result.json`。

后端44项通过，包含局域网认证、无凭证拒绝、未知Host、跨源和缺失CSRF拒绝，以及合法刷新成功；前端构建通过。两个Chrome检查通过：同一台机器经实际局域网IP登录、显示烟雾弹3D和英文静态模型说明；原平台中英刷新及资料索引同步正常。TCP监听地址通过Get-NetTCPConnection确认；启动器共享模式复用已实测。

此处验证的是本机经局域网IP访问，没有冒称第二台电脑、外部路由或公网入口已验收。虚拟网卡链接也写入共享文件，主接口排序在前；其他机器应使用实际可连通的主局域网地址。

源码为`app/network.py`、`app/cli.py`、`app/main.py`、`run.ps1`及`enable-sharing-firewall.ps1`。中英README已同步；静态资产、模型、游戏、Catalog和当前选择器未改写，没有Git/SFTP或公网发布。
