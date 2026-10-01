"""UE RHI material captures, cross-skeleton pose samples and repair exports."""
import json
import runpy
import traceback
from pathlib import Path
from datetime import datetime
import unreal

TOOLS = Path(__file__).resolve().parent
runpy.run_path(str(TOOLS / 'ue_inventory.py'), run_name='__main__')
LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence'
EXPORTS = OUT / 'Exports'
EXPORTS.mkdir(exist_ok=True)
REPORT = {'engine': unreal.SystemLibrary.get_engine_version(),
          'started_at': datetime.now().astimezone().isoformat(),
          'exports': [], 'captures': [], 'pose_tests': [], 'errors': []}


def checkpoint():
    (OUT / 'ue_visual_exports.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')


def error(stage):
    REPORT['errors'].append({'stage': stage, 'traceback': traceback.format_exc()})
    checkpoint()


inventory = json.loads((OUT / 'ue_load_inventory.json').read_text())
REPORT['extra_api'] = {name: [v for v in dir(getattr(unreal, name)) if not v.startswith('_')]
    for name in ('AnimPoseEvaluationOptions', 'GLTFExportOptions', 'AnimSequence',
                 'AnimPoseExtensions', 'PoseableMeshComponent')}
checkpoint()

# Actual UE geometry/skin exports for Blender numerical and deformation checks.
fbx_options = unreal.FbxExportOption()
fbx_options.set_editor_property('ascii', False)
fbx_options.set_editor_property('level_of_detail', False)
fbx_options.set_editor_property('collision', False)
fbx_options.set_editor_property('export_morph_targets', True)
fbx_options.set_editor_property('export_preview_mesh', False)
fbx_options.set_editor_property('bake_material_inputs', unreal.FbxMaterialBakeMode.DISABLED)
mesh_paths = [a['path'] for a in inventory['assets'] if a.get('class') == 'SkeletalMesh']
for mesh_path in mesh_paths:
    try:
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        filename = EXPORTS / (mesh.get_name() + '.fbx')
        task = unreal.AssetExportTask()
        task.object = mesh
        task.filename = str(filename)
        task.automated = True
        task.prompt = False
        task.replace_identical = True
        task.options = fbx_options
        ok = unreal.Exporter.run_asset_export_task(task)
        REPORT['exports'].append({'asset': mesh_path, 'format': 'FBX',
            'ok': bool(ok), 'file': str(filename), 'errors': list(task.errors)})
        checkpoint()
    except Exception:
        error('FBX ' + mesh_path)

selected = {
    'german_A': '/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varA',
    'german_B': '/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varB',
    'allied_A': '/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple',
    'allied_B': '/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simpleB',
}
clips = {
    'idle': 'Rifle_Idle', 'walk': 'Rifle_WalkFwdLoop', 'run': 'Rifle_RunFwdLoop',
    'fire': 'Rifle_ShootOnce', 'reload': 'Rifle_Reload_2',
    'hit': 'Rifle_Hit_C_1', 'death': 'Rifle_Death_3',
}
mesh_bones = {a['path']: {b['name']: b['parent'] for b in a.get('bones', [])}
              for a in inventory['assets'] if a.get('class') == 'SkeletalMesh'}
source_bones = mesh_bones.get('/Game/RifleAnimsetPro/UE4_Mannequin/Mesh/SK_Mannequin', {})
for label, mesh_path in selected.items():
    mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
    skeleton = mesh.get_editor_property('skeleton')
    target_bones = mesh_bones.get(mesh_path, {})
    REPORT.setdefault('hierarchy_comparisons', []).append({'mesh': mesh_path,
        'source_bones': len(source_bones), 'target_bones': len(target_bones),
        'missing_source_bones': sorted(set(source_bones) - set(target_bones)),
        'parent_mismatches': [n for n in source_bones if n in target_bones and source_bones[n] != target_bones[n]]})
    for action, clip_name in clips.items():
        try:
            sequence = unreal.EditorAssetLibrary.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/' + clip_name)
            options = unreal.AnimPoseEvaluationOptions()
            options.set_editor_property('optional_skeletal_mesh', mesh)
            options.set_editor_property('evaluation_type', unreal.AnimDataEvalType.COMPRESSED)
            length = unreal.AnimationLibrary.get_sequence_length(sequence)
            samples = []
            for fraction in (0.0, 0.25, 0.5, 0.75, 0.999):
                pose = unreal.AnimPoseExtensions.get_anim_pose_at_time(sequence, length * fraction, options)
                bones = unreal.AnimPoseExtensions.get_bone_names(pose)
                translations = {}
                for name in ('pelvis', 'head', 'hand_l', 'hand_r', 'foot_l', 'foot_r'):
                    t = unreal.AnimPoseExtensions.get_bone_pose(pose, name, unreal.AnimPoseSpaces.WORLD)
                    translations[name] = [t.translation.x, t.translation.y, t.translation.z]
                samples.append({'time': length * fraction, 'evaluated_bones': len(bones),
                                'component_positions_cm': translations})
            REPORT['pose_tests'].append({'mesh': mesh_path, 'action': action,
                'sequence': sequence.get_path_name(), 'samples': samples,
                'limit': 'Compressed editor pose evaluation with target mesh; not a gameplay anim graph or ragdoll test.'})
            checkpoint()
        except Exception:
            error('Pose ' + label + ' ' + action)

# glTF bakes are secondary exchange files, not a replacement for UE materials.
gltf_options = unreal.GLTFExportOptions()
gltf_options.set_editor_property('export_vertex_skin_weights', True)
gltf_options.set_editor_property('export_animation_sequences', True)
gltf_options.set_editor_property('export_morph_targets', True)
gltf_options.set_editor_property('default_level_of_detail', 0)
for label, mesh_path in selected.items():
    try:
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        filename = EXPORTS / (label + '.glb')
        result = unreal.GLTFExporter.export_to_gltf(mesh, str(filename), gltf_options, set())
        REPORT['exports'].append({'asset': mesh_path, 'format': 'GLB',
            'result': str(result), 'file': str(filename), 'exists': filename.exists()})
        checkpoint()
    except Exception:
        error('GLB ' + label)

# Capture the actual engine materials under one fixed studio setup.
try:
    unreal.EditorLevelLibrary.new_level('/Game/ParisCombat/Tests/AssetValidation/MaterialStage')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for location, rotation, intensity in [((250, -180, 270), (-30, -135, 0), 5.0),
                                           ((-200, 170, 180), (-20, 45, 0), 2.0)]:
        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(*location), unreal.Rotator(*rotation))
        comp = light.get_component_by_class(unreal.DirectionalLightComponent)
        comp.set_intensity(intensity)
        comp.set_cast_shadows(False)
    floor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(0, 0, -2))
    floor.static_mesh_component.set_static_mesh(unreal.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Plane'))
    floor.set_actor_scale3d(unreal.Vector(8, 8, 1))
    capture_actor = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(420, 0, 95))
    capture = capture_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property('projection_type', unreal.CameraProjectionMode.ORTHOGRAPHIC)
    capture.set_editor_property('ortho_width', 235.0)
    capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('capture_every_frame', False)
    capture.set_editor_property('capture_on_movement', False)
    target = unreal.RenderingLibrary.create_render_target2d(world, 900, 1000,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0.04, 0.04, 0.04, 1), False)
    capture.set_editor_property('texture_target', target)
    model_actor = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
    model_component = model_actor.get_component_by_class(unreal.SkeletalMeshComponent)
    for label, mesh_path in selected.items():
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        model_component.set_skeletal_mesh_asset(mesh)
        for view, location in [('front', (420, 0, 95)), ('back', (-420, 0, 95)),
                                ('side', (0, 420, 95)), ('three_quarter', (330, 330, 95))]:
            point = unreal.Vector(*location)
            capture_actor.set_actor_location(point, False, False)
            capture_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(point, unreal.Vector(0, 0, 95)), False)
            capture.capture_scene()
            name = label + '_' + view + '.png'
            unreal.RenderingLibrary.export_render_target(world, target, str(OUT), name)
            REPORT['captures'].append({'mesh': mesh_path, 'view': view,
                                      'file': name, 'exists': (OUT / name).exists()})
            checkpoint()
    unreal.EditorLevelLibrary.save_current_level()
except Exception:
    error('UE material capture')
REPORT['finished_at'] = datetime.now().astimezone().isoformat()
checkpoint()
unreal.log('CS549_LAB_VISUAL_DONE')
