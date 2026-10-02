"""Bounded source-motion subset/dependency discovery, pose review and UE582 save."""
import hashlib
import json
import math
import os
import traceback
from datetime import datetime
from pathlib import Path
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence/Baseline20261002'
OUT.mkdir(parents=True, exist_ok=True)
MODE = os.environ.get('CS549_RIFLE_BASELINE_MODE', 'inspect')
IDENTITY = os.environ.get('CS549_RIFLE_BASELINE_IDENTITY', MODE)
DEST = OUT / (IDENTITY + '.json')
if DEST.exists():
    raise RuntimeError('Existing baseline evidence; do not overwrite')
CLIPS = ['W2_Stand_Aim_Idle_IP', 'W2_Stand_Fire_Single_IP', 'W2_Stand_Aim_Reload_IP',
    'W2_Walk_Aim_F_Loop_IP', 'W2_Walk_Aim_B_Loop_IP', 'W2_Walk_Aim_L_Loop_IP', 'W2_Walk_Aim_R_Loop_IP',
    'W2_Stand_Aim_To_Walk_Aim_F_IP', 'W2_Stand_Aim_To_Walk_Aim_L90_Fwd_IP', 'W2_Stand_Aim_To_Walk_Aim_R90_Fwd_IP',
    'W2_Walk_Aim_F_to_W2_Stand_Aim_LU_IP', 'W2_Walk_Aim_F_to_W2_Stand_Aim_RU_IP',
    'W2_Stand_Aim_To_Relaxed_IP', 'W2_Stand_Relaxed_Death_F_IP', 'W2_Stand_Relaxed_Death_B_IP']
PREFIX = '/Game/Rifle_01/Animation/In-Place/'
MESH = '/Game/Rifle_01/Character/Mesh/SK_Mannequin'
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'mode': MODE,
    'started_at': datetime.now().astimezone().isoformat(), 'scope': 'generic full-body source-motion baseline only; not FP, M1 mechanics, historical/contact/gameplay acceptance',
    'clips': [], 'closure': [], 'engine_dependencies': [], 'poses': [], 'captures': [], 'errors': []}

def checkpoint():
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')

try:
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    registry.search_all_assets(True)
    if MODE == 'clean_preview':
        skeleton = unreal.load_asset(MESH).get_editor_property('skeleton')
        assert unreal.ParisBlueprintAuthoring.clear_skeleton_preview_attachments(skeleton.get_path_name())
        assert unreal.EditorAssetLibrary.save_loaded_asset(skeleton, only_if_is_dirty=False)
        report['preview_edit'] = 'Cleared editor-only attached preview assets on lab skeleton; reference bones, sockets, clip tracks and original delivery unchanged'
        MODE = 'clean_preview'  # Still discover the saved post-edit closure.
        registry.scan_modified_asset_files([str(LAB/'Content/Rifle_01/Character/Mesh/UE4_Mannequin_Skeleton.uasset')])
    options = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,
        include_hard_package_references=True, include_searchable_names=False,
        include_soft_management_references=False, include_hard_management_references=False)
    pending, packages, external = [MESH] + [PREFIX+c for c in CLIPS], set(), set()
    while pending:
        path = pending.pop()
        if path in packages:
            continue
        if not path.startswith('/Game/Rifle_01/'):
            if path.startswith(('/Engine/', '/Script/', '/ACLPlugin/')):
                if path.startswith('/ACLPlugin/') and not unreal.load_asset(path):
                    raise RuntimeError('Missing built-in UE ACL compression dependency ' + path)
                external.add(path)
                continue
            raise RuntimeError('Unexpected closure package ' + path)
        packages.add(path)
        if len(packages) > 100:
            raise RuntimeError('Unexpected broad closure; inspect before admission')
        asset = unreal.load_asset(path)
        if not asset:
            raise RuntimeError('Missing dependency ' + path)
        pending.extend(str(x) for x in registry.get_dependencies(path, options))
    report['engine_dependencies'] = sorted(external)
    loaded = {p: unreal.load_asset(p) for p in sorted(packages)}
    for path, asset in loaded.items():
        file = LAB / 'Content' / (path.removeprefix('/Game/') + '.uasset')
        if not file.is_file():
            raise RuntimeError('Missing ordinary native file ' + path)
        row = {'package': path, 'class': asset.get_class().get_name(), 'path': file.relative_to(LAB).as_posix(),
            'size_bytes': file.stat().st_size, 'sha256_before': hashlib.sha256(file.read_bytes()).hexdigest(),
            'dependencies': sorted(str(x) for x in registry.get_dependencies(path, options))}
        report['closure'].append(row)
    mesh = loaded[MESH]
    skeleton = mesh.get_editor_property('skeleton')
    for clip in CLIPS:
        asset = loaded[PREFIX+clip]
        if asset.get_editor_property('skeleton') != skeleton:
            raise RuntimeError('Unexpected clip skeleton ' + clip)
        report['clips'].append({'package': PREFIX+clip,
            'duration_seconds': unreal.AnimationLibrary.get_sequence_length(asset),
            'frames': unreal.AnimationLibrary.get_num_frames(asset),
            'root_motion_enabled': asset.get_editor_property('enable_root_motion'),
            'bone_tracks': len(unreal.AnimationLibrary.get_animation_track_names(asset)),
            'skeleton': skeleton.get_path_name()})
    checkpoint()
    if MODE == 'inspect':
        assert unreal.EditorLevelLibrary.new_level('/Game/ParisCombat/Tests/MotionBaseline/Unsaved_' + datetime.now().strftime('%H%M%S'))
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        for pitch,yaw in [(-25,-135),(-25,45),(-15,90),(-15,-90)]:
            light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0,0,300), unreal.Rotator(pitch=pitch,yaw=yaw,roll=0))
            comp = light.get_component_by_class(unreal.DirectionalLightComponent)
            comp.set_intensity(12)
            comp.set_cast_shadows(False)
        sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0,0,300))
        comp = sky.get_component_by_class(unreal.SkyLightComponent)
        comp.set_mobility(unreal.ComponentMobility.MOVABLE)
        comp.set_editor_property('source_type',unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
        comp.set_cubemap(unreal.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'))
        comp.set_intensity(1)
        comp.recapture_sky()
        camera = actors.spawn_actor_from_class(unreal.SceneCapture2D,unreal.Vector(0,400,95))
        capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
        capture.set_editor_property('capture_source',unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
        capture.set_editor_property('capture_every_frame',False)
        capture.set_editor_property('capture_on_movement',False)
        capture.set_editor_property('projection_type',unreal.CameraProjectionMode.ORTHOGRAPHIC)
        capture.set_editor_property('ortho_width',250)
        target = unreal.RenderingLibrary.create_render_target2d(world,900,1000,unreal.TextureRenderTargetFormat.RTF_RGBA8,unreal.LinearColor(.1,.1,.1,1),False)
        capture.set_editor_property('texture_target',target)
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        model = None
        for clip in CLIPS:
            asset = loaded[PREFIX+clip]
            length = unreal.AnimationLibrary.get_sequence_length(asset)
            for sample in range(31):
                if model:
                    actors.destroy_actor(model)
                model = actors.spawn_actor_from_class(unreal.SkeletalMeshActor,unreal.Vector(0,0,0))
                component = model.get_component_by_class(unreal.SkeletalMeshComponent)
                component.set_skeletal_mesh_asset(mesh)
                time = length*min(sample/30,.999)
                component.override_animation_data(asset,False,False,time,1)
                positions = {}
                for bone in ['root','pelvis','head','upperarm_l','lowerarm_l','hand_l','index_03_l','upperarm_r','lowerarm_r','hand_r','index_03_r','foot_l','foot_r']:
                    t = component.get_bone_transform(bone,unreal.RelativeTransformSpace.RTS_COMPONENT).translation
                    positions[bone] = [t.x,t.y,t.z]
                finite = all(math.isfinite(v) for xyz in positions.values() for v in xyz)
                if not finite:
                    raise RuntimeError('Nonfinite pose ' + clip)
                report['poses'].append({'clip':clip,'time_seconds':time,'positions_cm':positions,'finite':finite})
                if sample in (0,15,30):
                    for view,location in [('front',(0,400,95)),('side',(400,0,95))]:
                        point = unreal.Vector(*location)
                        camera.set_actor_location(point,False,False)
                        camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(point,unreal.Vector(0,0,95)),False)
                        capture.capture_scene()
                        filename=f'{clip}_{sample:02d}_{view}.png'
                        unreal.RenderingLibrary.export_render_target(world,target,str(OUT),filename)
                        report['captures'].append({'clip':clip,'sample':sample,'view':view,'file':filename})
            checkpoint()
    elif MODE == 'save':
        approval = json.loads((OUT/'visual_review.json').read_text(encoding='utf-8'))
        if approval['status'] != 'accepted_generic_source_motion_only':
            raise RuntimeError('Need direct pose review before selected resave')
        for row in report['closure']:
            assert unreal.EditorAssetLibrary.save_loaded_asset(loaded[row['package']],only_if_is_dirty=False)
            file=LAB/row['path']
            row['sha256_after']=hashlib.sha256(file.read_bytes()).hexdigest()
            row['size_bytes_after']=file.stat().st_size
    elif MODE not in ('fresh', 'clean_preview'):
        raise RuntimeError('Unknown baseline mode')
    report['status']='complete_'+MODE+'_bounded_source_motion_only'
except Exception:
    report['status']='failed'
    report['errors'].append(traceback.format_exc())
report['finished_at']=datetime.now().astimezone().isoformat()
checkpoint()
unreal.log('CS549_RIFLE_BASELINE '+report['status'])
if report['errors']:
    raise RuntimeError('Read preserved baseline report')
