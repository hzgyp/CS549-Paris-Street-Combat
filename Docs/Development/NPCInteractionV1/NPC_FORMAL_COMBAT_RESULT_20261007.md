# Formal map NPC combat result

7 October 2026. The local formal Paris map now uses native NPC AI for its two
Allies and three Germans. Original player, models, selected Allied V16/German
V11 grip assets, animations and weapons remain unchanged. This follows Yupu's
explicit permission for formal-map integration and fresh play regression.

## Local changes

Five new FormalCombatV1 packages derive from the tested CombatV2 controller,
tree and compatible sensing Pawns. A native bootstrap service waits for the
correct selected gun references and evaluated protected postprocess input,
then enables the existing equipment/combat interfaces once. Timeout is ten
game-seconds and fails closed. AI decisions and pose evaluation are native;
Python does not configure or drive the saved-map NPCs.

The five saved bodies retain faction, role, transform, source mesh/animation,
health100, loaded2/reserve16 and original attached Allied rifle actors. German
rifles still come from the selected native German policy. The map contains one
squad coordinator and one global friendly-fire policy, default OFF. Allies
follow/regroup and can fight; Germans initially guard and use bounded search.
New patrol routes, objectives or balance changes are not included.

## Verified entries

- formal_bootstrap_runtime_v3_20261007: fresh unsaved replacement test passes
  native startup, five private Blackboards, selected2/3bindings and finite real
  combat. Four Allied/nine German shots at the final sample; each NPC's loaded
  plus reserve plus original ShotSequence remains18. Real casualties stop and
  do not resurrect. No Python AI configuration, action requests, teleport/reset.
- formal_map_author_v1_20261007: saved only the authorized map, preserving7,986
  other Actor states and701 non-map protection rows. One physical map has two
  junction aliases; before/after and exact private recovery copy are recorded.
- formal_saved_runtime_v1_20261007: new process reopens the saved map and passes
  the same three functional checks. Eight Allied/nine German shots at the final
  sample, including original native reloads; ammo conservation and dead stops
  pass. Player/Allied deaths in this unmodified layout are real, not resets.
- formal_plain_game_v2_20261007: ordinary saved-map -game with -DisablePython
  explicitly logs interpreter disabled. Five unique combat-ready NPCs and the
  selected2/3native bindings initialize, bridge is not mounted/loaded, runtime
  errors0, all703 guards exact, normal exit0. The Python plugin may mount; its
  interpreter is disabled. No Python script runs in this game entry.
- Offline:14 model/guard tests pass, including receipt/row/authority tamper
  rejection. Source compiles and the new PowerShell launcher parses.

formal_selected_combat_regression_v1_20261007 also passes21 original shots:
player/Allied/German under FF OFF/ON, friendly blocking/damage, hostile35damage,
world blocking, duplicate cooldown rejection, original conserved reload and
corpse NoCollision/no double death. It reuses the one saved FF policy and stages
selected native equipment, not historical manual gear. Its AI-disabled transaction
fixture is distinct from the native formal-startup proof. Guards703/errors0/exit0.

All owned UE processes have exited normally. The native slot is released.
Final read-only audit formal_combat_final_20261007_v1 persists all703 exact
protection rows. All92 B disk packages are registered, unknown packages0.
Repository-filtered owned diff checks and21 untracked-file whitespace checks
pass; the preexisting DefaultEditor.ini is not altered or included. Git HEAD
remains912b0596, with0/0 remote-main divergence; local work is not committed.

## Protection and synchronization

The formal map is2,720,990bytes, SHA256
9ff18c1339ee1de61add8a15acebd56512617ed69547de668b7d59ee1772d65b.
AUTHORIZED_FORMAL_MAP_20261007.json authenticates the immutable author receipt
and advances only its two aliases. Current protection is703 rows: the original
immutable678-row A authority,25 added B packages and this explicit map exception.
A's old70df map snapshot, Catalog and published release remain unchanged.

New package hashes are in the B inventory; private bytes/logs/recovery stay in
the one existing workspace. This local map/AI delta is NOT published to SFTP or
committed/pushed. Do not restore the older Catalog map over this unsynchronized
authorized local increment. Other writers must explicitly adopt this ledger.

## Failures retained and remaining gates

NI002 preserves the wrong relative_transform property, the already-depleted
second-encounter fixture and the first ordinary entry's incorrectly inferred
Python disable. NI001, GP010 and AN008 criteria remain applicable; no failed
grip or stopped full-motion proof is rerun. Older -DisablePlugins intent is not
evidence of interpreter absence; the later explicit flag proof governs that
narrow claim without rewriting old receipts or epochs.

The existing spawn layout starts combat quickly; inactive-player/Allied deaths
do not establish balanced difficulty or a complete mission. Patrol routes,
objectives/checkpoints/restart, physical-input human play review, full visual
actions/recoil/contact, foreground/stress FPS, Shipping, second-machine restore,
new immutable asset publication and course MVP acceptance remain separate.
