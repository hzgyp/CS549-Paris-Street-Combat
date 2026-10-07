"""Lane-B-only K2 author helpers. Import has no asset-writing side effects."""
import sys
from pathlib import Path
import unreal
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ue_paris_graph_helpers import lib, pins, pin, wire, value, get, run, place


def call(g, name, **kw):
    unreal.log("NPC_GRAPH_CALL_BEGIN " + name)
    node = place(g.add_call_function_node(name))
    unreal.log("NPC_GRAPH_NODE_CREATED " + name)
    for key, datum in kw.items():
        unreal.log("NPC_GRAPH_PIN_BEGIN " + name + ":" + key)
        value(pin(node, key), datum)
        unreal.log("NPC_GRAPH_PIN_END " + name + ":" + key)
    unreal.log("NPC_GRAPH_CALL_END " + name)
    return node


def pure(g, name, **kw):
    return pin(call(g, name, **kw), "ReturnValue", True)


def math(g, function, **kw):
    return pure(g, "/Script/Engine.KismetMathLibrary." + function, **kw)


def branch(g, flow, condition):
    node = g.add_branch_node()
    wire(flow, lib.find_execute_pin(node))
    value(pin(node, "Condition"), condition)
    return pin(node, "then", True), pin(node, "else", True)


def put(g, flow, name, datum, target=None, cls=""):
    unreal.log("NPC_GRAPH_PUT " + name)
    node = g.add_set_member_variable_node(name, cls)
    value(pin(node, name), datum)
    if target is not None:
        wire(target, lib.find_self_pin(node))
    return run(g, flow, node)


def bbget(g, name, kind):
    return pure(g, "/Script/AIModule.BlackboardComponent.GetValueAs" + kind,
                self=get(g, "NPCBlackboard"), KeyName=pure(g, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value=name))


def bbput(g, flow, name, kind, datum):
    field = {"Bool": "BoolValue", "Int": "IntValue", "Name": "NameValue", "Vector": "VectorValue", "Float": "FloatValue"}[kind]
    return run(g, flow, call(g, "/Script/AIModule.BlackboardComponent.SetValueAs" + kind,
                self=get(g, "NPCBlackboard"), KeyName=pure(g, "/Script/Engine.KismetSystemLibrary.MakeLiteralName", Value=name), **{field: datum}))


def function(bp, name, parameters=()):
    unreal.log("NPC_GRAPH_FUNCTION_BEGIN " + name)
    g = unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp, name)
    unreal.log("NPC_GRAPH_FUNCTION_CREATED " + name)
    g.set_function_is_public()
    unreal.log("NPC_GRAPH_FUNCTION_PUBLIC " + name)
    values = []
    for param, kind in parameters:
        typ = lib.get_struct_type(unreal.load_object(None, "/Script/CoreUObject.Vector")) if kind == "Vector" else lib.get_basic_type_by_name(kind)
        values.append(g.add_graph_input_parameter(param, typ))
    return g, g.find_graph_entry_pin(), values


def invoke(g, flow, name, **kw):
    return run(g, flow, call(g, name, **kw))


def distance(g, a, b):
    # Direct fixed-signature function avoids the failing promoted subtraction.
    return math(g, "Vector_Distance", V1=a, V2=b)


def cast(g, flow, obj, cls):
    types = [n for n in g.list_available_nodes([]) if n.replace(" ", "").lower() == "utilities|casting|casttoactor"]
    node = g.create_node_from_name(types[0], unreal.Vector2D(), [])
    assert g.retarget_node_class(node, unreal.Actor.static_class(), cls)
    value(pin(node, "Object"), obj)
    wire(flow, lib.find_execute_pin(node))
    out = [p for p in lib.list_all_pins(node) if str(pins.get_pin_name(p)).startswith("As")]
    return lib.find_then_pin(node), out[0]
