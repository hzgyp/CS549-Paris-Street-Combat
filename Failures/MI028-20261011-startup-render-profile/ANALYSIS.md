# MI028：启动首帧先使用了默认画质

v15 `smoke_v15` 在 frame2/完整Ready之前出现 D3D12 DEVICE_HUNG，exit3。保留原启动收据、log和GPU dump，不将它冒称烟雾机制失败或“显存不足”：本帧LocalUsed4875MB、Budget9285MB，不能仅凭这些值解释GPU挂起。

有具体配置问题：命令行ExecCmds要求质量2，但初始Scalability日志与GPU breadcrumbs的TSR仍显示AntiAliasingQuality=3。设备早期渲染先使用默认等级；ExecCmds执行得更晚。原Renderer和设备仍为D3D12/RTX3080。

下一步是不同的启动配置验证，而非盲目重跑：使用引擎 DeviceProfileManager.cpp 737–775 的 DPCVars 提前设置同一组已选质量2、100%分辨率、1536MB池、无VSync。保持D3D12、不降低既定质量、不修改GPU驱动/系统安全设置/原资产。新identity `v15_early` 必须从日志确认早期值和真实Ready后再验机制，保存旧失败。此修正能排除错误首帧设置，不能单凭随后成功宣称GPU原因已根治。

早期门槛：启动质量2在设备配置阶段生效、完整Ready、浓烟和实际避险。若同一修正配置仍挂起，停止本配置并保留记录；不循环再启动、更换RHI或删旧证据。
