"""New native attachment actor for the imported static German rifle; no map save."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).parent))
from german_rifle_ue_common import ROOT, STORE, BASE, GUARDS, guard, read, sha, new_output
from ue_paris_graph_helpers import lib, wire, pin, call, pure, get, run

OUT = new_output(os.environ['CS549_GERMAN_UE_IDENTITY'])
(OUT / 'source.py').write_bytes(Path(__file__).read_bytes())
DEST = BASE + '/BP_PC_GermanRifleAttachmentV2'
r = {'status': 'starting', 'errors': [], 'package': DEST, 'native_files': [], 'map_saved': False}


def math(g, name, **kwargs):
    return pure(g, '/Script/Engine.KismetMathLibrary.' + name, **kwargs)


def branch(g, flow, condition):
    node = g.add_branch_node()
    wire(flow, lib.find_execute_pin(node))
    wire(condition, pin(node, 'Condition'))
    return pin(node, 'then', True), pin(node, 'else', True)


try:
    r['guard_count'] = guard()
    assert not hasattr(unreal, 'ParisBlueprintAuthoring')
    imported = read(STORE / 'Evidence/GermanRifleUEV1' / os.environ.get('CS549_GERMAN_IMPORT_SOURCE', 'import_v3') / 'result.json')
    assert not imported['errors'] and imported['status'].startswith('native_import_checked')
    for f in imported['native_files']:
        assert sha(ROOT / f['path']) == f['sha256'], f['path']
    assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
    config = read(GUARDS)
    bp = lib.create_blueprint_asset_with_parent(DEST, unreal.StaticMeshActor.static_class())
    events = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'EventGraph')
    combatant_cls = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2')
    assert events.add_member_variable('GripMesh', lib.get_object_reference_type(unreal.SkeletalMeshComponent.static_class()))
    assert events.add_member_variable('Combatant', lib.get_object_reference_type(combatant_cls))
    for name, v in zip(('GripX', 'GripY', 'GripZ'), config['grip_anchor_cm']):
        assert events.add_member_variable(name, lib.get_basic_type_by_name('real'), str(v))
    for name in ('GripMesh', 'Combatant', 'GripX', 'GripY', 'GripZ'):
        lib.set_blueprint_variable_instance_editable(bp, name, True)
    assert lib.compile_blueprint(bp)
    cls = unreal.EditorAssetLibrary.load_blueprint_class(DEST)
    cdo = unreal.get_default_object(cls)
    component = cdo.get_component_by_class(unreal.StaticMeshComponent)
    component.set_mobility(unreal.ComponentMobility.MOVABLE)
    component.set_static_mesh(unreal.load_asset(imported['mesh']))
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_editor_property('can_ever_affect_navigation', False)
    g = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, 'PC_UpdateGermanRifleAttachment')
    mesh, actor = get(g, 'GripMesh'), get(g, 'Combatant')
    valid = math(g, 'BooleanAND', A=pure(g, '/Script/Engine.KismetSystemLibrary.IsValid', Object=mesh), B=pure(g, '/Script/Engine.KismetSystemLibrary.IsValid', Object=actor))
    flow, _ = branch(g, g.find_graph_entry_pin(), valid)
    flow, _ = branch(g, flow, math(g, 'Not_PreBool', A=get(g, 'IsDead', combatant_cls.get_path_name(), actor)))
    state = get(g, 'ActionState', combatant_cls.get_path_name(), actor)
    reload = math(g, 'EqualEqual_NameName', A=state, B='Reloading')
    ready = math(g, 'EqualEqual_NameName', A=state, B='Ready')
    flow, _ = branch(g, flow, math(g, 'BooleanOR', A=reload, B=ready))

    def socket(n):
        return pure(g, '/Script/Engine.SceneComponent.GetSocketLocation', self=mesh, InSocketName=n)

    def hollow(side):
        fs = ('middle', 'ring', 'pinky') if side == 'r' else ('index', 'middle', 'ring', 'pinky')
        names = [f + '_0' + str(s) + '_' + side for f in fs for s in (2, 3)] + ['thumb_02_' + side, 'thumb_03_' + side]
        total = socket(names[0])
        for n in names[1:]:
            total = math(g, 'Add_VectorVector', A=total, B=socket(n))
        return math(g, 'Multiply_VectorFloat', A=total, B=1 / len(names))

    right, left = hollow('r'), hollow('l')
    direction = math(g, 'Subtract_VectorVector', A=left, B=right)
    flow, _ = branch(g, flow, math(g, 'Greater_DoubleDouble', A=math(g, 'VSizeSquared', A=direction), B=.01))
    look = call(g, '/Script/Engine.KismetMathLibrary.BreakRotator', InRot=math(g, 'FindLookAtRotation', Start=right, Target=left))
    held = math(g, 'MakeRotator', Pitch=0, Yaw=math(g, 'Subtract_DoubleDouble', A=pin(look, 'Yaw', True), B=90), Roll=math(g, 'Multiply_DoubleDouble', A=pin(look, 'Pitch', True), B=-1))
    original = read(ROOT / 'Assets/Integration/CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json')['rifle_attachment']['rotation']
    local = math(g, 'MakeTransform', Location='(X=0,Y=0,Z=0)', Rotation=f'(Pitch={original[0]},Yaw={original[1]},Roll={original[2]})', Scale='(X=1,Y=1,Z=1)')
    hand = pure(g, '/Script/Engine.SceneComponent.GetSocketTransform', self=mesh, InSocketName='hand_r')
    wrist = call(g, '/Script/Engine.KismetMathLibrary.BreakTransform', InTransform=math(g, 'ComposeTransforms', A=local, B=hand))
    rotation = math(g, 'SelectRotator', A=pin(wrist, 'Rotation', True), B=held, bPickA=reload)
    anchor = math(g, 'MakeVector', X=get(g, 'GripX'), Y=get(g, 'GripY'), Z=get(g, 'GripZ'))
    oriented = math(g, 'MakeTransform', Location='(X=0,Y=0,Z=0)', Rotation=rotation, Scale='(X=1,Y=1,Z=1)')
    location = math(g, 'Subtract_VectorVector', A=right, B=math(g, 'TransformLocation', T=oriented, Location=anchor))
    run(g, flow, call(g, '/Script/Engine.Actor.K2_SetActorLocationAndRotation', NewLocation=location, NewRotation=rotation, bSweep=False, bTeleport=True))
    event = lib.add_event_override(bp, 'ReceiveTick', unreal.IntPoint())
    run(events, lib.find_then_pin(event), call(events, 'PC_UpdateGermanRifleAttachment'))
    begin = lib.add_event_override(bp, 'ReceiveBeginPlay', unreal.IntPoint(0, 300))
    flow, _ = branch(events, lib.find_then_pin(begin), pure(events, '/Script/Engine.KismetSystemLibrary.IsValid', Object=get(events, 'GripMesh')))
    flow = run(events, flow, call(events, '/Script/Engine.Actor.AddTickPrerequisiteComponent', PrerequisiteComponent=get(events, 'GripMesh')))
    flow = run(events, flow, call(events, '/Script/Engine.Actor.SetTickGroup', NewTickGroup='TG_PostUpdateWork'))
    flow = run(events, flow, call(events, '/Script/Engine.Actor.SetActorEnableCollision', bNewActorEnableCollision=False))
    run(events, flow, call(events, '/Script/Engine.Actor.SetActorTickEnabled', bEnabled=True))
    assert lib.compile_blueprint(bp)
    r['graph_errors'] = [str(n) for n in g.list_nodes_with_errors() + events.list_nodes_with_errors()]
    assert not r['graph_errors']
    final_cdo = unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(DEST))
    final_cdo.set_actor_enable_collision(False)
    final_component = final_cdo.get_component_by_class(unreal.StaticMeshComponent)
    final_component.set_collision_profile_name('NoCollision')
    final_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    final_component.set_editor_property('can_ever_affect_navigation', False)
    assert guard()
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, False)
    p = STORE / ('Content/' + DEST.removeprefix('/Game/') + '.uasset')
    r['native_files'] = [{'path': p.relative_to(ROOT).as_posix(), 'size_bytes': p.stat().st_size, 'sha256': sha(p)}]
    r['grip_anchor_cm'] = config['grip_anchor_cm']
    r['muzzle_cm'] = config['muzzle_cm']
    r['status'] = 'saved_unselected_native_german_attachment_requires_contact_review'
except Exception:
    r['status'] = 'failed'
    r['errors'].append(traceback.format_exc())
finally:
    r['protected_files_unchanged'] = bool(guard())
    (OUT / 'result.json').write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
    unreal.log('CS549_GERMAN_AUTHOR ' + r['status'])
    unreal.SystemLibrary.quit_editor()
