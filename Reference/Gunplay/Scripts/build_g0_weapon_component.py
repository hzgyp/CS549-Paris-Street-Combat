"""Create the Blueprint ammo state core for the G0 animation lab."""

import unreal


PATH = "/Game/Normandy/Blueprints/Player/BP_WeaponComponent"
L = unreal.BlueprintEditorLibrary


def need(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def input_pin(node, name):
    return need(L.find_input_pin(node, name), f"Input pin {node.get_name()}.{name}")


def output_pin(node, name):
    return need(L.find_output_pin(node, name), f"Output pin {node.get_name()}.{name}")


def wire(source, target):
    need(source.try_create_connection(target), "Blueprint pin connection failed")


def literal(node, name, value):
    need(input_pin(node, name).set_pin_value(str(value)), f"Pin value {name}={value}")


def call(graph, function, x, y):
    node = need(
        graph.add_call_function_node(f"/Script/Engine.KismetMathLibrary.{function}"),
        function,
    )
    node.set_node_pos(unreal.IntPoint(x, y))
    return node


def get(graph, name, x, y):
    node = need(graph.add_get_member_variable_node(name), f"Get {name}")
    node.set_node_pos(unreal.IntPoint(x, y))
    return output_pin(node, name)


def set_var(graph, name, x, y):
    node = need(graph.add_set_member_variable_node(name), f"Set {name}")
    node.set_node_pos(unreal.IntPoint(x, y))
    return node


def math(graph, function, a, b, x, y):
    node = call(graph, function, x, y)
    wire(a, input_pin(node, "A"))
    if hasattr(b, "try_create_connection"):
        wire(b, input_pin(node, "B"))
    else:
        literal(node, "B", b)
    return output_pin(node, "ReturnValue")


def negate(graph, value, x, y):
    node = call(graph, "Not_PreBool", x, y)
    wire(value, input_pin(node, "A"))
    return output_pin(node, "ReturnValue")


def all_true(graph, values, x, y):
    result = values[0]
    for index, value in enumerate(values[1:]):
        result = math(graph, "BooleanAND", result, value, x + 170 * index, y)
    return result


def output(graph, name, type_name):
    node = graph.add_graph_output_parameter(name, L.get_basic_type_by_name(type_name))
    need(node, f"Output {name}")
    return node


def branch(graph, condition, x, y):
    node = need(graph.add_branch_node(), "Branch")
    node.set_node_pos(unreal.IntPoint(x, y))
    wire(graph.find_graph_entry_pin(), input_pin(node, "execute"))
    wire(condition, input_pin(node, "Condition"))
    return node


def return_value(graph, node, name, value, x, y):
    node.set_node_pos(unreal.IntPoint(x, y))
    if hasattr(value, "try_create_connection"):
        wire(value, input_pin(node, name))
    else:
        literal(node, name, value)
    return node


def build_fire(bp):
    graph = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, "RequestFire")
    result_true = output(graph, "Accepted", "bool")
    result_false = need(graph.add_return_node(), "False return")
    ammo = get(graph, "MagAmmo", -900, -400)
    has_ammo = math(graph, "Greater_IntInt", ammo, 0, -680, -400)
    no_reload = negate(graph, get(graph, "bReloading", -900, -200), -680, -200)
    enabled = negate(graph, get(graph, "bDisabled", -900, 0), -680, 0)
    condition = all_true(graph, [has_ammo, no_reload, enabled], -400, -300)
    decision = branch(graph, condition, 0, 0)
    set_ammo = set_var(graph, "MagAmmo", 350, -100)
    wire(output_pin(decision, "then"), input_pin(set_ammo, "execute"))
    remaining = math(graph, "Subtract_IntInt", get(graph, "MagAmmo", 50, -400), 1, 270, -400)
    wire(remaining, input_pin(set_ammo, "MagAmmo"))
    return_value(graph, result_true, "Accepted", "true", 650, -100)
    return_value(graph, result_false, "Accepted", "false", 350, 200)
    wire(output_pin(set_ammo, "then"), input_pin(result_true, "execute"))
    wire(output_pin(decision, "else"), input_pin(result_false, "execute"))


def build_begin_reload(bp):
    graph = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, "BeginReload")
    accepted = output(graph, "StartedActionId", "int")
    rejected = need(graph.add_return_node(), "Rejected return")
    room = math(
        graph, "Less_IntInt", get(graph, "MagAmmo", -1200, -600),
        get(graph, "Capacity", -1200, -400), -950, -500,
    )
    reserve = math(graph, "Greater_IntInt", get(graph, "ReserveAmmo", -1200, -200), 0, -950, -200)
    idle = negate(graph, get(graph, "bReloading", -1200, 0), -950, 0)
    enabled = negate(graph, get(graph, "bDisabled", -1200, 200), -950, 200)
    decision = branch(graph, all_true(graph, [room, reserve, idle, enabled], -650, -300), 0, 0)
    clear_commit = set_var(graph, "ReloadCommitted", 300, -200)
    literal(clear_commit, "ReloadCommitted", "false")
    set_reloading = set_var(graph, "bReloading", 550, -200)
    literal(set_reloading, "bReloading", "true")
    set_action = set_var(graph, "ActionId", 800, -200)
    next_action = math(graph, "Add_IntInt", get(graph, "ActionId", 300, -550), 1, 550, -550)
    wire(next_action, input_pin(set_action, "ActionId"))
    wire(output_pin(decision, "then"), input_pin(clear_commit, "execute"))
    wire(output_pin(clear_commit, "then"), input_pin(set_reloading, "execute"))
    wire(output_pin(set_reloading, "then"), input_pin(set_action, "execute"))
    return_value(graph, accepted, "StartedActionId", output_pin(set_action, "Output_Get"), 1100, -200)
    return_value(graph, rejected, "StartedActionId", "-1", 300, 200)
    wire(output_pin(set_action, "then"), input_pin(accepted, "execute"))
    wire(output_pin(decision, "else"), input_pin(rejected, "execute"))


def build_commit_reload(bp):
    graph = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, "CommitReload")
    need(
        graph.add_local_variable(
            "Transfer", L.get_basic_type_by_name("int"), "0"
        ),
        "Local Transfer",
    )
    expected = graph.add_graph_input_parameter("ExpectedActionId", L.get_basic_type_by_name("int"))
    need(expected, "ExpectedActionId input")
    committed = output(graph, "Committed", "bool")
    rejected = need(graph.add_return_node(), "Rejected return")
    match = math(
        graph, "EqualEqual_IntInt", expected,
        get(graph, "ActionId", -1500, -500), -1200, -500,
    )
    no_duplicate = negate(graph, get(graph, "ReloadCommitted", -1500, -300), -1200, -300)
    loading = get(graph, "bReloading", -1500, -100)
    decision = branch(graph, all_true(graph, [match, no_duplicate, loading], -900, -400), -100, 0)
    space = math(
        graph, "Subtract_IntInt", get(graph, "Capacity", -800, -800),
        get(graph, "MagAmmo", -800, -650), -550, -750,
    )
    transfer = math(graph, "Min", space, get(graph, "ReserveAmmo", -800, -500), -300, -700)
    save_transfer = need(graph.add_set_local_variable_node("Transfer"), "Cache Transfer")
    save_transfer.set_node_pos(unreal.IntPoint(100, -100))
    wire(transfer, input_pin(save_transfer, "Transfer"))
    cached_mag = need(graph.add_get_local_variable_node("Transfer"), "Read Transfer")
    cached_reserve = need(graph.add_get_local_variable_node("Transfer"), "Read Transfer")
    next_mag = math(
        graph, "Add_IntInt", get(graph, "MagAmmo", -250, -450),
        output_pin(cached_mag, "Transfer"), 0, -500,
    )
    next_reserve = math(
        graph, "Subtract_IntInt", get(graph, "ReserveAmmo", -250, -250),
        output_pin(cached_reserve, "Transfer"), 0, -250,
    )
    set_mag = set_var(graph, "MagAmmo", 250, -100)
    set_reserve = set_var(graph, "ReserveAmmo", 500, -100)
    set_flag = set_var(graph, "ReloadCommitted", 750, -100)
    wire(next_mag, input_pin(set_mag, "MagAmmo"))
    wire(next_reserve, input_pin(set_reserve, "ReserveAmmo"))
    literal(set_flag, "ReloadCommitted", "true")
    wire(output_pin(decision, "then"), input_pin(save_transfer, "execute"))
    wire(output_pin(save_transfer, "then"), input_pin(set_mag, "execute"))
    wire(output_pin(set_mag, "then"), input_pin(set_reserve, "execute"))
    wire(output_pin(set_reserve, "then"), input_pin(set_flag, "execute"))
    return_value(graph, committed, "Committed", "true", 1000, -100)
    return_value(graph, rejected, "Committed", "false", 250, 200)
    wire(output_pin(set_flag, "then"), input_pin(committed, "execute"))
    wire(output_pin(decision, "else"), input_pin(rejected, "execute"))


def build_end_reload(bp):
    graph = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, "EndReload")
    expected = need(
        graph.add_graph_input_parameter("ExpectedActionId", L.get_basic_type_by_name("int")),
        "ExpectedActionId input",
    )
    current = get(graph, "ActionId", -800, -200)
    matching = math(graph, "EqualEqual_IntInt", expected, current, -550, -200)
    loading = get(graph, "bReloading", -800, 0)
    decision = branch(graph, math(graph, "BooleanAND", matching, loading, -300, -100), 0, 0)
    clear = set_var(graph, "bReloading", 250, 0)
    literal(clear, "bReloading", "false")
    wire(output_pin(decision, "then"), input_pin(clear, "execute"))
    return graph


if unreal.EditorAssetLibrary.does_asset_exist(PATH):
    blueprint = need(unreal.EditorAssetLibrary.load_asset(PATH), "Load weapon Blueprint")
    # Rebuild after edits so the checked-in script remains the source of truth.
    L.remove_function_graph(blueprint, "EndReload")
    upgraded = build_end_reload(blueprint)
    L.rename_graph(upgraded.get_graph(), "EndReload")
    need(L.compile_blueprint(blueprint), "Compile weapon Blueprint")
    need(unreal.EditorAssetLibrary.save_loaded_asset(blueprint), "Save weapon Blueprint")
    unreal.log(f"G0_WEAPON updated EndReload in {PATH}")
else:
    blueprint = need(
        L.create_blueprint_asset_with_parent(PATH, unreal.ActorComponent.static_class()),
        "Create weapon Blueprint",
    )
    graph = unreal.BlueprintGraphEditor.create_and_edit_function_graph(blueprint, "WeaponSetup")
    values = [
        ("Capacity", "int", "8"), ("MagAmmo", "int", "8"),
        ("ReserveAmmo", "int", "24"), ("ActionId", "int", "0"),
        ("bReloading", "bool", "false"),
        ("ReloadCommitted", "bool", "false"),
        ("bDisabled", "bool", "false"),
    ]
    for name, kind, default in values:
        need(graph.add_member_variable(name, L.get_basic_type_by_name(kind), default), name)
    L.remove_function_graph(blueprint, "WeaponSetup")
    build_fire(blueprint)
    build_begin_reload(blueprint)
    build_commit_reload(blueprint)
    build_end_reload(blueprint)
    need(L.compile_blueprint(blueprint), "Compile weapon Blueprint")
    need(unreal.EditorAssetLibrary.save_loaded_asset(blueprint), "Save weapon Blueprint")
    unreal.log(f"G0_WEAPON created {PATH}")
