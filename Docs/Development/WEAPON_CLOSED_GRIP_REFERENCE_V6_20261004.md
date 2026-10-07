# Reference-led closed right-hand grip V6

4 October2026. Human correction supersedes thumb-only visual target: grasp means
thumb/web above the stock wrist PLUS middle/ring/little fingers wrapping below,
not isolated tip contact. Keep user-approved V3 index/gun calibration; V4/V5 thumb
results are retained unselected diagnostics, not accepted closed-grip baselines.

Read HANDOFF/Git, failure index, AN003/004/005/FP001, rejected coarse left-finger
result and V2/V3 contact results. Blender character workflow applies source-skin,
multi-view and deformation checks, not from-scratch hand modeling/new animations.

## Actual visual references inspected

1. [DVIDS,2013 Quantico M1 photograph](https://www.dvidshub.net/image/979778/52nd-annual-interservice-rifle-championship),
   official Marine Corps image, photo979778. Opened page and actual1000px image in
   browser. [Observed image](https://d2cto119c3bgok.cloudfront.net/thumbs/photos/1307/979778/1000w_q95.jpg).
   Clear whole rifle/standing side view: firing-hand web/thumb above rear wrist,
   fingers curl around below rather than a separate closed fist floating beneath.
   Far-side digits partly hidden; no exact pressure/joint angles inferred.
2. [DVIDS,2024 Hohenfels](https://www.dvidshub.net/image/8584839/european-best-sniper-team-competition),
   U.S. Army Spc.Andrew Clark photo8584839. Actual page screenshot inspected:
   shooter reacts after firing, right hand around stock wrist; thumb lies above/
   beside grip. Modern posture is shape/contact analogy, not1944 unit/history proof.
   Observed image URL: https://d1ldvf68ux039x.cloudfront.net/thumbs/photos/2408/8584839/1000w_q95.jpg.
3. [UNT /12th Armored Division Memorial Museum,1943–45](https://texashistory.unt.edu/ark:/67531/metapth436643/),
   accessionTADM_1997-108-262. Actual high-resolution image opened in browser:
   https://texashistory.unt.edu/ark:/67531/metapth436643/m1/1/high_res/.
   Whole crouched rifle outline/shoulder relationship visible; firing hand is
   largely obscured, so NOT evidence for hidden three-finger exact geometry.

No reference images downloaded/committed or used as textures. DVIDS labels public
domain with restrictions; other reuse rights not assumed. Store source links and
observations only. Search thumbnails/descriptions alone were not called inspection.

## New bounded contract

- First inspect existing D059/Rifle_Idle middle/ring/pinky local poses with fixed
  accepted index and rifle; verify no shared weights move the index. Prefer mature
  existing closed-grip rotations and bounded display adaptation, no new actions.
- If needed, adapt only thumb/middle/ring/pinky local joint ROTATIONS in copied
  evaluation, explicitly authorized by this whole-grip correction. Preserve local
  translations/scales/bone lengths/weights/source clips/mesh/rig/UV, palm/wrist/left
  hand/gun/camera/transactions and accepted index matrices AND evaluated skin.
- Judge coherent enclosure of the stock wrist: thumb/web above, three fingers
  wrapping below/around with distinct pads and believable knuckles. Single nearest
  point, zero crossing count or a fist-shaped silhouette alone cannot pass.
  Compare right/left/top/BOTTOM/oblique and whole weapon/arms with source images.
- Use new WeaponClosedGripV6 probe/fit identities; keep thumb-only and all previous
  diagnostics. Early stop on index movement, impossible enclosure under fixed
  palm/gun, new collapsed/torn finger skin or visible penetration. No offset grid,
  whole-hand move, relaxed thresholds, rejected twelve-left-finger curl revival,
  source animation creation or detailed hand production. Report actual limits.
- Offline initial scope, no UE slot/native selection/NPC copying/release/Catalog/
  package/commit/push. Further game binding needs serialized ownership/runtime plan.

中文：本轮明确纠正的是完整包握，不是继续抬拇指。照片看见上侧虎口／拇指和下侧
包绕关系，隐藏指节不冒充实测。先检查成熟姿态；有界适配仅右拇指、中指、无名指、
小指局部旋转，食指骨与皮肤严格锁定。必须看底面与整手关系，不用几个接触点的
距离代表握紧。不动枪位／掌腕／权重／源动作／镜头，不选正式地图。

## Probe and bounded fit decision

Actual probe finds four index-mask vertices also weighted to middle_01_r. Freeze
that joint as well; adapt only middle_02/03_r and ring/pinky_01/02/03_r. Stop if
any remaining joint influences accepted index skin. Existing D059 wrap is closer
than Rifle_Idle: retain that mature three-finger family, not three newly invented
poses. V5 thumb is only an unselected upper-contact starting hypothesis.

One copied evaluation fit uses two broad existing pad patches per finger (middle
and distal phalanges), actual stock surface and whole-digit near-surface clearance.
No isolated tip is the acceptance target. Finite local least-squares correction,
maximum18 iterations per digit,30degree local joint change /20degree distal limit,
no pose/offset grid or repeated fit versions on failure. Preserve bone lengths,
translations/scales and existing curl family. True triangle crossings, index
invariance and bottom/oblique visual enclosure decide whether to retain a preview.
Numeric fit alone never certifies grasp or game compatibility. If constraints fail,
retain the diagnostics unselected and report the limiting geometry.
