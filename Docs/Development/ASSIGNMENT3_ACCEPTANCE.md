# Assignment 3 MVP Acceptance Checklist

Prepared 30 September 2026 against [goal version 1](ASSIGNMENT3_GOAL_V1.md), [Assignment 2 MVP](../Proposal/CS549_Assignment2_Proposal.md), and [Assignment 3 source requirements](../Assignment%203_%20MVP%20Development.docx). This checklist is an internal implementation record, not the submitted 1-2 page progress report. All tests below are unrun. Existing concept approval and server-byte verification are evidence for those specific facts only, not gameplay acceptance.

## Recording results

For each ID record date/tester, Git revision, asset manifest versions, engine/plugins, packaged build identity, settings, steps/input, expected and actual behavior, result, evidence path/link and defect/limitation. Use `Not run`, `Pass`, `Fail`, `Blocked` or `Deferred optional`; a Must cannot pass without evidence. Deferred optional items must appear in Plan vs. Reality. Course submission/access requirements remain mandatory unless an actual instructor exception is recorded.

## Functional and technical checks

| ID | Priority | Procedure and acceptance condition | Status |
|---|---|---|---|
| ENV-01 | Must | Restore exact Git/SFTP dependencies without overwriting local edits; record versions/rights. Load city and selected team mission without missing required packages/plugins. | Not run |
| ENV-02 | Must | Capture overhead/route evidence, representative travel times, collision, sightlines and NavMesh. Select connected mission area/objectives from findings, not a preset block/duration. | Not run |
| ASSET-01 | Must | Verify licensed character/rifle/rig/actions and visible historical configuration; inspect locomotion, sockets, reload, hit/death and first-person suitability in compatibility map. Record engine/asset ownership boundaries. | Not run |
| LOOP-01 | Must | In packaged build, play with 1 player, 2 allies, 3 Germans and one player rifle. Movement/aim/fire/reload/damage, HUD, configurable intermediate objectives and win/fail operate together. | Not run |
| ANI-01 | Must | Test legal action transitions, repeated reload input, duplicate notify, cancellation before/after commit, death and restore. Exactly one permitted ammo transfer; no stale event or manufactured ammo. Inspect hand/weapon alignment. | Not run |
| COL-01 | Must | Test movement at walls, stairs, cover and narrow passages; camera-visible/muzzle-blocked target, inside-wall muzzle, window/frame, solid cover and open target. One accepted discharge/hit/damage result; visible obstruction policy matches expectations. | Not run |
| NAV-01 | Must | At matched start/goals and load, compare independent with coordinated NPC destinations. Show reachable distinct goals, occupied reservation retention, waiting and bounded recovery after blocking/unreachable goals; no teleport, false success or endless retries. Record stalls/regroup time. | Not run |
| AI-01 | Must | Show faction filtering, ally follow/regroup/support, German guard/foot patrol, sight acquisition/loss, last-seen search expiry and return to role. Per-NPC memory stays separate; no hidden-target omniscience. Death stops attacks/movement and releases goals. | Not run |
| OBJ-01 | Must | Reach accepts living player and already-overlapping activation. Clear rejects empty/incomplete roster; counts earlier legitimate kills, deduplicates deaths and does not count leaving/unloading/despawn as death. Only current objective advances once; death takes precedence. | Not run |
| RESET-01 | Must | From won/lost/partial mission, retry without checkpoint and full restart restore initial roster/health/ammo/objectives; clear timers, effects, actions, AI/navigation/reservations and stale callbacks. Complete three repeat runs without progression/reset deadlock. | Not run |
| UI-01 | Must | During shots, damage, interrupted reload, objective transitions, death and restart, HUD reads the same authoritative state. No separate UI ammo/health calculation or duplicate damage. | Not run |
| SAVE-01 | Should | If implemented, save at selected safe boundary, change objective/player/NPC state, then restore snapshot and roll back later changes. Verify no implicit healing/refill/revival, no stale requests/events, and full restart still uses initial state. Otherwise explicitly defer. | Not run |
| ASTAR-01 | Optional | Only if custom graph is implemented: document costs/heuristic, compare A*/Dijkstra optimal costs and expansions on matched pairs, and verify local legs and bounded failure handling. | Not run |

## Performance and delivery checks

| ID | Requirement | Procedure and acceptance condition | Status |
|---|---|---|---|
| PERF-01 | Target frame rate | In normal packaged initial mission, record three matched warmed runs at 1080p/declared preset on stated hardware. Report FPS, mean/median/p95 frame times, hitches, CPU/GPU/memory and roster/active AI. Verify 60 FPS target using the goal's proposed mean-frame-time check; record any miss honestly. | Not run |
| STRESS-01 | Demonstrate limits | Predeclare finite workload upper bound. Increase finite active NPC load across reset runs at the same bottleneck; compare movement modes, display frame times/stalls and an observed limiting condition. State maximum tested and failure/stop reason, without claiming an unmeasured safe limit. | Not run |
| BUILD-01 | Playable desktop entry | Test packaged Windows executable outside editor and a second-machine launch/restore; include version, dependencies, controls and strict run instructions. Verify upload/download and reviewer access; check bundled asset distribution permission separately from source-sharing permission. Course permits compiled executable or strict run instructions. | Not run |
| AIUSE-01 | Applicable AI integration | Record actual offline tool tasks, useful output, time/debugging tradeoffs and rejected work. Validate any claimed AI-created runtime asset in build. No runtime LLM/API is claimed; concept art and stopped pilot are identified correctly. | Not run |
| VIDEO-01 | 2-3 minute explained real-time demo | Verify duration, running-software capture, voiceover/text explanation, all four pillars/core integration and stress limit with readable metrics. Match the frozen build; publish authorized YouTube/Vimeo link and test reviewer access. | Not run |
| REPORT-01 | 1-2 page PDF | Cover Plan vs. Reality with actual features/cuts, AI Utility, Roadmap to Final, playable build/run entry, video link and source link. Render/inspect final PDF and verify links; no invented results or unsupported approval claims. | Not run |
| SOURCE-01 | Public GitHub with README | Prepare permitted source, build steps, tested versions, controls, asset restoration/rights and credits. Check no commercial bytes/secrets/private email/team-only SFTP credentials. Verify authorized public URL or documented instructor exception; private development repository alone does not satisfy literal public-access wording. | Not run |
| ADMIN-01 | Prerequisite and deadline | Verify Assignment 2 completed/approved, remaining mentor evidence and official deadline. Existing Paris concept/pillar approval is not proof of all these conditions. | Not run |
| RELEASE-01 | Matching reproducible handoff | Align frozen build, Git revision, asset versions, report/video and evidence. Publish verified changed SFTP bytes before matching manifests when authorized; preserve baselines and local unfinished work. Verify all final reviewer links. | Not run |

## Current evidence and release decision

- Paris concept/pillar approval: the user's email screenshot is recorded in [submission status](../Submission/STATUS.md); private original stays outside public Git.
- Original city and rights-filtered history: server bytes previously SHA-256/size-verified under [published baselines](../../Assets/Sync/README.md), with the owner's three-member source-sharing attestation. This does not establish teammate restoration, package redistribution rights or runtime compatibility.
- Active city association: UE5.8; exact tested patch/plugins and all gameplay/performance results remain unverified.
- Assignment 3 calls for public source. The user subsequently authorized cleaning asset bytes/history and publishing the same source repository only after matching private SFTP manifests. Actual source visibility/storage results are in `../Submission/PUBLICATION_REVIEW.md`; this does not establish a playable build, video upload or course submission.

Declare the MVP ready for delivery only when Must/core requirements and performance evidence are reviewed, actual cuts/unmet targets are disclosed, optional checkpoint status is explicit, and required access/prerequisites are resolved. An unmet course FPS or public-source requirement remains an issue unless accepted through actual instructor feedback; a report entry alone does not waive it.
