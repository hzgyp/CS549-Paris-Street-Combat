"""Runtime-only player aim substitution: never modifies/saves the editor city or NPCs."""
import hashlib,json
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
EVIDENCE=STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def runtime_class(package):
    # Generated classes load normally during PIE; EditorAssetLibrary refuses play mode.
    cls=unreal.load_class(None,package+'.'+package.rsplit('/',1)[1]+'_C')
    assert cls,package
    return cls
def trial_records():
    reports=[json.loads((EVIDENCE/n/'result.json').read_text()) for n in ('author_v4','rigid_author_v1','gun_author_v1')]
    assert all(not r['errors'] and r['status'].startswith('saved_unselected') for r in reports)
    files=[r['saved_trial'] for r in reports]
    assert all((ROOT/e['path']).stat().st_size==e['size_bytes'] and digest(ROOT/e['path'])==e['sha256'] for e in files)
    return files
def stage(world,player):
    files=trial_records()
    current=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
    deps=json.loads((ROOT/current['retained_dependency_inventory']).read_text())
    original=current['files']+deps['files']+current['retained_unselected_rejected_trial']
    assert all(digest(ROOT/e['path'])==e['sha256'] for e in original)
    mesh=player.get_component_by_class(unreal.SkeletalMeshComponent)
    old=player.get_editor_property('WeaponAppearance')
    assert old.get_class().get_name()=='BP_PC_RifleAttachmentV3_C'
    cls=runtime_class(files[2]['package'])
    spawn=unreal.get_default_object(unreal.GameplayStatics.static_class())
    new=spawn.call_method('BeginDeferredActorSpawnFromClass',args=(world,cls,old.get_actor_transform(),unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN,player,unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    new.set_editor_property('GripMesh',mesh);new.set_editor_property('Combatant',player);new.set_editor_property('LeftShiftCm',.5)
    new=spawn.call_method('FinishSpawningActor',args=(new,old.get_actor_transform(),unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT))
    assert new.attach_to_component(mesh,'hand_r',unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,unreal.AttachmentRule.KEEP_WORLD,False)
    mesh.set_anim_instance_class(runtime_class(files[1]['package']))
    player.set_editor_property('WeaponAppearance',new)
    old.call_method('K2_DestroyActor')
    return {'scope':'Transient PIE-only player variant; editor city and NPC selections unchanged','files':files,
            'player_anim_class':mesh.get_anim_instance().get_class().get_path_name(),
            'weapon_class':new.get_class().get_path_name(),'current_city_checkpoint':'CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json',
            'human_contact_and_fp_framing_pending':True,'published':False}
