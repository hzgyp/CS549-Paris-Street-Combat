"""GPU-cache-compatible owner-view forearm masking, after the copied pose tick."""
import hashlib,json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from ue_first_person_view_runtime import trial_records,GUN,EVIDENCE
from ue_paris_graph_helpers import lib,pins,wire,pin,call,pure,get,run
OUT=EVIDENCE/os.environ['CS549_FP_IDENTITY'];assert not OUT.exists();OUT.mkdir()
inventory=ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json'
record=json.loads(inventory.read_text());trial_records()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(inventory,OUT/'before_inventory.json')
for f in record['files']:
    p=ROOT/f['path'];copy=OUT/p.name;shutil.copy2(p,copy);assert digest(copy)==f['sha256']
r={'scope':__doc__,'errors':[],'status':'initializing','material_compilation':{}}
try:
    editing=unreal.MaterialEditingLibrary
    parameters={'L0':'lowerarm_l','L1':'middle_03_l','R0':'lowerarm_r','R1':'middle_03_r'}
    for label in ('Sleeves','Hands'):
        base=unreal.load_asset('/Game/ParisCombat/Materials/FirstPersonViewV1/M_PC_FirstPerson'+label+'V1')
        mask=editing.get_material_property_input_node(base,unreal.MaterialProperty.MP_OPACITY_MASK)
        assert isinstance(mask,unreal.MaterialExpressionCustom)
        inputs=[]
        for name in ('P',*parameters):
            i=unreal.CustomInput();i.set_editor_property('input_name',name);inputs.append(i)
        mask.set_editor_property('inputs',inputs)
        mask.set_editor_property('code','float3 a=P-L0,b=L1-L0; float dl=length(a-b*saturate(dot(a,b)/max(dot(b,b),0.001))); float3 c=P-R0,d=R1-R0; float dr=length(c-d*saturate(dot(c,d)/max(dot(d,d),0.001))); return step(min(dl,dr),9.0);')
        world=editing.create_material_expression(base,unreal.MaterialExpressionWorldPosition,-600,600)
        assert editing.connect_material_expressions(world,'',mask,'P')
        for index,name in enumerate(parameters):
            node=editing.create_material_expression(base,unreal.MaterialExpressionVectorParameter,-600,800+index*150)
            node.set_editor_property('parameter_name','FP_'+name)
            assert editing.connect_material_expressions(node,'',mask,name)
        errors=editing.recompile_material(base);r['material_compilation'][label]=[str(e) for e in errors];assert not errors
        assert unreal.EditorAssetLibrary.save_loaded_asset(base,only_if_is_dirty=False)
    bp=unreal.load_asset(GUN)
    g=unreal.BlueprintGraphEditor.create_and_edit_function_graph(bp,'PC_UpdateFirstPersonMask')
    mesh=get(g,'GripMesh');branch=g.add_branch_node();wire(g.find_graph_entry_pin(),lib.find_execute_pin(branch))
    wire(pure(g,'/Script/Engine.KismetSystemLibrary.IsValid',Object=mesh),pin(branch,'Condition'))
    flow=pin(branch,'then',True)
    for name,bone in parameters.items():
        location=pure(g,'/Script/Engine.SceneComponent.GetSocketLocation',self=mesh,InSocketName=bone)
        flow=run(g,flow,call(g,'/Script/Engine.MeshComponent.SetVectorParameterValueOnMaterials',self=mesh,ParameterName='FP_'+name,ParameterValue=location))
    events=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,'EventGraph')
    ticks=[]
    for n in events.list_all_nodes():
        if 'eventtick' in lib.get_node_title(n).replace(' ','').replace('\n','').lower():
            p=lib.find_then_pin(n)
            if pins.is_valid(p) and pins.list_connected_pins(p):ticks.append(p)
    assert len(ticks)==1
    start=ticks[0];destinations=pins.list_connected_pins(start);assert len(destinations)==1
    pins.break_pin_links(start);wire(run(events,start,call(events,'PC_UpdateFirstPersonMask')),destinations[0])
    assert lib.compile_blueprint(bp)
    assert not [n for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    for f in record['files']:
        p=ROOT/f['path'];f.update(size_bytes=p.stat().st_size,sha256=digest(p))
    record['previous_revision_backup']=OUT.relative_to(ROOT).as_posix()
    record['view_only_material_mask']='World-position elbow-to-middle-fingertip capsules, radius 9 cm; current copied pose; slots 2/8 only'
    record['status']='unselected_world_mask_draft_requires_fresh_visual_and_combat_tests'
    inventory.write_text(json.dumps(record,indent=2)+'\n')
    r['status']='saved_new_material_masks_and_new_rifle_helper';r['files']=record['files']
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
