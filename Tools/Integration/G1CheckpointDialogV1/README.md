# Checkpoint dialog candidate lane

Read `Docs/Development/G1_CHECKPOINT_DIALOG_IMPLEMENTATION_20261010_ZH.md` and
MI019 / MI022 first. Work only from the exact unified v9 parent frozen here.
`prepare.py` freezes sources, native guards, Game and current manual user files.
`author_changes.py` and `author_probe.py` describe the initial v1 change, not an
idempotent command against occupied sources. MI022 documents v2's sole naming fix.
v2 passes native menu/save checks; v3 changes only player-facing modal copy and
adds explicit pending-request leave coverage to the probe. Private prepared
snapshots/manifests retain the exact source identities of all three revisions.
Each prepared private Project and failed identity is immutable; use
`prepare.author` with a distinct revision, then `build.ps1`, `stage_runtime.py`.

Run `launch_check.ps1` for menu, checkpoint and fresh-process restore using
isolated UserDir/slots. The checkpoint seed is an existing real old V5 journal,
not a manufactured victory. Tests use native simulated inputs and an isolated
readonly slot to cause a real write failure. They are not physical OS keyboard/
mouse or a fresh combat-through-mission test. `check_source.py` audits reflected
schema and unchanged save/resource/AI/navigation blocks; `verify.py` additionally
audits native bytes, frames, actual durable serials and cross-process restoration.

The copied parent `ParisUXTest=checkpoint[_patrol]` observer assumes synchronous E
and is not a valid test of this asynchronous UI request lifecycle. Do not run it
or claim its old receipts as reruns of this child. The durable write itself stays
synchronous and exact. Normal launch has no observer/audit flags. Only Game is
built; copied cached Editor binaries must not be used for this source.

No asset/model/grip/clip/layout selection, public publication, SFTP or cleanup.
Keep source, failures, evidence and user saves. Inspect active engines each time.
