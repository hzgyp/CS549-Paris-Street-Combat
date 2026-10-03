"""Transient same-model first-person display; original world/action mesh is retained."""
import hashlib,json
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
EVIDENCE=STORE/'Evidence/CityGameplay20261002/FirstPersonViewV1'
SOURCE_ANIM='/Game/ParisCombat/Animation/DirectionalDraft/ABP_PC_Allied_Stride_v1'
VIEW='/Game/ParisCombat/Blueprints/FirstPersonViewV1/BP_PC_FirstPersonViewV1'
GUN='/Game/ParisCombat/Blueprints/FirstPersonViewV1/BP_PC_FirstPersonRifleV1'
def runtime_class(package):
    cls=unreal.load_class(None,package+'.'+package.rsplit('/',1)[1]+'_C');assert cls,package;return cls
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def trial_records():
    record=json.loads((ROOT/'Assets/Integration/FIRST_PERSON_VIEW_TRIAL_INVENTORY_20261002.json').read_text())
    files=record['files']
    assert 2<=len(files)<=7 and len({f['path'] for f in files})==len(files)
    assert all('/FirstPersonViewV1/' in f['package'] for f in files)
    assert all((ROOT/f['path']).stat().st_size==f['size_bytes'] and digest(ROOT/f['path'])==f['sha256'] for f in files)
    old=json.loads((ROOT/'Assets/Integration/PLAYER_AIM_TRIAL_INVENTORY_20261002.json').read_text())['files']
    assert all(digest(ROOT/f['path'])==f['sha256'] for f in old)
    return old+files
def stage(world,player):
    files=trial_records()
    inv=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
    dep=json.loads((ROOT/inv['retained_dependency_inventory']).read_text())
    assert all(digest(ROOT/f['path'])==f['sha256'] for f in inv['files']+dep['files']+inv['retained_unselected_rejected_trial'])
    mesh=player.get_component_by_class(unreal.SkeletalMeshComponent)
    assert mesh.get_anim_instance().get_class()==runtime_class(SOURCE_ANIM)
    camera=player.get_component_by_class(unreal.CameraComponent)
    assert camera.get_editor_property('relative_location')==unreal.Vector(25,0,60) and camera.get_editor_property('field_of_view')==90
    old=player.get_editor_property('WeaponAppearance');assert old.get_class().get_name()=='BP_PC_RifleAttachmentV3_C'
    api=unreal.get_default_object(unreal.GameplayStatics.static_class())
    def spawn(package,transform,properties):
        obj=api.call_method('BeginDeferredActorSpawnFromClass',args=(world,runtime_class(package),transform,unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,player,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
        for name,value in properties.items():obj.set_editor_property(name,value)
        return api.call_method('FinishSpawningActor',args=(obj,transform,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    view=spawn(VIEW,mesh.get_world_transform(),{'SourceMesh':mesh,'Combatant':player})
    viewmesh=view.get_component_by_class(unreal.SkeletalMeshComponent)
    assert viewmesh.get_skeletal_mesh_asset()==mesh.get_skeletal_mesh_asset()
    assert all(viewmesh.get_material(slot).get_blend_mode()==unreal.BlendMode.BLEND_MASKED for slot in (2,8)), 'Actual masked rendering is required; raw parent BlendMode is insufficient'
    gun=spawn(GUN,old.get_actor_transform(),{'GripMesh':viewmesh,'Combatant':player,'LeftShiftCm':.5})
    assert gun.attach_to_component(viewmesh,'hand_r',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    gun.static_mesh_component.set_only_owner_see(True);gun.static_mesh_component.set_cast_shadow(False)
    gun.static_mesh_component.set_visibility(False)
    # Rendering switches affect only this owner's view. Original mesh/collision/pose stay intact.
    mesh.set_owner_no_see(True);old.static_mesh_component.set_owner_no_see(True)
    mesh.set_cast_hidden_shadow(True);old.static_mesh_component.set_cast_hidden_shadow(True)
    player.set_editor_property('WeaponAppearance',gun)
    return {'scope':__doc__,'files':files,'view_actor':view.get_path_name(),'view_class':view.get_class().get_path_name(),
            'source_anim_class':mesh.get_anim_instance().get_class().get_path_name(),'weapon_class':gun.get_class().get_path_name(),
            'world_gun_retained':old.get_path_name(),'camera_unchanged':True,'map_saved':False,'human_visual_acceptance':False}
