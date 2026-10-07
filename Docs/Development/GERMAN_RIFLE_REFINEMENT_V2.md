# German rifle local refinement V2

2026-10-03. Owner yg745. Authorization: Yupu accepts the base direction and requests continued refinement. This resumes local prop authoring, not cloud spending, M1 reload, UE selection, SFTP/Catalog publication or Git commit/push. Previous one-base/two-repair outputs remain immutable historical evidence.

## Reviewed cases and changed mechanism

Read HANDOFF, Git status, Failures index, GP001 and FP001 analyses, the pilot contract/adaptation/result, and the Blender modeling skill and its four references. GP001 established color/UV damage after weld/decimate and an incomplete jagged handle extraction. FP001 warns against substituting numerical checks for actual visual review. Reinspect the same museum full sides and top/underside details, not a new invented rifle variant.

Start from the original `kar98k-base-v1.glb`, SHA `a8ccfed78eed6da13de2070b86cec6bd32357218dd0c0cfb4efe6ae512387b60`, using the fixed incoming-v2 normalization. Retain broad wooden silhouette and original UV/color data. No global welding, remeshing or collapse decimation. Replace the soft exposed receiver/bolt/sight/muzzle zones with separately named smooth, beveled exterior geometry. Use exact plane clipping with interpolated loop UVs at any retained source boundary, rather than centroid selection and jagged hole fills. Document contact/interface geometry; do not keep visible coplanar duplicate metal underneath replacements. Whole visible bolt and its handle share a semantic assembly; this is exterior game geometry, not internal mechanics, an operational firearm design or weapon-specific reload animation.

## Contract / storage

- Target: polished smooth German NPC world-prop refinement, not first-person kit. Low-poly is not requested. Approximate 1.105m silhouette follows the same museum specimen; dimensions are visual estimates, not manufacturing data.
- Preserve wood stock, handguard, guard opening and museum sling if inseparable. Rebuild only the bounded soft exterior metal zones; distinct dark blued steel, readable bevels, smooth barrel and connected bolt handle/knob, front/rear sights. Museum hood/rod are missing; no invented historical approval or claim its replacement Sten sling is German issue.
- Keep this detail master below 350k triangles. The previous 30k runtime target remains a later UV-safe LOD/UE-performance gate, not permission to repeat destructive reduction or label a high-poly master game-ready.
- New source: `Tools/AssetCreation/GermanRifleRefinementV2/`. New physical output: `Assets/LocalWorking/Experiments/GermanRiflePilot/20261003-refine-v2/`. No copy or overwrite of old source/output identities. References are reused read-only.
- Deliver deterministic script, packed editable blend, self-contained GLB, exact metrics/hashes, fixed dual-side/top/bottom/quarter views, and enlarged receiver/muzzle details. Fresh GLB import, source reproduction, UV retention and protected game hashes are required. Named bolt parenting can be diagnosed by displacement; no character reload is authored.

## Order and early acceptance

1. Verify raw source and 43 native + 7 action drafts; inspect fixed close views and source coordinates before cutting.
2. One coherent structural candidate: retain textured source outside bounded metal zones; build connected exterior assembly, sights and smooth tube surface. Immediately export/import and inspect neutral side/top/quarter and close receiver/muzzle views. Stop/reject if wooden silhouette is cut away, guard fills in, metal floats, source artifacts remain conspicuous, or contact cannot be explained.
3. One bounded correction maximum if early evidence identifies a concrete local defect. Preserve its first output. No parameter sweep, more cloud calls or stock reconstruction campaign. If structural review still fails, record failure and stop; do not disguise it with textures.
4. Inspect material and unlit-color views for triangular patches, then final fresh-import multiview. Reproduce from original in a second clean process and compare GLB hashes. Verify hierarchy, exact triangle parity, dimensions, UV/image availability, finite geometry, named interfaces and protected existing assets.

## Stop / rollback / acceptance limits

Stop on source SHA changes, protected native mismatch, nonfinite data, export failure, exhausted two-candidate bound or repeated major visual defect. Rollback means leave this unselected local candidate unused, not restoring old game files. Originals, failed adaptations, credentials and unique work are untouched. User direction approval is not final detail/history/UE/LOD/performance acceptance. No Unreal launch, additional credit debit, SFTP transfer, Catalog/allowlist edit, purchase, M1 reload change, commit or push.

## Early structural review / bounded second candidate

`structural_v1` setup TypeError occurred before authoring; retain the empty output and failure record. `structural_v1b` exports274,701 triangles with257,264 original faces retained and zero unchanged-corner UV error. Its fresh-import12/13 checks pass, but generated revolved part winding is inward. All ten neutral views inspected: upper far-side source artifacts outside the too-narrow cut, misplaced handle above its original support region and an exposed front-band cut also reject this candidate. Second coherent correction reverses lathe winding, removes the complete bounded exterior zones across their width, moves the handle/bridge to the source-observed attachment, introduces explicit inlet support plates, and fits an elliptical front-band transition to the retained fore-end. It does not change untouched stock faces, decimate, add cloud requests or relax final visual review. Freeze first source snapshot beside its evidence before correction.

### Explicit completion correction to this agent-authored bound

Both structural drafts remain unselected. V2 passes13 numeric gates but its enlarged cuts expose stock interfaces and oversized plates; production appearance is still rejected. The two structural-design drafts end here: no further cut-box/offset samples. Yupu's continued-local-refinement request did not impose a two-draft user gate; the earlier cap was this implementation's internal safeguard. Complete **one separately identified surface-closure pass**, then stop irrespective of outcome: derive local closing surfaces from actual cut-plane boundary positions, keep V2 cut volumes and steel axes fixed, reduce the temporary covering plates to the visible receiver supports, and preserve all original retained UVs. This is an explicit plan amendment before authoring, not relabeling V2 as passed or hiding another trial. No fourth pass, cloud call, source stock remesh, UE or publication. If these interfaces still look torn or blockout-like, report partial failure rather than continuing.
