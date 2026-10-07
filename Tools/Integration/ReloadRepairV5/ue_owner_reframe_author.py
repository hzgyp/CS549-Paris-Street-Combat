"""AN004 replacement: continuous camera-local frame blending, new owner only."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_V5_IDENTITY'];assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(ROOT/'Tools/Integration'))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,call,pure,get,run
SRC='/Game/ParisCombat/Blueprints/ReloadRepairV5/BP_PCReloadOwnerBlendV5'
DEST='/Game/ParisCombat/Blueprints/ReloadRepairV5/BP_PCReloadOwnerReframeV5'
ANIM='/Game/ParisCombat/Animation/ReloadRepairV5/ABP_PCReloadOwnerBlendV5'
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())['files']
for identity in ('blend_capability_v2','transition_proof_author_v2','owner_blend_author_v1'):
    rows+=json.loads((STORE/'Evidence/ReloadRepairV5'/identity/'result.json').read_text())['packages']
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in rows)
r={'status':'starting','errors':[],'packages':[],'stages':[],'owner_package':DEST,'map_saved':False,
   'selection':'new unselected frame-blend trial; AN004 old owner stopped',
   'open_defects':['RLD-01','RLD-02']}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def stage(s):r['stages'].append(s);write();unreal.log('RELOAD_REFRAME '+s)
def math(g,n,**kw):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**kw)
def put(g,f,n,v):
    node=g.add_set_member_variable_node(n);value(pin(node,n),v);return run(g,f,node)
def branch(g,f,c):
    n=g.add_branch_node();wire(f,lib.find_execute_pin(n));value(pin(n,'Condition'),c);return pin(n,'then',True),pin(n,'else',True)
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
    bp=unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(DEST.rsplit('/',1)[1],DEST.rsplit('/',1)[0],unreal.load_asset(SRC));assert bp
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    assert ev.add_member_variable('ViewReloadWeight',lib.get_basic_type_by_name('real'),'0')
    assert ev.add_member_variable('ReturnStartFramingT',lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform')))
    assert lib.compile_blueprint(bp)
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateActionViewPose')
    casts=[n for n in g.list_all_nodes() if 'DynamicCast' in n.get_class().get_name()];assert len(casts)==1
    cast=casts[0];objects=[p for p in lib.list_all_pins(cast) if str(pins.get_pin_name(p)).startswith('As')];assert len(objects)==1
    f=lib.find_then_pin(cast);ends=list(pins.list_connected_pins(f));assert ends;pins.break_pin_links(f)
    animcls=unreal.EditorAssetLibrary.load_blueprint_class(ANIM)
    f=put(g,f,'ViewReloadWeight',get(g,'ReloadWeight',animcls.get_path_name(),objects[0]))
    for end in ends:wire(f,end)
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateOwnerDisplay')
    ready=[n for n in g.list_all_nodes() if pins.is_valid(lib.find_input_pin(n,'B')) and pins.get_pin_value(lib.find_input_pin(n,'B'))=='Ready'];assert len(ready)==1
    readyout=pin(ready[0],'ReturnValue',True)
    connected=list(pins.list_connected_pins(readyout));assert len(connected)==1
    old_and=connected[0].get_owning_node();andout=pin(old_and,'ReturnValue',True)
    clients=list(pins.list_connected_pins(andout));assert clients;pins.break_pin_links(andout)
    for client in clients:wire(readyout,client)
    setters=[n for n in g.list_all_nodes() if pins.is_valid(lib.find_input_pin(n,'FramingT'))];assert len(setters)==1
    setter=setters[0];f=lib.find_then_pin(setter);ends=list(pins.list_connected_pins(f));assert ends;pins.break_pin_links(f)
    stable,settling=branch(g,f,math(g,'LessEqual_DoubleDouble',A=get(g,'ViewReloadWeight'),B=0.))
    stable=put(g,stable,'ReturnStartFramingT',get(g,'FramingT'))
    # Connect the typed operand first: promoted math nodes start with wildcard pins.
    inverse_weight=math(g,'Subtract_DoubleDouble',B=get(g,'ViewReloadWeight'),A=1.)
    settling=put(g,settling,'FramingT',math(g,'TLerp',A=get(g,'ReturnStartFramingT'),B=get(g,'FramingT'),Alpha=inverse_weight))
    settling=put(g,settling,'ViewT',math(g,'ComposeTransforms',A=get(g,'FramingT'),B=get(g,'CameraT')))
    relative=math(g,'MakeRelativeTransform',A=pure(g,'/Script/Engine.Actor.GetTransform',self=get(g,'WorldGun')),
                  RelativeTo=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentToWorld',self=get(g,'SourceMesh')))
    settling=put(g,settling,'FitGunT',math(g,'ComposeTransforms',A=relative,B=get(g,'ViewT')))
    for f in (stable,settling):
        for end in ends:wire(f,end)
    stage('continuous_frame_new_owner_patch_before_compile')
    assert lib.compile_blueprint(bp)
    r['graph_errors']=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()];assert not r['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    f=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    r['packages']=[{'package':DEST,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}]
    r['status']='saved_unselected_continuous_frame_owner_requires_actual_city_test';stage('new_owner_saved_old_owner_unchanged')
except Exception:r['status']='failed_stop_reframe';r['errors'].append(traceback.format_exc())
finally:r['protected_519_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
