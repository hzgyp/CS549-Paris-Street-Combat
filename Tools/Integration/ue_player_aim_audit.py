"""Read-only existing aim capabilities and actual upper-spine axis calibration."""
import hashlib,json,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[2]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/CityGameplay20261002/RifleCrosshairV4/upper_audit_v1'
assert not OUT.exists()
OUT.mkdir(parents=True)
a=json.loads((ROOT/'Assets/Integration/CITY_RIFLE_ACTION_DRAFT_INVENTORY_20261002.json').read_text())
d=json.loads((ROOT/a['retained_dependency_inventory']).read_text())
records=a['files']+d['files']+a['retained_unselected_rejected_trial']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert all(digest(ROOT/e['path'])==e['sha256'] for e in records)
r={'status':'initializing','errors':[]}
try:
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert levels.load_level('/Game/ParisCombat/Tests/Integration/P2_CharacterLifecycle_20261001')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    pawn=actors.spawn_actor_from_class(unreal.EditorAssetLibrary.load_blueprint_class('/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisPlayerV1'),unreal.Vector(0,0,100))
    mesh=pawn.get_component_by_class(unreal.SkeletalMeshComponent)
    clip=unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle')
    mesh.set_update_animation_in_editor(True)
    mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
    mesh.override_animation_data(clip,False,False,0,1)
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    def center(side):
        fs=('middle','ring','pinky') if side=='r' else ('index','middle','ring','pinky')
        ns=[f+'_0'+str(s)+'_'+side for f in fs for s in (2,3)]+['thumb_02_'+side,'thumb_03_'+side]
        return sum((mesh.get_socket_location(n) for n in ns),unreal.Vector())/len(ns)
    direction=center('l')-center('r')
    direction=direction/direction.length()
    def xyz(v): return [v.x,v.y,v.z]
    r['calibration']={}
    for n in ('spine_01','spine_02','spine_03','clavicle_l','clavicle_r','hand_l','hand_r'):
        t=mesh.get_socket_transform(n)
        axis=unreal.MathLibrary.inverse_transform_direction(t,direction)
        r['calibration'][n]={'position':xyz(t.translation),'axis':xyz(axis),'rotation':str(t.rotation)}
    registry=unreal.AssetRegistryHelpers.get_asset_registry()
    r['existing_aim_content']=[{'package':str(e.package_name),'class':str(e.asset_class_path)} for e in registry.get_assets_by_path('/Game/RifleAnimsetPro',True) if 'aim' in str(e.asset_name).lower() or 'offset' in str(e.asset_class_path).lower()]
    r['graph_api']=dir(unreal.BlueprintGraphEditor)
    r['pin_api']=dir(unreal.BlueprintGraphPinLibrary)
    r['status']='read_only_upper_axis_and_aim_inventory'
except Exception: r['status']='failed';r['errors'].append(traceback.format_exc())
finally:
    r['protected_37_unchanged']=all(digest(ROOT/e['path'])==e['sha256'] for e in records)
    (OUT/'result.json').write_text(json.dumps(r,indent=2))
    unreal.SystemLibrary.quit_editor()
