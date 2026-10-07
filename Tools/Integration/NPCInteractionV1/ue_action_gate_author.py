"""Native action identity/feedback wrapper; unreviewed NPC equipment stays gated."""
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
P = {k: DEST + "/" + n + VERSION for k, n in (("controller", "BP_PCNPCActionGate"), ("tree", "BT_PC_NPCActionGate"),
    ("service", "BTS_PC_NPCActionGate"), ("allied", "BP_PCAlliedActionGate"), ("german", "BP_PCGermanActionGate"))}
OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "action_gate_author.json"
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "packages": [], "files": [], "errors": [],
          "scope": "native action identity/actual feedback; default equipment human gate false, no formal combat acceptance"}
settings = None
original_promotion = None


def compile(bp):
    assert lib.compile_blueprint(bp)
    assert all(not unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors() for g in lib.list_graphs(bp))


def save(bp, package):
    if isinstance(bp, unreal.Blueprint):
        compile(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report["packages"].append(package)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")


def own(g):
    return pure(g, "/Script/Engine.Controller.K2_GetPawn")


def local(g):
    return pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=own(g))


def reply(g, flow, result, reason):
    return put(g, put(g, flow, "ActionReplyResult", result), "ActionReplyReason", reason)


def terminal(g, flow, result, reason):
    flow = put(g, flow, "ActionInFlight", False)
    flow = put(g, flow, "ActiveTerminalResult", result)
    # An intervening rejected request may have overwritten reply IDs. Native
    # completion/cancellation must identify the admitted request, never that one.
    for target, source in (("ReplyTaskID", "ActiveTaskID"), ("ReplyRequestID", "ActiveRequestID"), ("ReplyGeneration", "ActiveGeneration")):
        flow = put(g, flow, target, get(g, source))
    return reply(g, flow, result, reason)


def external(g, flow, cls, target, name, **kw):
    """Resolve public Blueprint calls in the pawn class, not controller self."""
    token = name.replace("_", "").lower()
    names = [n for n in g.list_available_nodes([])
             if n.split("|")[-1].replace(" ", "").replace("_", "").lower() == token]
    assert names, "Missing public pawn function " + name
    report.setdefault("external_call_routing", []).append({"function": name, "declaring_class": cls.get_path_name(), "type_ids": names})
    node = g.create_node_from_name(names[0], unreal.Vector2D(), [], cls)
    assert node
    wire(target, lib.find_self_pin(node))
    for parameter, datum in kw.items():
        value(pin(node, parameter), datum)
    return run(g, flow, node)


try:
    assert guards_match(rows) and all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in P.values())
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/BlueprintGraph.BlueprintEditorSettings"))
    original_promotion = settings.get_editor_property("bEnableTypePromotion")
    settings.set_editor_property("bEnableTypePromotion", False)
    assert settings.get_editor_property("bEnableTypePromotion") is False
    tree = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(P["tree"].rsplit("/", 1)[1], DEST, unreal.load_asset(DEST + "/BT_PC_NPCSquadV4"))
    bp = lib.create_blueprint_asset_with_parent(P["controller"], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCNPCSquadV4"))
    ev = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "EventGraph")
    for name, kind, default in (("EquipmentNumericVerified", "bool", "false"), ("EquipmentHumanAccepted", "bool", "false"),
        ("ActionInFlight", "bool", "false"), ("ActionReplyResult", "name", "None"), ("ActionReplyReason", "name", "None"),
        ("PendingNPCAction", "name", "None"), ("ReplyTaskID", "int", "-1"), ("ReplyRequestID", "int", "-1"),
        ("ReplyGeneration", "int", "-1"), ("ActiveTaskID", "int", "-1"), ("ActiveRequestID", "int", "-1"),
        ("ActiveGeneration", "int", "-1"), ("PendingOriginalActionID", "int", "-1"), ("ActionInitialShotSequence", "int", "0"),
        ("ActionAmmoTotal", "int", "0"), ("StopAcceptedGameTime", "real", "0"),
        ("ActionInitialReloadCommit", "int", "0"), ("ActiveTerminalResult", "name", "None")):
        assert ev.add_member_variable(name, lib.get_basic_type_by_name(kind), default)
    assert ev.add_member_variable("StopOrigin", lib.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector")))
    compile(bp)
    begin = lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint())
    use = call(ev, "/Script/AIModule.AIController.UseBlackboard", BlackboardAsset=DEST + "/BB_PC_NPCInteractionV1")
    flow = run(ev, lib.find_then_pin(begin), use)
    flow = put(ev, flow, "NPCBlackboard", pin(use, "BlackboardComponent", True))
    invoke(ev, flow, "/Script/AIModule.AIController.RunBehaviorTree", BTAsset=tree.get_path_name())
    g, flow, args = function(bp, "PC_ConfigureNPCEquipment", (("NumericVerified", "bool"), ("HumanAccepted", "bool")))
    flow = put(g, flow, "EquipmentNumericVerified", args[0])
    put(g, flow, "EquipmentHumanAccepted", args[1])
    compile(bp)
    base = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2")
    basepath = base.get_path_name()
    # Local UE source requires the exact defining class, not an inheriting class:
    # PC_RequestReload belongs to this retained transaction parent.
    reload_parent_path = "/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/BP_PCCombatantReloadV1"
    reload_parent_bp = unreal.load_asset(reload_parent_path)
    assert unreal.BlueprintGraphEditor.get_graph_editor_by_name(reload_parent_bp, "PC_RequestReload")
    reload_parent_cls = unreal.EditorAssetLibrary.load_blueprint_class(reload_parent_path)

    g, flow, args = function(bp, "PC_RequestNPCAction", (("Action", "name"), ("TaskID", "int"), ("RequestID", "int"), ("Generation", "int")))
    action, task, request, generation = args
    for n, datum in (("ReplyTaskID", task), ("ReplyRequestID", request), ("ReplyGeneration", generation)):
        flow = put(g, flow, n, datum)
    flow = reply(g, flow, "Rejected", "InvalidPawn")
    flow, pawn = cast(g, flow, own(g), base)
    current, stale = branch(g, flow, math(g, "EqualEqual_IntInt", A=generation, B=get(g, "RestoreGeneration", basepath, pawn)))
    reply(g, stale, "Rejected", "StaleGeneration")
    current, stale = branch(g, current, math(g, "EqualEqual_IntInt", A=task, B=bbget(g, "TaskID", "Int")))
    reply(g, stale, "Rejected", "StaleTask")
    current, invalid = branch(g, current, math(g, "Greater_IntInt", A=request, B=0))
    reply(g, invalid, "Rejected", "InvalidRequest")
    current, dead = branch(g, current, math(g, "Greater_DoubleDouble", A=get(g, "Health", basepath, pawn), B=0))
    reply(g, dead, "Rejected", "Dead")
    older = math(g, "BooleanAND", A=math(g, "Less_IntInt", A=request, B=get(g, "ActiveRequestID")),
        B=math(g, "BooleanAND", A=math(g, "EqualEqual_IntInt", A=task, B=get(g, "ActiveTaskID")),
               B=math(g, "EqualEqual_IntInt", A=generation, B=get(g, "ActiveGeneration"))))
    old_request, current = branch(g, current, older)
    reply(g, old_request, "Rejected", "StaleRequest")
    same = math(g, "BooleanAND", A=math(g, "EqualEqual_IntInt", A=get(g, "ActiveRequestID"), B=request),
        B=math(g, "BooleanAND", A=math(g, "EqualEqual_IntInt", A=get(g, "ActiveTaskID"), B=task),
               B=math(g, "EqualEqual_IntInt", A=get(g, "ActiveGeneration"), B=generation)))
    duplicate, fresh = branch(g, current, same)
    duplicate, changed_action = branch(g, duplicate, math(g, "EqualEqual_NameName", A=action, B=get(g, "PendingNPCAction")))
    reply(g, changed_action, "Rejected", "RequestActionMismatch")
    running, done = branch(g, duplicate, get(g, "ActionInFlight"))
    reply(g, running, "Running", "SameRequest")
    reply(g, done, get(g, "ActiveTerminalResult"), "AlreadyObserved")
    busy, fresh = branch(g, fresh, get(g, "ActionInFlight"))
    reply(g, busy, "Rejected", "ActionBusy")
    stop, other = branch(g, fresh, math(g, "EqualEqual_NameName", A=action, B="Stop"))

    def admitted(g, flow, name):
        for n, datum in (("ActiveTaskID", task), ("ActiveRequestID", request), ("ActiveGeneration", generation),
                         ("PendingNPCAction", name), ("ActionInFlight", True)):
            flow = put(g, flow, n, datum)
        flow = put(g, flow, "ActiveTerminalResult", "Running")
        return reply(g, flow, "Started", "NativeRequestAdmitted")

    stop = put(g, stop, "SquadEnabled", False)
    stop = put(g, stop, "PolicyEnabled", False)
    stop = invoke(g, stop, "PC_PolicyHold")
    stop = bbput(g, stop, "RequestID", "Int", 0)
    stop = put(g, stop, "StopOrigin", local(g))
    stop = put(g, stop, "StopAcceptedGameTime", pure(g, "/Script/Engine.GameplayStatics.GetTimeSeconds"))
    admitted(g, stop, "Stop")
    valid, no_gun = branch(g, other, pure(g, "/Script/Engine.KismetSystemLibrary.IsValid", Object=get(g, "WeaponAppearance", basepath, pawn)))
    reply(g, no_gun, "Rejected", "Unarmed")
    valid, unverified = branch(g, valid, get(g, "EquipmentNumericVerified"))
    reply(g, unverified, "Rejected", "EquipmentUnverified")
    valid, human = branch(g, valid, get(g, "EquipmentHumanAccepted"))
    reply(g, human, "Rejected", "EquipmentNeedsHumanReview")
    valid, busy = branch(g, valid, math(g, "EqualEqual_NameName", A=get(g, "ActionState", basepath, pawn), B="Ready"))
    reply(g, busy, "Rejected", "OriginalActionBusy")
    reload, fire = branch(g, valid, math(g, "EqualEqual_NameName", A=action, B="Reload"))
    reload = put(g, reload, "ActionInitialReloadCommit", get(g, "ReloadCommitCount", basepath, pawn))
    reload = external(g, reload, reload_parent_cls, pawn, "PC_RequestReload")
    reload, rejected = branch(g, reload, math(g, "EqualEqual_NameName", A=get(g, "ActionState", basepath, pawn), B="Reloading"))
    reply(g, rejected, "Rejected", "OriginalReloadRejected")
    reload = put(g, reload, "PendingOriginalActionID", get(g, "ActionID", basepath, pawn))
    reload = put(g, reload, "ActionAmmoTotal", math(g, "Add_IntInt", A=get(g, "LoadedAmmo", basepath, pawn), B=get(g, "ReserveAmmo", basepath, pawn)))
    admitted(g, reload, "Reload")
    fire, unsupported = branch(g, fire, math(g, "EqualEqual_NameName", A=action, B="Fire"))
    reply(g, unsupported, "Rejected", "UnsupportedAction")
    fire, invisible = branch(g, fire, bbget(g, "HasVisibleTarget", "Bool"))
    reply(g, invisible, "Rejected", "TargetNotVisible")
    velocity = pure(g, "/Script/Engine.Actor.GetVelocity", self=pawn)
    fire, moving = branch(g, fire, math(g, "LessEqual_DoubleDouble", A=math(g, "VSizeSquared", A=velocity), B=1))
    reply(g, moving, "Rejected", "BodyNotStopped")
    weapon = get(g, "WeaponAppearance", basepath, pawn)
    muzzle = math(g, "TransformLocation", T=pure(g, "/Script/Engine.Actor.GetTransform", self=weapon), Location="(X=0,Y=83.23,Z=0)")
    point = bbget(g, "LastSeenPosition", "Vector")
    forward = pure(g, "/Script/Engine.Actor.GetActorForwardVector", self=pawn)
    target_direction = math(g, "Normal", A=math(g, "Subtract_VectorVector", A=point, B=local(g)))
    fire, unturned = branch(g, fire, math(g, "GreaterEqual_DoubleDouble", A=math(g, "Dot_VectorVector", A=forward, B=target_direction), B=.966))
    reply(g, unturned, "Rejected", "BodyNotFacingTarget")
    trace = call(g, "/Script/Engine.KismetSystemLibrary.LineTraceSingle", Start=muzzle, End=point,
                 TraceChannel="TraceTypeQuery1", bTraceComplex=False, bIgnoreSelf=True)
    fire = run(g, fire, trace)
    hit = call(g, "/Script/Engine.GameplayStatics.BreakHitResult", Hit=pin(trace, "OutHit", True))
    clear, blocked = branch(g, fire, math(g, "EqualEqual_ObjectObject", A=pin(hit, "HitActor", True), B=bbget(g, "TargetActor", "Object")))
    reply(g, blocked, "Rejected", "WorldOrFriendlyShotLane")
    eyes = call(g, "/Script/Engine.Actor.GetActorEyesViewPoint", self=pawn)
    if pins.is_valid(lib.find_execute_pin(eyes)):
        clear = run(g, clear, eyes)
    origin = pin(eyes, "OutLocation", True)
    # Fixed-signature subtract is safe under the verified process-local setting.
    direction = math(g, "Normal", A=math(g, "Subtract_VectorVector", A=point, B=origin))
    clear = put(g, clear, "ActionInitialShotSequence", get(g, "ShotSequence", basepath, pawn))
    clear = external(g, clear, base, pawn, "PC_RequestFire", AimOrigin=origin, AimDirection=direction)
    accepted, rejected = branch(g, clear, math(g, "EqualEqual_IntInt", A=get(g, "ShotSequence", basepath, pawn),
        B=math(g, "Add_IntInt", A=get(g, "ActionInitialShotSequence"), B=1)))
    reply(g, rejected, "Rejected", "OriginalFireRejected")
    accepted = admitted(g, accepted, "Fire")
    terminal(g, accepted, "Completed", "OriginalShotSequenceObserved")
    compile(bp)

    g, flow, _ = function(bp, "PC_ObserveNPCAction")
    flow, _ = branch(g, flow, get(g, "ActionInFlight"))
    flow, pawn = cast(g, flow, own(g), base)
    flow, dead = branch(g, flow, math(g, "Greater_DoubleDouble", A=get(g, "Health", basepath, pawn), B=0))
    terminal(g, dead, "Cancelled", "PawnDied")
    current, stale = branch(g, flow, math(g, "EqualEqual_IntInt", A=get(g, "ActiveGeneration"), B=get(g, "RestoreGeneration", basepath, pawn)))
    terminal(g, stale, "Cancelled", "LifecycleGenerationChanged")
    current, stale_task = branch(g, current, math(g, "EqualEqual_IntInt", A=get(g, "ActiveTaskID"), B=bbget(g, "TaskID", "Int")))
    terminal(g, stale_task, "Cancelled", "TaskSuperseded")
    stop, reload = branch(g, current, math(g, "EqualEqual_NameName", A=get(g, "PendingNPCAction"), B="Stop"))
    elapsed = math(g, "Subtract_DoubleDouble", A=pure(g, "/Script/Engine.GameplayStatics.GetTimeSeconds"), B=get(g, "StopAcceptedGameTime"))
    stop, _ = branch(g, stop, math(g, "GreaterEqual_DoubleDouble", A=elapsed, B=.5))
    stable, drift = branch(g, stop, math(g, "LessEqual_DoubleDouble", A=distance(g, local(g), get(g, "StopOrigin")), B=1))
    terminal(g, stable, "Completed", "BodyStopObserved")
    terminal(g, drift, "Failed", "BodyStopDrift")
    valid, superseded = branch(g, reload, math(g, "EqualEqual_IntInt", A=get(g, "ActionID", basepath, pawn), B=get(g, "PendingOriginalActionID")))
    terminal(g, superseded, "Cancelled", "OriginalActionSuperseded")
    ready, _ = branch(g, valid, math(g, "EqualEqual_NameName", A=get(g, "ActionState", basepath, pawn), B="Ready"))
    conserved = math(g, "EqualEqual_IntInt", A=math(g, "Add_IntInt", A=get(g, "LoadedAmmo", basepath, pawn), B=get(g, "ReserveAmmo", basepath, pawn)), B=get(g, "ActionAmmoTotal"))
    good, bad = branch(g, ready, conserved)
    committed, uncommitted = branch(g, good, math(g, "EqualEqual_IntInt", A=get(g, "ReloadCommitCount", basepath, pawn),
        B=math(g, "Add_IntInt", A=get(g, "ActionInitialReloadCommit"), B=1)))
    terminal(g, committed, "Completed", "OriginalReloadReadyOneCommitConserved")
    cancelled, repeated = branch(g, uncommitted, math(g, "EqualEqual_IntInt", A=get(g, "ReloadCommitCount", basepath, pawn), B=get(g, "ActionInitialReloadCommit")))
    terminal(g, cancelled, "Cancelled", "OriginalReloadEndedWithoutCommit")
    terminal(g, repeated, "Failed", "OriginalReloadCommitCountInvalid")
    terminal(g, bad, "Failed", "OriginalReloadConservationFailed")
    save(bp, P["controller"])
    cls = unreal.EditorAssetLibrary.load_blueprint_class(P["controller"])
    service_bp = lib.create_blueprint_asset_with_parent(P["service"], unreal.BTService_BlueprintBase.static_class())
    compile(service_bp)
    sg = unreal.BlueprintGraphEditor.get_graph_editor_by_name(service_bp, "EventGraph")
    event = lib.add_event_override(service_bp, "ReceiveTickAI", unreal.IntPoint())
    flow, typed = cast(sg, lib.find_then_pin(event), pin(event, "OwnerController", True), cls)
    names = [n for n in sg.list_available_nodes([]) if n.split("|")[-1].replace(" ", "").lower() == "pcobservenpcaction"]
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
    for key, prefix in (("allied", "BP_PCAlliedSquad"), ("german", "BP_PCGermanSquad")):
        child = lib.create_blueprint_asset_with_parent(P[key], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + prefix + "V4"))
        compile(child)
        unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(P[key])).set_editor_property("ai_controller_class", cls)
        save(child, P[key])
    report["status"] = "pass_native_action_gate_requires_runtime_and_human_equipment"
except Exception:
    report["status"] = "failed_native_action_gate_author_preserve"
    report["errors"].append(traceback.format_exc())
finally:
    if settings is not None and original_promotion is not None:
        settings.set_editor_property("bEnableTypePromotion", original_promotion)
    for package in report["packages"]:
        p = package_file(package)
        report["files"].append({"package": package, "path": p.relative_to(ROOT).as_posix(), "size_bytes": p.stat().st_size, "sha256": digest(p)})
    report["protected_count"] = len(rows)
    report["protected_guards_unchanged"] = guards_match(rows)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    unreal.SystemLibrary.quit_editor()
