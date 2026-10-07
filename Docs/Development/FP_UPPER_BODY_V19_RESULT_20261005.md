# V19 native upper-body result

5 October 2026. User authorized adjustment of observed issues. See the bounded
implementation, AN006 and new AN007. **Holding/lateral motion improves; complete
action binding is unaccepted.** No formal player/map/Catalog selection or deletion.

## Verified changes

New native V19 subclass reuses selected D059 `W2_Stand_Aim_Idle_IP` for FP holding;
original body directional locomotion remains. Native source registration is
cached once, actions blend in parent-local space, same accepted V18 fingers/
pinky proportion/hand_r gun and original-length support IK. Camera unchanged;
no Python pose driver, mesh/weights/vendor animation edit or retarget/new motion.

Source code identifies run ring300 versus walk150/current ordinary speed300.
Refreshed native phase0.5 side-run hand is11.489cm lower than original idle.
Warmup-controlled24-sample holding comparison shows D059 hand span
0.197/0.520/0.293cm versus old idle2.300/13.466/5.636cm. Four arm segment lengths
are identical across the measured native clips. First editor sampler failed
refresh, two initial runtime samples were reference pose, and two unavailable
catalog variants stopped first holding probe; these are retained, not motion data.

Host builds: v1 fails struct/getter APIs; one header-backed correction gives v2
success; v3 completes fixed source-space registration before any city test and
compiles. Prior V18 DLL/PDB retained privately; new module remains default-disabled.

## Actual city evidence

`Evidence/FPUpperBodyV19/city_v1`:1246 read-only observations,2261 last native
updates,11 actual PNGs ALL opened. Isolated PID34056 exits0, no engine remains.
Early idle/left images inspected before allowing the remaining test phases.

- Idle/left/look up/down/forward/back/stop/returned holding keeps rifle in lower
  right, no large own-sleeve shard in inspected frames. Left gun camera Z now
  -16.497..-15.983cm versus old V18 -31.22..-16.57cm. Four directions reach300cm/s;
  this is native pose/locomotion observation, not a complete movement visual pass.
- Right movement reaches masonry; rifle is mostly occluded in `walk_right.png`.
  Local pose remains stable. Do not claim near-wall visual/collision/fire acceptance.
- `reload_mid.png` actually requested during Reloading at>=1.1s: major stretched
  sleeve sheets through left/central view. **RLD-02 fails.** Existing body Reload_2
  remains; approved D059 reload replacement has NOT been implemented by V19.
- Ammo2/16→8/10, one conserved native commit. First Reloading→Ready pair gives
  gun2.393878cm/wrist1.877148cm over24.498ms, below3cm. **This alone is insufficient.**
  Postcheck of the whole fade finds gun6.765319cm/wrist5.879395cm over140.510ms,
  native updates2145→2146: fails the unchanged sampled3cm screen. Initial observer
  enforced only the boundary. A synchronous full-result write at that boundary
  and a long engine frame confound timing; precise hitch cause/source discontinuity
  is unproved. Do not report complete continuity passed or fix by slowing blend.

Stable sample accepted30 finger rotations max2.415e-6degrees, gun relation
5.558e-13cm/2.415e-6degrees, arm-length error3.020e-13cm; support about5e-13cm.
Contact during action/partial grip return is not a held-grip pass. Screenshots
are dynamic requested frames, not a frozen phase-matched sequence or clearance proof.

## Preservation / next

`verification_v1` plus later `postcheck_v1` govern numeric facts; early test status
is not overall success.528 CURRENT recovery size/SHA guards exact, approved V18
blend/config unchanged, canonical map2791b4a7…ad68519 untouched; no native uasset
authored, source bytes/Catalog/NPC/B work unchanged. All media/config/compiled
binaries ignored; generic code/docs only for Git. No release/commit/push.

Stop full V19 action-proof route under AN007; its city launcher is locked. Preserve
useful holding separation, not automatic formal adoption. Next repair needs
different cause-supported compatible existing reload upper-body/source pairing
and low-overhead whole-return recording, not finger/weight/camera/offset/slow-blend
or old stopped author retries. Sprint/prone/jump/recoil/fire/moving reload/death/
reset/interruption/near-wall/FPS/package untested. Conditional old-copy cleanup
waits for complete actual acceptance/reference audit. Lane A releases native slot
after process/528-guard check; B can claim only after coordination.
