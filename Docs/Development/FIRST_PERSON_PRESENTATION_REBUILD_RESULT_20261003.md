# First-person rebuild V2 — bounded static result

Date: 3 October 2026. Plan: [V2](FIRST_PERSON_PRESENTATION_REBUILD_V2.md). [中文审阅](FIRST_PERSON_PRESENTATION_REBUILD_RESULT_20261003_ZH.md).

**FP001 archival is complete. The new three-position rigid composition probe fails the no-self-obstruction criterion. No candidate is selected, no dynamic extension was implemented, and saved V3 remains unchanged.** This is an early negative experiment, not a completed first-person repair or a new user-approved view.

## Archive prerequisite

[FP001 verification](../../Failures/FP001-20261003-first-person-view/VERIFICATION.json) confirms 664 archived/snapshotted entries (640,322,531 bytes), seven exclusive native packages removed from active Content, the previous 40 native files unchanged, and restored pre-FP bridge deployment. Fresh bridge-disabled V3 combat `archive_v3_v1` passed 15 cases/62 assertions, exit 0. The 17,273 selected local asset files passed the storage/hash check. These checks protect the starting point; they do not approve this new display or its muzzle interface.

## Retained attempts and actual evidence

Private evidence root: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/FirstPersonRebuildV2/`. Logs: `tmp/first-person-rebuild-v2/`.

- `composition_v1`: exit 0 and unchanged protected bytes, but source/A/B images showed the editor view and C included editor chrome. Its `REVIEW.json` marks the visual comparison invalid. Preserve all files; do not cite them as a matched comparison.
- `composition_v2`: viewport-only captures, settled control rotation, 20-second startup wait and at least 60 frames/5 seconds per sample. All four actual images were inspected. They show the same storefront/player viewpoint and frozen source pose. `Shot` without `SHOWUI` omits the Slate HUD; these images cannot establish HUD readability or crosshair alignment. The source runtime camera and existing HUD were not altered.

| Sample | Camera-local right-grasp target, cm | Inspected result |
| --- | --- | --- |
| source_v3 | Existing V3 | Original angled rifle and limited arm framing; historical baseline, not newly accepted. |
| A_near_right | (22, 22, -16) | Rifle/support arm enter from the lower right/bottom with the rear stock outside the frame, but head/helmet/straps intrude along the upper-right edge. Fail. |
| B_near_right | (26, 25, -18) | Larger visible head/neck/clothing obstruction at upper right. Fail. |
| C_near_right | (30, 28, -20) | Large own-body obstruction at right and a visible clothing fragment at left. Fail. |

`composition_v2/result.json` records four samples, no script errors, no native saves and all 40 protected files unchanged. Source finger delta is 0 throughout; maximum follower finger-local component delta is `1.1547e-12`. Maximum rear-grasp proxy distance is `1.8551e-12` cm. Support-grasp proxy distance stays at the source's approximately `0.028873` cm. These are matrix/proxy checks, not mesh-surface contact acceptance. Camera remains `(25,0,60)` cm, FOV 90, with identical sampled world position/rotation. Original mesh/material slots, scale 1 and source actions are retained; no masks or hidden bones are used.

The engine exited 0. Log inspection found no `Error:`, fatal, failed-ensure or failed-assertion matches; ordinary startup/vendor warnings remain. All task-owned editors are closed at closeout. Static testing did not fire, reload or move, and `WeaponAppearance` remained the original V3 gun. **Gameplay with the new visible muzzle is untested.**

## Decision and next boundary

The declared hypothesis was falsified for these three samples: preserving the whole source pose by rigidly moving the body and rifle does not place all non-arm geometry outside the protected camera view. Bringing the assembly forward also brings head/neck/clothing into view. This does not prove that every possible original-pose presentation is impossible.

Stop this offset set as required by the plan. Do not choose the least obstructed frame, add forearm capsule masks, sweep more offsets, extend movement, or select a map from these results. Before another implementation, document a different mechanism: assess compatible existing holding content or a bounded owner-view adaptation that separates non-arm visibility from continuous arm presentation, while protecting original assets, finger poses, source actions, camera and gun transactions. This is a next-design requirement, not authorization to resume the rejected modeling/finger route or purchase assets. A usable static candidate must exist before asking the user to judge the intended holding style.

No native V2 package, new model, commit, push, Catalog change or publication was made. Saved map SHA remains `d00056e8e65d3de6cf7c6af08fe9e52fa4e95e656bfe10a7392c03a82409f51f`.
