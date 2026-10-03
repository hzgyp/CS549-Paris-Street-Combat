# Failure archive implementation — 3 October 2026

Owner: yg745. User authorizes archiving the rejected first-person repair before restarting from saved V3 with COD: WWII M1 Garand ordinary holding as reference. Read AGENTS.md, HANDOFF.md and the current FP result before execution. This plan is written before moves or source withdrawal.

## Scope and physical storage

- Create `Failures/README.md` as the mandatory failure-case index and `Failures/FP001-20261003-first-person-view/` for this case's original documents, source scripts, shared-source before snapshots, withdrawn diff and source/hash metadata.
- Preserve all seven `FirstPersonViewV1` native packages, evidence, rendering, logs/crashes/build output and deployed v25 binaries physically under the ignored private workspace `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/FailureArchive/FP001-20261003-first-person-view/`. Native packages keep their internal /Game identities and relative Content structure but leave active Content. This is offline archival, not editor package renaming or an automatic restore source.
- Move the six FIRST_PERSON_VIEW_REPAIR documents, the FP inventory and all dedicated `ue_first_person_view_*.py` / `run_first_person_view_*.ps1` scripts into the source archive. Leave no active launcher for the rejected candidate.
- The previous 40 native files are shared/protected inputs, not modifications produced by this case. Preserve them in place. Register V4 aiming and older finger-layer rejection as linked prior lessons; do not silently relocate earlier inventories/dependencies as part of FP001.
- Shared code is not moved wholesale. Preserve exact before snapshots, withdraw only FP001-specific optional branches/helper/include, generate an exact before/after diff and retain all unrelated changes. Restore the independently hashed pre-FP bridge deployment after saving v25; generated gameplay has no runtime bridge dependency.

## Order and gates

1. Confirm user-owned editor is closed; no automatic termination. User reported closure in this conversation; verify actual processes.
2. Rehash the 47 recorded packages, verify catalog identities, inventory every selected source/evidence file, and audit Unreal asset referencers. Refuse removal if an external package references any of the seven FP assets.
3. Refuse occupied archive targets or reparse descendants. Resolve every source/destination under this exact project/workspace. Use PowerShell native filesystem operations end-to-end. Hash before and after each move; write original→archive mappings. Preserve recoverability and stop on mismatch.
4. Withdraw FP001-only shared source changes and restore the three pre-FP deployed files using their saved hashes. Keep original snapshots and patch. Do not restore whole Git files or touch the source animation/model bytes.
5. Update current documentation/index links and require failure-case review in AGENTS.md and DEVELOPMENT_PIPELINE.md. Archive content remains historical evidence, not executable instructions.
6. Verify every archived entry, absence of original exclusive paths, unchanged 40 retained files/V3 map, source parsers, storage guard and a bridge-disabled V3 fresh-load gameplay regression. Only actual checks become pass records.
7. After archive completion, write the new bounded first-person implementation document with an explicit FP001/V4 lesson checklist. Begin with ordinary holding composition in the actual Paris city, protected camera/models/fingers and unchanged gunplay functions. Use new package/evidence identities; first visual gate precedes full motion extension. No AI/VFX/ADS/new actions, release, commit or push.

## Failure handling

All selected bytes survive in the mapped destination. A partial move is an incomplete archive, not a completed case; consult the journal before continuation. Do not merge occupied targets, erase failed logs or overwrite new work. Historical evidence paths inside preserved files are resolved with the manifest; snapshots are not directly executable after relocation. No SFTP publication or Catalog/allowlist change is implied.
