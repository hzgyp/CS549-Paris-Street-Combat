# G1 approved HUD concept implementation

9 October 2026. [Chinese review](G1_HUD_CONCEPT_IMPLEMENTATION_20261009_ZH.md).
Yupu rejects the panel-based playable HUD, approves the generated WWII concept
and explicitly requests implementation. This is a private playable UI revision.

Cases read: Failures/README, MI012 (input integration, terrain/ballistic negatives,
capture decision boundaries and unexplained GPU startup), MI010–MI011 (stopped
recorders), and [MI013](../../Failures/MI013-20261009-hud-visual-design/FAILURE_ANALYSIS.md).
Also read the actual G1_PLAYTEST_REVISION_RESULT_20261009 and its plan. V10 is the
functional baseline; its model/grip/action/navigation/resource/save results are
preserved. A numeric startup does not establish visual design acceptance.

## What changes

Implement the user-selected image's composition: warm ivory and aged brass,
compact floating objective at top-left, circular map at top-right, medical cross/
segmented health and two squad silhouettes at bottom-left, large loaded/smaller
reserve counts and capacity ticks at bottom-right, small save icon/question/E/Esc
keycaps at lower-center. Remove oversized rectangular backings, permanent tutorial
row and duplicate status bars. Keep readable text shadows and compact transient
failure/saved/reload feedback. Ready retains one small Enter prompt.

Use the image as art direction only; never substitute a generated environment,
weapon/hand image, baked numeric display or invented minimap geometry for actual
gameplay. Draw icons/lines/triangles natively. Use an unmodified Cinzel font with
its [upstream OFL license](https://raw.githubusercontent.com/google/fonts/main/ofl/cinzel/OFL.txt)
as a packaged sidecar; no Windows font redistribution. Verify font bytes/type,
retain provenance/license and load once through the existing Slate font cache.

The circular map clips the SAME authenticated1024px metric texture through a
triangle fan. Preserve original world→XY mapping, player heading, objective,
live-Allied markers and 100m/FOV/LOS-gated enemy cache. Circular edge checks also
clip markers. Grid N remains local +Y, not geographical north. No scene camera,
additional surveying, full-city or elevation claim. Tint presentation only.

World checkpoint ring changes gold/thin/128 segments; its center/radius180cm,
death ledger, entry, standing/still/safe E, Escape, save schema/prefix/transactions
and restart/load policy stay exact. Only its rendering and related colour wording
change. Do not modify action class, future-floor guard, clips, models/grips,
gun/reload/damage, NPC/bridge policy, original observer or save identity.

## Private build and early acceptance

Authenticate V10 private39 source files/descriptor and final binary, canonical758
source/703 guards/359 selected native. Freeze V10 source before changing the shared
private wrapper; preserve both user trial folders, original receipts and saves.
Allow exactly ONE implementation cpp change: includes plus DrawHUD replacement,
ring-render call and colour wording. Every header/default/reflected declaration,
config, observer and native/cooked dependency must remain byte-exact. Rebuild only
monolithic Game and reuse hash-authenticated V10 cooked payloads in NEW hud_v1.
Add only font/license/provenance sidecars, no canonical native save or recook.

Early gate: compile, ordinary Ready with font/map actually present, correct native
player/grips, no strict logs, visible readable serif text, real circular clipping
and no large panels. Inspect actual1080 and1280×720 images against the approved
concept; verify health100 displays all health segments and 2/16 vs7/2 rounds are
read directly, not sampled concept values. Run ONE existing finite checkpoint
loop unchanged on this binary to render legitimate post-three-deaths question,
save and fresh-load states and confirm input/consent/resource policy is intact.
Do not rerun the action suite for this rendering-only cpp change unless a new
input issue appears. Prior action pass remains attributed to V10, not a new test.

Stop at first compile/strict-log, missing font/map, wrong resources/marker mapping,
clipped text, unwanted panels, save-policy mismatch or GPU failure. Retain the
failed identity before a different bounded correction; no renderer/recording sweep,
invented death/pose/resource writes or relaxed original assertions. A visual-only
layout correction after viewed evidence needs a dated addendum and distinct build.

After gates pass, deliver a separate local HUD trial with the SAME V5 save prefix/
config, so user's V10 checkpoints remain compatible. Exact non-render/save-policy
source comparisons and finite fresh-load test must substantiate compatibility.
Never overwrite occupied trial/evidence. Archive rejected HUD rendering source and
screenshots under MI013 privately; keep valid functional V10 and its user saves.
Final handoff records actual images/hash/limits. No commit/push/public asset upload,
formal native/Catalog adoption, model refinement, video or performance acceptance.

## V2 — Canvas runtime font adapter after viewed V1 failure

V1 compiles/exits0/strict0 and shows map/icons, but actual1080 Ready has NO text or
numbers. Its generic read-only audit passes identity/startup only, not visual
acceptance. Installed UE5.8 CanvasItem.cpp HasValidText requires non-null UFont,
GetFontCacheType dereferences UFont; composite-only FSlateFontInfo leaves FontObject
null. The font-file-exists log was therefore insufficient. No Cinzel face-load
event occurred. Preserve V1 source/archive/log/image as stopped presentation.

Distinct V2 adds one transient runtime UFont held by TStrongObjectPtr, with the
same licensed Cinzel composite, and passes that holder into FSlateFontInfo. No
new serialized/reflected fields, native font package, font-byte/size/layout change
or gameplay change. Assert each actual Canvas draw has nonzero glyph dimensions
and log the first draw separately; also require actual Cinzel face-load and viewed
text/numbers before any checkpoint entry. Freeze V1 and rebuild method-only under
new hud_v2; all original early/stopping/visual/resource gates remain unchanged.

## V3 — viewed edge/silhouette finish, same font and gameplay

V2 actual1080 Ready now shows Cinzel, health100/all six segments, loaded2/reserve16,
live metric map and compact Enter prompt; exit0/strict0 and real Cinzel face/draw
events pass. It is not a whole-design failure. Viewed circular outlines have
visible line-join aliasing and tiny Allies look like stick figures. Distinct V3
changes ONLY Circle/Soldier drawing helpers: a vertex-alpha feathered annulus using
the already working Canvas triangle path, and filled vector squad silhouettes.
No size/placement/font/map-data/marker/resource/mission/input change or new shader/
render backend. Freeze V2, one private cpp method rebuild under hud_v3. Inspect
final ordinary1080 and720 images, then the one unchanged checkpoint loop. Stop on
original font/visual/strict/GPU/resource gates; no further art/asset sweep.
