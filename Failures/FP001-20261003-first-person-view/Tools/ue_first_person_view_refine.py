"""Preserved-draft correction: owner-view section visibility and initial pose warmup."""
import hashlib,json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from ue_paris_graph_helpers import lib,pins,wire,pin,call,pure,get,run,value
from ue_first_person_view_runtime import trial_records,VIEW,EVIDENCE
OUT=EVIDENCE/os.environ['CS549_FP_IDENTITY'];assert not OUT.exists();OUT.mkdir()
inventory=ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json'
record=json.loads(inventory.read_text());files=trial_records()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(inventory,OUT/'before_inventory.json')
for f in record['files']:
    p=ROOT/f['path'];copy=OUT/p.name;shutil.copy2(p,copy);assert digest(copy)==f['sha256']
r={'scope':__doc__,'errors':[],'status':'initializing'}
def math(g,n,**kw):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**kw)
def put(g,flow,n,v):
    node=g.add_set_member_variable_node(n);value(pin(node,n),v);return run(g,flow,node)
def branch(g,flow,condition):
    n=g.add_branch_node();wire(condition,pin(n,'Condition'));wire(flow,lib.find_execute_pin(n));return pin(n,'then',True),pin(n,'else',True)
try:
    bp=unreal.load_asset(VIEW);events=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    assert events.add_member_variable('ViewInitialized',lib.get_basic_type_by_name('bool'),'false')
    assert events.add_member_variable('ViewWarmFrames',lib.get_basic_type_by_name('int'),'0')
    assert lib.compile_blueprint(bp)
    cdo=unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(VIEW))
    cdo.set_editor_property('RightGripCamera',unreal.Vector(46,8,-13))
    mesh=cdo.get_component_by_class(unreal.SkeletalMeshComponent)
    mesh.set_visibility(False,True)
    lod_count=mesh.get_num_lods();assert 1<=lod_count<=8;r['lod_count']=lod_count
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_InitializeFirstPersonVisibility')
    flow,done=branch(g,g.find_graph_entry_pin(),math(g,'Not_PreBool',A=get(g,'ViewInitialized')))
    flow=put(g,flow,'ViewWarmFrames',math(g,'Add_IntInt',A=get(g,'ViewWarmFrames'),B=1))
    flow,wait=branch(g,flow,math(g,'GreaterEqual_IntInt',A=get(g,'ViewWarmFrames'),B=3))
    component=get(g,'SkeletalMeshComponent','/Script/Engine.SkeletalMeshActor')
    for bone in ('neck_01','thigh_l','thigh_r'):
        flow=run(g,flow,call(g,'/Script/Engine.SkinnedMeshComponent.UnHideBoneByName',self=component,BoneName=bone))
    flow=run(g,flow,call(g,'/Script/Engine.SkinnedMeshComponent.HideBoneByName',self=component,BoneName='head',PhysBodyOption='PBO_None'))
    # Keep original jacket/sleeves (2) and skin/hands (8). Head skin is excluded by head bone only.
    hidden=[0,1,3,4,5,6,7,9,10,11,12,13]
    for lod in range(lod_count):
        for material in hidden:
            flow=run(g,flow,call(g,'/Script/Engine.SkinnedMeshComponent.ShowMaterialSection',self=component,MaterialID=material,SectionIndex=-1,bShow=False,LODIndex=lod))
    flow=run(g,flow,call(g,'/Script/Engine.SceneComponent.SetVisibility',self=component,bNewVisibility=True,bPropagateToChildren=True))
    put(g,flow,'ViewInitialized',True)
    body=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'PC_UpdateFirstPersonView')
    start=body.find_graph_entry_pin();old=pins.list_connected_pins(start);assert len(old)==1
    pins.break_pin_links(start);wire(run(body,start,call(body,'PC_InitializeFirstPersonVisibility')),old[0])
    assert lib.compile_blueprint(bp)
    assert not [n for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    for f in record['files']:
        p=ROOT/f['path'];f.update(size_bytes=p.stat().st_size,sha256=digest(p))
    record['previous_revision_backup']=OUT.relative_to(ROOT).as_posix()
    record['right_grip_camera_cm']=[46,8,-13]
    record['view_only_hidden_material_slots']=hidden
    record['status']='unselected_refined_draft_requires_fresh_runtime_and_human_review'
    inventory.write_text(json.dumps(record,indent=2)+'\n')
    r['status']='saved_only_view_blueprint_refinement';r['files']=record['files']
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
