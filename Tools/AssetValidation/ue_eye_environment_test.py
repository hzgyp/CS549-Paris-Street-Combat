"""Controlled eye-lighting comparison. No changes to vendor meshes/materials."""
import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
import unreal

LAB = Path(unreal.Paths.project_dir()).resolve()
OUT = LAB / 'Evidence/Repair20261001'
eye_test = os.environ.get('CS549_EYE_MATERIAL_TEST') == '1'
if eye_test:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ue_eye_repair import build_eye_material
report = {'engine': unreal.SystemLibrary.get_engine_version(), 'captures': [], 'errors': []}
selected = {
    'german_A': '/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varA',
    'german_B': '/Game/GermanSoldier/Meshes/SK_WWII_GermanSoldier_varB',
    'allied_A': '/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simple',
    'allied_B': '/Game/USParatrooper/Meshes/SK_WWII_US_Paratrooper_simpleB',
}
try:
    unreal.EditorLevelLibrary.new_level('/Game/ParisCombat/Tests/AssetValidation/EyeEnvironment_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for rotation, intensity in [((-30, -135, 0), 20.0), ((-20, 45, 0), 8.0)]:
        actor = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 300), unreal.Rotator(*rotation))
        light = actor.get_component_by_class(unreal.DirectionalLightComponent)
        light.set_intensity(intensity)
        light.set_cast_shadows(False)
    sky = actors.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(0, 0, 300))
    sky_component = sky.get_component_by_class(unreal.SkyLightComponent)
    sky_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    sky_component.set_editor_property('source_type', unreal.SkyLightSourceType.SLS_SPECIFIED_CUBEMAP)
    sky_component.set_cubemap(unreal.load_asset('/Engine/MapTemplates/Sky/DaylightAmbientCubemap'))
    sky_component.set_intensity(1.0)
    sky_component.recapture_sky()
    # One fixed perspective camera; every variant gets its own newly registered component.
    capture_actor = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(180, 220, 162))
    capture = capture_actor.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property('projection_type', unreal.CameraProjectionMode.PERSPECTIVE)
    capture.set_editor_property('fov_angle', 12.5)
    capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('capture_every_frame', False)
    capture.set_editor_property('capture_on_movement', False)
    capture_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(capture_actor.get_actor_location(), unreal.Vector(0, 0, 162)), False)
    target = unreal.RenderingLibrary.create_render_target2d(world, 900, 1000,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.04, .04, .04, 1), False)
    capture.set_editor_property('texture_target', target)
    loaded = {label: unreal.load_asset(path) for label, path in selected.items()}
    replacements = {faction: build_eye_material(faction) for faction in ('German', 'Allied')} if eye_test else {}
    unreal.AutomationLibrary.finish_loading_before_screenshot()
    for label, mesh in loaded.items():
        model = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, 0, 0))
        component = model.get_component_by_class(unreal.SkeletalMeshComponent)
        component.set_skeletal_mesh_asset(mesh)
        conditions = [('legacy_daylight', 1.0), ('pbr_daylight', 1.0), ('pbr_low_light', 1.0)] if eye_test else [('no_sky', 0.0), ('daylight_sky', 1.0)]
        for condition, intensity in conditions:
            if condition.startswith('pbr'):
                for n, slot in enumerate(mesh.get_editor_property('materials')):
                    if slot.material_interface and 'eye' in slot.material_interface.get_path_name().lower():
                        component.set_material(n, replacements['German' if label.startswith('german') else 'Allied'])
            if eye_test:
                for actor in actors.get_all_level_actors():
                    if isinstance(actor, unreal.DirectionalLight):
                        actor.get_component_by_class(unreal.DirectionalLightComponent).set_intensity(1.0 if condition == 'pbr_low_light' else 20.0)
            sky_component.set_intensity(intensity)
            sky_component.recapture_sky()
            unreal.AutomationLibrary.finish_loading_before_screenshot()
            for view, location in [('three_quarter', (180, 220, 162)), ('front', (0, 280, 162))]:
                point = unreal.Vector(*location)
                capture_actor.set_actor_location(point, False, False)
                capture_actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(point, unreal.Vector(0, 0, 162)), False)
                capture.capture_scene()
                filename = label + '_' + condition + '_' + view + '.png'
                unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
                report['captures'].append({'label': label, 'condition': condition, 'view': view, 'file': filename,
                    'size_bytes': (OUT / filename).stat().st_size})
        actors.destroy_actor(model)
except Exception:
    report['errors'].append(traceback.format_exc())
(OUT / ('eye_material_test.json' if eye_test else 'eye_environment_test.json')).write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_EYE_ENVIRONMENT_DONE')
