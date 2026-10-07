# AN008 — Allied native grip integration: partial native pass, selection withheld

6 October 2026. User accepts Allied V14 static appearance and authorizes UE
asset integration. This does not authorize further fitting or replacing the
original rig with a frozen diagnostic mesh. Read V15/V16/V17 plans and the
corresponding result before another attempt; FP001 and AN001–007 remain relevant.

## Preserved failures and useful results

| Entry | Actual result | What it does not establish |
| --- | --- | --- |
| cpp_v1 / cpp_v16 | Compiler-only include/pointer and narrowing/JSON-interface errors, corrected in distinct build identities | Not native crashes or animation evidence |
| native_ready_v1 | Native graph saved, harness calls unsupported World.spawn_actor; normal exit0 | No runtime bind/motion test |
| native_ready_v2 | Linked input/original identity/gun binding valid; Ready right-wrist residual10.069degrees fails3degree gate | Fixed local deltas do not reproduce a fixed accepted pose on an evolving input |
| native_hold_v16_early | Different absolute Ready-local overlay:11errors0, original source component, gun binding and five actual views pass early gate | No motion/adoption or zero blade crossings |
| native_hold_v16_motion | Wrong collision-response enum stops fixture before PIE | No action evidence |
| native_hold_v16_motion_b | Native walk300cm/s; fire request consumes1round but reports Barrel blocked; reload audit stops at0.151291degrees | No unobstructed shot/recoil/full return |
| native_hold_v16_audit17 | Python observer cannot read a diagnostic UPROPERTY from comma-separated declaration | No motion evidence; UHT declarations, not animation, corrected |
| native_hold_v16_audit17b | Reload raw protected quaternion component delta0; normalized physical angle3.415095e-6degrees; source norm error8.715524e-7 explains old raw-angle alarm | Return wrapper stopped during instance reinitialization; no full transition pass |
| native_reload_lifecycle_v17 | One bounded zero-evaluation wait; original2/16→8/10 reload returns Ready, input/gun audits valid,7actual images inspected | One pending frame not audited and333ms observations prevent full-motion acceptance |
| draft_asset_save / draft_asset_fresh | First entry saves DataAsset before None dependency-query error; fresh entry preserves that error and stops; both exit0 | Do not label either receipt successful persistence or recreate the occupied asset |
| draft_asset_read_v17 | Separate read-only native load/class/config/skeleton check, targeted synchronous registry scan and occupied-byte checks pass; PID19676 normal exit0 | Not a re-save, formal selection, complete dependency release or motion proof |

All611 protected rows remain exact at native entry closure. Formal map, FP,
B/NPC AI, German assets and Catalog are not edited. Actual logs/results stay
private in `Evidence/AlliedNPCUEV15`, in the one physical SFTP workspace; native
assets and failed binaries/build sources are retained in place. No cleanup,
formal adoption, publication or Git commit/push is implied.

## Measured cause distinctions

1. V14's source idle phase is not every runtime phase. Constant quaternion
   deltas follow source variation; they cannot pin accepted local rotations.
   V16 therefore uses the accepted local holding pose, without offset scans,
   new finger fitting or a different skeleton.
2. Installed Quat.h AngularDistance assumes unit quaternions. Identical
   compressed nonunit source entries give a nonzero raw angle. Normalize only
   temporary audit copies; keep raw component delta/norm error too. Never alter
   the actual protected pose or loosen the threshold to silence an alarm.
3. Original reload switches Blueprint→SingleNode→Blueprint and recreates the
   postprocess instance. Evaluations==0 is not an evaluated invalid pose.
   V17 waits ONLY for that expected zero-evaluation case, maximum0.5game-seconds;
   null/wrong-class/invalid evaluated input still stops. One pending frame is
   explicitly unvalidated, not a coverage pass.
4. HoldingAlpha is instance-local and initializes0. Source mode recreation
   resets it. A nominal0.15s interpolation in code does not prove that the
   whole release/return survives recreation continuously. Foreground sampling
   and state-lifecycle analysis are still required; do not blame timing alone.
5. Every sampled reload interval is333.333ms. Large position changes over
   those intervals are retained, not treated as short-frame proof failures or
   excluded to claim success. Installed background-editor throttling code is
   a plausible explanation, not a measured sole cause or performance result.
6. AssetRegistry dependency queries describe on-disk package references. A
   newly saved package can lack gathered registry data. None is unavailable,
   not an empty dependency list; verify occupied bytes and use one targeted
   synchronous scan/read-only check, never re-save the candidate blindly.

## Next-attempt contract

Preserve accepted posture and original model/weights/clips/FP/B/German.
Stopped fixed-delta and full-city motion launchers may not be rerun as a clean
proof. New work must document an explicit changed lifecycle/timing mechanism,
an early actual-frame cadence/input test and a bounded stop before the full
motion sequence. Do not increase blend time, tune gun offsets or claim ammo
conservation, an endpoint image, Editor compile or a fresh DataAsset read is
complete dynamic/Shipping/second-machine acceptance.

The separate read-only native asset persistence check is complete. Keep the
candidate disabled/unselected while full-motion, clear shot/muzzle/recoil,
near-wall, interruption/death/reset, second Allied NPC, FPS/package and
dependency/publication gates are unpassed. Preserve all earlier receipts and
their original process outcomes, including normal exit0 on test failure.

## Later human acceptance and formal adoption — 6 October

Yupu inspected the current V16 native preview, reported no problems and selected
it for all standard Allied NPCs. [Formal V18 result](../../Docs/Development/ALLIED_NPC_FORMAL_V18_RESULT_20261006.md)
supersedes the preceding disabled/unselected rule ONLY for this explicit adoption.
Both existing Allies and one later compatible spawn passed native selection and
owned-equipment cleanup; ordinary saved -game without Python/bridge passed.
Dependency closure/private SFTP publication and the new618-row guard epoch are
verified. The original model/rig/weights/clips/accepted adapter are unchanged.

This does not erase any failure above, prove zero intersections or close full
motion/instance-state/clear-shot/recoil/lifecycle/near-wall/FPS/Shipping/teammate
gates. Stopped fixed-delta/full-motion launchers remain stopped. No new blend,
finger or offset retry is authorized. Old map/Catalog guard hashes are historical
after authorized adoption, not instructions to roll back current shared assets.
