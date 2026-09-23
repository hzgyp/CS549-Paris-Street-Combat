# Technical design - Paris Street Combat

## 1. Boundaries

The asset pack supplies the city geometry, materials and vendor utilities. Unreal supplies rendering, animation runtime, scene queries, navigation and packaging. The team implements a bounded encounter and the three mechanisms in the proposal. This is a design baseline; it is not an implementation or validation report.

The active environment is Unreal/ParisStreetCombat/WW2FranceLiberation.uproject. Keep the vendor `/Game/WW2City` namespace unchanged. Future team content belongs in `/Game/ParisCombat/{Maps,Blueprints,Animation,Materials,VFX,UI,Tests}`. Use a team-owned encounter map or editor-aware duplication/migration when development resumes; do not rename binary package files in Explorer.

## 2. Proposed components

| Component | Owns | Must not own |
|---|---|---|
| Player controller / Enhanced Input | Move/look/aim/fire/reload commands, pause | Damage decisions hidden in UI or animation |
| Player character | Movement capsule, camera, weapon/hand attachment | Global mission completion |
| Weapon component | Ammo, accepted-shot cadence, reload transaction, authoritative shot result | Per-effect damage decisions |
| Animation Blueprint / action coordinator | Locomotion blending, action transitions, guarded notify dispatch, grip alignment | Independent authoritative ammo counter |
| Impact feedback component | Surface lookup, position/orientation, bounded decals/particles/audio | Hit detection or repeated damage |
| Health component | Damage acceptance and one death transition | Per-frame repeated objective updates |
| Enemy controller | Minimal acquire/attack/lost/dead behavior; limited navigation if needed | Runtime LLM or complex squad tactics |
| Mission controller | Encounter start, objective, win/fail, restart generation | Shader or bone manipulation |
| Debug/evidence view | Traces, impact/surface data, action IDs, counters and baseline selection | Shipping gameplay dependencies |

Use Blueprint interfaces for damage/target interaction and explicit event payloads for shot feedback. Data assets/tables may hold weapon tuning, surface mappings and encounter placements. Do not let every actor independently trace and decide the outcome of one shot.

## 3. Shot contract and collision pillar

Baseline shooting is hitscan. Cosmetic tracers do not determine damage; penetration, ricochet and physical bullet ballistics are out of scope.

Proposed sequence:

1. Reject input when dead, reloading, out of ammunition or inside the fire-rate interval.
2. Trace from the camera along the aiming direction to a fixed range to determine the intended aim point.
3. Trace from the muzzle to that point using the documented weapon obstruction channel, ignoring only the shooter's own permitted components.
4. Use the first physical muzzle-path hit as the authoritative hit, even if the camera sees an enemy beyond a corner.
5. Consume one round for an accepted discharge, assign one shot ID, apply damage once if appropriate, and dispatch one feedback event.
6. Visual feedback uses the authoritative hit position, normal and Physical Material. A miss cannot generate a hit effect or damage.

For a muzzle already inside a wall, line traces alone may be insufficient. Define a bounded muzzle-clearance check/weapon pose policy and validate it during Gate 3 rather than ignoring the containing geometry. The accepted-discharge versus blocked-action ammunition policy must remain consistent with animation and UI.

Suggested payload: shot ID, shooter, muzzle origin, camera aim point, hit actor/component, hit position/normal, surface type, and damage category. Damage is independent of rendering quality settings.

Define separate movement, weapon obstruction and perception policies. Decide explicitly whether glass, railings, vehicle shells and foliage block each policy. Decorative debris may be visually present without blocking the movement capsule; shootable cover must agree with its visible silhouette. An invisible player capsule should not unintentionally shield all visible enemy body regions.

Comparison: camera-only trace versus two-stage trace at identical positions. Cases include near wall, corner exposure, muzzle inside cover, window/frame, target behind solid cover and unobstructed target. Record expected/actual hits, false damage/blocking and repeated results at fixed frame-rate settings. These are scheduled tests.

## 4. Action contract and animation pillar

Acquire a compatible weapon/rig/action set before fine tuning. Separate first-person arms from third-person enemy representation when that reduces integration cost. Purchased animation clips are dependencies; state rules and event correctness are team work.

Proposed states: Ready, Aiming, Firing, Reloading, Dead; locomotion is a separate blended layer. Specify legal interruptions rather than allowing each input to play a montage independently.

A reload receives a unique transaction/action ID. A defined animation event commits ammunition exactly once. Cancellation before that event leaves ammunition unchanged; cancellation after commit does not reapply or refund it. Death cancels actions and timers. A stale notify from an earlier action or restart generation must be ignored. A timeout may safely cancel a stuck action and record an error; it must not silently manufacture an ammunition commit.

Start with one simple ammunition model appropriate to the selected weapon. Do not promise generic magazine handling before the actual historical weapon and action assets are chosen. Weapon-specific clips, sockets and moving parts are checked during asset compatibility work.

Comparison: a timer-only reference versus guarded animation-event synchronization under different playback rates and interruption points. Evidence includes duplicate/missing commits, state trace, event timing and observed hand/weapon attachment. Visual polish cannot substitute for correct action state.

## 5. Rendering pillar

Use a surface-to-feedback mapping for a small set of surfaces in the selected street, such as masonry, metal and wood. Start with existing permitted VFX/decal resources and implement team-owned selection, orientation, lifetime, count limits and parameter control. Do not claim to author the environment pack's master materials, Lumen or Nanite.

Impact effects must use the collision hit result. Surface normal drives orientation; decals should not spread across unrelated silhouettes. Effects have an explicit active-count cap and lifetime; clear or recycle them during restart. Decide limits from measurements rather than arbitrary ultra settings.

Use a fixed light/time preset for comparable evidence. Vendor wetness, snow, vehicles and filmic options do not become production requirements because they are available. If the vendor already supplies an identical feedback mechanism, document it and obtain instructor alignment on the bounded team extension rather than presenting it as original work.

Comparison: generic feedback versus surface-aware bounded feedback on the same camera path and shot sequence. Record GPU/CPU frame times, active effects and visual differences. Profile city streaming, shadows, ray tracing and effects separately; storage size does not predict VRAM residency.

## 6. Supporting encounter systems

Use a small enemy population and one enemy configuration. Fixed fighting positions are an acceptable first implementation. Engine-supported movement or a small Behavior Tree may be added if the encounter requires it. No custom threat-aware planner or squad system is required.

The enemy must obey occlusion, stop attacks after death, and reset. Player damage, enemy damage, objective and HUD updates use authoritative state/events. The mission has explicit Ready/Playing/Won/Lost states and a restart generation ID. Restart clears actors, damage flags, action IDs, timers, ammo state, effects and objective state before re-enabling inputs.

A simple reach-and-clear objective is sufficient. No bunker destruction, driveable tank, door interaction or cinematic landing is carried over from the old plan.

## 7. Asset and engine integration

- The local city descriptor associates with UE 5.8. Test the installed 5.8.2 baseline later and then pin the team's exact version.
- The vendor page requires ChaosVehiclesPlugin. It is included in the organized project descriptor because the engine plugin is installed, but vehicle gameplay is out of scope and dependency compatibility is not yet tested.
- Both default map settings point to the vendor Paris map for initial environment access; the future team encounter/game mode is not implemented by this configuration change.
- Preserve the vendor's level/sublevel and external-actor package layout during restoration. Do not cherry-pick only the visible `.umap`.
- Commercial environment content is excluded from Git; retain the local source delivery, asset listing/version, entitlement evidence when available, and inventory hashes.
- Reference/Gunplay scripts and Blueprints may reference archived maps, character rigs, materials and helper modules. Inspect and adapt on purpose. No automatic source conversion or generator execution is part of this reset.

## 8. Evidence and performance plan

Target Windows at 1080p and a declared preset, aiming for 60 FPS on the primary desktop. Gate 4 records median and upper-percentile frame times, visible hitches, GPU memory, resolution/upscaling and hardware details. Run the same route and shot workload for baseline/comparison captures. Validate outside the editor and on a second machine.

Performance fallback order: reduce loaded area/optional scenery, bounded effect load, expensive lighting/shadow options, then presentation resolution/preset if required and disclosed. Do not alter hit correctness to improve frame rate.

For each pillar keep: problem, engine/asset boundary, owned implementation, prediction, baseline, repeatable input, result and limitation. Actual results are stored only after measurement. No performance or interaction test was performed as part of this planning transition.

## 9. Demo plan

1. Briefly identify Paris liberation context and the asset/implementation boundary.
2. Play the small street encounter with movement, combat, reload, objective and reset.
3. Replay a wall/corner case with trace visualization.
4. Show a reload interruption with action/ammunition events.
5. Show a matched surface-feedback comparison and measured rendering cost.
6. Explain limitations, team ownership and the source/build identity.

Keep a backup recording of the same frozen build. The later final demo must reflect actual results rather than the environment vendor's trailer or the former Normandy browser prototype.
