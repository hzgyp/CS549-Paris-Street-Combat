# German NPC V8 — marked stock-side outward rotation result

6 October 2026. **ONE requested outward comparison delivered, not full-contact
acceptance or a formal replacement.** User approves continuing from V7 and
marks the stock side to turn toward the screen. Preserve V7 as the comparison
baseline; this feedback does not select a native asset or erase residual errors.

Read [V8 plan](GERMAN_NPC_SCREEN_ROTATE_V8_20261006.md), current HANDOFF/618 epoch,
Failures/V7 result, reviewed GP010/AN002/AN008, weapon-hand guide and character
workflow. The changed mechanism is a small 3D stock-side turn toward the actual
reverse camera, not further downward pitch, finger edits or a repeated old fit.
Early checks protect the trigger, right pose, original left-arm lengths, true
zero-left-influence skin and sleeve edges. Contact tradeoffs stop further fitting.

## Actual transform and protected scope

Starting V7 AFTER skin and gun reproduce its retained review exactly (0cm).
Approximate resized screenshot ray hits actual wood triangle14387 at
(-5706.526855, -1237.184814, 238.325531)cm. This point is inferred from screenshot
framing, not calibrated marking precision. Red box identifies an observation
region; the existing actual trigger remains the pivot.

ONE4-degree turn about normalized world axis
(-0.226373, -0.279889, +0.932962). The marked wood point moves
(-0.128222, +0.844408, +0.222211)cm, with +0.872648cm actual viewer-depth motion.
No independent translation/scale or angle sweep. Trigger residual9.10e-13cm;
protected bone matrices2.27e-12 and digit-local matrices1.82e-12 maximum error.
Raised right thumb, wrist/arm and other right digits are not edited.

The full left grasp follows the gun through original-length left IK: wrist moves
0.835378cm, upper/forearm lengths30.340206/26.975175cm, length errors<2.2e-13cm.
Left gun/hand-relative matrix error9.09e-13; mixed left-digit skin tracking
0.246483cm, not rigid skin zero. New severe edges0 (>3x AND >2cm-extra), maximum
extra edge0.173706cm. True-zero-LEFT-influence skin2.84e-12cm and distal right
index1.25e-12cm; six cross-hand-weight vertices remain affected. Actual three
right-side shared boundary vertices move0.103307/0.158082/0.104432cm in fresh
review. No weights/rest/source mesh/actions/materials/UV/lengths were changed.

## Contact and actual view findings

| Crossing-face diagnostic | V7 BEFORE | V8 AFTER |
| --- | ---: | ---: |
| Right thumb / wood | 44 | 57 |
| Right index / whole gun | 73 | 52 |
| Right index / wood | 29 | 16 |
| Right index / trigger blade | 20 | 22 |
| Left thumb/index/little / whole gun | 2 / 84 / 24 | 2 / 84 / 24 |

Other middle/ring/little counts remain zero. Counts are not penetration depth,
grip enclosure or complete visual acceptance. Index overlap reduces, but thumb
overlap increases and blade overlap remains. **Do not call this an overall
clearance pass or continue the outward angle automatically.**

Opened all ten original BEFORE/AFTER reverse, right, top, support and full-arm
images, then both labeled sheets. The stock moves toward the viewer and covers
more of the proximal orange thumb in the reverse image; that coverage is not
proof of repaired penetration. Top/right still show incomplete stock/hand fit.
Left arm/grasp remain continuous in these static views; small palm/cuff skin
projections persist. Palm-against-left-stock-side goal is not completely verified.
Gray diagnostics are not native UE materials or motion/binding evidence.

Fresh read-only reconstruction preserves the exact retained transform; maximum
skin transport error0.000244cm and gun0.000181cm stay within separately declared
0.01cm display parity. This does not relax raw matrix or contact checks. Reviewed
V7 renderer is reused as read-only scene/check code, not an old fitting launcher.

## Evidence and closure

Private evidence root:
`Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/GermanNPCScreenRotateV8/`.
`screen_turn_v1/result.json` records source/marking hashes and ONE comparison;
`review_v1/result.json`/`diagnostic_geometry.npz` records fresh checks and ten
images; `review_v1/three_views.png`, `context.png`, `presentation.json` are review
only. No usable character/weapon model or native asset was authored or selected.

Both owned Blender processes exit normally0. Final618 guards/13 retained input
references exact/three tools parse/no UE or Blender engines. No native slot was
claimed; lane A remains RELEASED. Formal German remains unarmed; approved
Allied/FP/B/AI/map/Catalog/source rig/weights/actions/materials untouched. No
asset/map/package save, release/publication, deletion, Git commit or push.
Stop for marking, no further angle/offset/thumb compensation under this plan.
Motion/reload/recoil/lifecycle/FPS/Shipping/second-machine gates remain untested.
