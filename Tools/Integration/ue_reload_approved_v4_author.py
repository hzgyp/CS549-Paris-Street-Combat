"""Two unselected native binding proof fixtures. Not a retarget or recoil author."""
import hashlib,json,os,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadContactBindingV3'/os.environ['CS549_APPROVED_IDENTITY']
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
sys.path.insert(0,str(Path(__file__).parent))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,call,pure,get,run
GUN='/Game/ParisCombat/Blueprints/WeaponAttachmentV3/BP_PC_RifleAttachmentV3'
OWNER='/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCActionOwnerViewV1'
NEWGUN='/Game/ParisCombat/Blueprints/ReloadApprovedV4/BP_PCReloadGunProofV4'
NEWOWNER='/Game/ParisCombat/Blueprints/ReloadApprovedV4/BP_PCReloadOwnerProofV4'
CLIP='/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1'
rows=json.loads((ROOT/'tmp/weapon-animation-reuse/preflight_v1.json').read_text())['files']
rows+=json.loads((ROOT/'Assets/Integration/WEAPON_ANIMATION_REUSE_DRAFT_INVENTORY_20261004.json').read_text())['files']
r={'status':'starting','errors':[],'packages':[],'map_saved':False,'selection':'proof_only_unselected',
   'source_motion':'/Game/Rifle_01/Animation/In-Place/W2_Stand_Aim_Reload_IP','diagnostic_derivative':CLIP,'stages':[]}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def stage(s):r['stages'].append(s);write();unreal.log('RELOAD_V4_PROOF '+s)
def guard():return all((ROOT/e['path']).stat().st_size==e['size_bytes'] and hashlib.sha256((ROOT/e['path']).read_bytes()).hexdigest()==e['sha256'] for e in rows)
def tr(t):return {'t':[t.translation.x,t.translation.y,t.translation.z],'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':[t.scale3d.x,t.scale3d.y,t.scale3d.z]}
def unpack(v):
    t=unreal.Transform();t.translation=unreal.Vector(*v['translation']);t.rotation=unreal.Quat(*v['rotation']);t.scale3d=unreal.Vector(*v['scale']);return t
def math(g,n,**kw):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**kw)
def branch(g,f,c):
    n=g.add_branch_node();wire(f,lib.find_execute_pin(n));value(pin(n,'Condition'),c);return pin(n,'then',True),pin(n,'else',True)
def save(bp,p):
    assert lib.compile_blueprint(bp)
    errors=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
    assert not errors,errors
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    f=STORE/('Content/'+p.removeprefix('/Game/')+'.uasset')
    r['packages'].append({'package':p,'path':f.relative_to(ROOT).as_posix(),'size_bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
def insert_after(g,node,operations):
    f=lib.find_then_pin(node);dest=list(pins.list_connected_pins(f));assert dest
    pins.break_pin_links(f)
    for op in operations:f=run(g,f,op)
    for d in dest:wire(f,d)
try:
    assert guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    assert not unreal.EditorAssetLibrary.does_asset_exist(NEWGUN)
    assert not unreal.EditorAssetLibrary.does_asset_exist(NEWOWNER)
    audit=json.loads((STORE/'Evidence/ReloadSleeveAdaptationV2/bone_audit_v1/result.json').read_text());assert not audit['errors']
    model=audit['models']['allied'];raw=audit['clips']['failed']['samples']['0'];component={}
    def bone(n):
        if n not in component:
            local=unpack(raw.get(n,model['ref_local'][n]));parent=model['parents'][n]
            component[n]=unreal.MathLibrary.compose_transforms(local,bone(parent)) if parent in model['parents'] else local
        return component[n]
    def hollow(side):
        digits=('middle','ring','pinky','thumb') if side=='r' else ('index','middle','ring','pinky','thumb')
        return sum((bone(d+'_0'+str(i)+'_'+side).translation for d in digits for i in (2,3)),unreal.Vector())/(len(digits)*2)
    right,left=hollow('r'),hollow('l');look=unreal.MathLibrary.find_look_at_rotation(right,left)
    ori=unreal.Transform(rotation=unreal.Rotator(pitch=0,yaw=look.yaw-90,roll=-look.pitch))
    candidate=unreal.Transform();candidate.translation=right-unreal.MathLibrary.transform_location(ori,unreal.Vector(-.5,-8,0));candidate.rotation=ori.rotation;candidate.scale3d=unreal.Vector(1,1,1)
    relative=unreal.MathLibrary.make_relative_transform(candidate,bone('hand_r'))
    r['audit_phase0_hand_relative']=tr(relative);stage('audit_calibration_ready')
    cls=unreal.EditorAssetLibrary.load_blueprint_class(GUN)
    bp=lib.create_blueprint_asset_with_parent(NEWGUN,cls);assert bp
    ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    assert ev.add_member_variable('ReloadHandRelativeT',lib.get_struct_type(unreal.load_object(None,'/Script/CoreUObject.Transform')))
    assert lib.compile_blueprint(bp);stage('gun_member_compiled')
    graph=lib.add_function_override(bp,'PC_UpdateRifleAttachment');assert graph
    g=unreal.BlueprintGraphEditor.get_graph_editor(graph);entry=g.find_graph_entry_pin()
    parent=next(n for n in g.list_all_nodes() if 'CallParentFunction' in n.get_class().get_name())
    pins.break_pin_links(entry)
    p=get(g,'Combatant');s=get(g,'GripMesh')
    valid=math(g,'BooleanAND',A=pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=p),B=pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=s))
    f,no=branch(g,entry,valid);wire(no,lib.find_execute_pin(parent))
    actorcls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2')
    f,no=branch(g,f,math(g,'EqualEqual_NameName',A=get(g,'ActionState',actorcls.get_path_name(),p),B='Reloading'))
    wire(no,lib.find_execute_pin(parent))
    t=math(g,'ComposeTransforms',A=get(g,'ReloadHandRelativeT'),B=pure(g,'/Script/Engine.SceneComponent.GetSocketTransform',self=s,InSocketName='hand_r'))
    run(g,f,call(g,'/Script/Engine.Actor.K2_SetActorTransform',NewTransform=t,bSweep=False,bTeleport=True))
    assert lib.compile_blueprint(bp)
    unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(NEWGUN)).set_editor_property('ReloadHandRelativeT',relative)
    save(bp,NEWGUN);stage('gun_saved_unselected')
    # Existing linear function only; no new chooser or cross-compile pin reuse.
    bp=unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(NEWOWNER.rsplit('/',1)[1],NEWOWNER.rsplit('/',1)[0],unreal.load_asset(OWNER));assert bp
    g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateActionViewPose')
    leaders=[];holding=[]
    for n in g.list_all_nodes():
        q=lib.find_input_pin(n,'NewLeaderBoneComponent')
        if pins.is_valid(q) and pins.list_connected_pins(q):leaders.append(n)
        q=lib.find_input_pin(n,'NewAnimToPlay')
        if pins.is_valid(q) and 'Rifle_Idle' in pins.get_pin_value(q):holding.append(n)
    assert len(leaders)==1 and len(holding)==1,(len(leaders),len(holding))
    pins.break_pin_links(pin(leaders[0],'NewLeaderBoneComponent'))
    s=get(g,'PoseMesh');v=get(g,'SkeletalMeshComponent','/Script/Engine.SkeletalMeshActor')
    insert_after(g,leaders[0],[call(g,'/Script/Engine.SkeletalMeshComponent.PlayAnimation',self=s,NewAnimToPlay=CLIP+'.'+CLIP.rsplit('/',1)[1],bLooping=False),
        call(g,'/Script/Engine.SkeletalMeshComponent.SetPlayRate',self=s,Rate=1.),
        call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=v,NewLeaderBoneComponent=s,bForceUpdate=True,bInFollowerShouldTickPose=False)])
    insert_after(g,holding[0],[call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=v,NewLeaderBoneComponent=s,bForceUpdate=True,bInFollowerShouldTickPose=False)])
    init=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_InitActionView');spawns=[]
    for n in init.list_all_nodes():
        q=lib.find_input_pin(n,'ActorClass')
        if pins.is_valid(q) and GUN in pins.get_pin_value(q):spawns.append(q)
    assert len(spawns)==1,len(spawns)
    value(spawns[0],unreal.EditorAssetLibrary.load_blueprint_class(NEWGUN).get_path_name())
    stage('owner_minimal_patch_complete_before_compile')
    save(bp,NEWOWNER);stage('owner_saved_unselected')
    r['status']='saved_unselected_binding_proof_requires_actual_target_visual_gate'
except Exception:r['errors'].append(traceback.format_exc());r['status']='failed_preserve_proof'
finally:
    r['protected_512_unchanged']=guard();write();unreal.SystemLibrary.quit_editor()
