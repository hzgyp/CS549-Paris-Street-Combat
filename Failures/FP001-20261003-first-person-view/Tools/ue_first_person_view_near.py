"""Bound only owner-view Ready aim distance; original fire/obstruction logic is untouched."""
import hashlib,json,os,shutil,sys,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from ue_first_person_view_runtime import trial_records,VIEW,EVIDENCE,STORE
from ue_paris_graph_helpers import lib,pins,wire,pin,pure
OLD='/Game/ParisCombat/Blueprints/WeaponAimingV4/BP_PC_PlayerRifleAimV4'
DEST='/Game/ParisCombat/Blueprints/FirstPersonViewV1/BP_PC_FirstPersonRifleV1'
OUT=EVIDENCE/os.environ['CS549_FP_IDENTITY'];assert not OUT.exists();OUT.mkdir()
inventory=ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json'
record=json.loads(inventory.read_text());guard=trial_records()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copy2(inventory,OUT/'before_inventory.json')
for f in record['files']:
    p=ROOT/f['path'];copy=OUT/p.name;shutil.copy2(p,copy);assert digest(copy)==f['sha256']
r={'scope':__doc__,'errors':[],'status':'initializing','nodes':{}}
def math(g,n,**kw):return pure(g,'/Script/Engine.KismetMathLibrary.'+n,**kw)
try:
    exists=unreal.EditorAssetLibrary.does_asset_exist(DEST)
    if not exists:
        gun=unreal.EditorAssetLibrary.duplicate_asset(OLD,DEST);assert gun
        assert unreal.EditorAssetLibrary.save_loaded_asset(gun,only_if_is_dirty=False)
    else:assert any(f['package']==DEST for f in record['files']),'Recover and inventory the retained prior draft first'
    # Separate processes avoid retaining installed Python graph-pin wrappers across recompilation/GC.
    tasks=[(VIEW,'PC_UpdateFirstPersonView')] if exists else [(DEST,'PC_UpdateRifleAttachment')]
    for package,name in tasks:
        bp=unreal.load_asset(package)
        g=unreal.BlueprintGraphEditor.get_graph_editor_by_name(bp,name)
        nodes=g.list_all_nodes();r['nodes'][name]=[lib.get_node_title(n) for n in nodes]
        choices=[n for n in nodes if lib.get_node_title(n).replace(' ','').replace('\n','').lower()=='selectvector']
        assert len(choices)==1,r['nodes'][name]
        goal=pin(choices[0],'ReturnValue',True);destinations=pins.list_connected_pins(goal);assert destinations
        # The far fallback input already carries camera + forward * 20000.
        far=pins.list_connected_pins(pin(choices[0],'B'));assert len(far)==1
        player_cls=unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1')
        actor=g.add_get_member_variable_node('Combatant')
        camera=g.add_get_member_variable_node('ParisPlayerCamera',player_cls.get_path_name());wire(pin(actor,'Combatant',True),pin(camera,'self'))
        start=pure(g,'/Script/Engine.SceneComponent.K2_GetComponentLocation',self=pin(camera,'ParisPlayerCamera',True))
        direction=pure(g,'/Script/Engine.SceneComponent.GetForwardVector',self=pin(camera,'ParisPlayerCamera',True))
        minimum=math(g,'Add_VectorVector',A=start,B=math(g,'Multiply_VectorFloat',A=direction,B=150))
        distance=math(g,'VSize',A=math(g,'Subtract_VectorVector',A=goal,B=start))
        safe=math(g,'SelectVector',A=goal,B=minimum,bPickA=math(g,'GreaterEqual_DoubleDouble',A=distance,B=150))
        for dest in destinations:pins.break_pin_links(dest);wire(safe,dest)
        r['stage']='before_compile_'+name;(OUT/'result.json').write_text(json.dumps(r,indent=2))
        assert lib.compile_blueprint(bp)
        assert not [n for graph in lib.list_graphs(bp) for n in unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors()]
        assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
    p=STORE/('Content/'+DEST.removeprefix('/Game/')+'.uasset')
    if not exists:record['files'].append({'package':DEST,'path':p.relative_to(ROOT).as_posix()})
    for f in record['files']:
        p=ROOT/f['path'];f.update(size_bytes=p.stat().st_size,sha256=digest(p))
    assert all(digest(ROOT/f['path'])==f['sha256'] for f in guard[:3])
    record['previous_revision_backup']=OUT.relative_to(ROOT).as_posix()
    record['presentation_min_target_cm']=150 if exists else None
    record['status']='unselected_near_target_bounded_draft_requires_runtime_and_human_review' if exists else 'unselected_near_rifle_only_requires_view_update'
    inventory.write_text(json.dumps(record,indent=2)+'\n')
    r['status']='saved_only_new_view_and_new_rifle';r['files']=record['files']
except Exception:r['status']='failed';r['errors'].append(traceback.format_exc())
(OUT/'result.json').write_text(json.dumps(r,indent=2));unreal.SystemLibrary.quit_editor()
