"""New-only native temporal blend proof; no gameplay transaction or owner binding."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_V5_IDENTITY'];assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(ROOT/'Tools/Integration'))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,call,pure,get,run
SRC='/Game/ParisCombat/Animation/ReloadRepairV5/ABP_PCReloadBlendCapabilityV5'
DEST='/Game/ParisCombat/Animation/ReloadRepairV5/ABP_PCReloadTransitionProofV5'
base=json.loads((STORE/'Evidence/ReloadRepairV5/blend_capability_v2/result.json').read_text());assert not base['errors']
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())['files']+base['packages']
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in rows)
r={'status':'starting','errors':[],'packages':[],'stages':[],'map_saved':False,'selection':'unselected temporal blend diagnostic'}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def stage(s):r['stages'].append(s);write();unreal.log('RELOAD_TRANSITION_PROOF '+s)
def put(g,f,n,v):
    node=g.add_set_member_variable_node(n);value(pin(node,n),v);return run(g,f,node)
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
    bp=unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(DEST.rsplit('/',1)[1],DEST.rsplit('/',1)[0],unreal.load_asset(SRC));assert bp
    event=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    real=lib.get_basic_type_by_name('real')
    assert event.add_member_variable('TargetWeight',real,'1')
    assert lib.set_blueprint_variable_instance_editable(bp,'ReloadWeight',True) is not False
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_SetTransitionTarget')
    target=g.add_graph_input_parameter('Target',real)
    put(g,g.find_graph_entry_pin(),'TargetWeight',target)
    node=lib.add_event_override(bp,'BlueprintUpdateAnimation',unreal.IntPoint());assert node
    weight=pure(event,'/Script/Engine.KismetMathLibrary.FInterpTo_Constant',Current=get(event,'ReloadWeight'),
                Target=get(event,'TargetWeight'),DeltaTime=pin(node,'DeltaTimeX',True),InterpSpeed=4.)
    put(event,lib.find_then_pin(node),'ReloadWeight',weight)
    stage('minimal_native_temporal_graph_complete_before_compile')
    assert lib.compile_blueprint(bp)
    r['graph_errors']=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()];assert not r['graph_errors']
    cls=unreal.EditorAssetLibrary.load_blueprint_class(DEST);cdo=unreal.get_default_object(cls)
    cdo.set_editor_property('ReloadWeight',1.)
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    f=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    r['packages']=[{'package':DEST,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}]
    r['status']='saved_unselected_native_temporal_proof_requires_fresh_run';stage('new_temporal_proof_saved')
except Exception:r['status']='failed_stop_temporal_proof';r['errors'].append(traceback.format_exc())
finally:r['protected_515_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
