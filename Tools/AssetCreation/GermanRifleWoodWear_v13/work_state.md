# V13 work state

2026-10-04. User authorized revision2 of paired localized-wood-wear plan.
Stage5/6 in progress; no runtime or publication authority.

Read modeling skill and its four required references, Failures/README, GP004,
GP009, V12 source/result and the actual M1/V12 comparison image. V12 form and
source textures are read-only. Raw geometry fingerprint checks are mandatory.

P0 preflight_v1: wood side UV conflicts0 at512; caps conflict with side and each
other. Separate stock/handguard side materials retain original cap bindings.
Steel outer-band isolation and guard checks are a separate early subtest.

P1 proof_v1 exit0: stock lower-butt local mask and exposed-barrel/muzzle mask,
8 actual PBR/unlit/alternate-light views inspected. Very restrained appearance,
no grid, tube whitening or wood/metal contamination observed. proof_mask_v2
actual three inspected mask views establish surface placement. Face/vertex
indices stored in build_report.json. No material correction yet.

Technical diagnostic failure retained: proof_mask_v1 loaded no unused mask
images (unreferenced masks are absent after blend reload), making invalid black
mask renders. Blender resolved relative render paths on C:, unlike the report
writer. Three PNGs were moved back into the intended private proof_mask_v1;
JSON was already there. Fixed absolute paths, explicit mask PNG loading and
minimum-mask assertion; valid proof_mask_v2 kept separately. No visual pass
is claimed for proof_mask_v1, even though its process exited0.

Ownership_v1 exit0: guard sides, band outer shell, external butt-plate cap
each have0 UV conflict pixels at1024. finish_v1 source multiview is retained;
wood-wear contrast is too weak (raw colour nearly equals base). One permitted
coordinated local contrast correction raises bare-wood colour relative to its
unchanged grain and darkens/roughens existing steel dirt masks. No new masks,
geometry, light changes or mark-count increase. Frozen before-source retained.

Finished bounded pass: finish_v2, audit_v1, fresh_details_v1, repeat_v1,
repeat_audit_v1 and comparison_v1 all exit0/pass. Actual source16/fresh10 and
matched sheet inspected.24 meshes/24,466triangles,14 materials/30primitives,
36 embedded images. Original6 normal PNG payloads retained exactly; fresh
per-material counts/areas match. Clean repeat attribute/PNG equality passes,
whole GLB differs (cause unproved). Baseline files and five comparison inputs
unchanged. No task Blender process remains, no interactive launch.

Review candidate: private finish_v2/GermanRifle_CoordinatedWear_V13.blend/.glb.
GLB SHA76c557b3334c8b9a7ee178b33783376642b5c8a176a37e662ab7203714c00a81.
Final evidence: presentation_v1/m1_v12_v13.png; fresh_details_v1/fresh_barrel.png.

Appearance limitation: whole-view improvement over V12 is small; wood wear is
light and steel still looks clean under the studio. Mask/attribute success
does not establish the requested M1-like/coherent aging target. Unselected
candidate, user review pending, V12 remains intact. No third adjustment in
this work package. UE mip/runtime/history/contact/rig/rights remain open.

Stop and show result. No game, source M1/library, SFTP, Catalog, cloud or
commit/push. Paired result documents hold the full factual record.
