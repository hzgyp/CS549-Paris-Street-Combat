# V14 work state — 2026-10-04

User correction: dark coated wood, not additional wear. Plan EN/ZH written.
Read skill and its four required references, failure index, GP004/009, V12/V13
results, prior actual matched comparison. Stages 5–7 active, geometry frozen.

Read-only diagnostic_v1 exits0. Blender sRGB image pixel (100,100) is encoded
[37,20,10]/255, matches PNG Pillow pixel with vertical flip; not linear colour.
V13 wood mean encoded RGB .207/.134/.086; roughness mean .640, standard IOR1.5,
specular .5, no clearcoat. Large pale reflections remain in matched views.
Implement sRGB→linear pigment tint→sRGB, existing masks only, restrained satin
roughness; all existing normal and steel images protected. Source V13 SHA pinned.

preview_v1 exits0, five actual pictures inspected. Unlit wood is deep warm
brown with retained grain, but PBR receiver/handguard have excessive broad white
reflections; this fails the early finish criterion, not the colour mapping.
Frozen source retained there. Sole causal correction: specular IOR level .5→.18,
roughness mean approximately .43→.52; no base colour/mask/light change. Verify
KHR_materials_specular survives GLB before delivery. No third adjustment.

Completed: finish_v1, audit_v1, material_audit_v1, repeat_v1/repeat_audit_v1 and
comparison_v1 all exit0/pass. Source11/fresh8/matched sheet plus individual
stock/receiver actually inspected.24meshes/24,466triangles/36PNG, all30protected
PNG payloads and11nonwood material definitions exact. Fresh specular extension
preserved. Clean rerun attributes/36PNGs match, wholeGLB differs/cause unproved.

Candidate finish_v1/GermanRifle_DarkWood_V14.blend/.glb, GLB
9ca471321bd2b684d324cd094eb50d2e3ae0b0adaf174f3ea19dd8b30b0d3c80.
Same-camera review presentation_v1/m1_v13_v14.png. Colour visibly deeper/warmer,
but grazing white response/handguard/underside and stretched grain remain.
Stop for user appearance review, no third correction. All task processes ended.

Metadata-only initial inventory assertion failed: Windows text stdin inserted
CR, Git quoted those paths. Original inventory source retained diagnostic_v1;
binary NUL-delimited Git check corrects it. No model/appearance change.
Output and evidence stay ignored LocalWorking; no game/native/sharing/push.
