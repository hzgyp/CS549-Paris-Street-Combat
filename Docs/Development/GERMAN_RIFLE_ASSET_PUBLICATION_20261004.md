# German rifle model — closeout and private SFTP publication

2026-10-04. Yupu accepts V15 modeling and requests asset closeout/publication.
He separately confirms MW2 project use and three-member private derivative
sharing. This supersedes the earlier no-SFTP/unselected boundary only for this
accepted model. Owner: Yupu Guo (yg745). No further refinement, UE integration,
game replacement, purchase, cloud use, public binaries or Git commit/push.

## Reviewed cases / early check / stop

Read failure index, GP004/009, V15 result/work_state, TEAM_SYNC_WORKFLOW and
existing publication scripts. GP009: rendered source is not an exported pass;
reuse the actual verified V15 export, never regenerate it for publication.
GP004: metadata/source protection is not semantic or appearance approval;
record Yupu's actual approval separately from still-open runtime/history checks.
Previous rifle publication's ACL failure shows local moves can retain restrictive
permissions: inspect final shared access, exercise SFTP CRUD, preserve root ACL.

Early check pins final blend/GLB hashes and published evidence, verifies no
external Blender library or unpacked used texture dependency, confirms no
running writer/occupied destination, checks source/Git state and private rights.
Stop on unknown dependency, hash/ACL/host-key mismatch, conflicting Catalog owner
or occupied release. Do not overwrite, broaden ACLs or bypass a failed check.
Preserve transfer state and unique source bytes for explicit recovery.

## Concrete changes / order

1. Asset ID `german-rifle-model`, version `german-rifle-model-20261004-v1`.
   Exact accepted hashes: blend b6c9afcd...2f26b8; GLB77f7fd8c...02b378f.
   New nonsecret rights/asset README in Git; retain V15 diagnostic records as
   dated provenance rather than rewriting their historical paths/hashes.
2. Verify self-contained editable blend and36-image embedded GLB. Prior fresh
   geometry/material/clean repeat and actual views stand; no extra polish/test
   sweep. No new UE release or complete mechanical/animation kit is claimed.
3. With editors closed, same-volume move only the final two models and selected
   proof files to `Assets/LocalShared/SFTP/workspaces/yg745/german-rifle-model-v1/`:
   `Model/`, `Evidence/`, and README. Hash/size before/after. No former-path
   junction unless a concrete active tool needs it. Old trials/failed evidence,
   original deliveries and original M1 stay untouched; no broad cleanup.
4. Using existing private SSH identity and pinned host, upload new bytes via a
   unique `/incoming/` path to immutable SHA-256 objects. Reuse only verified
   existing objects, never overwrite. Download every final object, hash/size
   compare and check shared-account CRUD in a unique new workspace probe; no
   root ACL change. Immutable version policy and one named editor still apply.
5. Publish and download/hash the new release manifest. Only then add its exact
   bytes to `Assets/Sync/manifests/german-rifle-model.json`, pin it in CATALOG,
   add publication status/paired handoff and update AGENTS/HANDOFF/gap notes.
   Existing active manifests/city/playtest remain byte-identical.
6. Remove only exact verified disposable verification downloads and own probes;
   preserve transfer logs/receipts and all unique diagnostic/rollback material.
   Git metadata remains local pending separate commit/push authorization.

## Acceptance / handoff

Model acceptance: user's appearance/ordinary static modeling approval plus
recorded Blender5.2.2 export tests. Publish only self-contained models and useful
proof, not full MW2/M1/original library or old iterations. No external asset
dependency is needed to open the packed blend/embedded GLB if early checks pass.

Final acceptance evidence: source→workspace→immutable object→authenticated SFTP
download byte equality; verified release manifest; local/server selected-asset
check; shared-account CRUD/root ACL invariant; ignored asset paths, Git guard.
Manual restore guide must name manifest/hash-object downloads: existing native
playtest restoration tool intentionally does not fetch this optional model.
Historical weapon variant/mechanism/rig/actions/contact/UE import/mips/FPS and
second-machine tests remain separate open gates; no public asset redistribution.
