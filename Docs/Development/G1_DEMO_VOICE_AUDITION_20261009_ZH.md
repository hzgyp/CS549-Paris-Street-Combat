# G1 AI配音试听

2026年10月9日。你要求提供几款声音选择，视频除英文字幕外增加AI配音；尚未选定声音。
本项扩展已审查的第三稿脚本，不开始录屏、不改变玩法。
[英文原文](G1_DEMO_VOICE_AUDITION_20261009.md)。

## 已读案例、本次改变、检查与停止条件

已读AGENTS/HANDOFF、当前基线/音效选择器、第三稿与英文SRT、失败索引、MI014/MI015/MI016。
之前真实游戏原声要求保留：不能用后期Foley或诊断混音WAV代替游戏声音。
这次新授权增加的是独立轨道、明确标明的离线AI旁白，配音不代表玩法/AI/性能验收通过。

用同一段原创英文台词、同一标称语速及匹配响度生成四份试听。
采用本机Kokoro1.0 ONNX CPU和标准声音，不克隆真人、不使用付费账户/API。
依赖仅安装至tmp内本项独立运行目录，模型/音频不进入Git；不动游戏、OBS、UE资产/源码、
用户存档、旧录像或SFTP发布。

先核对模型/声音名称及来源、大小/哈希，再检查导入、模型加载及首段有效24kHz PCM。
下载身份/大小不符、导入/推理失败、无声/非有限输出、削波、编码/解码失败即停止并保留
实际记录。不偷偷改成收费服务；波形统计不代表听感真实，也不声称助手亲耳听过。
最终由你试听选音。

## 四个候选

| 编号 | 标准声音ID | 官方目录属性 |
|---|---|---|
| A | am_michael | 美式英语、男声 |
| B | bm_george | 英式英语、男声 |
| C | bf_emma | 英式英语、女声 |
| D | af_heart | 美式英语、女声 |

四段都朗读：

> Welcome to Paris Street Combat. Lead an Allied squad across the bridge and
> secure the German-held bridgehead. This demonstration shows movement,
> collision, navigation, and enemy behavior. Save after clearing the guards,
> or restart the mission if the player is killed.

这是声音试听，不是游戏捕获原声或最终完整配音。标称语速统一1.0、匹配响度，保留原始
24kHz PCM后输出MP3；不同声音自然时长可以不同。

来源：[模型及Apache2.0权重](https://huggingface.co/hexgrad/Kokoro-82M)、
[声音目录](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)、
[ONNX实现及MIT许可](https://github.com/thewh1teagle/kokoro-onnx)、
[维护者模型发布](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0)。
原始来源、依赖版本/许可和输入输出哈希保留在私有记录，标准声音名称不代表某位真人身份
或真人声音克隆授权。

## 最终旁白安排

选定后，按实际镜头写简短英文旁白，不机械朗读全部SRT，也不全程覆盖动作演示。
走/跑/起跳/落地、换弹/开火及死亡/恢复检查留出清楚的原声窗口。
旁白独立成轨，必要时仅在说话期间降低游戏音量，不删除或替换捕获到的声音事件；
明确说明AI配音，字幕与实际行为一致。本版本压力数字仍未测，不能用旁白宣称完成。

试听/结果：`Assets/LocalShared/Deliverables/Assignment3/VoiceAudition20261009`；
运行依赖/模型/日志：`tmp/g1-voice-audition-20261009`。
执行后记录实际结果，本次不制作全片配音、不录屏、不上传。

## 保留的导出解析失败

首次推理已生成Michael原始PCM，但FFmpeg响度JSON后还有进度总结，初版解析器因此
报JSONDecodeError: Extra data并停止；没有把这次当作MP3试听通过。
原始源码/日志保留在tmp/g1-voice-audition-20261009/failed_v1，原PCM/分析日志留在交付根目录。
修正只读取完整JSON值，仍保留后续日志；使用新的selected_v2输出身份，复用首段Michael
原始PCM，仅合成其余三音。台词、模型、声音、语速、响度目标及音频/编码检查不变，
不涉及游戏源码修改。

对交付MP3复查，Heart为−20.67LUFS，未通过额外0.6dB比较检查；保留selected_v2和响度
日志，这不是削波或合成失败。用新selected_v3做测得的音量校准：复用原始浮点PCM和
原归一化，仅作衰减至统一−21LUFS，不增益放大、不重新合成、不转码有损输入。
检查完整MP3解码、真实峰值无削波及−21±0.2dB，失败即停止。
首段Michael的PCM样本完全相同，但重写WAV容器哈希不同，不能说容器字节也相同。

## 实际交付

四段最终MP3已生成，路径为
`Assets/LocalShared/Deliverables/Assignment3/VoiceAudition20261009/selected_v3`。
A Michael18.496秒、B George17.578667秒、C Emma15.061333秒、D Heart16.704秒；台词相同、
标称语速1.0，最终实测响度为−20.99至−21.00LUFS。完整解码均退出0，真实峰值低于0dB。
AUDITION_RESULT.json记录原PCM、衰减、大小及最终哈希；模型/依赖/源码/导出日志与
此前失败记录保留。未声称听感通过，声音仍待你选择。
当前游戏53ab36d9…950aec哈希不变，没有启动游戏/OBS或录屏/发布。
第三稿现允许独立AI旁白，英文开场字幕已说明；选音并取得实际录像后再写完整旁白和混音。
