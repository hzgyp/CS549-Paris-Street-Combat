# Thumb surface envelope V5 / 拇指整表面接触

4 October2026. V4 is stopped/unselected: thumb root swing18.6904degrees puts the
selected pad point0.055cm above upper stock, but actual thumb/stock surfaces still
cross28 triangles in each recorded phase. Index skin/bones exact0 change, no new
severe edges; source unchanged. Read V4 plan/results, latest trigger result,
AN003/004/005/FP001 and rejected coarse finger result. V4 pictures actually show
thumb resting above stock, but underside edge penetrates. A point is not a pad.

Changed mechanism: retain mature Rifle_Idle thumb grip/three-joint scope, fixed
gun/index/wrist/left arm. Instead of fitting a chosen pad-centre triangle, solve
first outward contact of the WHOLE evaluated thumb envelope with the actual
local upper-stock surface. Use V4 contact orientation only to define a fixed
physical lift axis about thumb_01_r; no arbitrary pose/offset grid. One bounded
scalar geometric root solve in [V4angle,40degrees], nearest actual local stock
normals for envelope constraints, then actual triangle intersection verification.
No margin or root-angle limit changes to make failed numbers pass.0.05cm envelope
margin; report closest actual thumb/stock gap and selected-centre gap separately.
Nearest-normal sign is only a local solver proxy, not closed-solid containment.

Early gate: entire thumb/stock and other-gun crossing count0 in all eight samples,
closest distal surface within0.15cm of actual upper stock; unchanged index skin/
local matrices, gun/left/non-thumb bones; no new severe skin edges or visibly
collapsed/torn thumb base. Stop if envelope contact cannot be achieved at40degrees,
wrong-side solver/mixed-skin issue or postsolve crossing persists. No more rotation
samples/contact-margin tuning, no hand/wrist/source model/weights/index edits.
New fit_v2 evidence identity; preserve fit_v1 and do not rerun its point-fit.
No new motion/keyframes/native owner, formal adoption/NPC copy/release/commit/push.
Fresh diagnostic blend check and multi-view review, not Unreal runtime acceptance.

中文：V4实际失败，单指腹点约0.55mm间隙仍有28面穿入。V5换成真实整拇指蒙皮的
表面约束，用固定抬起轴求首次整表面接触，不继续试一批任意角度。40°上限／0.5mm
名义间隙不变；最终仍以真实三角交叉及多视角为准，不能把最近法线当封闭体证明。
选定中心点距离和真正最靠近表面距离分别记录，不把改指标写成V4通过。食指实际
网格位置必须严格保持，不能动枪／手掌／左手／模型／权重／源动作。V5失败即停。
