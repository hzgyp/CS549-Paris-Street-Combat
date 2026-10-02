"""UMG and actual-city Fire integration after the guarded shared-shot author."""
import hashlib
import json
import os
import sys
import traceback
from pathlib import Path
import unreal

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ue_paris_graph_helpers import lib, pins, wire, pin, value, place, call, pure, get, run, cast_to

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/Setup'
IDENTITY = os.environ.get('CS549_HUD_AUTHOR_IDENTITY', 'hud_author_v1')
assert IDENTITY.replace('_', '').isalnum()
DEST = OUT / (IDENTITY + '.json')
assert not DEST.exists()
BASE = '/Game/ParisCombat/Blueprints/CityGameplayV1/BP_PCParisCombatantV2'
WIDGET = '/Game/ParisCombat/UI/CityGameplayV1/WBP_PCParisStatusV1'
PREFIX = '/Game/ParisCombat/Blueprints/CityGameplayV1/'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
inventory = json.loads((ROOT / 'Assets/Integration/CITY_GAMEPLAY_DRAFT_INVENTORY_20261002.json').read_text())
old = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
shot = json.loads((OUT / 'combat_author_v1.json').read_text())
assert shot['status'] == 'saved_shared_shot_blueprint_only_follow_on_pending'
recovery = json.loads((OUT / 'hud_author_v4.json').read_text())
assert IDENTITY == 'hud_author_v6' and recovery['status'] == 'failed_preserve_task_drafts'
assert recovery['assets'] == [BASE, WIDGET] and recovery['previous_28_drafts_unchanged']
report = {'scope': 'Native UMG/Fire/appearance-reference integration, not runtime or mission acceptance',
          'assets': [], 'defaults': [], 'errors': []}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def checkpoint():
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')


def save(bp, path):
    assert lib.compile_blueprint(bp), 'Compile failed: ' + path
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False)
    report['assets'].append(path)
    checkpoint()


def join(g, a, b):
    return pure(g, '/Script/Engine.KismetStringLibrary.Concat_StrStr', A=a, B=b)


try:
    for f in inventory['files'] + old['files'] + recovery['saved_files']:
        assert digest(ROOT / f['path']) == f['sha256'], 'Unsynchronized draft: ' + f['path']
    assert unreal.EditorAssetLibrary.does_asset_exist(WIDGET)
    shared = unreal.load_asset(BASE)
    # Retain the successfully saved shared Blueprint from the exact failed-v1 bytes.
    report['assets'].append(BASE)
    shared_class = unreal.EditorAssetLibrary.load_blueprint_class(BASE)
    # Successful v4 widget remains byte-for-byte unchanged. Original new-only
    # graph source is retained as build_new_status_widget in the helpers module.
    widget = unreal.load_asset(WIDGET)
    report['assets'].append(WIDGET)
    widget_class = unreal.EditorAssetLibrary.load_blueprint_class(WIDGET)
    # Capture defaults before reparenting only the three task-owned city children.
    children = []
    for name in ('BP_PCParisPlayerV1', 'BP_PCParisAlliedNPCV1', 'BP_PCParisGermanNPCV1'):
        path = PREFIX + name
        child = unreal.load_asset(path)
        cdo = unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(path))
        mesh = cdo.get_component_by_class(unreal.SkeletalMeshComponent)
        capsule = cdo.get_component_by_class(unreal.CapsuleComponent)
        children.append((path, child, mesh.get_skeletal_mesh_asset(), mesh.get_editor_property('anim_class'),
                         cdo.get_editor_property('TeamId'), cdo.get_editor_property('RoleId'), cdo.get_editor_property('auto_possess_player'),
                         capsule.get_unscaled_capsule_radius(), capsule.get_unscaled_capsule_half_height(),
                         mesh.get_editor_property('relative_location'), mesh.get_editor_property('relative_rotation'),
                         mesh.get_editor_property('relative_scale3d')))
    for path, child, mesh_asset, anim_class, team, role, possession, radius, half, mesh_location, mesh_rotation, mesh_scale in children:
        lib.reparent_blueprint(child, shared_class)
        assert lib.compile_blueprint(child)
        cdo = unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(path))
        mesh = cdo.get_component_by_class(unreal.SkeletalMeshComponent)
        mesh.set_skeletal_mesh_asset(mesh_asset)
        mesh.set_anim_instance_class(anim_class)
        mesh.set_editor_property('relative_location', mesh_location)
        mesh.set_editor_property('relative_rotation', mesh_rotation)
        mesh.set_editor_property('relative_scale3d', mesh_scale)
        cdo.set_editor_property('TeamId', team)
        cdo.set_editor_property('RoleId', role)
        cdo.set_editor_property('auto_possess_player', possession)
        capsule = cdo.get_component_by_class(unreal.CapsuleComponent)
        capsule.set_capsule_size(radius, half)
        capsule.set_collision_response_to_channel(
            unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_BLOCK)
        report['defaults'].append({'package': path, 'mesh': mesh_asset.get_path_name(),
            'anim_class': anim_class.get_path_name(), 'team': team, 'role': str(role), 'possession': str(possession),
            'capsule_radius_cm': radius, 'capsule_half_height_cm': half,
            'mesh_offset_cm': [mesh_location.x, mesh_location.y, mesh_location.z]})
        if path.endswith('BP_PCParisPlayerV1'):
            fire = unreal.BlueprintGraphEditor.create_and_edit_function_graph(child, 'PC_PlayerFire')
            camera = get(fire, 'ParisPlayerCamera')
            origin = pure(fire, '/Script/Engine.SceneComponent.K2_GetComponentLocation', self=camera)
            direction = pure(fire, '/Script/Engine.SceneComponent.GetForwardVector', self=camera)
            run(fire, fire.find_graph_entry_pin(), call(fire, 'PC_RequestFire', AimOrigin=origin, AimDirection=direction))
            graph = unreal.BlueprintGraphEditor.get_graph_editor_by_name(child, 'EventGraph')
            event = graph.create_node_from_name('Input|ActionEvents|PC_Fire', unreal.Vector2D(0, 1500), [])
            assert event
            run(graph, pin(event, 'Pressed', True), call(graph, 'PC_PlayerFire'))
            begin = graph.find_event_node('ReceiveBeginPlay') or lib.add_event_override(child, 'ReceiveBeginPlay', unreal.IntPoint(0, 1800))
            assert begin
            create = place(graph.create_node_from_name('UserInterface|CreateWidget', unreal.Vector2D(400, 1800), []))
            value(pin(create, 'Class'), widget_class.get_path_name())
            owner = pure(graph, '/Script/Engine.GameplayStatics.GetPlayerController', PlayerIndex=0)
            value(pin(create, 'OwningPlayer'), owner)
            created = run(graph, lib.find_then_pin(begin), create)
            add = call(graph, '/Script/UMG.UserWidget.AddToViewport', ZOrder=0)
            wire(pin(create, 'ReturnValue', True), lib.find_self_pin(add))
            run(graph, created, add)
        save(child, path)
    assert unreal.EditorLevelLibrary.load_level(ENTRY)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level_editor.set_current_level_by_name(unreal.Name(ENTRY.rsplit('/', 1)[1]))
    weapons = [a for a in actors if a.get_actor_label().startswith('PC_M1_Appearance_')]
    assert len(weapons) == 3
    for weapon in weapons:
        owner = weapon.get_owner()
        assert owner and owner.get_actor_label().startswith('PC_City_')
        owner.set_editor_property('WeaponAppearance', weapon)
    assert len([a for a in actors if a.get_actor_label().startswith('PC_City_')]) == 6
    for actor in actors:
        if actor.get_actor_label().startswith('PC_City_'):
            actor.get_component_by_class(unreal.CapsuleComponent).set_collision_response_to_channel(
                unreal.CollisionChannel.ECC_VISIBILITY, unreal.CollisionResponseType.ECR_BLOCK)
    assert unreal.EditorLevelLibrary.save_current_level()
    report['assets'].append(ENTRY)
    report['status'] = 'saved_actual_city_fire_and_umg_not_runtime_acceptance'
except Exception:
    report['status'] = 'failed_preserve_task_drafts'
    report['errors'].append(traceback.format_exc())
finally:
    report['previous_28_drafts_unchanged'] = all(digest(ROOT / f['path']) == f['sha256'] for f in old['files'])
    report['saved_files'] = []
    for package in report['assets']:
        file = STORE / 'Content' / (package.removeprefix('/Game/') + ('.umap' if package == ENTRY else '.uasset'))
        report['saved_files'].append({'package': package, 'path': file.relative_to(ROOT).as_posix(),
                                     'size_bytes': file.stat().st_size, 'sha256': digest(file)})
    checkpoint()
unreal.log('CS549_HUD_AUTHOR ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved HUD/input author evidence')
