# Paris map grid implementation

7 October 2026. The user requests a black and white planning map that preserves world distances and maps selected cells back to the existing Paris level. Existing positions remain test coordinates. This work creates a conservative candidate tool; it does not choose mission locations or modify the adopted characters, weapons, AI, collision, saved navigation or map.

## Existing evidence and failures read

Read HANDOFF.md, current Git state, Failures/README.md, ML001, ML003, ML006, ML007, ML008, ML010 and ML011. The completed pure survey contains 27,836 navigation polygons and 28,684 scheduled representative/connection observations. The formal verification covers three local routes. Neither is per-cell occupancy evidence.

| Case | Change in this attempt | Early check preventing recurrence |
| --- | --- | --- |
| ML001 and ML006 | Keep exact polygon identity, detailed surface height, native collision floor and separate cell height. Never flatten stacked surfaces or use averaged vertices as ground. | Known city surface and stacked surface samples must resolve the specified polygon with XY drift at most 0.01 cm. |
| ML003 | Await natural navigation unlock and verify the disposable registered bounds before rebuilding. Export saved navigation before the temporary expansion. | Active/exported tiles match; invalid records are zero; original map and 703 guards remain exact. |
| ML007 | Reuse only the authenticated static vehicle isolation functions. Preserve all collision and transform fields. | Before/after snapshots equal and simulation is disabled; subsequent snapshots remain exact. |
| ML008 | Classify the native supporting component and mesh. Package membership alone does not prove a usable city surface. | Road support is identified from actual component/mesh; Landscape, BasicShapes and unclassified proxy supports remain excluded or unknown. |
| ML010 and ML011 | Keep geometric occupancy, local connection, squad-policy arrival and combat results in separate fields. | Formation or shooting negatives must not turn an entire terrain polygon into a physical obstacle. |

## Grid and display contract

Use world centimeters internally and one meter per cell. Align X and Y edges to whole meters. Column increases with +X and row increases with -Y. Cell-center mapping is `X = Xmin + (column + 0.5) * 100`, `Y = Ymax - (row + 0.5) * 100`. Z is the native measured standing feet height of that specific surface, not a rounded floor number. Export foot coordinates and a separate body center for the selected capsule profile. A white cell admits its center, not every arbitrary position in its square.

Every XY cell starts black. White requires an exact navigation surface, walkable native collision support and an unobstructed upright formal-size capsule. Maintain reason codes for physical obstruction, unsupported surface, non-city/unknown support, saved navigation absence, coarse-grid omission and unmeasured data. Display only black and white; explain reasons in the inspector. Do not call unknown space a proven physical obstacle.

Preserve all candidate surfaces at the same XY. Order them by measured Z for inspection and label the order as overlapping surfaces, not building floors. Cross-surface navigation connections remain explicit. A visual layer is a viewing choice and does not establish a physical floor or a stair.

Record full-survey versus saved-map navigation independently. The former used expanded disposable bounds; the saved bounds are about 420 by 420 meters. The user has not selected a final playable boundary. The tool must allow inspection of the surveyed city beyond the saved bounds while the current-game filter excludes cells without exact saved navigation evidence. Do not save an expanded volume as a shortcut.

## Native geometric sampling

Add a new disabled Editor-only ParisGridSurveyV1 helper. Preserve both existing survey helpers and their binaries. In a unique owned editor entry, remove production gameplay actors from the unsaved world, retain all environment blockers, freeze vehicles with collision parity, and export saved navigation. Expand and rebuild only this disposable world using the established natural-unlock sequence.

Rasterize polygon interiors at grid centers, retaining polygon references. Sample each candidate through the installed `GetClosestPointOnPoly`, native CharacterMovement floor queries, and Pawn-channel capsule overlap at radius 34 cm and the maximum observed formal half-height 96.23316 cm. Use step 45 cm and slope 44.7651 degrees. Record the actual supporting component and mesh. Static sampling is not a played movement episode. It never repairs or retries prior failed locomotion, formation or combat cases.

For adjacent admitted centers, require a directed navigation connection on the specified surface and collision clearance along the connection. Keep height/step limitations and missing links explicit. Conservative gaps at one-meter resolution remain black/unknown and are listed for later local refinement rather than silently bridged. No diagonal corner cutting is permitted.

Purpose filters are geometric candidates: generation needs a declared assembly-space footprint; task placement needs a declared local operating-space footprint; encounter placement needs approach space and measured sight lines between candidate positions. These parameters remain editable and are not final mission rules. The inspector distinguishes geometry from the existing local formal-body, squad and combat evidence. White in a purpose filter does not certify an unspecified future mission or full squad behavior.

## Deliverables and execution order

1. Save this plan and synchronized Chinese review before source authoring.
2. Implement grid coordinate/raster/reason schemas and synthetic checks for round trips, stacked surfaces and boundary behavior.
3. Build the independent native helper. Run a small admission batch containing a known road, blocking space and stacked surface before the broad finite grid batch. Stop on API, isolation, height identity or collision parity failures.
4. Generate the full finite candidate grid, native reason records, surface layers, connection graph and geometric purpose filters. Retain counts and unknown areas.
5. Create a private local browser tool with zoom/pan, surface inspection, purpose and saved-navigation filters, coordinate selection and draft JSON export. Store derived images/data only under ignored private Evidence/MapGridV1. Public source/docs contain no commercial geometry or screenshots.
6. Audit masks and mappings independently. Select a small deterministic round-trip test bank from white centers, including a height/overlap case where admitted. Verify native standing and directed movement in a unique unsaved UE entry. These are test sites only.
7. Inspect the actual browser view and exported black/white figures. Publish local result documents and a handoff checkpoint with exact limitations, native exits, logs and protection evidence.

## Acceptance and stopping conditions

The early acceptance requires coordinate round-trip error below 0.01 cm, exact-surface XY error at most 0.01 cm, native floor/support records, retained stacked identity, zero false-white synthetic obstacles, source/helper/703 protection exact and normal owned exit with strict log zero. A negative terrain sample is a black cell with its reason; it is not a global API failure.

Stop the native batch on process ownership conflict, API/schema mismatch, missing required surface identity, unexpected production actor, changed environment collision/transform, changed protected bytes, navigation lock timeout, strict log error or wall deadline. Preserve the unique entry and archive the cause. Do not weaken tolerances, move failed points, relabel unknown space or rerun failed identities to obtain a pass. A different measurement correction needs a dated addendum and a new identity. Repeated UE negative movement sites are not retried under this plan.

Completion requires the finite grid batch and data audit, usable coordinate-selection tool, inspected black/white outputs, a bounded UE mapping check, and a record of all gaps. Full per-cell formal-role walking, AI formation repair, combat balance, final layout, FPS and course acceptance are outside this work package.

## Compilation correction

Build native_v1 fails before any native sampling because the condensed JSON policy header is absent under StrictIncludes. Read ML012. The next unique native_v2 build explicitly includes the installed header and uses float capsule constants. No acceptance rule changes; the original early controls still govern entry.

Early_v1 then stops before samples because the editor actor API deliberately excludes the RF_Transient probe. Native_v3 adds a world TActorIterator inventory including transient actors and superclass contamination checks. Require the same one-probe/zero-controller/zero-production standard in early_v2. Geometric sight pairs use two-way native Visibility traces at a declared 140 cm eye height and 5/10/15/20 m candidate distances; they are not formal AI vision or gun transactions.

Early_v2 crashes at the first floor query after successful isolation. Native_v4 explicitly binds the Editor probe's movement component to its capsule and validates cached owner/updated component before calling the installed floor API. Early_v3 uses the unchanged road/stack/blocker controls. Native sampling of saved-navigation links precedes disposable expansion, so current-map connectivity is measured against the actual saved navigation rather than inferred from its bounding box. Freeze all preparation sources per entry.

## Separate navigation collections

Read ML013 before deriving the accepted artifact. Full_v1 completes and independently audits all native requests; its first derived image fails because cross-scope matching wrongly requires equal Recast surface Z. Derived_v2 keeps saved and expanded cell/link collections separate. A current-navigation white center must come directly from its saved native record. Preserve actual coordinates and source IDs in both collections. Cross-scope sight association requires equal XY, identical support and actual feet within0.01cm, with the original ray endpoints retained. No native record or acceptance tolerance is changed and no native batch is rerun.
