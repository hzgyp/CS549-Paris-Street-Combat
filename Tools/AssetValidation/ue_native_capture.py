"""Actual UE material capture only; avoids optional lossy glTF material bakes."""
import json
import os
import traceback
from datetime import datetime
from pathlib import Path
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence'
repair_mode = os.environ.get('CS549_NATIVE_REPAIR_REGRESSION') == '1'
if repair_mode:
    OUT = LAB / 'Evidence/Repair20261001/FinalNativeCaptures'
    OUT.mkdir(parents=True, exist_ok=True)
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'captures': [], 'errors': [],
          'started_at': datetime.now().astimezone().isoformat()}
selected = {
    'german_A': '/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varA',
    'german_B': '/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varB',
    'allied_A': '/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple',
    'allied_B': '/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simpleB',
}
if repair_mode:
    selected = {label: '/Game/ParisCombat/Characters/Adaptation/Meshes/' + path.split('/')[-1] + '_UE582_v1'
                for label, path in selected.items()}


def save():
    (OUT / 'ue_native_captures.json').write_text(json.dumps(report, indent=2), encoding='utf-8')


save()
try:
    stage_path = '/Game/ParisCombat/Tests/AssetValidation/MaterialStage_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    report['stage_path'] = stage_path
    if not unreal.EditorLevelLibrary.new_level(stage_path):
        raise RuntimeError('Could not create unique isolated material stage')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for rotation, intensity in [((-30, -135, 0), 20.0), ((-20, 45, 0), 8.0)]:
        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 300), unreal.Rotator(*rotation))
        component = light.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_intensity(intensity)
        component.set_cast_shadows(False)
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
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.04, .04, .04, 1), False)
    capture.set_editor_property('texture_target', target)
    model = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
    component = model.get_component_by_class(unreal.SkeletalMeshComponent)
    loaded = {label: unreal.EditorAssetLibrary.load_asset(path) for label, path in selected.items()}
    # Native function finishes asset/shader compilation and streams texture mips.
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    for label, path in selected.items():
        component.set_skeletal_mesh_asset(loaded[label])
        for view, location in [('front', (0, 420, 95)), ('back', (0, -420, 95)),
                                ('side', (420, 0, 95)), ('three_quarter', (330, 330, 95))]:
            point = unreal.Vector(*location)
            capture_actor.set_actor_location(point, False, False)
            capture_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(point, unreal.Vector(0, 0, 95)), False)
            capture.capture_scene()
            filename = f'{label}_{view}.png'
            unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
            report['captures'].append({'mesh': path, 'view': view, 'file': filename,
                                       'exists': (OUT / filename).exists()})
            save()
        # Separate full-resolution face/material evidence, not a beauty render.
        capture.set_editor_property('ortho_width', 68.0)
        point = unreal.Vector(220, 220, 162)
        capture_actor.set_actor_location(point, False, False)
        capture_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(point, unreal.Vector(0, 0, 162)), False)
        capture.capture_scene()
        filename = label + '_head.png'
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
        report['captures'].append({'mesh': path, 'view': 'head', 'file': filename, 'exists': (OUT / filename).exists()})
        capture.set_editor_property('projection_type', unreal.CameraProjectionMode.PERSPECTIVE)
        capture.set_editor_property('fov_angle', 12.5)
        capture.capture_scene()
        filename = label + '_head_perspective.png'
        unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
        report['captures'].append({'mesh': path, 'view': 'head_perspective', 'file': filename,
                                   'exists': (OUT / filename).exists()})
        capture.set_editor_property('projection_type', unreal.CameraProjectionMode.ORTHOGRAPHIC)
        capture.set_editor_property('ortho_width', 235.0)
    unreal.EditorLevelLibrary.save_current_level()
except Exception:
    report['errors'].append(traceback.format_exc())
report['finished_at'] = datetime.now().astimezone().isoformat()
save()
unreal.log('CS549_NATIVE_CAPTURE_DONE')
