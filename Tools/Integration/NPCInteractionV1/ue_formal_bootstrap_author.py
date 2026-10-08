"""New native bootstrap assets and read-only survey; no formal map save."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEST, ROOT, STORE, digest, guard_rows, guards_match, package_file
from ue_graph import lib, pins, pin, wire, value, call, pure, get, run, math, branch, put, function, invoke, cast

VERSION = os.environ["CS549_NPC_BEHAVIOR_VERSION"]
P = {k: DEST + "/" + n + VERSION for k, n in (("controller", "BP_PCNPCFormalCombat"),
    ("tree", "BT_PC_NPCFormalCombat"), ("service", "BTS_PC_NPCFormalBootstrap"),
    ("allied", "BP_PCAlliedFormalCombat"), ("german", "BP_PCGermanFormalCombat"))}
OUT = STORE / "Evidence/NPCInteractionV1" / os.environ["CS549_NPC_IDENTITY"]
RESULT = OUT / "formal_bootstrap_author.json"
rows = guard_rows()
report = {"identity": os.environ["CS549_NPC_IDENTITY"], "errors": [], "packages": [], "files": [],
          "map_saved": False, "scope": "new bootstrap packages; saved roster read-only; no presentation edits"}
settings = original = None


def compile(bp):
    assert lib.compile_blueprint(bp)
    assert all(not unreal.BlueprintGraphEditor.get_graph_editor(g).list_nodes_with_errors() for g in lib.list_graphs(bp))


def save(bp, package):
    if isinstance(bp, unreal.Blueprint):
        compile(bp)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    report["packages"].append(package)
    RESULT.write_text(json.dumps(report, indent=2) + "\n")


def announce(g, flow, text):
    name = pure(g, "/Script/Engine.KismetSystemLibrary.GetObjectName", Object=pure(g, "/Script/Engine.Controller.K2_GetPawn"))
    message = pure(g, "/Script/Engine.KismetStringLibrary.Concat_StrStr", A=text, B=name)
    return invoke(g, flow, "/Script/Engine.KismetSystemLibrary.PrintString", InString=message,
                  bPrintToScreen=False, bPrintToLog=True, Duration=0)


try:
    assert guards_match(rows) and all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in P.values())
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level("/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    survey = []
    for a in actors.get_all_level_actors():
        label = a.get_actor_label()
        if label.startswith("PC_City_") or "GripPolicy" in a.get_class().get_name() or isinstance(a, unreal.NavMeshBoundsVolume):
            item = {"label": label, "class": a.get_class().get_path_name(), "transform": str(a.get_actor_transform())}
            if isinstance(a, unreal.Character):
                item.update({"team": a.get_editor_property("TeamId"), "mesh": a.mesh.get_editor_property("skeletal_mesh_asset").get_path_name(),
                             "anim_class": str(a.mesh.get_editor_property("anim_class")), "controller_class": str(a.get_editor_property("ai_controller_class")),
                             "gun": str(a.get_editor_property("WeaponAppearance"))})
            survey.append(item)
    report["saved_map_survey"] = survey
    settings = unreal.get_default_object(unreal.load_class(None, "/Script/BlueprintGraph.BlueprintEditorSettings"))
    original = settings.get_editor_property("bEnableTypePromotion")
    settings.set_editor_property("bEnableTypePromotion", False)
    tree = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(P["tree"].rsplit("/", 1)[1], DEST, unreal.load_asset(DEST + "/BT_PC_NPCCombatV2"))
    bp = lib.create_blueprint_asset_with_parent(P["controller"], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/BP_PCNPCCombatV2"))
    ev = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, "EventGraph")
    for name in ("BootstrapReady", "BootstrapFailed"):
        assert ev.add_member_variable(name, lib.get_basic_type_by_name("bool"), "false")
    compile(bp)
    begin = lib.add_event_override(bp, "ReceiveBeginPlay", unreal.IntPoint())
    use = call(ev, "/Script/AIModule.AIController.UseBlackboard", BlackboardAsset=DEST + "/BB_PC_NPCInteractionV1")
    flow = run(ev, lib.find_then_pin(begin), use)
    flow = put(ev, flow, "NPCBlackboard", pin(use, "BlackboardComponent", True))
    invoke(ev, flow, "/Script/AIModule.AIController.RunBehaviorTree", BTAsset=tree.get_path_name())
    g, flow, _ = function(bp, "PC_BootstrapCombat")
    flow, _ = branch(g, flow, math(g, "Not_PreBool", A=math(g, "BooleanOR", A=get(g, "BootstrapReady"), B=get(g, "BootstrapFailed"))))
    expired, flow = branch(g, flow, math(g, "Greater_DoubleDouble", A=pure(g, "/Script/Engine.Actor.GetGameTimeSinceCreation"), B=10))
    expired = put(g, expired, "BootstrapFailed", True)
    expired = invoke(g, expired, "PC_EnableCombat", Enabled=False)
    announce(g, expired, "PARIS_NPC_COMBAT_BOOTSTRAP_FAILED ")
    base = unreal.EditorAssetLibrary.load_blueprint_class("/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2")
    flow, pawn = cast(g, flow, pure(g, "/Script/Engine.Controller.K2_GetPawn"), base)
    mesh = get(g, "Mesh", "/Script/Engine.Character", pawn)
    weapon = get(g, "WeaponAppearance", base.get_path_name(), pawn)
    flow, _ = branch(g, flow, pure(g, "/Script/Engine.KismetSystemLibrary.IsValid", Object=weapon))
    allied, german = branch(g, flow, math(g, "EqualEqual_IntInt", A=get(g, "TeamId", base.get_path_name(), pawn), B=0))
    for flow, gun_path, config_path in ((allied, "/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3",
          "/Game/ParisCombat/Animation/AlliedGripV15/DA_PC_AlliedGripV16"),
         (german, "/Game/ParisCombat/Weapons/GermanRifleUEV1/BP_PC_GermanRifleAttachmentV2",
          "/Game/ParisCombat/Animation/GermanGripV14/DA_PC_GermanGripV11")):
        gun_class = unreal.EditorAssetLibrary.load_blueprint_class(gun_path)
        flow, gun = cast(g, flow, weapon, gun_class)
        good = math(g, "BooleanAND", A=math(g, "EqualEqual_ObjectObject", A=get(g, "Combatant", gun_class.get_path_name(), gun), B=pawn),
                    B=math(g, "EqualEqual_ObjectObject", A=get(g, "GripMesh", gun_class.get_path_name(), gun), B=mesh))
        flow, _ = branch(g, flow, good)
        pp_class = unreal.load_asset(config_path).get_editor_property("PostProcessClass")
        flow, pp = cast(g, flow, pure(g, "/Script/Engine.SkeletalMeshComponent.GetPostProcessInstance", self=mesh), pp_class)
        pp_path = "/Script/ParisNPCGripV15.ParisNPCGripAnimInstance"
        good = math(g, "BooleanAND", A=get(g, "ValidInput", pp_path, pp),
                    B=math(g, "BooleanAND", A=math(g, "Greater_Int64Int64", A=get(g, "Evaluations", pp_path, pp), B=0),
                        B=math(g, "Less_DoubleDouble", A=get(g, "ProtectionError", pp_path, pp), B=.0001)))
        flow, _ = branch(g, flow, good)
        flow = invoke(g, flow, "PC_SetSearchRole", Patrol=False, PatrolPoint=pure(g, "/Script/Engine.Actor.K2_GetActorLocation", self=pawn), Radius=500)
        flow = invoke(g, flow, "PC_ConfigureNPCEquipment", NumericVerified=True, HumanAccepted=True)
        flow = invoke(g, flow, "PC_EnableCombat", Enabled=True)
        flow = put(g, flow, "BootstrapReady", True)
        announce(g, flow, "PARIS_NPC_COMBAT_READY ")
    save(bp, P["controller"])
    cls = unreal.EditorAssetLibrary.load_blueprint_class(P["controller"])
    service_bp = lib.create_blueprint_asset_with_parent(P["service"], unreal.BTService_BlueprintBase.static_class())
    compile(service_bp)
    sg = unreal.BlueprintGraphEditor.get_graph_editor_by_name(service_bp, "EventGraph")
    event = lib.add_event_override(service_bp, "ReceiveTickAI", unreal.IntPoint())
    flow, typed = cast(sg, lib.find_then_pin(event), pin(event, "OwnerController", True), cls)
    names = [n for n in sg.list_available_nodes([]) if n.split("|")[-1].replace(" ", "").lower() == "pcbootstrapcombat"]
    assert names
    node = sg.create_node_from_name(names[0], unreal.Vector2D(), [], cls)
    wire(typed, lib.find_self_pin(node))
    run(sg, flow, node)
    save(service_bp, P["service"])
    service = unreal.new_object(unreal.EditorAssetLibrary.load_blueprint_class(P["service"]), outer=tree)
    service.set_editor_property("interval", .25)
    service.set_editor_property("random_deviation", 0)
    root = tree.get_editor_property("root_node")
    root.set_editor_property("services", [service] + list(root.get_editor_property("services")))
    save(tree, P["tree"])
    for key, parent in (("allied", "BP_PCAlliedCombatV2"), ("german", "BP_PCGermanCombatV2")):
        child = lib.create_blueprint_asset_with_parent(P[key], unreal.EditorAssetLibrary.load_blueprint_class(DEST + "/" + parent))
        compile(child)
        unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(P[key])).set_editor_property("ai_controller_class", cls)
        save(child, P[key])
    report["status"] = "pass_formal_bootstrap_authored_runtime_unpassed"
except Exception:
    report["status"] = "failed_formal_bootstrap_author_preserve"
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
