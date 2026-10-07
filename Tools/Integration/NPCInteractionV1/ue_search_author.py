"""New-only finite German search service over the real, retained V3 BT leaves."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match, package_file
from ue_graph import lib, pins, pin, wire, value, call, pure, get, run, math, branch, put, bbget, bbput, function, invoke, distance, cast

VERSION = os.environ.get("CS549_NPC_BEHAVIOR_VERSION", "V1")
OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "search_author.json"
P = {key: DEST + "/" + name + VERSION for key, name in (
    ("controller", "BP_PCNPCSearch"), ("tree", "BT_PC_NPCSearch"),
    ("service", "BTS_PC_NPCSearch"), ("allied", "BP_PCAlliedSearch"), ("german", "BP_PCGermanSearch"))}
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "packages": [], "errors": [],
          "scope": "German noncombat native finite frozen-memory search/role return; Allied tactics not yet implemented"}
settings = None
original_promotion = None
promotion_property = None


def checkpoint(stage):
    report["last_author_stage"] = stage
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.log("NPC_SEARCH_AUTHOR_STAGE " + stage)


def compile(bp):
    assert lib.compile_blueprint(bp)
    errors = [str(n) for g in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors()]
    assert not errors, errors


def save(bp, package):
    if isinstance(bp, unreal.Blueprint):
        compile(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report["packages"].append(package)


def local(g):
    return pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=pure(g, "/Script/Engine.Controller.K2_GetPawn"))


try:
    assert guards_match(rows) and all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in P.values())
    # Process-local author setting only; save ordinary fixed-signature K2 calls.
    # No .uproject/Config/global user-setting change, and no old asset rewrite.
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/BlueprintGraph.BlueprintEditorSettings"))
    report["promotion_attribute_names"] = [name for name in dir(settings) if "promo" in name.lower()]
    for candidate in ("bEnableTypePromotion", "EnableTypePromotion", "enable_type_promotion"):
        try:
            original_promotion = settings.get_editor_property(candidate)
            promotion_property = candidate
            break
        except Exception as exc:
            report.setdefault("promotion_property_diagnostics", []).append(str(exc))
    assert promotion_property is not None, "Type promotion property unavailable; do not claim disabled"
    settings.set_editor_property(promotion_property, False)
    assert settings.get_editor_property(promotion_property) is False
    report["author_type_promotion"] = {"original": original_promotion, "temporary": False, "save_config_called": False}
    checkpoint("fixed-signature author mode verified in memory")
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tree = tools.duplicate_asset(P["tree"].rsplit("/", 1)[1], DEST, unreal.load_asset(DEST + "/BT_PC_NPCBehaviorV3"))
    assert tree
    checkpoint("tree duplicated in memory")
    bp = lib.create_blueprint_asset_with_parent(P["controller"], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCNPCBehaviorV4"))
    ev = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "EventGraph")
    for name, kind, default in (
        ("PolicyEnabled", "bool", "false"), ("AnchorCaptured", "bool", "false"),
        ("SearchActive", "bool", "false"), ("GoalInitialized", "bool", "false"),
        ("RolePatrol", "bool", "false"), ("RoleLeg", "bool", "false"),
        ("SearchIndex", "int", "0"), ("SearchVisitedCount", "int", "0"),
        ("PolicyGeneration", "int", "0"), ("SearchConsumedSightTime", "real", "0"),
        ("PolicyDeadline", "real", "0"), ("SearchRadius", "real", "200"),
        ("PolicyState", "name", "Guard")):
        assert ev.add_member_variable(name, lib.get_basic_type_by_name(kind), default)
    for name in ("GuardAnchor", "RolePatrolPoint", "SearchOrigin", "PolicyGoal"):
        assert ev.add_member_variable(name, lib.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector")))
    compile(bp)
    checkpoint("controller variables compiled")
    begin = lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint())
    use = ev.add_call_function_node("UseBlackboard")
    value(pin(use, "BlackboardAsset"), DEST + "/BB_PC_NPCInteractionV1")
    flow = run(ev, lib.find_then_pin(begin), use)
    flow = put(ev, flow, "NPCBlackboard", pin(use, "BlackboardComponent", True))
    run(ev, flow, call(ev, "/Script/AIModule.AIController.RunBehaviorTree", BTAsset=tree.get_path_name()))
    checkpoint("begin graph wired")

    g, flow, args = function(bp, "PC_EnablePolicy", (("Enabled", "bool"),))
    put(g, flow, "PolicyEnabled", args[0])
    checkpoint("enable policy wired")
    g, flow, args = function(bp, "PC_SetSearchRole", (("Patrol", "bool"), ("PatrolPoint", "Vector"), ("Radius", "real")))
    flow = put(g, flow, "RolePatrol", args[0])
    flow = put(g, flow, "RolePatrolPoint", args[1])
    put(g, flow, "SearchRadius", math(g, "FClamp", Value=args[2], Min=100, Max=1500))
    checkpoint("role config wired")
    g, flow, _ = function(bp, "PC_PolicyHold")
    flow = put(g, flow, "PatrolEnabled", False)
    flow = bbput(g, flow, "HasMoveGoal", "Bool", False)
    invoke(g, flow, "/Script/Engine.Controller.StopMovement")
    checkpoint("hold wired")
    g, flow, args = function(bp, "PC_StartPolicyGoal", (("Goal", "Vector"),))
    flow = put(g, flow, "PatrolPoint", args[0])
    flow = put(g, flow, "HomePoint", args[0])
    flow = put(g, flow, "HomeCaptured", True)
    put(g, flow, "PatrolEnabled", True)
    compile(bp)
    checkpoint("goal primitives compiled")

    g, flow, args = function(bp, "PC_GotoPolicyGoal", (("Goal", "Vector"), ("State", "name")))
    goal, state = args
    flow = put(g, flow, "PolicyState", state)
    near, far = branch(g, flow, math(g, "LessEqual_DoubleDouble", A=distance(g, local(g), goal), B=50))
    invoke(g, near, "PC_PolicyHold")
    changed = math(g, "BooleanOR", A=math(g, "Not_PreBool", A=get(g, "GoalInitialized")),
                   B=math(g, "Greater_DoubleDouble", A=distance(g, get(g, "PolicyGoal"), goal), B=50))
    yes, no = branch(g, far, changed)
    yes = invoke(g, yes, "PC_PolicyHold")
    yes = put(g, yes, "PolicyGoal", goal)
    yes = put(g, yes, "GoalInitialized", True)
    yes = bbput(g, yes, "RetryCount", "Int", 0)
    yes = bbput(g, yes, "WaitingReason", "Name", "PolicyGoalAssigned")
    invoke(g, yes, "PC_StartPolicyGoal", Goal=goal)
    invoke(g, no, "PC_StartPolicyGoal", Goal=goal)
    compile(bp)
    checkpoint("goto compiled")

    g, flow, _ = function(bp, "PC_PolicyRole")
    checkpoint("role function created")
    patrol, guard = branch(g, flow, get(g, "RolePatrol"))
    checkpoint("role branch created")
    invoke(g, guard, "PC_GotoPolicyGoal", Goal=get(g, "GuardAnchor"), State="GuardReturn")
    checkpoint("role guard goal wired")
    goal = math(g, "SelectVector", A=get(g, "GuardAnchor"), B=get(g, "RolePatrolPoint"), bPickA=get(g, "RoleLeg"))
    near, far = branch(g, patrol, math(g, "LessEqual_DoubleDouble", A=distance(g, local(g), goal), B=50))
    near = put(g, near, "RoleLeg", math(g, "Not_PreBool", A=get(g, "RoleLeg")))
    invoke(g, near, "PC_PolicyHold")
    invoke(g, far, "PC_GotoPolicyGoal", Goal=goal, State="RolePatrol")
    compile(bp)
    checkpoint("role compiled")

    g, flow, _ = function(bp, "PC_SearchTick")
    done = math(g, "BooleanOR", A=math(g, "GreaterEqual_IntInt", A=get(g, "SearchIndex"), B=5),
                B=math(g, "GreaterEqual_DoubleDouble", A=pure(g, "/Script/Engine.GameplayStatics.GetTimeSeconds"), B=get(g, "PolicyDeadline")))
    finish, active = branch(g, flow, done)
    finish = put(g, finish, "SearchActive", False)
    finish = put(g, finish, "SearchConsumedSightTime", bbget(g, "LastSeenTime", "Float"))
    finish = put(g, finish, "PolicyState", "SearchFinished")
    invoke(g, finish, "PC_PolicyRole")
    goal = get(g, "SearchOrigin")
    offsets = ((1, 1, 0), (2, -1, 0), (3, 0, 1), (4, 0, -1))
    for index, dx, dy in offsets:
        offset = pure(g, "/Script/Engine.KismetMathLibrary.MakeVector",
                      X=math(g, "Multiply_DoubleDouble", A=get(g, "SearchRadius"), B=dx),
                      Y=math(g, "Multiply_DoubleDouble", A=get(g, "SearchRadius"), B=dy), Z=0)
        transform = math(g, "MakeTransform", Location=get(g, "SearchOrigin"))
        candidate = math(g, "TransformLocation", T=transform, Location=offset)
        goal = math(g, "SelectVector", A=candidate, B=goal,
                    bPickA=math(g, "EqualEqual_IntInt", A=get(g, "SearchIndex"), B=index))
    near = math(g, "LessEqual_DoubleDouble", A=distance(g, local(g), goal), B=50)
    exhausted = math(g, "EqualEqual_NameName", A=bbget(g, "WaitingReason", "Name"), B="PathExhausted")
    advance, moving = branch(g, active, math(g, "BooleanOR", A=near, B=exhausted))
    # Pure Blueprint nodes are evaluated at their consuming exec node. Count the
    # OLD point before changing SearchIndex, otherwise `near` reads the next goal.
    increment = math(g, "SelectInt", A=1, B=0, bPickA=near)
    advance = put(g, advance, "SearchVisitedCount", math(g, "Add_IntInt", A=get(g, "SearchVisitedCount"), B=increment))
    advance = put(g, advance, "SearchIndex", math(g, "Add_IntInt", A=get(g, "SearchIndex"), B=1))
    advance = bbput(g, advance, "WaitingReason", "Name", "SearchPointDone")
    invoke(g, advance, "PC_PolicyHold")
    invoke(g, moving, "PC_GotoPolicyGoal", Goal=goal, State="Search")
    compile(bp)
    checkpoint("search compiled")

    g, flow, _ = function(bp, "PC_UpdatePolicy")
    flow, _ = branch(g, flow, get(g, "PolicyEnabled"))
    base = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2")
    flow, pawn = cast(g, flow, pure(g, "/Script/Engine.Controller.K2_GetPawn"), base)
    anchor = math(g, "SelectVector", A=get(g, "GuardAnchor"), B=local(g), bPickA=get(g, "AnchorCaptured"))
    flow = put(g, flow, "GuardAnchor", anchor)
    flow = put(g, flow, "AnchorCaptured", True)
    changed = math(g, "NotEqual_IntInt", A=get(g, "PolicyGeneration"), B=get(g, "RestoreGeneration", base.get_path_name(), pawn))
    flow = put(g, flow, "SearchActive", math(g, "BooleanAND", A=get(g, "SearchActive"), B=math(g, "Not_PreBool", A=changed)))
    flow = put(g, flow, "SearchConsumedSightTime", math(g, "SelectFloat", A=bbget(g, "LastSeenTime", "Float"), B=get(g, "SearchConsumedSightTime"), bPickA=changed))
    flow = put(g, flow, "PolicyGeneration", get(g, "RestoreGeneration", base.get_path_name(), pawn))
    alive, dead = branch(g, flow, math(g, "Greater_DoubleDouble", A=get(g, "Health", base.get_path_name(), pawn), B=0))
    dead = put(g, dead, "SearchActive", False)
    dead = put(g, dead, "SearchConsumedSightTime", bbget(g, "LastSeenTime", "Float"))
    invoke(g, dead, "PC_PolicyHold")
    german, _ = branch(g, alive, math(g, "EqualEqual_IntInt", A=get(g, "TeamId", base.get_path_name(), pawn), B=1))
    visible, lost = branch(g, german, bbget(g, "HasVisibleTarget", "Bool"))
    visible = put(g, visible, "SearchActive", False)
    visible = put(g, visible, "PolicyState", "VisibleUnarmedIntent")
    near, far = branch(g, visible, math(g, "LessEqual_DoubleDouble", A=distance(g, local(g), bbget(g, "LastSeenPosition", "Vector")), B=600))
    invoke(g, near, "PC_PolicyHold")
    invoke(g, far, "PC_GotoPolicyGoal", Goal=bbget(g, "LastSeenPosition", "Vector"), State="VisibleUnarmedApproach")
    searching, not_searching = branch(g, lost, get(g, "SearchActive"))
    invoke(g, searching, "PC_SearchTick")
    new, old = branch(g, not_searching, math(g, "Greater_DoubleDouble", A=bbget(g, "LastSeenTime", "Float"), B=get(g, "SearchConsumedSightTime")))
    invoke(g, old, "PC_PolicyRole")
    new = put(g, new, "SearchActive", True)
    new = put(g, new, "SearchIndex", 0)
    new = put(g, new, "SearchVisitedCount", 0)
    new = put(g, new, "SearchOrigin", bbget(g, "LastSeenPosition", "Vector"))
    deadline = math(g, "Add_DoubleDouble", A=pure(g, "/Script/Engine.GameplayStatics.GetTimeSeconds"), B=15)
    new = put(g, new, "PolicyDeadline", deadline)
    new = bbput(g, new, "SearchDeadline", "Float", get(g, "PolicyDeadline"))
    invoke(g, new, "PC_SearchTick")
    save(bp, P["controller"])
    checkpoint("controller saved")
    ctrl_cls = unreal.EditorAssetLibrary.load_blueprint_class(P["controller"])

    service_bp = lib.create_blueprint_asset_with_parent(P["service"], unreal.BTService_BlueprintBase.static_class())
    compile(service_bp)
    sg = unreal.BlueprintGraphEditor.get_graph_editor_by_name(service_bp, "EventGraph")
    event = lib.add_event_override(service_bp, "ReceiveTickAI", unreal.IntPoint())
    flow, typed = cast(sg, lib.find_then_pin(event), pin(event, "OwnerController", True), ctrl_cls)
    types = [n for n in sg.list_available_nodes([]) if "pcupdatepolicy" in n.replace(" ", "").lower()]
    assert types
    node = sg.create_node_from_name(types[0], unreal.Vector2D(), [], ctrl_cls)
    wire(typed, lib.find_self_pin(node))
    run(sg, flow, node)
    save(service_bp, P["service"])
    checkpoint("service saved")
    service = unreal.new_object(unreal.EditorAssetLibrary.load_blueprint_class(P["service"]), outer=tree)
    service.set_editor_property("interval", .2)
    service.set_editor_property("random_deviation", 0.0)
    root = tree.get_editor_property("root_node")
    root.set_editor_property("services", list(root.get_editor_property("services")) + [service])
    save(tree, P["tree"])
    checkpoint("tree saved")
    for label, prefix in (("allied", "BP_PCAlliedBehavior"), ("german", "BP_PCGermanBehavior")):
        child = lib.create_blueprint_asset_with_parent(P[label], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + prefix + "V4"))
        compile(child)
        unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(P[label])).set_editor_property("ai_controller_class", ctrl_cls)
        save(child, P[label])
    report["status"] = "pass_native_search_authored_requires_city"
except Exception:
    report["status"] = "failed_search_author_preserve"
    report["errors"].append(traceback.format_exc())
finally:
    if settings is not None and original_promotion is not None:
        settings.set_editor_property(promotion_property, original_promotion)
        report["author_type_promotion"]["restored"] = settings.get_editor_property(promotion_property) == original_promotion
    report["files"] = []
    for package in report["packages"]:
        file = package_file(package)
        report["files"].append({"package": package, "path": file.relative_to(ROOT).as_posix(), "size_bytes": file.stat().st_size, "sha256": digest(file)})
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
