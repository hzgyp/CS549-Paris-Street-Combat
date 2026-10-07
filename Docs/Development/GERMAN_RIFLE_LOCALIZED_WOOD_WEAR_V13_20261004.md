# V13 — localized wood wear and coordinated barrel/steel aging

2026-10-04. **Implementation authorized by the user's “可以，按这个修正细节”.** Continue revision2 as a private independent V13. Their expected “basically usable afterwards” is an appearance target, not game integration permission. Chinese review: synchronized `_ZH.md`.

Revision2: user additionally requires barrel aging to avoid old wood paired with new steel. The prior no-steel-material-edit constraint is superseded for barrel and adjacent exposed hardware only; steel form/structural normals/mechanism/actions remain protected. Execute new preflight_v1, proof_v1, finish_v1 and audit_v1 identities in order. No geometry work is authorized.

## Contract and baseline

Retain V12's approved-direction form and reused M1 grain; add legible wood scratches, spatially credible abrasion and matching barrel/exposed-steel aging. Materials should read as one normally used maintained weapon, not identical colours or equally large damage patches. Ordinary game-prop finish, not photorealism or micro-mechanical refinement. Protect24parts/24,466 evaluated triangles/~1.1073m, vertices/topology/UV/mesh normals/modifiers/hierarchy/transforms. Do not edit steel geometry/mechanism, rigs/actions/grip, sculpt/indent geometry or call cloud/spend. Revisit Blender modeling skill stages5–7 only.

Baseline private `20261004-m1-texture-v12/finish_v1/GermanRifle_M1Texture_V12.blend`; GLB SHA862baf5ab6afa6f977e373d4710fce1e3bf6964e51e7e6483424f15bc9424193. M1 local portable scene is the visual analogue, not a new internet reference or exact native UE appearance. Derivative wood/barrel/exposed-steel textures/materials and, if required, material assignment of existing end faces may change; log those differences rather than claiming every datum unchanged. Steel structural normal is retained as a read-only underlying layer if fine detail is composed. Source assets read-only.

## Evidence-driven appearance design

Actual M1/V12 sheet shows irregular lighter wear at stock perimeter/grip neck/exposed wood–steel edges and readable scratches on otherwise intact planes. V12's clean M1 patch preserves grain, not target-local wear positioning. Do not repeat whole-atlas stretching or global brightness adjustments. M1 informs colour/mark morphology; actual German geometry determines location, not M1 baked shape normals/shadows.

| Target zone | Desired treatment | Reject |
| --- | --- | --- |
| Butt perimeter/lower corners/exposed wood beside butt plate | Interrupted pale-brown bare wood and small impact rubs | Uniform white perimeter or marking metal |
| Stock upper ridge/lower edge/convex shoulder | Narrow irregular exposed-edge islands | Every convex face bright or continuous highlight stripe |
| Grip neck/transition | Slight darkening/local polished roughness with sparse rubs | Large yellow peeling substituted for handling polish |
| Fore-end/handguard exposed sides/ridges | Sparse longitudinal/oblique scratches and protrusion wear | Heavy wear inside channels/under covered steel bands |
| Exposed wooden lips near metal/bands | Restrained local contact abrasion | Outline every boundary or paint wood strokes onto metal |
| Broad stock planes | Mostly intact grain with sparse varied scratches | Mirrored identical sides, all-over cracks/noise |

| Exposed steel zone | Desired treatment | Reject |
| --- | --- | --- |
| Barrel exterior | Restrained irregular tonal/roughness variation, sparse longitudinal/oblique scratches | Factory-new uniform tube, all-silver whitening, repeated rings |
| Muzzle outer rim/front-sight protrusions | Slightly stronger localized bluing abrasion/dark-grey exposed steel | Whole white rim, bore/geometry edits, exaggerated soot or heat tint |
| Bands/butt-plate corners/guard exposed ridges | Sparse corner rubs/scuffs coherent with adjacent wood | Pristine hardware beside aged wood or every edge equally bright |
| Exposed receiver/bolt-handle contact surfaces | Restrained handling polish/scuffs/dark grime, existing structure legible | Redrawn structural normal/geometry or all-over rust |
| Recesses/seams/covered areas | Sparse dark oil/dust patches; covered barrel relatively intact | Black mud everywhere, strongly bright recess wear, cross-substance marks |

Maintained used weapon, not an abandoned rusted gun: wood abrasion can be more conspicuous, steel marks finer/more restrained. Match use level, not brightness. Keep dark-grey/blued identity and structural normals; localized worn finish slightly lighter, never pure white. Separate scratches/grime masks from wooden bare-grain masks. Exposed substrate stays metallic; only actual small dirt-coated regions adapt coating response, never globally reduce metallic to fake age. Polish and dirt have different roughness changes; retain structural normals under optional weak micro-scratch detail. No major rust/pits/muzzle soot/rainbow heat bluing.

Three layers: retain V12 grain/colour/fine normals; add shallow sparse variable-length/orientation scratches; add localized edge abrasion revealing lighter raw wood. Handling polish may be darker/smoother, whereas raw scratched wood is generally drier/rougher. Use coherent masks for BaseColor/Roughness/tangent Normal, wood Metallic0. No mesh-normal/geometry edits. Suggested initial scratches10–40mm long/~0.8–1.5mm wide, edge islands~1–4mm wide; these are creative starting values, not verified measurements/quality thresholds. Judge at matched whole and close view distances, not a scratch quota or wear-area score.

## Execution order after user resumption

P0: inspect actual UV occupancy/seams for Wood_ContinuousStock and Wood_UpperHandguard. Source review confirms shared wood material, longitudinal-U/ring-V sides and circular capUV: overlaps are a risk, **not an executed UV-overlap test**. Use separate wood texture sets without changing UVs; existing overlapping end faces may receive separately recorded derivative material assignments, including per-end isolation if needed. Preserve consistent colour. If isolation cannot express position under these constraints, stop, not averaging conflicting texels or cutting/re-unwrapping.

Also inspect actual steel material/UV reuse for Barrel_Donor_Tapered, Muzzle_Donor_Insert, bands/plate/guard/receiver/bolt-handle. Object/existing-face ownership constrains masks; isolate derivative material/images where shared UV would duplicate a mark, without steel UV/topology edits. Muzzle abrasion must not duplicate on mid-barrel/sight/guard.

P1: prove one real butt lower edge/adjacent plate-exposed wood region first. Record object/face indices; use actual surface adjacency/convex-versus-concave relationships/geodesic or surface-distance masks, restricted by the stated wear zones. Curvature is only an aid, not a substance classifier or a rule to wear every triangle/UV edge. Inspect unlit mask/base colour plus fixed studio close-up and reverse/underside/seam. Earliest failure: flat areas wholly pale, steel contamination, mesh lines, erroneous handguard duplication, UV white line or off-edge mask. Do not add further marks after a failed localization proof.

Separate early steel proof: a short exposed barrel section with sparse marks/variation plus outer muzzle or band ridge. Require visible controlled aging without tube whitening/ring seams/wood contamination/lost structural normals; failure stops expansion to remaining steel. This does not reopen form construction.

P2: apply the proven mechanism to selected wood/exposed-steel zones, asymmetric sides, surface/mm-scaled scratches rather than uniform UV random lines. Existing M1 clean scratch patches may be reused only after D/N/ORM review and source-shape/AO removal; if none is clean, bounded reproducible curve masks, no cloud texture painting. Prefer2048² target wood sets for newly authored mark pixel density, not an assertion that upsampling the original723×434 patch creates grain detail. Add sparse localized steel abrasion/scratches/grime at existing resolution where possible; material isolation is not automatic permission for a high-resolution set per part. Retain read-only underlying steel structural normal, record optional micro-normal composition, outside-scope maps unchanged. Log sizes/material slots/GLB primitives/output cost, avoid unnecessary4K/runtime layers. Bake ordinary D/ORM/tangent Normal without studio light/shadow. No exported dependence on Blender Pointiness. Handle normal handedness/mirroring/padding and inspect reduced/mipmap-scale seams. Durable new script records all coordinates/parameters/seeds if used.

P3: compare M1/V12/V13 whole/stock/grip/handguard/barrel/muzzle/receiver steel with fixed camera/lights/exposure/metre scale; inspect both sides/top/bottom. Unlit colour and alternate side light distinguish actual texture wear from reflections. Whole-weapon acceptance must assess steel–wood age consistency, not only separate flattering close-ups. Permit one diagnosed material correction only (too white/dense/wide/seamed); if still wrong retain unselected V13 and stop, no threshold/noise/microdetail sweeps or lighting tricks.

P4: export_apply=True, embedded images; fresh GLB checks24names/24,466triangles/dimensions/UV/mesh normals and correct new wood/steel/end-face bindings. Verify unchanged underlying structural normal/outside-scope map hashes; list permitted D/ORM/micro-normal deltas, no longer assert all steel maps unchanged. Separate allowed material changes from forbidden form changes; use existing declared export attribute tolerances, not false bit-exact normal claims. Inspect actual imported six views plus stock/handguard/barrel/muzzle close-ups. Clean rerun and attribute/embedded-image checks; differing whole-file SHA is reported without invented cause. Deliver matched M1/V13 sheet for human approval, then end appearance iteration.

## Acceptance and stop

At ordinary whole view, recognizable used wooden stock with form/grain dominant, not a pale damage pattern. At close view, a few legible scratches and stronger wear on actual exposed ridges/corners/contact zones; restrained recess wear, asymmetric sides and coherent reverse/underside quality. Barrel/bands/adjacent exposed steel must not look factory-new beside old wood; use subtle metallic wear, not equal-colour whitening. Wear persists when light rotates, without grid/UV white rings/floating overlays/wooden strokes crossing steel/excess normal relief. Form/size/grain base/steel identity/underlying structural normals retained. Numerical checks do not approve appearance. Stop once user approves this ordinary prop appearance; no added screw/letter/major rust/dent/bolt polish. Historical/mechanism/contact/UE/runtime/rights remain separate, not grounds for unrelated expansion.

## Deliverables, storage and rollback

Source `Tools/AssetCreation/GermanRifleWoodWear_v13/`; private output `Assets/LocalWorking/Experiments/GermanRiflePilot/20261004-wood-wear-v13/<new-unique-stage>/`. Existing planned identities remain despite expanded material scope. Preserve failed identities/masks/parameters; produce standalone blend/GLB, wood/steel D/N/ORM/masks, reproducible script, M1/V12 comparison and fresh audit, non-release hash metadata recording material deltas. Code/Markdown/hash Git only, commercial bytes/images LocalWorking; do not copy2.2GiB library/26GiB city. On failure stop using candidate; V12 remains intact, no overwriting restoration/deletion.

No automatic UE/game/reload binding, SFTP/Catalog/commit/push. MW2 project-use/derivative-sharing rights remain separately pending. Later integration/rights acceptance then private SFTP publication follows project single-storage/remote SHA verification/redundancy cleanup, never publication based on a beauty image.

## Failures reviewed and proof of changed mechanism

Failures/README, GP004 and GP009 were read before authoring. GP004: no XYZ wood/metal envelope; known wood object ownership plus actual face adjacency/convex-edge proof. GP009: applied-modifier export and actual fresh-import views, semantic/image equality not whole-byte equality. V12 result: clean surface patches lack spatial wear and old overly glossy response failed; preserve corrected baseline response and avoid whole-body varnish. This attempt changes location ownership, not the accepted form. Actual tests are recorded only after execution; early localization failure stops expansion, and one causal visual correction is the limit.
