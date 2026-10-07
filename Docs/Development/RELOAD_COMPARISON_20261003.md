# Current reload versus existing D059 candidates

4 October binding policy: reuse existing purchased Xianyu mature reload/recoil
motions, then bounded target adaptation; no new motion creation. See the
[animation policy](GERMAN_RIFLE_UE_AND_ACTION_RESULT_20261004.md). Candidates are
not selected by this rule; original clips/ammo/finger/camera protections remain.

Date: 2026-10-03. [中文](RELOAD_COMPARISON_20261003_ZH.md). Inspection/recommendation only: no gameplay replacement, source/rig/finger/camera changes, formal map save, asset selection or publication.

## Recommendation

### Later human review: current reload appearance rejected

Later the same day, Yupu explicitly reports `Rifle_Reload_2` looks very ugly. This human visual rejection supersedes the earlier technical retention recommendation below: functional correctness does not justify retaining its appearance. Keep the saved version for rollback, not as a visually accepted reload. Next evaluate D059 Aim as an independent candidate on the same target soldier, existing M1 and protected camera before selection/adaptation; no native binding has changed in response yet. Its non-M1-specific limitation remains, but does not justify refusing a generic visual-improvement comparison.

The proposed AI/Aholo/Blender German rifle pilot is separate and cannot repair player M1 reload. See [the pilot plan](GERMAN_RIFLE_PILOT_IMPLEMENTATION_V1.md). Earlier findings below remain historical evidence, not final visual selection.

**Do not directly replace the current reload with D059 now.** Current gameplay already plays a real inventory clip, `Rifle_Reload_2`, not a timer-only omission. D059 standing aim reload is a future comparison candidate; relaxed reload does not directly fit the current raised Ready interface. Neither establishes matching M1 bolt/en-bloc/round mechanics or weapon contact. Swapping the clip alone will not close those gaps.

The MVP can retain its validated simplified reload transactions. For realistic M1 presentation, prefer matching articulated weapon parts and hand actions, then bounded adaptation. Do not buy more generic reload motions: the inventory is sufficient for candidate testing, not automatic first-person acceptance.

## Actual binding

| Role | Native path | State |
| --- | --- | --- |
| Current gameplay | `/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Reload_2` | Bound; continuous arms follow the body source during reload |
| D059 aim candidate | `/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP` | Available in inventory/baseline, unbound |
| D059 relaxed candidate | `/Game/Rifle_01/Animation/In-Place/W2_Stand_Relaxed_Reload_IP` | Available in full original, unbound |

`SetReloadDefaults` in `Unreal/ParisStreetCombat/Plugins/ParisEditorBridge/Source/ParisEditorBridge/Private/ParisReloadDraft.inl` supplies the current path. `PC_RequestReload` calls body-mesh `PlayAnimation`; actual fresh-load dependencies and the native playtest manifest corroborate the clip. The Editor bridge authors the Blueprint, not runtime per-frame Python control.

Simplification omits matched independent M1 bolt/clip/round mechanics and leaves generic contact limitations; it does not omit the entire body reload. [Earlier transaction tests](WEAPON_BASELINE_AND_RELOAD_RESULT_20261002.md) are historical gameplay evidence, not rerun by this inspection.

## Actual comparison

Separate UE 5.8.2 lab `compare_v4`: seven static phases (0, .15, .30, .50, .70, .85, .999), two fixed views per clip, 42 images at720×800 and21 bone samples. Positions match sampled times and hand excursions reject stale poses. Engine exit0; log summary0 errors/0 warnings. Current clip uses the adapted Allied model, D059 uses its own source mannequin: **not a matched-target/first-person replacement A/B**. No weapon or ammunition props are attached; images cannot certify contact or M1 mechanics.

Legacy `front` filenames actually refer to -Y rear diagnostic captures. Corrected sheets below label the upper row -Y rear and lower row +X side.

| Clip | Original seconds | UE API frame count | Root motion | Sampled left-hand excursion |
| --- | ---: | ---: | --- | ---: |
| Rifle_Reload_2 | 2.166667 | 324 | False | 61.72cm |
| D059 Aim Reload | 4.133333 | 123 | False | 85.70cm |
| D059 Relaxed Reload | 5.300000 | 158 | False | 49.98cm |

Different rigs/proportions affect distances; larger excursion is not a quality or obstruction ranking. Source frame counts are not rendered FPS/quality scores. Static phase samples do not prove smooth complete transitions or moving reload blends.

### Current

![Current reload fixed-phase diagnostic](../../Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/compare_v4/current_allied_review_sheet_v2.png)

Reviewed: raised start/end, support hand leaves its initial area, reaches waist/equipment around15–30%, returns forward around50–70%, and returns to the initial region. There is actual hand operation, not pure waiting. Soldier hand shape/contact still requires an equipped runtime check; empty-hand images do not accept fingers or contact.

### D059 aim

![D059 aim reload fixed-phase diagnostic](../../Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/compare_v4/d059_aim_review_sheet_v2.png)

Reviewed: raised start/end, operating hand raises, visits equipment and returns forward, with a longer staged operation. Its interface is closer to raised Ready than relaxed reload, but not an accepted M1 adaptation. At original speed it lasts approximately1.91×current; length/staging alone do not establish better FP quality.

### D059 relaxed

![D059 relaxed reload fixed-phase diagnostic](../../Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/compare_v4/d059_relaxed_review_sheet_v2.png)

Reviewed: low hand/weapon area at start/end, raised operation in between, then lowered again. Direct use from raised Ready risks discontinuities; it better suits a future explicitly designed low-holding state than an immediate replacement.

## Conditions for a later replacement — not implemented

1. State the target improvement: contact, transitions, rhythm or actual M1 mechanics; names/MoCap labels are not acceptance.
2. A new implementation plan must preserve protected model/rig/finger/camera/gun transactions. Compare on the same target soldier/weapon, admitting reference-pose/retarget compatibility rather than forcing flags.
3. Test the full standing/moving cycle, view pitch, contact, obstruction and Ready boundaries. Mechanical acceptance needs the actual parts, not empty hands.
4. Ammo commit must follow the safe insertion/completion event, not blindly retain1.083s or assume50%. Compressing D059 Aim to current duration needs approximately1.91×rate, changing its appearance; do not do this just to fit timing.
5. Regress interruption/death/reset/stale events/conservation/near-wall shots and continuous-arm/model guards. Use a separate identity, human review, then an explicit selection/SFTP decision.

## Retained failures and preservation

- `compare_v2`: current mesh path omitted `Meshes`; no valid action images.
- `compare_v3`: occupied diagnostic map name, exit1; no valid images. Earlier `new_level` actually created an empty map in isolated `ReloadLab/Content/ReloadReview` despite no explicit save call. Its `packages_saved=false` field is not proof no diagnostic map ever existed. That map remains outside the formal project as evidence.
- `compare_v4`: switched to a real `/Temp/Untitled` world, completed42 images without native saves. Initial sheets mislabeled -Y as front; preserve them and use corrected `*_review_sheet_v2.png` here.
- All results/logs remain in ignored `Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Reload/`. No failure deletion, formal rollback or selection.
- Rechecked new blend,43 native checkpoints,7 action drafts,206 published non-city native files and2153 original files across four manifests. Final sizes/SHA and Markdown link checks: [private report](../../Assets/LocalWorking/Validation/2026-10-03-asset-catalog-v1/Catalog/final_verification.json). Overlapping records are not duplicate physical storage.

[Illustrated catalog](../../Assets/XIAN_YU_ASSET_CATALOG_20261003.md) · [Scope and stop conditions](ASSET_CATALOG_AND_RELOAD_REVIEW_IMPLEMENTATION_20261003.md)
