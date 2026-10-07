# Shared FriendlyFireEnabled merge proposal

Lane B proposal only. The coordinator owns any edit to
`BP_PCParisCombatantV2` and the shared configuration. This document does not
apply a patch or claim runtime acceptance.

## Exact semantic change

Keep the current authoritative two-stage shot and first-hit obstruction. After a
living combatant is the first muzzle-path hit:

```text
IsFriendly = Shooter.TeamId == Recipient.TeamId
DamageAllowed = !IsFriendly || FriendlyFireEnabled

if DamageAllowed:
    Recipient.PC_ApplyDamage(NormalDamage) exactly once
    ShotOutcome = IsFriendly ? "Friendly hit" : "Hostile hit"
else:
    do not call PC_ApplyDamage
    ShotOutcome = "Friendly blocked"
```

The hit terminates in every branch. A friendly never becomes transparent when
damage is disabled, and the hostile behind it receives no damage. The switch does
not change TeamId, perception affiliation or retaliation. AI fire admission uses
the same obstruction result and avoids a friendly-blocked lane in both modes.

The switch must live in one coordinator-selected configuration owner used by the
player, Allied NPC and German NPC paths. An NPC-only variable is not an acceptable
global implementation. Existing `PC_ApplyDamage`, health/death generation and
shot/ammo ownership remain unchanged.

## Required coordinator regression

For each shooter type (player, Allied NPC, German NPC), test:

1. friendly first hit, switch off: one accepted discharge according to existing
   ammo policy, zero friendly damage, zero damage behind;
2. friendly first hit, switch on: exactly one normal friendly damage application,
   zero damage behind;
3. hostile first hit in both modes: exactly one normal hostile damage application;
4. world first hit and near-wall/muzzle block: unchanged outcomes;
5. friendly enters a previously clear lane after admission: the actual first hit
   follows the same switch and never penetrates;
6. death/reset/stale callbacks and ammo conservation remain unchanged.

Record shooter/recipient TeamId, switch value, ShotSequence, hit actor,
ShotOutcome, health before/after, ammo before/after, damage-call count and restore
generation. Run with the bridge disabled and preserve the current off-mode
regression as historical evidence; it does not prove the new on mode.
