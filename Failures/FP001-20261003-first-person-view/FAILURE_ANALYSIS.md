# FP001：第一人称强行入镜与前臂裁切

日期：2026-10-03。集成人：yg745。状态：用户明确否决；归档迁移是否完成以 `MANIFEST.json` / `VERIFICATION.json` 为准。

## 用户目标与实际结果

原目标是修复手臂出画面和运动遮挡，保留现有模型、手指及已验证枪械逻辑。用户看到修复后评价：“非常怪，视觉上感觉就是把枪顶在前胸这么处理。”随后选择《使命召唤：二战》的 M1 Garand 普通持枪作为基本参照，要求从 V3 重新做第一人称呈现。

本候选确实消除了检查画面中的大型自身遮挡，保留了模型/源动作/手指与枪械函数，16 项/66 断言也通过；但是普通持枪不自然，运动时前臂出现裁切端面。**整体视觉验收失败，功能局部成功不能覆盖这一结论。**

## 有证据支持的失败原因

1. **验收目标不完整。** 实现前没有确定正常持枪参考构图，把双手/前臂进入屏幕当成重要成果，未充分检查枪托、肩肘腕轮廓和中央视野。普通第一人称不要求双臂完整显示。
2. **整体搬位保留了不合适的轮廓关系。** Ready 右握点固定在相机局部 `(46,8,-13)` cm，并将原整套姿态刚性搬位/旋转。它保留了原接触关系，却使枪托显著伸向下方中央、右前臂横占画面。截图支持用户的胸前托枪观感；没有测量证明真实枪托-胸部接触。
3. **用裁切处理了表面，没有解决构图。** 半径 9 cm、肘到指端的胶囊保留前臂与手，移动时边界暴露，造成断臂般的端面。身体隐藏可以需要，但边界必须在全部目标动作中自然隐藏于画外，不能将缺口当成可接受限制。
4. **普通持枪与 ADS 视觉目标混在一起。** 普通 Ready 枪趋近中央，却没有完整照门/准星视图。应先验收普通持枪；增加 ADS 需要独立范围和过渡设计。
5. **原泛用动作的能力缺口没有解决。** 保留源动作不代表其换弹动作具备 M1 专用接触和第一人称可读性。该缺口应提前显式约束，而不是从正确弹药事件推断动画正确。

## 调试绕路及证据局限

- 早期跨动作阶段的截图不能做同帧对照；有效原遮挡定位是冻结相位后的 `diagnosis_v6`。`view_live_v6/*_viewport.png` 用于阶段画面；延迟 `_full.png` 不能证明同帧。
- 怀疑布料并关闭它没有解决问题；审计显示该网格无布料资产，不能把原问题解释为布料爆炸。
- 材质原始字段显示 Masked，但有效 `GetBlendMode()` 曾为 Opaque；只有实例显式覆盖后遮罩生效。检查实际有效状态，而非只看字段。
- `near_v1/v2` 的异常退出及其他退出失败仍然保留；没有确证根因时不能写成已解释。
- 新可视枪被赋给 `WeaponAppearance`，原枪械函数读取其变换做枪管/枪口阻挡。函数未改不等于空间输入没改；显示接口必须清楚，近墙测试不可省略。

## 已获得且可保留的经验

同帧遮挡隔离、原资源及手指局部变换校验、CopyPose 的标准节点方式、源网格/显示/枪的更新依赖、仅拥有者可见的独立表示、战斗及生命周期测试、近墙阻挡测试。这些是可审查复用的机制，不是重新选用失败画面的理由。

## 下一次必须不同

- 先读需求、此案例和 V4 关联案例，并在新实施文档写出改变的假设。
- 以 COD WWII 普通持枪的实际画面作参照：枪后部偏右下，枪托后端和显示边界在画外，支撑臂从边缘自然进入，中心保留给场景。
- 先做静止构图和接触检查，再扩展动态；不要先完成整套补丁再等最后一轮才看画面。
- 原模型、手指局部姿态、源动画、受保护相机和枪械事务继续保留。若这些约束下不能形成目标构图，明确实际限制，再设计有限的上肢显示适配或采用兼容现有内容；禁止无限调偏移、重新造详细人物或复活失败手指层。
- 新版本使用新路径；归档保留原状。任何旧测试通过只覆盖旧测试对象，新版本必须重新验收。

## 归档导航

`Docs/` 保存六份原始交接/实施/结果文档；`Tools/` 保存独有工具；`Metadata/` 保存原库存；`Changes/Before/` 保存共用源码原快照，撤回差异另存。原生资产和完整证据在 MANIFEST 所列私有目录。`MANIFEST.json` 的 original_path → archive_path 也用于解析保留文档中的历史路径；不篡改旧证据伪装为新路径/新测试。

## English review

The user rejected the whole visual result despite passing bounded gameplay regressions. Main supported causes: framing was judged by visibility rather than a reference holding composition; rigidly moving the full source pose preserved an unsuitable silhouette; forearm capsule masking exposed cut boundaries; ordinary holding was not separated clearly from sighted aiming; generic reload source capability remained limited. The exact internal implementation of COD WWII is not inferred. Retain useful diagnosis/test infrastructure, but start the next presentation version on saved V3 with an early visual gate and unchanged protected content. Archived scripts are historical evidence and must not be run from their relocated paths.
