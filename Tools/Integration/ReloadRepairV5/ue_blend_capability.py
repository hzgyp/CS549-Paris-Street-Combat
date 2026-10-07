"""New-only minimal AnimGraph capability proof. No owner, map, rig or source action edits."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
IDENTITY=os.environ['CS549_RELOAD_V5_IDENTITY']
OUT=STORE/'Evidence/ReloadRepairV5'/IDENTITY
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
sys.path.insert(0,str(ROOT/'Tools/Integration'))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,get
DEST='/Game/ParisCombat/Animation/ReloadRepairV5/ABP_PCReloadBlendCapabilityV5'
IDLE='/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle'
RELOAD='/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1'
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())['files']
r={'status':'starting','errors':[],'stages':[],'packages':[],'native_map_saved':False,
   'selection':'unselected diagnostic input/graph only; not visual repair acceptance'}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
def stage(s):r['stages'].append(s);write();unreal.log('RELOAD_BLEND_CAPABILITY '+s)
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in rows)
def describe(n):
    return {'name':n.get_name(),'class':n.get_class().get_path_name(),
            'pins':[{'name':str(pins.get_pin_name(p)), 'value':pins.get_pin_value(p)} for p in lib.list_all_pins(n)]}
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
    mesh=unreal.load_asset('/Game/ParisCombat/Characters/Adaptation/Meshes/SK_WWII_US_Paratrooper_simple_UE582_v1')
    idle,reload=unreal.load_asset(IDLE),unreal.load_asset(RELOAD)
    assert idle and reload and mesh
    factory=unreal.AnimBlueprintFactory()
    factory.set_editor_property('target_skeleton',mesh.get_editor_property('skeleton'))
    factory.set_editor_property('preview_skeletal_mesh',mesh)
    factory.set_editor_property('parent_class',unreal.AnimInstance.static_class())
    bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(DEST.rsplit('/',1)[1],DEST.rsplit('/',1)[0],unreal.AnimBlueprint,factory)
    assert bp;stage('new_anim_blueprint_created_unsaved')
    graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'AnimGraph');assert graph
    event=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    assert event.add_member_variable('ReloadWeight',lib.get_basic_type_by_name('real'),'0')
    assert event.add_member_variable('ReloadSeconds',lib.get_basic_type_by_name('real'),'4.1333332062')
    available=list(graph.list_available_nodes([]))
    r['available_filtered']=[str(n) for n in available if any(s.lower() in str(n).lower() for s in ('TwoWay','Two Way','Rifle_Idle','AS_PC_D059','SequenceEvaluator','Sequence Evaluator'))]
    stage('exact_menu_capabilities_recorded')
    def choose(token):
        found=[str(n) for n in available if token.lower().replace(' ','') in str(n).lower().replace(' ','')]
        assert len(found)==1,(token,found)
        return found[0]
    blend=graph.create_node_from_name(choose('TwoWayBlend'),unreal.Vector2D(0,0),[]);assert blend
    # Generic evaluators avoid duplicated asset-menu labels for different skeletons.
    evaluator='Animation|Sequences|SequenceEvaluator'
    assert evaluator in available
    a=graph.create_node_from_name(evaluator,unreal.Vector2D(-400,-200),[]);assert a
    b=graph.create_node_from_name(evaluator,unreal.Vector2D(-400,200),[]);assert b
    for n,asset in ((a,idle),(b,reload)):
        data=n.get_editor_property('node')
        data.set_editor_property('sequence',asset)
        data.set_editor_property('should_loop',False)
        n.set_editor_property('node',data)
    roots=[n for n in graph.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_Root'];assert len(roots)==1
    r['nodes_before_wiring']=[describe(n) for n in (a,b,blend,roots[0])];stage('four_native_nodes_created')
    wire(pin(a,'Pose',True),pin(blend,'A'))
    wire(pin(b,'Pose',True),pin(blend,'B'))
    wire(get(graph,'ReloadWeight'),pin(blend,'Alpha'))
    wire(get(graph,'ReloadSeconds'),pin(b,'ExplicitTime'))
    wire(pin(blend,'Pose',True),pin(roots[0],'Result'))
    stage('minimal_two_source_graph_wired_before_compile')
    assert lib.compile_blueprint(bp)
    # Compile invalidates graph/pin handles. Reacquire only.
    graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'AnimGraph')
    r['graph_errors']=[str(n) for n in graph.list_nodes_with_errors()];assert not r['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    f=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    r['packages']=[{'package':DEST,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}]
    r['status']='saved_minimal_blend_requires_fresh_native_pose_check';stage('new_only_minimal_blend_saved')
except Exception:
    r['status']='failed_capability_preserve_stop';r['errors'].append(traceback.format_exc())
finally:
    r['protected_514_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
