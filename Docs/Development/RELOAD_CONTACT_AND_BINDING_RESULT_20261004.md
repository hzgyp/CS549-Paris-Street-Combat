# Reload contact preview and game binding check — V3 record

4 October 2026, 17:15 EDT. Preview attachment inspected; actual-game binding test NOT run.
Chinese review: [result](RELOAD_CONTACT_AND_BINDING_RESULT_20261004_ZH.md).
Plan: [V3 implementation](RELOAD_CONTACT_AND_BINDING_V3_20261004.md).

Later 4 October update: the user accepted this original preview and requested
game adoption. Both actual-game binding scopes and the isolated V4 proof have
now run. Binding/proxy grip improve, but target-soldier sleeve views still fail;
the formal map is unchanged. See the [later result](RELOAD_APPROVED_GAME_INTEGRATION_RESULT_20261004.md)
and AN003. The 17:15 pending/not-run statements below are historical snapshots,
not a withdrawal of source-preview acceptance.

## Completed preview-only work

The user states the game grip was already corrected. Its parameters were not changed.
The original D059 `W2_Stand_Aim_Reload_IP` on `SK_Mannequin` had the existing M1
on `hand_rSocket_Aim` with an identity relative transform. That source socket is
not the validated Allied in-game attachment.

One transient candidate uses the existing V3 local grip (-0.5,-8,0)cm and
two-palm heading rule at source time zero, converted once into source `hand_r`
coordinates. The right proxy averages middle/ring/pinky/thumb 02/03 bones.
Relative translation is (-18.067599,5.678340,-0.657171)cm; quaternion is
(0.019928,-0.061716,-0.776552,-0.626706), with equivalent negation. Unit scale,
NoCollision. Native attachment subsequently moves the gun; no Python frame updater.
Models, rig, fingers, source motion and game camera remain unchanged.

Five explicit phase observations at 0/1.2/2.2/3.4/4.13 seconds retain the same
relative transform; maximum proxy anchor error 3.06e-14cm. Five Back-side native
viewport images were inspected: more coherent overall right grip, without obvious
whole-gun separation. Neither proxy precision nor these full-body views certify
every fingertip/trigger contact or absence of clipping. This modern generic reload
still lacks M1-specific left-hand loading. No new action or production selection.

Private evidence: workspace `Evidence/ReloadContactBindingV3/contact_probe_v1/`
and `contact_fit_v1/`; the Chinese record embeds two of the inspected images.
Preserve two console NameErrors before explicit builtins import; successful later
observations and native playback restoration are in the user-preview log.

## Prepared, not executed

New `ue_reload_game_binding_v3.py` and its serial launcher passed Python AST and
PowerShell parser checks. User-owned preview PID42928 remained open. Close the
entire editor before a disposable test; do not kill it or launch a competing writer.

Separate fresh scopes: `saved` for the saved city/player/native owner, and `actions`
for existing unsaved V6/ActionOwnerV1 staging used by the latest action preview.
Observe native Ready→Reload→Ready→reset, body/PoseMesh/display leaders, mesh/rig,
LOD, 15 component bones, rifle references and unchanged camera. Existing requests
only: no ammo injection, clip switch, leader correction, stopped AN001 stage/author
or AN002 geometry/skin read.

Source-based hypothesis, NOT a runtime finding: engine SetLeaderPoseComponent
reroutes followers to the final leader and does not restore them when unlinked.
ActionOwner links PoseMesh to BodySource during Reload, then only unlinks PoseMesh
at Ready. Display might remain linked to BodySource while its gun follows the
holding PoseMesh. Must verify actual transitions; not proof of the old sleeve defect
or a substitute for AN001 reference-pose diagnosis.

## Protection / limits

17:13 EDT: all 512 recorded size/SHA checks matched (507 protected + 5 failed
AN001 drafts). Formal map remains 2791b4a7...ad68519. No native save, formal-game
binding change, baseline/release/Catalog/allowlist selection or commit/push.
Character-workflow principles informed same-phase contact inspection only; no
Blender reconstruction. Actual-game binding and sleeve repair remain unverified.
