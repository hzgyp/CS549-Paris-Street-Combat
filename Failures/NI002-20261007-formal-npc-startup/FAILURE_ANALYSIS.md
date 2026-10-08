# Formal NPC startup integration failures

7 October 2026. Local formal-map integration is user-authorized under
Docs/Development/NPCInteractionV1/NPC_FORMAL_COMBAT_IMPLEMENTATION_20261007.md.
Private receipts stay in Evidence/NPCInteractionV1 in the existing workspace.

## Property access before play

formal_bootstrap_runtime_v1_20261007 fails before PIE: SkeletalMeshComponent has
no reflected relative_transform property. No combat or map save occurs; all703
protection rows are exact and the owned engine exits0. Its new unsaved actor is
not persistence or startup proof. The distinct second fixture copies the actual
relative_location, relative_rotation and relative_scale3d fields, preserving
the same mesh/animation/transform criteria. UObject/struct string addresses are
not stable comparison data; serialize values or asset paths instead.

Bootstrap assets compiling does not prove they run in ordinary saved -game.
Do not change grip/model/ammo fields or relax guards to correct this fixture.

## Native combat starts before the second fixture

formal_bootstrap_runtime_v2_20261007 passes all five automatic bootstrap/native
binding/private Blackboard checks. The original saved layout already produces
five Allied and six German real shots before eight game-seconds; Ally2 and one
German are dead, Ally1 has30HP. Teleporting that finite depleted roster into a
second encounter and expecting NEW Allied shots fails when Ally1 also dies.
All703 guards remain exact; no map save, ammo/health mutation or AI repair.

The new observer does not teleport or reset anyone. It measures the unmodified
saved-layout encounter against recorded PRE-PIE ShotSequence, including combat
before its readiness check. Both factions must still really fire, conserve18
total rounds each, cause a casualty and stop dead bodies without resurrection.
This tests the authorized saved map rather than assuming its native startup is
passive. The failed receipt remains failed; a fresh complete run is required.

## Fresh saved layout results

formal_bootstrap_runtime_v3_20261007 passes all three early checks, with four
Allied/nine German real shots by the final sample, conserved18 rounds per NPC
and real casualties/dead stops. All703 guards are exact and owned exit0. The
separate formal_map_author_v1_20261007 saves only the authorized map;7,986 other
Actor states match, and701 non-map protection rows remain exact. The old map's
two aliases and private single-map recovery copy are authenticated in its receipt.

formal_saved_runtime_v1_20261007 reopens that saved map in a new process and
passes all three startup/finite-play checks, with no Python AI configuration,
combat requests, teleport, reset or saved-map edits. All703 advanced protection
rows remain exact. This is functional map integration, not a complete animation,
mission, performance, Shipping, publication or teammate-restoration pass.

## Plugin disable intent is not interpreter disable evidence

formal_plain_game_v1_20261007 exits0, logs five unique native combat-ready bodies
and the2/3selected bindings with no runtime errors/703 exact guards. Its strict
Python absence check FAILS: despite -DisablePlugins=ParisEditorBridge,PythonScriptPlugin,
PythonScriptPlugin mounts, loads and logs Python enabled/Using Python plus engine
startup scripts. The same mounting is visible in the older German ordinary_game_v2
log. Those flags alone do not establish a Python-disabled entry; retain original
receipts and A epoch rather than rewriting their claims or assets.

Installed UE5.8 PythonScriptPlugin.cpp IsPythonEnabled checks -DisablePython
explicitly before default/user enable settings. The new ordinary entry uses that
flag, with the bridge separately disabled, and requires the actual interpreter-
disabled log plus no enable/Using Python/startup-script lines. Mounting a plugin
module is distinct from enabling its interpreter. The reason the old plugin-
disable list did not prevent mounting is not separately proven; no descriptor,
engine, module or native presentation change is made. A new result is required.

formal_plain_game_v2_20261007 now passes7 checks/703 exact/errors0/exit0: explicit
interpreter-disabled log, no Python enable/usage/startup scripts, bridge absent,
five unique native combat-ready bodies and2/3selected bindings. This supersedes
only the unverified interpreter-disabled claim, not other dated A/visual gates.
formal_selected_combat_regression_v1_20261007 also passes21 original shots/all
three shooters/OFF+ON with the one saved FF policy reused,703 exact/exit0.
