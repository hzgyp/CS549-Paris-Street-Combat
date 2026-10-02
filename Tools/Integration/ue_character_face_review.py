"""Unsaved reference-pose lighting diagnostic; preserves prior dark captures."""
import json
import traceback
from datetime import datetime
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
OUT = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1/Evidence/P2/HeadReview'
OUT.mkdir(parents=True, exist_ok=True)
report = {'started_at': datetime.now().astimezone().isoformat(),
    'engine': unreal.SystemLibrary.get_engine_version(), 'captures': [], 'errors': [],
    'scope': 'Reference-pose material diagnostic, shadowless controlled fill; not city daylight/shadow, facial animation or gameplay acceptance; no package saves'}
try:
    if not unreal.EditorLevelLibrary.load_level('/Game/ParisCombat/Tests/Integration/P2_CharacterPreview_20261001'):
        raise RuntimeError('Saved preview missing')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    # Diagnosis distinguishes a dark capture from missing skin/eye textures.
    for actor in actors.get_all_level_actors():
        if isinstance(actor, unreal.DirectionalLight):
            actor.get_component_by_class(unreal.DirectionalLightComponent).set_cast_shadows(False)
    for rotation in [(-20, 90, 0), (-20, -90, 0)]:
        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, -1200, 300), unreal.Rotator(*rotation))
        component = light.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_intensity(6)
        component.set_cast_shadows(False)
    camera = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector(0, -900, 165))
    capture = camera.get_component_by_class(unreal.SceneCaptureComponent2D)
    capture.set_editor_property('capture_source', unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR)
    capture.set_editor_property('capture_every_frame', False)
    capture.set_editor_property('capture_on_movement', False)
    capture.set_editor_property('fov_angle', 20)
    target = unreal.RenderingLibrary.create_render_target2d(world, 1200, 1000,
        unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(.04, .04, .04, 1), False)
    capture.set_editor_property('texture_target', target)
    for label, name in {
        'allied_A': 'SK_WWII_US_Paratrooper_simple_UE582_v1',
        'allied_B': 'SK_WWII_US_Paratrooper_simpleB_UE582_v1',
        'german_A': 'SK_WWII_GermanSoldier_varA_UE582_v1',
        'german_B': 'SK_WWII_GermanSoldier_varB_UE582_v1',
    }.items():
        model = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0, -1200, 0))
        component = model.get_component_by_class(unreal.SkeletalMeshComponent)
        mesh = unreal.load_asset('/Game/ParisCombat/Characters/Adaptation/Meshes/' + name)
        component.set_skeletal_mesh_asset(mesh)
        unreal.AutomationLibrary.finish_loading_before_screenshot()
        head = component.get_bone_transform('head', unreal.RelativeTransformSpace.RTS_WORLD).translation
        for view, offset in [('front', (0, 300, 5)), ('three_quarter', (170, 260, 5))]:
            loc = head + unreal.Vector(*offset)
            camera.set_actor_location(loc, False, False)
            camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(loc, head), False)
            capture.capture_scene()
            filename = label + '_' + view + '.png'
            unreal.RenderingLibrary.export_render_target(world, target, str(OUT), filename)
            report['captures'].append({'mesh': mesh.get_path_name(), 'file': filename, 'exists': (OUT / filename).exists()})
        actors.destroy_actor(model)
    # Deliberately do not save: original scene/character bytes remain unchanged.
except Exception:
    report['errors'].append(traceback.format_exc())
report['finished_at'] = datetime.now().astimezone().isoformat()
report['result'] = 'captured_pending_review' if not report['errors'] else 'fail'
(OUT / 'face_review.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
unreal.log('CS549_FACE_REVIEW_DONE ' + report['result'])
if report['errors']:
    raise RuntimeError('Read face_review.json for actual errors')
