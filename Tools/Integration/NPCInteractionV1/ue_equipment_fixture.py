"""Unsaved exact Allied NPC equipment clone, never a grip fit or player copy."""
import unreal


def allied_config(source):
    gun = source.get_editor_property("WeaponAppearance")
    assert gun and gun.get_class().get_name() == "BP_PC_RifleAttachmentV3_C"
    assert gun.get_editor_property("Combatant") == source
    assert gun.get_editor_property("GripMesh") == source.mesh
    component = gun.static_mesh_component
    return {"class": gun.get_class(), "soldier_mesh": source.mesh.get_editor_property("skeletal_mesh_asset"),
            "gun_mesh": component.get_editor_property("static_mesh"),
            "left_shift": gun.get_editor_property("LeftShiftCm"),
            "location": component.get_editor_property("relative_location"),
            "rotation": component.get_editor_property("relative_rotation"),
            "scale": component.get_editor_property("relative_scale3d")}


def stage_allied(soldier, config):
    assert soldier.get_editor_property("WeaponAppearance") is None
    assert soldier.mesh.get_editor_property("skeletal_mesh_asset") == config["soldier_mesh"]
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    gun = actors.spawn_actor_from_class(config["class"], soldier.get_actor_location(), unreal.Rotator())
    gun.set_editor_property("Combatant", soldier)
    gun.set_editor_property("GripMesh", soldier.mesh)
    gun.set_editor_property("LeftShiftCm", config["left_shift"])
    gun.set_owner(soldier)
    component = gun.static_mesh_component
    component.set_mobility(unreal.ComponentMobility.MOVABLE)
    component.set_static_mesh(config["gun_mesh"])
    for name, key in (("relative_location", "location"), ("relative_rotation", "rotation"), ("relative_scale3d", "scale")):
        component.set_editor_property(name, config[key])
        assert component.get_editor_property(name) == config[key]
    assert gun.attach_to_component(soldier.mesh, "hand_r", unreal.AttachmentRule.KEEP_RELATIVE,
                                  unreal.AttachmentRule.KEEP_RELATIVE, unreal.AttachmentRule.KEEP_RELATIVE, False)
    soldier.set_editor_property("WeaponAppearance", gun)
    return {"source": "saved PC_City_Ally1, not player", "gun_class": config["class"].get_path_name(),
            "soldier_mesh": config["soldier_mesh"].get_path_name(), "gun_mesh": config["gun_mesh"].get_path_name(),
            "left_shift_cm": config["left_shift"], "source_component_config_exact": True,
            "grip_accepted": False, "map_saved": False}
