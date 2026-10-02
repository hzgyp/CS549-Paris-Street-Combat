"""Hash-guarded real-city Blueprint combat authoring; no vendor/old draft writes."""
import hashlib
import json
import os
import traceback
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/Setup'
IDENTITY = os.environ.get('CS549_COMBAT_AUTHOR_IDENTITY', 'combat_author_v1')
assert IDENTITY.replace('_', '').isalnum()
DEST = OUT / (IDENTITY + '.json')
assert not DEST.exists(), 'Preserve occupied author evidence'
BASE = '/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2'
WIDGET = '/Game/ParisCombat/UI/CityGameplayV1/WBP_PCParisStatusV1'
OLD = '/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/BP_PCCombatantReloadV1'
PREFIX = '/Game/ParisCombat/Blueprints/CityGameplayV1/'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
inventory = json.loads((ROOT / 'Assets/Integration/CITY_GAMEPLAY_DRAFT_INVENTORY_20261002.json').read_text())
old_inventory = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
report = {'scope': 'Native Blueprint combat/HUD on actual city; not runtime/AI/mission/FP/performance acceptance',
          'assets': [], 'graph_nodes': {}, 'errors': []}
lib = unreal.BlueprintEditorLibrary
pins = unreal.BlueprintGraphPinLibrary
position = 0


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def checkpoint():
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')


def wire(a, b):
    assert pins.is_valid(a) and pins.is_valid(b), 'Missing graph pin'
    assert pins.try_create_connection(a, b), 'Rejected graph connection: ' + str(pins.get_pin_name(a)) + ' -> ' + str(pins.get_pin_name(b))


def pin(node, name, output=False):
    result = (lib.find_output_pin if output else lib.find_input_pin)(node, name)
    assert pins.is_valid(result), 'Missing pin ' + name + ': ' + node.get_name()
    return result


def value(target, source):
    if isinstance(source, unreal.BlueprintGraphPin):
        wire(source, target)
    else:
        assert pins.set_pin_value(target, str(source)), 'Rejected literal ' + str(source)


def place(node):
    global position
    assert node
    lib.set_node_pos(node, unreal.IntPoint(350 + (position % 8) * 350, (position // 8) * 250))
    position += 1
    return node


def call(g, function, **inputs):
    node = place(g.add_call_function_node(function))
    for name, val in inputs.items():
        value(pin(node, name), val)
    return node


def pure(g, function, **inputs):
    return pin(call(g, function, **inputs), 'ReturnValue', True)


def math(g, function, **inputs):
    if function == 'Multiply_VectorFloat' and isinstance(inputs.get('B'), (int, float)):
        # Automatic operator promotion otherwise erases the disconnected scalar
        # default. A uniform typed vector scale preserves the intended operation.
        amount = inputs['B']
        inputs['B'] = pure(g, '/Script/Engine.KismetMathLibrary.MakeVector', X=amount, Y=amount, Z=amount)
        function = 'Multiply_VectorVector'
    return pure(g, '/Script/Engine.KismetMathLibrary.' + function, **inputs)


def get(g, name, cls='', target=None):
    node = place(g.add_get_member_variable_node(name, cls))
    if target is not None:
        wire(target, lib.find_self_pin(node))
    return pin(node, name, True)


def put(g, flow, name, source):
    node = place(g.add_set_member_variable_node(name))
    value(pin(node, name), source)
    wire(flow, lib.find_execute_pin(node))
    return lib.find_then_pin(node)


def branch(g, flow, condition):
    node = place(g.add_branch_node())
    wire(flow, lib.find_execute_pin(node))
    value(pin(node, 'Condition'), condition)
    return lib.find_then_pin(node), pin(node, 'else', True)


def both(g, conditions):
    result = conditions[0]
    for other in conditions[1:]:
        result = math(g, 'BooleanAND', A=result, B=other)
    return result


def run(g, flow, node):
    wire(flow, lib.find_execute_pin(node))
    return lib.find_then_pin(node)


def cast_to(g, flow, obj, cls):
    node = place(g.create_node_from_name('Utilities|Casting|CastToCharacter', unreal.Vector2D(), [obj]))
    assert g.retarget_node_class(node, unreal.Character.static_class(), cls), 'Cannot retarget installed cast node'
    wire(obj, pin(node, 'Object'))
    wire(flow, lib.find_execute_pin(node))
    outputs = [p for p in lib.list_all_pins(node) if str(pins.get_pin_name(p)).startswith('As')]
    assert len(outputs) == 1
    return lib.find_then_pin(node), outputs[0]


def trace(g, flow, start, end, sphere=False):
    node = call(g, '/Script/Engine.KismetSystemLibrary.' + ('SphereTraceSingle' if sphere else 'LineTraceSingle'),
                Start=start, End=end, TraceChannel='TraceTypeQuery1', bTraceComplex='false', bIgnoreSelf='true')
    if sphere:
        value(pin(node, 'Radius'), 2)
    return run(g, flow, node), node


def save(bp, package):
    assert lib.compile_blueprint(bp), 'Compile failed: ' + package
    report['graph_nodes'][package] = {g.get_name(): len(unreal.BlueprintGraphEditor.get_graph_editor(g).list_all_nodes()) for g in lib.list_graphs(bp)}
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report['assets'].append(package)
    checkpoint()


try:
    for item in inventory['files'] + old_inventory['files']:
        assert digest(ROOT / item['path']) == item['sha256'], 'Unexpected unsynchronized draft: ' + item['path']
    assert not unreal.EditorAssetLibrary.does_asset_exist(BASE)
    assert not unreal.EditorAssetLibrary.does_asset_exist(WIDGET)
    parent = unreal.EditorAssetLibrary.load_blueprint_class(OLD)
    bp = lib.create_blueprint_asset_with_parent(BASE, parent)
    assert bp
    events = unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp, 'EventGraph')
    for name, kind, default in (('ShotGeneration', 'int', '-1'), ('ShotSequence', 'int', '0'),
                                ('NextShotTime', 'real', '0'), ('ShotOutcome', 'string', 'Not fired')):
        assert events.add_member_variable(name, lib.get_basic_type_by_name(kind), default)
    assert events.add_member_variable('WeaponAppearance', lib.get_object_reference_type(unreal.Actor.static_class()))
    assert lib.compile_blueprint(bp)
    g = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, 'PC_RequestFire')
    vector_type = lib.get_struct_type(unreal.load_object(None, '/Script/CoreUObject.Vector'))
    origin = g.add_graph_input_parameter('AimOrigin', vector_type)
    direction = g.add_graph_input_parameter('AimDirection', vector_type)
    flow = g.find_graph_entry_pin()
    flow = put(g, flow, 'ShotOutcome', 'Rejected')
    current_gen = get(g, 'RestoreGeneration')
    mismatch = math(g, 'NotEqual_IntInt', A=get(g, 'ShotGeneration'), B=current_gen)
    changed, same = branch(g, flow, mismatch)
    changed = put(g, changed, 'ShotGeneration', current_gen)
    changed = put(g, changed, 'NextShotTime', 0)
    # Both disjoint paths call one separate worker, avoiding an ambiguous exec merge.
    report['fire_entry_pending'] = True
    worker_graph = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, 'PC_DoShot')
    wo = worker_graph.add_graph_input_parameter('AimOrigin', vector_type)
    wd = worker_graph.add_graph_input_parameter('AimDirection', vector_type)
    assert lib.compile_blueprint(bp)
    for path in (changed, same):
        run(g, path, call(g, 'PC_DoShot', AimOrigin=origin, AimDirection=direction))
    report['fire_entry_pending'] = False
    g = worker_graph
    flow = g.find_graph_entry_pin()
    time_now = pure(g, '/Script/Engine.GameplayStatics.GetTimeSeconds')
    weapon = get(g, 'WeaponAppearance')
    length = math(g, 'VSizeSquared', A=wd)
    origin_length = math(g, 'VSizeSquared', A=wo)
    guard = both(g, [math(g, 'Not_PreBool', A=get(g, 'IsDead')),
        math(g, 'Greater_DoubleDouble', A=get(g, 'Health'), B=0),
        math(g, 'EqualEqual_NameName', A=get(g, 'ActionState'), B='Ready'),
        math(g, 'Greater_IntInt', A=get(g, 'LoadedAmmo'), B=0),
        math(g, 'LessEqual_IntInt', A=get(g, 'LoadedAmmo'), B=get(g, 'Capacity')),
        math(g, 'GreaterEqual_DoubleDouble', A=time_now, B=get(g, 'NextShotTime')),
        pure(g, '/Script/Engine.KismetSystemLibrary.IsValid', Object=weapon),
        math(g, 'Greater_DoubleDouble', A=length, B=.0001),
        math(g, 'Less_DoubleDouble', A=length, B=1000000),
        math(g, 'Less_DoubleDouble', A=origin_length, B=1000000000000)])
    flow, rejected = branch(g, flow, guard)
    flow = put(g, flow, 'LoadedAmmo', math(g, 'Subtract_IntInt', A=get(g, 'LoadedAmmo'), B=1))
    flow = put(g, flow, 'ShotSequence', math(g, 'Add_IntInt', A=get(g, 'ShotSequence'), B=1))
    flow = put(g, flow, 'NextShotTime', math(g, 'Add_DoubleDouble', A=time_now, B=.25))
    flow = put(g, flow, 'ShotOutcome', 'Miss')
    normal = math(g, 'Normal', A=wd)
    end = math(g, 'Add_VectorVector', A=wo, B=math(g, 'Multiply_VectorFloat', A=normal, B=20000))
    flow, camera_trace = trace(g, flow, wo, end)
    camera_hit = call(g, '/Script/Engine.GameplayStatics.BreakHitResult', Hit=pin(camera_trace, 'OutHit', True))
    aim = math(g, 'SelectVector', A=pin(camera_hit, 'ImpactPoint', True), B=end, bPickA=pin(camera_trace, 'ReturnValue', True))
    transform = pure(g, '/Script/Engine.Actor.GetTransform', self=weapon)
    muzzle = math(g, 'TransformLocation', T=transform, Location='(X=0,Y=83.23,Z=0)')
    grip = pure(g, '/Script/Engine.Actor.K2_GetActorLocation', self=weapon)
    flow, corridor = trace(g, flow, grip, muzzle, True)
    blocked, clear = branch(g, flow, pin(corridor, 'ReturnValue', True))
    put(g, blocked, 'ShotOutcome', 'Barrel blocked')
    tiny = math(g, 'Multiply_VectorFloat', A=normal, B=.1)
    flow, occupancy = trace(g, clear, math(g, 'Subtract_VectorVector', A=muzzle, B=tiny),
                             math(g, 'Add_VectorVector', A=muzzle, B=tiny), True)
    blocked, clear = branch(g, flow, pin(occupancy, 'ReturnValue', True))
    put(g, blocked, 'ShotOutcome', 'Muzzle blocked')
    aim_delta = math(g, 'Subtract_VectorVector', A=aim, B=muzzle)
    aim_normal = math(g, 'Normal', A=aim_delta)
    bullet_end = math(g, 'Add_VectorVector', A=aim,
        B=math(g, 'Multiply_VectorFloat', A=aim_normal, B=2))
    flow, bullet = trace(g, clear, muzzle, bullet_end)
    hit, miss = branch(g, flow, pin(bullet, 'ReturnValue', True))
    hit = put(g, hit, 'ShotOutcome', 'World blocked')
    hit_data = call(g, '/Script/Engine.GameplayStatics.BreakHitResult', Hit=pin(bullet, 'OutHit', True))
    hit, target = cast_to(g, hit, pin(hit_data, 'HitActor', True), parent)
    enemy, friend = branch(g, hit, math(g, 'NotEqual_IntInt', A=get(g, 'TeamId'),
        B=get(g, 'TeamId', parent.get_path_name(), target)))
    put(g, friend, 'ShotOutcome', 'Friendly blocked')
    living, dead = branch(g, enemy, math(g, 'Greater_DoubleDouble', A=get(g, 'Health', parent.get_path_name(), target), B=0))
    put(g, dead, 'ShotOutcome', 'Dead body blocked')
    damage = call(g, 'PC_ApplyDamage', Amount=35)
    wire(target, lib.find_self_pin(damage))
    living = run(g, living, damage)
    put(g, living, 'ShotOutcome', 'Hostile hit')
    save(bp, BASE)
    report['status'] = 'saved_shared_shot_blueprint_only_follow_on_pending'
except Exception:
    report['status'] = 'failed_preserve_task_drafts'
    report['errors'].append(traceback.format_exc())
finally:
    report['previous_28_drafts_unchanged'] = all(digest(ROOT / f['path']) == f['sha256'] for f in old_inventory['files'])
    report['prior_five_city_drafts_unchanged'] = all(digest(ROOT / f['path']) == f['sha256'] for f in inventory['files'])
    report['saved_files'] = []
    for package in report['assets']:
        file = STORE / 'Content' / (package.removeprefix('/Game/') + '.uasset')
        report['saved_files'].append({'package': package, 'path': file.relative_to(ROOT).as_posix(),
                                     'size_bytes': file.stat().st_size, 'sha256': digest(file)})
    checkpoint()
unreal.log('CS549_COMBAT_AUTHOR ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved combat author evidence')
