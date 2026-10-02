"""New-only actual-city setup using existing characters/motions and vendor sublevels."""
import hashlib
import json
import os
import traceback
from datetime import datetime
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/CityGameplay20261002/Setup'
IDENTITY = os.environ.get('CS549_CITY_SETUP_IDENTITY', 'author_v4')
assert IDENTITY.replace('_', '').isalnum()
DEST = OUT / (IDENTITY + '.json')
assert not DEST.exists(), 'Preserve occupied author evidence'
OUT.mkdir(parents=True, exist_ok=True)
ORIGINAL = '/Game/WW2City/Maps/LV_Paris_WW2'
ENTRY = '/Game/ParisCombat/Maps/LV_ParisStreetCombat_V1'
PREFIX = '/Game/ParisCombat/Blueprints/CityGameplayV1/'
NAMES = ('BP_PCParisPlayerV1', 'BP_PCParisAlliedNPCV1', 'BP_PCParisGermanNPCV1', 'BP_PCParisGameModeV1')
PATHS = [PREFIX + name for name in NAMES] + [ENTRY]
recovery = json.loads((OUT / 'author_v3.json').read_text(encoding='utf-8'))
assert IDENTITY == 'author_v4' and recovery['status'] == 'failed_preserve_new_drafts'
assert recovery['original_ten_map_hashes_unchanged'] and recovery['previous_28_drafts_unchanged']
recover_files = recovery['saved_files']
recover_packages = {f['package'] for f in recover_files}
assert set(PATHS) == recover_packages and unreal.EditorAssetLibrary.does_asset_exist(ENTRY)
for f in recover_files:
    file = ROOT / f['path']
    assert file.stat().st_size == f['size_bytes'] and hashlib.sha256(file.read_bytes()).hexdigest() == f['sha256'], 'Refuse altered partial draft'
snapshot = json.loads((ROOT / 'Assets/Integration/RELOAD_DRAFT_SNAPSHOT_20261002.json').read_text(encoding='utf-8-sig'))
report = {'started_at': datetime.now().astimezone().isoformat(), 'engine': unreal.SystemLibrary.get_engine_version(),
          'scope': 'Actual Paris asset/setup drafts only; not input/shots/HUD/AI/mission/package or FP acceptance',
          'assets': [], 'roster': [], 'weapons': [], 'errors': []}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def xyz(v):
    return [v.x, v.y, v.z]


def checkpoint():
    DEST.write_text(json.dumps(report, indent=2), encoding='utf-8')


def save_new(bp, path):
    assert unreal.BlueprintEditorLibrary.compile_blueprint(bp), 'Compile failed: ' + path
    assert unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False), 'Save failed: ' + path
    report['assets'].append(path)
    checkpoint()


def make_child(path, parent):
    if path in recover_packages:
        bp = unreal.load_asset(path)
        assert bp, 'Recorded partial draft missing'
        if unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp) != parent:
            unreal.BlueprintEditorLibrary.reparent_blueprint(bp, parent)
    else:
        assert not unreal.EditorAssetLibrary.does_asset_exist(path)
        bp = unreal.BlueprintEditorLibrary.create_blueprint_asset_with_parent(path, parent)
    assert bp and unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    return bp


def add_camera(bp):
    sub = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary
    handles = sub.k2_gather_subobject_data_for_blueprint(bp)
    report['subobjects'] = []
    capsule_handle = None
    for handle in handles:
        data = lib.get_data(handle)
        obj = lib.get_object_for_blueprint(data, bp)
        report['subobjects'].append({'name': str(lib.get_variable_name(data)), 'class': obj.get_class().get_name() if obj else None})
        if isinstance(obj, unreal.CapsuleComponent):
            capsule_handle = handle
        if isinstance(obj, unreal.CameraComponent) and str(lib.get_variable_name(data)) == 'ParisPlayerCamera':
            report['retained_team_camera'] = True
    if report.get('retained_team_camera'):
        assert sum(s['class'] == 'CameraComponent' for s in report['subobjects']) == 1, 'Inherited diagnostic camera remains'
        return
    assert capsule_handle, 'Inherited capsule handle missing'
    handle, reason = sub.add_new_subobject(unreal.AddNewSubobjectParams(
        parent_handle=capsule_handle, new_class=unreal.CameraComponent, blueprint_context=bp))
    assert lib.is_handle_valid(handle), str(reason)
    assert sub.rename_subobject(handle, unreal.Text('ParisPlayerCamera'))
    camera = lib.get_object_for_blueprint(lib.get_data(handle), bp)
    camera.set_editor_property('relative_location', unreal.Vector(25, 0, 60))
    camera.set_editor_property('use_pawn_control_rotation', True)
    camera.set_editor_property('field_of_view', 90)


original_files = [STORE / 'Content/WW2City/Maps' / name for name in (
    'LV_Paris_WW2.umap', 'LV_Lighting_Day.umap', 'LV_Lighting_Midnight.umap', 'LV_Lighting_WarFog.umap',
    'LV_NewsetDressing.umap', 'LV_SplineRoads.umap', 'LV_Proxy.umap', 'LV_StructureAsset.umap',
    'LV_VFX.umap', 'LV_Powerline.umap')]
original_hashes = {p: digest(p) for p in original_files}
try:
    assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
    survey = json.loads((STORE / 'Evidence/CityGameplay20261002/Survey/structure_v3.json').read_text(encoding='utf-8'))
    assert survey['status'] == 'pass_readonly_inventory_ground_queries_only'
    assert survey['map_unchanged'] and survey['previous_28_drafts_unchanged']
    for item in snapshot['files']:
        assert digest(ROOT / item['path']) == item['sha256'], item['path']
    start = survey['player_starts'][0]['location_cm']
    anchors = [('Player', 0, 0, -2000), ('Ally1', 1, -140, -2300), ('Ally2', 1, 140, -2600),
               ('Enemy1', 2, -140, -1250), ('Enemy2', 2, 140, -1100), ('Enemy3', 2, 0, -1550)]
    assert unreal.EditorLevelLibrary.load_level(ENTRY)
    original_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    report['placement_preflight'] = []
    for label, kind, dx, dy in anchors:
        hit = unreal.SystemLibrary.line_trace_single(original_world,
            unreal.Vector(start[0] + dx, start[1] + dy, 500),
            unreal.Vector(start[0] + dx, start[1] + dy, -2000),
            unreal.TraceTypeQuery.ECC_VISIBILITY, False, [], unreal.DrawDebugTrace.NONE, True)
        assert hit, 'No preflight surface: ' + label
        values = hit.to_tuple()
        assert values[0] and values[7].z >= .85 and 'Road' in values[9].get_actor_label(), 'Unaccepted preflight surface: ' + label
        report['placement_preflight'].append({'label': label, 'ground_actor': values[9].get_actor_label(),
                                              'ground_z_cm': values[5].z})
    checkpoint()
    old_prefix = '/Game/ParisCombat/Blueprints/Characters/SimplifiedReloadDraft/'
    allied_parent = unreal.EditorAssetLibrary.load_blueprint_class(old_prefix + 'BP_PCCombatantReloadV1')
    german_parent = unreal.EditorAssetLibrary.load_blueprint_class(old_prefix + 'BP_PCNPCReloadV1')
    assert allied_parent and german_parent
    for index, name in enumerate(NAMES[:3]):
        bp = unreal.load_asset(PREFIX + name)
        assert bp and unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp) == (allied_parent if index < 2 else german_parent)
        defaults = unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(PREFIX + name))
        assert defaults.get_editor_property('auto_possess_player') == (unreal.AutoReceiveInput.PLAYER0 if index == 0 else unreal.AutoReceiveInput.DISABLED)
        assert defaults.get_editor_property('TeamId') == (0 if index < 2 else 1)
        assert str(defaults.get_editor_property('RoleId')) == ('Player', 'Ally', 'Enemy')[index]
    assert unreal.get_default_object(unreal.EditorAssetLibrary.load_blueprint_class(PREFIX + NAMES[3])).get_editor_property('default_pawn_class') is None
    report['assets'] = list(PATHS)
    report['recovery_from'] = 'author_v3.json; preserve saved entry/Blueprints; only failed unsaved roster was discarded'
    checkpoint()
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert not any(a.get_actor_label().startswith(('PC_City_', 'PC_M1_Appearance_')) for a in actors.get_all_level_actors()), 'Refuse occupied roster'
    report['removed_lighting_references'] = []
    for level in list(unreal.EditorLevelUtils.get_levels(world)):
        package = level.get_outer().get_path_name()
        if any(k in package for k in ('LV_Lighting_Midnight', 'LV_Lighting_WarFog')):
            assert unreal.EditorLevelUtils.remove_level_from_world(level), 'Cannot remove extra light layer'
            report['removed_lighting_references'].append(package)
    levels = list(unreal.EditorLevelUtils.get_levels(world))
    root_level = next(l for l in levels if l.get_outer().get_path_name().startswith(ENTRY + '.'))
    level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    assert level_editor.set_current_level_by_name(unreal.Name(ENTRY.rsplit('/', 1)[1])), 'Cannot select team persistent level'
    assert level_editor.get_current_level() == root_level
    # EditorActorSubsystem deliberately omits some editor-hidden utility actors.
    # GameplayStatics includes WorldSettings; select only the new persistent level.
    settings = next(a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.WorldSettings)
                    if a.get_outer() == root_level)
    settings.set_editor_property('default_game_mode', unreal.EditorAssetLibrary.load_blueprint_class(PREFIX + NAMES[3]))
    idle = unreal.load_asset('/Game/RifleAnimsetPro/Animations/InPlace/Rifle_Idle')
    rifle = unreal.load_asset('/Game/USParatrooper/Meshes/Weapon/Sm_M1_Garand')
    assert idle and rifle
    for label, kind, dx, dy in anchors:
        cls = unreal.EditorAssetLibrary.load_blueprint_class(PREFIX + NAMES[kind])
        capsule = unreal.get_default_object(cls).get_editor_property('capsule_component')
        x, y = start[0] + dx, start[1] + dy
        hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 500), unreal.Vector(x, y, -2000),
            unreal.TraceTypeQuery.ECC_VISIBILITY, False, [], unreal.DrawDebugTrace.NONE, True)
        assert hit, 'No placement surface: ' + label
        values = hit.to_tuple()
        assert values[0] and values[7].z >= .85 and 'Road' in values[9].get_actor_label(), 'Unaccepted placement surface: ' + label
        location = unreal.Vector(x, y, values[5].z + capsule.get_unscaled_capsule_half_height() + 3)
        actor = actors.spawn_actor_from_class(cls, location, unreal.Rotator(yaw=0 if kind < 2 else 180))
        assert actor.get_outer() == root_level, 'Character spawned into vendor level'
        actor.set_actor_label('PC_City_' + label)
        actor.set_editor_property('tags', [unreal.Name('ParisCombat'), unreal.Name(label)])
        mesh = actor.get_component_by_class(unreal.SkeletalMeshComponent)
        mesh.set_update_animation_in_editor(True)
        report['roster'].append({'label': actor.get_actor_label(), 'class': cls.get_path_name(),
                                 'location_cm': xyz(location), 'mesh': mesh.get_skeletal_mesh_asset().get_path_name(),
                                 'anim_class': mesh.get_editor_property('anim_class').get_path_name(),
                                 'ground_actor': values[9].get_actor_label(), 'ground_z_cm': values[5].z})
        if kind < 2:
            animation_class = mesh.get_editor_property('anim_class')
            mesh.override_animation_data(idle, False, False, 0, 1)
            hand = mesh.get_socket_transform('hand_r', unreal.RelativeTransformSpace.RTS_WORLD)
            weapon = actors.spawn_actor_from_class(unreal.StaticMeshActor, hand.translation,
                unreal.Rotator(yaw=actor.get_actor_rotation().yaw - 90))
            assert weapon.get_outer() == root_level
            weapon.set_actor_label('PC_M1_Appearance_' + label)
            weapon.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            weapon.static_mesh_component.set_static_mesh(rifle)
            weapon.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            assert weapon.attach_to_component(mesh, 'hand_r', unreal.AttachmentRule.KEEP_WORLD,
                unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
            weapon.set_owner(actor)
            mesh.set_animation_mode(unreal.AnimationMode.ANIMATION_BLUEPRINT)
            mesh.set_anim_instance_class(animation_class)
            report['weapons'].append({'actor': weapon.get_actor_label(), 'owner': label, 'mesh': rifle.get_path_name(),
                                      'attachment_bone': 'hand_r', 'status': 'provisional appearance; grip/FP/reload/contact not accepted'})
        checkpoint()
    assert len(report['roster']) == 6 and len(report['weapons']) == 3
    assert unreal.EditorLevelLibrary.save_current_level(), 'Team entry save failed'
    report['loaded_levels'] = [l.get_outer().get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)]
    report['status'] = 'saved_asset_backed_city_setup_not_gameplay_acceptance'
except Exception:
    report['errors'].append(traceback.format_exc())
    report['status'] = 'failed_preserve_new_drafts'
finally:
    report['original_ten_map_hashes_unchanged'] = all(digest(p) == h for p, h in original_hashes.items())
    report['previous_28_drafts_unchanged'] = all(digest(ROOT / item['path']) == item['sha256'] for item in snapshot['files'])
    if not report['original_ten_map_hashes_unchanged'] or not report['previous_28_drafts_unchanged']:
        report['errors'].append('Unexpected original/previous-draft byte changes')
        report['status'] = 'failed_preserve_new_drafts'
    for package in report['assets']:
        file = STORE / 'Content' / (package.removeprefix('/Game/') + ('.umap' if package == ENTRY else '.uasset'))
        if file.is_file():
            report.setdefault('saved_files', []).append({'package': package, 'path': file.relative_to(ROOT).as_posix(),
                'size_bytes': file.stat().st_size, 'sha256': digest(file)})
    report['finished_at'] = datetime.now().astimezone().isoformat()
    checkpoint()
unreal.log('CS549_CITY_SETUP ' + report['status'])
if report['errors']:
    raise RuntimeError('Read preserved setup report before hash-guarded recovery')
