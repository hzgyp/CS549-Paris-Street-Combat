# Kar98k bounded Blender adaptation — round 1

2026-10-03. Local-only supplement to German rifle pilot V1, not M1/UE/SFTP selection. Cases read: FP001 full analysis and stopped Lux3D character pilot; change is a single rigid prop, immutable base, fixed complementary cameras, at most two coherent repairs. Numerical import is not visual acceptance.

## Evidence and early decision

Aholo task3919866 used20 gifted credits, balance260→240. Base GLB17,173,888 bytes, SHA `a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60`; ZIP13,923,303 bytes preserved. One mesh299,479 triangles, one UV layer, two packed2048² images. Incoming v1 had invalid diagonal-pose top/quarter framing: retain it as camera diagnostic, not shape evidence. Incoming v2 uses principal-axis pose alignment, approximate1.105m length, six neutral and four PBR views. All ten views must be inspected before final claims.

Viewed dual sides/top/quarter: continuous recognizable stock, curved wrist, slim fore-end/exposed barrel, visible guard opening and downturned handle. Primary form is sufficient for a **bounded NPC-world candidate adaptation**, not finish acceptance. The top receiver and sight are rounded/soft; muzzle/front sight has artifacts, metal is too shiny/light, museum replacement sling remains. No precision FP/historical kit acceptance.

## Exact round 1

1. Start from raw GLB in a clean5.2.2 scene; apply the fixed incoming-v2 normalization matrix, not a new proportion edit. Guard original SHA before/after.
2. Extract only the visible right-hand handle protrusion using a named spatial selection recorded in source. Preserve its UV/materials; remaining body/receiver/stock/sling are not rebuilt. Cap only new cut loops where possible; put pivot at the reviewed handle attachment. A handle is not the complete independent operating bolt, so record that limitation even if motion is demonstrable.
3. Weld near-identical positions in working copies, retain loop UVs, decimate toward30k total, smooth broad forms. No texture rebake or hidden cloud calls; original base is immutable. Do not claim raw UV-seam index boundaries are all geometry tears. Report actual post-export geometry risks.
4. Retain generated color/metallic images but temper gloss with explicit glTF-compatible scalar roughness0.58; do not introduce unsupported correction-node chains or bake/edit reference photos. No material-only hiding of shape errors.
5. Save a packed named candidate .blend, export named GLB with body and handle parented under a root, then fresh import and compare names, hierarchy, dimensions, triangle count, UV/images, finite coordinates and obvious seams. Keep fixed v2 cameras for before/after side/top/quarter evidence. Also inspect enlarged handle area in rest/displaced state; motion demonstrates digital separation only, not a real mechanism or matched reload.

## Stop / rollback

Stop if extraction harms stock/receiver/contact, loses an open guard/shape, leaves visible holes, exceeds budget without acceptable appearance, or two coherent repairs fail. Preserve every candidate/evidence, select none formally. Do not silently downgrade the required complete bolt into a passed full kit: a partial handle-only candidate keeps that gap explicit. No manufacture-level internals, source character changes, cloud resubmit, Unreal launch, SFTP/Catalog update, commit or push. Local candidacy may be delivered for review with remaining form/part limitations; it is not a completed production asset.

## Round 1 reviewed / bounded round 2

Round1 produces a body plus separate exterior handle, authored28,897 triangles. Fresh GLB inspection has28,884; source export reported `Mesh geometry_0 is not valid`, although both fresh meshes validate unchanged. Do not erase that warning or claim source/export parity. Neutral dual sides/top/quarter preserve overall silhouette and open guard, but top receiver/sight softness and original welded topology risks remain. The complete operating bolt is **not** separated; museum sling stays attached.

Round2 changes only explicit working-mesh validation after decimation and before measurement/save/export, recording what it removes. No new geometry design, selection-region sampling or cloud task. Reproduce a second independent output from raw base, compare exact authored/export triangle count/names/hierarchy/scale/UV/image availability; inspect frozen multiview and rest/exploded handle diagnostic. Stop at this two-round cap. Deliver only a local candidate with limitations, not a production acceptance or complete animation-ready gun.
