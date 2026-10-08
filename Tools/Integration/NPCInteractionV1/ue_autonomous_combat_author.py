"""New shared native BT service: selected-equipment Stop/Turn/Fire/Reload."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match, package_file
from ue_graph import lib, pins, pin, wire, value, call, pure, get, run, math, branch, put, bbget, bbput, function, invoke, distance, cast

VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
P = {k: DEST + "/" + n + VERSION for k, n in (("controller", "BP_PCNPCCombat"), ("tree", "BT_PC_NPCCombat"),
    ("service", "BTS_PC_NPCCombat"), ("allied", "BP_PCAlliedCombat"), ("german", "BP_PCGermanCombat"))}
OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "autonomous_combat_author.json"
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "packages": [], "files": [],
          "scope": "native autonomous decisions only; exact selected policy equipment; no formal map or presentation mutation"}
settings = original = None


def compile(bp):
    assert lib.compile_blueprint(bp)
    assert all(not unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors() for g in lib.list_graphs(bp))


def save(bp, p):
    if isinstance(bp, unreal.Blueprint):
        compile(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    report["packages"].append(p)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")


def own(g):
    return pure(g, "/Script/Engine.Controller.K2_GetPawn")


def local(g):
    return pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=own(g))


try:
    assert guards_match(rows) and all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in P.values())
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/BlueprintGraph.BlueprintEditorSettings"))
    original = settings.get_editor_property("bEnableTypePromotion")
    settings.set_editor_property("bEnableTypePromotion", False)
    tree = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(P["tree"].rsplit("/", 1)[1], DEST, unreal.load_asset(DEST + "/BT_PC_NPCActionGateV7"))
    bp = lib.create_blueprint_asset_with_parent(P["controller"], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCNPCActionGateV7"))
    ev = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "EventGraph")
    for name, kind, default in (("CombatEnabled", "bool", "false"), ("CombatHold", "bool", "false"),
        ("CombatPhase", "name", "Acquire"), ("CombatRequestCounter", "int", "1000"),
        ("CombatGeneration", "int", "-1"), ("CombatNextAttempt", "real", "0"),
        ("CombatDecisionCount", "int", "0"), ("CombatLastRequestAction", "name", "None")):
        assert ev.add_member_variable(name, lib.get_basic_type_by_name(kind), default)
    compile(bp)
    begin = lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint())
    use = call(ev, "/Script/AIModule.AIController.UseBlackboard", BlackboardAsset=DEST + "/BB_PC_NPCInteractionV1")
    flow = run(ev, lib.find_then_pin(begin), use)
    flow = put(ev, flow, "NPCBlackboard", pin(use, "BlackboardComponent", True))
    invoke(ev, flow, "/Script/AIModule.AIController.RunBehaviorTree", BTAsset=tree.get_path_name())
    g, flow, args = function(bp, "PC_EnableCombat", (("Enabled", "bool"),))
    flow = put(g, flow, "CombatEnabled", args[0])
    flow = put(g, flow, "PolicyEnabled", args[0])
    flow = put(g, flow, "SquadEnabled", args[0])
    flow = put(g, flow, "CombatHold", False)
    put(g, flow, "CombatPhase", "Acquire")
    compile(bp)
    base = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2")
    basepath = base.get_path_name()
    # Native inherited services still execute for death/restoration even while
    # combat holds movement. Their original reservation/lifecycle logic survives.
    for fname in ("PC_UpdateSquad", "PC_UpdatePolicy"):
        graph = lib.add_function_override(bp, unreal.Name(fname))
        assert graph
        g = unreal.BlueprintGraphEditor.get_graph_editor(graph)
        parents = [n for n in g.list_all_nodes() if "CallParentFunction" in n.get_class().get_name()]
        assert len(parents) == 1
        parent = parents[0]
        assert pins.break_pin_links(lib.find_execute_pin(parent))
        flow, wrapped_pawn = cast(g, g.find_graph_entry_pin(), own(g), base)
        hold = math(g, "BooleanAND", A=get(g, "CombatHold"), B=math(g, "BooleanAND",
            A=math(g, "Greater_DoubleDouble", A=get(g, "Health", basepath, wrapped_pawn), B=0),
            B=math(g, "EqualEqual_IntInt", A=get(g, "CombatGeneration"), B=get(g, "RestoreGeneration", basepath, wrapped_pawn))))
        _, available = branch(g, flow, hold)
        run(g, available, parent)
        compile(bp)

    g, flow, _ = function(bp, "PC_UpdateCombat")
    active, disabled = branch(g, flow, get(g, "CombatEnabled"))
    put(g, disabled, "CombatHold", False)
    active, pawn = cast(g, active, own(g), base)
    alive, dead = branch(g, active, math(g, "Greater_DoubleDouble", A=get(g, "Health", basepath, pawn), B=0))
    dead = put(g, dead, "CombatHold", False)
    dead = put(g, dead, "CombatPhase", "Acquire")
    invoke(g, dead, "PC_PolicyHold")
    changed, alive = branch(g, alive, math(g, "NotEqual_IntInt", A=get(g, "CombatGeneration"), B=get(g, "RestoreGeneration", basepath, pawn)))
    changed = put(g, changed, "CombatGeneration", get(g, "RestoreGeneration", basepath, pawn))
    changed = put(g, changed, "CombatPhase", "Acquire")
    changed = put(g, changed, "CombatNextAttempt", 0)
    put(g, changed, "CombatHold", False)
    visible, lost = branch(g, alive, bbget(g, "HasVisibleTarget", "Bool"))
    lost = put(g, lost, "CombatHold", False)
    put(g, lost, "CombatPhase", "Acquire")
    # No hidden target position/health reads. Memory is native-sensing supplied.
    visible, visible_target = cast(g, visible, bbget(g, "TargetActor", "Object"), base)
    current_los = pure(g, "/Script/Engine.Controller.LineOfSightTo", Other=visible_target, bAlternateChecks=False)
    visible, blocked = branch(g, visible, current_los)
    blocked = put(g, blocked, "CombatHold", False)
    put(g, blocked, "CombatPhase", "Acquire")
    equipped, unequipped = branch(g, visible, math(g, "BooleanAND", A=get(g, "EquipmentNumericVerified"), B=get(g, "EquipmentHumanAccepted")))
    put(g, unequipped, "CombatHold", False)
    nearby = math(g, "LessEqual_DoubleDouble", A=distance(g, local(g), bbget(g, "LastSeenPosition", "Vector")), B=1200)
    player = pure(g, "/Script/Engine.GameplayStatics.GetPlayerPawn", PlayerIndex=0)
    within_player = math(g, "BooleanAND", A=math(g, "Less_DoubleDouble", A=distance(g, local(g), pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=player)), B=900),
                        B=math(g, "Less_DoubleDouble", A=get(g, "ChaseDistance"), B=850))
    allowed = math(g, "BooleanAND", A=nearby, B=math(g, "BooleanOR", A=math(g, "EqualEqual_IntInt", A=get(g, "TeamId", basepath, pawn), B=1), B=within_player))
    combat, role = branch(g, equipped, allowed)
    role = put(g, role, "CombatHold", False)
    put(g, role, "CombatPhase", "Acquire")
    combat = put(g, combat, "CombatHold", True)
    waiting, combat = branch(g, combat, get(g, "ActionInFlight"))
    now = pure(g, "/Script/Engine.GameplayStatics.GetTimeSeconds")
    combat, _ = branch(g, combat, math(g, "GreaterEqual_DoubleDouble", A=now, B=get(g, "CombatNextAttempt")))
    # One actual admitted action per service visit. IDs are monotonic, separate
    # from original reload ActionID and from destination reservation IDs.
    def submit(path, action):
        path = put(g, path, "CombatRequestCounter", math(g, "Add_IntInt", A=get(g, "CombatRequestCounter"), B=1))
        path = put(g, path, "CombatLastRequestAction", action)
        path = put(g, path, "CombatDecisionCount", math(g, "Add_IntInt", A=get(g, "CombatDecisionCount"), B=1))
        path = invoke(g, path, "PC_RequestNPCAction", Action=action, TaskID=bbget(g, "TaskID", "Int"),
                      RequestID=get(g, "CombatRequestCounter"), Generation=get(g, "RestoreGeneration", basepath, pawn))
        path = put(g, path, "CombatPhase", action)
        put(g, path, "CombatNextAttempt", math(g, "Add_DoubleDouble", A=now, B=.4))
    acquire, progress = branch(g, combat, math(g, "EqualEqual_NameName", A=get(g, "CombatPhase"), B="Acquire"))
    submit(acquire, "Stop")
    # Stop is sampled for0.5game-seconds by the existing identity observer.
    good, failed = branch(g, progress, math(g, "EqualEqual_NameName", A=get(g, "ActionReplyResult"), B="Completed"))
    # Obstruction/cooldown rejects wait then restart the identified stop cycle.
    failed = put(g, failed, "CombatPhase", "Acquire")
    put(g, failed, "CombatNextAttempt", math(g, "Add_DoubleDouble", A=now, B=.4))
    turning, ready = branch(g, good, math(g, "EqualEqual_NameName", A=get(g, "CombatPhase"), B="Turn"))
    reload, fire = branch(g, turning, math(g, "LessEqual_IntInt", A=get(g, "LoadedAmmo", basepath, pawn), B=0))
    reload, empty = branch(g, reload, math(g, "Greater_IntInt", A=get(g, "ReserveAmmo", basepath, pawn), B=0))
    submit(reload, "Reload")
    empty = put(g, empty, "CombatHold", False)
    put(g, empty, "CombatPhase", "Acquire")
    submit(fire, "Fire")
    submit(ready, "Turn")
    save(bp, P["controller"])
    cls = unreal.EditorAssetLibrary.load_blueprint_class(P["controller"])
    service_bp = lib.create_blueprint_asset_with_parent(P["service"], unreal.BTService_BlueprintBase.static_class())
    compile(service_bp)
    sg = unreal.BlueprintGraphEditor.get_graph_editor_by_name(service_bp, "EventGraph")
    event = lib.add_event_override(service_bp, "ReceiveTickAI", unreal.IntPoint())
    flow, typed = cast(sg, lib.find_then_pin(event), pin(event, "OwnerController", True), cls)
    names = [n for n in sg.list_available_nodes([]) if n.split("|")[-1].replace(" ", "").lower() == "pcupdatecombat"]
    assert names
    node = sg.create_node_from_name(names[0], unreal.Vector2D(), [], cls)
    wire(typed, lib.find_self_pin(node))
    run(sg, flow, node)
    save(service_bp, P["service"])
    service = unreal.new_object(unreal.EditorAssetLibrary.load_blueprint_class(P["service"]), outer=tree)
    service.set_editor_property("interval", .1)
    service.set_editor_property("random_deviation", 0)
    root = tree.get_editor_property("root_node")
    root.set_editor_property("services", list(root.get_editor_property("services")) + [service])
    save(tree, P["tree"])
    for key, name in (("allied", "BP_PCAlliedActionGateV7"), ("german", "BP_PCGermanActionGateV7")):
        child = lib.create_blueprint_asset_with_parent(P[key], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + name))
        compile(child)
        unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(P[key])).set_editor_property("ai_controller_class", cls)
        save(child, P[key])
    report["status"] = "pass_native_autonomous_combat_authored_runtime_unpassed"
except Exception:
    report["status"] = "failed_autonomous_combat_author_preserve"
    report["errors"].append(traceback.format_exc())
finally:
    if settings is not None:
        settings.set_editor_property("bEnableTypePromotion", original)
    for p in report["packages"]:
        f = package_file(p)
        report["files"].append({"package": p, "path": f.relative_to(ROOT).as_posix(), "size_bytes": f.stat().st_size, "sha256": digest(f)})
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
