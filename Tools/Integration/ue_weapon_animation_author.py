"""New Blueprint bindings only; existing reload transaction and clips preserved."""
import json
import os
import sys
import traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from weapon_animation_reuse_common import ROOT, STORE, PLAYER, OWNER, RELOAD, SHOOT, output, guard, record, read
from ue_paris_graph_helpers import lib, pins, pin, wire, value, call, pure, get, run
OUT = output(os.environ['CS549_ANIMATION_IDENTITY'])
STAGE = os.environ.get('CS549_ANIMATION_AUTHOR_STAGE','reload')
r = {'status':'authoring','errors':[],'packages':[],'stage':STAGE,'map_saved':False}
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())


def math(g,n,**kw):
    return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**kw)


def branch(g,f,c):
    n=g.add_branch_node(); wire(f,lib.find_execute_pin(n));value(pin(n,'Condition'),c)
    return pin(n,'then',True),pin(n,'else',True)


def put(g,f,n,v):
    node=g.add_set_member_variable_node(n); value(pin(node,n),v)
    return run(g,f,node)


def ands(g,vals):
    out=vals[0]
    for v in vals[1:]: out=math(g,'BooleanAND',A=out,B=v)
    return out


def save(bp,path):
    assert lib.compile_blueprint(bp)
    errors=[str(n) for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
    assert not errors, errors
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['packages'].append(record(path))


try:
    guard();assert not hasattr(unreal,'ParisBlueprintAuthoring')
    motion=read(STORE/'Evidence/WeaponAnimationReuseV1/retarget_v1/result.json')
    assert not motion['errors'] and motion['finger_local_max_delta']<.002
    if STAGE=='reload':
        assert not unreal.EditorAssetLibrary.does_asset_exist(PLAYER)
        bp=lib.create_blueprint_asset_with_parent(PLAYER,unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCParisPlayerActionsV6'))
        assert bp
        graph=lib.add_function_override(bp,'PC_RequestReload');assert graph
        g=unreal.BlueprintGraphEditor.get_graph_editor(graph)
        entry=g.find_graph_entry_pin(); assert pins.is_valid(entry)
        g.remove_nodes([n for n in g.list_all_nodes() if n!=entry.get_owning_node()])
        # Same request guards/tokens as the inherited transaction. No CallParent
        # here: the rejected old clip never starts on the candidate.
        legal=ands(g,[math(g,'Not_PreBool',A=get(g,'IsDead')),
            math(g,'EqualEqual_NameName',A=get(g,'ActionState'),B='Ready'),
            math(g,'Greater_IntInt',A=get(g,'Capacity'),B=0),
            math(g,'GreaterEqual_IntInt',A=get(g,'LoadedAmmo'),B=0),
            math(g,'Less_IntInt',A=get(g,'LoadedAmmo'),B=get(g,'Capacity')),
            math(g,'Greater_IntInt',A=get(g,'ReserveAmmo'),B=0),
            math(g,'Greater_DoubleDouble',A=get(g,'ReloadPlayRate'),B=0),
            math(g,'EqualEqual_DoubleDouble',A=math(g,'Subtract_DoubleDouble',A=get(g,'ReloadPlayRate'),B=get(g,'ReloadPlayRate')),B=0)])
        f,_=branch(g,entry,legal)
        f=put(g,f,'ActionID',math(g,'Add_IntInt',A=get(g,'ActionID'),B=1))
        for n,v in [('ReloadActionID',get(g,'ActionID')),('ReloadGeneration',get(g,'RestoreGeneration')),
            ('ActionState','Reloading'),('ReloadCommitted',False),('ReloadElapsed',0)]: f=put(g,f,n,v)
        mesh=get(g,'Mesh','/Script/Engine.Character')
        f=run(g,f,call(g,'/Script/Engine.SkeletalMeshComponent.PlayAnimation',self=mesh,NewAnimToPlay=RELOAD+'.'+RELOAD.rsplit('/',1)[1],bLooping=False))
        f=run(g,f,call(g,'/Script/Engine.SkeletalMeshComponent.SetPlayRate',self=mesh,Rate=get(g,'ReloadPlayRate')))
        run(g,f,call(g,'/Script/Engine.SkeletalMeshComponent.SetPosition',self=mesh,InPos=0,bFireNotifies=False))
        assert lib.compile_blueprint(bp)
        cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(PLAYER))
        cdo.set_editor_property('ReloadDuration',motion['duration'])
        # Conservative generic-action completion, not simulated mechanical insertion.
        # Final target review must validate or reject this proposal before selection.
        cdo.set_editor_property('ReloadCommitTime',3.95)
        cdo.set_editor_property('ReloadPlayRate',1.0)
        save(bp,PLAYER)
        r['reload_binding']=RELOAD;r['commit_s']=3.95;r['duration_s']=motion['duration']
        r['old_reload_executable_binding_removed']=True
        r['status']='saved_unselected_reload_binding_requires_target_visual_gate'
    elif STAGE=='owner':
        assert not unreal.EditorAssetLibrary.does_asset_exist(OWNER)
        src=unreal.load_asset('/Game/ParisCombat/Blueprints/PlayerActionsV1/BP_PCActionOwnerViewV1')
        bp=unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(OWNER.rsplit('/',1)[1],OWNER.rsplit('/',1)[0],src);assert bp
        ev=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
        for n,t,d in [('RecoilActive','bool','false'),('SeenShot','int','0'),('SeenLife','int','0')]:
            assert ev.add_member_variable(n,lib.get_basic_type_by_name(t),d)
        assert lib.compile_blueprint(bp)
        # Compile complete helpers in dependency order. A Blueprint compilation
        # can reconstruct pins; never retain pin handles across a compile.
        pc=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1').get_path_name()
        g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_ReturnReusedHolding')
        f,_=branch(g,g.find_graph_entry_pin(),math(g,'NotEqual_NameName',A=get(g,'PoseMode'),B='Holding'))
        s=get(g,'PoseMesh')
        f=run(g,f,call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=s,bForceUpdate=True,bInFollowerShouldTickPose=False))
        f=run(g,f,call(g,'/Script/Engine.SkeletalMeshComponent.PlayAnimation',self=s,NewAnimToPlay='/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle.Rifle_Idle',bLooping=True))
        put(g,f,'PoseMode','Holding')
        assert lib.compile_blueprint(bp)
        unreal.log('REUSE_OWNER_V2 holding helper compiled; discard handles')
        g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_ChooseReusedActionPose')
        entry=g.find_graph_entry_pin();p=get(g,'Combatant');s=get(g,'PoseMesh')
        seq=get(g,'ShotSequence',pc,p)
        reload,ready=branch(g,entry,math(g,'EqualEqual_NameName',A=get(g,'ActionState',pc,p),B='Reloading'))
        reload=put(g,reload,'SeenShot',seq);reload=put(g,reload,'RecoilActive',False)
        reload,_=branch(g,reload,math(g,'NotEqual_NameName',A=get(g,'PoseMode'),B='Reloading'))
        reload=run(g,reload,call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=s,NewLeaderBoneComponent=get(g,'BodySource'),bForceUpdate=True,bInFollowerShouldTickPose=False))
        put(g,reload,'PoseMode','Reloading')
        ready,_=branch(g,ready,math(g,'EqualEqual_NameName',A=get(g,'ActionState',pc,p),B='Ready'))
        fire,no_fire=branch(g,ready,math(g,'Greater_IntInt',A=seq,B=get(g,'SeenShot')))
        fire=put(g,fire,'SeenShot',seq);fire=put(g,fire,'RecoilActive',True);fire=put(g,fire,'PoseMode','Recoil')
        fire=run(g,fire,call(g,'/Script/Engine.SkinnedMeshComponent.SetLeaderPoseComponent',self=s,bForceUpdate=True,bInFollowerShouldTickPose=False))
        run(g,fire,call(g,'/Script/Engine.SkeletalMeshComponent.PlayAnimation',self=s,NewAnimToPlay=SHOOT+'.Rifle_ShootOnce',bLooping=False))
        active,idle=branch(g,no_fire,get(g,'RecoilActive'))
        done,_=branch(g,active,math(g,'GreaterEqual_DoubleDouble',A=pure(g,'/Script/Engine.SkeletalMeshComponent.GetPosition',self=s),B=.799))
        done=put(g,done,'RecoilActive',False)
        for path in (done,idle):run(g,path,call(g,'PC_ReturnReusedHolding'))
        assert lib.compile_blueprint(bp)
        unreal.log('REUSE_OWNER_V2 chooser compiled; discard handles')
        g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateActionViewPose')
        entry=g.find_graph_entry_pin();g.remove_nodes([n for n in g.list_all_nodes() if n!=entry.get_owning_node()])
        p=get(g,'Combatant');seq=get(g,'ShotSequence',pc,p);life=get(g,'RestoreGeneration',pc,p)
        reset,normal=branch(g,entry,math(g,'NotEqual_IntInt',A=get(g,'SeenLife'),B=life))
        reset=put(g,reset,'SeenLife',life)
        # ResetLifecycle preserves ShotSequence. Keep an unseen accepted shot
        # if firing occurs in the same frame as reset; clamp only a rolled-back
        # sequence so subsequent real shots can be observed.
        reset=put(g,reset,'SeenShot',math(g,'Min',A=get(g,'SeenShot'),B=seq))
        reset=put(g,reset,'RecoilActive',False)
        for path in (reset,normal):run(g,path,call(g,'PC_ChooseReusedActionPose'))
        # Ready fitting otherwise numerically erases source wrist recoil. Retain
        # prior holding FramingT through recoil, exactly as through reload.
        g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateOwnerDisplay')
        matches=[]
        for node in g.list_all_nodes():
            b=lib.find_input_pin(node,'B')
            if pins.is_valid(b) and pins.get_pin_value(b)=='Ready':matches.append(node)
        assert len(matches)==1, matches
        old=pin(matches[0],'ReturnValue',True);destinations=list(pins.list_connected_pins(old));assert destinations
        pins.break_pin_links(old)
        augmented=math(g,'BooleanAND',A=old,B=math(g,'Not_PreBool',A=get(g,'RecoilActive')))
        for p in destinations:wire(augmented,p)
        save(bp,OWNER)
        r['shoot_binding']=SHOOT;r['camera_recoil']=False
        r['status']='saved_unselected_native_source_recoil_requires_motion_visual_gate'
    else:raise ValueError(STAGE)
except Exception:
    r['errors'].append(traceback.format_exc());r['status']='failed'
finally:
    r['protected_files_unchanged']=guard()
    (OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    unreal.SystemLibrary.quit_editor()
