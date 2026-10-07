# Approved first-person formal selection — 5 October 2026

Yupu accepts the current V20 presentation and ends hand refinement. The formal
map selects the accepted V18 right grip/distal pinky, unchanged V19 native hold
adapter and exact V20 left-thumb data. Cases/stops/corrections are recorded in
[the implementation plan](FIRST_PERSON_FORMAL_V21_20261005.md).

## Selected runtime and verification

Saved `/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1` now contains persistent
`ParisFirstPersonApprovedActor` / `PC_FirstPersonApprovedV20`. Map SHA256:
`f2aeac69bd17ace4a76057e8d2ab89cc6f0b087e76900406bdff74f38b7b4020`.
Private config `/Game/ParisCombat/FirstPerson/ApprovedV20/DA_PC_FirstPersonGripV20`
SHA256 `e65f9169eb467b048f63fe31ddd5ab2f5e795d06c56f673f9f8e651b62f2b254`;
payload remains `04f4588cc6922a907f3aaa2bc60d41dec985240e96d3c6c31f1d32dfde3bc7a7`.

Project explicitly enables the runtime plugin; it prepares/binds once natively.
Original owner/gun remain authoritative dependencies, hidden visually after
binding. Source mesh/rig/weights/materials/actions/camera/ammo logic unchanged;
no static diagnostic hand mesh, new motion or NPC offset copy.

BuildPlugin Win64 editor Development passes. Unsaved early_v2 passes numeric and
actual textured Ready gate. Fresh_v2 reopens the SAVED map without actor injection
or Python binding: Ready, left walk300cm/s, one original reload2/16→8/10 with one
commit, returned Ready. All three actual images opened. Thirty local rotations
match within2.414837e-6degree; gun hand_r/support chain match; camera25/0/60/FOV90
and authoritative weapon retained. Ordinary `-game` with Python/bridge disabled
logs native binding ready, exits0 via engine `-seconds=45`. Launcher CheckOnly
and selected228-file local hash/storage/Git check pass. Seven synthetic restore
tests pass, including DLL/modules outside Content; not second-machine acceptance.

Saved dependency audit covers15,456 existing packages, zero missing hard
dependencies and the same five supplier soft gaps. One physical map changes via
two aliases in the533-row old snapshot;531 other rows exact BEFORE publication.
Publication additionally updates the explicitly authorized Catalog metadata;
old map/Catalog guards are therefore historical, not current rollback authority.
All new555 approved guard rows match. New555-row approved
snapshot: private `Evidence/FirstPersonFormalV21/selected_v1/result.json`; old
snapshots/failure inputs retained, not rewritten. Build shadow-name, screenshot
size, guard alias/count, early movement sampling, truncated metadata diff and
mixed newlines are preserved in the plan/evidence; none changed accepted poses.
Optional current-user server-filesystem check was permission-denied, not passed;
authenticated SFTP byte readback supplies the actual remote verification.

## Private publication / handoff

Catalog selects `paris-native-playtest-20261005-fp-v20`, same playtest asset ID.
228 required files;224 immutable objects reused, four new objects totaling
2,981,682bytes uploaded. Every final object and manifest was downloaded through
pinned-host SFTP and size/SHA checked. Manifest SHA256:
`01e2fb2e1980562eff30099d428ea463858793382eb3b4dcbef4353799516c26`.
City baseline unchanged; shared CRUD probe passes/root ACL unchanged.228 exact
temporary downloads (~528MiB) removed; sources/recovery backups/old release and
failure evidence retained. No usable asset tree duplicated for adoption.

Private payloads/module binaries stay in SFTP; generic source/config/docs/hash
references stay in Git. **No commit/push requested or performed this turn.** Team
restore needs the matching Git revision after coordinator publication; no actual
teammate restore/runtime pass claimed.

Hand refinement is closed. Sleeves explicitly deferred; original Reload_2 remains.
Full-return/lifecycle/near-wall/FPS/Shipping gates remain unpassed; appearance
approval does not close AN007 or authorize old solver/proof reruns. All engines
closed; A releases serialized slot. B/NPC packages unchanged; B uses new approved
map guard snapshot before another writer.
