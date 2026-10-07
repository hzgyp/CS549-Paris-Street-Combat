"""New-only native pose/rifle crossfade; healthy owner, unchanged clips and transactions."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3];STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadRepairV5'/os.environ['CS549_RELOAD_V5_IDENTITY'];assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(ROOT/'Tools/Integration'))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,call,pure,get,run
ANIM='/Game/ParisCombat/Animation/ReloadRepairV5/ABP_PCReloadOwnerBlendV5'
OWNER='/Game/ParisCombat/Blueprints/ReloadRepairV5/BP_PCReloadOwnerBlendV5'
GUN='/Game/ParisCombat/Blueprints/ReloadRepairV5/BP_PCReloadBlendGunV5'
OLDGUN='/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3'
BASE='/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2'
proof=json.loads((STORE/'Evidence/ReloadRepairV5/transition_proof_fresh_v2/result.json').read_text())
assert not proof['errors'] and proof['status'].startswith('native_crossfade_proof_pass')
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/RELOAD_APPROVED_BINDING_PROOF_INVENTORY_20261004.json').read_text())['files']
for identity in ('blend_capability_v2','transition_proof_author_v2'):
    rows+=json.loads((STORE/'Evidence/ReloadRepairV5'/identity/'result.json').read_text())['packages']
def guard():return all((ROOT/f['path']).stat().st_size==f['size_bytes'] and hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256'] for f in rows)
r={'status':'starting','errors':[],'stages':[],'packages':[],'map_saved':False,'selection':'unselected owner transition trial',
   'open_defects':['RLD-01 index penetration','RLD-02 sleeve stretch/obstruction'],
   'protected_contract':'no finger/mesh/weights/rig/source keys/camera/transaction edits'}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def stage(s):r['stages'].append(s);write();unreal.log('RELOAD_OWNER_BLEND '+s)
def math(g,n,**kw):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**kw)
def branch(g,f,c):
    n=g.add_branch_node();wire(f,lib.find_execute_pin(n));value(pin(n,'Condition'),c);return pin(n,'then',True),pin(n,'else',True)
def put(g,f,n,v,cls='',target=None):
    node=g.add_set_member_variable_node(n,cls)
    if target is not None:wire(target,lib.find_self_pin(node))
    value(pin(node,n),v);return run(g,f,node)
def cast(g,f,obj,cls):
    node=g.create_node_from_name('Utilities|Casting|CastToCharacter',unreal.Vector2D(),[]);assert node
    assert g.retarget_node_class(node,unreal.Character.static_class(),cls)
    wire(obj,pin(node,'Object'));wire(f,lib.find_execute_pin(node))
    outputs=[p for p in lib.list_all_pins(node) if str(pins.get_pin_name(p)).startswith('As')];assert len(outputs)==1
    return lib.find_then_pin(node),outputs[0]
def save(bp,path):
    assert lib.compile_blueprint(bp)
    errors=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()];assert not errors,errors
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    f=STORE/('Content/'+path.removeprefix('/Game/')+'.uasset')
    r['packages'].append({'package':path,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
def duplicate(src,path):
    return unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(path.rsplit('/',1)[1],path.rsplit('/',1)[0],unreal.load_asset(src))
def insert_after(g,node,ops):
    f=lib.find_then_pin(node);ends=list(pins.list_connected_pins(f));assert ends;pins.break_pin_links(f)
    for op in ops:f=run(g,f,op)
    for end in ends:wire(f,end)
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    assert all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in (ANIM,GUN,OWNER))
    basecls=unreal.EditorAssetLibrary.load_blueprint_class(BASE)
    bp=duplicate('/Game/ParisCombat/Animation/ReloadRepairV5/ABP_PCReloadBlendCapabilityV5',ANIM);assert bp
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph');real=lib.get_basic_type_by_name('real')
    for name in ('IdleSeconds','TargetWeight'):assert ev.add_member_variable(name,real,'0')
    assert ev.add_member_variable('WasReloading',lib.get_basic_type_by_name('bool'),'false')
    graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'AnimGraph')
    evaluators=[n for n in graph.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_SequenceEvaluator'];assert len(evaluators)==2
    idle_node=next(n for n in evaluators if 'Rifle_Idle' in n.get_editor_property('node').get_editor_property('sequence').get_path_name())
    wire(get(graph,'IdleSeconds'),pin(idle_node,'ExplicitTime'))
    e=lib.add_event_override(bp,'BlueprintUpdateAnimation',unreal.IntPoint());assert e
    owning=pure(ev,'/Script/Engine.AnimInstance.GetOwningActor')
    combatant=pure(ev,'/Script/Engine.Actor.GetOwner',self=owning)
    f,p=cast(ev,lib.find_then_pin(e),combatant,basecls)
    dt=pin(e,'DeltaTimeX',True)
    idle=unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle')
    mod=call(ev,'/Script/Engine.KismetMathLibrary.FMod',Dividend=math(ev,'Add_DoubleDouble',A=get(ev,'IdleSeconds'),B=dt),Divisor=idle.get_play_length())
    f=put(ev,f,'IdleSeconds',pin(mod,'Remainder',True))
    active=math(ev,'BooleanAND',A=math(ev,'EqualEqual_NameName',A=get(ev,'ActionState',basecls.get_path_name(),p),B='Reloading'),
                B=math(ev,'Not_PreBool',A=get(ev,'IsDead',basecls.get_path_name(),p)))
    yes,no=branch(ev,f,active)
    enter,continuing=branch(ev,yes,math(ev,'Not_PreBool',A=get(ev,'WasReloading')))
    enter=put(ev,enter,'ReloadSeconds',0.)
    for path in (enter,continuing):
        path=put(ev,path,'WasReloading',True);path=put(ev,path,'TargetWeight',1.)
        path=put(ev,path,'ReloadSeconds',math(ev,'FMin',A=math(ev,'Add_DoubleDouble',A=get(ev,'ReloadSeconds'),B=dt),B=4.133333206176758))
        put(ev,path,'ReloadWeight',math(ev,'FInterpTo_Constant',Current=get(ev,'ReloadWeight'),Target=get(ev,'TargetWeight'),DeltaTime=dt,InterpSpeed=4.))
    no=put(ev,no,'WasReloading',False);no=put(ev,no,'TargetWeight',0.)
    put(ev,no,'ReloadWeight',math(ev,'FInterpTo_Constant',Current=get(ev,'ReloadWeight'),Target=get(ev,'TargetWeight'),DeltaTime=dt,InterpSpeed=4.))
    stage('new_animation_simple_native_flow_before_compile');save(bp,ANIM)
    animcls=unreal.EditorAssetLibrary.load_blueprint_class(ANIM);stage('animation_saved')

    parentcls=unreal.EditorAssetLibrary.load_blueprint_class(OLDGUN)
    bp=lib.create_blueprint_asset_with_parent(GUN,parentcls);assert bp
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    struct=lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform'))
    for name in ('LastHeldRelativeT','ReloadRelativeT'):assert ev.add_member_variable(name,struct)
    # Compile declarations only, then reacquire all graph/pins.
    assert lib.compile_blueprint(bp)
    graph=lib.add_function_override(bp,'PC_UpdateRifleAttachment');assert graph
    g=unreal.BlueprintGraphEditor.get_graph_editor(graph)
    parent=next(n for n in g.list_all_nodes() if 'CallParentFunction' in n.get_class().get_name())
    f=lib.find_then_pin(parent)
    instance=pure(g,'/Script/Engine.SkeletalMeshComponent.GetAnimInstance',self=get(g,'GripMesh'))
    f,instance=cast(g,f,instance,animcls)
    weight=get(g,'ReloadWeight',animcls.get_path_name(),instance)
    hand=pure(g,'/Script/Engine.SceneComponent.GetSocketTransform',self=get(g,'GripMesh'),InSocketName='hand_r')
    held,other=branch(g,f,math(g,'LessEqual_DoubleDouble',A=weight,B=0.))
    put(g,held,'LastHeldRelativeT',math(g,'MakeRelativeTransform',A=pure(g,'/Script/Engine.Actor.GetTransform'),RelativeTo=hand))
    relative=math(g,'TLerp',A=get(g,'LastHeldRelativeT'),B=get(g,'ReloadRelativeT'),Alpha=weight)
    run(g,other,call(g,'/Script/Engine.Actor.K2_SetActorTransform',NewTransform=math(g,'ComposeTransforms',A=relative,B=hand),bSweep=False,bTeleport=True))
    assert lib.compile_blueprint(bp)
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(GUN))
    calib=json.loads((STORE/'Evidence/ReloadContactBindingV3/binding_proof_author_v2/result.json').read_text())['audit_phase0_hand_relative']
    transform=unreal.Transform();transform.translation=unreal.Vector(*calib['t']);transform.rotation=unreal.Quat(*calib['q']);transform.scale3d=unreal.Vector(*calib['s'])
    cdo.set_editor_property('ReloadRelativeT',transform)
    save(bp,GUN);stage('gun_saved')

    bp=duplicate('/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCActionOwnerViewV1',OWNER);assert bp
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_InitActionView')
    play=[n for n in g.list_all_nodes() if pins.is_valid(lib.find_input_pin(n,'NewAnimToPlay'))];assert len(play)==1
    insert_after(g,play[0],[call(g,'/Script/Engine.SkeletalMeshComponent.SetAnimInstanceClass',self=get(g,'PoseMesh'),NewClass=animcls.get_path_name())])
    spawns=[lib.find_input_pin(n,'ActorClass') for n in g.list_all_nodes() if pins.is_valid(lib.find_input_pin(n,'ActorClass')) and OLDGUN in pins.get_pin_value(lib.find_input_pin(n,'ActorClass'))];assert len(spawns)==1
    value(spawns[0],unreal.EditorAssetLibrary.load_blueprint_class(GUN).get_path_name())
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateActionViewPose')
    entry=g.find_graph_entry_pin().get_owning_node();g.remove_nodes([n for n in g.list_all_nodes() if n!=entry])
    f=run(g,g.find_graph_entry_pin(),call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=get(g,'SkeletalMeshComponent','/Script/Engine.SkeletalMeshActor'),NewLeaderBoneComponent=get(g,'PoseMesh'),bForceUpdate=False,bInFollowerShouldTickPose=False))
    f,inst=cast(g,f,pure(g,'/Script/Engine.SkeletalMeshComponent.GetAnimInstance',self=get(g,'PoseMesh')),animcls)
    yes,no=branch(g,f,math(g,'Greater_DoubleDouble',A=get(g,'ReloadWeight',animcls.get_path_name(),inst),B=0.))
    put(g,yes,'PoseMode','ReloadBlend');put(g,no,'PoseMode','Holding')
    # Only alter the existing Ready condition. No new framing offset/camera.
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateOwnerDisplay')
    ready=[n for n in g.list_all_nodes() if pins.is_valid(lib.find_input_pin(n,'B')) and pins.get_pin_value(lib.find_input_pin(n,'B'))=='Ready'];assert len(ready)==1
    old=pin(ready[0],'ReturnValue',True);destinations=list(pins.list_connected_pins(old));assert destinations
    pins.break_pin_links(old)
    # PoseMode is written by the preceding native pose update on this actor's tick.
    stable=math(g,'EqualEqual_NameName',A=get(g,'PoseMode'),B='Holding')
    admitted=math(g,'BooleanAND',A=old,B=stable)
    for target in destinations:wire(admitted,target)
    stage('healthy_owner_minimal_blend_patch_before_compile');save(bp,OWNER);stage('owner_saved')
    r['status']='saved_unselected_owner_blend_requires_city_continuity_and_visual_tests'
except Exception:r['status']='failed_stop_owner_blend';r['errors'].append(traceback.format_exc())
finally:r['protected_516_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
