"""Read-only actual M1 FBX plus native compressed index poses, no old owner/lab rerun."""
import hashlib,json,os,traceback
from pathlib import Path
import unreal
ROOT=Path(__file__).resolve().parents[3]
STORE=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT=STORE/'Evidence/ReloadIndexContactV6'/os.environ['CS549_INDEX_V6_ID']
assert not OUT.exists();OUT.mkdir(parents=True)
(OUT/'source.py').write_bytes(Path(__file__).read_bytes())
rows=json.loads((STORE/'Evidence/ReloadIndexContactV6/preflight_v1/result.json').read_text())['files']
def guard():return all((ROOT/r['path']).stat().st_size==r['size_bytes'] and hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in rows)
r={'scope':__doc__,'status':'starting','stages':[],'errors':[], 'native_modified':False,'map_saved':False,
   'limitation':'Native compressed editor evaluation, not full runtime owner blend, gameplay or contact acceptance.',
   'models':{},'clips':{}}
def write():(OUT/'result.json').write_text(json.dumps(r,indent=2)+'\n')
def stage(s):r['stages'].append(s);write();unreal.log('INDEX_CONTACT_V6 '+s)
def tr(t):return {'t':[t.translation.x,t.translation.y,t.translation.z],
 'q':[t.rotation.x,t.rotation.y,t.rotation.z,t.rotation.w],'s':[t.scale3d.x,t.scale3d.y,t.scale3d.z]}
try:
    assert len(rows)==528 and guard() and not hasattr(unreal,'ParisBlueprintAuthoring')
    stage('guarded528_current_bytes_no_city_load')
    gun=unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand');assert isinstance(gun,unreal.StaticMesh)
    options=unreal.FbxExportOption()
    for name,v in {'ascii':False,'level_of_detail':False,'collision':False,'export_preview_mesh':False,'bake_material_inputs':unreal.FbxMaterialBakeMode.DISABLED}.items():options.set_editor_property(name,v)
    task=unreal.AssetExportTask();task.object=gun;task.filename=str(OUT/'Sm_M1_Garand.fbx');task.options=options
    task.automated=True;task.prompt=False;task.replace_identical=False
    stage('actual_static_m1_export_before_native_call')
    ok=unreal.Exporter.run_asset_export_task(task)
    r['gun_export']={'asset':gun.get_path_name(),'ok':bool(ok),'errors':list(task.errors),'file':'Sm_M1_Garand.fbx'}
    assert ok and not task.errors and (OUT/'Sm_M1_Garand.fbx').stat().st_size>1000
    stage('actual_static_m1_exported')
    for label,path in {'owner':'/Game/ParisCombat/Characters/FirstPersonContinuousArmsV3/SK_PC_ContinuousArmsV3',
                       'sleeve_copy':'/Game/ParisCombat/Characters/ReloadRepairV5/SK_PC_SleeveWeightsV5'}.items():
        mesh=unreal.load_asset(path);assert mesh
        options=unreal.AnimPoseEvaluationOptions();options.set_editor_property('optional_skeletal_mesh',mesh)
        options.set_editor_property('evaluation_type',unreal.AnimDataEvalType.COMPRESSED)
        r['models'][label]={'asset':mesh.get_path_name(),'skeleton':mesh.get_editor_property('skeleton').get_path_name()}
        for action,clip_path in {'reload':'/Game/ParisCombat/Animation/WeaponAnimationReuseV1/AS_PC_D059AimReloadV1',
                                 'idle':'/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle'}.items():
            clip=unreal.load_asset(clip_path);length=clip.get_play_length();name=label+'_'+action
            r['clips'][name]={'asset':clip.get_path_name(),'length_s':length,'samples':{}}
            for phase in ([0.,.4,1.2,2.2,3.4,3.8,3.98,4.1] if action=='reload' else [0.,.4]):
                t=min(phase,length-.00001)
                pose=unreal.AnimPoseExtensions.get_anim_pose_at_time(clip,t,options)
                names=unreal.AnimPoseExtensions.get_bone_names(pose)
                bones={str(n):tr(unreal.AnimPoseExtensions.get_bone_pose(pose,n,unreal.AnimPoseSpaces.WORLD)) for n in names}
                assert 'index_03_r' in bones and 'hand_r' in bones
                r['clips'][name]['samples'][str(phase)]={'phase':t,'bones_component':bones}
            stage(name+'_compressed_poses_collected')
    r['status']='read_only_exchange_and_pose_data_collected_requires_alignment_and_surface_review'
except Exception:r['status']='failed_exchange_stop';r['errors'].append(traceback.format_exc())
finally:
    r['protected_current528_unchanged']=guard()
    r['artifacts']=[{'file':p.name,'size_bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in OUT.glob('*.fbx')]
    write();unreal.SystemLibrary.quit_editor()
