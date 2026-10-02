# Selective weapon / animation intake results and repair gates

Date: 1 October 2026. Owner: Yupu Guo (yg745).

## Outcome

The three deliveries are preserved and selectively inspected under [the implementation plan](WEAPON_ASSET_VALIDATION_V1.md). They add candidate FP arm geometry and a large generic rifle-motion family, but **do not close the complete WWII rifle / first-person reload gap**. The tested direct-animation FP configuration is not accepted. No new SFTP release, active catalog change, live-game asset edit, commit or push was made.

Private three-member original/derivative sharing is confirmed by the owner's attestation in [the rights record](../../Assets/Integration/WEAPON_INTAKE_RIGHTS_20261001.md). Public vendor-byte redistribution and packaged-game licensing are not established by this attestation.

## Preservation and selective scope

| Delivery | Original files | Original bytes | Selection / disposition |
| --- | ---: | ---: | --- |
| ShooterStarter FPS Arm A | 607 | 3,154,499,065 | Inspect arm mesh/material/skeleton candidates. Modern rifle is not a WWII weapon selection; bundled StarterContent excluded from lab |
| D059 Rifle Pro - MoCap Pack | 1,563 | 1,944,249,213 | Inspect native Rifle_01 actions and mannequin; FBX/Maya/wrapper/cache content not duplicated into native lab |
| Assorted UE4 animation collection | 250 | 24,108,906,232 | 125 archives / 125 previews; inspect four relevant archive catalogs without extracting the collection |

All **2,420 files / 29,207,654,510 bytes** were SHA-256 inventoried and rechecked: zero changed/missing files and zero additions. All 25 previous unpublished gameplay drafts also match their existing hashes. New intake and this lab are physical LocalWorking directories; existing runtime/SFTP aliases are untouched. Originals and failed evidence are retained; no asset deletion occurred.

The isolated discovery lab contains 1,076 native files / 2,651,721,356 bytes: 290 ShooterStarter and 786 Rifle_01 packages. This broad discovery set is **not** a proposed production dependency closure. Hash-only [diagnostic metadata](../../Assets/Integration/WEAPON_INTAKE_DIAGNOSTICS_20261001.json) records staged original hashes and selected archive hashes; it is explicitly not Catalog-selected or restoration authority. Password-bearing delivery wrappers are excluded from public metadata; passwords remain in memory during archive inspection.

## Archive screening: avoid unnecessary duplicates

| Catalog inspected | Result | Decision |
| --- | --- | --- |
| Rifle Animset Pro | 298 matching native file size/CRC entries against the previously accepted original family; none different/missing | No new extraction/import for this task |
| Rifle Pro - MoCap Pack | 786 matching native entries against D059; none different/missing | Use the already delivered native D059 for discovery, not a second archive copy |
| Rifle Basic MoCap Pack | 785 matching entries, one different, none missing | Not a demonstrated new FP kit; do not duplicate/import wholesale |
| Animated Modern Civilian Hands Pack | Catalog has unarmed grab/punch/walk/throw/VR hand actions, not the required rifle-reload family | Excluded from this weapon integration scope |

These are **CRC/size screening results, not cryptographic extracted-byte equivalence**. No archive was extracted, resaved, deleted or certified fully redundant. The remaining collection names were screened for relevance, not individually loaded/tested. Cover and other generic packs remain future candidates only if a documented gameplay need arises; fantasy, melee, civilian and unrelated content is not admitted merely because available.

## Actual compatibility and deformation evidence

- UE **5.8.2-56702186** loaded all 1,076 discovered assets with zero inventory-script errors. The first inventory commandlet reported zero errors/warnings. Load success does not establish complete action contacts, playability or release acceptance.
- ShooterStarter combined arms: 68 native bones, four LODs (16,368 / 8,556 / 6,544 / 3,273 vertices), two resolved shirt/glove material slots. Left/right split meshes are separate candidates, not three production copies to retain automatically.
- ShooterStarter has seven third-person demo arm clips and seven modern weapon/attachment clips. The modern assembled rifle has 23 bones and 86,213 LOD0 vertices. Its `Reload` / magazine reload drives gun parts, **not** matching FP hand reload actions. Modern rifle geometry is excluded from the WWII choice.
- D059 has 761 native generic full-body AnimSequences. Its 70-bone mannequin shares the arms' 68 names/parents, with additional `hand_l_wep` / `hand_r_wep`. That hierarchy match is insufficient: upper-arm reference local rotation differs by about **49.85 degrees**, lower arms **32.56 degrees**, hands **18.47 degrees**. Left lower-arm twist differs **66.31 degrees**; IK helper reference transforms differ too. Never save a compatible-skeleton flag as a substitute for evaluated retargeting.
- An **unsaved, memory-only** direct-compatible-skeleton trial sampled idle, single fire and generic reload at seven phases each. V1 produced 21 sampled poses, 63 captures and six successful FBX exports. Its dark images/default near plane are retained as inadequate initial diagnostic evidence.
- V2 added daylight cubemap fill, 20/8 directional lighting, 1cm capture near plane, reference-pose control, and both +/-Y eye directions. It produced **22 samples / 88 captures**, no script errors. The commandlet reported zero errors and one deprecated `new_level` API warning. Seven V2 views were directly reviewed: reference front; idle front and both FP directions; mid-fire side; mid-reload FP; late-reload front. Texture appearance improved enough to see sleeve/glove surfaces, but shadows remain dark; this is not exhaustive material-quality approval.
- Both tested FP directions still show excessive sleeve/cuff foreground geometry and incomplete/poorly placed hands; direct generic-action poses show an unsuitable sleeve/hand arrangement. These are failures of the tested rig/action/camera combination, **not proof that the delivered mesh is inherently broken or every possible retarget fails**. No weapon was attached; grip, ADS, muzzle, reload part contact and ammo commit are untested.
- Blender **5.2.2 LTS** freshly imported three mesh and three action FBX exports without script errors. All three meshes have one UV layer, two material slots, zero unweighted vertices, zero weight sums outside .001 and zero degenerate triangles. Combined arms: 24,900 triangles, two vertices with eight influences; split arms: 12,450 triangles each, one five-influence vertex each. Influence counts are diagnostics, not an automatic failure under UE's supported skinning configuration.
- Blender exposes 67 armature bones versus 68 in UE; importer root/armature handling is not normalized for production round-trip. Imported action spans also differ slightly from native durations (see metadata). Six imported files are **not** an accepted animation re-export pipeline or native material dependency closure.

No unique production adaptation was saved. UE5.8.2 resave/fresh-load release validation was deliberately not performed on an unaccepted broad discovery set. No gameplay/input/ammo-event/performance/package/history acceptance is implied.

## Prioritized optimization / remaining dependency gates

| Priority | Issue | Bounded next work and acceptance |
| --- | --- | --- |
| P0: human weapon choice | No coherent WWII FP rifle kit; existing M1 is a one-bone appearance model, German rifle still absent | Obtain/select a licensed WWII kit with arm/world mesh, actual weapon moving parts/ammunition and matching idle/ADS/fire/reload. Do not silently use modern rifle or MP40 instead |
| P1: retarget | Arms and generic action bind poses differ | On a separate derivative, evaluate IK/ref-pose retarget with elbow/wrist/finger/twist controls. Test against the **chosen** weapon's grip targets; finite joint positions alone cannot pass |
| P1: FP view/contact | Sleeve foreground clipping and poor framing in tested eye cameras | Bound camera/arm rig placement, check full action cycle and ADS, validate sight/muzzle/left/right grips. Do not fix only one screenshot or hide required reload motion |
| P1: historical appearance | Digital camouflage sleeves and reinforced tactical gloves are visible | For retained arm candidate, bounded material/texture adaptation or replace with appropriate existing sleeves/hands; record date/unit/weapon variant before historical approval. No new detailed character-production route |
| P2: exchange | FBX root handling/timing not normalized | Pin source rate, compare sampled joint/skin results and clip seconds after any needed round-trip. Keep native UE source authoritative when no Blender repair is required |
| P2: native release | No candidate passes the required production gates yet | Select only useful assets plus recursive native dependencies; resave complete selected closure in UE5.8.2, fresh-load and regress; then verify immutable SFTP bytes and publish matching hash metadata |

The reload gap is content/semantics, not engine-version conversion: generic magazine reload cannot certify M1 en-bloc/bolt behavior. Existing M1 lacks the required independent reload parts. Modern-rifle gun clips cannot repair that absence automatically.

The [P3/P4 human decision gate](WEAPON_CAPABILITY_REVIEW_20261001.md) remains: provide/select a coherent historical rifle kit, or explicitly authorize a temporary **simplified diagnostic** first-person/reload presentation. The latter must still be adapted/tested, cannot pass final weapon/reload/history acceptance, and is not presumed approved by permission to inspect these deliveries. No additional purchase is authorized.

## Evidence and handoff

Canonical local lab: `Assets/LocalWorking/Validation/UE582/2026-10-01-weapons-v1/`; see `work_state.md` and `Evidence/ue_load_inventory.json`, `CandidateProbe/`, `CandidateProbe_v2/`. Private original inventory/preservation/archive catalogs and commandlet logs are in ignored `tmp/weapon-intake-20261001/`. The source tools are `Tools/AssetValidation/weapon_intake.py`, `ue_weapon_candidate_probe.py`, `ue_inventory.py`, and `blender_export_audit.py`.

Keep these candidates LocalWorking and unpublished until acceptance; do not scatter another full copy into SFTP or live Content. After acceptance, use the single-home migration/version procedure in `Assets/TEAM_SYNC_WORKFLOW.md`; remove only hash-verified redundant working copies, preserve originals/versions and keep an alias only when needed. No teammate restoration was tested here.
