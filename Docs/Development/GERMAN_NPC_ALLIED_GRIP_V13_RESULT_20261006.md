# German V13 — rejected by user; resume the previous refined German pose

## Decision

6 October 2026: Yupu says the effect is poor, explicitly abandons this trial and
directs continuation from the previously refined model/parameters. **V13 is
retired in its entirety. Do not consume its pose/config/diagnostic blends for
UE binding or repeat the whole-grasp transfer/seating mechanism.**

Resume `Evidence/GermanNPCLowerGripV11/source_frame_v4/result.json` with its
`frame_failure_views_v1/diagnostic_geometry.npz` and unchanged FineWoodV15 gun.
This is the earlier thumb/lower-three appearance subsequently accepted by the
user in the V12 conversation, not complete contact/native/formal acceptance.
Keep V11's raw failed numeric result. V12's failed index trial is NOT the fallback.

All evidence is within the existing ignored private SFTP workspace. No duplicate
production model was made elsewhere. Formal German was never changed by V13
and remains unarmed; no source/map/Catalog rollback is necessary.

## What this experiment actually established

The 32 common hand/reference frames and hierarchy passed compatibility checks;
30 corresponding local digit rotations could be transferred while retaining
German translations/scales/bone lengths/weights. This is **technical pose
compatibility, not a successful grip**.

The first conventional Allied NPC V14/V16 donor still had a relatively straight
index. Actual views exposed the mismatch with the user's explicitly linked
`WeaponTexturedViewsV17/presentation_v2/three_views.jpg`, which is the Allied
first-person hand presentation. A documented donor correction then used the
accepted/current FP V18-right/V20-left local rotations; its pinky 0.90 scale
was deliberately NOT transferred. No approved Allied/FP data was modified.

Correct-reference transfer fit (`transfer_fit_v2`) registers the actual German
blade to its donor correspondence, changes gun orientation10.044 degrees and
origin4.756cm from V11, and follows with original-length left arm. Index wood/
guard/blade face counts8/11/22 ->10/0/0, but thumb wood57->83 and lower three
lose their previously refined contact. Left thumb/index wood80/41 remain; one
new index-neighbor self pair is recorded. Zero crossings in the other lower
digits are NOT evidence of closure: views show gaps.

One actual opposed-surface rigid seating (`seating_v3`) turns19.000 degrees and
moves gun origin5.072cm from the transfer. Index stock/guard0 but blade11;
thumb wood71, lower wood38/52/73; station residuals0.369..1.061cm. Actual views
show a raised muzzle and deficient support grip. This comparison is stopped,
not a successful fine-tune; do not add another angle/offset or individual digit
compensation based on its counters. Both trials have no new severe edges under
the documented criterion; that does not excuse contact/visual failure.

## Evidence and limitations

Fresh full-skin reconstruction of the seating has skin error0.000232cm and
gun0.000218cm. `gray_v3` and `textured_v3` contain full original body geometry;
full-body reverse/top closeups are torso-occluded, not acceptance evidence.
`presentation_v2` contains matched hand-only diagnostic views plus unchanged
full-body context for both comparisons. Hand isolation copies existing triangles/
vertices/UVs only for presentation; ragged sleeve boundaries are NOT a runtime
cut or a repaired asset. Portable jacket/helmet appear pale instead of native
camo, so these renders do not establish UE material parity. No texture repair
or recoloring was attempted to hide that limitation.

The three final sheets were inspected, with original trigger/support/full-context
details opened. A material-name collision initially stopped textured_v2 before
rendering; one material-key-only viewer repair produced textured_v3. That failed
receipt remains. Earlier tool revisions changed during development; their
historical source hashes must not be called freshly exact. Binary/data inputs,
current image hashes and all618 current formal guards passed checks.

The final private serialization check restores protected bone dictionaries
exactly rather than float32 re-encoding them. Skin difference from displayed
comparisons is <0.000009cm, local donor rotation error<0.000080 degrees. It is
not a new fit, improvement or accepted asset; these payloads are also retired.
The user's rejection arrived after that owned background check had completed;
its normal exit0 is preserved, not canceled or relabeled successful contact.

## Resume checkpoint

`Evidence/GermanNPCAlliedGripV13/retired_by_user_v1/result.json` records verified
previous baseline/model hashes and618 current guards. All owned Blender runs
exited0; no Blender/Unreal process was found at retirement check, no native slot
was claimed. A remains RELEASED. No UE package/map save, native integration,
formal adoption, Catalog publication, asset deletion, commit or push occurred.

Next work must retain the earlier refined German thumb/lower-three and gun
parameters and make only a newly bounded local correction. Do not replace the
entire grasp again, replay V12/V13 solvers or treat the visual fallback as full
animation acceptance. Preserve existing motions/source weights/model/rig,
approved Allied and first-person assets, B/AI and the current guard epoch.
