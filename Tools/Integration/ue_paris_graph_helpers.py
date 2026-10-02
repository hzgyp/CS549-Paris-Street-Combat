"""Small installed K2 graph helpers; runtime graphs never call this module."""
import unreal

lib = unreal.BlueprintEditorLibrary
pins = unreal.BlueprintGraphPinLibrary
position = 0


def wire(a, b):
    assert pins.is_valid(a) and pins.is_valid(b), 'Missing graph pin'
    assert pins.try_create_connection(a, b), 'Rejected graph connection'


def pin(node, name, output=False):
    p = (lib.find_output_pin if output else lib.find_input_pin)(node, name)
    assert pins.is_valid(p), 'Missing pin ' + name + ': ' + node.get_name()
    return p


def value(target, source):
    if isinstance(source, unreal.BlueprintGraphPin):
        wire(source, target)
    else:
        assert pins.set_pin_value(target, str(source)), 'Rejected literal: ' + str(source)


def place(node):
    global position
    assert node
    lib.set_node_pos(node, unreal.IntPoint(350 + (position % 8) * 350, (position // 8) * 250))
    position += 1
    return node


def call(g, function, **inputs):
    if function == '/Script/Engine.KismetMathLibrary.Multiply_VectorFloat' and isinstance(inputs.get('B'), (int, float)):
        amount = inputs['B']
        inputs['B'] = pure(g, '/Script/Engine.KismetMathLibrary.MakeVector', X=amount, Y=amount, Z=amount)
        function = '/Script/Engine.KismetMathLibrary.Multiply_VectorVector'
    node = place(g.add_call_function_node(function))
    for name, v in inputs.items():
        value(pin(node, name), v)
    return node


def pure(g, function, **inputs):
    return pin(call(g, function, **inputs), 'ReturnValue', True)


def get(g, name, cls='', target=None):
    node = place(g.add_get_member_variable_node(name, cls))
    if target is not None:
        wire(target, lib.find_self_pin(node))
    return pin(node, name, True)


def run(g, flow, node):
    wire(flow, lib.find_execute_pin(node))
    return lib.find_then_pin(node)


def cast_to(g, flow, obj, cls):
    node = place(g.create_node_from_name('Utilities|Casting|CastToCharacter', unreal.Vector2D(), [obj]))
    assert g.retarget_node_class(node, unreal.Character.static_class(), cls)
    wire(obj, pin(node, 'Object'))
    wire(flow, lib.find_execute_pin(node))
    outputs = [p for p in lib.list_all_pins(node) if str(pins.get_pin_name(p)).startswith('As')]
    assert len(outputs) == 1
    return lib.find_then_pin(node), outputs[0]


def build_new_status_widget(package, combatant_class):
    """Retained v4 UMG authoring source; caller must hash-guard and save.

    New-only template construction requires the Editor-only bridge. Generated
    normal UMG/K2 graphs do not call this module or the bridge at runtime.
    """
    assert package.startswith('/Game/ParisCombat/UI/CityGameplayV1/')
    assert not unreal.EditorAssetLibrary.does_asset_exist(package)
    factory = unreal.WidgetBlueprintFactory()
    factory.set_editor_property('parent_class', unreal.UserWidget.static_class())
    widget = unreal.AssetToolsHelpers.get_asset_tools().create_asset(package.rsplit('/', 1)[1],
        package.rsplit('/', 1)[0], unreal.WidgetBlueprint, factory)
    assert widget and unreal.ParisBlueprintAuthoring.create_status_widget_template(widget)
    assert lib.compile_blueprint(widget)
    widget_class = unreal.EditorAssetLibrary.load_blueprint_class(package)
    unreal.get_default_object(widget_class).set_editor_property('is_focusable', False)
    g = unreal.BlueprintGraphEditor.create_and_edit_function_graph(widget, 'PC_UpdateStatus')
    pawn = pure(g, '/Script/UMG.UserWidget.GetOwningPlayerPawn')
    flow, actor = cast_to(g, g.find_graph_entry_pin(), pawn, combatant_class)
    hp_int = pure(g, '/Script/Engine.KismetMathLibrary.FTrunc',
                  A=get(g, 'Health', combatant_class.get_path_name(), actor))
    hp = pure(g, '/Script/Engine.KismetStringLibrary.Conv_IntToString', InInt=hp_int)
    def join(a, b):
        return pure(g, '/Script/Engine.KismetStringLibrary.Concat_StrStr', A=a, B=b)
    line = join('HP ', hp)
    for label, field, converter in (
        ('   AMMO ', 'LoadedAmmo', 'Conv_IntToString'), ('/', 'ReserveAmmo', 'Conv_IntToString'),
        ('   ', 'ActionState', 'Conv_NameToString'), ('   ', 'ShotOutcome', None),
        (' #', 'ShotSequence', 'Conv_IntToString')):
        datum = get(g, field, combatant_class.get_path_name(), actor)
        if converter:
            datum = pure(g, '/Script/Engine.KismetStringLibrary.' + converter,
                **{('InName' if converter == 'Conv_NameToString' else 'InInt'): datum})
        line = join(join(line, label), datum)
    text = pure(g, '/Script/Engine.KismetTextLibrary.Conv_StringToText', InString=line)
    setter = call(g, '/Script/UMG.TextBlock.SetText', InText=text)
    wire(get(g, 'StatusText'), lib.find_self_pin(setter))
    run(g, flow, setter)
    events = unreal.BlueprintGraphEditor.get_graph_editor_by_name(widget, 'EventGraph')
    event = events.find_event_node('Tick') or lib.add_event_override(widget, 'Tick', unreal.IntPoint(0, 0))
    assert event
    run(events, lib.find_then_pin(event), call(events, 'PC_UpdateStatus'))
    return widget
