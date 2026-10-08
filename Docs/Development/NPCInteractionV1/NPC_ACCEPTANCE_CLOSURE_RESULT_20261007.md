# B00–B05 functional acceptance closure

7 October 2026. B00–B05 bounded core-functional supplement is closed: SIX fresh
clean scenarios pass. Intermittent navigation reliability and visual/performance
gates remain open; this is NOT unconditional NPC/whole-city/full-motion/course MVP
sign-off. [Chinese](NPC_ACCEPTANCE_CLOSURE_RESULT_20261007_ZH.md).

The user requested acceptance closure. See the
[bounded implementation plan](NPC_ACCEPTANCE_CLOSURE_IMPLEMENTATION_20261007.md)
for read cases NI001/NI002/NI003/GP010/AN003/AN008, mechanisms, early gates and stops.
No native package, model, rig, weights, grip, original animation, player, formal
map, project configuration, Catalog or release was changed in this attempt.
Only local acceptance tools, tests and documentation were added or updated.

## Verified functional evidence

Each identity below is a NEW owned process using the saved FormalCombatV1 map,
finite explicitly logged unsaved stimuli and native decision/action trees.
No Python Blackboard/health/ammo assignment, per-frame movement/pose driver or
asset save. Strict error/ensure match count0, normal exit0 and exact703 protection
are required independently of a functional pass_* receipt.

| Private identity | Actual observed result |
| --- | --- |
| accept_formal_roles_v4_20261007 | Seven checks. Two original Allied bodies walk to distinct reserved goals, retain idle ownership, release only the dead owner's slot. Three German private last-seen memories remain frozen; fixed deadline23.630564s, end23.772831s, visited2 each, never more than5. Actual guard errors43.848/49.156cm within55cm. Third German physically visits home→destination→home. Unreachable point reaches RetryCount2/PathExhausted, then two seconds of stationary wait with no restart/teleport. |
| accept_formal_travel_v10_20261007 | Both ORIGINAL Allies tested sequentially on the same actually traversed eastern lane. Real native target replacement preserves the current episode and travel. Cumulative cutoffs904.178/872.118cm, physical regroup errors25.842/41.848cm.43 actual0.25s chase frames. Retained budgets in18/19 in-progress regroup samples, cleared only at actual arrival. |
| accept_formal_radius_v2_20261007 | Player-distance cutoffs942.783/918.455cm, physical regroup errors14.871/49.430cm.19 actual0.25s chase frames. Budgets retained in23/41 in-progress regroup samples. Maximum sampled Chase-mode player distance871.760cm; cutoff samples are already Regroup. Both the reported cutoffs and all measured chase values stay below1000cm. |
| accept_formal_blocked_v3_20261007 | Two original Allies facing three temporary blocking cubes stop after two replans each in15.686s, reservations released. Disable the blockers and assign the player a NEW destination once; both physically reach their distinct reserved goals in4.529s. No silent retry of the unchanged failed destination or speculative teleport/AI patch. |
| accept_formal_combat_off_v1_20261007 |18s six-finite-combatant fixture, global FF OFF. Native Allied/German shots1/9, two NPC deaths plus passive-player death. Original ammo conservation18 per NPC, dead stopping/reservation release, no resurrection or observed friendly target/damage. |
| accept_formal_combat_on_v1_20261007 | Same finite fixture with FF ON. Native shots3/10, three NPC deaths plus passive-player death. Same original conservation/death/ownership/faction checks; no observed friendly target/damage. Not proof that every crowded lane is safe. |

The earlier blocked_v1 bounded-stop subcheck is NOT its complete pass: recovery
fails continuity. blocked_v2 parks a nonparticipant over unverified far-floor
coverage and fails speed. blocked_v3 uses three distinct original settled roster
anchor sites; hidden collision remains enabled. The complete pass is only V3.

The quarter-second frames are a DECLARED stress fixture, not normal performance,
arbitrary-stall safety or FPS acceptance. These two boundaries are not concurrent
two-lane navigation, game respawn or whole-city coverage. The first original Ally
dies via original damage; the second has one declared original lifecycle reset
before natural slot0 ownership. Reset does not replenish ammunition.

## B00–B05 mapping and preserved evidence

- B00: current formal five-NPC private controllers/BBs, correct2/3 native equipment
  and single coordinator/FF policy pass in every new clean entry. Earlier saved-map
  ordinary -game with actual -DisablePython remains valid because its native
  dependencies are exact; this turn's test observer itself uses Python.
- B01/B03: native faction filtering, finite frozen-memory search, role return,
  actual patrol and unreachable wait are demonstrated under the stated fixtures.
  Formal saved Germans remain guards; the patrol role is unsaved test configuration,
  not an authored mission patrol route. Current search ends after2 points at timeout;
  the earlier search_runtime_v2 visited5 per German, not the current run.
- B02: two-body follow/ownership/death and REAL cumulative/player-radius boundaries
  now have fresh formal-brain evidence. Earlier squad_runtime_v5 retains original
  reload ownership and matched SAME-two-body/RVO comparison. Coordinated1.812s
  versus independent1.687s/0 failures is not coordination superiority. Obstacle
  recovery now passes its own finite fixture; repeated-layout reliability remains
  qualified by the retained57cm arrival and western-route failures.
- B04/B05: these FF OFF/ON autonomous fixtures supplement, not replace,
  action_combat_runtime_v8_20261006, autonomous_runtime_v6_20261006 and the current
  formal_selected_combat_regression_v1_20261007 21-shot player/Allied/German matrix.
  The latter proves original OFF blocking/no damage, ON35 friendly damage once,
  enemy35, wall/cooldown/reload/corpse behavior. Earlier selected action tests cover
  native Stop/Turn/Fire/Reload identity/replay/cancel/death/reset and stale callbacks.

See [formal result](NPC_FORMAL_COMBAT_RESULT_20261007.md) and
[combat result](NPC_COMBAT_V2_RESULT_20261006.md) for those dated actual records.
Preserved native hashes, not prose alone, support their dependency continuity.

## Visual diagnostic and reliability limits

Three ORIGINAL unpaused roles_v4 walking PNGs were inspected: early/later frames
show different body/leg positions with visibly continuous arms and the existing
rifles. Motion blur remains; the arrived camera crops the left body. These are
limited gross-shape checks, not complete continuous gait, surface contact, recoil,
reload return, near-wall clearance or every evaluation frame. AN008's stopped
full-motion launchers were not reopened. No grip fitting or animation tuning.

[NI003](../../../Failures/NI003-20261007-npc-acceptance-fixtures/FAILURE_ANALYSIS.md)
retains ALL failed identities. Raw/projection/heading/unisolated-body/unexported
API/far-parking failures are not promoted to passes. Functional travel_v5/v6 with
handled ensures remain OVERALL failed. The public ObjectIterator discovery avoids
the CLASS navigation lookup ensure without protected World-property access.

roles_v2/v3 reported Arrived while one real body stayed about57cm from its anchor.
roles_v4 passes with unchanged native assets; parking/independent diagnostics do
not prove the sole cause or that an AI/spawn defect was repaired. Preserve this
intermittent arrival/congestion risk and the actual western-body-route failure.
No relaxed55cm/1000cm gate, speculative native patch or unmeasured spawn correction.
Current author source ties PolicyEnabled/SquadEnabled to PC_EnableCombat; the
earlier contrary isolation hypothesis is explicitly qualified in NI003.

Finite combat can kill an inactive player quickly. Balance, mission routes,
objectives/checkpoints/restart, crowded connected-city pressure/FPS, Shipping,
second-machine restore, full-motion/contact and course deliverables remain open.
Passing selected bounded fixtures does not close those reliability/product gates.

## Protection, audit and handoff

Final read-only evidence acceptance_closure_final_20261007_v1 contains result.json
with703 exact size/SHA rows and acceptance_audit.json with all SIX clean receipt
SHA256s, strict exits/log checks, actual maxima and regroup-retention observations.
Disk inventory92 native B packages/92 registered rows/unknown0; no added package.
All owned UE processes exited0, including failed gates. At09:39:57 EDT actual UE
process count0, B releases native slot; never terminated the foreign query/user UE.
Check actual ownership before the next entry; this is a dated snapshot.
At09:40:08 the other window starts height_walk_v1_20261007; its PID17496 is
observed at09:43:03, foreign and untouched. B release is NOT a claim that this
later shared native slot is unoccupied. Preserve its mission documents/tools.

Offline20 tests pass:
ten contract/model, four formal protection and six receipt-validator tests. The
validator rejects handled-ensure passes, bad exits,1001cm overshoot, premature
budget reset and missing individual regroup observations; synthetic tests are not
native acceptance evidence. Python directory compilation and new launcher AST pass.
Final owned-nine-new-file whitespace and touched tracked-document diff checks
pass; Git's LF/CRLF normalization warnings are not failures. Existing editor
presets remain the same preexisting6-line addition. HEAD stays912b0596; no commit/push.

Current formal map remains2,720,990bytes, SHA256
9ff18c1339ee1de61add8a15acebd56512617ed69547de668b7d59ee1772d65b.
Current703 rows are immutable A678 plus25 B-only additions and the explicit
two-alias/ONE-map ledger. Immutable A snapshot/Catalog/release remain unchanged;
do not restore their older70df map over this authorized LOCAL unsynchronized map.
No new native package, SFTP publication, deletion, Git commit or push. Existing
DefaultEditor.ini/user changes and the other window's mission work are preserved.

Evidence is private under Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/
Evidence/NPCInteractionV1/<identity>; original logs/exits in tmp/npc-interaction-v1.
Each entry retains its actual copied source; later observer edits do not rewrite
running/completed entries. Commercial bytes/screenshots stay outside Git.
