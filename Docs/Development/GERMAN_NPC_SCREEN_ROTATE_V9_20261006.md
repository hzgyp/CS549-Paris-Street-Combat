# German NPC V9 — user-requested extra two-degree comparison

6 October 2026. User: add another 2 degrees to the reviewed V8 direction.
This explicitly supersedes V8's no-extra-angle stop ONLY for this one comparison.
It is not full-contact acceptance, native testing or formal asset selection.

## Reviewed cases and changed scope

Read current HANDOFF, Git state, Failures index, V8 plan/result, previously
reviewed V7 shared-weight/V6 thumb failures, GP010, AN002/AN008, weapon-hand
calibration guide and character-workflow skill/references. V8 index overlap
improved but thumb overlap worsened; neither camera occlusion nor reduced face
counts prove correct grasp. Retain every preceding failed result. This is the
user's explicit small-angle comparison, not an autonomous scan or clean rerun.

Start from actual V8 AFTER transforms and its fresh read-only geometry. Reuse
the recorded world rotation axis and actual local trigger pivot unchanged.
Apply ONE additional +2-degree rotation (4 -> 6 degrees relative to V7), not a
new screenshot raycast, axis solve, translation, scaling or finger adjustment.
Left wrist/grasp follows through its original-length whole-arm chain. Keep
the raised RIGHT thumb and all right bones/digit locals unchanged. Existing
six cross-hand-weight vertices can move with the left arm; do not claim all
right skin fixed or change source weights to hide this boundary limitation.

## Early checks and actual review

Require 618 approved guards and retained input hashes exact. Reproduce V8
read-only skin/gun <0.0001cm before fitting; axis must be identical to V8.
Fixed actual trigger <0.0001cm; protected/digit-local matrices <1e-8; original
left-arm length error <0.0001cm; true-zero-LEFT-influence and actual distal
right-index skin <0.0001cm; no new severe edges (>3x AND >2cm extra).
Measure the actual extra and cumulative rotation, marked viewer-depth motion,
all positive-weight digit crossing faces and mixed boundary tracking.
Do not require/claim that a fixed trigger point protects the whole blade.

Fresh separate-process reconstruction must reproduce stored geometry within
the existing 0.01cm display-parity budget. Render matched reverse/right/top,
support and complete-arm BEFORE/AFTER images; inspect all ten originals and
two labeled 4-degree/6-degree comparison sheets. Gray diagnostic pixels are
not UE shader/material, native binding, gameplay or motion acceptance.

## Stopping condition and protected production scope

Stop if guards, reproduction, fixed pivot, protected pose, reach or skin-edge
checks fail; preserve evidence. Contact can worsen during this requested
comparison: report it honestly, do not adopt or compensate. Stop after ONE
extra2-degree result for user review; no automatic third angle, offset,
thumb/finger solver or old proof rerun. No native slot/engine entry, usable
asset authoring, source rig/mesh/weights/actions/UV/material edit, map/package
save, formal German binding, FP/Allied/B/AI/Catalog/release change, deletion,
publication, Git commit or push. Formal German remains unarmed. Native motion,
reload/recoil, lifecycle, FPS/Shipping/second-machine tests remain unrun.

Private evidence: `Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/
Evidence/GermanNPCScreenRotateV9/extra_two_v1` and read-only `review_v1`.
