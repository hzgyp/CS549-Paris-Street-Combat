"""Scoped map roster wiring; selected presentation assets are never edited."""
import unreal
from common import DEST

LABELS = ("PC_City_Ally1", "PC_City_Ally2", "PC_City_Enemy1", "PC_City_Enemy2", "PC_City_Enemy3")
MAP = "/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1"


def prop(a, name):
    return a.get_editor_property(name)


def xyz(v):
    return [v.x, v.y, v.z]


def actor_state(a):
    rot = a.get_actor_rotation()
    item = {"label": a.get_actor_label(), "class": a.get_class().get_path_name(),
            "location": xyz(a.get_actor_location()), "rotation": [rot.pitch, rot.yaw, rot.roll],
            "scale": xyz(a.get_actor_scale3d())}
    if isinstance(a, unreal.Character):
        gun = prop(a, "WeaponAppearance")
        item.update({"team": prop(a, "TeamId"), "role": str(prop(a, "RoleId")),
                     "mesh": prop(a.mesh, "skeletal_mesh_asset").get_path_name(),
                     "anim": prop(a.mesh, "anim_class").get_path_name(),
                     "mesh_relative": [xyz(prop(a.mesh, "relative_location")),
                         [prop(a.mesh, "relative_rotation").pitch, prop(a.mesh, "relative_rotation").yaw, prop(a.mesh, "relative_rotation").roll],
                         xyz(prop(a.mesh, "relative_scale3d"))],
                     "gun": gun.get_path_name() if gun else None, "health": prop(a, "Health"),
                     "ammo": [prop(a, "LoadedAmmo"), prop(a, "ReserveAmmo")], "shots": prop(a, "ShotSequence")})
    return item


def replace_roster(version):
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    lookup = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    before = [actor_state(lookup[label]) for label in LABELS]
    player_before = actor_state(lookup["PC_City_Player"])
    after = []
    for label in LABELS:
        old = lookup[label]
        cls = unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + ("BP_PCAlliedFormalCombat" if prop(old, "TeamId") == 0 else "BP_PCGermanFormalCombat") + version)
        new = actors.spawn_actor_from_class(cls, old.get_actor_location(), old.get_actor_rotation())
        assert new
        new.set_actor_scale3d(old.get_actor_scale3d())
        assert prop(new, "TeamId") == prop(old, "TeamId") and prop(new, "RoleId") == prop(old, "RoleId")
        # Selected policies bind the original source component on BeginPlay.
        assert prop(new.mesh, "skeletal_mesh_asset") == prop(old.mesh, "skeletal_mesh_asset")
        assert prop(new.mesh, "anim_class") == prop(old.mesh, "anim_class")
        for name in ("relative_location", "relative_rotation", "relative_scale3d"):
            new.mesh.set_editor_property(name, prop(old.mesh, name))
        assert [prop(new, n) for n in ("Health", "LoadedAmmo", "ReserveAmmo")] == [prop(old, n) for n in ("Health", "LoadedAmmo", "ReserveAmmo")]
        gun = prop(old, "WeaponAppearance")
        if gun:
            component = gun.static_mesh_component
            original_component = {n: prop(component, n) for n in ("static_mesh", "relative_location", "relative_rotation", "relative_scale3d")}
            gun.set_editor_property("Combatant", new)
            gun.set_editor_property("GripMesh", new.mesh)
            gun.set_owner(new)
            assert gun.attach_to_component(new.mesh, "hand_r", unreal.AttachmentRule.KEEP_RELATIVE,
                unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
            for name, datum in original_component.items():
                component.set_editor_property(name, datum)
                assert prop(component, name) == datum
            new.set_editor_property("WeaponAppearance", gun)
            old.set_editor_property("WeaponAppearance", None)
        assert actors.destroy_actor(old)
        new.set_actor_label(label)
        state = actor_state(new)
        original = next(x for x in before if x["label"] == label)
        for name in ("team", "role", "mesh", "anim", "mesh_relative", "gun", "health", "ammo"):
            assert state[name] == original[name], (label, name, state[name], original[name])
        for name in ("location", "rotation", "scale"):
            assert max(abs(a-b) for a, b in zip(state[name], original[name])) < .0001
        after.append(state)
    assert actor_state(lookup["PC_City_Player"]) == player_before
    added = []
    for package, label in ((DEST + "/BP_PCSquadReservationV4", "PC_City_SquadCoordinator"),
                           (DEST + "/BP_PCFriendlyFirePolicyV1", "PC_City_FriendlyFirePolicy")):
        cls = unreal.EditorAssetLibrary.load_blueprint_class(package)
        existing = [a for a in actors.get_all_level_actors() if a.get_class() == cls]
        assert len(existing) <= 1, "Duplicate global policy"
        if not existing:
            a = actors.spawn_actor_from_class(cls, lookup["PC_City_Player"].get_actor_location(), unreal.Rotator())
            a.set_actor_label(label)
            existing = [a]
            added.append(actor_state(a))
        if "FriendlyFire" in package:
            assert prop(existing[0], "FriendlyFireEnabled") is False
    return {"before": before, "after": after, "player_exact": True, "player": player_before, "added": added}


def ready_snapshot(world, roster):
    bindings = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.ParisNPCGripActor)
    result = []
    for a in roster:
        c = unreal.AIHelperLibrary.get_ai_controller(a)
        assert c and prop(c, "BootstrapReady") and not prop(c, "BootstrapFailed")
        assert prop(c, "CombatEnabled") and prop(c, "EquipmentNumericVerified") and prop(c, "EquipmentHumanAccepted")
        b = [x for x in bindings if prop(x, "Target") == a]
        assert len(b) == 1 and prop(b[0], "Initialized") and not str(prop(b[0], "BindingError"))
        expected = "/Game/ParisCombat/Animation/" + ("AlliedGripV15/DA_PC_AlliedGripV16.DA_PC_AlliedGripV16" if prop(a, "TeamId") == 0 else "GermanGripV14/DA_PC_GermanGripV11.DA_PC_GermanGripV11")
        assert prop(b[0], "BindingConfig").get_path_name() == expected
        gun = prop(a, "WeaponAppearance")
        assert gun and not gun.get_actor_enable_collision()
        assert prop(gun, "Combatant") == a and prop(gun, "GripMesh") == a.mesh
        pp = a.mesh.get_post_process_instance()
        assert pp and prop(pp, "ValidInput") and prop(pp, "Evaluations") > 0 and prop(pp, "ProtectionError") < .0001
        result.append({"label": a.get_actor_label(), "team": prop(a, "TeamId"), "controller": c.get_class().get_path_name(),
                       "blackboard": prop(c, "blackboard").get_path_name(), "config": expected,
                       "gun": gun.get_class().get_path_name(), "actor_collision": gun.get_actor_enable_collision(),
                       "component_collision": str(gun.static_mesh_component.get_collision_enabled()),
                       "bootstrap_ready": True, "native_updates": prop(b[0], "NativeUpdates")})
    assert len(set(x["blackboard"] for x in result)) == 5
    return result
