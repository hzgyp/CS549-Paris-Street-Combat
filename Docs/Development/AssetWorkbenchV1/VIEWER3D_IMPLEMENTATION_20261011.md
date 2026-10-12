# 3D and animation viewer — 2026-10-11

Local implementation prioritizes current characters, first-person geometry, rifles, rifle animation clips and the candidate mine. Keep original files, native assets, rigs, weights and accepted finger overrides unchanged; create private viewing derivatives only.

Apply the read-only export/deformation checks from blender-character-workflow. Read MI030 (GLB versus UE appearance), MI033 (capture completion), and existing FBX repair/export scripts. Add orbit, zoom, pan, reset, wireframe, clip selection, play/pause, timeline and speed with Chinese/English labels. Identify source version and any absent native gameplay overrides. Never manufacture clips for static models.

Serve only registered self-contained glTF 2.0 GLB, at most 128 MiB, after hash/format/resource validation. Reject external dependencies and arbitrary paths. Load on demand and release GPU resources on navigation.

Early gate: render the exact rifle/mine first, then inspect existing character and animation exchanges for bones, weights, materials, axes, duration and deformation. Stop faulty or incompatible exports rather than disguising errors with whole-object motion. Fresh-import exported characters and inspect multiple action frames. Verify real WebGL controls and rendering plus negative API boundaries. Browser acceptance does not establish new UE acceptance.
