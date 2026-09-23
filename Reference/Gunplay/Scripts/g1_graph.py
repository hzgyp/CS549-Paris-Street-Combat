"""Small checked helpers for editable native Blueprint graphs; no runtime Python."""
import unreal
L=unreal.BlueprintEditorLibrary
A=unreal.EditorAssetLibrary

def ip(n,k):
    p=L.find_input_pin(n,k);assert p.is_valid(),('Missing input',L.get_node_title(n),k);return p
def op(n,k='ReturnValue'):
    p=L.find_output_pin(n,k);assert p.is_valid(),('Missing output',L.get_node_title(n),k);return p
def link(a,b):
    assert a.is_valid() and b.is_valid(),('Invalid connection',str(a),str(b))
    assert a.try_create_connection(b),'Cannot connect '+str(a)+' -> '+str(b)
def value(n,k,v):
    if isinstance(v,unreal.BlueprintGraphPin):link(v,ip(n,k))
    else:assert ip(n,k).set_pin_value(str(v)),(L.get_node_title(n),k,v,[str(p.get_pin_name()) for p in L.list_input_pins(n)])
def call(g,path,**kwargs):
    if path.startswith('math.'):path='/Script/Engine.KismetMathLibrary.'+path[5:]
    elif path.startswith('system.'):path='/Script/Engine.KismetSystemLibrary.'+path[7:]
    elif path.startswith('game.'):path='/Script/Engine.GameplayStatics.'+path[5:]
    n=g.add_call_function_node(path);assert n,path
    # Promotable math nodes resolve numeric types from connected pins first.
    for k,v in sorted(kwargs.items(),key=lambda item:not isinstance(item[1],unreal.BlueprintGraphPin)):value(n,k,v)
    return n
def pure(g,path,**kwargs):return op(call(g,path,**kwargs))
def get(g,name,cls='',target=None):
    n=g.add_get_member_variable_node(name,cls);assert n,name
    if target is not None:value(n,'self',target)
    return op(n,name)
def setv(g,name,v,cls='',target=None):
    n=g.add_set_member_variable_node(name,cls);assert n,name;value(n,name,v)
    if target is not None:value(n,'self',target)
    return n
def chain(start,*nodes):
    for i,n in enumerate(nodes):
        link(start,ip(n,'execute'));start=L.find_output_pin(n,'then')
        assert start.is_valid() or i==len(nodes)-1,('Missing continuation',L.get_node_title(n))
    return start
def branch(g,start,condition):
    n=g.add_branch_node();value(n,'Condition',condition);link(start,ip(n,'execute'));return op(n,'then'),op(n,'else')
def function(bp,name):
    for existing in L.list_graph_names(bp):
        existing=str(existing)
        if existing==name or (existing.startswith(name+'_') and existing[len(name)+1:].isdigit()):L.remove_function_graph(bp,existing)
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,name)
    if g.get_graph().get_name()!=name:L.rename_graph(g.get_graph(),name)
    return g
def member(g,bp,name,kind,default=''):
    if name in [str(v) for v in L.list_member_variable_names(bp)]:return
    if isinstance(kind,str):kind=L.get_basic_type_by_name(kind)
    assert g.add_member_variable(name,kind,default),name
def param(g,name,kind):return g.add_graph_input_parameter(name,L.get_basic_type_by_name(kind) if isinstance(kind,str) else kind)
def compile_save(bp):
    assert L.compile_blueprint(bp),bp.get_name()
    assert A.save_loaded_asset(bp,only_if_is_dirty=False)
def cls_path(bp):return bp.get_path_name()+'_C'
def object_type(cls):return L.get_object_reference_type(cls)
def eq(g,a,b):return pure(g,'math.EqualEqual_IntInt',A=a,B=b)
def both(g,a,b):return pure(g,'math.BooleanAND',A=a,B=b)
def invert(g,a):return pure(g,'math.Not_PreBool',A=a)
def log(g,msg):return call(g,'system.PrintString',InString=msg,bPrintToScreen='false',bPrintToLog='true')
def tidy(g):
    # Place sequential nodes in readable rows; manual editorial layout can follow integration.
    for i,n in enumerate(g.list_all_nodes()):n.set_node_pos(unreal.IntPoint((i%8)*320,(i//8)*230))
