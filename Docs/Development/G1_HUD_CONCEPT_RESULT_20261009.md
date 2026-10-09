# G1 approved HUD concept — actual implementation result

9 October 2026. [Chinese review](G1_HUD_CONCEPT_RESULT_20261009_ZH.md).
Yupu selects the generated ivory/brass WWII interface for implementation.
[The paired plan](G1_HUD_CONCEPT_IMPLEMENTATION_20261009.md) records cases read,
bounded V1/V2/V3 differences, early visual checks and stopping conditions.

## Delivered change

Private `hud_v3` implements the selected composition over the ORIGINAL live Paris
scene: Cinzel serif type, warm ivory/brass, compact floating objective, circular
metric map, medical cross/six-segment health, two filled squad silhouettes,
large loaded/smaller reserve counts, actual capacity ticks and compact save icon/
question/E/Esc keycaps. No oversized panels, permanent tutorial row or duplicate
feedback bar. Transient saved/reload/unsafe/failure feedback remains readable.
Circular borders use feathered vertex-alpha annuli; the ground checkpoint ring is
thin gold, same180cm center/radius/entry test. The concept's generated environment,
weapon/hands, fixed sample numbers and sketch map are NOT used as runtime assets.

Only ONE private cpp differs from functional V10: rendering includes/DrawHUD,
the ring's colour/segments/thickness and green→gold feedback wording. All38 other
source files, original headers/defaults/reflection/config/observer/cooked
dependencies and non-render action/navigation/resource/save policy remain exact.
The39-file source manifest includes this one changed cpp;40-file SourcePatch
additionally freezes the unchanged descriptor. No canonical asset/native save,
Catalog selection, model/grip/clip/camera/gun/damage/reload/input/AI modification.
Canonical758 source/703 protected/359 selected native authenticate at preparation;
758/703 and private source identities are repeated by runtime/delivery audits.

Unmodified Cinzel125,468-byte sidecar SHA256
`f4d83d34d1f6c741193e4acf4b3dff9531e5a67b6aa65228d00a7db72a4e0f34`
is distributed with its [upstream OFL license](https://raw.githubusercontent.com/google/fonts/main/ofl/cinzel/OFL.txt)
and provenance. One strongly held transient runtime UFont supplies Canvas's required
FontObject; no native font package or new serialized/reflected fields. Actual
Cinzel face loads and positive glyph-draw metrics appear in every final entry.

## Actual verification

Final executable SHA256:
`497221422d7754d562b4e6d11fd8cc50c9223e40b329b26c8c14391a98d1c42b`.
Game-only compilation and complete reused-cooked-payload checks pass. Compiler
C4701 in unchanged ValidateSnapshot is retained in raw build logs; that method
was not changed or newly repaired here. No Editor build/recook claim.

| Entry | Actual result |
|---|---|
| `hud_plain_v3` | Observer-disabled1920×1080 Ready, exit0/strict0. Viewed authentic serif text, circular clip/smooth rim, health100/all six segments, real2/16 and capacity pips, native FP/Allied equipment and compact Enter prompt. |
| `hud_small_v3` | Observer-disabled1280×720 Ready, exit0/strict0. Viewed layout, digits, labels and map inside margins without overlaps/clipping. |
| `hud_checkpoint_v3` | 137.272s, exit0/strict0; unchanged finite observer. Nine real hostile-hit shots kill three Germans. Two/one survivors do not unlock; zero unlocks. Enter question/Serial0/no autosave; Escape/leave/reenter, moving E denied, safe standing E saves once Serial1; fresh-world F9 restores Won/death/resources, F6 resets Ready/three defenders/circle. Three native worlds/action integrations/bridge-policy applications. |

Actual checkpoint prompt/saved/loaded1080 images were all viewed. They show100
health,7 loaded/2 reserve, seven of eight capacity ticks,3/3 elimination objective,
gold circle and actual save question/saved/recovered feedback. Map is still the
authenticated G1 ground survey, same world→XY/heading/visible-enemy rules; circular
clipping hides corners rather than inventing streets. Grid N remains +Y. No
full-city/multilevel or geographic survey claim; no extra scene-capture camera.

The checkpoint test repeats eight stationary seconds: nearest Ally459.619cm,
maximum Ally travel0. Result SHA256
`749ef21b0da126bd148d1e642ca659ed6f0ff37b7f1c6da37ec7d74b6514bf3f`.
Visual review is separate from generic identity/numeric audit. The V10 action
suite was NOT rerun for this rendering-only change; its movement/obstruction pass
remains attributed to V10. No new performance, sustained-motion/contact, natural
two-sided combat, video, second-machine, human or course completion acceptance.

## Preserved negative and bounded correction

Read MI010–MI013 and previous actual playtest result before authoring. V1 shows
map/icons but no text despite compile/exit0/strict0 and generic audit. Installed
UE Canvas HasValidText requires UFont; composite-only Slate info left it null.
Archive `Evidence/Failures/MI013/hud_v1_missing_text` authenticates source/log/
launch/audit/image; do not rewrite generic audit as a visual pass. V2's transient
UFont/real-draw witness fixes the mechanism, viewed text/numbers pass. V3 modifies
only Circle/Soldier primitives after viewing aliasing/stick silhouettes, preserving
V2 font/layout/data/policy. FrozenSource records retain each parent. No stopped
recorder/backend sweep or model/grip fitting was reopened. Original V9 GPU startup
cause remains unverified; all three final HUD entries start/exit normally, not a
claim to have diagnosed/repaired that old device failure.

Early/stop gates were compile, authentic font/map/text, actual two-resolution
layout, original legitimate death/consent/resources/load and strict/GPU identity.
V1 stopped at the visual font gate; no further entry used that failed mechanism.
Final gates above pass locally, user visual acceptance of implemented UI pending.

## Private playable handoff

New directory `tmp/Playtest-G1-HUD-20261009`, entry `PLAY_G1_REVISION.cmd`.
Enter starts; previous action controls remain; E saves/Esc declines; F9 loads,
F6 restarts. SAME `ParisG1PlaytestV5` prefix/config and
`%LOCALAPPDATA%/ParisStreetCombat/G1PlaytestV5` save directory as V10; exact
nonrender/schema/config supports compatibility, but no user-owned old save was
opened or overwritten in tests. Test prefixes/UserDirs are isolated.

Private `Evidence/G1HUDConceptV1/delivery_v1` preserves40-file SourcePatch,
delivery receipt and16 final raw qualification files with their manifest.47 Archive
files are copied and SHA/size verified, then one recorded launcher-only override
adds `DisableAllScreenMessages` as in final tests. Old8October and9October trial
folders/saves and frozen Archives remain intact. Font/license/provenance are the
only three added sidecars over V10. No new ZIP, public binary upload or commit/push.
Approved concept and rejected V10 presentation references are retained privately.

Original terrain-restricted prone, standing-only firing/reload, incomplete low-
posture eye height and sprint/jump lowering remain unchanged. Human/full-contact,
second-machine,60FPS/natural-combat/video/course gates remain open. Inspect actual
processes before later entries; never end user-owned games automatically.
