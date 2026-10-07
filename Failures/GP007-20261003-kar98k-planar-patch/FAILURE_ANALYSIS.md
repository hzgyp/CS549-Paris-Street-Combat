# GP007 — non-planar receiver boundary

2026-10-03. V8 original-edge proof selected 1,884 connected steel faces with 156 correctly paired boundary edges, excluding wood/ball/sling. Five cyan views were inspected. The next **required** projection check found three crossing edge pairs (51/54, 94/96, 94/97). A simple 3D loop is not necessarily a usable planar polygon. Blender returned shell exit 0 despite the Python AssertionError; the actual assertion failed.

No faces were removed/rebuilt, no export/material change occurred, no contour retuning is allowed. Preserve `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-topology-v8/interface_v1/`, `profile_measurements.json` and immutable `profile_probe.py` as evidence. They are private unfinished work, not selected assets.

The separately documented V8B intrinsic alternative also stopped before authoring: diagnostic region Euler=1 and boundary exactly156, but physical edge77542/77546 has **four** incident faces151520/180930/180935/180936. Endpoint coordinates are exactly identical across UV copies (not a quantization artifact). Therefore this region is not a manifold disk; no harmonic solve/remesh ran. `intrinsic_failure_diagnosis.json` preserves exact faces/coordinates. Do not retry tolerance/contour changes, remove faces blindly, or call Euler=1 sufficient.

Both source-dependent repair candidates are stopped. A distinct safe output may be standalone analytically authored mechanical subassemblies, **not superimposed onto or cut out of the old rifle**. They can demonstrate manufactured geometry but do not establish interfaces, whole bolt/wood integration, or a usable replacement rifle. Original V7 remains the sole unchanged input/checkpoint.

## Associated standalone authoring defect

V8C initial gray sight had crossed wedge side quads and black undersides. Its per-solid paired-edge/positive-volume test did not detect the face-loop defect. Keep `parts_clay_v1/source_before_correction.py` and eight original gray images. The one documented structural correction orders six wedge quad loops correctly and adds corner-orientation assertions for the analytical convex faces. New `parts_clay_v2` passes the strengthened check (24 meshes/10,104 triangles), eight images actually inspected. This fixes the independent part defect, **not** the original source's topology or rifle integration. No original silhouette/material fitting is implied.
