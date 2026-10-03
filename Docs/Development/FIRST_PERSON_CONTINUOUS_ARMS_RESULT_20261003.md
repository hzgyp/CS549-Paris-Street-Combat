# Continuous first person arms static result

Date: 3 October 2026. [Implementation](FIRST_PERSON_CONTINUOUS_ARMS_IMPLEMENTATION_V3.md). [中文结果](FIRST_PERSON_CONTINUOUS_ARMS_RESULT_20261003_ZH.md).

Subsequent user review: Yupu says this static view is much better and authorizes movement/reload validation. The static direction gate is now passed by user report; dynamic, muzzle and shipping acceptance remain open. Continue under [the dynamic plan](CONTINUOUS_ARMS_DYNAMIC_IMPLEMENTATION_V1.md), not the historical static-review pause below.

## Outcome and next human gate

A new complete-arm derivative produces a usable **static review candidate** in the real Paris city. Inspection of `static_v2/continuous_arms.png` shows the M1 rear/receiver toward the lower right, a continuous left sleeve entering through the bottom, no visible shoulder/forearm cut face and no head/neck/equipment intrusion. The rear stock exits the view rather than crossing the lower center. The actual [COD WWII ordinary holding reference](https://steamuserimages-a.akamaihd.net/ugc/850479378283268857/6FD1E05F7B9B71363EA2DF1BAB83CE03BD257616/) was inspected in the browser; its [source guide](https://steamcommunity.com/sharedfiles/filedetails/?id=1190361079) is retained as a link, not a copied asset.

This is an internal static image finding, **not Yupu's visual approval or a completed repair of movement/reload**. Pause here for his holding-composition review, as the implementation plan requires. Do not select the candidate in the saved map yet. There is no accepted dynamic motion or new-muzzle gameplay implementation.

## Different mechanism and actual changes

The arm geometry is extracted from the existing permitted US soldier exchange file, not modeled from scratch. Retain faces whose vertices have at least 0.25 summed upper-arm-descendant skin weight; preserve complete sleeves, hands and original per-vertex data. No forearm capsules, material opacity masks, finger edits, bone pose redesign or additional offset sweep were used. The one static grasp position is `(22,22,-16)` cm in the original camera frame.

The derivative has 6,135 exchange vertices, 10,943 triangles, four UV layers and no unweighted/bad-sum vertices in the recorded checks. Original material slots persist in the editable exchange; the native arm-only mesh resolves the two used original jacket/skin materials. Geometry selection does not authorize changes to the original full body or source actions.

Two new unselected native packages, mesh and separate experimental skeleton, total **1,519,887 bytes**. Current hashes and dependency references are in [CONTINUOUS_ARMS_TRIAL_INVENTORY_20261003.json](../../Assets/Integration/CONTINUOUS_ARMS_TRIAL_INVENTORY_20261003.json). Source/FBX/mesh before-material-repair bytes remain privately preserved. Original 40 native files plus these two are verified, 42 retained in active storage; FP001's seven archived packages remain offline. Catalog and immutable releases are unchanged.

## Exchange and native checks with retained failures

Private evidence root: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/ContinuousArmsV3/`; logs: `tmp/continuous-arms-v3/`.

- `exchange_v1/result.json`: initial extraction completed, but strict rounded vertex signatures and local-unit bone matrix tolerance failed. Blender process exited 0 despite the Python assertion; the report is failed, not a pass.
- `exchange_v1/roundtrip_precision_v1.json`: read-only inspection of that same exported derivative passed the declared precision gate. Maximum world vertex-position difference `3.24614e-7` m, skin-weight difference 0, world bone-matrix component difference `7.74860e-7`; full bone hierarchy and vertex/face/UV-layer counts match. This does not prove every native motion or lossless engine shading.
- `native_import_v1`: unavailable `imported_material_slot_name` property, report failed, no native asset save. Engine exit 0 does not override the failed report.
- `native_import_v2`: corrected slot lookup, new mesh/skeleton saved, all original 40 files unchanged. No missing/extra bones or parent mismatches; tested upper-limb reference translation maximum `0.000180` cm and axis-vector difference `8.33e-6`. The importer warned about invalid bind poses/time-zero rebinding and absent smoothing groups. These warnings remain limits requiring further motion/shading review.
- `static_v1`: fresh load revealed WorldGrid materials because modified structs were not assigned back into the Unreal array. The inspected gray candidate is geometry evidence only. Its recorded material claims from the earlier in-memory import do not establish persisted binding.
- `native_material_v1`: explicit array-index writeback fixes only the new mesh's original native material bindings; before bytes retained, new skeleton unchanged, original 40 files unchanged. Engine exit 0.
- `static_v2`: new engine process asserts the saved jacket/skin materials, freezes one original idle phase and captures saved V3 versus the complete-arm display. Both actual viewport images were inspected. Same composition/geometry as v1, not another pose/offset trial. Engine exit 0, empty report errors and no `Error:`, fatal, failed-ensure or failed-assertion matches in the log. Ordinary engine/vendor warnings remain.

## What the static measurements establish

`static_v2/result.json` records zero source-finger change and maximum follower finger-local component difference `8.69e-13`. Right-grasp proxy difference is about `9.48e-13` cm; support-grasp proxy separation remains the source's approximately `0.009684` cm. These are matrix/proxy measurements, not proof of perfect fingertip-to-wood mesh contact. The imported native reference pose is close and the inspected idle arm surface shows no obvious collapse, but other poses remain untested.

Camera `(25,0,60)`, FOV 90, original evaluated source class/fingers and original `WeaponAppearance` binding remain intact. All 42 sizes/SHA matched during the trial and the final read-only check. Saved map remains V3, SHA `d00056e8e65d3de6cf7c6af08fe9e52fa4e95e656bfe10a7392c03a82409f51f`. Runtime modifications are discarded when PIE ends; all task-owned editors exited.

The `Shot` viewport captures omit Slate HUD. They do not establish HUD/crosshair readability, pixel-perfect sight alignment, actual keyboard input or motion performance. The original V3 gun remains the gameplay `WeaponAppearance`, owner-hidden; the displayed gun has not been tested as the authoritative muzzle. Original gunplay source is unchanged, but old combat passes are not a pass for this new display.

## Next work only after visual direction is confirmed

If Yupu accepts this ordinary holding direction, first update the implementation increment for original idle/movement/start/stop/sideways/pitch/fire/reload/death/reset checks. Inspect shoulder boundaries throughout those motions and retain the generic reload limitation. Explicitly define/update and regress the visible versus authoritative muzzle interface, including near walls and ammo/lifecycle. Do not infer dynamic obstruction removal from this still image or hide a failed cut boundary with masks.

No AI/VFX/ADS/new movement, acquisition, saved-map selection, packaging, immutable asset publication, Catalog/allowlist change, commit or push occurred. Python/PowerShell syntax and source-storage metadata guard passed; the guard checked 17,273 selected metadata entries, not all selected local hashes in this turn. The dedicated 42-file native hash check did check actual bytes. Preserve all failed attempts and existing dirty work.
