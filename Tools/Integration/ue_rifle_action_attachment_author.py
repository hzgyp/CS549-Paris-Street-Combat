"""New standard Blueprint rifle-only fitting actor; does not select it in the city."""
import hashlib
import json
import os
import sys
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/RifleActionAttachmentV3' / os.environ['CS549_RIFLE_ACTION_AUTHOR_IDENTITY']
assert OUT.name.replace('_', '').isalnum() and not OUT.exists()
OUT.mkdir(parents=True)
DEST = '/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3'
inventory = json.loads((ROOT / 'Assets/Integration/CITY_WEAPON_TRANSFORM_DRAFT_INVENTORY_20261002.json').read_text())
deps = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text())
records = inventory['files'] + deps['files'] + inventory['retained_unselected_rejected_trial']

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

assert all(digest(ROOT / e['path']) == e['sha256'] for e in records)
assert not unreal.EditorAssetLibrary.does_asset_exist(DEST), 'Preserve occupied trial package'
fit = json.loads((OUT.parent / 'fit_v2/result.json').read_text())
assert not fit['errors'] and fit['source_clips_unchanged'] and fit['protected_36_unchanged']
sys.path.insert(0, str(Path(__file__).parent))
from ue_paris_graph_helpers import lib, pins, wire, pin, call, pure, get, run
report = {'scope': __doc__, 'status': 'initializing', 'errors': [], 'package': DEST}

def write():
    (OUT / 'result.json').write_text(json.dumps(report, indent=2))

def math(g, name, **inputs):
    return pure(g, '/Script/Engine.KismetMathLibrary.' + name, **inputs)

def branch(g, flow, condition):
    node = g.add_branch_node()
    wire(flow, lib.find_execute_pin(node))
    wire(condition, pin(node, 'Condition'))
    return pin(node, 'then', True), pin(node, 'else', True)

try:
    bp = lib.create_blueprint_asset_with_parent(DEST, unreal.StaticMeshActor.static_class())
    assert bp
    events = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'EventGraph')
    combatant_cls = unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2')
    assert events.add_member_variable('GripMesh', lib.get_object_reference_type(unreal.SkeletalMeshComponent.static_class()))
    assert events.add_member_variable('Combatant', lib.get_object_reference_type(combatant_cls))
    assert events.add_member_variable('LeftShiftCm', lib.get_basic_type_by_name('real'), '0.5')
    for name in ('GripMesh', 'Combatant', 'LeftShiftCm'):
        lib.set_blueprint_variable_instance_editable(bp, name, True)
    assert lib.compile_blueprint(bp)
    cls = unreal.EditorAssetLibrary.load_blueprint_class(DEST)
    cdo = unreal.get_default_object(cls)
    tick = cdo.get_editor_property('primary_actor_tick')
    group_type = type(tick.get_editor_property('tick_group'))
    report['tick_group_enum'] = str(group_type)
    tick.set_editor_property('tick_group', group_type.TG_POST_UPDATE_WORK)
    cdo.set_editor_property('primary_actor_tick', tick)
    component = cdo.get_component_by_class(unreal.StaticMeshComponent)
    component.set_mobility(unreal.ComponentMobility.MOVABLE)
    component.set_static_mesh(unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand'))
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    g = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, 'PC_UpdateRifleAttachment')
    mesh, actor = get(g, 'GripMesh'), get(g, 'Combatant')
    valid = math(g, 'BooleanAND', A=pure(g, '/Script/Engine.KismetSystemLibrary.IsValid', Object=mesh),
                 B=pure(g, '/Script/Engine.KismetSystemLibrary.IsValid', Object=actor))
    flow, invalid = branch(g, g.find_graph_entry_pin(), valid)
    flow, dead = branch(g, flow, math(g, 'Not_PreBool', A=get(g, 'IsDead', combatant_cls.get_path_name(), actor)))
    state = get(g, 'ActionState', combatant_cls.get_path_name(), actor)
    is_reload = math(g, 'EqualEqual_NameName', A=state, B='Reloading')
    is_ready = math(g, 'EqualEqual_NameName', A=state, B='Ready')
    flow, other = branch(g, flow, math(g, 'BooleanOR', A=is_reload, B=is_ready))
    def socket(n):
        return pure(g, '/Script/Engine.SceneComponent.GetSocketLocation', self=mesh, InSocketName=n)
    def hollow(side):
        fs = ('middle', 'ring', 'pinky') if side == 'r' else ('index', 'middle', 'ring', 'pinky')
        names = [f+'_0'+str(s)+'_'+side for f in fs for s in (2, 3)] + ['thumb_02_'+side, 'thumb_03_'+side]
        total = socket(names[0])
        for n in names[1:]:
            total = math(g, 'Add_VectorVector', A=total, B=socket(n))
        return math(g, 'Multiply_VectorFloat', A=total, B=1/len(names))
    right, left = hollow('r'), hollow('l')
    direction = math(g, 'Subtract_VectorVector', A=left, B=right)
    flow, short = branch(g, flow, math(g, 'Greater_DoubleDouble', A=math(g, 'VSizeSquared', A=direction), B=.01))
    look = call(g, '/Script/Engine.KismetMathLibrary.BreakRotator', InRot=math(g, 'FindLookAtRotation', Start=right, Target=left))
    held_rot = math(g, 'MakeRotator', Pitch=0,
                    Yaw=math(g, 'Subtract_DoubleDouble', A=pin(look, 'Yaw', True), B=90),
                    Roll=math(g, 'Multiply_DoubleDouble', A=pin(look, 'Pitch', True), B=-1))
    r = inventory['rifle_attachment']['rotation']
    local = math(g, 'MakeTransform', Location='(X=0,Y=0,Z=0)', Rotation=f'(Pitch={r[0]},Yaw={r[1]},Roll={r[2]})', Scale='(X=1,Y=1,Z=1)')
    hand = pure(g, '/Script/Engine.SceneComponent.GetSocketTransform', self=mesh, InSocketName='hand_r')
    wrist = call(g, '/Script/Engine.KismetMathLibrary.BreakTransform', InTransform=math(g, 'ComposeTransforms', A=local, B=hand))
    rotation = math(g, 'SelectRotator', A=pin(wrist, 'Rotation', True), B=held_rot, bPickA=is_reload)
    anchor = math(g, 'MakeVector', X=math(g, 'Multiply_DoubleDouble', A=get(g, 'LeftShiftCm'), B=-1), Y=-8, Z=0)
    oriented = math(g, 'MakeTransform', Location='(X=0,Y=0,Z=0)', Rotation=rotation, Scale='(X=1,Y=1,Z=1)')
    location = math(g, 'Subtract_VectorVector', A=right, B=math(g, 'TransformLocation', T=oriented, Location=anchor))
    run(g, flow, call(g, '/Script/Engine.Actor.K2_SetActorLocationAndRotation', NewLocation=location,
                     NewRotation=rotation, bSweep=False, bTeleport=True))
    event = lib.add_event_override(bp, 'ReceiveTick', unreal.IntPoint(0, 0))
    assert event
    run(events, lib.find_then_pin(event), call(events, 'PC_UpdateRifleAttachment'))
    begin = lib.add_event_override(bp, 'ReceiveBeginPlay', unreal.IntPoint(0, 300))
    assert begin
    start, invalid = branch(events, lib.find_then_pin(begin), pure(events, '/Script/Engine.KismetSystemLibrary.IsValid', Object=get(events, 'GripMesh')))
    start = run(events, start, call(events, '/Script/Engine.Actor.AddTickPrerequisiteComponent', PrerequisiteComponent=get(events, 'GripMesh')))
    start = run(events, start, call(events, '/Script/Engine.Actor.SetTickGroup', NewTickGroup='TG_PostUpdateWork'))
    run(events, start, call(events, '/Script/Engine.Actor.SetActorTickEnabled', bEnabled=True))
    assert lib.compile_blueprint(bp)
    report['graph_errors'] = [str(n) for n in g.list_nodes_with_errors() + events.list_nodes_with_errors()]
    assert not report['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    p = STORE / ('Content/' + DEST.removeprefix('/Game/') + '.uasset')
    report['saved_trial'] = {'package': DEST, 'path': p.relative_to(ROOT).as_posix(), 'sha256': digest(p), 'size_bytes': p.stat().st_size}
    report['status'] = 'saved_unselected_rifle_actor_requires_fresh_runtime_review'
except Exception:
    report['status'] = 'failed'
    report['errors'].append(traceback.format_exc())
finally:
    report['protected_36_unchanged'] = all(digest(ROOT / e['path']) == e['sha256'] for e in records)
    write()
    unreal.SystemLibrary.quit_editor()
