"""New-only native CopyPose accepted-grip layer, no new motions/retarget/weights."""
import json,os,re,sys,traceback
from pathlib import Path
import unreal
sys.path.insert(0,str(Path(__file__).parent))
from common import ROOT,STORE,BASE,config,guard,inventory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ue_paris_graph_helpers import lib,pins,pin,wire,value,get
OUT=BASE/os.environ['CS549_GRIP_BINDING_ID'];assert not OUT.exists();OUT.mkdir()
DEST='/Game/ParisCombat/Animation/GripBindingV18/ABP_PCGripBindingV18'
r={'errors':[],'stages':[],'packages':[],'map_saved':False,'selected':False}
def stage(n):
    r['stages'].append(n);(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n');unreal.log('GRIP_BINDING_V18 '+n)
def describe(n):
    return {'class':n.get_class().get_name(),'pins':[{'name':str(pins.get_pin_name(p)),'value':pins.get_pin_value(p)} for p in lib.list_all_pins(n)]}
try:
    r['guards_before']=guard();assert not r['guards_before']['mismatches']
    c=config();assert not hasattr(unreal,'ParisBlueprintAuthoring')
    assert not unreal.EditorAssetLibrary.does_asset_exist(DEST)
    mesh=unreal.load_asset(c['source_mesh']);assert mesh
    factory=unreal.AnimBlueprintFactory()
    factory.set_editor_property('target_skeleton',mesh.get_editor_property('skeleton'))
    factory.set_editor_property('preview_skeletal_mesh',mesh)
    factory.set_editor_property('parent_class',unreal.AnimInstance.static_class())
    bp=unreal.AssetToolsHelpers.get_asset_tools().create_asset(DEST.rsplit('/',1)[1],DEST.rsplit('/',1)[0],unreal.AnimBlueprint,factory);assert bp
    graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'AnimGraph')
    event=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    assert event.add_member_variable('PoseSource',lib.get_object_reference_type(unreal.SkeletalMeshComponent.static_class()))
    assert event.add_member_variable('GripAlpha',lib.get_basic_type_by_name('real'),'1')
    menu=[str(x) for x in graph.list_available_nodes([])]
    def normalized(n):return re.sub('[^a-z0-9]','',n.lower())
    r['capabilities']=[n for n in menu if any(k in normalized(n) for k in ('copypose','modifybone','twoboneik','localtocomponent','componenttolocal'))]
    stage('new_unsaved_graph_menu_recorded')
    def node(token):
        found=[n for n in menu if token in normalized(n) and
               (token not in ('modifybone','twoboneik') or n.startswith('Animation|SkeletalControls|'))]
        assert len(found)==1,(token,found)
        result=graph.create_node_from_name(found[0],unreal.Vector2D(),[]);assert result
        return result
    cp=node('copyposefrommesh')
    wire(get(graph,'PoseSource'),pin(cp,'SourceMeshComponent'))
    lc=node('localtocomponent');wire(pin(cp,'Pose',True),pin(lc,'LocalPose'))
    preceding=pin(lc,'ComponentPose',True)
    # First compile a minimal source-preserving copy/scale graph. No broad
    # authoring is attempted until this exact capability compiles cleanly.
    scale=node('modifybone');data=scale.get_editor_property('node')
    bone=data.get_editor_property('bone_to_modify');bone.set_editor_property('bone_name','pinky_02_r');data.set_editor_property('bone_to_modify',bone)
    data.set_editor_property('rotation_mode',unreal.BoneModificationMode.BMM_IGNORE)
    data.set_editor_property('translation_mode',unreal.BoneModificationMode.BMM_IGNORE)
    data.set_editor_property('scale_mode',unreal.BoneModificationMode.BMM_REPLACE)
    data.set_editor_property('scale_space',unreal.BoneControlSpace.BCS_BONE_SPACE)
    scale.set_editor_property('node',data)
    value(pin(scale,'Scale'),'(X=0.9,Y=0.9,Z=0.9)')
    wire(preceding,pin(scale,'ComponentPose'))
    cl=node('componenttolocal');wire(pin(scale,'ComponentPose',True),pin(cl,'ComponentPose'))
    root=[n for n in graph.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_Root'];assert len(root)==1
    wire(pin(cl,'LocalPose',True),pin(root[0],'Result'))
    r['minimal_nodes']=[describe(n) for n in (cp,lc,scale,cl)]
    stage('minimal_copy_scale_graph_before_compile')
    assert lib.compile_blueprint(bp)
    graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'AnimGraph')
    assert not graph.list_nodes_with_errors()
    stage('minimal_copy_scale_compile_pass')
    # Reacquire all graph objects after compile. The new chain only reproduces
    # the already accepted rotations; no angle solve or source edit occurs.
    menu=[str(x) for x in graph.list_available_nodes([])]
    lc=[n for n in graph.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_LocalToComponentSpace'][0]
    scale=[n for n in graph.list_all_nodes() if n.get_class().get_name()=='AnimGraphNode_ModifyBone'][0]
    source_pin=pin(lc,'ComponentPose',True)
    r['rotation_bindings']=[]
    for name,row in c['fingers_local'].items():
        n=node('modifybone');data=n.get_editor_property('node')
        bone=data.get_editor_property('bone_to_modify');bone.set_editor_property('bone_name',name);data.set_editor_property('bone_to_modify',bone)
        data.set_editor_property('rotation_mode',unreal.BoneModificationMode.BMM_REPLACE)
        data.set_editor_property('rotation_space',unreal.BoneControlSpace.BCS_PARENT_BONE_SPACE)
        data.set_editor_property('translation_mode',unreal.BoneModificationMode.BMM_IGNORE)
        data.set_editor_property('scale_mode',unreal.BoneModificationMode.BMM_IGNORE)
        n.set_editor_property('node',data)
        q=unreal.Quat(*row['q']);rot=q.rotator()
        value(pin(n,'Rotation'),f'(Pitch={rot.pitch},Yaw={rot.yaw},Roll={rot.roll})')
        wire(get(graph,'GripAlpha'),pin(n,'Alpha'))
        wire(source_pin,pin(n,'ComponentPose'));source_pin=pin(n,'ComponentPose',True)
        r['rotation_bindings'].append({'bone':name,'local_q':row['q']})
    ik=node('twoboneik');data=ik.get_editor_property('node')
    bone=data.get_editor_property('ik_bone');bone.set_editor_property('bone_name','hand_l');data.set_editor_property('ik_bone',bone)
    data.set_editor_property('effector_location_space',unreal.BoneControlSpace.BCS_BONE_SPACE)
    data.set_editor_property('joint_target_location_space',unreal.BoneControlSpace.BCS_BONE_SPACE)
    for prop in ('effector_target','joint_target'):
        target=data.get_editor_property(prop)
        bone=target.get_editor_property('bone_reference');bone.set_editor_property('bone_name','hand_r');target.set_editor_property('bone_reference',bone)
        target.set_editor_property('use_socket',False);data.set_editor_property(prop,target)
    data.set_editor_property('allow_stretching',False)
    data.set_editor_property('take_rotation_from_effector_space',True)
    ik.set_editor_property('node',data)
    def vec(v):return f'(X={v[0]},Y={v[1]},Z={v[2]})'
    value(pin(ik,'EffectorLocation'),vec(c['support_hand_relative_to_right']['t']))
    value(pin(ik,'JointTargetLocation'),vec(c['elbow_pole_relative_to_right_cm']))
    wire(get(graph,'GripAlpha'),pin(ik,'Alpha'));wire(source_pin,pin(ik,'ComponentPose'));source_pin=pin(ik,'ComponentPose',True)
    n=node('modifybone');data=n.get_editor_property('node')
    bone=data.get_editor_property('bone_to_modify');bone.set_editor_property('bone_name','hand_l');data.set_editor_property('bone_to_modify',bone)
    data.set_editor_property('rotation_mode',unreal.BoneModificationMode.BMM_ADDITIVE)
    data.set_editor_property('rotation_space',unreal.BoneControlSpace.BCS_BONE_SPACE)
    data.set_editor_property('translation_mode',unreal.BoneModificationMode.BMM_IGNORE)
    data.set_editor_property('scale_mode',unreal.BoneModificationMode.BMM_IGNORE)
    n.set_editor_property('node',data)
    rot=unreal.Quat(*c['support_hand_relative_to_right']['q']).rotator()
    value(pin(n,'Rotation'),f'(Pitch={rot.pitch},Yaw={rot.yaw},Roll={rot.roll})')
    wire(get(graph,'GripAlpha'),pin(n,'Alpha'));wire(source_pin,pin(n,'ComponentPose'))
    wire(pin(n,'ComponentPose',True),pin(scale,'ComponentPose'))
    stage('accepted_rotation_and_support_chain_before_compile')
    assert lib.compile_blueprint(bp)
    graph=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'AnimGraph')
    r['graph_errors']=[str(n) for n in graph.list_nodes_with_errors()];assert not r['graph_errors']
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    r['packages']=[inventory(DEST)]
    r['status']='saved_unselected_native_binding_requires_fresh_pose_and_view_proof'
    stage('new_anim_binding_saved')
except Exception:r['status']='stopped_author_error';r['errors'].append(traceback.format_exc())
finally:
    r['guards_after']=guard();(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
    unreal.SystemLibrary.quit_editor()
