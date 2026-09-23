"""Expose character-level fire and reload requests backed by its weapon component."""

import unreal


PLAYER = "/Game/Normandy/Blueprints/Player/BP_NormandyPlayerCharacter"
WEAPON_CLASS = (
    "/Game/Normandy/Blueprints/Player/"
    "BP_WeaponComponent.BP_WeaponComponent_C"
)
library = unreal.BlueprintEditorLibrary
blueprint = unreal.EditorAssetLibrary.load_asset(PLAYER)
assert blueprint


def pin(node, name, output=False):
    finder = library.find_output_pin if output else library.find_input_pin
    return finder(node, name)


def connect(source, target):
    assert source.try_create_connection(target)


def make_request(name, function, result_name, kind):
    if library.find_graph(blueprint, name):
        return
    graph = unreal.BlueprintGraphEditor.create_and_edit_function_graph(blueprint, name)
    result = graph.add_graph_output_parameter(
        result_name, library.get_basic_type_by_name(kind)
    )
    component = graph.add_get_member_variable_node("WeaponComponent")
    call = graph.add_call_function_node(f"{WEAPON_CLASS}.{function}")
    assert component and call and result
    connect(pin(component, "WeaponComponent", True), pin(call, "self"))
    connect(graph.find_graph_entry_pin(), pin(call, "execute"))
    connect(pin(call, result_name, True), pin(result, result_name))
    connect(pin(call, "then", True), pin(result, "execute"))


make_request("TryFire", "RequestFire", "Accepted", "bool")
make_request("TryReload", "BeginReload", "StartedActionId", "int")
assert library.compile_blueprint(blueprint)
assert unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
unreal.log(f"G0_PLAYER_ACTIONS ready {PLAYER}")
