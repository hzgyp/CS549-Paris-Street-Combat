"""Read-only native weapon/action closure inventory for the P3 human selection gate."""
import json
from pathlib import Path
import unreal

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P3'
OUT.mkdir(exist_ok=True)
DEST=OUT/'weapon_capability_v1.json'
if DEST.exists():
    raise RuntimeError('Refusing existing weapon inventory')
registry=unreal.AssetRegistryHelpers.get_asset_registry()
report={'engine':unreal.SystemLibrary.get_engine_version(),'native_meshes':[],'action_clips':[],
        'first_person_named_candidates':[],'blueprint_candidates':[],'errors':[],
        'scope':'Native package/rig/material/action metadata; not first-person, grip, muzzle, reload mechanics or historical acceptance'}
editor=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
for root in ('/Game/USParatrooper','/Game/GermanSoldier','/Game/RifleAnimsetPro'):
    for data in registry.get_assets_by_path(root,recursive=True):
        path=str(data.package_name)
        cls=str(data.asset_class_path.asset_name)
        if any(k in path.lower() for k in ('firstperson','first_person','fp_','arms','garand','kar98','thompson','clip','cartridge')):
            report['first_person_named_candidates'].append({'path':path,'class':cls,'note':'Name match only, not proven FP capability'})
        if cls in ('Blueprint','AnimBlueprint','AnimMontage'):
            report['blueprint_candidates'].append({'path':path,'class':cls})
        if cls not in ('SkeletalMesh','StaticMesh'):
            continue
        asset=unreal.load_asset(path)
        item={'path':path,'class':cls}
        if isinstance(asset,unreal.SkeletalMesh):
            c=unreal.new_object(unreal.SkeletalMeshComponent)
            c.set_skeletal_mesh_asset(asset)
            item['bones']=[str(c.get_bone_name(i)) for i in range(c.get_num_bones())]
            item['skeleton']=asset.get_editor_property('skeleton').get_path_name()
            physics=asset.get_editor_property('physics_asset')
            item['physics_asset']=physics.get_path_name() if physics else None
            item['materials']=[{'slot':str(m.material_slot_name),'material':m.material_interface.get_path_name() if m.material_interface else None} for m in asset.get_editor_property('materials')]
            item['lod_vertices']=[editor.get_num_verts(asset,i) for i in range(editor.get_lod_count(asset))]
        elif isinstance(asset,unreal.StaticMesh):
            item['materials']=[m.material_interface.get_path_name() if m.material_interface else None for m in asset.get_editor_property('static_materials')]
            if hasattr(asset,'get_bounding_box'):
                box=asset.get_bounding_box()
                item['bounds_cm']={'min':[box.min.x,box.min.y,box.min.z],'max':[box.max.x,box.max.y,box.max.z]}
        report['native_meshes'].append(item)
for name in ('Rifle_Idle','Rifle_ShootOnce','Rifle_Reload_2','Rifle_Hit_C_1','Rifle_Death_3'):
    clip=unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/'+name)
    report['action_clips'].append({'path':clip.get_path_name(),
        'length_s':unreal.AnimationLibrary.get_sequence_length(clip),
        'root_motion':clip.get_editor_property('enable_root_motion'),
        'tracks':[str(n) for n in unreal.AnimationLibrary.get_animation_track_names(clip)],
        'notifies':[str(n) for n in unreal.AnimationLibrary.get_animation_notify_event_names(clip)]})
report['locomotion_root_speeds']=[]
for name in ('Rifle_WalkFwdLoop','Rifle_WalkBwdLoop','Rifle_StrafeLeftLoop','Rifle_StrafeRightLoop','Rifle_RunFwdLoop','Rifle_RunBwdLoop'):
    clip=unreal.load_asset('/Game/RifleAnimsetPro/Animations/RootMotion/'+name)
    length=unreal.AnimationLibrary.get_sequence_length(clip)
    a=unreal.AnimationLibrary.get_bone_pose_for_time(clip,'root',0,False).translation
    b=unreal.AnimationLibrary.get_bone_pose_for_time(clip,'root',length,False).translation
    report['locomotion_root_speeds'].append({'path':clip.get_path_name(),'length_s':length,
        'root_delta_cm':[b.x-a.x,b.y-a.y,b.z-a.z],
        'average_planar_speed_cm_s':((b.x-a.x)**2+(b.y-a.y)**2)**.5/length})
DEST.write_text(json.dumps(report,indent=2),encoding='utf-8')
unreal.log('CS549_WEAPON_CAPABILITY_AUDIT_DONE')
