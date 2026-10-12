# Player death presentation and trial-directory implementation

2026-10-11. User requests all trial entries inside the existing dedicated tmp area, visible mine fire/blast feedback, and third-person player collapse before the death/restart UI. Start from the exact69 field-manual candidate, not the older formal52. Preserve original models, fingers, gun/resource algorithms, enemy-clear objective and durable save/restore logic.

## Cases read and change

Read MI014 (saved corpses must stay terminal, new deaths animate), MI024 (wait for approved display), MI029/030 (post-clear hazards remain lethal; stale save modal and numeric/render mismatch), MI032 (explicit engine API prerequisites), MI033 (asynchronous capture timing), MI037 (actual images determine visual fit). This attempt adds a transient death camera/render observer and transient explosion particles; it does not author character meshes or native animations, change damage, collision/nav admission, or make hazards a checkpoint gate. Source comparisons enumerate exact manifest rows, never the Content junction or compiled caches.

Retire only the three newly added root trial wrappers after exact identity checks, preserving their bytes in private relocation evidence. Trial files and launchers live under tmp/Playtest-*/; the selected formal entry and original files remain. Record this standing placement rule and use an actual tmp launcher in delivery links.

## Presentation sequence

1. Preserve the original PC_ApplyDamage/PC_Die endpoint. An alive-to-dead player transition immediately keeps the authoritative Lost state and existing collision/movement/resource protection, but delays displayed death/restart actions.
2. Reveal the existing full player body, hide the first-person presentation, switch to a wall-swept third-person camera, and let existing Rifle_Death_3 finish. No new skeleton, finger/grip edit, physics ragdoll, health/ammo change or animation replay. Reuse the original live death voice/impact audio.
3. Block movement/fire/equipment/menu/load/restart during the short collapse; suppress the combat HUD/save/terminal text until collapse finishes. After the terminal pose and a brief hold, show the existing Lost/restart/load UI and cursor. Never seek a saved NPC corpse back to its beginning. New world/load/reset destroys the transient camera and resets only presentation state.
4. Mine and frag blasts retain original recorded explosion audio and original radial/occlusion damage. Add a bounded warm flash, sparks and dust using existing cooked materials; no new collision, AI cover or damage emitter. Nonlethal explosions also show their own local effect. No persistent fire or new save payload.

## Early acceptance and stopping condition

First compile a separate identity, then run a real mine death with the original damage and capture standing/start, falling, corpse and terminal UI. Require a visible full body, advancing original death clip, clear camera line of sight, early input/HUD suppression and delayed menu. Inspect actual pixels and wait for screenshot completion before subsequent fixture changes. If body/camera/FX are invisible, clip restarts, the menu appears early, or any protected byte/resource/save rule drifts, preserve that identity and stop delivery; diagnose with a separately documented bounded correction.

## Acceptance scope

MI041 addendum: rubble-edge initial position rejects the prone fixture before death. Use the previously physically reached prone test site and real Z input with the same DesiredPosture2 gate; declare relocation and keep gameplay/posture constraints unchanged. No new spawn point is selected.

MI040 addendum: v3 fixes the body/camera/footer, but early firelight is not visually adequate. Read existing material parameters without native writes before a bounded v4 flash correction. Retain original damage, audio and death sequence; stop if fresh early pixels still fail. v3 posture diagnostics remain historical until the final Game repeats them.

MI039 addendum: v2's numeric mine sequence passes but actual images reject camera smear, cropped head and terminal footer overlap. v3 makes an intentional camera cut, sweeps a420cm/70degree view, raises the initial target, captures at0.2s and changes only Lost title/redundant feedback rendering. All original animation, input-timing, damage and save gates remain; fresh actual pictures must pass before delivery.

MI038 addendum: v1 stops before runtime on helper declaration order and probe RunGeneration type. v2 adds the existing function declarations and uses the existing FString identity, preserving native/reflected/gameplay fields and all original acceptance gates.

Run actual mine/frag deaths, original damage death in standing/crouched/prone postures, post-clear saved-window hazard death, default-cancel F9 and F6 after completion, restart/load cleanup, and new-process equipment/legacy saved corpse compatibility. Re-run applicable gun/menu/checkpoint/equipment/UI regressions on the final Game. Record probe positioning/AI isolation/damage fixtures honestly; do not label them human combat or large-NPC stress. Review actual explosion and collapse frames at1080p and menu at720p. Keep existing Editors open; Game checks do not establish new Editor/PIE/cook acceptance. No automatic baseline adoption, publication, recording or broad cleanup.


11 October addendum MI040/v4: runtime warning proves M_Glow lacks cooked ParticleSprites usage; read-only audits3–5 confirm existing M_Fire_SubUV_11X11_Noise is compatible and uses 11x11 SubUV plus LerpNoise/X/Contrast/Scale inputs. Use that existing material, matching atlas and transient dynamic (0,0,1,1), with no native flag edit or recook. Fresh actual mine/frag flash pixels must pass before delivery; stop on missing material/shader/atlas or invisible fire. The prone diagnostic uses the previously measured clear site and real Z input; retain actual posture gate.


v5/MI040: v4 removed shader-usage fallback but fire pixels still fail; do not continue atlas/gain sweeps. Use the existing authored NS_Fire_Small Niagara system for the short blast, emission stop0.15s/hard lifetime0.8s, alongside the same dust/light. Add Niagara dependency only, no native edits. Damage/audio and original death sequence remain exact. Fresh mine/frag pixels must pass.


v6 diagnostic bound: v5 numeric sequence passes but early flame still fails. Read-only fire system has no exposed inputs/warmup, Editor compilation is pending; this does not prove runtime readiness. Stop short Niagara reuse. Use compatible fire sprites with explicitly non-baked runtime curves and dynamic-module usage flags, add opt-in 0.2s active-particle/alpha/position log; installed DistributionFloat.h shows raw curve initialization is Editor-only. No further gain sweep. Test actual particles and pixels before further action; retain v5. Remove unconsumed Niagara dependency.
