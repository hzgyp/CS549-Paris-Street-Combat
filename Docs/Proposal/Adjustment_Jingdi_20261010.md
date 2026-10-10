# Initial-release playtest adjustments — Jingdi, 10 October 2026

Jingdi reports having tried the initial playable release downloaded from SFTP.
The following eight suggestions summarize that feedback for team review. The
tested release ID and executable hash were not supplied, so record them before
diagnosing differences against the selected audio V2 source. The observations
below are user reports; the suggested changes and acceptance checks are proposals.

Priorities: **P0** restores essential interaction; **P1** improves normal play;
**P2** refines presentation after the functional issues are resolved.

## Playing method

### 1. Start a new mission with a full M1 Garand — P1

- **Reported:** The player starts with two loaded rounds rather than eight.
- **Suggested change:** Configure a fresh mission and full new-mission restart
  with eight loaded rounds. The current rifle already has an eight-round capacity;
  starting ammunition is a loadout choice. Specify the starting reserve separately.
  Loading a checkpoint must restore its saved ammunition rather than grant a refill.
- **Acceptance:** A fresh start shows eight loaded rounds and permits eight shots
  before empty. The ninth attempt consumes nothing. Restart restores the configured
  initial loadout; checkpoint load preserves the actual saved loaded/reserve counts.

### 2. Make the main menu selectable — P0

- **Reported:** There appears to be no usable button for selecting menu items.
- **Source context:** The selected Ready screen displays an Enter prompt through
  the HUD; it does not provide a conventional clickable menu or selection navigation.
- **Suggested change:** Give every displayed menu item a working input action.
  Support mouse selection and keyboard navigation with visible focus, Enter to
  confirm, and clear disabled states. Keep the available start/load/restart actions
  consistent with the displayed instructions.
- **Acceptance:** From a fresh launch, a player can select each available action
  using either mouse or keyboard. Clicking a menu item does not also fire the rifle.
  Starting play restores mouse-look and gameplay input correctly.

### 3. Make the radar follow the player — P1

- **Reported:** The map remains fixed on the initial local area as the player moves.
- **Source context:** The current minimap uses a fixed surveyed G1 background with
  live player and NPC markers; its view does not scroll around the player.
- **Suggested change:** Use a player-centered radar whose background scrolls with
  movement. Use a consistent orientation and transform for terrain, heading, allies,
  objective and checkpoint markers. Show off-screen ally directions at the edge.
  Match the displayed area to the surveyed mission coverage; do not represent
  uncharted areas as a complete Paris map.
- **Acceptance:** Walking in each direction moves the background correctly while
  the player stays centered. Turns and boundary crossings preserve marker alignment,
  scale and heading. Test this together with the ally indicators in suggestion 8.

### 4. Increase walking and running speed — P1

- **Reported:** Both walking and running feel too slow.
- **Source context:** The earlier selected playtest measured approximately
  150 cm/s walking and 300 cm/s running; these are reference values, not new
  measurements of Jingdi's package.
- **Suggested change:** Compare a bounded faster walk/run preset on the same route
  and select it through manual play. Keep walking, running and slow movement distinct.
  Check squad following, stopping distance, collision and animation/audio timing
  alongside speed rather than changing the movement value alone.
- **Acceptance:** Record actual travel time and velocity before and after the change.
  Traversal feels faster without new foot sliding, mistimed steps, overshoot, wall
  penetration or allies falling behind. Keep crouch/prone movement separately tested.

## Figure animation and aiming presentation

### 5. Improve the aiming cursor; consider ADS separately — P1 / P2

- **Reported:** The aim cursor is difficult to see. Jingdi suggests a green cross
  or an aiming action similar to Call of Duty: WWII.
- **Suggested change:** First provide a clear green crosshair with a contrasting
  outline and enough size/opacity to remain readable against bright and dark city
  surfaces. Treat aim-down-sights (ADS), for example on right mouse, as a separate
  P2 option using compatible existing animation assets. A visibility fix does not
  require new character models, replacement finger poses or a new aiming animation.
- **Acceptance:** The cursor remains visible at the supported resolutions, is
  centered on the existing aiming direction and preserves actual shot/cover behavior.
  If ADS is added, test entry/exit, firing, reload, death and near-wall transitions
  while preserving the accepted weapon attachment and resource rules.

### 6. Review the M1 Garand reload presentation — P2

- **Reported/requested:** The reload should visibly represent inserting a full,
  preloaded eight-round en-bloc clip into the rifle's internal magazine, rather
  than an incompatible reload action. The M1 Garand's eight-round en-bloc feeding
  is documented by the [Civilian Marksmanship Program](https://thecmp.org/wp-content/uploads/Distinguished_History.pdf).
- **Reference:** [Jingdi's supplied reload video](https://youtube.com/shorts/JfvR_o67pNU?si=9siGQ76oNbVOt8ZQ).
  The video could not be inspected during this document review; the team should
  verify the exact visible sequence before selecting or adapting an animation.
- **Suggested change:** Review the existing compatible clip and its timing first.
  For an empty-rifle reload, the requested presentation shows the open action,
  clip insertion, closing action and return to Ready. Evaluate a nonempty reload
  separately. Reuse licensed compatible assets and keep the accepted model/grip
  unless a specific bounded adaptation is agreed.
- **Acceptance:** Visual action, mechanism sounds and the single ammunition commit
  agree. Loaded rounds never exceed eight; ammunition is conserved. Partial reserve,
  repeated reload input, interruption and death retain the existing transaction rules.
  A visual full-clip sequence must not manufacture missing reserve ammunition.

## Mission design

### 7. Diagnose checkpoint saving and explain failures — P0

- **Reported:** Pressing E after arriving at the checkpoint failed to save.
- **Source context:** The G1 checkpoint unlocks after all three registered guards
  are defeated. Entering the green ring offers the save question. Saving still
  requires the original safe-boundary conditions, including a standing, grounded,
  still player and eligible surviving squad state. Arrival alone is insufficient.
  Earlier scripted passes do not resolve this manual failure.
- **Suggested change:** Reproduce the reported path in the exact tested release.
  Distinguish a locked checkpoint, missing prompt/input focus, unmet safety
  condition and failed disk write. Display a specific actionable reason, retain
  a usable retry prompt, and confirm success only after the journal write succeeds.
  Make the required checkpoint conditions visible without bypassing the save rules.
- **Acceptance:** After legitimately clearing G1 and satisfying the safety conditions,
  one E press creates a valid checkpoint with a clear confirmation. A fresh launch
  and F9 restore position, objective, ammunition, health, squad state and stopped
  dead enemies. Unsafe attempts explain the reason and preserve the previous save.

### 8. Spread NPCs across the encounter and expose ally positions — P1

- **Reported:** NPCs should be more dispersed, and allies should be locatable on radar.
- **Source context:** Live ally markers already exist in the selected HUD, but markers
  outside the circular map are omitted. Their presence in source does not establish
  that they were readable in the tested release.
- **Suggested change:** Reposition the existing two allies and three German guards
  across the surveyed connected encounter, with deliberate cover, sightlines and
  reachable routes. Keep the initial roster count while improving spacing. Make
  ally markers legible, update them from live positions and provide off-screen
  direction indicators. Distinguish surviving and defeated squad members clearly.
- **Acceptance:** NPCs start on valid navigable ground, avoid initial overlap, and
  remain able to follow/regroup or engage as intended. Radar movement matches world
  movement. Dispersal preserves the three-guard objective and checkpoint eligibility;
  verify actual squad arrival rather than relying on path-query success alone.

## Review basis and implementation handoff

Read: [current development baseline](../Development/CURRENT_DEVELOPMENT_BASELINE.md),
[current build guide](../Development/TEAM_CURRENT_BUILD_20261009.md),
[HUD/input/checkpoint result](../Development/G1_PLAYTEST_REVISION_RESULT_20261009.md),
the selected audio V2 controller/HUD source, [failure index](../../Failures/README.md),
and cases [MI005](../../Failures/MI005-20261008-packaged-squad-transit/FAILURE_ANALYSIS.md),
[MI006](../../Failures/MI006-20261008-navigation-preflight-frame/FAILURE_ANALYSIS.md),
[MI014](../../Failures/MI014-20261009-checkpoint-death-audio/FAILURE_ANALYSIS.md),
[MI015](../../Failures/MI015-20261009-audio-realism-turn/FAILURE_ANALYSIS.md) and
[MI016](../../Failures/MI016-20261009-player-foot-contact-jump/FAILURE_ANALYSIS.md).

Suggested order: menu and checkpoint feedback first; initial loadout, crosshair,
player-centered radar and ally indicators next; then bounded speed/placement trials
and reload/ADS presentation. This attempt creates the review document. Before any
implementation, identify the tested package, reproduce the issue or measure the
baseline, and record a bounded change with its acceptance check. Stop the candidate
on resource/save corruption, new collision/navigation failures, broken input or
degraded accepted character/grip/animation behavior; retain the failure evidence.
Gameplay fixes and new acceptance results remain separate work.
