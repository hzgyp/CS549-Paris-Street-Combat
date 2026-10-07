"""New-only V2 sight author: Pawn owns sensing; controller owns private memory."""
import json
import os
import sys
import traceback
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match, package_file
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ue_paris_graph_helpers import lib, pins, pin, wire, value, call, pure, get, run, cast_to, place

IDENTITY = os.environ["CS549_NPC_IDENTITY"]
OUT = STORE / "Evidence/NPCInteractionV1" / IDENTITY
VERSION = os.environ.get("CS549_NPC_SIGHT_VERSION", "V2")
RESULT = OUT / os.environ.get("CS549_NPC_SIGHT_AUTHOR_RESULT", "b1_sight_author_v2.json")
PACKAGES = {
    "controller": DEST + "/BP_PCNPCControllerSight" + VERSION,
    "allied": DEST + "/BP_PCAlliedNPCSight" + VERSION,
    "german": DEST + "/BP_PCGermanNPCSight" + VERSION,
}
BB = DEST + "/BB_PC_NPCInteractionV1"
BT = DEST + "/BT_PC_NPCInteractionV1"
BASE = "/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2"
B0_ALLY = DEST + "/BP_PCAlliedNPCInteractionV1"
B0_GERMAN = DEST + "/BP_PCGermanNPCInteractionV1"
rows = guard_rows()
report = {
    "identity": IDENTITY,
    "scope": "new-only " + VERSION + ": Pawn-owned native sensing, faction filter, frozen private last-seen memory",
    "packages": [], "errors": [], "map_saved": False,
}


def math(graph, name, **inputs):
    return pure(graph, "/Script/Engine.KismetMathLibrary." + name, **inputs)


def branch(graph, flow, condition):
    node = graph.add_branch_node()
    wire(flow, lib.find_execute_pin(node))
    wire(condition, pin(node, "Condition"))
    return pin(node, "then", True), pin(node, "else", True)


def put(graph, flow, name, datum):
    node = graph.add_set_member_variable_node(name)
    value(pin(node, name), datum)
    return run(graph, flow, node)


def key(graph, name):
    return pure(graph, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value=name)


def cast_actor(graph, flow, obj, cls):
    type_ids = [name for name in graph.list_available_nodes([])
                if name.replace(" ", "").lower() == "utilities|casting|casttoactor"]
    assert type_ids, "CastToActor node type unavailable"
    report["cast_node_types"] = type_ids
    node = place(graph.create_node_from_name(type_ids[0], unreal.Vector2D(), []))
    assert graph.retarget_node_class(node, unreal.Actor.static_class(), cls)
    wire(obj, pin(node, "Object"))
    wire(flow, lib.find_execute_pin(node))
    outputs = [p for p in lib.list_all_pins(node) if str(pins.get_pin_name(p)).startswith("As")]
    assert len(outputs) == 1
    return lib.find_then_pin(node), outputs[0]


def save(bp, package):
    assert lib.compile_blueprint(bp), package
    errors = [str(node) for graph in lib.list_graphs(bp)
              for node in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
    assert not errors, (package, errors)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report["packages"].append(package)


def add_sensing(bp, controller_cls):
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    sublib = unreal.SubobjectDataBlueprintFunctionLibrary
    handles = subsystem.k2_gather_subobject_data_for_blueprint(bp)
    assert handles
    handle, reason = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(
        parent_handle=handles[0], new_class=unreal.PawnSensingComponent, blueprint_context=bp))
    assert sublib.is_handle_valid(handle), str(reason)
    assert subsystem.rename_subobject(handle, unreal.Text("NPCSight"))
    sensing = sublib.get_object_for_blueprint(sublib.get_data(handle), bp)
    assert sensing
    sensing.set_editor_property("sensing_interval", 0.25)
    sensing.set_editor_property("sight_radius", 2000.0)
    sensing.set_editor_property("peripheral_vision_angle", 90.0)
    sensing.set_editor_property("only_sense_players", False)
    for prop, datum in (("enable_sensing_updates", True), ("see_pawns", True)):
        try:
            sensing.set_editor_property(prop, datum)
        except Exception as exc:
            report.setdefault("optional_component_property_warnings", []).append(prop + ": " + str(exc))
    assert lib.compile_blueprint(bp)
    graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "EventGraph")
    seen_event = graph.add_component_bound_event_node(sensing, unreal.Name("OnSeePawn"))
    assert seen_event
    seen = lib.find_output_pin(seen_event, "Pawn")
    assert pins.is_valid(seen)
    controller = pure(graph, "/Script/Engine.Pawn.GetController")
    flow, typed_controller = cast_actor(graph, lib.find_then_pin(seen_event), controller, controller_cls)
    record_types = [name for name in graph.list_available_nodes([])
                    if "pcrecordsight" in name.replace(" ", "").lower()]
    assert record_types, "Public PC_RecordSight call type unavailable in Pawn graph"
    report.setdefault("record_call_types", {})[bp.get_name()] = record_types
    record = place(graph.create_node_from_name(record_types[0], unreal.Vector2D(), [], controller_cls))
    assert record
    value(pin(record, "SeenPawn"), seen)
    wire(typed_controller, lib.find_self_pin(record))
    run(graph, flow, record)
    return sensing


try:
    assert guards_match(rows)
    assert all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in PACKAGES.values())
    base_cls = unreal.EditorAssetLibrary.load_blueprint_class(BASE)
    b0_ally = unreal.EditorAssetLibrary.load_blueprint_class(B0_ALLY)
    b0_german = unreal.EditorAssetLibrary.load_blueprint_class(B0_GERMAN)
    assert base_cls and b0_ally and b0_german

    controller = lib.create_blueprint_asset_with_parent(PACKAGES["controller"], unreal.AIController.static_class())
    assert controller
    event_graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(controller, "EventGraph")
    assert event_graph.add_member_variable(
        "NPCBlackboard", lib.get_object_reference_type(unreal.BlackboardComponent.static_class()))
    assert lib.compile_blueprint(controller)

    begin = lib.add_event_override(controller, "ReceiveBeginPlay", unreal.IntPoint(0, 0))
    use = event_graph.add_call_function_node("UseBlackboard")
    run_tree = event_graph.add_call_function_node("RunBehaviorTree")
    value(lib.find_input_pin(use, "BlackboardAsset"), BB)
    value(lib.find_input_pin(run_tree, "BTAsset"), BT)
    flow = run(event_graph, lib.find_then_pin(begin), use)
    flow = put(event_graph, flow, "NPCBlackboard", lib.find_output_pin(use, "BlackboardComponent"))
    run(event_graph, flow, run_tree)

    record_graph = unreal.BlueprintGraphEditor.create_and_edit_function_graph(controller, "PC_RecordSight")
    record_graph.set_function_is_public()
    seen = record_graph.add_graph_input_parameter(
        "SeenPawn", lib.get_object_reference_type(unreal.Pawn.static_class()))
    flow, seen_combatant = cast_to(record_graph, record_graph.find_graph_entry_pin(), seen, base_cls)
    own_pawn = pure(record_graph, "/Script/Engine.Controller.K2_GetPawn")
    flow, own_combatant = cast_to(record_graph, flow, own_pawn, base_cls)
    hostile = math(record_graph, "NotEqual_IntInt",
                   A=get(record_graph, "TeamId", base_cls.get_path_name(), seen_combatant),
                   B=get(record_graph, "TeamId", base_cls.get_path_name(), own_combatant))
    flow, _ = branch(record_graph, flow, hostile)
    bb = get(record_graph, "NPCBlackboard")
    now = pure(record_graph, "/Script/Engine.GameplayStatics.GetTimeSeconds")
    location = pure(record_graph, "/Script/Engine.Actor.K2_GetActorLocation", self=seen_combatant)
    for function, args in (
        ("/Script/AIModule.BlackboardComponent.SetValueAsObject",
         {"self": bb, "KeyName": key(record_graph, "TargetActor"), "ObjectValue": seen_combatant}),
        ("/Script/AIModule.BlackboardComponent.SetValueAsVector",
         {"self": bb, "KeyName": key(record_graph, "LastSeenPosition"), "VectorValue": location}),
        ("/Script/AIModule.BlackboardComponent.SetValueAsFloat",
         {"self": bb, "KeyName": key(record_graph, "LastSeenTime"), "FloatValue": now}),
        ("/Script/AIModule.BlackboardComponent.SetValueAsBool",
         {"self": bb, "KeyName": key(record_graph, "HasVisibleTarget"), "BoolValue": True}),
    ):
        flow = run(record_graph, flow, call(record_graph, function, **args))

    tick = lib.add_event_override(controller, "ReceiveTick", unreal.IntPoint(0, 700))
    bb = get(event_graph, "NPCBlackboard")
    stale = math(event_graph, "Greater_DoubleDouble",
                 A=math(event_graph, "Subtract_DoubleDouble",
                        A=pure(event_graph, "/Script/Engine.GameplayStatics.GetTimeSeconds"),
                        B=pure(event_graph, "/Script/AIModule.BlackboardComponent.GetValueAsFloat",
                               self=bb, KeyName=key(event_graph, "LastSeenTime"))),
                 B=0.75)
    visible = pure(event_graph, "/Script/AIModule.BlackboardComponent.GetValueAsBool",
                   self=bb, KeyName=key(event_graph, "HasVisibleTarget"))
    flow, _ = branch(event_graph, lib.find_then_pin(tick), math(event_graph, "BooleanAND", A=visible, B=stale))
    run(event_graph, flow, call(event_graph, "/Script/AIModule.BlackboardComponent.SetValueAsBool",
                                self=bb, KeyName=key(event_graph, "HasVisibleTarget"), BoolValue=False))
    save(controller, PACKAGES["controller"])
    controller_cls = unreal.EditorAssetLibrary.load_blueprint_class(PACKAGES["controller"])
    assert controller_cls

    report["pawn_components"] = {}
    for label, parent in (("allied", b0_ally), ("german", b0_german)):
        bp = lib.create_blueprint_asset_with_parent(PACKAGES[label], parent)
        assert bp
        assert lib.compile_blueprint(bp)
        sensing = add_sensing(bp, controller_cls)
        cls = unreal.EditorAssetLibrary.load_blueprint_class(PACKAGES[label])
        cdo = unreal.get_default_object(cls)
        cdo.set_editor_property("ai_controller_class", controller_cls)
        cdo.set_editor_property("auto_possess_ai", unreal.AutoPossessAI.PLACED_IN_WORLD_OR_SPAWNED)
        report["pawn_components"][label] = {
            "owner_blueprint": PACKAGES[label],
            "class": sensing.get_class().get_name(),
            "events": [str(x) for x in unreal.BlueprintGraphEditor.get_graph_editor_by_name(
                bp, "EventGraph").list_component_events(sensing)],
        }
        save(bp, PACKAGES[label])

    report["status"] = "pass_b1_v2_pawn_owned_sensing_authored_requires_runtime"
except Exception:
    report["status"] = "failed_preserve_b1_v2_sensing_evidence"
    report["errors"].append(traceback.format_exc())
finally:
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    report["files"] = []
    for package in report["packages"]:
        path = package_file(package)
        if path.is_file():
            report["files"].append({
                "package": package, "path": path.relative_to(ROOT).as_posix(),
                "size_bytes": path.stat().st_size, "sha256": digest(path),
            })
    OUT.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
