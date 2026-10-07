"""Native two-slot reservation actor and allied follow/chase BT service."""
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
SEARCH_VERSION = "V9"
OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "squad_author.json"
P = {k: DEST + "/" + n + VERSION for k, n in (
    ("coordinator", "BP_PCSquadReservation"), ("controller", "BP_PCNPCSquad"),
    ("tree", "BT_PC_NPCSquad"), ("service", "BTS_PC_NPCSquad"),
    ("allied", "BP_PCAlliedSquad"), ("german", "BP_PCGermanSquad"))}
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "packages": [], "errors": [],
          "scope": "new native allied reservation/follow/regroup/conservative short chase; no armed combat acceptance"}
settings = None
original_promotion = None


def checkpoint(stage):
    report["stage"] = stage
    RESULT.write_text(json.dumps(report, indent=2) + "\n")


def compile(bp):
    assert lib.compile_blueprint(bp)
    assert all(not unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors() for g in lib.list_graphs(bp))


def save(bp, package):
    if isinstance(bp, unreal.Blueprint):
        compile(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report["packages"].append(package)
    checkpoint("saved " + package)


def obj_fn(bp, name, extra=()):
    g = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, name)
    g.set_function_is_public()
    ctrl = g.add_graph_input_parameter("Requester", lib.get_object_reference_type(unreal.AIController.static_class()))
    extra_pins = []
    for parameter, kind in extra:
        typ = lib.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector")) if kind == "Vector" else lib.get_basic_type_by_name(kind)
        extra_pins.append(g.add_graph_input_parameter(parameter, typ))
    return g, g.find_graph_entry_pin(), ctrl, extra_pins


def external(g, flow, cls, target, name, **kw):
    token = name.replace("_", "").lower()
    candidates = [n for n in g.list_available_nodes([]) if n.split("|")[-1].replace(" ", "").replace("_", "").lower() == token]
    assert candidates, "Missing public external function " + name
    node = g.create_node_from_name(candidates[0], unreal.Vector2D(), [], cls)
    assert node
    wire(target, lib.find_self_pin(node))
    for parameter, datum in kw.items():
        value(pin(node, parameter), datum)
    return run(g, flow, node)


def own_pawn(g):
    return pure(g, "/Script/Engine.Controller.K2_GetPawn")


def own_controller(g):
    return pure(g, "/Script/AIModule.AIBlueprintHelperLibrary.GetAIController", ControlledActor=own_pawn(g))


def local(g):
    return pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=own_pawn(g))


try:
    assert guards_match(rows) and all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in P.values())
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/BlueprintGraph.BlueprintEditorSettings"))
    original_promotion = settings.get_editor_property("bEnableTypePromotion")
    settings.set_editor_property("bEnableTypePromotion", False)
    assert settings.get_editor_property("bEnableTypePromotion") is False
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tree = tools.duplicate_asset(P["tree"].rsplit("/", 1)[1], DEST, unreal.load_asset(DEST + "/BT_PC_NPCSearch" + SEARCH_VERSION))
    coord = lib.create_blueprint_asset_with_parent(P["coordinator"], unreal.Actor.static_class())
    ce = unreal.BlueprintGraphEditor.get_graph_editor_by_name(coord, "EventGraph")
    for i in range(2):
        assert ce.add_member_variable("Owner" + str(i), lib.get_object_reference_type(unreal.AIController.static_class()))
        assert ce.add_member_variable("Point" + str(i), lib.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector")))
        assert ce.add_member_variable("RID" + str(i), lib.get_basic_type_by_name("int"), "0")
    assert ce.add_member_variable("NextRID", lib.get_basic_type_by_name("int"), "1")
    compile(coord)
    coord_cls = unreal.EditorAssetLibrary.load_blueprint_class(P["coordinator"])
    bp = lib.create_blueprint_asset_with_parent(P["controller"], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCNPCSearch" + SEARCH_VERSION))
    ev = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "EventGraph")
    for name, kind, default in (("SquadEnabled", "bool", "false"), ("FormationSlot", "int", "-1"),
        ("SquadReservationID", "int", "0"), ("SquadGeneration", "int", "0"), ("ChaseActive", "bool", "false"),
        ("ChaseDistance", "real", "0"), ("ChaseEpisode", "int", "0"), ("SquadMode", "name", "Follow"),
        ("SquadPositionInitialized", "bool", "false"), ("SquadFailed", "bool", "false")):
        assert ev.add_member_variable(name, lib.get_basic_type_by_name(kind), default)
    for name in ("HeldGoal", "SquadPreviousPosition", "SquadDesiredGoal"):
        assert ev.add_member_variable(name, lib.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector")))
    compile(bp)
    begin = lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint())
    use = ev.add_call_function_node("UseBlackboard")
    value(pin(use, "BlackboardAsset"), DEST + "/BB_PC_NPCInteractionV1")
    flow = run(ev, lib.find_then_pin(begin), use)
    flow = put(ev, flow, "NPCBlackboard", pin(use, "BlackboardComponent", True))
    invoke(ev, flow, "/Script/AIModule.AIController.RunBehaviorTree", BTAsset=tree.get_path_name())
    g, flow, args = function(bp, "PC_EnableSquad", (("Enabled", "bool"),))
    put(g, flow, "SquadEnabled", args[0])
    compile(bp)
    ctrl_cls = unreal.EditorAssetLibrary.load_blueprint_class(P["controller"])
    cpath = ctrl_cls.get_path_name()

    g, flow, requester, _ = obj_fn(coord, "PC_Register")
    flow, typed = cast(g, flow, requester, ctrl_cls)
    # An existing slot-1 owner must not migrate to slot 0 when its teammate dies.
    existing1, flow = branch(g, flow, math(g, "EqualEqual_ObjectObject", A=get(g, "Owner1"), B=requester))
    put(g, existing1, "FormationSlot", 1, typed, cpath)
    own0 = get(g, "Owner0")
    use0, use1 = branch(g, flow, math(g, "BooleanOR", A=math(g, "EqualEqual_ObjectObject", A=own0, B=requester),
        B=math(g, "Not_PreBool", A=pure(g, "/Script/Engine.KismetSystemLibrary.IsValid", Object=own0))))
    use0 = put(g, use0, "Owner0", requester)
    put(g, use0, "FormationSlot", 0, typed, cpath)
    own1 = get(g, "Owner1")
    yes, no = branch(g, use1, math(g, "BooleanOR", A=math(g, "EqualEqual_ObjectObject", A=own1, B=requester),
        B=math(g, "Not_PreBool", A=pure(g, "/Script/Engine.KismetSystemLibrary.IsValid", Object=own1))))
    yes = put(g, yes, "Owner1", requester)
    put(g, yes, "FormationSlot", 1, typed, cpath)
    put(g, no, "FormationSlot", -1, typed, cpath)
    compile(coord)

    g, flow, requester, args = obj_fn(coord, "PC_Reserve", (("Destination", "Vector"),))
    flow, typed = cast(g, flow, requester, ctrl_cls)
    dest = args[0]
    slot0, slot1 = branch(g, flow, math(g, "EqualEqual_IntInt", A=get(g, "FormationSlot", cpath, typed), B=0))
    for i, path in ((0, slot0), (1, slot1)):
        path, _ = branch(g, path, math(g, "EqualEqual_ObjectObject", A=get(g, "Owner" + str(i)), B=requester))
        retained, new = branch(g, path, math(g, "Greater_IntInt", A=get(g, "RID" + str(i)), B=0))
        retained = put(g, retained, "SquadReservationID", get(g, "RID" + str(i)), typed, cpath)
        put(g, retained, "HeldGoal", get(g, "Point" + str(i)), typed, cpath)
        other = 1 - i
        separated = math(g, "BooleanOR", A=math(g, "LessEqual_IntInt", A=get(g, "RID" + str(other)), B=0),
                         B=math(g, "GreaterEqual_DoubleDouble", A=distance(g, dest, get(g, "Point" + str(other))), B=150))
        accept, reject = branch(g, new, separated)
        accept = put(g, accept, "RID" + str(i), get(g, "NextRID"))
        accept = put(g, accept, "Point" + str(i), dest)
        accept = put(g, accept, "NextRID", math(g, "Add_IntInt", A=get(g, "NextRID"), B=1))
        accept = put(g, accept, "SquadReservationID", get(g, "RID" + str(i)), typed, cpath)
        put(g, accept, "HeldGoal", dest, typed, cpath)
        put(g, reject, "SquadReservationID", 0, typed, cpath)
    compile(coord)

    g, flow, requester, args = obj_fn(coord, "PC_Release", (("Reason", "name"),))
    flow, typed = cast(g, flow, requester, ctrl_cls)
    allowed = math(g, "EqualEqual_NameName", A=args[0], B="reassigned")
    for reason in ("failed", "dead", "restored"):
        allowed = math(g, "BooleanOR", A=allowed, B=math(g, "EqualEqual_NameName", A=args[0], B=reason))
    flow, _ = branch(g, flow, allowed)
    free_owner = math(g, "BooleanOR", A=math(g, "EqualEqual_NameName", A=args[0], B="dead"),
                      B=math(g, "EqualEqual_NameName", A=args[0], B="restored"))
    for i in range(2):
        owned, flow = branch(g, flow, math(g, "EqualEqual_ObjectObject", A=get(g, "Owner" + str(i)), B=requester))
        owned = put(g, owned, "RID" + str(i), 0)
        owned = put(g, owned, "SquadReservationID", 0, typed, cpath)
        release, _ = branch(g, owned, free_owner)
        node = g.add_set_member_variable_node("Owner" + str(i))
        release = run(g, release, node)  # unconnected object default is None
        put(g, release, "FormationSlot", -1, typed, cpath)
    save(coord, P["coordinator"])
    coord_cls = unreal.EditorAssetLibrary.load_blueprint_class(P["coordinator"])
    checkpoint("coordinator complete")

    def coordinator(g, flow):
        query = call(g, "/Script/Engine.GameplayStatics.GetActorOfClass", ActorClass=coord_cls.get_path_name())
        flow = run(g, flow, query)  # BlueprintCallable has an exec pin; not pure.
        return cast(g, flow, pin(query, "ReturnValue", True), coord_cls)

    def release(g, flow, reason):
        flow, actor = coordinator(g, flow)
        return external(g, flow, coord_cls, actor, "PC_Release", Requester=own_controller(g), Reason=reason)

    g, flow, args = function(bp, "PC_SquadRequestGoal", (("Goal", "Vector"), ("Mode", "name")))
    raw_desired, mode = args
    # Reserve the actual navigable endpoint, not an off-mesh formation point.
    # MoveTo can otherwise report arrival at a projected path end while the
    # body is still >1m from the arbitrarily reserved world coordinate.
    projection = call(g, "/Script/NavigationSystem.NavigationSystemV1.K2_ProjectPointToNavigation",
                      Point=raw_desired, QueryExtent="(X=200,Y=200,Z=200)")
    flow, invalid_point = branch(g, flow, pin(projection, "ReturnValue", True))
    invalid_point = release(g, invalid_point, "failed")
    invalid_point = bbput(g, invalid_point, "ReservationID", "Int", 0)
    invalid_point = bbput(g, invalid_point, "WaitingReason", "Name", "SquadProjectionRejected")
    invoke(g, invalid_point, "PC_PolicyHold")
    flow, nav_pawn = cast(g, flow, own_pawn(g), unreal.Character.static_class())
    capsule = get(g, "CapsuleComponent", "/Script/Engine.Character", nav_pawn)
    height = pure(g, "/Script/Engine.CapsuleComponent.GetScaledCapsuleHalfHeight", self=capsule)
    desired = math(g, "TransformLocation", T=math(g, "MakeTransform", Location=pin(projection, "ProjectedLocation", True)),
                   Location=math(g, "MakeVector", X=0, Y=0, Z=height))
    flow, actor = coordinator(g, flow)
    flow = external(g, flow, coord_cls, actor, "PC_Register", Requester=own_controller(g))
    flow, invalid = branch(g, flow, math(g, "GreaterEqual_IntInt", A=get(g, "FormationSlot"), B=0))
    invoke(g, invalid, "PC_PolicyHold")
    changed = math(g, "BooleanOR", A=math(g, "NotEqual_NameName", A=get(g, "SquadMode"), B=mode),
                   B=math(g, "Greater_DoubleDouble", A=distance(g, get(g, "SquadDesiredGoal"), desired), B=150))
    # Cache before mutating mode/goal: later exec consumers must not re-evaluate
    # an expression whose inputs have already been overwritten.
    changed_path, same_path = branch(g, flow, changed)
    changed_path = external(g, changed_path, coord_cls, actor, "PC_Release", Requester=own_controller(g), Reason="reassigned")
    changed_path = put(g, changed_path, "SquadFailed", False)
    changed_path = put(g, changed_path, "SquadMode", mode)
    changed_path = put(g, changed_path, "SquadDesiredGoal", desired)
    changed_path = external(g, changed_path, coord_cls, actor, "PC_Reserve", Requester=own_controller(g), Destination=desired)
    valid, reject = branch(g, changed_path, math(g, "Greater_IntInt", A=get(g, "SquadReservationID"), B=0))
    valid = bbput(g, valid, "ReservationID", "Int", get(g, "SquadReservationID"))
    invoke(g, valid, "PC_GotoPolicyGoal", Goal=get(g, "HeldGoal"), State=mode)
    invoke(g, reject, "PC_PolicyHold")
    failed = math(g, "BooleanOR", A=get(g, "SquadFailed"),
                  B=math(g, "EqualEqual_NameName", A=bbget(g, "WaitingReason", "Name"), B="PathExhausted"))
    fail, retry = branch(g, same_path, failed)
    fail = external(g, fail, coord_cls, actor, "PC_Release", Requester=own_controller(g), Reason="failed")
    fail = bbput(g, fail, "ReservationID", "Int", 0)
    fail = put(g, fail, "SquadFailed", True)
    invoke(g, fail, "PC_PolicyHold")
    retry = external(g, retry, coord_cls, actor, "PC_Reserve", Requester=own_controller(g), Destination=desired)
    valid, reject = branch(g, retry, math(g, "Greater_IntInt", A=get(g, "SquadReservationID"), B=0))
    valid = bbput(g, valid, "ReservationID", "Int", get(g, "SquadReservationID"))
    invoke(g, valid, "PC_GotoPolicyGoal", Goal=get(g, "HeldGoal"), State=mode)
    invoke(g, reject, "PC_PolicyHold")
    compile(bp)
    checkpoint("squad request goal compiled")

    g, flow, _ = function(bp, "PC_ClearObservedTarget")
    flow = invoke(g, flow, "/Script/AIModule.BlackboardComponent.ClearValue", self=get(g, "NPCBlackboard"),
                  KeyName=pure(g, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value="TargetActor"))
    flow = bbput(g, flow, "HasVisibleTarget", "Bool", False)
    flow = bbput(g, flow, "LastSeenTime", "Float", 0)
    flow = bbput(g, flow, "LastSeenPosition", "Vector", "(X=0,Y=0,Z=0)")
    flow = put(g, flow, "SearchActive", False)
    flow = put(g, flow, "SearchConsumedSightTime", 0)
    invoke(g, flow, "PC_PolicyHold")
    compile(bp)
    # Override the native function called by inherited PawnSensing delegates.
    # Reject observed corpses/own death at the actual observation boundary; never
    # inspect a hidden target's current position or invent omniscient death.
    overridden = lib.add_function_override(bp, unreal.Name("PC_RecordSight"))
    assert overridden
    g = unreal.BlueprintGraphEditor.get_graph_editor(overridden)
    g.set_function_is_public()
    g.remove_nodes([n for n in g.list_all_nodes() if "CallParentFunction" in n.get_class().get_name()])
    entry = g.find_graph_entry_pin()
    seen = pin(entry.get_owning_node(), "SeenPawn", True)
    base = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2")
    flow, target = cast(g, entry, seen, base)
    flow, self_pawn = cast(g, flow, own_pawn(g), base)
    flow, _ = branch(g, flow, math(g, "Greater_DoubleDouble", A=get(g, "Health", base.get_path_name(), self_pawn), B=0))
    alive, dead = branch(g, flow, math(g, "Greater_DoubleDouble", A=get(g, "Health", base.get_path_name(), target), B=0))
    dead, _ = branch(g, dead, math(g, "EqualEqual_ObjectObject", A=bbget(g, "TargetActor", "Object"), B=target))
    invoke(g, dead, "PC_ClearObservedTarget")
    alive, _ = branch(g, alive, math(g, "NotEqual_IntInt", A=get(g, "TeamId", base.get_path_name(), self_pawn), B=get(g, "TeamId", base.get_path_name(), target)))
    set_target = call(g, "/Script/AIModule.BlackboardComponent.SetValueAsObject", self=get(g, "NPCBlackboard"),
                      KeyName=pure(g, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value="TargetActor"), ObjectValue=target)
    alive = run(g, alive, set_target)
    alive = bbput(g, alive, "LastSeenPosition", "Vector", pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=target))
    alive = bbput(g, alive, "LastSeenTime", "Float", pure(g, "/Script/Engine.GameplayStatics.GetTimeSeconds"))
    bbput(g, alive, "HasVisibleTarget", "Bool", True)
    compile(bp)
    checkpoint("native sight corpse rejection override compiled")

    g, flow, args = function(bp, "PC_SquadReturn", (("Goal", "Vector"), ("Mode", "name")))
    flow = invoke(g, flow, "PC_SquadRequestGoal", Goal=args[0], Mode=args[1])
    arrived, _ = branch(g, flow, math(g, "LessEqual_DoubleDouble", A=distance(g, local(g), get(g, "HeldGoal")), B=50))
    arrived = put(g, arrived, "ChaseActive", False)
    arrived = put(g, arrived, "ChaseDistance", 0)
    bbput(g, arrived, "ChaseTravelDistance", "Float", 0)
    compile(bp)

    g, flow, _ = function(bp, "PC_UpdateSquad")
    flow, _ = branch(g, flow, get(g, "SquadEnabled"))
    base = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2")
    basepath = base.get_path_name()
    flow, pawn = cast(g, flow, own_pawn(g), base)
    flow, _ = branch(g, flow, math(g, "EqualEqual_IntInt", A=get(g, "TeamId", basepath, pawn), B=0))
    restored, current = branch(g, flow, math(g, "NotEqual_IntInt", A=get(g, "SquadGeneration"), B=get(g, "RestoreGeneration", basepath, pawn)))
    restored = release(g, restored, "restored")
    restored = bbput(g, restored, "ReservationID", "Int", 0)
    restored = put(g, restored, "ChaseActive", False)
    restored = put(g, restored, "ChaseDistance", 0)
    restored = put(g, restored, "SquadPositionInitialized", False)
    restored = put(g, restored, "SquadGeneration", get(g, "RestoreGeneration", basepath, pawn))
    restored = put(g, restored, "SquadFailed", False)
    invoke(g, restored, "PC_PolicyHold")
    alive, dead = branch(g, current, math(g, "Greater_DoubleDouble", A=get(g, "Health", basepath, pawn), B=0))
    dead = release(g, dead, "dead")
    dead = bbput(g, dead, "ReservationID", "Int", 0)
    dead = put(g, dead, "ChaseActive", False)
    dead = put(g, dead, "ChaseDistance", 0)
    invoke(g, dead, "PC_PolicyHold")
    chasing = math(g, "BooleanAND", A=get(g, "ChaseActive"),
                   B=math(g, "EqualEqual_NameName", A=get(g, "SquadMode"), B="Chase"))
    step = math(g, "SelectFloat", A=distance(g, local(g), get(g, "SquadPreviousPosition")), B=0,
                bPickA=math(g, "BooleanAND", A=chasing, B=get(g, "SquadPositionInitialized")))
    alive = put(g, alive, "ChaseDistance", math(g, "Add_DoubleDouble", A=get(g, "ChaseDistance"), B=step))
    alive = bbput(g, alive, "ChaseTravelDistance", "Float", get(g, "ChaseDistance"))
    alive = put(g, alive, "SquadPreviousPosition", local(g))
    alive = put(g, alive, "SquadPositionInitialized", True)
    ready, busy = branch(g, alive, math(g, "EqualEqual_NameName", A=get(g, "ActionState", basepath, pawn), B="Ready"))
    # Busy holds its existing reservation; no release at reload/fire/idle.
    invoke(g, busy, "PC_PolicyHold")
    ready, actor = coordinator(g, ready)
    ready = external(g, ready, coord_cls, actor, "PC_Register", Requester=own_controller(g))
    ready, _ = branch(g, ready, math(g, "GreaterEqual_IntInt", A=get(g, "FormationSlot"), B=0))
    player = pure(g, "/Script/Engine.GameplayStatics.GetPlayerPawn", PlayerIndex=0)
    ready, _ = branch(g, ready, pure(g, "/Script/Engine.KismetSystemLibrary.IsValid", Object=player))
    player_pos = pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=player)
    player_rot = pure(g, "/Script/Engine.Actor.K2_GetActorRotation", self=player)
    side = math(g, "SelectFloat", A=-200, B=200, bPickA=math(g, "EqualEqual_IntInt", A=get(g, "FormationSlot"), B=0))
    formation_transform = math(g, "MakeTransform", Location=player_pos, Rotation=player_rot)
    offset = math(g, "MakeVector", X=-400, Y=side, Z=0)
    follow_goal = math(g, "TransformLocation", T=formation_transform, Location=offset)
    player_distance = distance(g, local(g), player_pos)
    # Conservative operational cutoffs leave room for a service interval; the
    # acceptance limit remains 1000cm, not 850/900cm. Long-frame proof is separate.
    allowed = math(g, "BooleanAND", A=bbget(g, "HasVisibleTarget", "Bool"),
        B=math(g, "BooleanAND", A=math(g, "Less_DoubleDouble", A=player_distance, B=900),
               B=math(g, "Less_DoubleDouble", A=get(g, "ChaseDistance"), B=850)))
    chase, follow = branch(g, ready, allowed)
    continuing, new = branch(g, chase, get(g, "ChaseActive"))
    new = put(g, new, "ChaseActive", True)
    new = put(g, new, "ChaseEpisode", math(g, "Add_IntInt", A=get(g, "ChaseEpisode"), B=1))
    target_transform = math(g, "MakeTransform", Location=bbget(g, "LastSeenPosition", "Vector"), Rotation=player_rot)
    support_goal = math(g, "TransformLocation", T=target_transform, Location=math(g, "MakeVector", X=-350, Y=side, Z=0))
    invoke(g, new, "PC_SquadRequestGoal", Goal=support_goal, Mode="Chase")
    invoke(g, continuing, "PC_SquadRequestGoal", Goal=support_goal, Mode="Chase")
    mode = math(g, "SelectName", A=pure(g, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value="Regroup"), B=pure(g, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value="Follow"),
                bPickA=math(g, "BooleanOR", A=get(g, "ChaseActive"), B=math(g, "Greater_DoubleDouble", A=player_distance, B=1000)))
    invoke(g, follow, "PC_SquadReturn", Goal=follow_goal, Mode=mode)
    save(bp, P["controller"])
    checkpoint("squad controller saved")
    ctrl_cls = unreal.EditorAssetLibrary.load_blueprint_class(P["controller"])

    service_bp = lib.create_blueprint_asset_with_parent(P["service"], unreal.BTService_BlueprintBase.static_class())
    compile(service_bp)
    sg = unreal.BlueprintGraphEditor.get_graph_editor_by_name(service_bp, "EventGraph")
    event = lib.add_event_override(service_bp, "ReceiveTickAI", unreal.IntPoint())
    flow, typed = cast(sg, lib.find_then_pin(event), pin(event, "OwnerController", True), ctrl_cls)
    external(sg, flow, ctrl_cls, typed, "PC_UpdateSquad")
    save(service_bp, P["service"])
    service = unreal.new_object(unreal.EditorAssetLibrary.load_blueprint_class(P["service"]), outer=tree)
    service.set_editor_property("interval", .1)
    service.set_editor_property("random_deviation", 0.0)
    root = tree.get_editor_property("root_node")
    root.set_editor_property("services", list(root.get_editor_property("services")) + [service])
    save(tree, P["tree"])
    for label, prefix in (("allied", "BP_PCAlliedSearch"), ("german", "BP_PCGermanSearch")):
        child = lib.create_blueprint_asset_with_parent(P[label], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + prefix + SEARCH_VERSION))
        compile(child)
        cdo = unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(P[label]))
        cdo.set_editor_property("ai_controller_class", ctrl_cls)
        movement = cdo.get_component_by_class(unreal.CharacterMovementComponent)
        assert movement and movement.get_outer() == cdo, "Do not edit an inherited source component template"
        movement.set_editor_property("use_rvo_avoidance", True)
        save(child, P[label])
    report["operational_cutoffs_cm"] = {"chase_travel": 850, "player_distance": 900, "acceptance_limit": 1000}
    report["avoidance"] = "CharacterMovement RVO only; no Crowd"
    report["status"] = "pass_native_squad_authored_requires_city"
except Exception:
    report["status"] = "failed_squad_author_preserve"
    report["errors"].append(traceback.format_exc())
finally:
    if settings is not None and original_promotion is not None:
        settings.set_editor_property("bEnableTypePromotion", original_promotion)
    report["files"] = []
    for package in report["packages"]:
        file = package_file(package)
        report["files"].append({"package": package, "path": file.relative_to(ROOT).as_posix(), "size_bytes": file.stat().st_size, "sha256": digest(file)})
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
