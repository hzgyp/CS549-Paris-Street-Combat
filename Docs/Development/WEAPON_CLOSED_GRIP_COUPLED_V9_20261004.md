# V9 coupled digit/gun contact / 手指之间与枪托同时约束

Latest status,4 October23:06 EDT: user-paused, stopped/unselected, no rerun.
See the pause addendum in `WEAPON_CLOSED_GRIP_RESULT_20261004.md` and `_ZH.md`.
用户暂停，以下为历史实施记录，不继续逐指求解。

4 October2026. Same user-authorized micro-adaptation, offline only. Read V6/V7/V8
records, failure index and AN003/004/005/FP001. V7/V8 pass sampled gun intersections
but final read-only review finds NEW middle/ring58 and ring/little141 nonadjacent
surface-intersection pairs; baseline0. They are NOT grasp passes/selected assets.
No source/native change. Source-family separating-plane probe has overlapping
projections, so a fixed halfspace is NOT justified and will not be used.

Changed mechanism: solve the already permitted eight joints TOGETHER. Constrain
evaluated skin/edge/face samples against closed stock AND neighboring digit
surfaces, with both digits' derivatives. Previous independent digit seating cannot
account for shared finite finger volume. Use only interior-phalanx samples whose
source-family signed clearance is positive; open root surfaces/shared seams are
not treated as solids. Exact triangle tests (exclude only shared physical seams)
must verify no NEW self-intersections, regardless of proxy success.

Same protected gun/index skin/three index rotations, middle_01, palm/wrist/left,
source mesh/weights/UV/rig/actions/camera/transactions. Existing D059 rotation
bounds30degree first/second,20degree distal unchanged. At most24 coupled trust-step
iterations, no angle/render grid, repeated solve variants or relaxed contact gates.
V8 is unsafe diagnostic initialization, not accepted baseline. Sources preserved.

Early acceptance:8 phases non-index gun crossings0; three-phase exact selected
digit-pair self-intersections no increase from baseline; index/other bones/skin
exact, no new severe edges. Then bottom/side/oblique/whole-arm volume/contact
review and fresh copied-scene read. Actual glare/low-poly limitations remain.
Stop on untrusted sign, bounded non-improvement, remaining actual self/gun
intersections, distorted digits or protection change. Retain failure unselected,
no silent use of a no-gun-crossing candidate with fingers embedded in each other.

New private identity`coupled_grip_v9` in the same workspace; no UE/NPC/B6/BT/BB,
formal map save, release/Catalog/package/commit/push. No source action creation.

中文：补查证明V7／V8手指互穿，不能采用。本轮不重跑逐指方案，改为八个允许的
关节一起小幅求解，枪托间隙与相邻手指体积同时约束。原动作的指间投影不是分离
平面，所以不强塞平面。只用原姿态签名可靠的内部指节取样，避开开放掌根／共享
接缝，最终仍按真实三角交叉与图验收。界限、食指、模型／权重／枪位／镜头不变。

Technical serialization correction only: first run reaches skin validation but
NumPy int64 pair counts cannot be serialized, so its exit0 is NOT completion.
Preserve copied source/last valid report; one new`coupled_grip_v9b` converts counts
to native int. No solver/rotation/gate parameters change or native authoring.
