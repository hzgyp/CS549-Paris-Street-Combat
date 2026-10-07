# Kar98k V8C standalone mechanical candidate

2026-10-03. Within user-approved local receiver/sight/muzzle rebuilding, after GP007's two early gates stopped. Read GP001–007, V8/V8B and museum top/side reference. Original V7 and stock/sling/game remain unchanged. **No integrated rifle is produced or selected in this step.** This different candidate authors analytical mechanical meshes independently, not source cutting, welding, covering or automatic material classification. It does not retry the failed patch.

## Scope / order

Build independent receiver rings/open lower rails/bolt body/rear cap/safety/extractor, tangent rear sight base/leaf/slider/notch/hinge, and hollow muzzle barrel/front blade/band. No replacement handle/ball, stock or sling. Use source's provisional1.105m frame and observed axial trend as rough placement, museum proportions as visual guidance (not certified drawings/issued variant). Receiver and sight dimensions may differ from the imperfect generated base; placement/wood interfaces and operating handle remain unverified. Make separate named meshes and intentional pivots, measured chamfers, own UVs and standard scalar glTF steel materials, no reused commercial M1 textures/procedural shader promise.

First render untextured analytical parts alone (both sides, top, bottom, oblique and each assembly close-up). Early acceptance = manufactured curves, visible receiver opening/hollow muzzle/notch, no stray fins or global cover plate; each solid itself has paired edges, outward positive volume, finite dimensions and declared UVs. Then standard PBR, packed blend/GLB, fresh import measurements/multiview, clean rebuild byte comparison, prior hashes. Sources `Tools/AssetCreation/GermanRifleTopologyV8/`; outputs new `parts_clay_v1`, `parts_finish_v1`, `parts_repeat_v1`, `parts_audit_v1`. Never overlay output on original or remove source geometry to pretend integration.

## Stop / rollback

Observed first clay defect: sight wedge side quad indices formed crossed faces (black underside/sawtooth edges), even though each edge had two incident faces and signed volume positive. Preserve first clay/output/source snapshot. The **one** structural correction fixes wedge's six quad loops, adds convex-face corner orientation audit, and outputs `parts_clay_v2` before any PBR. No size/fit sweep or source-rifle edits. If this remains invalid, stop.

At most one structural correction for a specifically observed shape/mesh defect. Stop if validity or visual manufacturing gate still fails. Otherwise deliver **unselected standalone parts**, explicitly not complete rifle/history/operating bolt/reload/game/production acceptance. Replacing the old mixed mesh still requires a separately validated interface method or manual art integration; do not resume the failed cuts/hulls/maps. Old V7 is unchanged rollback. No cloud/spend/UE/SFTP/Catalog/commit/push. No unrelated feature work.
