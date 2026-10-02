"""New movement/locomotion draft only; refuses existing output packages."""
import json
import hashlib
import traceback
from datetime import datetime
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
assert Path(unreal.Paths.project_dir()).resolve() == (ROOT / 'Unreal/ParisStreetCombat').resolve()
STORE = ROOT / 'Assets/LocalShared/SFTP/workspaces/yg745/paris-gameplay-v1'
OUT = STORE / 'Evidence/P2/Movement'
OUT.mkdir(parents=True, exist_ok=True)
MAP = '/Game/ParisCombat/Tests/Integration/P2_CharacterMovement_20261001'
BP = '/Game/ParisCombat/Blueprints/Characters/'
ANIM = '/Game/ParisCombat/Animation/LocomotionDraft/'
MESH = '/Game/ParisCombat/Characters/Adaptation/Meshes/'
VARIANTS = {
    'allied_A': 'SK_WWII_US_Paratrooper_simple_UE582_v1',
    'allied_B': 'SK_WWII_US_Paratrooper_simpleB_UE582_v1',
    'german_A': 'SK_WWII_GermanSoldier_varA_UE582_v1',
    'german_B': 'SK_WWII_GermanSoldier_varB_UE582_v1',
}
REPORT = {'started_at': datetime.now().astimezone().isoformat(), 'errors': [],
          'engine': unreal.SystemLibrary.get_engine_version(), 'map': MAP, 'actors': [],
          'scope': 'Blueprint Character shell and velocity-driven locomotion draft; no health/death, action transaction, weapon, AI, city contact or packaged acceptance'}


def checkpoint():
    (OUT / 'authoring.json').write_text(json.dumps(REPORT, indent=2), encoding='utf-8')


RESUME = '-ParisResumeMovementDraft' in unreal.SystemLibrary.get_command_line()
previous = json.loads((OUT / 'authoring.json').read_text(encoding='utf-8')) if RESUME else None
if previous:
    REPORT['previous_attempt'] = previous
checkpoint()
try:
    if RESUME:
        # Bounded recovery of this task's first failure, not a general overwrite mode.
        expected = {
            'Blueprints/Characters/BP_PCCombatantBase.uasset': '9062088dd8855cf6215bcb8fd15b980328971710685086c9c4dcbcf3707f6604',
            'Blueprints/Characters/BP_PCNPC.uasset': '19f863ec120ee1d520115d5bc3c09463e0826d8dc0801f4de2ddf194f8241725',
            'Blueprints/Characters/BP_PCPlayer.uasset': 'ebc55f531d6b332eb61a0cd41fe10543b578f023bc5635ad4cce91357308417b',
            'Animation/LocomotionDraft/ABP_PC_Allied.uasset': '7631d3ec637965d31ec52a24b0cb349a93d056d09d8eb579158a3d7cdfba6dc8',
            'Animation/LocomotionDraft/ABP_PC_German.uasset': '07190647d39135767352070737f5dde88f7ba7de464493b7148264f4b5688a77',
            'Animation/LocomotionDraft/BS_PC_Allied.uasset': '1f7dfb8e67cbb9f36800b879c8853b8a1e6cdf76260aa8e922873710a42058ba',
            'Animation/LocomotionDraft/BS_PC_German.uasset': 'ae17b16dc1c205ffaad37baa615b7b2f2e955c6ccc0540b59c1bb80d1b832563',
            'Tests/Integration/P2_CharacterMovement_20261001.umap': 'ccb71f830734accbfc472edbaeccaf6933bf4059708682a87562a7baf6da815f',
        }
        if not previous or previous.get('result') != 'fail_preserved_drafts' or len(previous['actors']) != 0:
            raise RuntimeError('Resume checkpoint is not the initial empty-scene failure')
        for relative, sha in expected.items():
            path = STORE / 'Content/ParisCombat' / relative
            if hashlib.sha256(path.read_bytes()).hexdigest() != sha:
                raise RuntimeError('Unique asset edits detected; refusing recovery: ' + relative)
        REPORT['verified_resume_hashes'] = expected
        REPORT['bridge'] = previous['bridge']
        base = unreal.load_asset(BP + 'BP_PCCombatantBase')
        for variable in ('TeamId', 'RoleId'):
            unreal.BlueprintEditorLibrary.set_blueprint_variable_instance_editable(base, variable, True)
        unreal.BlueprintEditorLibrary.compile_blueprint(base)
        for name in ('BP_PCPlayer', 'BP_PCNPC'):
            unreal.BlueprintEditorLibrary.compile_blueprint(unreal.load_asset(BP + name))
    elif unreal.EditorAssetLibrary.does_asset_exist(MAP):
        raise RuntimeError('Refusing existing movement map; retain drafts and choose a new task identity')
    else:
        REPORT['bridge'] = json.loads(unreal.ParisBlueprintAuthoring.create_movement_draft())
    if 'error' in REPORT['bridge']:
        raise RuntimeError(REPORT['bridge']['error'])
    checkpoint()
    for path in REPORT['bridge']['assets']:
        asset = unreal.load_asset(path)
        if not asset or not unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False):
            raise RuntimeError('Save failed: ' + path)
    if RESUME:
        if not unreal.EditorLevelLibrary.load_level(MAP):
            raise RuntimeError('Cannot load known empty failed scene')
    elif not unreal.EditorLevelLibrary.new_level(MAP):
        raise RuntimeError('Cannot create fresh movement map')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cube = unreal.load_asset('/Engine/BasicShapes/Cube')
    for label, loc, scale in [
        ('P2_Movement_Floor', (0, 0, -5), (50, 50, .1)),
        ('P2_Movement_Wall', (1100, 0, 150), (1, 20, 3)),
        ('P2_Movement_Obstacle', (-450, -150, 50), (1, 1, 1)),
    ]:
        actor = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*loc))
        actor.static_mesh_component.set_static_mesh(cube)
        actor.static_mesh_component.set_collision_profile_name('BlockAll')
        actor.set_actor_scale3d(unreal.Vector(*scale))
        actor.set_actor_label(label)
    for rotation, intensity in [((-35, -135, 0), 20), ((-20, 45, 0), 8)]:
        light = actors.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 400), unreal.Rotator(*rotation))
        component = light.get_component_by_class(unreal.DirectionalLightComponent)
        component.set_intensity(intensity)
        component.set_cast_shadows(True)
    roster = ['allied_A', 'allied_B', 'allied_A', 'german_A', 'german_B', 'german_A']
    for i, variant in enumerate(roster):
        player = i == 0
        cls = unreal.load_class(None, BP + ('BP_PCPlayer.BP_PCPlayer_C' if player else 'BP_PCNPC.BP_PCNPC_C'))
        actor = actors.spawn_actor_from_class(cls, unreal.Vector(-150 + (i % 3) * 240, (i // 3) * 280, 120))
        actor.set_actor_label('P2_Movement_%d_%s' % (i + 1, variant))
        faction = 'Allied' if variant.startswith('allied') else 'German'
        mesh = unreal.load_asset(MESH + VARIANTS[variant])
        anim = unreal.load_asset(ANIM + 'ABP_PC_' + faction)
        config = json.loads(unreal.ParisBlueprintAuthoring.configure_draft_character(actor, mesh, anim))
        if 'error' in config:
            raise RuntimeError(config['error'])
        actor.set_actor_location(unreal.Vector(-150 + (i % 3) * 240, (i // 3) * 280, config['capsule_half_height_cm'] + 2.15), False, False)
        actor.set_editor_property('TeamId', 1 if faction == 'Allied' else 2)
        actor.set_editor_property('RoleId', 'Player' if player else 'DiagnosticNPC')
        REPORT['actors'].append({'label': actor.get_actor_label(), 'class': cls.get_path_name(),
            'mesh': mesh.get_path_name(), 'anim_class': anim.generated_class().get_path_name(),
            'player': player, 'configuration': config})
    if not unreal.EditorLevelLibrary.save_current_level():
        raise RuntimeError('Movement map save failed')
    REPORT['result'] = 'saved_drafts_pending_fresh_load_and_runtime_probe'
except Exception:
    REPORT['errors'].append(traceback.format_exc())
    REPORT['result'] = 'fail_preserved_drafts'
REPORT['finished_at'] = datetime.now().astimezone().isoformat()
checkpoint()
unreal.log('CS549_MOVEMENT_AUTHOR_DONE ' + REPORT['result'])
if REPORT['errors']:
    raise RuntimeError('Read Movement/authoring.json; do not rerun over saved drafts')
