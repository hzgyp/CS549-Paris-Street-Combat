# M1 / current V12 — human comparison

2026-10-04. User requests a fresh matched comparison for their own visual review, not refinement. Read HANDOFF, Failures index and GP004/009, prior texture comparison and V12 result. Blender modeling skill used only for inspection/rendering; no new model/export/production gates.

Use existing repaired portable M1 with its own materials, and actual V12 GLB SHA862baf5ab6afa6f977e373d4710fce1e3bf6964e51e7e6483424f15bc9424193. Reuse prior comparison cameras/metre scale/+X muzzle/bounds center, fixed studio lights/AgX Medium High Contrast/exposure0/gamma1/Cycles40. Deliver whole/receiver/stock six PNGs, inspection scenes and labeled three-row side-by-side sheet (leftM1/rightV12). No asset/material/UV changes, no resize-to-equal-length, no crop/retouch, no original saves or original-library load. This is Blender portable appearance, not native UE shader parity.

First check actual correct variant, textures/axis/scale and legible views; if missing/misframed stop or make only one presentation correction, never repair models. Preserve occupied outputs. Stop after six images and sheet inspected; user supplies aesthetic verdict. Source hashes checked before/after, private new comparison identity `20261004-texture-comparison/m1_v12_v1` and `m1_v12_presentation_v1`. No cloud/UE/game/SFTP/Catalog/commit/push or silent acceptance.

## Actual outcome / 实际结果

Blender5.2.2LTS fresh job exit0. All six PNGs and labeled sheet actually inspected: correct M1/V12, axis/scale and visible textures pass the presentation check; no correction applied. Five input hashes (M1 scene, its three source PNGs, V12 GLB) unchanged. Only Material/World.use_nodes future deprecation warnings; no asset export or source save. All task jobs ended. No aesthetic verdict or user acceptance inferred; this turn stops for the requested human comparison. Same renderer/light/camera/exposure and real metre scale; M1 portable shading is not exact native UE equivalence. No game/cloud/sharing/commit/push change.

中文：左盟军M1，右最新德军V12；从上到下整枪、机匣、木托。两把枪按实际米制尺寸、相同灯光/曝光/相机渲染，不把枪拉伸成一样长，也没有对图修饰。六原图和拼图已查看，只确认展示正确，外观优劣由用户判断。原文件哈希不变，未修改模型。

[对比大图](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-texture-comparison/m1_v12_presentation_v1/m1_vs_v12.png)

[六图/输入哈希记录](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-texture-comparison/m1_v12_v1/comparison.json)；[渲染代码](D:/0.Rutgers/CS549/Project-New/Tools/AssetValidation/blender_rifle_texture_compare.py)及[拼图代码](D:/0.Rutgers/CS549/Project-New/Tools/AssetValidation/compose_rifle_texture_comparison.py)，新可选参数保留旧V11默认行为。

[盟军独立检查场景](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-texture-comparison/m1_v12_v1/allied_m1_inspection.blend)；[德军独立检查场景](D:/0.Rutgers/CS549/Project-New/Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-texture-comparison/m1_v12_v1/german_v12_inspection.blend)。仅展示副本，不是新模型或生产选择；PNG/blend/report均保持ignored LocalWorking。
