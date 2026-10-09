# MI009 - Actor tick 后尚无有效视口读取纹理

2026年10月8日。[英文原稿](FAILURE_ANALYSIS.md)。demo_capture_v2／instrument_v14在
首次采集后12秒门槛停止：仅16帧，总20.807秒，正常退出0，但有D3D12RenderTarget.cpp
599行InRHITexture严格ensure。首张1920×1080PNG全部RGBA极值均为(0,0)，尺寸及
非空缓冲并不证明有可用画面。未开始任务移动，不计录像、性能或完整循环通过。

失败读取在OnWorldPostActorTick，区别于已经成功的Shot SHOWUI流程。安装UE
GameViewportClient.cpp:2369–2580显示ProcessScreenShots用Slate::TakeScreenshot
取得带UI图片，成功后设置alpha255、广播OnScreenshotCaptured并重置请求。本任务
已实际检查的1920×1080 SHOWUI截图证明另一种“请求／完成”机制可用，不能证明
tick内直接读取有效。

停止保留此直接读取方法，不重复尝试空纹理、不降低采集准入或裁掉错误；另立仅采集
完成回调计划。V13任务实现、有限功能及性能结论不变，正式资产／源码／Catalog未写。
MI009 MANIFEST记录关闭后的失败录制／构建私下归档与选定哈希。
