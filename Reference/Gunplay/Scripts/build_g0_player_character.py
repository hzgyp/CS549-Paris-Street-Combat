"""Create the project player Blueprint and attach the ammo-owning component."""

import unreal


PATH = "/Game/Normandy/Blueprints/Player/BP_NormandyPlayerCharacter"
TEMPLATE = "/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"
WEAPON = "/Game/Normandy/Blueprints/Player/BP_WeaponComponent"

assets = unreal.EditorAssetLibrary
library = unreal.BlueprintEditorLibrary
parent_class = assets.load_blueprint_class(TEMPLATE)
weapon_class = assets.load_blueprint_class(WEAPON)
assert parent_class and weapon_class

if assets.does_asset_exist(PATH):
    blueprint = assets.load_asset(PATH)
else:
    blueprint = library.create_blueprint_asset_with_parent(PATH, parent_class)
assert blueprint

subobjects = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
names = unreal.SubobjectDataBlueprintFunctionLibrary
handles = subobjects.k2_gather_subobject_data_for_blueprint(blueprint)
assert handles
has_weapon = any(
    str(names.get_variable_name(subobjects.k2_find_subobject_data_from_handle(handle)))
    == "WeaponComponent"
    for handle in handles
)
if not has_weapon:
    root = next(
        handle
        for handle in handles
        if names.is_root_actor(subobjects.k2_find_subobject_data_from_handle(handle))
    )
    params = unreal.AddNewSubobjectParams(
        blueprint_context=blueprint,
        parent_handle=root,
        new_class=weapon_class,
    )
    component, reason = subobjects.add_new_subobject(params)
    assert names.is_handle_valid(component), reason
    assert subobjects.rename_subobject(component, "WeaponComponent")

assert library.compile_blueprint(blueprint)
assert assets.save_loaded_asset(blueprint)
unreal.log(f"G0_PLAYER ready {PATH}")
