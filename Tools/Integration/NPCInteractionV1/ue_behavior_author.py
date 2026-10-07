"""New-only real BT patrol/guard/path budget/lifecycle implementation."""
import json
import os
import sys
import traceback
from pathlib import Path

import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match, package_file
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ue_paris_graph_helpers import lib, pins, pin, wire, value, call, pure, get, run

VERSION = os.environ.get("CS549_NPC_BEHAVIOR_VERSION", "V1")
OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "behavior_author.json"
P = {key: DEST + "/" + name.removesuffix("V1") + VERSION for key, name in (
    ("tree", "BT_PC_NPCBehaviorV1"), ("controller", "BP_PCNPCBehaviorV1"),
    ("plan", "BTT_PC_NPCPlanV1"), ("arrive", "BTT_PC_NPCArriveV1"),
    ("failure", "BTT_PC_NPCFailureV1"), ("lifecycle", "BTS_PC_NPCLifecycleV1"),
    ("allied", "BP_PCAlliedBehaviorV1"), ("german", "BP_PCGermanBehaviorV1"))}
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "packages": [], "errors": [],
          "scope": "new-only native BT noncombat guard/patrol/full-path/two-replan/lifecycle; no formal selection"}


def math(g, name, **kw):
    return pure(g, "/Script/Engine.KismetMathLibrary." + name, **kw)


def branch(g, flow, condition):
    node = g.add_branch_node()
    wire(flow, lib.find_execute_pin(node))
    value(pin(node, "Condition"), condition)
    return pin(node, "then", True), pin(node, "else", True)


def put(g, flow, name, datum, target=None, cls=""):
    node = g.add_set_member_variable_node(name, cls)
    value(pin(node, name), datum)
    if target is not None:
        wire(target, lib.find_self_pin(node))
    return run(g, flow, node)


def key(g, name):
    return pure(g, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value=name)


def bbget(g, bb, name, kind):
    return pure(g, "/Script/AIModule.BlackboardComponent.GetValueAs" + kind, self=bb, KeyName=key(g, name))


def bbput(g, flow, bb, name, kind, datum):
    field = {"Bool": "BoolValue", "Int": "IntValue", "Name": "NameValue", "Vector": "VectorValue"}[kind]
    return run(g, flow, call(g, "/Script/AIModule.BlackboardComponent.SetValueAs" + kind,
                             self=bb, KeyName=key(g, name), **{field: datum}))


def cast(g, flow, obj, cls):
    types = [n for n in g.list_available_nodes([]) if n.replace(" ", "").lower() == "utilities|casting|casttoactor"]
    node = g.create_node_from_name(types[0], unreal.Vector2D(), [])
    assert g.retarget_node_class(node, unreal.Actor.static_class(), cls)
    value(pin(node, "Object"), obj)
    wire(flow, lib.find_execute_pin(node))
    out = [p for p in lib.list_all_pins(node) if str(pins.get_pin_name(p)).startswith("As")]
    assert len(out) == 1
    return lib.find_then_pin(node), out[0]


def save(asset, package):
    if isinstance(asset, unreal.Blueprint):
        assert lib.compile_blueprint(asset), package
        errors = [str(n) for g in lib.list_graphs(asset)
                  for n in unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors()]
        assert not errors, (package, errors)
    assert unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False)
    report["packages"].append(package)


def finish_task(g, flow, success=True):
    return run(g, flow, call(g, "/Script/AIModule.BTTask_BlueprintBase.FinishExecute", bSuccess=success))


def selector(name, kind):
    key_selector = unreal.BlackboardKeySelector()
    key_selector.set_editor_property("selected_key_name", unreal.Name(name))
    key_selector.set_editor_property("selected_key_type", unreal.load_class(None, "/Script/AIModule.BlackboardKeyType_" + kind))
    return key_selector


def children(root, tasks, decorators=None):
    result = []
    for i, task in enumerate(tasks):
        child = unreal.BTCompositeChild()
        child.set_editor_property("child_composite" if isinstance(task, unreal.BTCompositeNode) else "child_task", task)
        if decorators and i in decorators:
            child.set_editor_property("decorators", decorators[i])
        result.append(child)
    root.set_editor_property("children", result)


def scalar(node, field, datum):
    struct = node.get_editor_property(field)
    struct.set_editor_property("default_value", datum)
    node.set_editor_property(field, struct)


try:
    assert guards_match(rows)
    assert all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in P.values())
    base = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2")
    bb_asset = unreal.load_asset(DEST + "/BB_PC_NPCInteractionV1")
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tree = tools.create_asset(P["tree"].rsplit("/", 1)[1], DEST, unreal.BehaviorTree, unreal.BehaviorTreeFactory())
    tree.set_editor_property("blackboard_asset", bb_asset)
    controller = lib.create_blueprint_asset_with_parent(P["controller"],
        unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCNPCControllerSightV4"))
    cg = unreal.BlueprintGraphEditor.get_graph_editor_by_name(controller, "EventGraph")
    for name in ("PatrolEnabled", "HomeCaptured", "PatrolLeg"):
        assert cg.add_member_variable(name, lib.get_basic_type_by_name("bool"))
    for name in ("PatrolPoint", "HomePoint"):
        assert cg.add_member_variable(name, lib.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector")))
    assert lib.compile_blueprint(controller)
    begin = lib.add_event_override(controller, "ReceiveBeginPlay", unreal.IntPoint())
    use = cg.add_call_function_node("UseBlackboard")
    value(pin(use, "BlackboardAsset"), bb_asset.get_path_name())
    flow = run(cg, lib.find_then_pin(begin), use)
    flow = put(cg, flow, "NPCBlackboard", pin(use, "BlackboardComponent", True))
    run(cg, flow, call(cg, "/Script/AIModule.AIController.RunBehaviorTree", BTAsset=tree.get_path_name()))
    save(controller, P["controller"])
    ctrl_cls = unreal.EditorAssetLibrary.load_blueprint_class(P["controller"])
    cpath = ctrl_cls.get_path_name()

    assets = {}
    for name in ("plan", "arrive", "failure", "lifecycle"):
        parent = unreal.BTService_BlueprintBase if name == "lifecycle" else unreal.BTTask_BlueprintBase
        bp = lib.create_blueprint_asset_with_parent(P[name], parent.static_class())
        assert bp and lib.compile_blueprint(bp)
        g = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "EventGraph")
        event = lib.add_event_override(bp, "ReceiveTickAI" if name == "lifecycle" else "ReceiveExecuteAI", unreal.IntPoint())
        flow, ctrl = cast(g, lib.find_then_pin(event), pin(event, "OwnerController", True), ctrl_cls)
        flow, pawn = cast(g, flow, pin(event, "ControlledPawn", True), base)
        bb = get(g, "NPCBlackboard", cpath, ctrl)
        alive = math(g, "Greater_DoubleDouble", A=get(g, "Health", base.get_path_name(), pawn), B=0)

        if name == "plan":
            enabled = math(g, "BooleanAND", A=alive, B=get(g, "PatrolEnabled", cpath, ctrl))
            enabled = math(g, "BooleanAND", A=enabled, B=math(g, "NotEqual_NameName",
                A=bbget(g, bb, "WaitingReason", "Name"), B="PathExhausted"))
            active, idle = branch(g, flow, enabled)
            finish_task(g, idle, False)
            loc = pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=pawn)
            home = math(g, "SelectVector", A=get(g, "HomePoint", cpath, ctrl), B=loc,
                        bPickA=get(g, "HomeCaptured", cpath, ctrl))
            flow = put(g, active, "HomePoint", home, ctrl, cpath)
            flow = put(g, flow, "HomeCaptured", True, ctrl, cpath)
            # Select_Vector picks A for true.
            goal = math(g, "SelectVector", A=get(g, "HomePoint", cpath, ctrl),
                        B=get(g, "PatrolPoint", cpath, ctrl), bPickA=get(g, "PatrolLeg", cpath, ctrl))
            nav = call(g, "/Script/NavigationSystem.NavigationSystemV1.FindPathToLocationSynchronously",
                       PathStart=loc, PathEnd=goal, PathfindingContext=pawn)
            flow = run(g, flow, nav)
            path = pin(nav, "ReturnValue", True)
            present, absent = branch(g, flow, pure(g, "/Script/Engine.KismetSystemLibrary.IsValid", Object=path))
            absent = bbput(g, absent, bb, "WaitingReason", "Name", "PathInvalid")
            finish_task(g, absent, False)
            valid = call(g, "/Script/NavigationSystem.NavigationPath.IsValid", self=path)
            partial = call(g, "/Script/NavigationSystem.NavigationPath.IsPartial", self=path)
            # Const BlueprintCallable methods are exported as pure K2 nodes.
            flow = present
            for node in (valid, partial):
                if pins.is_valid(lib.find_execute_pin(node)):
                    flow = run(g, flow, node)
            good, bad = branch(g, flow, math(g, "BooleanAND", A=pin(valid, "ReturnValue", True),
                                           B=math(g, "Not_PreBool", A=pin(partial, "ReturnValue", True))))
            bad = bbput(g, bad, bb, "WaitingReason", "Name", "PathInvalid")
            finish_task(g, bad, False)
            for key_name in ("TaskID", "RequestID"):
                good = bbput(g, good, bb, key_name, "Int", math(g, "Add_IntInt", A=bbget(g, bb, key_name, "Int"), B=1))
            good = bbput(g, good, bb, "RestoreGeneration", "Int", get(g, "RestoreGeneration", base.get_path_name(), pawn))
            good = bbput(g, good, bb, "DesiredPosition", "Vector", goal)
            good = bbput(g, good, bb, "HasMoveGoal", "Bool", True)
            good = bbput(g, good, bb, "WaitingReason", "Name", "MoveStarted")
            finish_task(g, good)
        elif name == "arrive":
            flow = put(g, flow, "PatrolLeg", math(g, "Not_PreBool", A=get(g, "PatrolLeg", cpath, ctrl)), ctrl, cpath)
            flow = bbput(g, flow, bb, "HasMoveGoal", "Bool", False)
            flow = bbput(g, flow, bb, "RetryCount", "Int", 0)
            flow = bbput(g, flow, bb, "WaitingReason", "Name", "Arrived")
            finish_task(g, flow)
        elif name == "failure":
            reason = bbget(g, bb, "WaitingReason", "Name")
            needs_retry = math(g, "BooleanOR", A=math(g, "EqualEqual_NameName", A=reason, B="PathInvalid"),
                               B=math(g, "EqualEqual_NameName", A=reason, B="MoveStarted"))
            yes, no = branch(g, flow, needs_retry)
            finish_task(g, no)
            retry, exhausted = branch(g, yes, math(g, "Less_IntInt", A=bbget(g, bb, "RetryCount", "Int"), B=2))
            retry = bbput(g, retry, bb, "RetryCount", "Int", math(g, "Add_IntInt", A=bbget(g, bb, "RetryCount", "Int"), B=1))
            retry = bbput(g, retry, bb, "WaitingReason", "Name", "PathRetry")
            finish_task(g, retry)
            exhausted = bbput(g, exhausted, bb, "HasMoveGoal", "Bool", False)
            exhausted = bbput(g, exhausted, bb, "WaitingReason", "Name", "PathExhausted")
            finish_task(g, exhausted)
        else:
            changed = math(g, "NotEqual_IntInt", A=bbget(g, bb, "RestoreGeneration", "Int"),
                           B=get(g, "RestoreGeneration", base.get_path_name(), pawn))
            cancel, _ = branch(g, flow, math(g, "BooleanOR", A=math(g, "Not_PreBool", A=alive), B=changed))
            cancel = bbput(g, cancel, bb, "HasMoveGoal", "Bool", False)
            cancel = run(g, cancel, call(g, "/Script/Engine.Controller.StopMovement", self=ctrl))
            cancel = run(g, cancel, call(g, "/Script/AIModule.BlackboardComponent.ClearValue", self=bb, KeyName=key(g, "TargetActor")))
            cancel = bbput(g, cancel, bb, "HasVisibleTarget", "Bool", False)
            cancel = bbput(g, cancel, bb, "RequestID", "Int", 0)
            cancel = bbput(g, cancel, bb, "RetryCount", "Int", 0)
            cancel = bbput(g, cancel, bb, "RestoreGeneration", "Int", get(g, "RestoreGeneration", base.get_path_name(), pawn))
            bbput(g, cancel, bb, "WaitingReason", "Name", "LifecycleCancelled")
        save(bp, P[name])
        cls = unreal.EditorAssetLibrary.load_blueprint_class(P[name])
        assets[name] = cls

    root = unreal.new_object(unreal.BTComposite_Selector, outer=tree)
    root.set_editor_property("node_name", "Native guard/patrol and bounded fallback")
    service = unreal.new_object(assets["lifecycle"], outer=tree)
    service.set_editor_property("interval", .1)
    service.set_editor_property("random_deviation", 0.0)
    root.set_editor_property("services", [service])
    patrol = unreal.new_object(unreal.BTComposite_Sequence, outer=tree)
    move = unreal.new_object(unreal.BTTask_MoveTo, outer=tree)
    move.set_editor_property("blackboard_key", selector("DesiredPosition", "Vector"))
    for field, datum in (("allow_partial_path", False), ("project_goal_location", False),
                         ("reach_test_includes_agent_radius", False), ("reach_test_includes_goal_radius", False),
                         ("acceptable_radius", 35.0)):
        scalar(move, field, datum)
    decorator = unreal.new_object(unreal.BTDecorator_Blackboard, outer=tree)
    decorator.set_editor_property("blackboard_key", selector("HasMoveGoal", "Bool"))
    decorator.set_editor_property("basic_operation", unreal.BasicKeyOperation.SET)
    decorator.set_editor_property("flow_abort_mode", unreal.BTFlowAbortMode.SELF)
    wait = unreal.new_object(unreal.BTTask_Wait, outer=tree)
    scalar(wait, "wait_time", .5)
    children(patrol, [unreal.new_object(assets["plan"], outer=tree), move,
                      unreal.new_object(assets["arrive"], outer=tree), wait], {1: [decorator]})
    fallback = unreal.new_object(unreal.BTComposite_Sequence, outer=tree)
    idle = unreal.new_object(unreal.BTTask_Wait, outer=tree)
    scalar(idle, "wait_time", .5)
    children(fallback, [unreal.new_object(assets["failure"], outer=tree), idle])
    children(root, [patrol, fallback])
    tree.set_editor_property("root_node", root)
    save(tree, P["tree"])
    for label in ("allied", "german"):
        parent_name = "BP_PCAlliedNPCSightV4" if label == "allied" else "BP_PCGermanNPCSightV4"
        bp = lib.create_blueprint_asset_with_parent(P[label], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + parent_name))
        assert lib.compile_blueprint(bp)
        cdo = unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(P[label]))
        cdo.set_editor_property("ai_controller_class", ctrl_cls)
        save(bp, P[label])
    report["status"] = "pass_native_behavior_authored_requires_city"
except Exception:
    report["status"] = "failed_behavior_author_preserve"
    report["errors"].append(traceback.format_exc())
finally:
    report["files"] = []
    for package in report["packages"]:
        file = package_file(package)
        if file.is_file():
            report["files"].append({"package": package, "path": file.relative_to(ROOT).as_posix(),
                                    "size_bytes": file.stat().st_size, "sha256": digest(file)})
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
